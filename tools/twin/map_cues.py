#!/usr/bin/env python3
"""Give every English named cue its frame in the Hindi edit. No model involved.

usage (from the twin's work/): vt-python tools/twin/map_cues.py [--english-data <dir>] [--data remotion/public/data]
    [--script ../script.md] [--report twin/map-report.json]
(a) an anchor in the Hindi script's beat tag, [B07 | SPLIT | tableScan="poori table"], sets cue
    B07.tableScan to that Hindi phrase; else
(b) the cue keeps its fraction of the beat, snapped to the nearest Hindi word onset or pause within
    0.25 s.
Writes cue_frames.json and the report. Flags: beat length ratio < 0.75 or > 1.4, unresolved anchors,
and cues closer than 6 frames that weren't in English. Exit 1: a cue's beat is missing in Hindi.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.captions import resolve_cues as rc  # noqa: E402
from tools.script_beats import parse_beats  # noqa: E402
from tools.twin import common  # noqa: E402

ANCHOR = re.compile(r'([A-Za-z_]\w*)\s*=\s*"([^"]+)"')
SNAP_S, PAUSE_S = 0.25, 0.15
RATIO_RANGE = (0.75, 1.4)
MIN_GAP = 6   # frames
STILL_OFFSET = 9


def script_anchors(text: str) -> dict[str, str]:
    """{"B07.tableScan": "poori table"} from the beat tags."""
    out = {}
    for beat in parse_beats(text):
        for name, phrase in ANCHOR.findall(beat["rest"] or ""):
            if beat["id"]:
                out[f"{beat['id']}.{name}"] = phrase
    return out


def snap_points(words: list[dict], fps: int) -> list[float]:
    """Word onsets, and the start of every pause."""
    points = [w["s"] for w in words]
    points += [a["e"] for a, b in zip(words, words[1:]) if b["s"] - a["e"] >= PAUSE_S * fps]
    return sorted(points)


def map_cues(cues: dict, english_frames: dict, english: dict, hindi: dict, anchors: dict) -> tuple[dict, dict]:
    """({cue: Hindi frame}, report)."""
    fps = hindi.get("fps", 30)
    en_spans, hi_spans = rc.beat_spans(english["words"]), rc.beat_spans(hindi["words"])
    points = snap_points(hindi["words"], fps)
    window = SNAP_S * fps
    frames: dict[str, int] = {}
    detail: dict[str, dict] = {}
    flags: list[dict] = []

    def flag(kind, beat, text):
        flags.append({"kind": kind, "beat": beat, "detail": text})

    for name, spec in cues.items():
        beat = spec["beat"]
        if beat not in hi_spans or beat not in en_spans or name not in english_frames:
            flag("unmapped", beat, f"{name}: no {'Hindi' if beat not in hi_spans else 'English'} data for it")
            continue
        phrase = anchors.get(name)
        if phrase is not None:
            wanted = {"beat": beat, "phrase": phrase}
            if spec.get("edge"):
                wanted["edge"] = spec["edge"]
            found, errors = rc.resolve({name: wanted}, hindi["words"])
            if not errors:
                frames[name] = found[name]
                detail[name] = {"beat": beat, "source": "anchor", "frame": found[name]}
                continue
            flag("anchor", beat, errors[0])
        en_from, en_to = en_spans[beat]
        hi_from, hi_to = hi_spans[beat]
        fraction = min(1.0, max(0.0, (english_frames[name] - en_from) / max(en_to - en_from, 1)))
        raw = hi_from + fraction * (hi_to - hi_from)
        near = [p for p in points if abs(p - raw) <= window]
        value = min(near, key=lambda p: abs(p - raw)) if near else raw
        frames[name] = rc.frame(value)
        detail[name] = {"beat": beat, "source": "relative", "fraction": round(fraction, 3),
                        "snapped": bool(near), "frame": frames[name]}
    for name in sorted(set(anchors) - set(cues)):
        flag("anchor", name.split(".")[0], f"{name}: the English project has no such cue")

    beats = {}
    for beat, (en_from, en_to) in en_spans.items():
        if beat not in hi_spans:
            continue
        hi_from, hi_to = hi_spans[beat]
        en_len, hi_len = en_to - en_from, hi_to - hi_from
        ratio = round(hi_len / en_len, 2) if en_len > 0 else None
        beats[beat] = {"english_s": round(en_len / fps, 2), "hindi_s": round(hi_len / fps, 2), "ratio": ratio}
        if ratio is not None and not RATIO_RANGE[0] <= ratio <= RATIO_RANGE[1]:
            flag("ratio", beat, f"Hindi {hi_len / fps:.2f} s vs English {en_len / fps:.2f} s (x{ratio})")

    ordered = sorted(frames, key=lambda n: frames[n])
    for a, b in zip(ordered, ordered[1:]):
        if frames[b] - frames[a] < MIN_GAP and abs(english_frames[b] - english_frames[a]) >= MIN_GAP:
            flag("close", cues[b]["beat"], f"{a} and {b} are {frames[b] - frames[a]} frames apart "
                                           f"({abs(english_frames[b] - english_frames[a])} in English)")

    flagged = sorted({f["beat"] for f in flags})
    stills = sorted({detail[n]["frame"] + STILL_OFFSET for n in detail if detail[n]["beat"] in flagged}
                    | {rc.frame(hi_spans[b][0]) + STILL_OFFSET for b in flagged if b in hi_spans})
    report = {
        "counts": {"cues": len(cues), "mapped": len(frames),
                   "anchor": sum(d["source"] == "anchor" for d in detail.values()),
                   "relative": sum(d["source"] == "relative" for d in detail.values()), "flags": len(flags)},
        "beats": beats, "cues": detail, "flags": flags, "flagged_beats": flagged, "still_frames": stills,
    }
    return frames, report


def _load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--english-data", help="default: the twin_of project's work/remotion/public/data")
    ap.add_argument("--data", default="remotion/public/data")
    ap.add_argument("--script", default="../script.md")
    ap.add_argument("--report", default="twin/map-report.json")
    args = ap.parse_args(argv)
    english_data = args.english_data or os.path.join(common.english_of(".."), "work", "remotion", "public", "data")
    with open(args.script, encoding="utf-8") as f:
        anchors = script_anchors(f.read())
    frames, report = map_cues(
        _load(os.path.join(english_data, "cues.json")), _load(os.path.join(english_data, "cue_frames.json")),
        _load(os.path.join(english_data, "timeline.json")), _load(os.path.join(args.data, "timeline.json")), anchors)
    os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    c = report["counts"]
    print(f"cues {c['cues']} · mapped {c['mapped']} (anchor {c['anchor']}, relative {c['relative']}) · flags {c['flags']}")
    for flagged in report["flags"][:16]:
        print(f"{flagged['kind']:8} {flagged['beat']}  {flagged['detail']}")
    if len(report["flags"]) > 16:
        print(f"… {len(report['flags']) - 16} more in {args.report}")
    if c["mapped"] != c["cues"]:
        print(f"{c['cues'] - c['mapped']} cue(s) unmapped: cue_frames.json not written", file=sys.stderr)
        return 1
    with open(os.path.join(args.data, "cue_frames.json"), "w", encoding="utf-8") as f:
        json.dump(frames, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
