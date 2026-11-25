#!/usr/bin/env python3
"""Machine-readable project state (mirror of log handoffs). log.md remains authoritative."""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = 1
STAGES = ("prep", "cut", "compose", "deliver")
APPROVALS = ("script", "rough_cut", "storyboard", "stills", "final")


def state_path(project: str) -> str:
    return os.path.join(project, "project-state.json")


def default_state(project: str) -> dict:
    name = project.rstrip("/").split("/")[-1]
    return {
        "schema_version": SCHEMA_VERSION,
        "project": name,
        "project_path": project,
        "stage": "prep",
        "status": "not_started",
        "master_language": "en",
        "approvals": {k: False for k in APPROVALS},
        "artifacts": {
            "transcript": "pending",
            "edl": "pending",
            "storyboard": "pending",
            "composition": "pending",
            "final_qa": "pending",
        },
        "open_issues": [],
        "next_actions": ["Run Stage 1 · Prep per pipeline/stages.md"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def load_state(project: str) -> dict:
    p = state_path(project)
    if not os.path.isfile(p):
        return default_state(project)
    with open(p) as f:
        return json.load(f)


def save_state(project: str, state: dict) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state["schema_version"] = SCHEMA_VERSION
    p = state_path(project)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def parse_last_handoff(log_path: str) -> dict | None:
    if not os.path.isfile(log_path):
        return None
    with open(log_path) as f:
        text = f.read()
    parts = re.split(r"(?=^### Handoff:)", text, flags=re.M)
    if len(parts) < 2:
        return None
    block = parts[-1].strip()
    info: dict = {"raw": block}
    for key, pat in [
        ("stage_line", r"^### Handoff:\s*(.+)$"),
        ("decisions", r"^\*\*Decisions:\*\*\s*(.+)$"),
        ("rejected", r"^\*\*Rejected:\*\*\s*(.+)$"),
        ("open_issues", r"^\*\*Open issues:\*\*\s*(.+)$"),
        ("files", r"^\*\*Files:\*\*\s*(.+)$"),
        ("next", r"^\*\*Next:\*\*\s*(.+)$"),
    ]:
        m = re.search(pat, block, re.M)
        if m:
            info[key] = m.group(1).strip()
    return info


def sync_handoff(project: str) -> dict:
    state = load_state(project)
    handoff = parse_last_handoff(os.path.join(project, "log.md"))
    if not handoff:
        save_state(project, state)
        return state
    line = handoff.get("stage_line", "")
    m = re.search(r"(\d)\s*·\s*(\w+)", line)
    if m:
        stage_map = {"1": "prep", "2": "cut", "3": "compose", "4": "deliver"}
        state["stage"] = stage_map.get(m.group(1), state["stage"])
    if handoff.get("open_issues"):
        state["open_issues"] = [
            s.strip() for s in re.split(r"·", handoff["open_issues"]) if s.strip()
        ]
    if handoff.get("next"):
        state["next_actions"] = [handoff["next"]]
    state["status"] = "in_progress"
    nxt = (handoff.get("next") or "").lower()
    if state["stage"] in ("compose", "deliver") and "waiting for ok" not in nxt:
        state["approvals"]["rough_cut"] = True
    save_state(project, state)
    return state


def cmd_init(args):
    save_state(args.project, default_state(args.project))
    print(state_path(args.project))


def cmd_show(args):
    print(json.dumps(load_state(args.project), indent=2))


def cmd_set_stage(args):
    st = load_state(args.project)
    st["stage"] = args.stage
    st["status"] = "in_progress"
    save_state(args.project, st)


def cmd_set_approval(args):
    st = load_state(args.project)
    st["approvals"][args.name] = args.value.lower() in ("1", "true", "yes")
    save_state(args.project, st)


def cmd_sync(args):
    print(json.dumps(sync_handoff(args.project), indent=2))


def main():
    p = argparse.ArgumentParser(description="Project state for video-toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Create default project-state.json")
    s.add_argument("project")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("show", help="Print project-state.json")
    s.add_argument("project")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("set-stage", help="Set stage")
    s.add_argument("project")
    s.add_argument("stage", choices=STAGES)
    s.set_defaults(func=cmd_set_stage)

    s = sub.add_parser("set-approval", help="Set approval flag")
    s.add_argument("project")
    s.add_argument("name", choices=APPROVALS)
    s.add_argument("value")
    s.set_defaults(func=cmd_set_approval)

    s = sub.add_parser("sync-handoff", help="Update from latest ### Handoff in log.md")
    s.add_argument("project")
    s.set_defaults(func=cmd_sync)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()