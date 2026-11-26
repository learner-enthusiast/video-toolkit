# fix CTC onsets that run > 0.45 s after Whisper's start (difflib mis-matches): take the speech onset from the
# energy envelope between Whisper's start and the CTC onset (first rise > -28 dB after >= 60 ms below -35 dB);
# fall back to Whisper + 0.13 s (median offset)
# usage (from work/): vt-python tools/captions/clamp_ctc.py [--ctc ...] [--whisper ...] [--wav ...] [--out ...]
import argparse, json, numpy as np, soundfile as sf
ap = argparse.ArgumentParser()
for flag, default in (('--ctc', 'transcript/words_ctc.json'), ('--whisper', 'transcript/cut_words.json'), ('--wav', 'audio/voice.wav'), ('--out', 'transcript/words_ctc_fixed.json')):
    ap.add_argument(flag, default=default)
args = ap.parse_args()
C = json.load(open(args.ctc)); Wh = json.load(open(args.whisper))
assert len(C) == len(Wh)
x, sr = sf.read(args.wav); x = x if x.ndim == 1 else x.mean(1); w = int(sr * 0.01); n = len(x) // w
r = 20 * np.log10(np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)
def onset(a, b):
    i0, i1 = max(0, int(a * 100) - 10), min(n - 1, int(b * 100) + 10)
    for i in range(i0 + 6, i1):
        if r[i] > -28 and (r[i - 6:i] < -35).all(): return i / 100
    return None
out, k = [], 0
for (cs, ce, wd), (ws, we, _) in zip(C, Wh):
    if cs - ws > 0.45:
        o = onset(ws, cs); ns = o if o is not None else ws + 0.13; k += 1
        print(f'fix {wd!r} ctc {cs:.2f} whisper {ws:.2f} -> {ns:.2f} ({"energy" if o is not None else "whisper+0.13"})')
        out.append([ns, max(ns + 0.04, ce - (cs - ns)), wd])
    else: out.append([cs, ce, wd])
for i in range(1, len(out)):
    if out[i][0] < out[i - 1][0] + 0.02: out[i][0] = out[i - 1][0] + 0.02; out[i][1] = max(out[i][1], out[i][0] + 0.04)
json.dump(out, open(args.out, 'w')); print('fixed', k)
