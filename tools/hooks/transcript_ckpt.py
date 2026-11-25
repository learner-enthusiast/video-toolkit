"""Incremental JSONL transcript scanning checkpoints (Stop hook token collection)."""
from __future__ import annotations

import json
import os
import tempfile

CHECKPOINT_SCHEMA = 1


def _file_identity(path: str) -> dict | None:
    try:
        st = os.stat(path)
    except OSError:
        return None
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns}


def checkpoint_path(root: str, session_id: str) -> str:
    d = os.path.join(root, ".hook-state", "checkpoints")
    os.makedirs(d, exist_ok=True)
    safe = session_id.replace("/", "_")
    return os.path.join(d, f"{safe}.json")


def load_checkpoint(root: str, session_id: str) -> dict:
    p = checkpoint_path(root, session_id)
    if not os.path.isfile(p):
        return {"schema": CHECKPOINT_SCHEMA, "session_id": session_id, "files": {}}
    try:
        with open(p) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"schema": CHECKPOINT_SCHEMA, "session_id": session_id, "files": {}, "_invalid": True}
    if not isinstance(data, dict):
        return {"schema": CHECKPOINT_SCHEMA, "session_id": session_id, "files": {}, "_invalid": True}
    data.setdefault("files", {})
    if not isinstance(data.get("files"), dict):
        data["files"] = {}
    return data


def save_checkpoint(root: str, session_id: str, data: dict) -> None:
    p = checkpoint_path(root, session_id)
    data["schema"] = CHECKPOINT_SCHEMA
    data["session_id"] = session_id
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".ckpt-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    except Exception:
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise


def _complete_line_offset(data: bytes, start: int) -> int:
    """Offset after the last complete newline in data[start:], or start if none."""
    if start >= len(data):
        return start
    chunk = data[start:]
    if chunk.endswith(b"\n"):
        return len(data)
    last_nl = chunk.rfind(b"\n")
    if last_nl < 0:
        return start
    return start + last_nl + 1


def parse_jsonl_assistant_lines(
    fh,
    since: str,
    main_only: bool | None,
    seen: set,
    logged_ids: set,
    start_offset: int,
    stats: dict,
) -> tuple[dict, str | None, int, dict, int]:
    """Read from fh (binary, seekable); return tot, last_ts, n_new, by_model, new_offset."""
    tot = dict(input=0, cache_write=0, cache_read=0, output=0)
    by_model: dict[str, dict] = {}
    last = None
    n_new = 0
    fh.seek(0, os.SEEK_END)
    size = fh.tell()
    stats["bytes_read"] += size - start_offset
    fh.seek(start_offset)
    buf = fh.read()
    pos = 0
    while pos < len(buf):
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        raw = buf[pos:nl]
        pos = nl + 1
        stats["records_scanned"] += 1
        if b'"assistant"' not in raw:
            continue
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        stats["records_parsed"] += 1
        if e.get("type") != "assistant" or (e.get("timestamp") or "") < since:
            continue
        if main_only is not None and bool(e.get("isSidechain")) == main_only:
            continue
        m = e.get("message") or {}
        mid = m.get("id") or e.get("uuid")
        if not mid or mid in seen or mid in logged_ids:
            continue
        seen.add(mid)
        logged_ids.add(mid)
        n_new += 1
        u = m.get("usage") or {}
        model = m.get("model") or "unknown"
        mt = by_model.setdefault(model, dict(input=0, cache_write=0, cache_read=0, output=0))
        for key, src in (
            ("input", "input_tokens"),
            ("cache_write", "cache_creation_input_tokens"),
            ("cache_read", "cache_read_input_tokens"),
            ("output", "output_tokens"),
        ):
            v = u.get(src) or 0
            tot[key] += v
            mt[key] += v
        last = max(last or "", e["timestamp"])
    new_offset = start_offset + _complete_line_offset(buf, 0)
    return tot, last, n_new, by_model, new_offset


def usage_since(
    paths,
    since: str,
    main_only=None,
    seen=None,
    *,
    root: str | None = None,
    session_id: str | None = None,
    checkpoint: dict | None = None,
    incremental: bool = True,
    stats: dict | None = None,
):
    """Sum assistant usage; incremental append reads when checkpoint provided."""
    stats = stats if stats is not None else {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0, "mode": "full"}
    seen = set() if seen is None else seen
    n0 = len(seen)
    tot = dict(input=0, cache_write=0, cache_read=0, output=0)
    by_model: dict[str, dict] = {}
    last = None
    files_ckpt = (checkpoint or {}).get("files", {}) if incremental else {}
    use_incremental = incremental and checkpoint is not None and session_id

    for p in paths:
        if not p:
            continue
        try:
            fh = open(p, "rb")
        except OSError:
            continue
        with fh:
            identity = _file_identity(p)
            start = 0
            logged_ids: set[str] = set()
            ck = files_ckpt.get(p) if use_incremental else None
            if use_incremental and ck and identity:
                prev = ck.get("identity") or {}
                if prev == identity:
                    start = int(ck.get("offset") or 0)
                elif prev.get("size") is not None and identity["size"] >= prev["size"]:
                    start = int(ck.get("offset") or 0)
                else:
                    start = 0
                    stats["mode"] = "full_rescan"
                if start > identity["size"]:
                    start = 0
                if stats.get("mode") != "full_rescan":
                    stats["mode"] = "incremental"
                    logged_ids = set(ck.get("logged_ids") or [])
            elif use_incremental:
                stats["mode"] = "full_rescan"

            pt, plast, pn, pmodels, new_off = parse_jsonl_assistant_lines(
                fh, since, main_only, seen, logged_ids, start, stats
            )
            for k in tot:
                tot[k] += pt[k]
            for model, t in pmodels.items():
                dst = by_model.setdefault(model, dict(input=0, cache_write=0, cache_read=0, output=0))
                for key in dst:
                    dst[key] += t[key]
            if plast:
                last = max(last or "", plast)

            if use_incremental and identity:
                files_ckpt[p] = {
                    "identity": identity,
                    "offset": new_off,
                    "logged_ids": sorted(logged_ids)[-5000:],
                }

    return tot, last, len(seen) - n0, by_model


def usage_since_full(paths, since, main_only=None, seen=None):
    """Reference full-file scan (no checkpoint)."""
    return usage_since(
        paths,
        since,
        main_only,
        seen,
        checkpoint=None,
        incremental=False,
        stats={"mode": "full", "bytes_read": 0, "records_scanned": 0, "records_parsed": 0},
    )