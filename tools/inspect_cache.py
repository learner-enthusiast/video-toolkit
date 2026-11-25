#!/usr/bin/env python3
"""Content-addressed cache for full video-inspect output directories."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

CACHE_SCHEMA = 2
MANIFEST = "work/inspect/.cache-manifest.json"
REQUIRED_FOR_FULL = ("report.json",)
REQUIRED_FOR_VISUAL = ("report.json", "contact_sheet.jpg")
OPTIONAL_GLOBS = ("sheet_*.jpg", "keyframes/*")


def sha256_file(path: str, chunk=1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
            timeout=30,
        )
        fmt = json.loads(out).get("format") or {}
        return {"size": int(fmt.get("size") or 0), "duration": float(fmt.get("duration") or 0)}
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, subprocess.TimeoutExpired):
        return {"size": os.path.getsize(path), "duration": None}


def hash_paths(paths: list[str]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        if os.path.isfile(p):
            h.update(p.encode())
            h.update(sha256_file(p).encode())
    return h.hexdigest()[:16]


def fingerprint(video: str, args) -> str:
    meta = probe_meta(video)
    parts = [
        f"schema{CACHE_SCHEMA}",
        sha256_file(video),
        str(meta["size"]),
        f"{meta['duration']:.3f}" if meta.get("duration") is not None else "na",
        args.mode,
        str(args.start if args.start is not None else 0),
        str(args.end if args.end is not None else "end"),
    ]
    if args.inspect_script:
        parts.append(hash_paths([args.inspect_script]))
    if args.ocr_script:
        parts.append(hash_paths([args.ocr_script]))
    if args.config_hash:
        parts.append(args.config_hash)
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def manifest_path(project: str) -> str:
    return os.path.join(project, MANIFEST)


def load_manifest(project: str) -> dict:
    p = manifest_path(project)
    if os.path.isfile(p):
        with open(p) as f:
            data = json.load(f)
        if data.get("schema") != CACHE_SCHEMA:
            return {"schema": CACHE_SCHEMA, "entries": {}}
        return data
    return {"schema": CACHE_SCHEMA, "entries": {}}


def save_manifest_atomic(project: str, manifest: dict) -> None:
    manifest["schema"] = CACHE_SCHEMA
    p = manifest_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".manifest-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        os.replace(tmp, p)
    except Exception:
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise


def bundle_dir(project: str, key: str) -> str:
    return os.path.join(project, "work", "inspect", ".cache", key)


def validate_bundle(path: str, thorough: bool) -> list[str]:
    missing = []
    for req in REQUIRED_FOR_VISUAL if thorough else REQUIRED_FOR_FULL:
        if not os.path.isfile(os.path.join(path, req)):
            missing.append(req)
    manifest = os.path.join(path, "bundle.json")
    if not os.path.isfile(manifest):
        missing.append("bundle.json")
    return missing


def write_bundle_meta(bundle: str, meta: dict) -> None:
    with open(os.path.join(bundle, "bundle.json"), "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")


def cmd_lookup(args):
    key = fingerprint(args.video, args)
    project = args.project
    man = load_manifest(project)
    ent = man.get("entries", {}).get(key)
    thorough_required = args.for_final or args.mode == "thorough"
    reason = "miss"
    hit = False
    if ent:
        bpath = os.path.join(project, ent["bundle_dir"])
        missing = validate_bundle(bpath, thorough_required)
        if missing:
            reason = f"incomplete:{','.join(missing)}"
        elif thorough_required and ent.get("mode") != "thorough" and not args.allow_non_thorough:
            reason = "not_thorough_for_final_qa"
        elif thorough_required and ent.get("stale_for_final"):
            reason = "cached_intermediate_only"
        else:
            hit = True
            reason = "hit"
    out = {
        "cache_key": key,
        "hit": hit,
        "reason": reason,
        "for_final_qa": bool(thorough_required),
        "entry": ent,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if hit else 1)


def _atomic_copy_tree(src: str, dest: str) -> None:
    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)
    tmp = dest + ".tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.rename(tmp, dest)


def cmd_store(args):
    key = fingerprint(args.video, args)
    project = args.project
    src_dir = args.inspect_dir
    if not os.path.isdir(src_dir):
        sys.exit(f"inspect dir not found: {src_dir}")
    dest = bundle_dir(project, key)
    with tempfile.TemporaryDirectory() as staging:
        shutil.copytree(src_dir, os.path.join(staging, "bundle"), dirs_exist_ok=True)
        meta = {
            "key": key,
            "video": os.path.abspath(args.video),
            "mode": args.mode,
            "stored_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "stale_for_final": args.mode != "thorough",
            "artifacts": sorted(os.listdir(os.path.join(staging, "bundle"))),
        }
        write_bundle_meta(os.path.join(staging, "bundle"), meta)
        _atomic_copy_tree(os.path.join(staging, "bundle"), dest)
    man = load_manifest(project)
    man.setdefault("entries", {})[key] = {
        "bundle_dir": os.path.relpath(dest, project),
        "mode": args.mode,
        "video": os.path.abspath(args.video),
        "reason": "stored",
    }
    save_manifest_atomic(project, man)
    json.dump({"cache_key": key, "bundle": dest}, sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_restore(args):
    key = fingerprint(args.video, args)
    project = args.project
    man = load_manifest(project)
    ent = man.get("entries", {}).get(key)
    if not ent:
        sys.exit(2)
    src = os.path.join(project, ent["bundle_dir"])
    missing = validate_bundle(src, args.for_final or args.mode == "thorough")
    if missing:
        sys.exit(f"bundle incomplete: {missing}")
    out_dir = args.out_dir or os.path.join(
        project, "work", "inspect", os.path.splitext(os.path.basename(args.video))[0]
    )
    if os.path.isdir(out_dir) and os.listdir(out_dir) and not args.force:
        sys.exit("out-dir non-empty; pass --force")
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(src):
        if name == "bundle.json":
            continue
        sp = os.path.join(src, name)
        dp = os.path.join(out_dir, name)
        if os.path.isdir(sp):
            if os.path.exists(dp):
                shutil.rmtree(dp)
            shutil.copytree(sp, dp)
        else:
            shutil.copy2(sp, dp)
    print(out_dir)


def cmd_status(args):
    man = load_manifest(args.project)
    json.dump({"schema": man.get("schema"), "entry_count": len(man.get("entries", {}))}, sys.stdout, indent=2)
    sys.stdout.write("\n")


def add_common(sp):
    sp.add_argument("project")
    sp.add_argument("video")
    sp.add_argument("--mode", default="default")
    sp.add_argument("--start", type=float)
    sp.add_argument("--end", type=float)
    sp.add_argument("--inspect-script", help="work/scripts/video_inspect.py for hash")
    sp.add_argument("--ocr-script")
    sp.add_argument("--config-hash", default="")


def main():
    ap = argparse.ArgumentParser(description="Video inspect artifact cache")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = add_common(sub.add_parser("lookup"))
    s.add_argument("--for-final", action="store_true", help="Require thorough bundle for hit")
    s.add_argument("--allow-non-thorough", action="store_true")
    s.set_defaults(func=cmd_lookup)

    s = add_common(sub.add_parser("store"))
    s.add_argument("inspect_dir", help="work/inspect/<deliverable>/ with artifacts")
    s.set_defaults(func=cmd_store)

    s = add_common(sub.add_parser("restore"))
    s.add_argument("--out-dir")
    s.add_argument("--for-final", action="store_true")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_restore)

    s = sub.add_parser("status")
    s.add_argument("project")
    s.set_defaults(func=cmd_status)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()