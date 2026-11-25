#!/usr/bin/env python3
"""Emit compact JSON job result from a finished work/jobs/*.status or a log tail."""
import argparse
import json
import os
import re
import sys
import time


def parse_status(path: str) -> dict:
    data = {"job": os.path.basename(path).replace(".status", ""), "status": "unknown"}
    if not os.path.isfile(path):
        data["status"] = "missing"
        return data
    with open(path) as f:
        text = f.read()
    for line in text.splitlines():
        if line.startswith("state="):
            data["status"] = "done" if "done" in line else "failed"
        elif line.startswith("exit="):
            data["exit_code"] = int(line.split("=", 1)[1])
        elif line.startswith("seconds="):
            data["duration_seconds"] = int(line.split("=", 1)[1])
        elif line.startswith("output="):
            data["output"] = line.split("=", 1)[1]
    log_path = path.replace(".status", ".log")
    if os.path.isfile(log_path):
        data["log"] = log_path
        with open(log_path, errors="replace") as f:
            tail = f.readlines()[-40:]
        joined = "".join(tail)
        for pat in [
            r"(CUDA out of memory)",
            r"(error)",
            r"(Error:)",
            r"(failed)",
        ]:
            m = re.search(pat, joined, re.I)
            if m:
                data["summary"] = m.group(1)[:200]
                break
        if "summary" not in data:
            data["summary"] = tail[-1].strip()[:200] if tail else "ok"
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("status_file", help="work/jobs/NN-job.status")
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args()
    json.dump(parse_status(args.status_file), sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if parse_status(args.status_file).get("status") == "done" else 1)


if __name__ == "__main__":
    main()