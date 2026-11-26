#!/usr/bin/env python3
"""Roman Hindi captions from tools only (pipeline/hindi-twin.md). Nobody writes caption text by hand.

usage (from work/):
  vt-python tools/captions/hindi_captions.py --script ../script.md --heard transcript/hi/voice.json \
      --wav audio/voice.wav [--project <name>-hi] [--no-learn]
  vt-python tools/captions/hindi_captions.py --romanize-only --heard transcript/hi/source.json \
      --romanize-out transcript/hi/source_roman.txt          (readable source transcript for take selection)

The romanized script gives the caption text, Whisper (language=hi) checks what was said, and the MMS
aligner gives the times. Writes transcript/caption_text.md, transcript/words_aligned.json,
captions/hi-display.json and captions/hi-report.json; then run
  tools/captions/build_timeline.py transcript/words_aligned.json <K> --display captions/hi-display.json
Timestamps come only from the aligner; transliteration and formatting never change them.
Exit: 0 ok · 2 a spoken word could not be romanized (nothing but the report is written).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from statistics import median

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from tools.captions import hindi_numbers, hindi_text as ht  # noqa: E402

LANG = os.path.join(REPO, "languages", "hi")


def load_settings(path: str) -> dict:
    """Matching thresholds and the transliterator command: languages/hi/config.json."""
    return ht.load_json(path, {})


def heard_words(path: str) -> list[dict]:
    """Whisper JSON -> [{text, s, e}]."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [{"text": w["word"].strip(), "s": w["start"], "e": w["end"]}
            for seg in data["segments"] for w in seg.get("words", []) if ht.bare(w["word"])]


