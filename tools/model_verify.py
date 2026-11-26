#!/usr/bin/env python3
"""Validate model-routing config and local Claude Code capabilities (read-only)."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.routing_config import load_config, validate_claude_files, validate_config, tier_id  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG = os.path.join(ROOT, "config", "model-routing.json")


def cli_capabilities() -> dict:
    out = {"claude_cli": None, "model_flag": False, "effort_flag": False, "effort_values": []}
    try:
        help_r = subprocess.run(["claude", "--help"], capture_output=True, text=True, timeout=15)
        ht = help_r.stdout + help_r.stderr
        out["model_flag"] = "--model" in ht
        out["effort_flag"] = "--effort" in ht
        ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=10)
        out["claude_cli"] = (ver.stdout or ver.stderr).strip()
        if m := re.search(r"--effort\s*<(\w+)>", ht):
            out["effort_values"] = ["low", "medium", "high"]
    except (OSError, subprocess.TimeoutExpired) as e:
        out["error"] = str(e)
    return out


def local_model_hints() -> dict:
    """Recent session model strings only; not proof of account access."""
    hints = {"recent_session_models": [], "status": "unverified"}
    cj = os.path.expanduser("~/.claude.json")
    if not os.path.isfile(cj):
        hints["status"] = "no_local_config"
        return hints
    try:
        with open(cj) as f:
            d = json.load(f)
    except (OSError, json.JSONDecodeError):
        hints["status"] = "unreadable"
        return hints
    models = set()
    slots = d.get("clientDataCacheSlots") or {}
    for block in slots.values():
        if isinstance(block, dict) and block.get("model"):
            models.add(block["model"])
    hints["recent_session_models"] = sorted(models)
    hints["status"] = "hints_only"
    return hints


def verify_model_ids(config: dict, hints: dict) -> list[dict]:
    results = []
    seen = set(hints.get("recent_session_models") or [])
    for tier, block in (config.get("models") or {}).items():
        mid = block.get("id")
        if not mid:
            results.append({"tier": tier, "id": None, "availability": "invalid"})
            continue
        if seen and mid in seen:
            avail = "seen_in_recent_sessions"
        elif seen:
            avail = "unverified"
        else:
            avail = "unverified"
        results.append({"tier": tier, "id": mid, "availability": avail})
    return results


def probe_model(model_id: str, timeout: int) -> dict:
    """Opt-in: makes a real Claude Code request."""
    try:
        r = subprocess.run(
            ["claude", "-p", "Reply exactly: OK", "--model", model_id, "--max-turns", "1"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "model": model_id,
            "exit_code": r.returncode,
            "ok": "OK" in (r.stdout or ""),
            "note": "This invocation consumed API/subscription usage",
        }
    except subprocess.TimeoutExpired:
        return {"model": model_id, "exit_code": -1, "ok": False, "note": "timeout"}
    except OSError as e:
        return {"model": model_id, "error": str(e)}


def build_report(config_path: str | None, probe: str | None, probe_timeout: int) -> dict:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_valid": False,
        "config_errors": [],
        "cli": cli_capabilities(),
        "local_hints": local_model_hints(),
        "configured_models": [],
        "vision_qa_policy": (config.get("subagents") or {}).get("vision_qa") if (config := load_config(config_path)) else None,
    }
    report["config_errors"] = validate_config(config) + validate_claude_files(config, ROOT)
    report["config_valid"] = not report["config_errors"]
    report["configured_models"] = verify_model_ids(config, report["local_hints"])
    report["creative_tier_id"] = tier_id(config, "creative")
    if probe:
        report["probe"] = probe_model(probe, probe_timeout)
    report["verified_at_note"] = (
        "Update config verified_at only after manual review of this report; "
        "hints do not prove subscription access."
    )
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--probe", metavar="MODEL_ID", help="Opt-in live model probe (uses quota)")
    ap.add_argument("--probe-timeout", type=int, default=90)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()
    report = build_report(args.config, args.probe if not args.validate_only else None, args.probe_timeout)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if report["config_valid"] else 1)


if __name__ == "__main__":
    main()