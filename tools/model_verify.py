#!/usr/bin/env python3
"""Print model IDs and effort support for pipeline/model-routing.md (read-only)."""
import json
import os
import subprocess
import sys

CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "model-routing.json")


def main():
    out = {"config": None, "claude_cli": None, "effort_flag": False}
    if os.path.isfile(CONFIG):
        with open(CONFIG) as f:
            out["config"] = json.load(f)
    try:
        r = subprocess.run(
            ["claude", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        help_text = r.stdout + r.stderr
        out["effort_flag"] = "--effort" in help_text
        out["model_flag"] = "--model" in help_text
        ver = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out["claude_cli"] = (ver.stdout or ver.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        out["claude_cli_error"] = str(e)

    cj = os.path.expanduser("~/.claude.json")
    if os.path.isfile(cj):
        with open(cj) as f:
            d = json.load(f)
        models = set()
        for v in d.values():
            if isinstance(v, dict) and "model" in v:
                models.add(v["model"])
        for block in d.get("clientDataCacheSlots", {}).values():
            if isinstance(block, dict) and block.get("model"):
                models.add(block["model"])
        out["recent_session_models"] = sorted(models)

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()