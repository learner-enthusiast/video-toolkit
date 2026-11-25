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
STAGE_LINE = re.compile(r"^\*\*Stage:\*\*\s*(\w+)\s*$", re.M | re.I)
STAGE_HANDOFF = re.compile(r"^### Handoff:\s*\d\s*·\s*(\w+)", re.M)
MODELS_NEW = re.compile(r";\s*models\s+main:\s*(.+?)(?:\s*\|\s*sub:\s*(.+))?$", re.I)
MODELS_LEGACY = re.compile(r";\s*models:\s*(.+)$", re.I)
MODEL_PART = re.compile(
    r"(\S+)\s+in\s+([\d,]+)\s+cw\s+([\d,]+)\s+cr\s+([\d,]+)\s+out\s+([\d,]+)",
    re.I,
)


def _ints(*parts):
    return [int(p.replace(",", "")) for p in parts]


def _zero():
    return dict(input=0, cache_write=0, cache_read=0, output=0)


def _add(dst: dict, src: dict) -> None:
    for k in dst:
        dst[k] += src.get(k) or 0


def _parse_model_bucket(text: str) -> dict[str, dict]:
    models: dict[str, dict] = {}
    for part in text.split("·"):
        pm = MODEL_PART.search(part.strip())
        if not pm:
            continue
        models[pm.group(1)] = dict(
            zip(
                ("input", "cache_write", "cache_read", "output"),
                _ints(pm.group(2), pm.group(3), pm.group(4), pm.group(5)),
            )
        )
    return models


def _parse_models(tail: str) -> tuple[dict | None, dict | None]:
    m = MODELS_NEW.search(tail)
    if m:
        return _parse_model_bucket(m.group(1)), _parse_model_bucket(m.group(2) or "")
    m = MODELS_LEGACY.search(tail)
    if m:
        legacy = _parse_model_bucket(m.group(1))
        return legacy, None
    return None, None


def _stage_for_entry(text: str, token_start: int) -> str:
    block = text[:token_start]
    stage_lines = STAGE_LINE.findall(block)
    if stage_lines:
        return stage_lines[-1].lower()
    handoffs = STAGE_HANDOFF.findall(block)
    if handoffs:
        return handoffs[-1].lower()
    return "unknown"


def parse_token_lines(log_path: str) -> list[dict]:
    if not log_path or not __import__("os").path.isfile(log_path):
        return []
    with open(log_path) as fh:
        text = fh.read()
    entries = []
    for m in TOKEN_RE.finditer(text):
        stage = _stage_for_entry(text, m.start())
        main = dict(zip(("input", "cache_write", "cache_read", "output"), _ints(*m.groups())))
        tail = text[m.end() : m.end() + 800]
        sm = SUB_RE.search(tail)
        sub = (
            dict(zip(("input", "cache_write", "cache_read", "output"), _ints(*sm.groups())))
            if sm
            else None
        )
        main_models, sub_models = _parse_models(tail)
        entries.append(
            {
                "stage": stage,
                "main": main,
                "subagents": sub,
                "models_main": main_models,
                "models_subagents": sub_models,
            }
        )
    return entries


def summarize(entries: list[dict]) -> dict:
    if not entries:
        return {"entries": 0, "totals": None, "note": "No hook token lines found"}
    tot_main = _zero()
    tot_sub = _zero()
    by_stage: dict[str, dict] = {}
    by_stage_sub: dict[str, dict] = {}
    by_model_main: dict[str, dict] = {}
    by_model_sub: dict[str, dict] = {}
    by_stage_model_main: dict[str, dict[str, dict]] = {}
    by_stage_model_sub: dict[str, dict[str, dict]] = {}

    for e in entries:
        st = e["stage"]
        by_stage.setdefault(st, _zero())
        by_stage_sub.setdefault(st, _zero())
        _add(tot_main, e["main"])
        _add(by_stage[st], e["main"])
        if e["subagents"]:
            _add(tot_sub, e["subagents"])
            _add(by_stage_sub[st], e["subagents"])
        for label, bucket, target, stage_map in (
            ("models_main", e.get("models_main"), by_model_main, by_stage_model_main),
            ("models_subagents", e.get("models_subagents"), by_model_sub, by_stage_model_sub),
        ):
            if not bucket:
                continue
            for model, t in bucket.items():
                dst = target.setdefault(model, _zero())
                _add(dst, t)
                sm = stage_map.setdefault(st, {})
                dst2 = sm.setdefault(model, _zero())
                _add(dst2, t)

    return {
        "entries": len(entries),
        "totals": {"main": tot_main, "subagents": tot_sub},
        "by_stage": {"main": by_stage, "subagents": by_stage_sub},
        "by_model": {"main": by_model_main or None, "subagents": by_model_sub or None},
        "by_stage_model": {
            "main": by_stage_model_main or None,
            "subagents": by_stage_model_sub or None,
        },
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