#!/usr/bin/env python3
"""After the final render: add the track's credit line to the social copy and mark the track used.

usage: vt-python tools/music/finalize.py <project>     (before the Deliver commit; safe to run twice)
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import date

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools import project_state as pst  # noqa: E402
from tools.music import library  # noqa: E402

# (platform, description field, character limit or None). YouTube first.
FIELDS = (("youtube", "description", 5000), ("linkedin", "post", 3000), ("instagram", "caption", 2200),
          ("facebook", "post", None), ("x", "post_long", None), ("x", "post", 280), ("threads", "post", 500))


def add_credit(social: dict, line: str) -> tuple[list[str], list[str]]:
    """Append the exact line to every description field it fits. Returns (added, did not fit)."""
    added, full = [], []
    for platform, field, limit in FIELDS:
        text = social.get(platform, {}).get(field)
        if not text or line in text:
            continue
        joined = f"{text.rstrip()}\n\n{line}"
        if limit and len(joined) > limit:
            full.append(f"{platform}.{field}")
        else:
            social[platform][field] = joined
            added.append(f"{platform}.{field}")
    return added, full


def project_name(project: str) -> str:
    path = os.path.abspath(project)
    parts = path.split(os.sep)
    return "/".join(parts[parts.index("projects") + 1:]) if "projects" in parts else os.path.basename(path)


def finalize(project: str, today: str | None = None) -> int:
    state, err = pst.try_load_state(project)
    if err:
        raise SystemExit(f"{project}: project-state.json unreadable ({err})")
    track_id = (state.get("music") or {}).get("id")
    if not track_id:
        print("no music bed: nothing to credit or mark")
        return 0
    row = library.find(track_id)
    if row["credit"] != "none" and not state.get("twin_of"):          # a twin ships no social copy
        files = glob.glob(os.path.join(glob.escape(project), "out", "*_social.json"))
        if not files:
            raise SystemExit(f"{project}/out has no *_social.json, but {track_id} requires a credit: write it first")
        for path in files:
            with open(path, encoding="utf-8") as f:
                social = json.load(f)
            if not social.get("youtube", {}).get("description"):
                raise SystemExit(f"{path}: youtube.description is empty; the credit goes there first")
            added, full = add_credit(social, row["credit"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(social, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"{path}: credit added to {', '.join(added) or 'nothing new'}")
            if full:
                print(f"CREDIT DOES NOT FIT in {', '.join(full)}: tell me; no text was changed there")
    name = project_name(project)
    rows = library.rows()
    for r in rows:
        if r["id"] == track_id:
            used = [u for u in r["used_in"].split(", ") if u and u != library.EMPTY]
            if name not in used:
                used.append(name)
                r["last_used"] = today or date.today().isoformat()
            r["used_in"] = ", ".join(used)
    library.write(rows)
    print(f"{library.index_path()}: {track_id} used in {name} (commit it with the components and icons)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(finalize(sys.argv[1]))
