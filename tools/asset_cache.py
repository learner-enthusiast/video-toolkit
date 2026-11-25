#!/usr/bin/env python3
"""Content-addressed cache for expensive deterministic preprocessing (per project)."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from tools import path_safety as ps

_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

CACHE_VERSION = 2
MANIFEST = "work/cache/asset-manifest.json"
SCRIPT_SELF = os.path.abspath(__file__)

# Test instrumentation: increment on each input file hash (see tests).
_INPUT_HASH_CALLS = 0


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def implementation_hash() -> str:
    return sha256_file(SCRIPT_SELF)[:16]


class MissingScriptFingerprintError(ValueError):
    pass


def _hash_input_file(path: str) -> tuple[str | None, int | None, int | None]:
    global _INPUT_HASH_CALLS
    if not os.path.isfile(path):
        return None, None, None
    _INPUT_HASH_CALLS += 1
    st = os.stat(path)
    digest = sha256_file(path)
    return digest, st.st_size, st.st_mtime_ns


def build_operation_fingerprint(
    op: str,
    inp: str,
    params: dict | None,
    *,
    script_path: str | None = None,
    tool_version: str | None = None,
) -> dict:
    """Compute all fingerprint fields once per command."""
    if script_path and not os.path.isfile(script_path):
        raise MissingScriptFingerprintError(f"script not found: {script_path}")
    inp_abs = os.path.abspath(inp)
    inp_hash, inp_size, inp_mtime = _hash_input_file(inp) if os.path.isfile(inp) else (None, None, None)
    impl = implementation_hash()
    script_hash = None
    if script_path and os.path.isfile(script_path):
        script_hash = sha256_file(script_path)[:16]
    return {
        "op": op,
        "input": inp_abs,
        "input_sha256": inp_hash,
        "input_size": inp_size,
        "input_mtime_ns": inp_mtime,
        "params": params,
        "tool_version": tool_version or "unknown",
        "implementation": impl,
        "script_hash": script_hash,
    }


def cache_key_from_fingerprint(fp: dict) -> str:
    inp_tag = fp["input_sha256"] if fp.get("input_sha256") else fp["input"]
    parts = [
        f"v{CACHE_VERSION}",
        fp["implementation"],
        fp["op"],
        inp_tag,
        fp["tool_version"],
    ]
    if fp.get("script_hash"):
        parts.append(fp["script_hash"])
    if fp.get("params") is not None:
        parts.append(hashlib.sha256(json.dumps(fp["params"], sort_keys=True).encode()).hexdigest()[:16])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def cache_key(
    op: str,
    inp: str,
    params: dict | None,
    *,
    script_path: str | None = None,
    tool_version: str | None = None,
    fingerprint: dict | None = None,
) -> str:
    fp = fingerprint or build_operation_fingerprint(
        op, inp, params, script_path=script_path, tool_version=tool_version
    )
    return cache_key_from_fingerprint(fp)


def manifest_path(project: str) -> str:
    return os.path.join(project, MANIFEST)


def _quarantine_manifest_file(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    base = path + ".corrupt"
    target = base
    n = 0
    while os.path.isfile(target):
        n += 1
        target = f"{base}-{n}"
    try:
        shutil.copy2(path, target)
        return target
    except OSError:
        return None


def _read_manifest_file(project: str) -> tuple[dict, str | None]:
    p = manifest_path(project)
    if not os.path.isfile(p):
        return {"version": CACHE_VERSION, "entries": {}}, None
    data, err = ps.load_json_dict(p)
    if err == "missing":
        return {"version": CACHE_VERSION, "entries": {}}, None
    if err:
        return {"version": CACHE_VERSION, "entries": {}}, err
    if "entries" not in data:
        return {"version": CACHE_VERSION, "entries": {}}, "invalid_manifest"
    if not isinstance(data.get("entries"), dict):
        return {"version": CACHE_VERSION, "entries": {}}, "invalid_entries"
    if data.get("version") != CACHE_VERSION:
        return {"version": CACHE_VERSION, "entries": {}}, "schema_mismatch"
    return data, None


def manifest_transaction(project: str, mutate) -> dict:
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lock_path = p + ".lock"
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".am-")
    with open(lock_path, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            man, read_err = _read_manifest_file(project)
            if read_err and os.path.isfile(p):
                _quarantine_manifest_file(p)
            mutate(man)
            man["version"] = CACHE_VERSION
            man.pop("_quarantined", None)
            with os.fdopen(fd, "w") as f:
                json.dump(man, f, indent=2)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, p)
            return man
        except Exception:
            if os.path.isfile(tmp):
                os.remove(tmp)
            raise
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def load_manifest(project: str) -> dict:
    man, _ = _read_manifest_file(project)
    return man


def bundle_root(project: str, key: str) -> str:
    return os.path.join(project, "work", "cache", "bundles", key)


def _entry_matches_operation(ent: dict, expect: dict) -> str | None:
    if ent.get("op") != expect["op"]:
        return "op_mismatch"
    if ent.get("input") != expect["input"]:
        return "input_mismatch"
    if expect.get("input_sha256"):
        if ent.get("input_sha256") and ent["input_sha256"] != expect["input_sha256"]:
            return "input_hash_mismatch"
    stored_ver = ent.get("tool_version") or "unknown"
    if stored_ver != expect["tool_version"]:
        return "tool_version_mismatch"
    if ent.get("implementation") != expect["implementation"]:
        return "implementation_mismatch"
    if expect["script_hash"]:
        if ent.get("script_hash") != expect["script_hash"]:
            return "script_hash_mismatch"
    if expect["params"] != ent.get("params"):
        return "params_mismatch"
    return None


def verify_entry(
    project: str,
    ent: dict,
    key: str | None = None,
    *,
    operation: dict | None = None,
) -> tuple[bool, str]:
    if not isinstance(ent, dict):
        return False, "invalid_entry"
    required = (
        "path",
        "sha256",
        "size",
        "cache_key",
        "op",
        "schema",
        "input",
        "tool_version",
        "implementation",
    )
    for field in required:
        if field not in ent:
            return False, f"missing_field:{field}"
    if ent["schema"] != CACHE_VERSION:
        return False, "schema_mismatch"
    if key is not None and ent["cache_key"] != key:
        return False, "fingerprint_mismatch"
    if not _SHA256_RE.match(str(ent["sha256"])):
        return False, "invalid_checksum_format"
    if not isinstance(ent["size"], int) or ent["size"] < 1:
        return False, "invalid_size"
    lookup_key = key or ent["cache_key"]
    resolved = ps.resolve_in_asset_bundle(project, lookup_key, ent["path"])
    if not resolved:
        return False, "path_forbidden"
    size = os.path.getsize(resolved)
    if size != ent["size"]:
        return False, "size_mismatch"
    if sha256_file(resolved) != ent["sha256"]:
        return False, "checksum_mismatch"
    if operation:
        meta_err = _entry_matches_operation(ent, operation)
        if meta_err:
            return False, meta_err
    return True, "hit"


def _key_lock_path(project: str, key: str) -> str:
    return bundle_root(project, key) + ".lock"


def _atomic_install_output(project: str, key: str, src_file: str, dest_name: str) -> str:
    dest_dir = bundle_root(project, key)
    if ps.path_has_symlink_component(dest_dir):
        raise ValueError("symlink_forbidden:bundle_root")
    os.makedirs(dest_dir, exist_ok=True)
    target = os.path.join(dest_dir, dest_name)
    lock = _key_lock_path(project, key)
    fd, tmp = tempfile.mkstemp(dir=dest_dir, prefix=".out-")
    try:
        with open(lock, "a") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                with os.fdopen(fd, "wb") as fout:
                    with open(src_file, "rb") as fin:
                        shutil.copyfileobj(fin, fout)
                    fout.flush()
                    os.fsync(fout.fileno())
                fd = None
                if os.path.getsize(tmp) < 1:
                    raise ValueError("empty_output")
                os.replace(tmp, target)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise
    return target


def cmd_lookup(args):
    params = json.loads(args.params) if args.params else None
    try:
        fp = build_operation_fingerprint(
            args.op, args.input, params, script_path=args.script, tool_version=args.tool_version
        )
    except MissingScriptFingerprintError as exc:
        out = {"hit": False, "key": None, "reason": str(exc), "entry": None}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)
    key = cache_key_from_fingerprint(fp)
    man, man_err = _read_manifest_file(args.project)
    if man_err:
        out = {"hit": False, "key": key, "reason": man_err, "entry": None}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)
    ent = man["entries"].get(key)
    op_expect = fp
    out = {"hit": False, "key": key, "reason": "miss", "entry": ent}
    if ent:
        ok, reason = verify_entry(args.project, ent, key, operation=op_expect)
        out["hit"] = ok
        out["reason"] = reason
        if ok:
            out["path"] = os.path.join(args.project, ent["path"])
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if out.get("hit") else 1)


def cmd_store(args):
    params = json.loads(args.params) if args.params else None
    try:
        fp = build_operation_fingerprint(
            args.op, args.input, params, script_path=args.script, tool_version=args.tool_version
        )
    except MissingScriptFingerprintError as exc:
        sys.exit(str(exc))
    key = cache_key_from_fingerprint(fp)
    if not os.path.isfile(args.output):
        sys.exit("output file missing")
    out_size = os.path.getsize(args.output)
    if out_size < 1:
        sys.exit("output file empty")
    if fp.get("input_size") is not None and os.path.isfile(args.input):
        st = os.stat(args.input)
        if st.st_size != fp["input_size"] or st.st_mtime_ns != fp["input_mtime_ns"]:
            sys.exit("input changed during operation")
    out_hash = sha256_file(args.output)
    target = _atomic_install_output(args.project, key, args.output, os.path.basename(args.output))
    rel = os.path.relpath(target, args.project).replace("\\", "/")
    entry = {
        "op": fp["op"],
        "path": rel,
        "input": fp["input"],
        "input_sha256": fp.get("input_sha256"),
        "params": fp.get("params"),
        "tool_version": fp["tool_version"],
        "schema": CACHE_VERSION,
        "cache_key": key,
        "size": out_size,
        "sha256": out_hash,
        "implementation": fp["implementation"],
        "script_hash": fp.get("script_hash"),
    }

    def _add(man: dict) -> None:
        man.setdefault("entries", {})[key] = entry

    manifest_transaction(args.project, _add)
    print(target)


def cmd_probe_ffprobe(args):
    """Store ffprobe JSON for a media file if cache miss."""
    params = {"tool": "ffprobe", "entries": args.entries or "format,duration:stream=codec_type"}
    fp = build_operation_fingerprint(
        "ffprobe", args.input, params, script_path=None, tool_version=args.tool_version or "unknown"
    )
    key = cache_key_from_fingerprint(fp)
    man, man_err = _read_manifest_file(args.project)
    op_expect = fp
    if not man_err:
        ent = man["entries"].get(key)
        if ent and not args.force:
            ok, reason = verify_entry(args.project, ent, key, operation=op_expect)
            if ok:
                print(os.path.join(args.project, ent["path"]))
                return
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", params["entries"], "-of", "json", args.input],
            text=True,
        )
    except FileNotFoundError:
        sys.exit("ffprobe not available")
    try:
        json.loads(out)
    except json.JSONDecodeError:
        sys.exit("ffprobe returned invalid JSON")
    fd, tmp_path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w") as tmp_probe:
            tmp_probe.write(out)
            tmp_probe.flush()
            os.fsync(tmp_probe.fileno())
        target = _atomic_install_output(args.project, key, tmp_path, "probe.json")
    finally:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
    rel = os.path.relpath(target, args.project).replace("\\", "/")
    entry = {
        "op": "ffprobe",
        "path": rel,
        "input": fp["input"],
        "input_sha256": fp.get("input_sha256"),
        "params": params,
        "tool_version": fp["tool_version"],
        "schema": CACHE_VERSION,
        "cache_key": key,
        "size": os.path.getsize(target),
        "sha256": sha256_file(target),
        "implementation": fp["implementation"],
        "script_hash": None,
    }

    def _add(man: dict) -> None:
        man.setdefault("entries", {})[key] = entry

    manifest_transaction(args.project, _add)
    print(target)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("project")
        sp.add_argument("input")
        sp.add_argument("op")
        sp.add_argument("--params", default="")
        sp.add_argument("--script", help="Implementation script to fingerprint")
        sp.add_argument("--tool-version", default="")

    s = common(sub.add_parser("lookup"))
    s.set_defaults(func=cmd_lookup)

    s = common(sub.add_parser("store"))
    s.add_argument("output")
    s.set_defaults(func=cmd_store)

    s = sub.add_parser("ffprobe")
    s.add_argument("project")
    s.add_argument("input")
    s.add_argument("--entries")
    s.add_argument("--force", action="store_true")
    s.add_argument("--tool-version", default="")
    s.set_defaults(func=cmd_probe_ffprobe)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()