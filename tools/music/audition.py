#!/usr/bin/env python3
"""Mix each candidate track under the cut voice with the real chain and check it. I pick by ear.

usage: gpu-run vt-python tools/music/audition.py <project> [--tracks id id …] [--words file.json]
Needs the rough cut: the cleaned recording, work/audio/voice.wav and its word timings. Writes
out/music-audition/<NN>-<id>/{voice_only,with_music,with_music_phone}.wav and report.md.
Run as a heavy job (tools/jobs/batch.sh).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools import project_state as pst  # noqa: E402
from tools.inspect import caption_reference  # noqa: E402
from tools.music import analyze, house, library, pick  # noqa: E402
from tools.qa import clarity  # noqa: E402
from tools.sound import music_bed  # noqa: E402

SR = music_bed.SR
SEPARATOR_S = 0.8
WORD_FILES = ("remotion/public/data/timeline.json", "transcript/cut/voice.json", "transcript/hi/cut/voice.json")


def preconditions(work: str, words_file: str | None) -> str:
    """The words file to use; refuses before a cleaned, cut and transcribed voice exists."""
    if not glob.glob(os.path.join(glob.escape(work), "audio", "cleaned", "*.wav")):
        raise SystemExit("refused: no cleaned recording in work/audio/cleaned/ (the voice gate comes first)")
    if not os.path.isfile(os.path.join(work, "audio", "voice.wav")):
        raise SystemExit("refused: no cut voice (work/audio/voice.wav): make the rough cut first")
    for candidate in [words_file] if words_file else [os.path.join(work, w) for w in WORD_FILES]:
        if candidate and os.path.isfile(candidate):
            if os.path.basename(candidate) == "timeline.json":
                return candidate
            # a transcript older than the cut describes a different cut
            if os.path.getmtime(candidate) >= os.path.getmtime(os.path.join(work, "audio", "voice.wav")):
                return candidate
    raise SystemExit("refused: no word timings for this cut (transcribe the cut voice first)")


def word_list(path: str) -> list[list]:
    if os.path.basename(path) == "timeline.json":
        return caption_reference.load(path)
    return clarity.words(path)


def windows(words: list, total_s: float, params: dict) -> list[tuple[str, float, float]]:
    """The busiest stretch (most words) and a quiet moment (longest real pause, else the hook)."""
    busy = min(params["busy_s"], total_s)
    best = max((sum(1 for s, e, _ in words if start <= s and e <= start + busy), -start, start)
               for start in [min(s, total_s - busy) for s, _, _ in words])[2]
    quiet = min(params["quiet_s"], total_s)
    pauses = sorted(((b[0] - a[1], a[1], b[0]) for a, b in zip(words, words[1:])), key=lambda p: (-p[0], p[1]))
    if pauses and pauses[0][0] >= params["min_pause_s"]:
        _, begin, end = pauses[0]
        start = min(max((begin + end) / 2 - quiet / 2, 0.0), total_s - quiet)
        label = "longest pause"
    else:
        start, label = 0.0, "hook"
    return [("busiest", round(best, 2), round(best + busy, 2)), (label, round(start, 2), round(start + quiet, 2))]


def excerpt(x: np.ndarray, spans: list) -> np.ndarray:
    gap = np.zeros(int(SEPARATOR_S * SR))
    parts = []
    for _, a, b in spans:
        if parts:
            parts.append(gap)
        parts.append(x[int(a * SR): int(b * SR)])
    return np.concatenate(parts)


def phone(source: str, target: str, params: dict) -> None:
    """What a phone speaker keeps: mono, no low end, limited top."""
    chain = f"highpass=f={params['phone_highpass_hz']}:p=2,highpass=f={params['phone_highpass_hz']}:p=2," \
            f"lowpass=f={params['phone_lowpass_hz']}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", source, "-af", chain, "-ac", "1", "-ar", str(SR), target], check=True)


def clock(seconds: float) -> str:
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def audition_track(project: str, row: dict, voice: np.ndarray, spans: list, cuts: list, folder: str,
                   gain: float, voice_excerpt: str, language: str, params: dict) -> dict:
    result = {"id": row["id"], "status": "rejected"}
    path = library.track_path(row)
    if not os.path.isfile(path) or library.sha256(path) != row["sha256"]:
        return {**result, "reason": "audio missing or changed (tools/music/restore.py)"}
    try:
        bed, built = music_bed.build(voice, spans, analyze.decode(path), library.loop_points(row), params)
    except SystemExit as why:
        return {**result, "reason": str(why)}
    gap = built["gap"]
    result.update(gap=gap, loops_at_s=built["loops_at_s"], auto_level_rounds=built["auto_level_rounds"])
    if not built["passed"]:
        return {**result, "reason": f"worst gap {gap['worst_db']} dB stays below {params['gap_fail_db']} dB"}
    os.makedirs(folder, exist_ok=True)
    alone, mixed = os.path.join(folder, "voice_only.wav"), os.path.join(folder, "with_music.wav")
    # one gain for both files, so my voice is equally loud in them
    sf.write(alone, excerpt(voice, cuts) * gain, SR, subtype="PCM_24")
    sf.write(mixed, excerpt(voice + bed, cuts) * gain, SR, subtype="PCM_24")
    phone(mixed, os.path.join(folder, "with_music_phone.wav"), params["audition"])
    scratch = os.path.join(project, "work", "transcript", "audition", row["id"])
    os.makedirs(scratch, exist_ok=True)
    shutil.copyfile(mixed, os.path.join(scratch, f"mix_{row['id']}.wav"))
    heard = clarity.check(project, voice_excerpt, os.path.join(scratch, f"mix_{row['id']}.wav"), scratch, language)
    result["clarity"] = heard
    if not heard["passed"]:
        shutil.rmtree(folder)
        return {**result, "reason": "clarity: lost " + ", ".join(f"{w['word']} @{w['at_s']}s" for w in heard["missing"][:6])}
    return {**result, "status": "ok", "folder": folder}


def report_line(entry: dict) -> str:
    if entry["status"] != "ok":
        return f"{entry['n']} · {entry['id']} · REJECTED: {entry['reason']}"
    loops = f"loops at {', '.join(clock(t) for t in entry['loops_at_s'])}" if entry["loops_at_s"] else "no loop needed"
    return (f"{entry['n']} · {entry['id']} · voice over music median {entry['gap']['median_db']:.0f} dB, "
            f"worst {entry['gap']['worst_db']:.0f} dB · clarity PASS · {loops}")   # format: pipeline/music.md


def run(project: str, tracks: list[str] | None, words_file: str | None = None) -> list[dict]:
    work = os.path.join(project, "work")
    words_path = preconditions(work, words_file)
    state, err = pst.try_load_state(project)
    if err:
        raise SystemExit(f"{project}: project-state.json unreadable ({err})")
    if state.get("twin_of"):
        raise SystemExit("a Hindi twin inherits the English track: no audition")
    voice, sr = sf.read(os.path.join(work, "audio", "voice.wav"))
    if sr != SR or voice.ndim != 1:
        raise SystemExit("the voice stem must be 48 kHz mono")
    total = len(voice) / SR
    refs = tracks or (state.get("music") or {}).get("candidates") \
        or [r["id"] for r in pick.rotation(total)[:pick.AUDITION_SIZE]]
    if not refs:
        raise SystemExit("no track to audition: add ★house tracks or name ids")
    rows = [library.find(r) for r in refs]
    words = word_list(words_path)
    spans = [[s, e] for s, e, _ in words]
    params = music_bed.settings()
    cuts = windows(words, total, params["audition"])
    out = os.path.join(project, "out", "music-audition")
    if os.path.isdir(out):
        shutil.rmtree(out)                                     # only this tool writes here
    os.makedirs(out)
    scratch = os.path.join(work, "transcript", "audition", "voice")
    os.makedirs(scratch, exist_ok=True)
    alone = os.path.join(scratch, "audition_voice.wav")
    sf.write(alone, excerpt(voice, cuts), SR, subtype="PCM_24")
    language = state.get("language", "en")
    lufs, peak = analyze.loudness(alone)
    limits = house.values()
    gain = 10 ** (min(limits["lufs"] - lufs, limits["true_peak_max_db"] - 1.5 - peak) / 20)
    results = []
    for n, row in enumerate(rows, 1):
        entry = audition_track(project, row, voice, spans, cuts, os.path.join(out, f"{n:02d}-{row['id']}"),
                               gain, alone, language, params)
        results.append({"n": n, **entry})
    with open(os.path.join(out, "audition.json"), "w", encoding="utf-8") as f:
        json.dump({"windows": cuts, "tracks": results}, f, indent=1)
    lines = ["# Music audition", "",
             "Windows: " + ", ".join(f"{label} {clock(a)}–{clock(b)}" for label, a, b in cuts), ""]
    lines += [report_line(e) for e in results]
    lines += ["", "Reply with e.g. `cut ok, music 2` (or `music none`)."]
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--tracks", nargs="+")
    ap.add_argument("--words", help="word timings (timeline.json or a Whisper JSON of the cut voice)")
    args = ap.parse_args(argv)
    results = run(args.project, args.tracks, args.words)
    return 0 if any(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
