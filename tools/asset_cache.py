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


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def implementation_hash() -> str:
    return sha256_file(SCRIPT_SELF)[:16]


def cache_key(
    op: str,
    inp: str,
    params: dict | None,
    *,
    script_path: str | None = None,
    tool_version: str | None = None,
) -> str:
    parts = [
        f"v{CACHE_VERSION}",
        implementation_hash(),
        op,
        sha256_file(inp) if os.path.isfile(inp) else inp,
        tool_version or "unknown",
    ]
    if script_path and os.path.isfile(script_path):
        parts.append(sha256_file(script_path)[:16])
    if params:
        parts.append(hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def manifest_path(project: str) -> str:
    return os.path.join(project, MANIFEST)


def _read_manifest_file(project: str) -> tuple[dict, str | None]:
    p = manifest_path(project)
    if not os.path.isfile(p):
        return {"version": CACHE_VERSION, "entries": {}}, None
    try:
        with open(p) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {"version": CACHE_VERSION, "entries": {}}, "corrupt_manifest"
    if not isinstance(data, dict) or "entries" not in data:
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
            man, _ = _read_manifest_file(project)
            mutate(man)
            man["version"] = CACHE_VERSION
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


def verify_entry(project: str, ent: dict, key: str | None = None) -> tuple[bool, str]:
    required = ("path", "sha256", "size", "cache_key", "op", "schema")
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
    resolved = ps.safe_project_relpath(project, ent["path"])
    if not resolved or not os.path.isfile(resolved):
        return False, "missing_file"
    if os.path.islink(resolved):
        return False, "symlink_forbidden"
    size = os.path.getsize(resolved)
    if size != ent["size"]:
        return False, "size_mismatch"
    if sha256_file(resolved) != ent["sha256"]:
        return False, "checksum_mismatch"
    return True, "hit"


def _key_lock_path(project: str, key: str) -> str:
    return bundle_root(project, key) + ".lock"


def _atomic_install_output(project: str, key: str, src_file: str, dest_name: str) -> str:
    dest_dir = bundle_root(project, key)
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
                    raise ValueError("empty output")
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
    key = cache_key(
        args.op,
        args.input,
        params,
        script_path=args.script,
        tool_version=args.tool_version,
    )
    man, man_err = _read_manifest_file(args.project)
    if man_err:
        out = {"hit": False, "key": key, "reason": man_err, "entry": None}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)
    ent = man["entries"].get(key)
    out = {"hit": False, "key": key, "reason": "miss", "entry": ent}
    if ent:
        ok, reason = verify_entry(args.project, ent, key)
        out["hit"] = ok
        out["reason"] = reason
        if ok:
            out["path"] = os.path.join(args.project, ent["path"])
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if out.get("hit") else 1)


def cmd_store(args):
    params = json.loads(args.params) if args.params else None
    key = cache_key(
        args.op,
        args.input,
        params,
        script_path=args.script,
        tool_version=args.tool_version,
    )
    if not os.path.isfile(args.output):
        sys.exit("output file missing")
    out_size = os.path.getsize(args.output)
    if out_size < 1:
        sys.exit("output file empty")
    out_hash = sha256_file(args.output)
    target = _atomic_install_output(args.project, key, args.output, os.path.basename(args.output))
    rel = os.path.relpath(target, args.project)
    entry = {
        "op": args.op,
        "path": rel,
        "input": os.path.abspath(args.input),
        "params": params,
        "tool_version": args.tool_version or "unknown",
        "schema": CACHE_VERSION,
        "cache_key": key,
        "size": out_size,
        "sha256": out_hash,
        "implementation": implementation_hash(),
    }

    def _add(man: dict) -> None:
        man.setdefault("entries", {})[key] = entry

    manifest_transaction(args.project, _add)
    print(target)


def cmd_probe_ffprobe(args):
    """Store ffprobe JSON for a media file if cache miss."""
    params = {"tool": "ffprobe", "entries": args.entries or "format,duration:stream=codec_type"}
    key = cache_key("ffprobe", args.input, params, tool_version=args.tool_version or "unknown")
    man, man_err = _read_manifest_file(args.project)
    if not man_err:
        ent = man["entries"].get(key)
        if ent and not args.force:
            ok, reason = verify_entry(args.project, ent, key)
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
    tmp_probe = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    try:
        tmp_probe.write(out)
        tmp_probe.flush()
        os.fsync(tmp_probe.fileno())
        tmp_probe.close()
        target = _atomic_install_output(args.project, key, tmp_probe.name, "probe.json")
    finally:
        if os.path.isfile(tmp_probe.name):
            os.remove(tmp_probe.name)
    rel = os.path.relpath(target, args.project)
    entry = {
        "op": "ffprobe",
        "path": rel,
        "input": os.path.abspath(args.input),
        "params": params,
        "tool_version": args.tool_version or "unknown",
        "schema": CACHE_VERSION,
        "cache_key": key,
        "size": os.path.getsize(target),
        "sha256": sha256_file(target),
        "implementation": implementation_hash(),
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