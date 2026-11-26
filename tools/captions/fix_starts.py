"""Move sentence/clause-first words that CTC parked on the previous word's tail to the real onset after the pause.
A word is moved when: the previous token ends in . , : ? !, a quiet run (>= 0.15 s below -36 dB) begins within 0.45 s after its
start, the NEXT word also starts after that quiet run (otherwise the word really is spoken before the pause, e.g. "Read it."),
and speech (> -30 dB) resumes within 1.2 s. New start = onset - 0.03 s.
usage: vt-python tools/captions/fix_starts.py voice.wav timeline.json (in place)"""
import sys, json, numpy as np, soundfile as sf
wav, tlp = sys.argv[1:3]
tl = json.load(open(tlp)); W = tl['words']; FPS = tl['fps']
x, sr = sf.read(wav); x = x.mean(1) if x.ndim > 1 else x
h = sr // 100; n = len(x) // h
e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
moved = 0
for i in range(1, len(W) - 1):
    if W[i]['w'] == '' or W[i - 1]['raw'][-1] not in '.,:?!': continue
    k0 = int(W[i]['s'] / FPS * 100); run = None
    for st in range(0, 46):
        if k0 + st + 15 <= n and (e[k0 + st:k0 + st + 15] < -36).all(): run = k0 + st; break
    if run is None: continue
    on = next((k for k in range(run + 15, min(n, k0 + 120)) if e[k] > -30), None)
    if on is None: continue
    if W[i + 1]['s'] / FPS * 100 < run: continue  # next word is before the pause too: this word is right
    ns = round((on / 100 - 0.03) * FPS, 2)
    if ns <= W[i]['s']: continue
    d = ns - W[i]['s']
    print(f"move {W[i]['raw']!r} {W[i]['s'] / FPS:.2f}s -> {ns / FPS:.2f}s")
    W[i]['s'] = ns; W[i]['e'] = max(W[i]['e'], ns + 2); moved += 1
    j = i + 1
    while j < len(W) and W[j]['s'] < W[j - 1]['s'] + 2:  # keep order
        W[j]['s'] = W[j - 1]['s'] + 2; W[j]['e'] = max(W[j]['e'], W[j]['s'] + 2); j += 1
json.dump(tl, open(tlp, 'w'), indent=0)
print('moved', moved)
