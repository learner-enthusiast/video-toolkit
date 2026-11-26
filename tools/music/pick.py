#!/usr/bin/env python3
"""Resolve a video's `**Music:**` prompt line and record it (pipeline/music.md). Never a judgement.

usage: vt-python tools/music/pick.py <project> (--prompt prompt.md | --value "<id|file|none|audition [a,b]|>")
    [--seconds 170]
No line (or an empty value) = rotation: the least recently used ★house track that fits. A Hindi twin
always inherits the English video's track. Writes project-state.json `music` and one log.md line.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools import project_state as pst  # noqa: E402
from tools.music import library  # noqa: E402
from tools.project_log_lock import project_log_lock  # noqa: E402

LINE = re.compile(r"^\s*\*\*Music:\*\*(.*)$", re.M)
AUDITION = re.compile(r"^audition\b\s*(?:\[(.*)\])?$", re.I)
AUDITION_SIZE = 3
MAX_REEL_S = 179.0        # CLAUDE.md -> House numbers, when no cut exists yet


def prompt_value(text: str) -> str:
    found = LINE.search(text)
    value = found[1].strip() if found else ""
    return "" if value.startswith("<") else value          # the template placeholder is no choice


def fits(row: dict, seconds: float) -> bool:
    return library.loop_points(row) is not None or library.seconds(row) >= seconds


def rotation(seconds: float) -> list[dict]:
    """★house tracks that fit, least recently used first (never used before any date), ties by id."""
    house_tracks = [r for r in library.rows()
                    if library.is_house(r) and r["instrumental"] == "yes" and fits(r, seconds)]
    return sorted(house_tracks, key=lambda r: ("" if r["last_used"] == library.EMPTY else r["last_used"], r["id"]))


def resolve(value: str, seconds: float) -> dict:
    value = value.strip().strip("`").strip()
    if value.lower() == "none":
        return {"id": None, "mode": "none"}
    audition = AUDITION.match(value)
    if audition:
        refs = [r.strip() for r in (audition[1] or "").split(",") if r.strip()]
        ids = [library.find(r)["id"] for r in refs] or [r["id"] for r in rotation(seconds)[:AUDITION_SIZE]]
        return {"id": None, "mode": "audition", "candidates": ids} if ids else {"id": None, "mode": "no-house-track"}
    if value:
        return {"id": library.find(value)["id"], "mode": "named"}
    ranked = rotation(seconds)
    return {"id": ranked[0]["id"], "mode": "rotation"} if ranked else {"id": None, "mode": "no-house-track"}


def inherit(project: str, twin_of: str) -> dict:
    english = os.path.join(os.path.dirname(os.path.abspath(project)), twin_of)
    state, err = pst.try_load_state(english)
    if err:
        raise SystemExit(f"{english}: project-state.json unreadable ({err})")
    return {"id": (state.get("music") or {}).get("id"), "mode": "inherited"}


def record(project: str, choice: dict) -> None:
    choice = {**choice, "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with project_log_lock(project):
        state, err = pst.try_load_state(project)
        if err == "NO_STATE":
            state = pst.default_state(project)
        elif err:
            raise SystemExit(f"{project}: project-state.json unreadable ({err}); run sync-handoff")
        state["music"] = choice
        pst.save_state(project, state)
        pst.append_log_line(project, f"**Music bed:** {choice['id'] or 'none'} ({choice['mode']})")


def cut_seconds(project: str) -> float:
    voice = os.path.join(project, "work", "audio", "voice.wav")
    if not os.path.isfile(voice):
        return MAX_REEL_S
    import soundfile as sf
    return sf.info(voice).duration


def describe(choice: dict) -> str:
    if choice["mode"] == "audition":
        return f"music: audition at the end of Cut: {', '.join(choice['candidates'])}"
    if choice["mode"] == "no-house-track":
        return "music: NO BED (no ★house track fits). Say so in the Cut handoff"
    return f"music: {choice['id'] or 'no bed'} ({choice['mode']})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--prompt")
    group.add_argument("--value")
    ap.add_argument("--seconds", type=float, help="video length; default: the cut voice, else the reel limit")
    args = ap.parse_args(argv)
    if not os.path.isfile(os.path.join(args.project, "log.md")):
        raise SystemExit(f"{args.project}: not a project (no log.md)")
    state, _ = pst.try_load_state(args.project)
    twin_of = (state or {}).get("twin_of")
    if twin_of:
        choice = inherit(args.project, twin_of)
    else:
        if args.prompt is None and args.value is None:
            ap.error("give --prompt <file> or --value (empty for no Music line)")
        if args.prompt is not None:
            with open(args.prompt, encoding="utf-8") as f:
                value = prompt_value(f.read())
        else:
            value = args.value
        choice = resolve(value, args.seconds or cut_seconds(args.project))
    record(args.project, choice)
    print(describe(choice))
    return 0


if __name__ == "__main__":
    sys.exit(main())
