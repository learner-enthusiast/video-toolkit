# CTC onset fix for Whisper word starts (pipeline/transcribe.md).
# usage: gpu-run vt-python tools/captions/align_ctc.py voice.wav words_in.json words_out.json
# words json: [[start, end, "word"], ...]
import sys, json, re, difflib, numpy as np, soundfile as sf, torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

M = "facebook/wav2vec2-large-960h-lv60-self"
wav, win, wout = sys.argv[1:4]
x, sr = sf.read(wav)
if x.ndim > 1: x = x.mean(1)
if sr != 16000:
    import scipy.signal as ss
    x = ss.resample_poly(x, 16000, sr); sr = 16000
proc = Wav2Vec2Processor.from_pretrained(M)
model = Wav2Vec2ForCTC.from_pretrained(M).cuda().eval()
vocab = {v: k for k, v in proc.tokenizer.get_vocab().items()}
blank = proc.tokenizer.pad_token_id
STEP = 0.02  # wav2vec2 frame
ctc_words = []  # (onset, end, word)
W, H = 8.0, 1.0
t = 0.0
dur = len(x) / sr
while t < dur:
    a, b = int(t * sr), int(min(dur, t + W + H) * sr)
    seg = x[a:b].astype(np.float32)
    inp = proc(seg, sampling_rate=16000, return_tensors="pt").input_values.cuda()
    with torch.no_grad():
        ids = model(inp).logits[0].argmax(-1).cpu().numpy()
    cur, cs, prev, last = "", None, blank, None
    for i, k in enumerate(ids):
        ts = t + i * STEP
        if k != blank and k != prev:
            ch = vocab[k]
            if ch == "|":
                if cur: ctc_words.append((cs, last, cur)); cur = ""
            else:
                if not cur: cs = ts
                cur += ch; last = ts + STEP
        prev = k
    if cur: ctc_words.append((cs, last, cur))
    # keep only words starting inside [t, t+W) except at the end
    t += W
ctc_words = sorted({(round(s, 2), w): (s, e, w) for s, e, w in ctc_words}.values())
# dedupe overlap: drop words whose onset is within 0.05 s of the previous with same text
dd = []
for w in ctc_words:
    if dd and w[2] == dd[-1][2] and abs(w[0] - dd[-1][0]) < 0.1: continue
    dd.append(w)
ctc_words = dd
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
words = json.load(open(win))
A = [norm(w[2]) for w in words]
B = [w[2].lower().replace("'", "") for w in ctc_words]
B = [norm(b) for b in B]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
off = [None] * len(words)
for blk in sm.get_matching_blocks():
    for j in range(blk.size):
        i, k = blk.a + j, blk.b + j
        if len(A[i]) >= 2 or blk.size >= 2:
            o = (ctc_words[k][0] - 0.03) - words[i][0]
            if -0.3 <= o <= 0.8: off[i] = o
idx = [i for i, o in enumerate(off) if o is not None]
print(f"matched {len(idx)}/{len(words)}; median offset {np.median([off[i] for i in idx]):+.3f}s p90 {np.percentile([abs(off[i]) for i in idx],90):.3f}")
for i in range(len(words)):
    if off[i] is None and idx:
        off[i] = float(np.interp(i, idx, [off[j] for j in idx]))
out = []
for i, (s, e, w) in enumerate(words):
    ns = s + (off[i] or 0)
    ns = min(ns, e - 0.04)
    if out: ns = max(ns, out[-1][0] + 0.02)
    out.append([round(ns, 3), round(max(e, ns + 0.04), 3), w])
json.dump(out, open(wout, "w"))
big = [(words[i][2], round(off[i], 2)) for i in idx if abs(off[i]) > 0.35]
print("offsets > 0.35 s:", big[:40])