def run_json(command: list[str], payload, suffix: str = ""):
    """Run `command in.json out.json` and return the parsed output."""
    with tempfile.TemporaryDirectory() as td:
        src, dst = os.path.join(td, f"in{suffix}.json"), os.path.join(td, "out.json")
        with open(src, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        r = subprocess.run([*command, src, dst], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{' '.join(command)} failed:\n{r.stderr[-1500:]}")
        with open(dst, encoding="utf-8") as f:
            return json.load(f)


def romanize(words: list[str], dictionary: dict, command: list[str] | None) -> dict[str, dict]:
    """word -> {candidates, source}. Dictionary first, then the model; Latin passes through."""
    out, ask = {}, []
    for word in dict.fromkeys(ht.bare(w) for w in words):
        if not ht.DEVANAGARI.search(word):
            out[word] = {"candidates": [word], "source": "latin"}
        elif word in dictionary:
            out[word] = {"candidates": [dictionary[word]["roman"]], "source": "dictionary"}
        else:
            ask.append(word)
    answers = run_json(command, ask) if ask and command else {}
    for word in ask:
        found = [c for c in answers.get(word, []) if c and not ht.DEVANAGARI.search(c)]
        out[word] = {"candidates": found, "source": "model" if found else "unknown"}
    return out


def model_candidates(words: list[str], command: list[str] | None) -> dict[str, list[str]]:
    """Model spellings for matching, including dictionary words (a second chance to match the script)."""
    ask = [w for w in dict.fromkeys(ht.bare(x) for x in words) if ht.DEVANAGARI.search(w)]
    return run_json(command, ask) if ask and command else {}


def plan(script_text: str, heard: list[dict], dictionary: dict, glossary: dict, settings: dict,
         translit: list[str] | None, tables: dict) -> dict:
    """The text side: which tokens are captions, in spoken order, with their beat and origin."""
    beats = ht.script_beats(script_text)
    script = [(beat, tok) for beat, said in beats for tok in ht.tokens(said)]
    if not script:
        sys.exit("no beat lines with IDs found in the script ([B01 | HEAD] ...)")
    roman = romanize([w["text"] for w in heard], dictionary, translit)
    extra = model_candidates([w["text"] for w in heard if ht.bare(w["text"]) in dictionary], translit)

    def candidates(word: str) -> list[str]:
        base = roman[ht.bare(word)]["candidates"]
        return list(dict.fromkeys(base + extra.get(ht.bare(word), [])))

    script_units = ht.number_units([[tok] for _, tok in script], tables)
    heard_units = ht.number_units([candidates(w["text"]) for w in heard], tables)
    merged = ht.diff(script_units, heard_units, settings.get("similarity", 0.6), tables)

    captions, flags, pairs = [], [], []
    counts = dict(script_words=len(script), heard_words=len(heard), matched=0, adlib=0, dropped=0, unknown=0,
                  check=0)
    last_beat = script[0][0]
    for si, hi, sim in merged:
        if si is not None and hi is not None:
            s_unit, h_unit = script_units[si], heard_units[hi]
            beat = script[s_unit.indexes[0]][0]
            time = heard[h_unit.indexes[0]]["s"]
            for k in s_unit.indexes:
                captions.append({"beat": script[k][0], "text": ht.apply_glossary(script[k][1], glossary),
                                 "kind": "script", "heard_at": time})
            counts["matched"] += len(s_unit.indexes)
            said = " ".join(heard[k]["text"] for k in h_unit.indexes)
            if sim < settings.get("check_below", 0.75):
                counts["check"] += 1
                flags.append({"beat": beat, "time": time, "kind": "check", "text": script[s_unit.indexes[0]][1],
                              "detail": f"heard {said!r} (similarity {sim:.2f})"})
            # learn only a clear one-word-to-one-word match
            if len(s_unit.indexes) == len(h_unit.indexes) == 1 and sim >= settings.get("learn_similarity", 0.75):
                word = ht.bare(heard[h_unit.indexes[0]]["text"])
                if ht.DEVANAGARI.fullmatch(word[:1] or " ") and not word.isdigit():
                    pairs.append((word, ht.spelling(script[s_unit.indexes[0]][1], glossary)))
            last_beat = script[s_unit.indexes[-1]][0]
        elif si is not None:
            for k in script_units[si].indexes:
                counts["dropped"] += 1
                flags.append({"beat": script[k][0], "time": None, "kind": "dropped", "text": script[k][1],
                              "detail": "in the script, not heard: left out of the captions"})
                last_beat = script[k][0]
        else:
            for k in heard_units[hi].indexes:
                word = heard[k]
                info = roman[ht.bare(word["text"])]
                if not info["candidates"]:
                    counts["unknown"] += 1
                    flags.append({"beat": last_beat, "time": word["s"], "kind": "unknown", "text": word["text"],
                                  "detail": "spoken, and no romanization from the dictionary or the model"})
                    continue
                shown = info["candidates"][0]
                punct = ht.SENTENCE_END.search(word["text"])
                if punct:
                    shown += "." if punct[0] == "।" else punct[0]
                shown = ht.apply_glossary(shown, glossary)
                counts["adlib"] += 1
                captions.append({"beat": last_beat, "text": shown, "kind": "adlib", "heard_at": word["s"]})
                flags.append({"beat": last_beat, "time": word["s"], "kind": "adlib", "text": shown,
                              "detail": f"not in the script; heard {word['text']!r}, from {info['source']}"})
    return {"captions": captions, "flags": flags, "counts": counts, "pairs": pairs}


def timed(captions: list[dict], aligned: list) -> list[list]:
    """[[start, end, token]] from the aligner. A token it couldn't align sits between its neighbours."""
    times: list = [None if a is None else [a[0], a[1]] for a in aligned]
    for i, t in enumerate(times):
        if t is None:
            before = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            after = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), before + 0.3)
            gap_from = max(before, 0.0)
            times[i] = [gap_from, max(after, gap_from + 0.04)]
    out, floor = [], 0.0
    for (s, e), caption in zip(times, captions):
        s = max(s, floor)
        out.append([round(s, 3), round(max(e, s + 0.04), 3), caption["text"]])
        floor = s + 0.02
    return out


