#!/usr/bin/env python3
"""Shared validation for video projects. Compact JSON report to stdout."""
import argparse
import json
import os
import re
import subprocess
import sys

TOOLKIT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _err(code, message, **kw):
    return {"code": code, "message": message, **kw}


def check_project(project: str) -> list:
    errs = []
    required = ["script.md", "log.md"]
    for f in required:
        if not os.path.isfile(os.path.join(project, f)):
            errs.append(_err("MISSING_FILE", f"Required file missing", file=f))
    for d in ["raw", "work", "out"]:
        if not os.path.isdir(os.path.join(project, d)):
            errs.append(_err("MISSING_DIR", f"Expected directory missing", path=d))
    return errs


def check_stage(project: str) -> list:
    errs = []
    state_file = os.path.join(project, "project-state.json")
    if not os.path.isfile(state_file):
        errs.append(
            _err(
                "NO_STATE",
                "project-state.json missing; run tools/project_state.py init",
                file=state_file,
            )
        )
        return errs
    with open(state_file) as f:
        st = json.load(f)
    stage = st.get("stage", "prep")
    approvals = st.get("approvals", {})
    if stage == "compose" and not approvals.get("rough_cut"):
        errs.append(
            _err(
                "ROUGH_CUT_NOT_APPROVED",
                "Compose requires rough_cut approval in project-state or log",
            )
        )
    return errs


def check_subtitles(path: str) -> list:
    errs = []
    if not os.path.isfile(path):
        return [_err("MISSING_FILE", "SRT not found", file=path)]
    prev_end = None
    with open(path, encoding="utf-8", errors="replace") as f:
        blocks = re.split(r"\n\n+", f.read().strip())
    ts_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
    )

    def to_ms(h, m, s, ms):
        return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

    for i, block in enumerate(blocks, 1):
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        m = ts_re.match(lines[1] if lines[0].isdigit() else lines[0])
        if not m and lines[0].isdigit():
            m = ts_re.match(lines[1])
        if not m:
            errs.append(_err("SRT_BAD_TIMESTAMP", "Unparseable cue", index=i))
            continue
        start = to_ms(*m.groups()[:4])
        end = to_ms(*m.groups()[4:])
        if end <= start:
            errs.append(_err("SRT_BAD_INTERVAL", "Cue end before start", index=i))
        if prev_end is not None and start < prev_end:
            errs.append(_err("SRT_OVERLAP", "Overlapping cues", index=i))
        prev_end = end
    return errs


def check_render(path: str, expect: dict | None = None) -> list:
    errs = []
    if not os.path.isfile(path):
        return [_err("MISSING_FILE", "Video not found", file=path)]
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=width,height,r_frame_rate,codec_name",
                "-of",
                "json",
                path,
            ],
            text=True,
        )
        data = json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return [_err("FFPROBE_FAILED", str(e), file=path)]
    streams = data.get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video" or "width" in s), streams[0] if streams else {})
    dur = float((data.get("format") or {}).get("duration") or 0)
    if expect:
        if expect.get("width") and v.get("width") != expect["width"]:
            errs.append(
                _err("BAD_WIDTH", f"width {v.get('width')} != {expect['width']}", file=path)
            )
        if expect.get("height") and v.get("height") != expect["height"]:
            errs.append(
                _err("BAD_HEIGHT", f"height {v.get('height')} != {expect['height']}", file=path)
            )
        if expect.get("max_duration") and dur > expect["max_duration"] + 0.05:
            errs.append(
                _err("BAD_DURATION", f"duration {dur:.2f}s too long", file=path)
            )
    return errs


def check_phrases(project: str, timeline_path: str, scene_glob: str) -> list:
    errs = []
    if not os.path.isfile(timeline_path):
        return [_err("MISSING_TIMELINE", "timeline.json not found", file=timeline_path)]
    with open(timeline_path) as f:
        tl = json.load(f)
    words = []
    for w in tl.get("words") or tl.get("timeline", {}).get("words") or []:
        if isinstance(w, dict):
            words.append(str(w.get("word") or w.get("text") or "").lower())
        elif isinstance(w, (list, tuple)) and len(w) >= 3:
            words.append(str(w[2]).lower())
    corpus = " ".join(words)
    remotion = os.path.join(project, "work", "remotion")
    if not os.path.isdir(remotion):
        return errs
    pat = re.compile(r"""at\s*\(\s*['"]([^'"]+)['"]""")
    for root, _, files in os.walk(remotion):
        for fn in files:
            if not fn.endswith((".tsx", ".ts")):
                continue
            if scene_glob and scene_glob not in os.path.join(root, fn):
                pass
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8") as f:
                text = f.read()
            for phrase in pat.findall(text):
                needle = phrase.lower().replace("-", " ")
                if needle and needle not in corpus and phrase.lower() not in corpus:
                    errs.append(
                        _err(
                            "MISSING_PHRASE",
                            "Phrase not found in timeline words",
                            file=p,
                            phrase=phrase,
                        )
                    )
    return errs


CHECKS = {
    "project": check_project,
    "stage": check_stage,
}


def main():
    ap = argparse.ArgumentParser(description="Validate video project artifacts")
    ap.add_argument("project", help="projects/<name>/ path")
    ap.add_argument(
        "--check",
        action="append",
        choices=["project", "stage", "subtitles", "render", "phrases"],
        default=["project"],
    )
    ap.add_argument("--srt", help="SRT path for subtitles check")
    ap.add_argument("--video", help="MP4 path for render check")
    ap.add_argument("--timeline", help="timeline.json for phrases check")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--max-duration", type=float)
    args = ap.parse_args()

    errors = []
    checks_run = {}
    for name in args.check:
        if name in CHECKS:
            e = CHECKS[name](args.project)
            checks_run[name] = "failed" if e else "passed"
            errors.extend(e)
        elif name == "subtitles":
            if not args.srt:
                sys.exit("--srt required for subtitles check")
            e = check_subtitles(args.srt)
            checks_run[name] = "failed" if e else "passed"
            errors.extend(e)
        elif name == "render":
            if not args.video:
                sys.exit("--video required for render check")
            expect = {}
            if args.width:
                expect["width"] = args.width
            if args.height:
                expect["height"] = args.height
            if args.max_duration:
                expect["max_duration"] = args.max_duration
            e = check_render(args.video, expect or None)
            checks_run[name] = "failed" if e else "passed"
            errors.extend(e)
        elif name == "phrases":
            tl = args.timeline or os.path.join(
                args.project, "work", "remotion", "public", "data", "timeline.json"
            )
            e = check_phrases(args.project, tl, "")
            checks_run[name] = "failed" if e else "passed"
            errors.extend(e)

    report = {
        "status": "failed" if errors else "passed",
        "checks": checks_run,
        "errors": errors,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()