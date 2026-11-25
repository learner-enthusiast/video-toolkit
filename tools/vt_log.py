#!/usr/bin/env python3
"""Aggregate token usage from a project log.md (hook-written Tokens lines)."""
import argparse
import json
import re
import sys


def parse_tokens(log_path: str) -> list:
    entries = []
    if not log_path or not __import__("os").path.isfile(log_path):
        return entries
    with open(log_path) as f:
        text = f.read()
    for m in re.finditer(
        r"\*\*Tokens:\*\*\s*input\s*([\d,]+)\s*·\s*cache write\s*([\d,]+)\s*·\s*cache read\s*([\d,]+)\s*·\s*output\s*([\d,]+)",
        text,
    ):
        entries.append(
            {
                "input": int(m.group(1).replace(",", "")),
                "cache_write": int(m.group(2).replace(",", "")),
                "cache_read": int(m.group(3).replace(",", "")),
                "output": int(m.group(4).replace(",", "")),
            }
        )
    return entries


def summarize(entries: list) -> dict:
    if not entries:
        return {"entries": 0, "totals": None, "note": "No hook token lines found"}
    tot = dict(input=0, cache_write=0, cache_read=0, output=0)
    for e in entries:
        for k in tot:
            tot[k] += e[k]
    return {"entries": len(entries), "totals": tot}


def cmd_summary(args):
    json.dump(summarize(parse_tokens(args.log_md)), sys.stdout, indent=2)
    sys.stdout.write("\n")


def main():
    ap = argparse.ArgumentParser(description="Summarize token lines from log.md")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary", help="Sum Tokens: lines from log.md")
    s.add_argument("log_md", help="projects/<name>/log.md")
    s.set_defaults(func=cmd_summary)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()