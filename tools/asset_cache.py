#!/usr/bin/env python3
"""Content-addressed cache for expensive deterministic preprocessing (per project)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

CACHE_VERSION = 1
MANIFEST = "work/cache/asset-manifest.json"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_key(op: str, inp: str, params: dict | None) -> str:
    parts = [f"v{CACHE_VERSION}", op, sha256_file(inp) if os.path.isfile(inp) else inp]
    if params:
        parts.append(hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def manifest_path(project: str) -> str:
    return os.path.join(project, MANIFEST)


def load_manifest(project: str) -> dict:
    p = manifest_path(project)
    if os.path.isfile(p):
        with open(p) as f:
            return json.load(f)
    return {"version": CACHE_VERSION, "entries": {}}


def save_manifest(project: str, manifest: dict) -> None:
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".am-")
    with os.fdopen(fd, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def bundle_root(project: str, key: str) -> str:
    return os.path.join(project, "work", "cache", "bundles", key)


def cmd_lookup(args):
    key = cache_key(args.op, args.input, json.loads(args.params) if args.params else None)
    man = load_manifest(args.project)
    ent = man["entries"].get(key)
    out = {"hit": bool(ent), "key": key, "entry": ent}
    if ent:
        path = os.path.join(args.project, ent["path"])
        out["path_exists"] = os.path.isfile(path)
        if not out["path_exists"]:
            out["hit"] = False
            out["reason"] = "missing_file"
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if out.get("hit") else 1)


def cmd_store(args):
    key = cache_key(args.op, args.input, json.loads(args.params) if args.params else None)
    if not os.path.isfile(args.output):
        sys.exit("output file missing")
    dest = bundle_root(args.project, key)
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, os.path.basename(args.output))
    shutil.copy2(args.output, target)
    rel = os.path.relpath(target, args.project)
    man = load_manifest(args.project)
    man["entries"][key] = {"op": args.op, "path": rel, "input": os.path.abspath(args.input)}
    save_manifest(args.project, man)
    print(target)


def cmd_probe_ffprobe(args):
    """Store ffprobe JSON for a media file if cache miss."""
    params = {"tool": "ffprobe", "entries": args.entries or "format,duration:stream=codec_type"}
    key = cache_key("ffprobe", args.input, params)
    man = load_manifest(args.project)
    if key in man["entries"] and not args.force:
        path = os.path.join(args.project, man["entries"][key]["path"])
        print(path)
        return
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", params["entries"], "-of", "json", args.input],
        text=True,
    )
    dest = bundle_root(args.project, key)
    os.makedirs(dest, exist_ok=True)
    target = os.path.join(dest, "probe.json")
    with open(target, "w") as f:
        f.write(out)
    rel = os.path.relpath(target, args.project)
    man["entries"][key] = {"op": "ffprobe", "path": rel, "input": os.path.abspath(args.input)}
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
    s.set_defaults(func=cmd_probe_ffprobe)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()