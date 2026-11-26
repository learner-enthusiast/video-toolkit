#!/usr/bin/env python3
"""Turn named cues (cues.json) into output frames (cue_frames.json) using the timeline's words.

usage (from work/remotion/): vt-python tools/captions/resolve_cues.py [--cues public/data/cues.json]
    [--timeline public/data/timeline.json] [--out public/data/cue_frames.json] [--src src]
Run it after every timeline step (build, retime, fix_starts). It writes nothing if any cue fails.

cues.json: {"B07.tableScan": {"beat": "B07", "phrase": "full table", "from": ..., "edge": "end"}}
  phrase  matched like at(): case and punctuation ignored (so hyphen and possessive tokens are one
          token), number words equal their digits. The match must start in `beat`.
  from    optional: a frame, or a cue name with an offset ("B07.theFix+5"). The first match at or
          after it is used. Without it the phrase must occur exactly once in the beat.
  edge    "start" (default): the first word's start. "end": the last word's end.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys

# The same map as lib/timeline.ts at(): Whisper writes some numbers as digits.
NUM = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
       "seven": "7", "eight": "8", "nine": "9", "ten": "10", "fifteen": "15", "million": "million"}
NAME = re.compile(r"^(B?[A-Za-z0-9]+)\.[A-Za-z_]\w*$")
FROM_REF = re.compile(r"^(?P<cue>[\w]+\.\w+)\s*(?:(?P<sign>[+-])\s*(?P<offset>\d+))?$")
CUE_CALL = re.compile(r"""\bcue\(\s*(['"])([^'"]+)\1""")
BEAT_CALL = re.compile(r"""\bbeatAt\(\s*(['"])([^'"]+)\1\s*(?:,\s*([-\d.]+))?""")


class CueError(ValueError):
    pass


def norm(token: str) -> str:
    t = re.sub(r"[^a-z0-9]", "", token.lower())
    return NUM.get(t, t)


def frame(value: float) -> int:
    """JavaScript's Math.round (half goes up), so frames equal at()'s."""
    return math.floor(value + 0.5)


def beat_spans(words: list[dict]) -> dict[str, tuple[float, float]]:
    """beat -> (its first word's start, the next beat's first word start); the last beat ends
    with its last word. The same rule as beatAt() in cues.ts."""
    spans: dict[str, tuple[float, float]] = {}
    for i, word in enumerate(words):
        beat = word.get("b")
        if not beat or beat in spans:
            continue
        j = i
        while j + 1 < len(words) and words[j + 1].get("b") == beat:
            j += 1
        spans[beat] = (word["s"], words[j + 1]["s"] if j + 1 < len(words) else words[j]["e"])
    return spans


def find(words: list[dict], normed: list[str], tokens: list[str], beat: str) -> list[int]:
    n = len(tokens)
    return [i for i in range(len(words) - n + 1) if words[i].get("b") == beat and normed[i:i + n] == tokens]


def resolve(cues: dict, words: list[dict]) -> tuple[dict[str, int], list[str]]:
    """({cue: frame}, errors). Every cue is checked, so one run reports every problem."""
    normed = [norm(w["raw"]) for w in words]
    beats = {w.get("b") for w in words if w.get("b")}
    frames: dict[str, int] = {}
    errors: dict[str, str] = {}

    def one(name: str, stack: tuple) -> int:
        if name in frames:
            return frames[name]
        if name in errors:
            raise CueError(f"depends on the failed cue {name}")
        if name in stack:
            raise CueError(f"`from` loops through {' -> '.join(stack + (name,))}")
        spec = cues[name]
        unknown = set(spec) - {"beat", "phrase", "from", "edge"}
        if unknown:
            raise CueError(f"unknown keys {sorted(unknown)}")
        match = NAME.match(name)
        beat, phrase = spec.get("beat"), spec.get("phrase") or ""
        if not match or match[1] != beat:
            raise CueError(f"name must be '{beat}.<word>' for beat {beat}")
        if beat not in beats:
            raise CueError(f"beat {beat} has no words in the timeline")
        edge = spec.get("edge", "start")
        if edge not in ("start", "end"):
            raise CueError(f"edge must be 'start' or 'end', not {edge!r}")
        tokens = [t for t in (norm(p) for p in phrase.split()) if t]
        if not tokens:
            raise CueError("empty phrase")
        hits = find(words, normed, tokens, beat)
        if not hits:
            elsewhere = sorted({words[i].get("b") for b in beats for i in find(words, normed, tokens, b)})
            raise CueError(f"phrase {phrase!r} is not in {beat}" + (f" (it is in {', '.join(elsewhere)})" if elsewhere else ""))
        floor = spec.get("from")
        if floor is None:
            if len(hits) > 1:
                at = ", ".join(str(frame(words[i]["s"])) for i in hits)
                raise CueError(f"phrase {phrase!r} is ambiguous in {beat} (frames {at}): use a longer phrase or `from`")
        else:
            if isinstance(floor, str):
                ref = FROM_REF.match(floor)
                if not ref or ref["cue"] not in cues:
                    raise CueError(f"`from` {floor!r} names no cue")
                offset = int(ref["offset"] or 0) * (-1 if ref["sign"] == "-" else 1)
                floor = one(ref["cue"], stack + (name,)) + offset
            hits = [i for i in hits if words[i]["s"] >= floor]
            if not hits:
                raise CueError(f"phrase {phrase!r} does not occur in {beat} at or after frame {floor}")
        i = hits[0]
        frames[name] = frame(words[i]["s"] if edge == "start" else words[i + len(tokens) - 1]["e"])
        return frames[name]

    for name in cues:
        try:
            one(name, ())
        except CueError as exc:
            errors[name] = str(exc)
    return frames, [f"{name}: {message}" for name, message in errors.items()]


def source_problems(src: str, cues: dict, spans: dict) -> tuple[list[str], list[str]]:
    """(errors, unused cue names) for the cue()/beatAt() calls in the scene code."""
    code = ""
    for path in sorted(glob.glob(os.path.join(src, "**", "*.ts*"), recursive=True)):
        if os.path.isfile(path) and os.sep + "shared" + os.sep not in path:
            with open(path, encoding="utf-8") as f:
                code += f.read() + "\n"
    called = {m[2] for m in CUE_CALL.finditer(code)}
    errors = [f"{name}: called in {src}/ but not in cues.json" for name in sorted(called - set(cues))]
    for m in BEAT_CALL.finditer(code):
        beat, fraction = m[2], float(m[3] or 0)
        if beat not in spans:
            errors.append(f"beatAt('{beat}'): beat has no words in the timeline")
        if not 0 <= fraction <= 1:
            errors.append(f"beatAt('{beat}', {fraction}): the fraction must be 0..1")
    return errors, sorted(set(cues) - called)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cues", default="public/data/cues.json")
    ap.add_argument("--timeline", default="public/data/timeline.json")
    ap.add_argument("--out", default="public/data/cue_frames.json")
    ap.add_argument("--src", help="also check every cue()/beatAt() call under this folder")
    args = ap.parse_args(argv)
    with open(args.cues, encoding="utf-8") as f:
        cues = json.load(f)
    with open(args.timeline, encoding="utf-8") as f:
        words = json.load(f)["words"]
    if not any(w.get("b") for w in words):
        print("the timeline words carry no beat IDs (rebuild it with tools/captions/build_timeline.py)", file=sys.stderr)
        return 1
    frames, errors = resolve(cues, words)
    unused: list[str] = []
    if args.src:
        more, unused = source_problems(args.src, cues, beat_spans(words))
        errors += more
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} problem(s); {args.out} not written", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(frames, f, indent=1)
        f.write("\n")
    print(f"resolved {len(frames)} cue(s) -> {args.out}")
    if unused:
        print(f"unused in {args.src}: {', '.join(unused)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
