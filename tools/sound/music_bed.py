#!/usr/bin/env python3
"""The faint music bed under my voice (pipeline/music.md). Only the music is processed.

usage (from work/): vt-python tools/sound/music_bed.py main|trailer
Reads the track from ../project-state.json (tools/music/pick.py), the voice stem audio/voice_<which>.wav
and the word timings. Writes audio/stems/<which>-music.wav and the values used to
work/config/sound_music.json (a Hindi twin takes the English ones). Then mix it:
vt-python tools/compose/mix.py <which> --music audio/stems/<which>-music.wav
Exit: 0 bed written · 3 this video has no music · 1 the gap can't be met.

Chain: loop at the indexed seam (or trim) -> speech-pocket EQ -> sidechain duck keyed by the voice,
holding through short pauses -> fades -> a level set against the voice, then checked and lowered.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import lfilter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools import project_state as pst  # noqa: E402
from tools.inspect import caption_reference  # noqa: E402
from tools.music import analyze, house, library  # noqa: E402
from tools.qa import loudness_windows as lw  # noqa: E402

SR = lw.SR
CONFIG = os.path.join(REPO, "config", "music.json")


def settings(overrides: dict | None = None) -> dict:
    """config/music.json plus the House numbers; `overrides` (a twin's English values) win."""
    with open(CONFIG, encoding="utf-8") as f:
        params = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    hn = house.values()
    params.update(gap_target_db=hn["music_gap_target_db"], gap_fail_db=hn["music_gap_fail_db"],
                  fade_in_s=hn["music_fade_in_s"], hold_pause_s=hn["music_hold_pause_s"])
    params.update(overrides or {})
    if params["hold_s"] <= params["hold_pause_s"]:
        raise SystemExit(f"config/music.json hold_s {params['hold_s']} must be longer than the "
                         f"{params['hold_pause_s']} s pauses it has to hold through (House numbers)")
    return params


def fit(track: np.ndarray, length: int, loop: tuple[float, float] | None, crossfade_s: float, sr: int = SR) -> tuple[np.ndarray, list[float]]:
    """`length` samples of the track: trimmed, or looped at the seam with an equal-power crossfade.
    Returns the bed and the times it loops."""
    if len(track) >= length:
        return track[:length].astype(np.float64), []
    if not loop:
        raise SystemExit(f"the track is {len(track) / sr:.1f} s, shorter than {length / sr:.1f} s, and not loopable")
    start, seam = int(round(loop[0] * sr)), int(round(loop[1] * sr))
    fade = min(int(crossfade_s * sr), len(track) - seam, seam - start)
    if fade <= 0:
        raise SystemExit("the loop seam leaves no audio to crossfade")
    angle = np.linspace(0, np.pi / 2, fade)
    out = list(track[:seam].astype(np.float64))
    out = np.array(out)
    body = track[start:seam].astype(np.float64)
    seams = []
    while len(out) < length:
        seams.append(round(len(out) / sr, 2))
        tail = track[seam: seam + fade].astype(np.float64)           # what would have played on
        head = body[:fade]
        joined = tail * np.cos(angle) + head * np.sin(angle)
        out = np.concatenate([out, joined, body[fade:]])
    return out[:length], seams


def speech_pocket(x: np.ndarray, eq: dict, sr: int = SR) -> np.ndarray:
    """A gentle peaking cut in the consonant range (RBJ cookbook)."""
    amp = 10 ** (eq["gain_db"] / 40)
    w = 2 * np.pi * eq["freq_hz"] / sr
    alpha = np.sin(w) / (2 * eq["q"])
    b = np.array([1 + alpha * amp, -2 * np.cos(w), 1 - alpha * amp])
    a = np.array([1 + alpha / amp, -2 * np.cos(w), 1 - alpha / amp])
    return lfilter(b / a[0], a / a[0], x)


def duck_gain_db(voice: np.ndarray, params: dict, sr: int = SR) -> np.ndarray:
    """0 dB while I speak and through pauses up to `hold_s`; rises by `duck_depth_db` in real gaps.
    Down early (`attack_s` before the voice returns), up slowly (`release_s`)."""
    hop = sr // 100
    frames = int(np.ceil(len(voice) / hop))
    padded = np.pad(voice, (0, frames * hop - len(voice)))
    level = 10 * np.log10(np.mean(padded.reshape(frames, hop) ** 2, axis=1) + 1e-12)
    active = level > params["voice_gate_db"]
    hold, attack, release = (int(round(params[k] * 100)) for k in ("hold_s", "attack_s", "release_s"))
    held = active.copy()
    last = -10 ** 9
    for i in range(frames):
        if active[i]:
            last = i
        elif i - last <= hold:
            held[i] = True
    open_amount = np.where(held, 0.0, 1.0)
    for i in range(1, frames):                                   # slow rise after the hold
        open_amount[i] = min(open_amount[i], open_amount[i - 1] + 1.0 / max(release, 1))
    for i in range(frames - 2, -1, -1):                          # be down before the voice is back
        open_amount[i] = min(open_amount[i], open_amount[i + 1] + 1.0 / max(attack, 1))
    gain = open_amount * params["duck_depth_db"]
    return np.interp(np.arange(len(voice)), np.arange(frames) * hop + hop / 2, gain)


def fades(length: int, params: dict, last_word_end_s: float, sr: int = SR) -> np.ndarray:
    """Fade in from the start; fade out to silence at the very end, starting no earlier than my last word."""
    env = np.ones(length)
    rise = min(length, int(params["fade_in_s"] * sr))
    env[:rise] *= np.sin(np.linspace(0, np.pi / 2, rise)) ** 2
    start = max(int(last_word_end_s * sr), length - int(params["fade_out_s"] * sr))
    start = min(max(start, 0), length)
    if start < length:
        env[start:] *= np.cos(np.linspace(0, np.pi / 2, length - start)) ** 2
    return env


def build(voice: np.ndarray, spans: list, track: np.ndarray, loop, params: dict, *, edges: bool = True,
          sr: int = SR) -> tuple[np.ndarray, dict]:
    """(music stem, report). The voice is only read. `edges` adds the fade in and out (off for excerpts)."""
    bed, seams = fit(track, len(voice), loop, params["loop_crossfade_s"], sr)
    bed = speech_pocket(bed, params["eq"], sr)
    bed = bed * 10 ** (duck_gain_db(voice, params, sr) / 20)
    if edges:
        bed = bed * fades(len(voice), params, max((e for _, e in spans), default=0.0), sr)
    if not np.any(bed):
        raise SystemExit("the music is silent")
    # set the level against the voice: the median gap while I speak is the House-numbers target
    gain_db = lw.gap(voice, bed, spans, params, sr)["median_db"] - params["gap_target_db"]
    rounds = 0
    while True:
        measured = lw.gap(voice, bed * 10 ** (gain_db / 20), spans, params, sr)
        if measured["worst_db"] >= params["gap_fail_db"] or rounds >= params["auto_level_rounds"]:
            break
        gain_db -= params["gap_fail_db"] - measured["worst_db"] + 0.05     # only the music moves
        rounds += 1
    return bed * 10 ** (gain_db / 20), {
        "gain_db": round(gain_db, 2), "gap": measured, "auto_level_rounds": rounds,
        "passed": measured["worst_db"] >= params["gap_fail_db"], "loops_at_s": seams,
    }


def word_spans(timeline: str, ranges: str | None) -> list:
    return [[s, e] for s, e, _ in caption_reference.load(timeline, ranges)]


def twin_params(project: str) -> dict | None:
    """A twin reproduces the English video's mix values."""
    state, err = pst.try_load_state(project)
    if err or not state.get("twin_of"):
        return None
    path = os.path.join(os.path.dirname(os.path.abspath(project)), state["twin_of"], "work", "config", "sound_music.json")
    if not os.path.isfile(path):
        raise SystemExit(f"the English project has no {path}: mix its music bed first")
    with open(path, encoding="utf-8") as f:
        return json.load(f)["params"]


def selection(project: str) -> dict | None:
    """The recorded music choice; None when pick.py hasn't run."""
    state, err = pst.try_load_state(project)
    return None if err else state.get("music")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("which", choices=("main", "trailer"))
    ap.add_argument("--project", default="..")
    ap.add_argument("--timeline", default="remotion/public/data/timeline.json")
    ap.add_argument("--ranges", default="audio/trailer_ranges.json")
    args = ap.parse_args(argv)
    choice = selection(args.project)
    if not choice:
        print("NOTE: no music decision recorded (tools/music/pick.py), so no music bed")
        return 3
    if not choice.get("id"):
        if choice.get("mode") == "audition":
            raise SystemExit("the audition has no chosen track yet (project_state.py set-music)")
        print("no music bed for this video")
        return 3
    row = library.find(choice["id"])
    path = library.track_path(row)
    if not os.path.isfile(path) or library.sha256(path) != row["sha256"]:
        raise SystemExit(f"track {row['id']} is missing or changed: tools/music/restore.py")
    voice, sr = sf.read(f"audio/voice_{args.which}.wav")
    if sr != SR or voice.ndim != 1:
        raise SystemExit("the voice stem must be 48 kHz mono")
    spans = word_spans(args.timeline, args.ranges if args.which == "trailer" else None)
    params = settings(twin_params(args.project))
    bed, report = build(voice, spans, analyze.decode(path), library.loop_points(row), params)
    os.makedirs("audio/stems", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    used = {}
    if os.path.isfile("config/sound_music.json"):
        with open("config/sound_music.json", encoding="utf-8") as f:
            used = json.load(f)
    deliverables = used.get("deliverables", {}) if used.get("track", {}).get("sha256") == row["sha256"] else {}
    deliverables[args.which] = report

    def save() -> None:
        with open("config/sound_music.json", "w", encoding="utf-8") as f:
            json.dump({"track": {"id": row["id"], "sha256": row["sha256"]}, "params": params,
                       "deliverables": deliverables}, f, indent=1)
            f.write("\n")

    save()
    g = report["gap"]
    print(f"{args.which}: {row['id']} · voice over music median {g['median_db']} dB, worst {g['worst_db']} dB "
          f"@{g['worst_at_s']}s · gain {report['gain_db']} dB · lowered {report['auto_level_rounds']}x")
    if not report["passed"]:
        print(f"BLOCKER: worst gap still below {params['gap_fail_db']} dB", file=sys.stderr)
        return 1
    stem = f"audio/stems/{args.which}-music.wav"
    sf.write(stem, bed.astype(np.float32), SR, subtype="PCM_24")
    report.update(voice_sha256=library.sha256(f"audio/voice_{args.which}.wav"), stem_sha256=library.sha256(stem))
    save()
    return 0


if __name__ == "__main__":
    sys.exit(main())
