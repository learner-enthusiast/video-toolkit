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
TOOK_RE = re.compile(
    r"\*\*Took\*\*\s*(?:(\d+)\s*m\s+(\d+)\s*s|(\d+)\s*s)",
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


def _took_seconds(text: str, pos: int) -> int | None:
    block = text[max(0, pos - 400) : pos]
    matches = list(TOOK_RE.finditer(block))
    if not matches:
        return None
    m = matches[-1]
    if m.group(1) is not None:
        return int(m.group(1)) * 60 + int(m.group(2))
    return int(m.group(3))


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
                "took_seconds": _took_seconds(text, m.start()),
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

    timings = [e["took_seconds"] for e in entries if e.get("took_seconds") is not None]
    timing_stats = None
    if timings:
        timings.sort()
        mid = timings[len(timings) // 2]
        timing_stats = {
            "samples": len(timings),
            "total_seconds": sum(timings),
            "median_seconds": mid,
            "p90_seconds": timings[int(len(timings) * 0.9) - 1] if len(timings) > 1 else mid,
        }

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
        "timing": timing_stats,
        "note": "Measured hook usage only; cache_read is not fresh input. Context byte estimates in token-budget.md are separate.",
    }


def _diff_bucket(a: dict | None, b: dict | None) -> dict:
    a = a or _zero()
    b = b or _zero()
    return {k: b[k] - a[k] for k in a}


def compare_logs(base_path: str, cand_path: str) -> dict:
    base = summarize(parse_token_lines(base_path))
    cand = summarize(parse_token_lines(cand_path))
    return {
        "baseline": base_path,
        "candidate": cand_path,
        "baseline_totals": base.get("totals"),
        "candidate_totals": cand.get("totals"),
        "delta_main": _diff_bucket(
            (base.get("totals") or {}).get("main"),
            (cand.get("totals") or {}).get("main"),
        ),
        "delta_subagents": _diff_bucket(
            (base.get("totals") or {}).get("subagents"),
            (cand.get("totals") or {}).get("subagents"),
        ),
        "baseline_timing": base.get("timing"),
        "candidate_timing": cand.get("timing"),
        "by_stage_delta_main": _diff_by_stage(
            (base.get("by_stage") or {}).get("main"),
            (cand.get("by_stage") or {}).get("main"),
        ),
        "note": "Stages present in only one log are flagged with only_* keys.",
    }


def _diff_by_stage(a: dict | None, b: dict | None) -> dict:
    a = a or {}
    b = b or {}
    out = {}
    for st in sorted(set(a) | set(b)):
        if st not in a:
            out[f"only_candidate:{st}"] = b[st]
        elif st not in b:
            out[f"only_baseline:{st}"] = a[st]
        else:
            out[st] = _diff_bucket(a[st], b[st])
    return out


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

    def cmd_compare(args):
        json.dump(compare_logs(args.baseline, args.candidate), sys.stdout, indent=2)
        sys.stdout.write("\n")

    s = sub.add_parser("compare")
    s.add_argument("baseline")
    s.add_argument("candidate")
    s.set_defaults(func=cmd_compare)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()