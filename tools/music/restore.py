#!/usr/bin/env python3
"""Check every library row's audio file and sha256; list what to download again (pipeline/music.md).

usage: vt-python tools/music/restore.py      exit 0: complete · 1: something is missing or changed
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.music import library  # noqa: E402


def problems() -> list[tuple[str, str, str, str]]:
    out = []
    for row in library.rows():
        path = library.track_path(row)
        if not os.path.isfile(path):
            out.append((row["id"], "missing", path, row["source_url"]))
        elif library.sha256(path) != row["sha256"]:
            out.append((row["id"], "sha256 differs", path, row["source_url"]))
    return out


def main() -> int:
    found = problems()
    for track_id, what, path, url in found:
        print(f"{track_id}: {what} -> {path}\n  download again: {url}")
    print(f"{len(library.rows()) - len(found)} of {len(library.rows())} tracks present and unchanged")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
