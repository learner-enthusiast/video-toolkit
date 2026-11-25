#!/usr/bin/env python3
"""Aggregate token usage from project log.md (hook-written **Tokens:** lines)."""
from __future__ import annotations

import argparse
import json
import re
import sys

TOKEN_RE = re.compile(
    r"\*\*Tokens:\*\*\s*input\s*([\d,]+)\s*·\s*cache write\s*([\d,]+)\s*·\s*cache read\s*([\d,]+)\s*·\s*output\s*([\d,]+)",
    re.I,
)
SUB_RE = re.compile(
    r"subagents:\s*input\s*([\d,]+)\s*·\s*cache write\s*([\d,]+)\s*·\s*cache read\s*([\d,]+)\s*·\s*output\s*([\d,]+)",
    re.I,
)
STAGE_RE = re.compile(r"^### Handoff:\s*\d\s*·\s*(\w+)", re.M)


def _ints(*parts):
    return [int(p.replace(",", "")) for p in parts]


def parse_token_lines(log_path: str) -> list[dict]:
    if not log_path or not __import__("os").path.isfile(log_path):
        return []
    text = open(log_path).read()
    stages = STAGE_RE.findall(text)
    stage_iter = iter(stages)
    current_stage = "unknown"
    entries = []
    for m in TOKEN_RE.finditer(text):
        before = text[: m.start()]
        if "### Handoff:" in before:
            last = list(STAGE_RE.finditer(before))
            if last:
                current_stage = last[-1].group(1).lower()
        main = dict(zip(("input", "cache_write", "cache_read", "output"), _ints(*m.groups())))
        sub = None
        tail = text[m.end() : m.end() + 400]
        sm = SUB_RE.search(tail)
        if sm:
            sub = dict(zip(("input", "cache_write", "cache_read", "output"), _ints(*sm.groups())))
        entries.append({"stage": current_stage, "main": main, "subagents": sub})
    return entries


def summarize(entries: list[dict]) -> dict:
    if not entries:
        return {"entries": 0, "totals": None, "note": "No hook token lines found"}
    tot_main = dict(input=0, cache_write=0, cache_read=0, output=0)
    tot_sub = dict(input=0, cache_write=0, cache_read=0, output=0)
    by_stage: dict[str, dict] = {}
    for e in entries:
        for k in tot_main:
            tot_main[k] += e["main"][k]
        if e["subagents"]:
            for k in tot_sub:
                tot_sub[k] += e["subagents"][k]
        st = e["stage"]
        by_stage.setdefault(st, dict(input=0, cache_write=0, cache_read=0, output=0))
        for k in tot_main:
            by_stage[st][k] += e["main"][k]
    return {
        "entries": len(entries),
        "totals": {"main": tot_main, "subagents": tot_sub},
        "by_stage": by_stage,
        "note": "Categories kept separate; cache_read is not fresh input cost",
    }


def cmd_summary(args):
    entries = parse_token_lines(args.log_md)
    json.dump(summarize(entries), sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_breakdown(args):
    json.dump(parse_token_lines(args.log_md), sys.stdout, indent=2)
    sys.stdout.write("\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary")
    s.add_argument("log_md")
    s.set_defaults(func=cmd_summary)
    s = sub.add_parser("breakdown")
    s.add_argument("log_md")
    s.set_defaults(func=cmd_breakdown)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()