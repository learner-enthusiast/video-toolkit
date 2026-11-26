# Moves every EDL edge whose 20 ms window is above -35 dB to the quietest 30 fps frame within +-100 ms (take-selection.md).
# usage (from work/): vt-python tools/cut/nudge_edges.py [--wav audio/clean.wav] [--edl edl.json]
import argparse, json, numpy as np, soundfile as sf
ap = argparse.ArgumentParser(); ap.add_argument("--wav", default="audio/clean.wav"); ap.add_argument("--edl", default="edl.json")
args = ap.parse_args()
x, sr = sf.read(args.wav); x = x if x.ndim == 1 else x.mean(1); fr = 1 / 30
def e(t, w=0.02): s = int((t - w / 2) * sr); return 20 * np.log10(np.sqrt(np.mean(x[s:s + int(w * sr)] ** 2)) + 1e-9)
E = json.load(open(args.edl)); S = E["segments"]; moved = []
for seg in S:
    for k in (0, 1):
        t = seg[k]
        if e(t) > -35:
            best = min([round(round(t / fr) * fr + d * fr, 4) for d in range(-3, 4)], key=e)
            if e(best) < e(t): moved.append((round(t, 2), round(best, 2))); seg[k] = best
json.dump(E, open(args.edl, "w"))
print("nudged", moved, "| still loud", [(round(t, 2), round(e(t), 1)) for s in S for t in s if e(t) > -35])
