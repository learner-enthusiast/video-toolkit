"""Paths and facts shared by the Hindi twin tools (pipeline/hindi-twin.md)."""
from __future__ import annotations

import glob
import os

from tools import project_state as pst

SUFFIX = "-hi"


def twin_path(english: str) -> str:
    return os.path.normpath(english) + SUFFIX


def read_state(project: str) -> dict:
    state, err = pst.try_load_state(project)
    return {} if err else state


def english_of(twin: str) -> str:
    """The English project a twin points at (project-state.json `twin_of`, a sibling folder)."""
    name = read_state(twin).get("twin_of")
    if not name:
        raise SystemExit(f"{twin}: project-state.json has no twin_of (create it with tools/twin/new_twin.py)")
    return os.path.join(os.path.dirname(os.path.normpath(twin)), name)


def english_main(english: str) -> str | None:
    """The delivered English main video: out/<stem>_9x16.mp4 (not the trailer)."""
    found = sorted(p for p in glob.glob(os.path.join(english, "out", "*_9x16.mp4"))
                   if not p.endswith("_trailer_9x16.mp4"))
    return found[0] if len(found) == 1 else None


def twin_stem(english: str) -> str | None:
    main = english_main(english)
    return os.path.basename(main)[: -len("_9x16.mp4")] + SUFFIX if main else None


def twin_deliverables(english: str) -> list[str] | None:
    """The only four files a twin ships."""
    stem = twin_stem(english)
    return [f"{stem}_9x16.mp4", f"{stem}_9x16.srt", f"{stem}_trailer_9x16.mp4", f"{stem}_trailer_9x16.srt"] if stem else None
