#!/usr/bin/env python3
"""Forced alignment of romanized text (Hindi + English words as written) with the MMS aligner.

usage: gpu-run vt-python tools/captions/align_mms.py <wav> <words.json> <out.json>
  words.json: ["chalo", "aaj", "Postgres", ...]      out.json: [[start_s, end_s, score] or null, ...]
A word with no letters the model knows (digits, symbols) comes back null.

Model: MahmoudAshraf/mms-300m-1130-forced-aligner (Meta MMS, licence CC-BY-NC 4.0: non-commercial).
The CTC alignment is done here in NumPy, so this needs only the torch and transformers already in
vt-python and doesn't use torchaudio's removed MMS_FA pipeline.
"""
import json
import re
import sys

import numpy as np

MODEL = "MahmoudAshraf/mms-300m-1130-forced-aligner"
REVISION = "49402e9577b1158620820667c218cd494cc44486"  # pinned: the vocabulary and timings depend on it
SR = 16000
STRIDE = 320  # samples per emission frame (20 ms)
WINDOW_S, CONTEXT_S = 30.0, 2.0


def forced_align(logp: np.ndarray, targets: list[int], blank: int) -> list[tuple[int, int, float]]:
    """CTC Viterbi alignment. For each target label: (first frame, last frame + 1, mean probability).

    logp is [frames, vocabulary] log-probabilities. The state path is blank, t1, blank, t2, ... blank;
    two different labels may follow each other without a blank, equal ones may not.
    """
    frames, n = len(logp), len(targets)
    if n == 0:
        return []
    states = np.full(2 * n + 1, blank)
    states[1::2] = targets
    size = len(states)
    can_skip = np.zeros(size, bool)
    can_skip[3::2] = states[3::2] != states[1:-2:2]
    if frames < n:
        raise ValueError(f"{frames} frames cannot hold {n} labels: wrong text for this audio?")
    score = np.full(size, -np.inf)
    score[0], score[1] = logp[0, blank], logp[0, states[1]]
    back = np.zeros((frames, size), np.int8)
    for t in range(1, frames):
        stay = score
        step = np.concatenate(([-np.inf], score[:-1]))
        skip = np.where(can_skip, np.concatenate(([-np.inf, -np.inf], score[:-2])), -np.inf)
        choices = np.stack([stay, step, skip])
        pick = choices.argmax(0)
        score = choices[pick, np.arange(size)] + logp[t, states]
        back[t] = pick
    state = size - 1 if score[size - 1] >= score[size - 2] else size - 2
    if not np.isfinite(score[state]):
        raise ValueError("no alignment path: wrong text for this audio?")
    path = np.empty(frames, int)
    for t in range(frames - 1, -1, -1):
        path[t] = state
        state -= int(back[t, state])  # keep a Python int: an int8 step would overflow the state index
    out = []
    for k in range(n):
        where = np.flatnonzero(path == 2 * k + 1)
        out.append((int(where[0]), int(where[-1]) + 1, float(np.exp(logp[where, targets[k]]).mean())))
    return out


def blank_id(vocab: dict[str, int]) -> int:
    """The CTC blank. In this vocabulary `<blank>` (0) is the blank and `<pad>` (1) is not: taking
    the tokenizer's pad token leaves no usable blank and stretches words across every silence."""
    if "<blank>" not in vocab:
        raise ValueError("the aligner vocabulary has no <blank> token")
    return vocab["<blank>"]


def letters(word: str, vocab: dict[str, int]) -> list[int]:
    return [vocab[c] for c in re.sub(r"[^a-z']", "", word.lower()) if c in vocab]


def align_words(logp: np.ndarray, words: list[str], vocab: dict[str, int], blank: int,
                frame_s: float = STRIDE / SR) -> list[list[float] | None]:
    """[[start, end, score] or None] per word, from emissions."""
    labels, owner = [], []
    for i, word in enumerate(words):
        ids = letters(word, vocab)
        labels += ids
        owner += [i] * len(ids)
    out: list[list[float] | None] = [None] * len(words)
    spans: dict[int, list] = {}
    for (a, b, p), i in zip(forced_align(logp, labels, blank), owner):
        spans.setdefault(i, []).append((a, b, p))
    for i, parts in spans.items():
        out[i] = [round(parts[0][0] * frame_s, 3), round(parts[-1][1] * frame_s, 3),
                  round(float(np.mean([p for *_, p in parts])), 3)]
    return out


def emissions(wav: np.ndarray, model, torch) -> np.ndarray:
    """Log-probabilities for the whole file, computed in windows with context on both sides."""
    window, context = int(WINDOW_S * SR), int(CONTEXT_S * SR)
    chunks = []
    for start in range(0, len(wav), window):
        left = min(context, start)
        piece = wav[start - left: start + window + context]
        if len(piece) < STRIDE * 2:
            break
        x = torch.from_numpy(piece.astype(np.float32)).unsqueeze(0).cuda()
        with torch.no_grad():
            logp = torch.log_softmax(model(x).logits[0].float(), dim=-1).cpu().numpy()
        skip = left // STRIDE
        keep = (min(window, len(wav) - start)) // STRIDE
        chunks.append(logp[skip: skip + keep])
    return np.concatenate(chunks)


def main() -> int:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    import soundfile as sf
    import torch
    from transformers import AutoModelForCTC, AutoTokenizer

    wav_path, words_path, out_path = sys.argv[1:4]
    if not torch.cuda.is_available():
        sys.exit("CUDA is not available: run through gpu-run (no silent CPU fallback)")
    x, sr = sf.read(wav_path)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        from scipy.signal import resample_poly
        x = resample_poly(x, SR, sr)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    vocab = {k.lower(): v for k, v in tokenizer.get_vocab().items()}
    model = AutoModelForCTC.from_pretrained(MODEL, revision=REVISION).cuda().eval()
    with open(words_path, encoding="utf-8") as f:
        words = json.load(f)
    out = align_words(emissions(x, model, torch), words, vocab, blank_id(vocab))
    with open(out_path, "w") as f:
        json.dump(out, f)
    print(f"aligned {sum(o is not None for o in out)}/{len(words)} words with {MODEL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
