#!/usr/bin/env python3
"""Shared validation for video projects. Compact JSON report to stdout."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

# Allow running as script or module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools import project_state as pst  # noqa: E402

SCHEMA_VERSION = 1
NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def _err(code, message, severity="error", **kw):
    return {"code": code, "message": message, "severity": severity, **kw}


def check_project(project: str) -> list:
    errs = []
    for f in ("script.md", "log.md"):
        if not os.path.isfile(os.path.join(project, f)):
            errs.append(_err("MISSING_FILE", "Required file missing", file=f))
    for d in ("raw", "work", "out"):
        if not os.path.isdir(os.path.join(project, d)):
            errs.append(_err("MISSING_DIR", "Expected directory missing", path=d))
    return errs


def check_state_schema(project: str) -> list:
    sp = pst.state_path(project)
    if not os.path.isfile(sp):
        return [_err("NO_STATE", "project-state.json missing", file=sp)]
    try:
        with open(sp) as f:
            st = json.load(f)
    except json.JSONDecodeError as e:
        return [_err("INVALID_STATE_JSON", str(e), file=sp)]
    except OSError as e:
        return [_err("INVALID_STATE_JSON", str(e), file=sp)]
    if not isinstance(st, dict):
        return [_err("INVALID_STATE_SCHEMA", "top-level JSON must be an object", file=sp)]
    errs = []
    if st.get("schema_version") != SCHEMA_VERSION:
        errs.append(
            _err(
                "INVALID_STATE_SCHEMA",
                f"schema_version {st.get('schema_version')!r} != {SCHEMA_VERSION}",
                file=sp,
            )
        )
    approvals = st.get("approvals")
    if approvals is None:
        errs.append(_err("INVALID_STATE_SCHEMA", "approvals missing", file=sp))
    elif not isinstance(approvals, dict):
        errs.append(_err("INVALID_STATE_SCHEMA", "approvals must be an object", file=sp))
    else:
        for k in pst.APPROVALS:
            if k not in approvals:
                errs.append(_err("INVALID_STATE_SCHEMA", f"approvals.{k} missing", file=sp))
            elif not isinstance(approvals[k], bool):
                errs.append(_err("INVALID_STATE_SCHEMA", f"approvals.{k} must be boolean", file=sp))
    stage = st.get("stage")
    if stage is not None and stage not in pst.STAGES:
        errs.append(_err("INVALID_STATE_SCHEMA", f"unknown stage {stage!r}", file=sp))
    return errs


def check_stage(project: str) -> list:
    errs = []
    schema_errs = check_state_schema(project)
    errs.extend(schema_errs)
    fatal = {e["code"] for e in schema_errs}
    if fatal & {"NO_STATE", "INVALID_STATE_JSON", "INVALID_STATE_SCHEMA"}:
        return errs
    auth = pst.authoritative_approvals(project)
    if auth["source"] == "missing_log":
        errs.append(_err("MISSING_FILE", "log.md required for stage validation", file="log.md"))
        return errs
    st, load_err = pst.try_load_state(project)
    if load_err:
        errs.append(_err(load_err, "project-state.json unreadable", file=pst.state_path(project)))
        return errs
    stage = (st or {}).get("stage", "prep")
    rec = pst.reconcile(project)
    for issue in rec["issues"]:
        errs.append(
            _err(
                "STATE_OUT_OF_SYNC",
                f"{issue['approval']}: log={issue['log']} state={issue['state']}",
                approval=issue["approval"],
                log_evidence=issue.get("log_evidence"),
            )
        )
    if stage in ("compose", "deliver"):
        rc = auth["approvals"]["rough_cut"]
        if rc["status"] == "unverified" and not rc["approved"]:
            errs.append(
                _err(
                    "APPROVAL_UNVERIFIABLE",
                    "No **Approval:** rough_cut=… line in log.md; cannot verify user OK",
                    stage=stage,
                )
            )
        elif rc["status"] == "rejected":
            errs.append(_err("ROUGH_CUT_NOT_APPROVED", "rough_cut=rejected in log", stage=stage))
        elif not rc["approved"]:
            errs.append(_err("ROUGH_CUT_NOT_APPROVED", "rough_cut not approved in log.md", stage=stage))
    return errs


def check_subtitles(path: str, max_chars_per_line: int = 42, max_lines: int = 2) -> list:
    errs = []
    warns = []
    if not os.path.isfile(path):
        return [_err("MISSING_FILE", "SRT not found", file=path)]
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read().strip()
    if not raw:
        return [_err("SRT_EMPTY", "SRT file is empty", file=path)]
    blocks = re.split(r"\n\n+", raw)
    ts_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
    )

    def to_ms(h, m, s, ms):
        return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

    prev_end = None
    expect_index = 1
    for i, block in enumerate(blocks, 1):
        lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            errs.append(_err("SRT_EMPTY_CUE", "Empty cue block", index=i))
            continue
        idx = None
        ts_idx = 0
        if lines[0].isdigit():
            idx = int(lines[0])
            if idx != expect_index:
                warns.append(
                    _err("SRT_INDEX_SKIP", f"expected cue {expect_index}, got {idx}", index=i, severity="warning")
                )
            expect_index = max(expect_index, idx + 1)
            ts_idx = 1
        if ts_idx >= len(lines):
            errs.append(_err("SRT_BAD_TIMESTAMP", "Missing timestamp line", index=i))
            continue
        m = ts_re.match(lines[ts_idx])
        if not m:
            errs.append(_err("SRT_BAD_TIMESTAMP", "Unparseable cue timestamp", index=i))
            continue
        start = to_ms(*m.groups()[:4])
        end = to_ms(*m.groups()[4:])
        if start < 0 or end < 0:
            errs.append(_err("SRT_NEGATIVE_TIME", "Negative timestamp", index=i))
        if end <= start:
            errs.append(_err("SRT_BAD_INTERVAL", "Cue end before start", index=i))
        if prev_end is not None and start < prev_end:
            errs.append(_err("SRT_OVERLAP", "Overlapping cues", index=i))
        text_lines = lines[ts_idx + 1 :]
        if not text_lines:
            errs.append(_err("SRT_EMPTY_TEXT", "Cue has no text", index=i))
        if len(text_lines) > max_lines:
            warns.append(
                _err("SRT_TOO_MANY_LINES", f">{max_lines} lines", index=i, severity="warning")
            )
        for tl in text_lines:
            if len(tl) > max_chars_per_line:
                warns.append(
                    _err("SRT_LONG_LINE", f"line length {len(tl)}", index=i, severity="warning")
                )
        dur = end - start
        if dur > 12000:
            warns.append(_err("SRT_LONG_CUE", f"cue {dur}ms", index=i, severity="warning"))
        prev_end = end
    return errs + warns


def parse_frame_rate(value: str | None) -> float | None:
    if not value:
        return None
    if "/" in value:
        num, den = value.split("/", 1)
        try:
            den_f = float(den)
            if den_f == 0:
                return None
            return float(num) / den_f
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def ffprobe_json(path: str) -> dict:
    return json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=codec_type,codec_name,width,height,"
                "r_frame_rate,avg_frame_rate,pix_fmt,sample_rate,channels",
                "-of",
                "json",
                path,
            ],
            text=True,
            timeout=60,
        )
    )


def ffmpeg_full_decode(path: str) -> None:
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"],
        capture_output=True,
        timeout=120,
        check=True,
    )


def validate_render_cli_args(
    *,
    lufs_required: bool,
    lufs_target,
    true_peak_required: bool,
    true_peak_max,
) -> str | None:
    if lufs_required and lufs_target is None:
        return "--lufs-required requires --lufs-target"
    if true_peak_required and true_peak_max is None:
        return "--true-peak-required requires --true-peak-max"
    return None


def _loudness_requested(expect: dict) -> bool:
    return bool(
        expect.get("lufs_target") is not None
        or expect.get("true_peak_max") is not None
        or expect.get("lufs_required")
        or expect.get("true_peak_required")
    )


def _safe_float(value) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    return f


def _extract_json_objects(text: str) -> list[dict]:
    """Extract balanced `{...}` JSON objects from FFmpeg diagnostic output."""
    objects: list[dict] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        in_str = False
        esc = False
        start = i
        j = i
        while j < n:
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        chunk = text[start : j + 1]
                        try:
                            obj = json.loads(chunk)
                            if isinstance(obj, dict):
                                objects.append(obj)
                        except json.JSONDecodeError:
                            pass
                        i = j + 1
                        break
            j += 1
        else:
            break
    return objects


def _parse_loudnorm_json(stderr: str) -> tuple[float | None, float | None]:
    for data in reversed(_extract_json_objects(stderr)):
        if "input_i" not in data:
            continue
        lufs = _safe_float(data.get("input_i"))
        peak = _safe_float(data.get("input_tp")) if "input_tp" in data else None
        return lufs, peak
    return None, None


def measure_loudness(path: str, expect: dict) -> tuple[list, float | None, float | None]:
    """Return (issues, integrated_lufs, true_peak_db). Uses loudnorm JSON for true peak (input_tp)."""
    if not _loudness_requested(expect):
        return [], None, None
    errs = []
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                path,
                "-af",
                "loudnorm=I=-16:TP=-2:LRA=11:print_format=json",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        if expect.get("lufs_required") or expect.get("true_peak_required"):
            errs.append(_err("LOUDNESS_SKIPPED", f"ffmpeg loudnorm unavailable: {e}", file=path))
        else:
            errs.append(_err("LOUDNESS_SKIPPED", "ffmpeg loudnorm unavailable", severity="warning"))
        return errs, None, None
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "")[:200]
        sev = "error" if expect.get("lufs_required") or expect.get("true_peak_required") else "warning"
        errs.append(_err("LOUDNESS_FAILED", f"ffmpeg loudnorm exit {proc.returncode}: {msg}", severity=sev, file=path))
        return errs, None, None
    lufs, peak = _parse_loudnorm_json(proc.stderr)
    if expect.get("lufs_target") is not None:
        if lufs is None:
            sev = "error" if expect.get("lufs_required") else "warning"
            errs.append(_err("LOUDNESS_UNMEASURED", "Could not parse loudnorm integrated loudness", severity=sev, file=path))
        else:
            target = expect["lufs_target"]
            if abs(lufs - target) > expect.get("lufs_tolerance", 0.5):
                errs.append(
                    _err(
                        "LOUDNESS_OUT_OF_RANGE",
                        f"integrated {lufs:.1f} LUFS, target {target}",
                        file=path,
                        actual=lufs,
                    )
                )
    if expect.get("true_peak_max") is not None:
        if peak is None:
            sev = "error" if expect.get("true_peak_required") else "warning"
            errs.append(_err("TRUE_PEAK_UNMEASURED", "Could not parse loudnorm input_tp", severity=sev, file=path))
        elif peak > expect["true_peak_max"]:
            errs.append(
                _err(
                    "TRUE_PEAK_EXCEEDED",
                    f"true peak {peak:.2f} dBFS > max {expect['true_peak_max']}",
                    file=path,
                    actual=peak,
                )
            )
    return errs, lufs, peak


def check_render(path: str, expect: dict | None = None) -> list:
    errs = []
    if not os.path.isfile(path):
        return [_err("MISSING_FILE", "Video not found", file=path)]
    if os.path.getsize(path) < 256:
        return [_err("RENDER_EMPTY", "Output file too small", file=path)]
    expect = expect or {}
    try:
        data = ffprobe_json(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return [_err("FFPROBE_FAILED", str(e), file=path)]
    streams = data.get("streams") or []
    videos = [s for s in streams if s.get("codec_type") == "video" or ("width" in s and "codec_type" not in s)]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if not videos:
        errs.append(_err("MISSING_VIDEO_STREAM", "No video stream", file=path))
    v = videos[0] if videos else {}
    a = audios[0] if audios else {}
    dur = float((data.get("format") or {}).get("duration") or 0)
    if expect.get("require_audio", True) and not audios:
        errs.append(_err("MISSING_AUDIO_STREAM", "No audio stream", file=path))
    if expect.get("width") and v.get("width") != expect["width"]:
        errs.append(_err("BAD_WIDTH", f"width {v.get('width')} != {expect['width']}", file=path))
    if expect.get("height") and v.get("height") != expect["height"]:
        errs.append(_err("BAD_HEIGHT", f"height {v.get('height')} != {expect['height']}", file=path))
    tol = expect.get("duration_tolerance", 0.5)
    if expect.get("duration") is not None and abs(dur - expect["duration"]) > tol:
        errs.append(
            _err("BAD_DURATION", f"duration {dur:.2f}s expected {expect['duration']}", file=path)
        )
    if expect.get("max_duration") and dur > expect["max_duration"] + tol:
        errs.append(_err("BAD_DURATION", f"duration {dur:.2f}s too long", file=path))
    if expect.get("video_codec") and v.get("codec_name") != expect["video_codec"]:
        errs.append(_err("BAD_CODEC", f"codec {v.get('codec_name')}", file=path))
    if expect.get("pixel_format") and v.get("pix_fmt") != expect["pixel_format"]:
        errs.append(_err("BAD_PIXEL_FORMAT", f"pix_fmt {v.get('pix_fmt')}", file=path))
    if expect.get("fps") is not None:
        actual_fps = parse_frame_rate(v.get("r_frame_rate"))
        avg_fps = parse_frame_rate(v.get("avg_frame_rate"))
        if actual_fps is None and avg_fps is not None:
            actual_fps = avg_fps
        if actual_fps is None:
            errs.append(_err("BAD_FRAME_RATE", f"unparseable fps {v.get('r_frame_rate')}", file=path))
        elif abs(actual_fps - expect["fps"]) > expect.get("fps_tolerance", 0.02):
            errs.append(
                _err(
                    "BAD_FRAME_RATE",
                    f"fps {actual_fps:.3f} expected {expect['fps']}",
                    file=path,
                    actual=actual_fps,
                )
            )
    if expect.get("audio_codec") and a.get("codec_name") != expect["audio_codec"]:
        errs.append(_err("BAD_AUDIO_CODEC", f"audio codec {a.get('codec_name')}", file=path))
    if expect.get("sample_rate") is not None:
        try:
            sr = int(a.get("sample_rate") or 0)
        except (TypeError, ValueError):
            sr = 0
        if sr != expect["sample_rate"]:
            errs.append(_err("BAD_SAMPLE_RATE", f"sample rate {sr}", file=path))
    if expect.get("channels") is not None and a.get("channels") != expect["channels"]:
        errs.append(_err("BAD_CHANNELS", f"channels {a.get('channels')}", file=path))
    try:
        ffmpeg_full_decode(path)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        errs.append(_err("FFMPEG_DECODE_FAILED", str(e)[:200], file=path))
    loudness_errs, _, _ = measure_loudness(path, expect)
    errs.extend(loudness_errs)
    return errs


def _normalize_phrase(phrase: str) -> list[str]:
    low = phrase.lower().strip()
    variants = [low, low.replace("-", " ")]
    tokens = low.split()
    mapped = " ".join(NUMBER_WORDS.get(t, t) for t in tokens)
    if mapped != low:
        variants.append(mapped)
    return variants


def _timeline_corpus(tl: dict) -> str:
    words = []
    for w in tl.get("words") or tl.get("timeline", {}).get("words") or []:
        if isinstance(w, dict):
            words.append(str(w.get("word") or w.get("text") or "").lower())
        elif isinstance(w, (list, tuple)) and len(w) >= 3:
            words.append(str(w[2]).lower())
    return " ".join(words)


def check_phrases(project: str, timeline_path: str, scene_glob: str = "") -> list:
    errs = []
    if not os.path.isfile(timeline_path):
        return [_err("MISSING_TIMELINE", "timeline.json not found", file=timeline_path)]
    with open(timeline_path) as f:
        tl = json.load(f)
    corpus = _timeline_corpus(tl)
    remotion = os.path.join(project, "work", "remotion")
    if not os.path.isdir(remotion):
        return errs
    pat = re.compile(r"""at\s*\(\s*['"]([^'"]+)['"]""")
    skip_dirs = {"node_modules", ".cache", "dist"}
    for root, dirs, files in os.walk(remotion):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in files:
            if not fn.endswith((".tsx", ".ts")):
                continue
            p = os.path.join(root, fn)
            if scene_glob and scene_glob not in p:
                continue
            with open(p, encoding="utf-8") as f:
                text = f.read()
            for phrase in pat.findall(text):
                if not any(v in corpus or v.replace(" ", "-") in corpus for v in _normalize_phrase(phrase)):
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
    "state_schema": check_state_schema,
}


def main():
    ap = argparse.ArgumentParser(description="Validate video project artifacts")
    ap.add_argument("project", help="projects/<name>/ path")
    ap.add_argument(
        "--check",
        action="append",
        choices=list(CHECKS) + ["subtitles", "render", "phrases"],
        default=["project"],
    )
    ap.add_argument("--srt")
    ap.add_argument("--video")
    ap.add_argument("--timeline")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--max-duration", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--lufs-target", type=float)
    ap.add_argument("--lufs-tolerance", type=float, default=0.5)
    ap.add_argument("--lufs-required", action="store_true")
    ap.add_argument("--true-peak-max", type=float, help="Maximum allowed true peak (dBFS)")
    ap.add_argument("--true-peak-required", action="store_true")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--fps-tolerance", type=float, default=0.02)
    ap.add_argument("--video-codec")
    ap.add_argument("--audio-codec")
    ap.add_argument("--pixel-format")
    ap.add_argument("--sample-rate", type=int)
    ap.add_argument("--channels", type=int)
    ap.add_argument("--no-audio-required", action="store_true")
    args = ap.parse_args()
    cli_err = validate_render_cli_args(
        lufs_required=args.lufs_required,
        lufs_target=args.lufs_target,
        true_peak_required=args.true_peak_required,
        true_peak_max=args.true_peak_max,
    )
    if cli_err:
        sys.exit(cli_err)

    errors = []
    checks_run = {}
    for name in args.check:
        if name in CHECKS:
            e = CHECKS[name](args.project)
        elif name == "subtitles":
            if not args.srt:
                sys.exit("--srt required")
            e = check_subtitles(args.srt)
        elif name == "render":
            if not args.video:
                sys.exit("--video required")
            expect = {"require_audio": not args.no_audio_required}
            if args.width:
                expect["width"] = args.width
            if args.height:
                expect["height"] = args.height
            if args.max_duration:
                expect["max_duration"] = args.max_duration
            if args.duration:
                expect["duration"] = args.duration
            if args.lufs_target is not None:
                expect["lufs_target"] = args.lufs_target
            if args.lufs_tolerance is not None:
                expect["lufs_tolerance"] = args.lufs_tolerance
            if args.lufs_required:
                expect["lufs_required"] = True
            if args.true_peak_max is not None:
                expect["true_peak_max"] = args.true_peak_max
            if args.true_peak_required:
                expect["true_peak_required"] = True
            if args.fps is not None:
                expect["fps"] = args.fps
            expect["fps_tolerance"] = args.fps_tolerance
            if args.video_codec:
                expect["video_codec"] = args.video_codec
            if args.audio_codec:
                expect["audio_codec"] = args.audio_codec
            if args.pixel_format:
                expect["pixel_format"] = args.pixel_format
            if args.sample_rate:
                expect["sample_rate"] = args.sample_rate
            if args.channels:
                expect["channels"] = args.channels
            e = check_render(args.video, expect)
        elif name == "phrases":
            tl = args.timeline or os.path.join(
                args.project, "work", "remotion", "public", "data", "timeline.json"
            )
            e = check_phrases(args.project, tl)
        else:
            e = []
        failed = any(x.get("severity", "error") == "error" for x in e)
        checks_run[name] = "failed" if failed else ("warn" if e else "passed")
        errors.extend(e)

    report = {"status": "failed" if any(x.get("severity", "error") == "error" for x in errors) else "passed", "checks": checks_run, "errors": errors}
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(1 if report["status"] == "failed" else 0)


if __name__ == "__main__":
    main()