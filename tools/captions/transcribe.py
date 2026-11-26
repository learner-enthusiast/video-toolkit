#!/usr/bin/env python3
"""Whisper through the asset cache: reuse a pass only when the WAV, model, flags and this script match.

usage (from work/): vt-python tools/captions/transcribe.py <project> <wav> --out-dir transcript/A \
    [--model large-v3] [--force] -- <other whisper-ctranslate2 flags, e.g. --compute_type int8 --language en>

Run the voice-cleaning gate first (pipeline/voice-cleaning.md). Always on the GPU. A pass succeeds only if
its JSON exists: whisper-ctranslate2 exits 0 on CUDA out-of-memory.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools import asset_cache, cache_events  # noqa: E402

FIXED = ("--model", "--device", "--output_dir", "--output_format", "-o", "-f")


def tool_version() -> str:
    try:
        r = subprocess.run(["whisper-ctranslate2", "--version"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip().splitlines()[-1] or "unknown"
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return "unknown"


def readable_json(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as f:
            return isinstance(json.load(f), dict)
    except (OSError, ValueError):
        return False


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    extra = []
    if "--" in argv:
        cut = argv.index("--")
        argv, extra = argv[:cut], argv[cut + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("wav")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--force", action="store_true", help="run again even on a cache hit")
    args = ap.parse_args(argv)
    clash = sorted({a.split("=")[0] for a in extra} & set(FIXED))
    if clash:
        ap.error(f"set by this tool, remove from the extra flags: {' '.join(clash)}")
    if not os.path.isfile(args.wav):
        ap.error(f"no such WAV: {args.wav}")

    params = {"model": args.model, "args": extra}
    fingerprint = dict(script=os.path.abspath(__file__), tool_version=tool_version())
    out_json = os.path.join(args.out_dir, os.path.splitext(os.path.basename(args.wav))[0] + ".json")
    found = {"hit": False, "reason": "forced"}
    if not args.force:
        found = asset_cache.lookup(args.project, args.wav, "whisper", params, **fingerprint)
    cache_events.record(args.project, "asset", "whisper", "hit" if found["hit"] else "miss", found["reason"])
    os.makedirs(args.out_dir, exist_ok=True)
    if found["hit"]:
        shutil.copyfile(found["path"], out_json)
        print(f"CACHE HIT {out_json}")
        return 0

    if os.path.exists(out_json):
        os.remove(out_json)  # a stale JSON must not pass for this run's output
    cmd = ["gpu-run", "whisper-ctranslate2", args.wav, "--model", args.model, "--device", "cuda",
           "--output_format", "json", "--output_dir", args.out_dir, *extra]
    rc = subprocess.run(cmd).returncode
    if rc or not readable_json(out_json):
        print(f"FAILED: whisper exit {rc}, no readable JSON at {out_json} (check for 'out of memory')", file=sys.stderr)
        return rc or 1
    asset_cache.store(args.project, args.wav, "whisper", out_json, params, **fingerprint)
    print(f"CACHE STORE {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
