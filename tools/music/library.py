"""music/index.md: one row per track. The tools read and write it; nothing else does."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COLUMNS = ("id", "file", "mood", "bpm", "length", "loopable", "instrumental", "★house", "license", "credit",
           "content_id_risk", "source_url", "sha256", "LUFS / TP", "used_in", "last_used")
EMPTY = "—"
ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def root() -> str:
    """The library folder (VT_MUSIC_DIR overrides it, for tests)."""
    return os.environ.get("VT_MUSIC_DIR") or os.path.join(REPO, "music")


def index_path() -> str:
    return os.path.join(root(), "index.md")


def track_path(row: dict) -> str:
    return os.path.join(root(), "tracks", row["file"])


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _cells(line: str) -> list[str]:
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def _split() -> tuple[str, list[dict]]:
    with open(index_path(), encoding="utf-8") as f:
        lines = f.read().splitlines()
    head = next((i for i, l in enumerate(lines) if _cells(l)[:1] == ["id"]), None)
    if head is None:
        raise SystemExit(f"{index_path()}: table header not found")
    rows = []
    for line in lines[head + 2:]:
        cells = _cells(line) if line.startswith("|") else []
        if len(cells) == len(COLUMNS):
            rows.append(dict(zip(COLUMNS, cells)))
    return "\n".join(lines[: head + 2]), rows


def rows() -> list[dict]:
    return _split()[1]


def write(new_rows: list[dict]) -> None:
    header, _ = _split()
    body = ["| " + " | ".join(str(r[c]).replace("|", "\\|") or EMPTY for c in COLUMNS) + " |"
            for r in sorted(new_rows, key=lambda r: r["id"])]
    fd, tmp = tempfile.mkstemp(dir=root(), prefix=".index-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join([header, *body]) + "\n")
    os.replace(tmp, index_path())


def find(ref: str) -> dict:
    """A row by id, file name or music/tracks/<file> path."""
    name = os.path.basename(ref.strip().strip("`"))
    for row in rows():
        if ref.strip().strip("`") == row["id"] or name == row["file"]:
            return row
    raise SystemExit(f"no track {ref!r} in {index_path()} (add it with tools/music/add_track.py)")


def seconds(row: dict) -> float:
    return float(row["length"].rstrip(" s"))


def loop_points(row: dict) -> tuple[float, float] | None:
    """(loop start, seam) in seconds from "yes @ 63.50 s from 0.12 s", else None."""
    m = re.match(r"yes @ ([\d.]+) s from ([\d.]+) s", row["loopable"])
    return (float(m[2]), float(m[1])) if m else None


def is_house(row: dict) -> bool:
    return row["★house"] == "★"
