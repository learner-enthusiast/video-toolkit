"""Audio placement check: output voice envelope vs source (pre.wav) envelope for an EDL segment, source time-scaled by speed.
Lag in output frames (+ = output audio LATER than the timeline says). usage: vt-python tools/qa/qa_audio_lag.py voice.wav pre.wav timeline.json segs"""
import sys, json, numpy as np, soundfile as sf
V, S, T = sys.argv[1:4]; segs = [int(x) for x in sys.argv[4].split(',')]
tl = json.load(open(T)); sp = tl['speed']
v, sr = sf.read(V, dtype='float32'); s, _ = sf.read(S, dtype='float32')
if v.ndim > 1: v = v.mean(1)
if s.ndim > 1: s = s.mean(1)
H = sr // 300  # 3.33 ms hop
env = lambda x: np.sqrt(np.convolve(x ** 2, np.ones(H) / H, 'same')[::H] + 1e-10)
for si in segs:
    g = tl['segments'][si]
    a, b = g['outIn'] / 30 + 0.15, g['outOut'] / 30 - 0.15
    o = env(v[int(a * sr):int(b * sr)])
    sa = g['srcIn'] / 30 + (a - g['outIn'] / 30) * sp
    src = s[int(sa * sr):int((sa + (b - a) * sp) * sr)]
    se = env(src); se = np.interp(np.linspace(0, len(se) - 1, len(o)), np.arange(len(se)), se)
    o, se = np.log(o), np.log(se)
    best = max(range(-30, 31), key=lambda L: np.corrcoef(o[max(0, L):len(o) + min(0, L)], se[max(0, -L):len(se) - max(0, L)])[0, 1])
    print(si, round(a, 2), 'lag_ms', round(best * 1000 / 300, 1), 'frames', round(best / 10, 2))
