#!/usr/bin/env python3
"""Content-addressed cache for video-inspect report.json (per project)."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

CACHE_VERSION = 1
DEFAULT_MANIFEST = "work/inspect/.cache-manifest.json"


def sha256_file(path: str, chunk=1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def probe_meta(path: str) -> dict:
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=size,duration",
                "-of",
                "json",
                path,
            ],
            text=True,
        )
        fmt = json.loads(out).get("format") or {}
        return {"size": int(fmt.get("size") or 0), "duration": float(fmt.get("duration") or 0)}
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
        return {"size": os.path.getsize(path), "duration": None}


def cache_key(video: str, args) -> str:
    meta = probe_meta(video)
    parts = [
        f"v{CACHE_VERSION}",
        sha256_file(video),
        str(meta["size"]),
        f"{meta['duration']:.2f}" if meta.get("duration") else "na",
        args.mode,
        str(args.start or 0),
        str(args.end or "end"),
        args.script_version or "unknown",
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def manifest_path(project: str) -> str:
    return os.path.join(project, DEFAULT_MANIFEST)


def load_manifest(project: str) -> dict:
    p = manifest_path(project)
    if os.path.isfile(p):
        with open(p) as f:
            return json.load(f)
    return {"entries": {}}


def save_manifest(project: str, manifest: dict) -> None:
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def cmd_lookup(args):
    key = cache_key(args.video, args)
    man = load_manifest(args.project)
    ent = man.get("entries", {}).get(key)
    out = {"cache_key": key, "hit": bool(ent), "entry": ent}
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if ent else 1)


def cmd_store(args):
    key = cache_key(args.video, args)
    man = load_manifest(args.project)
    dest_dir = os.path.join(args.project, "work", "inspect", ".cache", key)
    os.makedirs(dest_dir, exist_ok=True)
    if not os.path.isfile(args.report):
        sys.exit(f"report not found: {args.report}")
    shutil.copy2(args.report, os.path.join(dest_dir, "report.json"))
    man.setdefault("entries", {})[key] = {
        "video": os.path.abspath(args.video),
        "output_dir": os.path.relpath(dest_dir, args.project),
        "mode": args.mode,
        "reason": "stored",
    }
    save_manifest(args.project, man)
    print(dest_dir)


def cmd_restore(args):
    key = cache_key(args.video, args)
    man = load_manifest(args.project)
    ent = man.get("entries", {}).get(key)
    if not ent:
        sys.exit(2)
    src = os.path.join(args.project, ent["output_dir"], "report.json")
    if not os.path.isfile(src):
        sys.exit(3)
    out_dir = args.out_dir or os.path.join(
        args.project, "work", "inspect", os.path.splitext(os.path.basename(args.video))[0]
    )
    os.makedirs(out_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(out_dir, "report.json"))
    print(out_dir)


def add_common(sp):
    sp.add_argument("project")
    sp.add_argument("video")
    sp.add_argument("--mode", default="default")
    sp.add_argument("--start", type=float)
    sp.add_argument("--end", type=float)
    sp.add_argument("--script-version", default="video_inspect.py@project")
    return sp


def main():
    ap = argparse.ArgumentParser(description="Video inspect cache")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = add_common(sub.add_parser("lookup", help="Test cache hit"))
    s.set_defaults(func=cmd_lookup)

    s = add_common(sub.add_parser("store", help="Store report.json under cache key"))
    s.add_argument("report")
    s.set_defaults(func=cmd_store)

    s = add_common(sub.add_parser("restore", help="Copy cached report into inspect output dir"))
    s.add_argument("--out-dir")
    s.set_defaults(func=cmd_restore)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()