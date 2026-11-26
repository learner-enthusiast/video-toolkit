#!/usr/bin/env python3
"""SessionStart hook: print a compact brief of the current project (pipeline/stages.md).

Reads `.current-project` (SessionStart has no prompt) and prints the project state,
the approvals from log.md, open issues and the latest `### Handoff` block, capped at
MAX_BYTES. Plain stdout is added to the session context. Silent, exit 0 on any error.
"""
import json
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tools import project_state as pst  # noqa: E402
from tools.hooks import projlog  # noqa: E402

MAX_BYTES = 4096
HANDOFF = re.compile(r"^### Handoff\b", re.M)
SECTION = re.compile(r"^## ", re.M)


def latest_handoff(text: str) -> tuple[int, str] | None:
    """(line number, block) of the last handoff, up to the next `## ` entry."""
    found = list(HANDOFF.finditer(text))
    if not found:
        return None
    start = found[-1].start()
    end = SECTION.search(text, start)
    block = text[start:end.start() if end else len(text)].strip()
    return text.count("\n", 0, start) + 1, block


def truncate(text: str, max_bytes: int, pointer: str) -> str:
    data = text.encode()
    if len(data) <= max_bytes:
        return text
    tail = f"\n… truncated; {pointer}\n"
    keep = data[: max(0, max_bytes - len(tail.encode()))].decode(errors="ignore")
    return keep.rsplit("\n", 1)[0] + tail


def build_brief(root: str) -> str | None:
    rel, _ = projlog.read_current_project(root)
    if not rel or not projlog.is_project(root, rel):
        return None
    project = os.path.join(root, rel)
    state, err = pst.try_load_state(project)
    if err not in (None, "NO_STATE"):
        return None  # corrupt state: say nothing, the normal stage-start reads apply
    log_file = pst.log_path(project)
    if not os.path.isfile(log_file):
        return None
    with open(log_file, encoding="utf-8") as f:
        text = f.read()

    out = [
        f"# Session brief: {rel}",
        "Last project worked on (`.current-project`). Ignore it if this session is about something else. "
        "log.md wins on conflict.",
    ]
    if state:
        out.append(f"State: stage={state.get('stage')} · status={state.get('status')} · "
                   f"updated={state.get('updated_at')}")
        for key, label in (("next_actions", "Next"), ("open_issues", "Open issues (state)")):
            if state.get(key):
                out.append(f"{label}: " + " · ".join(map(str, state[key])))
    else:
        out.append("State: no project-state.json.")
    approvals = pst.authoritative_approvals(project)["approvals"]
    out.append("Approvals (log.md): "
               + " · ".join(f"{name}={approvals[name]['status']}" for name in pst.APPROVALS))

    handoff = latest_handoff(text)
    if not handoff:
        out.append("Latest handoff: none in log.md.")
        return truncate("\n".join(out) + "\n", MAX_BYTES, f"read {rel}/log.md")
    line, block = handoff
    out.append(f"Latest handoff ({rel}/log.md line {line}; open issues are listed in it):")
    out.append("")
    out.append(block)
    return truncate("\n".join(out) + "\n", MAX_BYTES, f"read {rel}/log.md from line {line}")


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        brief = build_brief(projlog.repo_root(data))
        if brief:
            sys.stdout.write(brief)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
