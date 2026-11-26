"""The House-numbers values the audio tools enforce. CLAUDE.md is their only copy."""
from __future__ import annotations

import os
import re

CLAUDE_MD = os.path.join(os.path.dirname(__file__), "..", "..", "CLAUDE.md")
_NUMBER = r"([−-]?\d+(?:\.\d+)?)"
PATTERNS = {
    "music_gap_target_db": rf"\*\*Music:\*\*.*?{_NUMBER} dB under my voice",
    "music_gap_fail_db": rf"\*\*Music:\*\*.*?fail < {_NUMBER} dB",
    "music_fade_in_s": rf"\*\*Music:\*\*.*?{_NUMBER} s fade-in",
    "music_hold_pause_s": rf"\*\*Music:\*\*.*?holds {_NUMBER} s pauses",
    "lufs": rf"\*\*Loudness:\*\*.*?{_NUMBER} ± ",
    "lufs_tolerance": rf"\*\*Loudness:\*\*.*?± {_NUMBER} LUFS",
    "true_peak_max_db": rf"\*\*Loudness:\*\*.*?≤ {_NUMBER} dBTP",
}


def values(path: str = CLAUDE_MD) -> dict[str, float]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    out = {}
    for name, pattern in PATTERNS.items():
        match = re.search(pattern, text)
        if not match:
            raise SystemExit(f"CLAUDE.md → House numbers: cannot read {name} (keep the line's wording)")
        out[name] = float(match[1].replace("−", "-"))
    return out
