#!/usr/bin/env python3
"""Beat tags in a script.md: `[B07 | mm:ss–mm:ss | SPLIT]` (the time range is optional).

usage: vt-python tools/script_beats.py projects/<name>/script.md   -> beats as JSON; exit 1 on bad IDs.
Scripts written before beat IDs (no tag has one) are accepted as they are.
"""
from __future__ import annotations

import json
import re
import sys

BEAT_ID = re.compile(r"^B\d{2,}$")
_TIME = r"(?:\d{1,2}:\d{2}|mm:ss)"  # templates carry the literal placeholder
TAG = re.compile(
    r"\[\s*(?:(?P<id>B\d{2,})\s*\|\s*)?"
    rf"(?:(?P<start>{_TIME})\s*[–-]\s*(?P<end>{_TIME})\s*\|\s*)?"
    r"(?P<state>HEAD|FULL|SPLIT)\s*(?:\|(?P<rest>[^\]]*))?\]"
)


def parse_beats(text: str) -> list[dict]:
    """Every beat tag in order: {id, start, end, state, rest, line}."""
    beats = []
    for number, line in enumerate(text.splitlines(), 1):
        for m in TAG.finditer(line):
            beats.append({**m.groupdict(), "line": number})
    return beats


def id_problems(ids: list[str | None]) -> list[str]:
    """Rules for a script that uses IDs: every tag has one, unique, in increasing order."""
    if not any(ids):
        return []
    problems = []
    if not all(ids):
        problems.append(f"{sum(1 for i in ids if not i)} beat tag(s) have no ID while others do")
    present = [i for i in ids if i]
    repeated = sorted({i for i in present if present.count(i) > 1})
    if repeated:
        problems.append(f"repeated beat IDs: {', '.join(repeated)}")
    numbers = [int(i[1:]) for i in present]
    for a, b in zip(numbers, numbers[1:]):
        if b < a:
            problems.append(f"beat IDs out of order: B{a:02d} comes before B{b:02d}")
            break
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        beats = parse_beats(f.read())
    problems = id_problems([b["id"] for b in beats])
    json.dump({"beats": beats, "problems": problems}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