def number_display(captions: list[dict], tables: dict) -> dict[str, str]:
    """token index -> shown text for spoken numbers ('' hides a merged token). Never crosses a beat or a
    punctuation mark; only the shown text changes."""
    display: dict[str, str] = {}
    start = 0
    for i, c in enumerate(captions):
        last = i + 1 == len(captions)
        if last or captions[i + 1]["beat"] != c["beat"] or c["text"].rstrip("\"'")[-1:] in ".,?!:;":
            words = [ht.number_form(x["text"]) for x in captions[start:i + 1]]
            for a, b, shown in hindi_numbers.display_runs(words, tables):
                display[str(start + a)] = shown
                for k in range(a + 1, b):
                    display[str(start + k)] = ""
            start = i + 1
    return display


def caption_markdown(captions: list[dict]) -> str:
    out, beat = [], None
    for c in captions:
        if c["beat"] != beat:
            beat = c["beat"]
            out.append(f"### {beat}\n")
        out[-1] += c["text"] + " "
    return "\n".join(block.rstrip() + "\n" for block in out)


def onset_error(wav: str, words: list[list]) -> dict | None:
    """Aligned start vs the energy onset, for words that follow a pause (the check used for English)."""
    import numpy as np
    import soundfile as sf

    x, sr = sf.read(wav)
    if x.ndim > 1:
        x = x.mean(1)
    hop = sr // 100
    n = len(x) // hop
    level = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    errors, previous_end = [], 0.0
    for s, e, _ in words:
        if s - previous_end >= 0.15:
            lo, hi = max(5, int((s - 0.4) * 100)), min(n, int((s + 0.4) * 100))
            onsets = [k / 100 for k in range(lo, hi) if level[k] > -28 and (level[k - 5:k] < -35).all()]
            if onsets:
                errors.append(s - min(onsets, key=lambda o: abs(o - s)))
        previous_end = e
    if not errors:
        return None
    absolute = sorted(abs(v) for v in errors)
    return {"words": len(errors), "median_signed_s": round(median(errors), 3),
            "median_abs_s": round(median(absolute), 3), "p90_abs_s": round(absolute[int(0.9 * (len(absolute) - 1))], 3)}


def summary_lines(report: dict) -> list[str]:
    c = report["counts"]
    lines = [
        f"Hindi captions: {report['status']}",
        f"script {c['script_words']} · heard {c['heard_words']} · matched {c['matched']} · ad-lib {c['adlib']} · "
        f"dropped {c['dropped']} · unknown {c['unknown']} · to check {c['check']}",
        f"dictionary: {len(report['learned'])} learned, {len(report['conflicts'])} conflict(s)",
    ]
    weak = sorted((v["align_confidence"], b) for b, v in report["beats"].items() if v["align_confidence"] is not None)[:3]
    if weak:
        lines.append("weakest alignment: " + " · ".join(f"{b} {p:.2f}" for p, b in weak))
    if report.get("onset"):
        o = report["onset"]
        lines.append(f"onsets vs energy ({o['words']} words after a pause): median |{o['median_abs_s']}| s, p90 {o['p90_abs_s']} s")
    order = {"unknown": 0, "dropped": 1, "adlib": 2, "check": 3}
    flags = sorted(report["flags"], key=lambda f: order[f["kind"]])
    room = 20 - len(lines) - 1
    for f in flags[:room]:
        at = "" if f["time"] is None else f" @{f['time']:.2f}s"
        lines.append(f"{f['kind']:7} {f['beat']}{at} {f['text']!r}")
    if len(flags) > room:
        lines.append(f"… {len(flags) - room} more flag(s) in hi-report.json")
    return lines[:20]


