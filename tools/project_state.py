#!/usr/bin/env python3
"""Machine-readable project state (mirror of log). log.md is authoritative."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
from datetime import datetime, timezone

APPROVAL_STATUSES = ("approved", "rejected", "pending")

SCHEMA_VERSION = 1
STAGES = ("prep", "cut", "compose", "deliver")
APPROVALS = ("script", "rough_cut", "storyboard", "stills", "final")
APPROVAL_LINE = re.compile(r"^\*\*Approval:\*\*\s*(.+)$", re.M | re.I)
APPROVAL_KV = re.compile(r"(\w+)=(approved|rejected|pending)", re.I)


def state_path(project: str) -> str:
    return os.path.join(project, "project-state.json")


def log_path(project: str) -> str:
    return os.path.join(project, "log.md")


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
        "approval_evidence": {k: "none" for k in APPROVALS},
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
        st = json.load(f)
    st.setdefault("approval_evidence", {k: "none" for k in APPROVALS})
    return st


def try_load_state(project: str) -> tuple[dict | None, str | None]:
    """Return (state, error_code) — error_code set when JSON is unreadable."""
    p = state_path(project)
    if not os.path.isfile(p):
        return None, "NO_STATE"
    try:
        with open(p) as f:
            return json.load(f), None
    except json.JSONDecodeError:
        return None, "INVALID_STATE_JSON"
    except OSError:
        return None, "INVALID_STATE_JSON"


def save_state(project: str, state: dict) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state["schema_version"] = SCHEMA_VERSION
    p = state_path(project)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def parse_approvals_from_log(text: str) -> dict[str, dict]:
    """Latest approval line per key: {name: {value, line_index, raw}}."""
    found: dict[str, dict] = {}
    for m in APPROVAL_LINE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        for kv in APPROVAL_KV.finditer(m.group(1)):
            key = kv.group(1).lower()
            if key not in APPROVALS:
                continue
            found[key] = {
                "value": kv.group(2).lower(),
                "line": line_no,
                "raw": m.group(0).strip(),
            }
    return found


def authoritative_approvals(project: str) -> dict:
    lp = log_path(project)
    if not os.path.isfile(lp):
        return {
            "source": "missing_log",
            "approvals": {k: {"approved": False, "evidence": "missing_log"} for k in APPROVALS},
        }
    with open(lp) as f:
        text = f.read()
    parsed = parse_approvals_from_log(text)
    out = {}
    for k in APPROVALS:
        if k in parsed:
            out[k] = {
                "approved": parsed[k]["value"] == "approved",
                "evidence": parsed[k]["raw"],
                "line": parsed[k]["line"],
                "status": parsed[k]["value"],
            }
        else:
            out[k] = {"approved": False, "evidence": "none", "status": "unverified"}
    return {"source": "log.md", "approvals": out, "parsed_lines": len(parsed)}


def reconcile(project: str) -> dict:
    """Compare log approvals to project-state.json."""
    auth = authoritative_approvals(project)
    state = load_state(project)
    st_ap = state.get("approvals") or {}
    issues = []
    for k in APPROVALS:
        log_ok = auth["approvals"][k]["approved"]
        st_ok = bool(st_ap.get(k))
        if log_ok != st_ok:
            issues.append(
                {
                    "code": "STATE_OUT_OF_SYNC",
                    "approval": k,
                    "log": log_ok,
                    "state": st_ok,
                    "log_evidence": auth["approvals"][k].get("evidence"),
                }
            )
    return {"authoritative": auth, "state_file": st_ap, "issues": issues}


def parse_last_handoff(log_file: str) -> dict | None:
    if not os.path.isfile(log_file):
        return None
    with open(log_file) as f:
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
    handoff = parse_last_handoff(log_path(project))
    auth = authoritative_approvals(project)
    for k in APPROVALS:
        state["approvals"][k] = auth["approvals"][k]["approved"]
        state["approval_evidence"][k] = auth["approvals"][k].get("evidence", "none")
    if handoff:
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


def _append_log_line(project: str, line: str) -> None:
    lp = log_path(project)
    os.makedirs(os.path.dirname(lp) or ".", exist_ok=True)
    lock = lp + ".lock"
    with open(lock, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            lead = ""
            if os.path.isfile(lp) and os.path.getsize(lp):
                with open(lp, "rb") as f:
                    if not f.read().endswith(b"\n"):
                        lead = "\n"
            else:
                lead = ""
            with open(lp, "a") as f:
                f.write(f"{lead}{line}\n")
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def cmd_record_approval(args):
    status = args.status.lower()
    if status not in APPROVAL_STATUSES:
        sys.exit(f"status must be one of: {', '.join(APPROVAL_STATUSES)}")
    if not os.path.isfile(log_path(args.project)):
        sys.exit("log.md missing; create the project first")
    _append_log_line(args.project, f"**Approval:** {args.name}={status}")
    sync_handoff(args.project)
    print(log_path(args.project))


def cmd_set_approval(args):
    sys.stderr.write(
        "set-approval is deprecated: approvals must be recorded in log.md.\n"
        "Use: vt-python tools/project_state.py record-approval "
        f"{args.project} {args.name} approved|rejected|pending\n"
    )
    sys.exit(2)


def cmd_sync(args):
    print(json.dumps(sync_handoff(args.project), indent=2))


def cmd_reconcile(args):
    print(json.dumps(reconcile(args.project), indent=2))


def main():
    p = argparse.ArgumentParser(description="Project state for video-toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_proj(name, func):
        s = sub.add_parser(name)
        s.add_argument("project")
        s.set_defaults(func=func)

    add_proj("init", cmd_init)
    add_proj("show", cmd_show)
    add_proj("sync-handoff", cmd_sync)
    add_proj("reconcile", cmd_reconcile)

    s = sub.add_parser("set-stage")
    s.add_argument("project")
    s.add_argument("stage", choices=STAGES)
    s.set_defaults(func=cmd_set_stage)

    s = sub.add_parser("set-approval")
    s.add_argument("project")
    s.add_argument("name", choices=APPROVALS)
    s.add_argument("value")
    s.set_defaults(func=cmd_set_approval)

    s = sub.add_parser("record-approval")
    s.add_argument("project")
    s.add_argument("name", choices=APPROVALS)
    s.add_argument("status", choices=APPROVAL_STATUSES)
    s.set_defaults(func=cmd_record_approval)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()