#!/usr/bin/env python3
"""Aggregate token usage from project log.md (hook-written **Tokens:** lines)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

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
CALLS_RE = re.compile(
    r"\*\*Calls:\*\*\s*main\s*(\d+)\s*·\s*sidechain\s*(\d+)\s*·\s*subagents\s*(\d+)(?:;\s*by model:\s*(.+))?", re.I
)
COST_RE = re.compile(r"\*\*Cost:\*\*\s*weighted USD\s*([\d.]+)", re.I)
HEADER_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) IST\b", re.M)
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


def _parse_calls(footer: str) -> dict | None:
    m = CALLS_RE.search(footer)
    if not m:
        return None
    by_model = {}
    for part in (m.group(4) or "").split("·"):
        bits = part.split()
        if len(bits) == 2 and bits[1].isdigit():
            by_model[bits[0]] = int(bits[1])
    return {"main": int(m.group(1)), "sidechain": int(m.group(2)), "subagents": int(m.group(3)), "by_model": by_model}


def _started_at(before: str) -> str | None:
    """ISO start of the entry that owns a footer: its `## date time IST` header."""
    headers = HEADER_RE.findall(before)
    return f"{headers[-1][0]}T{headers[-1][1]}:00+05:30" if headers else None


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
        # The rest of the Tokens line, and the footer lines under it (up to the blank line):
        # looking further would read the next entry, and `$` would never match this one.
        tail, _, rest = text[m.end() :].partition("\n")
        footer = rest.split("\n\n", 1)[0].split("**Tokens:**", 1)[0]
        sm = SUB_RE.search(tail)
        sub = (
            dict(zip(("input", "cache_write", "cache_read", "output"), _ints(*sm.groups())))
            if sm
            else None
        )
        main_models, sub_models = _parse_models(tail)
        cost = COST_RE.search(footer)
        entries.append(
            {
                "stage": stage,
                "message_id": mid,
                "took_seconds": _took_seconds(text, m.start()),
                "main": main,
                "subagents": sub,
                "models_main": main_models,
                "models_subagents": sub_models,
                "calls": _parse_calls(footer),
                "cost_weighted_usd": float(cost.group(1)) if cost else None,
                "started_at": _started_at(text[: m.start()]),
            }
        )
    return entries


def call_totals(entries: list[dict]) -> dict | None:
    """None unless every entry has a Calls line: a partial total would look like a saving."""
    if not entries or any(not e.get("calls") for e in entries):
        return None
    out = {"main": 0, "sidechain": 0, "subagents": 0, "by_model": {}}
    for e in entries:
        for key in ("main", "sidechain", "subagents"):
            out[key] += e["calls"][key]
        for model, n in e["calls"]["by_model"].items():
            out["by_model"][model] = out["by_model"].get(model, 0) + n
    return out


def cost_total(entries: list[dict]) -> float | None:
    costs = [e.get("cost_weighted_usd") for e in entries]
    if not costs or any(c is None for c in costs):
        return None
    return round(sum(costs), 4)


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
    timing_by_stage: dict[str, list[int]] = {}
    stage_counts: dict[str, int] = {}
    for e in entries:
        st = e["stage"]
        stage_counts[st] = stage_counts.get(st, 0) + 1
        if e.get("took_seconds") is not None:
            timing_by_stage.setdefault(st, []).append(e["took_seconds"])

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

    stage_timing = {
        st: timing_stats(vals)
        for st, vals in timing_by_stage.items()
        if vals
    }
    return {
        "entries": len(entries),
        "unknown_stage_entries": unknown_stage,
        "stage_sample_counts": stage_counts,
        "totals": {"main": tot_main, "subagents": tot_sub},
        "by_stage": {"main": by_stage, "subagents": by_stage_sub},
        "by_model": {"main": by_model_main or None, "subagents": by_model_sub or None},
        "by_stage_model": {
            "main": by_stage_model_main or None,
            "subagents": by_stage_model_sub or None,
        },
        "calls": call_totals(entries),
        "cost_weighted_usd": cost_total(entries),
        "cost_weighted_usd_by_stage": {st: cost_total([e for e in entries if e["stage"] == st]) for st in stage_counts},
        "entries_without_calls_or_cost": sum(1 for e in entries if not e.get("calls") or e.get("cost_weighted_usd") is None),
        "timing": timing_stats(timings),
        "timing_by_stage": stage_timing,
        "timing_note": "Summed prompt-turn **Took** durations; not total wall-clock production time.",
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


def _pct_stage_delta(
    base_stages: dict | None, cand_stages: dict | None, deltas: dict | None
) -> dict:
    base_stages = base_stages or {}
    cand_stages = cand_stages or {}
    deltas = deltas or {}
    out = {}
    for st, delta in deltas.items():
        if not isinstance(delta, dict) or st.startswith("only_"):
            continue
        out[st] = {
            k: _pct_delta(base_stages.get(st, _zero()).get(k, 0), cand_stages.get(st, _zero()).get(k, 0))
            for k in _zero()
        }
    return out


def _stage_timing_compare(base: dict, cand: dict) -> dict:
    bs = (base.get("timing_by_stage") or {})
    cs = (cand.get("timing_by_stage") or {})
    out = {}
    for st in sorted(set(bs) | set(cs)):
        if st == "unknown":
            continue
        if st not in bs:
            out[f"only_candidate:{st}"] = cs[st]
        elif st not in cs:
            out[f"only_baseline:{st}"] = bs[st]
        else:
            bsum = bs[st].get("total_seconds")
            csum = cs[st].get("total_seconds")
            out[st] = {
                "baseline": bs[st],
                "candidate": cs[st],
                "delta_total_seconds": (csum - bsum) if bsum is not None and csum is not None else None,
            }
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
    by_stage_main = _diff_by_stage(
        (base.get("by_stage") or {}).get("main"),
        (cand.get("by_stage") or {}).get("main"),
    )
    by_stage_sub = _diff_by_stage(
        (base.get("by_stage") or {}).get("subagents"),
        (cand.get("by_stage") or {}).get("subagents"),
    )
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
        "delta_subagents_pct": {
            k: _pct_delta(
                (base.get("totals") or {}).get("subagents", _zero()).get(k, 0),
                (cand.get("totals") or {}).get("subagents", _zero()).get(k, 0),
            )
            for k in _zero()
        },
        "baseline_calls": base.get("calls"),
        "candidate_calls": cand.get("calls"),
        "delta_calls": (
            {k: cand["calls"][k] - base["calls"][k] for k in ("main", "sidechain", "subagents")}
            if base.get("calls") and cand.get("calls") else None
        ),
        "baseline_cost_weighted_usd": base.get("cost_weighted_usd"),
        "candidate_cost_weighted_usd": cand.get("cost_weighted_usd"),
        "delta_cost_weighted_usd": (
            round(cand["cost_weighted_usd"] - base["cost_weighted_usd"], 4)
            if base.get("cost_weighted_usd") is not None and cand.get("cost_weighted_usd") is not None else None
        ),
        "delta_cost_weighted_pct": (
            _pct_delta(base["cost_weighted_usd"], cand["cost_weighted_usd"])
            if base.get("cost_weighted_usd") is not None and cand.get("cost_weighted_usd") is not None else None
        ),
        "baseline_timing": base.get("timing"),
        "candidate_timing": cand.get("timing"),
        "timing_by_stage_compare": _stage_timing_compare(base, cand),
        "delta_total_seconds": delta_tm,
        "stage_sample_counts": {
            "baseline": base.get("stage_sample_counts"),
            "candidate": cand.get("stage_sample_counts"),
        },
        "by_stage_delta_main": by_stage_main,
        "by_stage_delta_subagents": by_stage_sub,
        "by_stage_delta_main_pct": _pct_stage_delta(
            (base.get("by_stage") or {}).get("main"),
            (cand.get("by_stage") or {}).get("main"),
            by_stage_main,
        ),
        "by_stage_delta_subagents_pct": _pct_stage_delta(
            (base.get("by_stage") or {}).get("subagents"),
            (cand.get("by_stage") or {}).get("subagents"),
            by_stage_sub,
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
        "by_stage_model_delta_subagents": _diff_stage_model(
            (base.get("by_stage_model") or {}).get("subagents"),
            (cand.get("by_stage_model") or {}).get("subagents"),
        ),
        "note": "Stages unknown excluded from stage deltas. Model deltas only in comparable_models.",
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


def cmd_record(args):
    from tools import stage_record

    path = stage_record.write_record(
        args.project, args.stage, since=args.since,
        validators=args.validators, final_qa=args.final_qa,
    )
    print(path)


def _side(project_or_log: str) -> dict:
    path = os.path.join(project_or_log, "log.md") if os.path.isdir(project_or_log) else project_or_log
    summary = summarize(parse_token_lines(path))
    totals = summary.get("totals")
    calls = summary.get("calls")
    return {
        "path": project_or_log,
        "turns": summary.get("entries"),
        "tokens": ({k: totals["main"][k] + totals["subagents"][k] for k in totals["main"]} if totals else None),
        "api_calls": (calls["main"] + calls["sidechain"] + calls["subagents"]) if calls else None,
        "cost_weighted_usd": summary.get("cost_weighted_usd"),
        "turn_seconds": (summary.get("timing") or {}).get("total_seconds"),
    }


def side_by_side(first: str, second: str) -> dict:
    """English project vs its Hindi twin: both columns and the second as a share of the first.
    Anything either side didn't measure stays null."""
    a, b = _side(first), _side(second)

    def share(x, y):
        return round(y / x, 3) if x and y is not None else None

    ratio = {k: share(a[k], b[k]) for k in ("turns", "api_calls", "cost_weighted_usd", "turn_seconds")}
    ratio["tokens"] = ({k: share(a["tokens"][k], b["tokens"][k]) for k in a["tokens"]}
                       if a["tokens"] and b["tokens"] else None)
    return {"first": a, "second": b, "second_over_first": ratio}


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
    s = sub.add_parser("record", help="write work/metrics/<stage>-<run_id>.json (stage handoff step)")
    s.add_argument("project")
    s.add_argument("--stage", required=True, choices=("prep", "cut", "compose", "deliver"))
    s.add_argument("--since", help="only turns started at or after this IST time, 'YYYY-MM-DD HH:MM'")
    s.add_argument("--validators", choices=("pass", "fail"), help="result of the validators you ran; omit if not run")
    s.add_argument("--final-qa", choices=("pass", "fail"), help="result of the fresh final QA; omit if not run")
    s.set_defaults(func=cmd_record)
    s = sub.add_parser("breakdown")
    s.add_argument("log_md")
    s.set_defaults(func=cmd_breakdown)

    def cmd_compare(args):
        result = (side_by_side(args.baseline, args.candidate) if args.side_by_side
                  else compare_logs(args.baseline, args.candidate))
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")

    s = sub.add_parser("compare")
    s.add_argument("baseline")
    s.add_argument("candidate")
    s.add_argument("--side-by-side", action="store_true",
                   help="two project folders or logs in two columns, e.g. English and its Hindi twin")
    s.set_defaults(func=cmd_compare)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()