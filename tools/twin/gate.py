#!/usr/bin/env python3
"""May /hindi-twin start? Only on a delivered, approved English project that a twin can reuse.

usage: vt-python tools/twin/gate.py projects/<name>-hi      exit 0 = go, 1 = refused (reasons listed)
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools import project_state as pst  # noqa: E402
from tools.script_beats import id_problems, parse_beats  # noqa: E402
from tools.twin import common  # noqa: E402

TRAILER_DATA = re.compile(r"\btrailerRanges\b|data/trailer_ranges\.json")
AT_CALL = re.compile(r"""(?<![\w.])(?:at|end)\(\s*['"`]""")


def source_text(src: str) -> str:
    """The project's own scene code: not the shared library link, and not the stock cue library."""
    text = []
    for folder, dirs, files in os.walk(src):  # the shared library symlink isn't followed
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for name in files:
            if name.endswith((".ts", ".tsx")) and name != "cues.ts":
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    text.append(f.read())
    return "\n".join(text)


def final_qa_passed(english: str) -> bool:
    """The latest `**Final QA:**` line in log.md, else the latest Deliver stage record."""
    log = pst.log_path(english)
    if os.path.isfile(log):
        with open(log, encoding="utf-8") as f:
            lines = re.findall(r"^\*\*Final QA:\*\*\s*(pass|fail)", f.read(), re.M | re.I)
        if lines:
            return lines[-1].lower() == "pass"
    records = sorted(glob.glob(os.path.join(english, "work", "metrics", "deliver-*.json")))
    if records:
        with open(records[-1], encoding="utf-8") as f:
            return json.load(f).get("quality", {}).get("fresh_final_qa_passed") is True
    return False


def problems(twin: str) -> list[str]:
    state = common.read_state(twin)
    if state.get("language") != "hi" or not state.get("twin_of"):
        return [f"{twin} is not a Hindi twin project (tools/twin/new_twin.py)"]
    english = common.english_of(twin)
    if not os.path.isdir(english):
        return [f"English project not found: {english}"]
    out = []
    approval = pst.authoritative_approvals(english)["approvals"]["final"]
    if not approval["approved"]:
        out.append(f"English has no final approval in log.md (**Approval:** final=approved); status: {approval['status']}")
    if not final_qa_passed(english):
        out.append("English has no passed final QA (**Final QA:** pass in log.md, or a Deliver record with fresh_final_qa_passed)")
    if not common.english_main(english):
        out.append(f"no single delivered main video in {english}/out/*_9x16.mp4")
    remotion = os.path.join(english, "work", "remotion")
    cues_path = os.path.join(remotion, "public", "data", "cues.json")
    cues = {}
    if os.path.isfile(cues_path):
        with open(cues_path, encoding="utf-8") as f:
            cues = json.load(f)
    if not cues:
        out.append("the English project has no named cues (public/data/cues.json): scenes built with at() can't be reused")
    code = source_text(os.path.join(remotion, "src")) if os.path.isdir(os.path.join(remotion, "src")) else ""
    if not code:
        out.append("English remotion/src not found")
    else:
        left = len(AT_CALL.findall(re.sub(r"export const (at|end)\b.*", "", code)))
        if left:
            out.append(f"English scenes still call at()/end() with spoken phrases ({left} place(s))")
        if not TRAILER_DATA.search(code):
            out.append("the English trailer doesn't read trailerRanges / public/data/trailer_ranges.json (pipeline/composition.md)")
    script = os.path.join(twin, "script.md")
    if not os.path.isfile(script):
        out.append("the twin has no script.md (the Hindi script)")
    else:
        with open(script, encoding="utf-8") as f:
            ids = [b["id"] for b in parse_beats(f.read())]
        bad = id_problems(ids) or ([] if any(ids) else ["no beat IDs"])
        out += [f"Hindi script: {p}" for p in bad]
        missing = sorted({c["beat"] for c in cues.values()} - set(ids))
        if missing and not bad:
            out.append(f"Hindi script lacks beats the English cues use: {', '.join(missing)}")
    return out


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    found = problems(sys.argv[1])
    if found:
        print("Hindi twin REFUSED:\n- " + "\n- ".join(found))
        return 1
    print("Hindi twin gate: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
