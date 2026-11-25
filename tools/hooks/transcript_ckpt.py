"""Incremental JSONL transcript scanning checkpoints (Stop hook token collection)."""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import tempfile

CHECKPOINT_SCHEMA = 2
_BOUNDARY_LEN = 64

_LOCK_ORDER_DOC = "Acquire session checkpoint lock before project log.md lock when both are needed."


def _zero():
    return dict(input=0, cache_write=0, cache_read=0, output=0)


def _add_bucket(dst: dict, src: dict) -> None:
    for k in dst:
        dst[k] += src.get(k) or 0


def _merge_models(dst: dict, src: dict) -> None:
    for model, t in src.items():
        d = dst.setdefault(model, _zero())
        _add_bucket(d, t)


def _file_identity(path: str) -> dict | None:
    try:
        st = os.stat(path)
    except OSError:
        return None
    return {
        "dev": st.st_dev,
        "ino": st.st_ino,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
    }


def _boundary_fingerprint(path: str, offset: int) -> str | None:
    if offset <= 0:
        return None
    try:
        with open(path, "rb") as f:
            f.seek(max(0, offset - _BOUNDARY_LEN))
            chunk = f.read(_BOUNDARY_LEN)
    except OSError:
        return None
    return hashlib.sha256(chunk).hexdigest()[:16]


def checkpoint_path(root: str, session_id: str) -> str:
    d = os.path.join(root, ".hook-state", "checkpoints")
    os.makedirs(d, exist_ok=True)
    safe = session_id.replace("/", "_")
    return os.path.join(d, f"{safe}.json")


def checkpoint_lock_path(root: str, session_id: str) -> str:
    return checkpoint_path(root, session_id) + ".lock"


