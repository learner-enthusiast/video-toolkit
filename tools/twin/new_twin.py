#!/usr/bin/env python3
"""Create the Hindi twin project of an English project (used by /new-video --twin-of).

usage: vt-python tools/twin/new_twin.py projects/<name>        -> projects/<name>-hi/
Existing files (a script saved during the English Prep) are never overwritten.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools import project_state as pst  # noqa: E402
from tools.twin import common  # noqa: E402


def create(english: str) -> str:
    english = os.path.normpath(english)
    if english.endswith(common.SUFFIX):
        raise SystemExit(f"{english} is already a twin")
    if not os.path.isfile(os.path.join(english, "log.md")):
        raise SystemExit(f"{english}: not a project (no log.md)")
    twin = common.twin_path(english)
    for folder in ("raw", "assets", "work/logs", "work/config", "work/twin", "out"):
        os.makedirs(os.path.join(twin, folder), exist_ok=True)
    log = os.path.join(twin, "log.md")
    if not os.path.exists(log):
        with open(log, "w", encoding="utf-8") as f:
            f.write(f"# {os.path.basename(twin)} log\n\nHindi twin of `{os.path.basename(english)}`.\n")
    state, err = pst.try_load_state(twin)
    if err == "NO_STATE":
        state = pst.default_state(twin)
    elif err:
        raise SystemExit(f"{twin}: project-state.json unreadable ({err})")
    state.update(twin_of=os.path.basename(english), language="hi",
                 next_actions=["H1 · Prep + Cut (pipeline/hindi-twin.md)"])
    pst.save_state(twin, state)
    return twin


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(create(sys.argv[1]))
