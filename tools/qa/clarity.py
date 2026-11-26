"""Clarity test: a word Whisper reliably hears in my voice alone must also be heard in the mix.

Whisper changes some words when the audio changes inaudibly (measured: -0.5 dB alone changed 9 of
87 words in a 31 s excerpt of a cut voice), so one pass against one pass blocks clean mixes. Two safeguards:
a word is evidence only if every voice-only pass hears it (as is, CONTROLS), and a loss counts only
if a second pass over the mix misses it too. Every pass is cached.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL = "large-v3"
# The settings tools/inspect/video_inspect.py transcribes with, so its transcript can stand in for the mix.
FLAGS = ["--compute_type", "int8", "--vad_filter", "True", "--best_of", "1",
         "--condition_on_previous_text", "False"]
NEAR = 0.85       # spelling variants ("colour"/"color") are the same heard word
SLACK_S = 1.0
LATER_S = 0.05
CONTROLS = ("quieter", "later")      # inaudible changes: -0.5 dB; 50 ms of leading silence


# Whisper writes "three" in one pass and "3" in the next: a number is the same word either way.
_SMALL = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
          "sixteen seventeen eighteen nineteen twenty").split()
NUMBERS = {word: str(n) for n, word in enumerate(_SMALL)}
NUMBERS.update({word: str(n * 10) for n, word in
                enumerate("thirty forty fifty sixty seventy eighty ninety".split(), 3)})
NUMBERS.update({word: str(n) for n, word in enumerate("शून्य एक दो तीन चार पांच छह सात आठ नौ दस".split())})


def transcribe(project: str, wav: str, out_dir: str, language: str) -> list[list]:
    """[[start, end, word]] from one cached Whisper pass on the GPU (tools/captions/transcribe.py)."""
    cmd = [sys.executable, os.path.join(REPO, "tools", "captions", "transcribe.py"), project, wav,
           "--out-dir", out_dir, "--model", MODEL, "--language", language, "--", *FLAGS]
    if subprocess.run(cmd).returncode:
        raise SystemExit(f"clarity test: transcription of {wav} failed; not run on the CPU instead")
    return words(os.path.join(out_dir, os.path.splitext(os.path.basename(wav))[0] + ".json"))


def variant(wav: str, name: str, out_dir: str) -> str:
    """An inaudibly different copy of `wav`."""
    import numpy as np
    import soundfile as sf
    samples, rate = sf.read(wav)
    if name == "quieter":
        samples = samples * 10 ** (-0.5 / 20)
    else:
        samples = np.concatenate([np.zeros((int(LATER_S * rate), *samples.shape[1:])), samples])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(wav))[0]}_{name}.wav")
    sf.write(path, samples, rate, subtype="PCM_24")
    return path


def heard_in(project: str, wav: str, out_dir: str, language: str, change: str | None = None) -> list[list]:
    """One transcript of `wav` (or of an inaudibly changed copy), on `wav`'s own clock."""
    source = variant(wav, change, out_dir) if change else wav
    found = transcribe(project, source, os.path.join(out_dir, change or "as-is"), language)
    offset = LATER_S if change == "later" else 0.0
    return [[s - offset, e - offset, w] for s, e, w in found]


def check(project: str, voice_wav: str, mix_wav: str, out_dir: str, language: str,
          mix_words: list | None = None) -> dict:
    """`mix_words`: an existing transcript of the mix, used for its first pass."""
    key = lambda w: (w["at_s"], w["word"])
    base = heard_in(project, voice_wav, os.path.join(out_dir, "voice"), language)
    unstable = set()
    for change in CONTROLS:
        again = heard_in(project, voice_wav, os.path.join(out_dir, "voice"), language, change)
        unstable.update(key(w) for w in missing_words(base, again))
    first = mix_words or heard_in(project, mix_wav, os.path.join(out_dir, "mix"), language)
    lost = [w for w in missing_words(base, first) if key(w) not in unstable]
    if lost:
        second = {key(w) for w in missing_words(base, heard_in(project, mix_wav, os.path.join(out_dir, "mix"),
                                                                language, "later"))}
        lost = [w for w in lost if key(w) in second]
    total = sum(1 for w in base if token(w[2]))
    return {"passed": not lost, "voice_words": total, "testable_words": total - len(unstable), "missing": lost}


def words(path: str) -> list[list]:
    """Word timings from a whisper-ctranslate2 JSON or a video-inspect report.json."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "segments" in data:
        found = [[w["start"], w["end"], w["word"].strip()] for s in data["segments"] for w in s.get("words", [])]
    else:
        found = [list(w[:3]) for w in data.get("words", []) if isinstance(w, list)]
    if not found:
        raise SystemExit(f"{path}: no word timestamps")
    return found


def letters(word: str) -> str:
    """Letters, marks (Devanagari vowel signs) and digits only, case-folded."""
    kept = "".join(c for c in unicodedata.normalize("NFKC", word).casefold() if unicodedata.category(c)[0] in "LMN")
    return "".join(str(unicodedata.digit(c)) if unicodedata.category(c) == "Nd" else c for c in kept)


def token(word: str) -> str:
    """The word as compared: a number word becomes its digits."""
    kept = letters(word)
    return NUMBERS.get(kept, kept)


def joined(first: str, second: str) -> set[str]:
    """How two words (as letters()) can be written as one: "every one" → everyone, "twenty three" → 23."""
    forms = {first + second, token(first + second)}
    first, second = token(first), token(second)
    if first.isdigit() and second.isdigit() and 20 <= int(first) <= 90 and int(first) % 10 == 0 and 0 < int(second) < 10:
        forms.add(str(int(first) + int(second)))
    return forms


def missing_words(voice: list, mix: list, slack_s: float = SLACK_S) -> list[dict]:
    """Words in the voice-only transcript that the mix transcript lost or changed."""
    v = [(s, e, w, token(w), letters(w)) for s, e, w in voice if token(w)]
    m = [(s, token(w), letters(w)) for s, _, w in mix if token(w)]
    used = [False] * len(m)
    matcher = SequenceMatcher(None, [x[3] for x in v], [x[1] for x in m], autojunk=False)
    pending = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            used[j1:j2] = [True] * (j2 - j1)
        elif i2 > i1:
            ours, theirs = "".join(x[4] for x in v[i1:i2]), "".join(x[2] for x in m[j1:j2])
            if theirs and ours == theirs:                       # "every one" / "everyone"
                used[j1:j2] = [True] * (j2 - j1)
            else:
                pending.extend(range(i1, i2))
    lost, matched = [], set()
    for i in pending:
        if i in matched:
            continue
        start, _, shown, ours, raw = v[i]
        near = [j for j, found in enumerate(m) if not used[j] and abs(found[0] - start) <= slack_s]
        # one word heard as one, two of mine heard as one, or one of mine heard as two
        for j in near:
            if SequenceMatcher(None, ours, m[j][1]).ratio() >= NEAR:
                used[j] = True
                break
            if i + 1 in pending and m[j][1] in joined(raw, v[i + 1][4]):
                used[j] = True
                matched.add(i + 1)
                break
            if j + 1 < len(m) and not used[j + 1] and ours in joined(m[j][2], m[j + 1][2]):
                used[j] = used[j + 1] = True
                break
        else:
            lost.append({"at_s": round(start, 2), "word": shown})
    return lost
