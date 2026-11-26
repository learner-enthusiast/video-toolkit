#!/usr/bin/env python3
"""Voice-safety checks of one finished deliverable (pipeline/music.md). A failure is a blocker.

usage: gpu-run vt-python tools/qa/voice_over_music.py <project> <out/video.mp4> [--mix-transcript inspect/<stem>/report.json]
1. gap: voice stem vs ducked music stem, only where I'm speaking
2. clarity: Whisper hears every word of the voice-only stem in the final mix too
3. master: House-numbers loudness and true peak of the final file
Writes work/qa/voice_over_music_<main|trailer>.json and one line to log.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import soundfile as sf

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools import project_state as pst  # noqa: E402
from tools.music import analyze, house, library  # noqa: E402
from tools.project_log_lock import project_log_lock  # noqa: E402
from tools.qa import clarity, loudness_windows as lw  # noqa: E402
from tools.sound import music_bed  # noqa: E402


def beat_label(timeline_path: str, at_s: float, ranges_path: str | None) -> str:
    """The script beat ID that is on screen at `at_s` of this deliverable."""
    with open(timeline_path, encoding="utf-8") as f:
        timeline = json.load(f)
    frame = at_s * timeline.get("fps", 30)
    if ranges_path:                                       # trailer time -> main frame
        with open(ranges_path, encoding="utf-8") as f:
            offset = 0
            for a, b in json.load(f)["ranges"]:
                if frame < offset + b - a:
                    frame = a + frame - offset
                    break
                offset += b - a
    label = "no beat IDs"
    for beat in timeline.get("beats", []):
        if isinstance(beat, dict) and "words" in beat and timeline["words"][beat["words"][0]]["s"] <= frame:
            label = beat["id"]
    return label


def master(path: str) -> dict:
    limits = house.values()
    lufs, peak = analyze.loudness(path)
    ok = abs(lufs - limits["lufs"]) <= limits["lufs_tolerance"] + 1e-9 and peak <= limits["true_peak_max_db"] + 1e-9
    return {"lufs": lufs, "true_peak_db": peak, "passed": ok}


def check_gap(work: str, which: str, row: dict) -> dict:
    config = os.path.join(work, "config", "sound_music.json")
    if not os.path.isfile(config):
        return {"passed": False, "problem": "no work/config/sound_music.json: run tools/sound/music_bed.py"}
    with open(config, encoding="utf-8") as f:
        used = json.load(f)
    voice_path = os.path.join(work, "audio", f"voice_{which}.wav")
    stem_path = os.path.join(work, "audio", "stems", f"{which}-music.wav")
    done = used.get("deliverables", {}).get(which)
    if not done or used["track"]["id"] != row["id"] or not os.path.isfile(stem_path):
        return {"passed": False, "problem": f"no {which} bed for track {row['id']}: run tools/sound/music_bed.py {which}"}
    if done.get("voice_sha256") != library.sha256(voice_path) or done.get("stem_sha256") != library.sha256(stem_path):
        return {"passed": False, "problem": "the voice or music stem changed after the bed was built: rebuild and re-mix"}
    spans = music_bed.word_spans(os.path.join(work, "remotion", "public", "data", "timeline.json"),
                                 os.path.join(work, "audio", "trailer_ranges.json") if which == "trailer" else None)
    voice, _ = sf.read(voice_path)
    stem, _ = sf.read(stem_path)
    measured = lw.gap(voice, stem, spans, used["params"])
    measured["passed"] = measured["worst_db"] >= used["params"]["gap_fail_db"]
    measured["worst_beat"] = beat_label(
        os.path.join(work, "remotion", "public", "data", "timeline.json"), measured["worst_at_s"],
        os.path.join(work, "audio", "trailer_ranges.json") if which == "trailer" else None)
    if not measured["passed"]:
        measured["problem"] = f"worst gap below {used['params']['gap_fail_db']} dB"
    return measured


def check_clarity(project: str, work: str, which: str, deliverable: str, language: str,
                  mix_transcript: str | None) -> dict:
    out = os.path.join(work, "transcript", "clarity", which)
    heard = None
    if mix_transcript:
        if os.path.getmtime(mix_transcript) < os.path.getmtime(deliverable):
            raise SystemExit(f"{mix_transcript} is older than {deliverable}: it transcribes another render")
        heard = clarity.words(mix_transcript)
    os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, f"final_{which}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", deliverable, "-vn", "-ac", "1", "-ar", "48000", wav], check=True)
    return clarity.check(project, os.path.join(work, "audio", f"voice_{which}.wav"), wav, out, language, heard)


def summary_line(which: str, report: dict) -> str:
    parts = [f"{which} {'PASS' if report['passed'] else 'FAIL'}"]
    gap = report.get("gap")
    if gap is None:
        parts.append("no music bed")
    elif "median_db" in gap:
        parts.append(f"voice over music median {gap['median_db']} dB, worst {gap['worst_db']} dB "
                     f"@{gap['worst_at_s']}s ({gap['worst_beat']})")
    if gap and gap.get("problem"):
        parts.append(gap["problem"])
    if "clarity" in report:
        lost = report["clarity"]["missing"]
        tested = f"({report['clarity']['testable_words']} of {report['clarity']['voice_words']} words testable)"
        parts.append(f"clarity PASS {tested}" if not lost else
                     "clarity FAIL: " + ", ".join(f"{w['word']} @{w['at_s']}s" for w in lost[:8]) + f" {tested}")
    m = report["master"]
    parts.append(f"{m['lufs']} LUFS / {m['true_peak_db']} dBTP {'PASS' if m['passed'] else 'FAIL'}")
    return " · ".join(parts)


def run(project: str, deliverable: str, mix_transcript: str | None = None) -> dict:
    work = os.path.join(project, "work")
    which = "trailer" if "_trailer" in os.path.basename(deliverable) else "main"
    state, err = pst.try_load_state(project)
    if err:
        raise SystemExit(f"{project}: project-state.json unreadable ({err})")
    choice = state.get("music")
    if not choice:
        raise SystemExit("no music decision recorded: run tools/music/pick.py (or say none)")
    report: dict = {"which": which, "deliverable": os.path.basename(deliverable), "track": choice.get("id")}
    if choice.get("id"):
        report["gap"] = check_gap(work, which, library.find(choice["id"]))
        if os.path.isfile(os.path.join(work, "audio", "stems", f"{which}-music.wav")) and \
                os.path.getmtime(deliverable) < os.path.getmtime(os.path.join(work, "audio", "stems", f"{which}-music.wav")):
            report["gap"].update(passed=False, problem="the deliverable is older than the music stem: re-mix and mux again")
        report["clarity"] = check_clarity(project, work, which, deliverable, state.get("language", "en"), mix_transcript)
    report["master"] = master(deliverable)
    report["passed"] = all(report[k]["passed"] for k in ("gap", "clarity", "master") if k in report)
    os.makedirs(os.path.join(work, "qa"), exist_ok=True)
    with open(os.path.join(work, "qa", f"voice_over_music_{which}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with project_log_lock(project):
        pst.append_log_line(project, f"**Music QA:** {summary_line(which, report)}")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("deliverable")
    ap.add_argument("--mix-transcript", help="the video-inspect report.json of this exact render (no second Whisper pass)")
    args = ap.parse_args(argv)
    report = run(args.project, args.deliverable, args.mix_transcript)
    print(summary_line(report["which"], report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
