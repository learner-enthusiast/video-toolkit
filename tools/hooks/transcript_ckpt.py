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
_GLOBAL_ID_CAP = 50_000
_FILE_ID_CAP = 5_000
_CONTENT_FP_CHUNK = 256 * 1024

_LOCK_ORDER_DOC = "Acquire session checkpoint lock before project log.md lock when both are needed."


def turn_idempotency_key(started_utc: str, prompt_ref: str | None) -> str:
    """Stable Stop-hook turn id (session checkpoint scope)."""
    ref = prompt_ref or ""
    return f"{started_utc}\x1f{ref}"


def _strict_nonneg_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < 0:
        return None
    return value


def _strict_id_field(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _normalize_id_list(raw: object) -> list[str] | None:
    if raw is None:
        return []
    if not isinstance(raw, list):
        return None
    out: list[str] = []
    for item in raw:
        if item is None:
            continue
        if not isinstance(item, (str, int)):
            return None
        s = str(item).strip()
        if s:
            out.append(s)
    return out


def _content_fingerprint(path: str, end: int) -> str | None:
    if end <= 0:
        return None
    try:
        with open(path, "rb") as f:
            h = hashlib.sha256()
            remain = end
            while remain > 0:
                chunk = f.read(min(_CONTENT_FP_CHUNK, remain))
                if not chunk:
                    break
                h.update(chunk)
                remain -= len(chunk)
    except OSError:
        return None
    return h.hexdigest()[:32]


def global_logged_ids(ckpt: dict | None) -> set[str]:
    if not ckpt:
        return set()
    ids = _normalize_id_list(ckpt.get("logged_ids_global"))
    if ids is None:
        return set()
    return set(ids)


class OrderedIds(dict):
    """A set of message ids that remembers insertion order, so caps drop the oldest."""

    def __init__(self, ids=()):
        super().__init__(dict.fromkeys(ids))

    def add(self, item: str) -> None:
        self.setdefault(item, None)

    def update(self, ids) -> None:
        for item in ids:
            self.add(item)

    def newest(self, cap: int) -> list[str]:
        return list(self)[-cap:]


def ordered_logged_ids(ckpt: dict | None) -> list[str]:
    """Stored ids, oldest first."""
    return (_normalize_id_list((ckpt or {}).get("logged_ids_global")) or [])


def merge_global_logged_ids(ckpt: dict, seen) -> None:
    merged = OrderedIds(ordered_logged_ids(ckpt))
    merged.update(seen)
    ckpt["logged_ids_global"] = merged.newest(_GLOBAL_ID_CAP)


def validate_file_record(path: str, ck: object, *, require_boundary: bool = False) -> bool:
    if not isinstance(ck, dict):
        return False
    off = _strict_nonneg_int(ck.get("offset"))
    if off is None:
        return False
    ident = ck.get("identity")
    if not isinstance(ident, dict):
        return False
    for key in ("dev", "ino", "size", "mtime_ns"):
        if key not in ident:
            return False
        v = ident[key]
        if key in ("dev", "ino"):
            if _strict_id_field(v) is None:
                return False
        elif _strict_nonneg_int(v) is None:
            return False
    if not isinstance(path, str) or not path:
        return False
    ids_norm = _normalize_id_list(ck.get("logged_ids"))
    if ck.get("logged_ids") is not None and ids_norm is None:
        return False
    boundary = ck.get("boundary_fp")
    if off > 0:
        if require_boundary and (not isinstance(boundary, str) or not boundary):
            return False
        if boundary is not None and not isinstance(boundary, str):
            return False
    content_fp = ck.get("content_fp")
    if content_fp is not None and not isinstance(content_fp, str):
        return False
    try:
        st = os.stat(path)
    except OSError:
        return False
    if off > st.st_size:
        return False
    return True


def validate_completed_turns(raw: object, session_id: str) -> dict | None:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        return None
    out: dict = {}
    for key, val in raw.items():
        if not isinstance(key, str) or not key:
            return None
        if not isinstance(val, dict):
            return None
        if val.get("session_id") and val.get("session_id") != session_id:
            return None
        if val.get("started_utc") and not isinstance(val["started_utc"], str):
            return None
        if val.get("prompt_ref") is not None and not isinstance(val["prompt_ref"], str):
            return None
        out[key] = dict(val)
    return out


def sanitize_checkpoint(data: dict, session_id: str) -> tuple[dict, bool]:
    """Return (checkpoint, invalid). Drops unsafe file records; clears bad nested fields."""
    invalid = bool(data.pop("_invalid", False))
    if data.get("schema") != CHECKPOINT_SCHEMA:
        invalid = True
    if not data.get("session_id"):
        data["session_id"] = session_id
    elif data.get("session_id") != session_id:
        invalid = True
    files = data.get("files")
    if not isinstance(files, dict):
        files = {}
        invalid = True
    safe_files: dict = {}
    for path, rec in files.items():
        if not isinstance(path, str) or not path:
            invalid = True
            continue
        if validate_file_record(path, rec):
            safe_files[path] = rec
        else:
            invalid = True
    data["files"] = safe_files
    ids = _normalize_id_list(data.get("logged_ids_global"))
    if data.get("logged_ids_global") is not None and ids is None:
        invalid = True
        data["logged_ids_global"] = []
    elif ids is not None:
        data["logged_ids_global"] = ids
    else:
        data.setdefault("logged_ids_global", [])
    turns = validate_completed_turns(data.get("completed_turns"), session_id)
    if data.get("completed_turns") is not None and turns is None:
        invalid = True
        data["completed_turns"] = {}
    elif turns is not None:
        data["completed_turns"] = turns
    else:
        data.setdefault("completed_turns", {})
    data["schema"] = CHECKPOINT_SCHEMA
    data["session_id"] = session_id
    return data, invalid


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
    return validate_file_record(path, ck, require_boundary=False)


def _resolve_start(path: str, ck: dict | None, stats: dict) -> tuple[int, list[str], bool]:
    """Return (start_offset, logged_ids, incremental_ok)."""
    if not ck or not _validate_file_ckpt(path, ck):
        stats["mode"] = "full_rescan"
        return 0, [], False
    cur = _file_identity(path)
    prev = ck.get("identity") or {}
    if not cur:
        stats["mode"] = "full_rescan"
        return 0, [], False
    off = int(ck.get("offset") or 0)
    if cur["ino"] != prev.get("ino") or cur["dev"] != prev.get("dev"):
        stats["mode"] = "full_rescan"
        return 0, [], False
    if cur["size"] < off:
        stats["mode"] = "full_rescan"
        return 0, [], False
    boundary = ck.get("boundary_fp")
    if off > 0 and boundary:
        if _boundary_fingerprint(path, off) != boundary:
            stats["mode"] = "full_rescan"
            return 0, [], False
    stored_content = ck.get("content_fp")
    if off > 0 and stored_content:
        live = _content_fingerprint(path, off)
        if live is None or live != stored_content:
            stats["mode"] = "full_rescan"
            return 0, [], False
    if cur["size"] == prev.get("size") and cur["mtime_ns"] != prev.get("mtime_ns"):
        stats["mode"] = "full_rescan"
        return 0, [], False
    if cur["size"] > prev.get("size", 0) and cur["size"] > off and off > 0:
        # Append-only growth is allowed when boundary + content_fp matched; residual risk:
        # in-place edits solely beyond offset without mtime change are not always detectable
        # without hashing the whole tail on every pass (see module docstring in project-log docs).
        pass
    stats["mode"] = "incremental"
    logged_raw = ck.get("logged_ids")
    ids_norm = _normalize_id_list(logged_raw)
    if logged_raw is not None and ids_norm is None:
        stats["mode"] = "full_rescan"
        return 0, [], False
    logged = list(ids_norm or [])
    return off, logged, True


def load_checkpoint(root: str, session_id: str) -> dict:
    p = checkpoint_path(root, session_id)
    if not os.path.isfile(p):
        return {
            "schema": CHECKPOINT_SCHEMA,
            "session_id": session_id,
            "files": {},
            "logged_ids_global": [],
            "completed_turns": {},
        }
    try:
        with open(p) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {"schema": CHECKPOINT_SCHEMA, "session_id": session_id, "files": {}, "_invalid": True}
    if not isinstance(data, dict):
        data = {"schema": CHECKPOINT_SCHEMA, "session_id": session_id, "files": {}, "_invalid": True}
    clean, invalid = sanitize_checkpoint(data, session_id)
    if invalid:
        clean["_invalid"] = True
    return clean


def is_turn_committed(ckpt: dict, idem_key: str) -> bool:
    turns = ckpt.get("completed_turns") or {}
    return isinstance(turns, dict) and idem_key in turns


def mark_turn_committed(ckpt: dict, idem_key: str, *, started_utc: str, prompt_ref: str | None, session_id: str) -> None:
    ckpt.setdefault("completed_turns", {})[idem_key] = {
        "session_id": session_id,
        "started_utc": started_utc,
        "prompt_ref": prompt_ref,
    }


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


def _count_call(stats: dict, model: str) -> None:
    calls = stats.setdefault("calls_by_model", {})
    calls[model] = calls.get(model, 0) + 1


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
    _count_call(stats, model)
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
    ordered_global = ordered_logged_ids(checkpoint) if use_inc else []
    seen.update(ordered_global)

    try:
        fh = open(path, "rb")
    except OSError:
        return main_tot, side_tot, main_models, side_models, last, n_main, n_side, stats

    with fh:
        start = 0
        logged_ids = OrderedIds(ordered_global)
        ck = files_ckpt.get(path) if use_inc else None
        if use_inc:
            start, file_ids, _ = _resolve_start(path, ck, stats)
            logged_ids.update(file_ids)
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
                "content_fp": _content_fingerprint(path, new_off),
                "logged_ids": logged_ids.newest(_FILE_ID_CAP),
            }
            merge_global_logged_ids(checkpoint, logged_ids)

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
    ordered_global = ordered_logged_ids(checkpoint) if use_inc else []
    seen.update(ordered_global)

    for path in paths:
        if not path:
            continue
        try:
            fh = open(path, "rb")
        except OSError:
            continue
        with fh:
            start = 0
            logged_ids = OrderedIds(ordered_global)
            ck = files_ckpt.get(path) if use_inc else None
            if use_inc:
                sub_stats = {"mode": "incremental"}
                start, file_ids, _ = _resolve_start(path, ck, sub_stats)
                logged_ids.update(file_ids)
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
                _count_call(stats, model)
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
                    "content_fp": _content_fingerprint(path, new_off),
                    "logged_ids": logged_ids.newest(_FILE_ID_CAP),
                }
                merge_global_logged_ids(checkpoint, logged_ids)
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