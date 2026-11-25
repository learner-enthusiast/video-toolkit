#!/usr/bin/env python3
"""Content-addressed cache for expensive deterministic preprocessing (per project)."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

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


def load_manifest(project: str) -> dict:
    p = manifest_path(project)
    if os.path.isfile(p):
        with open(p) as f:
            data = json.load(f)
        if data.get("version") != CACHE_VERSION:
            return {"version": CACHE_VERSION, "entries": {}}
        return data
    return {"version": CACHE_VERSION, "entries": {}}


def save_manifest(project: str, manifest: dict) -> None:
    manifest["version"] = CACHE_VERSION
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lock_path = p + ".lock"
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".am-")
    with open(lock_path, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(manifest, f, indent=2)
                f.write("\n")
            os.replace(tmp, p)
        except Exception:
            if os.path.isfile(tmp):
                os.remove(tmp)
            raise
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def bundle_root(project: str, key: str) -> str:
    return os.path.join(project, "work", "cache", "bundles", key)


def verify_entry(project: str, ent: dict) -> tuple[bool, str]:
    path = os.path.join(project, ent["path"])
    if not os.path.isfile(path):
        return False, "missing_file"
    size = os.path.getsize(path)
    if size != ent.get("size"):
        return False, "size_mismatch"
    if ent.get("sha256") and sha256_file(path) != ent["sha256"]:
        return False, "checksum_mismatch"
    if size < 1:
        return False, "empty_output"
    return True, "hit"


def cmd_lookup(args):
    params = json.loads(args.params) if args.params else None
    key = cache_key(
        args.op,
        args.input,
        params,
        script_path=args.script,
        tool_version=args.tool_version,
    )
    man = load_manifest(args.project)
    ent = man["entries"].get(key)
    out = {"hit": False, "key": key, "reason": "miss", "entry": ent}
    if ent:
        ok, reason = verify_entry(args.project, ent)
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
    dest = bundle_root(args.project, key)
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, os.path.basename(args.output))
    tmp = target + ".tmp"
    shutil.copy2(args.output, tmp)
    os.replace(tmp, target)
    rel = os.path.relpath(target, args.project)
    man = load_manifest(args.project)
    man["entries"][key] = {
        "op": args.op,
        "path": rel,
        "input": os.path.abspath(args.input),
        "params": params,
        "tool_version": args.tool_version or "unknown",
        "schema": CACHE_VERSION,
        "size": out_size,
        "sha256": out_hash,
        "implementation": implementation_hash(),
    }
    save_manifest(args.project, man)
    print(target)


def cmd_probe_ffprobe(args):
    """Store ffprobe JSON for a media file if cache miss."""
    params = {"tool": "ffprobe", "entries": args.entries or "format,duration:stream=codec_type"}
    key = cache_key("ffprobe", args.input, params, tool_version=args.tool_version or "unknown")
    man = load_manifest(args.project)
    ent = man["entries"].get(key)
    if ent and not args.force:
        ok, reason = verify_entry(args.project, ent)
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
    dest = bundle_root(args.project, key)
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, "probe.json")
    with open(target, "w") as f:
        f.write(out)
    rel = os.path.relpath(target, args.project)
    man = load_manifest(args.project)
    man["entries"][key] = {
        "op": "ffprobe",
        "path": rel,
        "input": os.path.abspath(args.input),
        "params": params,
        "tool_version": args.tool_version or "unknown",
        "schema": CACHE_VERSION,
        "size": os.path.getsize(target),
        "sha256": sha256_file(target),
        "implementation": implementation_hash(),
    }
    save_manifest(args.project, man)
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