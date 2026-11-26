"""The words a video's captions should show, from its caption timeline (video_inspect.py --captions).

For a Hindi twin, Whisper's Devanagari can't be compared with Roman captions read by OCR, so the
caption checks use the timeline the captions were rendered from.
"""
from __future__ import annotations

import json


def load(timeline_path: str, ranges_path: str | None = None) -> list[list]:
    """[[start_s, end_s, shown word]] on the video's own clock. With trailer ranges (frames of the
    main timeline) the words are re-based onto the trailer's clock."""
    with open(timeline_path, encoding="utf-8") as f:
        timeline = json.load(f)
    fps = timeline.get("fps", 30)
    words = [w for w in timeline["words"] if w.get("w")]
    if ranges_path:
        with open(ranges_path, encoding="utf-8") as f:
            ranges = json.load(f)["ranges"]
        rebased, offset = [], 0
        for a, b in ranges:
            rebased += [{**w, "s": w["s"] - a + offset, "e": min(w["e"], b) - a + offset} for w in words if a <= w["s"] < b]
            offset += b - a
        words = rebased
    return [[round(w["s"] / fps, 2), round(w["e"] / fps, 2), part]
            for w in words for part in w["w"].split()]