def command_from(value: str | None, default: list[str] | None) -> list[str] | None:
    return value.split() if value else default


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--heard", required=True, help="Whisper JSON from transcribe.py --language hi")
    ap.add_argument("--script")
    ap.add_argument("--wav", help="the cut voice the captions are timed on")
    ap.add_argument("--project", default=os.path.basename(os.path.dirname(os.getcwd())))
    ap.add_argument("--captions-out", default="transcript/caption_text.md")
    ap.add_argument("--words-out", default="transcript/words_aligned.json")
    ap.add_argument("--display-out", default="captions/hi-display.json")
    ap.add_argument("--report", default="captions/hi-report.json")
    ap.add_argument("--dictionary", default=os.path.join(LANG, "romanization.json"))
    ap.add_argument("--glossary", default=os.path.join(LANG, "glossary.json"))
    ap.add_argument("--settings", default=os.path.join(LANG, "config.json"))
    ap.add_argument("--translit-cmd", help="override the transliterator command (tests)")
    ap.add_argument("--align-cmd", help="override the aligner command (tests)")
    ap.add_argument("--no-learn", action="store_true")
    ap.add_argument("--romanize-only", action="store_true")
    ap.add_argument("--romanize-out", default="transcript/hi/source_roman.txt")
    args = ap.parse_args(argv)

    settings = load_settings(args.settings)
    tables = hindi_numbers.load_tables()
    dictionary = ht.load_json(args.dictionary, {})
    translit = command_from(args.translit_cmd, [
        part.replace("{repo}", REPO) for part in (settings.get("translit") or {}).get("command", [])] or None)
    heard = heard_words(args.heard)

    if args.romanize_only:
        roman = romanize([w["text"] for w in heard], dictionary, translit)
        os.makedirs(os.path.dirname(args.romanize_out) or ".", exist_ok=True)
        with open(args.romanize_out, "w", encoding="utf-8") as f:
            for w in heard:
                shown = (roman[ht.bare(w["text"])]["candidates"] or [w["text"]])[0]
                f.write(f"{w['s']:8.2f} {w['e']:8.2f}  {shown}\n")
        print(f"{len(heard)} words -> {args.romanize_out} (for reading only; these are not captions)")
        return 0

    if not args.script or not args.wav:
        ap.error("--script and --wav are required")
    with open(args.script, encoding="utf-8") as f:
        script_text = f.read()
    glossary = ht.load_glossary(args.glossary, script_text)
    p = plan(script_text, heard, dictionary, glossary, settings, translit, tables)
    report = {"status": "ok", "counts": p["counts"], "flags": p["flags"], "beats": {}, "learned": [], "conflicts": [],
              "onset": None, "translit": (settings.get("translit") or {}).get("backend")}

    def write_report():
        os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("\n".join(summary_lines(report)))

    if p["counts"]["unknown"]:
        report["status"] = "FAILED: some spoken words have no romanization"
        write_report()
        return 2

    captions = p["captions"]
    align = command_from(args.align_cmd, ["gpu-run", "vt-python", os.path.join(REPO, "tools", "captions", "align_mms.py"),
                                          os.path.abspath(args.wav)])
    aligned = run_json(align, [c["text"] for c in captions])
    if len(aligned) != len(captions):
        sys.exit(f"aligner returned {len(aligned)} times for {len(captions)} words")
    words = timed(captions, aligned)
    for beat in dict.fromkeys(c["beat"] for c in captions):
        scores = [a[2] for a, c in zip(aligned, captions) if c["beat"] == beat and a is not None]
        report["beats"][beat] = {"words": sum(c["beat"] == beat for c in captions),
                                 "align_confidence": round(sum(scores) / len(scores), 3) if scores else None}
    report["onset"] = onset_error(args.wav, words)

    for path, content in ((args.captions_out, caption_markdown(captions)),
                          (args.words_out, json.dumps(words, ensure_ascii=False)),
                          (args.display_out, json.dumps(number_display(captions, tables), ensure_ascii=False))):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    if p["pairs"]:
        learned, conflicts = ht.learn(dictionary, p["pairs"], args.project)
        report["learned"] = [{"word": w, "roman": dictionary[w]["roman"]} for w in learned]
        report["conflicts"] = conflicts
        if not args.no_learn:
            ht.save_dictionary(args.dictionary, dictionary)
    write_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
