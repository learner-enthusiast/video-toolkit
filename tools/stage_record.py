"""Per-stage benchmark record (docs/optimization/benchmark-protocol.md, Per-stage record).

Everything comes from files on disk. A value that wasn't measured is null; nothing is
estimated from transcript or file sizes. The Stop hook never runs this.
"""
from __future__ import annotations

import glob
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from tools import cache_events, pricing, project_state, routing_config, vt_log

SCHEMA_VERSION = 1
IST = timezone(timedelta(hours=5, minutes=30))
# Which log.md approvals gate each stage.
STAGE_APPROVALS = {"prep": ("script",), "cut": ("rough_cut",), "compose": ("storyboard", "stills"), "deliver": ("final",)}
DELEGATION_LOG = re.compile(r"^\d+-(copilot|codex|cursor-agent|cursor|haiku)-")


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def _tokens(entries: list[dict]) -> dict | None:
    if not entries:
        return None
    out = {"main": vt_log._zero(), "subagents": vt_log._zero()}
    for e in entries:
        vt_log._add(out["main"], e["main"])
        if e["subagents"]:
            vt_log._add(out["subagents"], e["subagents"])
    return out


def _model_calls(entries: list[dict], config: dict) -> dict | None:
    totals = vt_log.call_totals(entries)
    if totals is None:
        return None
    by_tier: dict[str, int] = {}
    for model, n in totals["by_model"].items():
        tier = pricing.tier_for(model, config) or "unknown"
        by_tier[tier] = by_tier.get(tier, 0) + n
    return {**totals, "by_tier": by_tier}


def _wall_time(entries: list[dict]) -> dict:
    took = [e.get("took_seconds") for e in entries]
    turn = sum(took) if entries and all(t is not None for t in took) else None
    span = None
    if turn is not None and all(e.get("started_at") for e in entries):
        ends = [_parse(e["started_at"]) + timedelta(seconds=e["took_seconds"]) for e in entries]
        span = int((max(ends) - min(_parse(e["started_at"]) for e in entries)).total_seconds())
    return {"turn_seconds": turn, "span_seconds": span}


def _cache(project: str, start: datetime | None) -> dict:
    events = cache_events.read(project)
    out: dict = {}
    for cache in ("asset", "inspect"):
        if events is None or start is None:
            out[cache] = None
            continue
        rows = [e for e in events if e.get("cache") == cache and _parse(e["ts"]) >= start]
        out[cache] = {
            "hits": sum(e["result"] == "hit" for e in rows),
            "misses": sum(e["result"] == "miss" for e in rows),
        }
        if cache == "inspect":
            out[cache]["final_qa_bypasses"] = sum(e["result"] == "bypass" for e in rows)
    return out


def _delegation(project: str, start: datetime | None) -> list[dict] | None:
    folder = os.path.join(project, "work", "delegation")
    if not os.path.isdir(folder) or start is None:
        return None
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.log"))):
        if os.path.getmtime(path) < start.timestamp():
            continue
        with open(path, errors="replace") as f:
            exits = re.findall(r"^EXIT (-?\d+)", f.read(), re.M)
        usage = None
        try:  # Copilot's --usage-output-file, written beside its log
            with open(path[: -len(".log")] + ".usage.json") as f:
                usage = json.load(f)
        except (OSError, ValueError):
            pass
        name = os.path.basename(path)
        tool = DELEGATION_LOG.match(name)
        out.append({"log": name, "tool": tool[1] if tool else None,
                    "exit_code": int(exits[-1]) if exits else None, "usage": usage})
    return out


def _user_approval(project: str, stage: str) -> bool | None:
    approvals = project_state.authoritative_approvals(project)["approvals"]
    recorded = [approvals[n] for n in STAGE_APPROVALS[stage] if approvals[n].get("status") in ("approved", "rejected", "pending")]
    if not recorded:
        return None
    return all(a["approved"] for a in recorded)


def _language(project: str) -> dict:
    """language and twin_of from project-state.json; null when there is no readable state."""
    state, err = project_state.try_load_state(project)
    state = {} if err else state
    return {"language": state.get("language"), "twin_of": state.get("twin_of")}


def _commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__),
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build_record(project: str, stage: str, *, since: str | None = None,
                 validators: str | None = None, final_qa: str | None = None) -> dict:
    config = routing_config.load_config()
    entries = [e for e in vt_log.parse_token_lines(project_state.log_path(project)) if e["stage"] == stage]
    if since:
        floor = datetime.strptime(since, "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        entries = [e for e in entries if e.get("started_at") and _parse(e["started_at"]) >= floor]
    starts = [_parse(e["started_at"]) for e in entries if e.get("started_at")]
    start = min(starts) if starts else None
    now = datetime.now(timezone.utc)
    verdict = {"pass": True, "fail": False, None: None}
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": f"{now:%Y%m%dT%H%M%SZ}-{secrets.token_hex(3)}",
        "project": os.path.basename(os.path.normpath(project)),
        **_language(project),
        "stage": stage,
        "recorded_at": now.isoformat(),
        "toolkit_commit": _commit(),
        "turns": len(entries),
        "window_start": start.isoformat() if start else None,
        "model_calls": _model_calls(entries, config),
        "tokens": _tokens(entries),
        "cost_weighted_usd": vt_log.cost_total(entries),
        "wall_time": _wall_time(entries),
        "cache": _cache(project, start),
        "delegation": _delegation(project, start),
        "quality": {
            "validators_passed": verdict[validators],
            "fresh_final_qa_passed": verdict[final_qa],
            "user_approval": _user_approval(project, stage),
        },
    }


def write_record(project: str, stage: str, **kwargs) -> str:
    record = build_record(project, stage, **kwargs)
    if not record["turns"]:
        sys.stderr.write(f"warning: no log.md turns with **Stage:** {stage}; usage fields are null "
                         "(set the stage with project_state.py at stage start)\n")
    folder = os.path.join(project, "work", "metrics")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{stage}-{record['run_id']}.json")
    with open(path, "x", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    return path
