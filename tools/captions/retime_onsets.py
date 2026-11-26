"""Snap caption word starts to measured speech onsets in the final voice.
For each word, look for a quiet->loud onset (>= 50 ms below -35 dB, then > -28 dB) in [s-0.4, s+0.15] s; correction = s - (onset-0.03).
Corrections are interpolated over time for words with no detectable onset (clamped to [-0.05, 0.40] s); times stay monotonic.
usage: vt-python tools/captions/retime_onsets.py voice.wav timeline.json (in place)"""
import sys, json, numpy as np, soundfile as sf
wav, tlp = sys.argv[1:3]
tl = json.load(open(tlp)); W = tl['words']; FPS = tl['fps']
x, sr = sf.read(wav); x = x.mean(1) if x.ndim > 1 else x
h = sr // 100; n = len(x) // h
e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
ts, cs = [], []; ps = -1.0
for w in W:
    s = w['s'] / FPS; i0 = max(5, int(max(s - 0.4, ps + 0.08) * 100)); i1 = min(n, int((s + 0.15) * 100)); ps = s  # never look back past the previous word (fast speech: its onset is not ours)
    on = None
    for k in range(i0, i1):
        if e[k] > -28 and e[k - 5:k].max() < -35: on = k / 100
    if on is not None: ts.append(s); cs.append(s - (on - 0.03))
ts, cs = np.array(ts), np.clip(np.array(cs), -0.05, 0.40)
corr = np.interp([w['s'] / FPS for w in W], ts, cs)
prev = 0
for w, c in zip(W, corr):
    d = c * FPS
    w['s'] = round(max(prev, w['s'] - d), 2); w['e'] = round(max(w['s'] + 2, w['e'] - d), 2); prev = w['s']
tl['speechEnd'] = W[-1]['e']
json.dump(tl, open(tlp, 'w'), indent=0)
print(f'onsets={len(ts)} median_corr={np.median(cs):.3f}s p90={np.percentile(cs, 90):.3f}s applied_mean={corr.mean():.3f}s')
