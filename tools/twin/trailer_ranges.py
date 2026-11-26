#!/usr/bin/env python3
"""Trailer ranges (output frames) from beat IDs: public/data/trailer_ranges.json.

usage (from the twin's work/): vt-python tools/twin/trailer_ranges.py [--script ../script.md]
    [--timeline remotion/public/data/timeline.json] [--out remotion/public/data/trailer_ranges.json]
    [--beats "B01, B02, B05–B07"] [--english-data <dir>]
Beats come from --beats, else the script's 60-second cut section, else the beats the English trailer
uses. Neighbouring beats merge into one range.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.captions import resolve_cues as rc  # noqa: E402
from tools.twin import common  # noqa: E402

LEAD, TAIL = 4, 6   # frames kept before the first word and after the last
RANGE = re.compile(r"\bB(\d{2,})\b(?:\s*[–-]\s*B(\d{2,})\b)?")
SECTION = re.compile(r"^##\s+(?:Hindi\s+)?60-second cut\b.*?$(.*?)(?=^#{1,2}\s|\Z)", re.M | re.S | re.I)


def parse_beat_list(text: str) -> list[str]:
    """'B01, B02, B05–B07' -> ['B01','B02','B05','B06','B07'] (first line(s) that list beats only)."""
    beats: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith(("[", "`[")):
            continue   # a Hindi-only line change under the list, not the list itself
        for a, b in RANGE.findall(line.split("(+")[0]):
            beats += [f"B{n:02d}" for n in range(int(a), int(b or a) + 1)]
    return list(dict.fromkeys(beats))


def beats_in_ranges(words: list[dict], ranges: list) -> list[str]:
    """Beats with a word that starts inside one of the ranges."""
    return list(dict.fromkeys(w["b"] for a, b in ranges for w in words if a <= w["s"] < b))


def ranges_for(words: list[dict], beats: list[str], total: int) -> list[list[int]]:
    index: dict[str, list[int]] = {}
    for i, w in enumerate(words):
        index.setdefault(w["b"], []).append(i)
    missing = [b for b in beats if b not in index]
    if missing:
        raise SystemExit(f"trailer beats with no words in this timeline: {', '.join(missing)}")
    spans: list[list[int]] = []
    for beat in beats:
        first, last = index[beat][0], index[beat][-1]
        if spans and first == spans[-1][1] + 1:
            spans[-1][1] = last
        else:
            spans.append([first, last])
    out = []
    for first, last in spans:
        # never run into the neighbouring words
        start = max(rc.frame(words[first]["s"]) - LEAD, rc.frame(words[first - 1]["e"]) if first else 0)
        stop = rc.frame(words[last]["e"]) + TAIL
        if last + 1 < len(words):
            stop = min(stop, max(rc.frame(words[last + 1]["s"]), rc.frame(words[last]["e"])))
        out.append([start, min(stop, total)])
    return out


def _load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--script", default="../script.md")
    ap.add_argument("--timeline", default="remotion/public/data/timeline.json")
    ap.add_argument("--out", default="remotion/public/data/trailer_ranges.json")
    ap.add_argument("--beats")
    ap.add_argument("--english-data")
    args = ap.parse_args(argv)
    source = "--beats"
    beats = parse_beat_list(args.beats) if args.beats else []
    if not beats and os.path.isfile(args.script):
        with open(args.script, encoding="utf-8") as f:
            section = SECTION.search(f.read())
        beats, source = (parse_beat_list(section[1]), "the script's 60-second cut") if section else ([], source)
    if not beats:
        data = args.english_data or os.path.join(common.english_of(".."), "work", "remotion", "public", "data")
        english = _load(os.path.join(data, "timeline.json"))
        beats = beats_in_ranges(english["words"], _load(os.path.join(data, "trailer_ranges.json"))["ranges"])
        source = "the English trailer's beats"
    if not beats:
        raise SystemExit("no trailer beats found")
    timeline = _load(args.timeline)
    ranges = ranges_for(timeline["words"], beats, timeline["total"])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"ranges": ranges}, f)
    seconds = sum(b - a for a, b in ranges) / timeline.get("fps", 30)
    print(f"{len(beats)} beats from {source} -> {len(ranges)} range(s), {seconds:.2f} s before the end card")
    return 0


if __name__ == "__main__":
    sys.exit(main())