@contextlib.contextmanager
def checkpoint_lock(root: str, session_id: str):
    """Serialize checkpoint + commit for a session. Acquire before log.md lock."""
    lp = checkpoint_lock_path(root, session_id)
    os.makedirs(os.path.dirname(lp), exist_ok=True)
    with open(lp, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def _validate_file_ckpt(path: str, ck: object) -> bool:
    if not isinstance(ck, dict):
        return False
    off = ck.get("offset")
    if not isinstance(off, int) or off < 0:
        return False
    ident = ck.get("identity")
    if not isinstance(ident, dict):
        return False
    for key in ("dev", "ino", "size", "mtime_ns"):
        if key not in ident:
            return False
    try:
        st = os.stat(path)
    except OSError:
        return False
    if off > st.st_size:
        return False
    ids = _file_identity(path)
    if not ids:
        return False
    return True


def _resolve_start(path: str, ck: dict | None, stats: dict) -> tuple[int, set[str], bool]:
    """Return (start_offset, logged_ids, incremental_ok)."""
    if not ck or not _validate_file_ckpt(path, ck):
        stats["mode"] = "full_rescan"
        return 0, set(), False
    cur = _file_identity(path)
    prev = ck.get("identity") or {}
    if not cur:
        stats["mode"] = "full_rescan"
        return 0, set(), False
    off = int(ck.get("offset") or 0)
    if cur["ino"] != prev.get("ino") or cur["dev"] != prev.get("dev"):
        stats["mode"] = "full_rescan"
        return 0, set(), False
    if cur["size"] < off:
        stats["mode"] = "full_rescan"
        return 0, set(), False
    boundary = ck.get("boundary_fp")
    if off > 0 and boundary:
        if _boundary_fingerprint(path, off) != boundary:
            stats["mode"] = "full_rescan"
            return 0, set(), False
    if cur["size"] == prev.get("size") and cur["mtime_ns"] != prev.get("mtime_ns"):
        stats["mode"] = "full_rescan"
        return 0, set(), False
    stats["mode"] = "incremental"
    logged = set(ck.get("logged_ids") or [])
    return off, logged, True


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
    if data.get("schema") != CHECKPOINT_SCHEMA:
        data["_invalid"] = True
    if data.get("session_id") and data.get("session_id") != session_id:
        data["_invalid"] = True
    data.setdefault("files", {})
    if not isinstance(data.get("files"), dict):
        data["files"] = {}
        data["_invalid"] = True
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
    if start >= len(data):
        return start
    chunk = data[start:]
    if chunk.endswith(b"\n"):
        return len(data)
    last_nl = chunk.rfind(b"\n")
    if last_nl < 0:
        return start
    return start + last_nl + 1


def _message_id(e: dict) -> str | None:
    m = e.get("message") or {}
    mid = m.get("id") or e.get("uuid")
    return str(mid) if mid else None


def _accumulate_usage(
    e: dict,
    since: str,
    seen: set,
    logged_ids: set,
    main_tot: dict,
    main_models: dict,
    side_tot: dict,
    side_models: dict,
    stats: dict,
) -> tuple[str | None, bool]:
    if e.get("type") != "assistant" or (e.get("timestamp") or "") < since:
        return None, False
    mid = _message_id(e)
    if mid:
        if mid in seen or mid in logged_ids:
            return e.get("timestamp"), False
        seen.add(mid)
        logged_ids.add(mid)
    else:
        stats.setdefault("unattributed", 0)
        stats["unattributed"] += 1
    m = e.get("message") or {}
    u = m.get("usage") or {}
    model = m.get("model") or "unknown"
    is_side = bool(e.get("isSidechain"))
    tot = side_tot if is_side else main_tot
    models = side_models if is_side else main_models
    mt = models.setdefault(model, _zero())
    for key, src in (
        ("input", "input_tokens"),
        ("cache_write", "cache_creation_input_tokens"),
        ("cache_read", "cache_read_input_tokens"),
        ("output", "output_tokens"),
    ):
        v = u.get(src) or 0
        tot[key] += v
        mt[key] += v
    stats["messages_counted"] = stats.get("messages_counted", 0) + 1
    return e.get("timestamp"), True


def scan_parent_transcript(
    path: str,
    since: str,
    seen: set,
    *,
    checkpoint: dict | None = None,
    session_id: str | None = None,
    incremental: bool = True,
    stats: dict | None = None,
):
    """Single pass: main + parent sidechain buckets."""
    stats = stats if stats is not None else {}
    stats.setdefault("bytes_read", 0)
    stats.setdefault("records_scanned", 0)
    stats.setdefault("records_parsed", 0)
    stats.setdefault("mode", "full")
    stats["parent_scans"] = stats.get("parent_scans", 0) + 1
    main_tot = _zero()
    side_tot = _zero()
    main_models: dict = {}
    side_models: dict = {}
    last = None
    n_main = n_side = 0
    if not path:
        return main_tot, side_tot, main_models, side_models, last, n_main, n_side, stats

    files_ckpt = (checkpoint or {}).get("files", {}) if incremental and checkpoint else {}
    use_inc = bool(incremental and checkpoint is not None and session_id)

    try:
        fh = open(path, "rb")
    except OSError:
        return main_tot, side_tot, main_models, side_models, last, n_main, n_side, stats

    with fh:
        start = 0
        logged_ids: set[str] = set()
        ck = files_ckpt.get(path) if use_inc else None
        if use_inc:
            start, logged_ids, _ = _resolve_start(path, ck, stats)
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        stats["bytes_read"] += size - start
        fh.seek(start)
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
            ts, counted = _accumulate_usage(
                e, since, seen, logged_ids, main_tot, main_models, side_tot, side_models, stats
            )
            if counted:
                if e.get("isSidechain"):
                    n_side += 1
                else:
                    n_main += 1
            if ts:
                last = max(last or "", ts)
        new_off = start + _complete_line_offset(buf, 0)
        ident = _file_identity(path)
        if use_inc and ident and checkpoint is not None:
            files_ckpt[path] = {
                "identity": ident,
                "offset": new_off,
                "boundary_fp": _boundary_fingerprint(path, new_off),
                "logged_ids": sorted(logged_ids)[-5000:],
            }

    return main_tot, side_tot, main_models, side_models, last, n_main, n_side, stats


def scan_subagent_files(
    paths,
    since: str,
    seen: set,
    *,
    checkpoint: dict | None = None,
    session_id: str | None = None,
    incremental: bool = True,
    stats: dict | None = None,
):
    stats = stats if stats is not None else {}
    stats.setdefault("bytes_read", 0)
    stats.setdefault("records_scanned", 0)
    stats.setdefault("records_parsed", 0)
    sub_tot = _zero()
    sub_models: dict = {}
    last = None
    n_sub = 0
    files_ckpt = (checkpoint or {}).get("files", {}) if incremental and checkpoint else {}
    use_inc = bool(incremental and checkpoint is not None and session_id)

    for path in paths:
        if not path:
            continue
        try:
            fh = open(path, "rb")
        except OSError:
            continue
        with fh:
            start = 0
            logged_ids: set[str] = set()
            ck = files_ckpt.get(path) if use_inc else None
            if use_inc:
                sub_stats = {"mode": "incremental"}
                start, logged_ids, _ = _resolve_start(path, ck, sub_stats)
                stats["mode"] = sub_stats.get("mode", stats.get("mode"))
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            stats["bytes_read"] += size - start
            fh.seek(start)
            buf = fh.read()
            pos = 0
            main_tot = _zero()
            main_models = {}
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
                mid = _message_id(e)
                if mid:
                    if mid in seen or mid in logged_ids:
                        continue
                    seen.add(mid)
                    logged_ids.add(mid)
                else:
                    stats.setdefault("unattributed", 0)
                    stats["unattributed"] += 1
                m = e.get("message") or {}
                u = m.get("usage") or {}
                model = m.get("model") or "unknown"
                mt = sub_models.setdefault(model, _zero())
                for key, src in (
                    ("input", "input_tokens"),
                    ("cache_write", "cache_creation_input_tokens"),
                    ("cache_read", "cache_read_input_tokens"),
                    ("output", "output_tokens"),
                ):
                    v = u.get(src) or 0
                    sub_tot[key] += v
                    mt[key] += v
                n_sub += 1
                ts = e.get("timestamp")
                if ts:
                    last = max(last or "", ts)
            new_off = start + _complete_line_offset(buf, 0)
            ident = _file_identity(path)
            if use_inc and ident and checkpoint is not None:
                files_ckpt[path] = {
                    "identity": ident,
                    "offset": new_off,
                    "boundary_fp": _boundary_fingerprint(path, new_off),
                    "logged_ids": sorted(logged_ids)[-5000:],
                }
    return sub_tot, sub_models, last, n_sub, stats


def collect_usage_reference(tp: str, sub_paths: list[str], since: str):
    """Full-scan reference totals (no checkpoint)."""
    seen: set[str] = set()
    stats: dict = {}
    main, side, mm, sm, last, nm, ns, stats = scan_parent_transcript(
        tp, since, seen, checkpoint=None, incremental=False, stats=stats
    )
    sub, subm, slast, nsub, _ = scan_subagent_files(
        sub_paths, since, seen, checkpoint=None, incremental=False
    )
    sub_combined = dict(sub)
    _add_bucket(sub_combined, side)
    sub_models = {}
    _merge_models(sub_models, sm)
    _merge_models(sub_models, subm)
    return (main, sub_combined, mm, sub_models, last, slast, nm, nsub + ns)


def usage_since(paths, since, main_only=None, seen=None, **kwargs):
    """Backward-compatible wrapper; prefer scan_parent_transcript for parent files."""
    stats = kwargs.get("stats") or {"bytes_read": 0, "records_scanned": 0, "records_parsed": 0, "mode": "full"}
    checkpoint = kwargs.get("checkpoint")
    session_id = kwargs.get("session_id")
    incremental = kwargs.get("incremental", True)
    if main_only is False and len(paths) == 1:
        _, side, _, sm, last, _, n, _ = scan_parent_transcript(
            paths[0],
            since,
            seen or set(),
            checkpoint=checkpoint,
            session_id=session_id,
            incremental=incremental,
            stats=stats,
        )
        return side, last, n, sm
    if main_only is True and len(paths) == 1:
        main, _, mm, _, last, n, _, _ = scan_parent_transcript(
            paths[0],
            since,
            seen or set(),
            checkpoint=checkpoint,
            session_id=session_id,
            incremental=incremental,
            stats=stats,
        )
        return main, last, n, mm
    sub, sm, last, n, _ = scan_subagent_files(
        paths,
        since,
        seen or set(),
        checkpoint=checkpoint,
        session_id=session_id,
        incremental=incremental,
        stats=stats,
    )
    return sub, last, n, sm


def usage_since_full(paths, since, main_only=None, seen=None):
    seen = set() if seen is None else seen
    stats = {"mode": "full", "bytes_read": 0, "records_scanned": 0, "records_parsed": 0}
    return usage_since(paths, since, main_only, seen, checkpoint=None, incremental=False, stats=stats)