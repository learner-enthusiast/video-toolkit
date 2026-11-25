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
MSG_ID_RE = re.compile(r"\*\*Message(?:\s+ID)?:\*\*\s*(\S+)", re.I)


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
    """Explicit **Stage:** only — never infer from handoff lines."""
    block = text[:token_start]
    stage_lines = STAGE_LINE.findall(block)
    if stage_lines:
        return stage_lines[-1].lower()
    return "unknown"


def _message_id_before(text: str, token_start: int) -> str | None:
    block = text[max(0, token_start - 1200) : token_start]
    hits = MSG_ID_RE.findall(block)
    return hits[-1] if hits else None


def _took_seconds(text: str, pos: int) -> int | None:
    block = text[max(0, pos - 400) : pos]
    matches = list(TOOK_RE.finditer(block))
    if not matches:
        return None
    m = matches[-1]
    if m.group(1) is not None:
        return int(m.group(1)) * 60 + int(m.group(2))
    return int(m.group(3))


def _median(vals: list[int | float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2.0


def _percentile_nearest_rank(vals: list[int | float], p: float) -> float:
    """Nearest-rank percentile on a sorted list; p in (0,1]."""
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n == 1:
        return float(s[0])
    rank = max(1, min(n, int(p * n + 0.999999)))
    return float(s[rank - 1])


def timing_stats(vals: list[int]) -> dict | None:
    if not vals:
        return None
    return {
        "samples": len(vals),
        "total_seconds": sum(vals),
        "median_seconds": _median(vals),
        "p90_seconds": _percentile_nearest_rank(vals, 0.9),
        "definition": "median=average of middle two when even; p90=nearest-rank ceil(0.9*n)",
    }


def parse_token_lines(log_path: str) -> list[dict]:
    if not log_path or not __import__("os").path.isfile(log_path):
        return []
    with open(log_path) as fh:
        text = fh.read()
    entries = []
    seen_ids: set[str] = set()
    for m in TOKEN_RE.finditer(text):
        mid = _message_id_before(text, m.start())
        if mid and mid in seen_ids:
            continue
        if mid:
            seen_ids.add(mid)
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
                "message_id": mid,
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
    unknown_stage = sum(1 for e in entries if e.get("stage") == "unknown")

    timings = [e["took_seconds"] for e in entries if e.get("took_seconds") is not None]

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
        "unknown_stage_entries": unknown_stage,
        "totals": {"main": tot_main, "subagents": tot_sub},
        "by_stage": {"main": by_stage, "subagents": by_stage_sub},
        "by_model": {"main": by_model_main or None, "subagents": by_model_sub or None},
        "by_stage_model": {
            "main": by_stage_model_main or None,
            "subagents": by_stage_model_sub or None,
        },
        "timing": timing_stats(timings),
        "note": "Measured hook usage only; cache_read is not fresh input. Context byte estimates in token-budget.md are separate.",
    }


def _diff_bucket(a: dict | None, b: dict | None) -> dict:
    a = a or _zero()
    b = b or _zero()
    return {k: b[k] - a[k] for k in a}


def _pct_delta(base: float, cand: float) -> float | None:
    if base == 0:
        return None
    return (cand - base) / base * 100.0


def _diff_by_stage(a: dict | None, b: dict | None, *, skip_unknown: bool = True) -> dict:
    a = a or {}
    b = b or {}
    out: dict = {}
    for st in sorted(set(a) | set(b)):
        if skip_unknown and st == "unknown":
            if st in a or st in b:
                out["unknown_excluded"] = True
            continue
        if st not in a:
            out[f"only_candidate:{st}"] = b[st]
        elif st not in b:
            out[f"only_baseline:{st}"] = a[st]
        else:
            out[st] = _diff_bucket(a[st], b[st])
    return out


def _model_sets(summary: dict) -> tuple[set[str], set[str]]:
    bm = summary.get("by_model") or {}
    main = set((bm.get("main") or {}).keys())
    sub = set((bm.get("subagents") or {}).keys())
    return main, sub


def _diff_models(a: dict | None, b: dict | None) -> dict:
    a = a or {}
    b = b or {}
    out = {}
    all_models = set(a) | set(b)
    only_a = set(a) - set(b)
    only_b = set(b) - set(a)
    if only_a:
        out["only_baseline"] = sorted(only_a)
    if only_b:
        out["only_candidate"] = sorted(only_b)
    comparable = {}
    for m in sorted(all_models - only_a - only_b):
        comparable[m] = _diff_bucket(a[m], b[m])
    if comparable:
        out["comparable"] = comparable
    return out


def compare_logs(base_path: str, cand_path: str) -> dict:
    base = summarize(parse_token_lines(base_path))
    cand = summarize(parse_token_lines(cand_path))
    base_tm = (base.get("timing") or {}).get("total_seconds")
    cand_tm = (cand.get("timing") or {}).get("total_seconds")
    delta_tm = None
    if base_tm is not None and cand_tm is not None:
        delta_tm = cand_tm - base_tm
    b_models, b_sub = _model_sets(base)
    c_models, c_sub = _model_sets(cand)
    return {
        "baseline": base_path,
        "candidate": cand_path,
        "baseline_entries": base.get("entries"),
        "candidate_entries": cand.get("entries"),
        "unknown_stage_baseline": base.get("unknown_stage_entries"),
        "unknown_stage_candidate": cand.get("unknown_stage_entries"),
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
        "delta_main_pct": {
            k: _pct_delta(
                (base.get("totals") or {}).get("main", _zero()).get(k, 0),
                (cand.get("totals") or {}).get("main", _zero()).get(k, 0),
            )
            for k in _zero()
        },
        "baseline_timing": base.get("timing"),
        "candidate_timing": cand.get("timing"),
        "delta_total_seconds": delta_tm,
        "by_stage_delta_main": _diff_by_stage(
            (base.get("by_stage") or {}).get("main"),
            (cand.get("by_stage") or {}).get("main"),
        ),
        "by_model_delta_main": _diff_models(
            (base.get("by_model") or {}).get("main"),
            (cand.get("by_model") or {}).get("main"),
        ),
        "by_model_delta_subagents": _diff_models(
            (base.get("by_model") or {}).get("subagents"),
            (cand.get("by_model") or {}).get("subagents"),
        ),
        "model_sets": {
            "baseline_main": sorted(b_models),
            "candidate_main": sorted(c_models),
            "baseline_subagents": sorted(b_sub),
            "candidate_subagents": sorted(c_sub),
        },
        "model_mismatch": bool(b_models != c_models or b_sub != c_sub),
        "by_stage_model_delta_main": _diff_stage_model(
            (base.get("by_stage_model") or {}).get("main"),
            (cand.get("by_stage_model") or {}).get("main"),
        ),
        "note": "Stages unknown excluded from by_stage_delta_main. Model deltas only in comparable_models.",
    }


def _diff_stage_model(a: dict | None, b: dict | None) -> dict:
    a = a or {}
    b = b or {}
    out = {}
    for st in sorted(set(a) | set(b)):
        if st == "unknown":
            continue
        if st not in a:
            out[f"only_candidate:{st}"] = b[st]
        elif st not in b:
            out[f"only_baseline:{st}"] = a[st]
        else:
            out[st] = _diff_models(a[st], b[st])
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