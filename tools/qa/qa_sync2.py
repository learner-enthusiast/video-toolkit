"""Picture sync vs EDL: motion-energy of the output's face panel vs the source frames the EDL+speed map to.
Best lag must be 0 ±1 output frame. usage: vt-python tools/qa/qa_sync2.py out.mp4 talk.mov timeline.json seg_i,seg_j,seg_k [x0,y0,x1,y1]
The crop is the face panel in the output (default: the 9:16 SPLIT inner square)."""
import sys, json
import numpy as np, cv2

OUT, SRC, TLP = sys.argv[1:4]; SEGS = [int(x) for x in sys.argv[4].split(',')]
PANEL = tuple(int(v) for v in sys.argv[5].split(',')) if len(sys.argv) > 5 else (250, 1190, 830, 1771)
tl = json.load(open(TLP)); sp = tl['speed']

def frames(path, start, n, crop=None):
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_FRAMES, start); out = []
    for _ in range(n):
        ok, fr = cap.read()
        if not ok: break
        if crop: x0, y0, x1, y1 = crop; fr = fr[y0:y1, x0:x1]
        out.append(cv2.resize(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), (96, 96)).astype(np.float32))
    return np.array(out)

res = []
for si in SEGS:
    g = tl['segments'][si]
    a, b = int(np.ceil(g['outIn'])) + 3, int(np.floor(g['outOut'])) - 3
    n = b - a
    o = frames(OUT, a, n, crop=PANEL)
    om = np.abs(np.diff(o, axis=0)).mean((1, 2))
    s0 = int(g['srcIn'] + (a - g['outIn']) * sp) - 20
    src = frames(SRC, max(0, s0), int(n * sp) + 50)
    best = None
    for lag in range(-8, 9):
        idx = [int(round(g['srcIn'] + (a + k + lag - g['outIn']) * sp)) - max(0, s0) for k in range(n)]
        if min(idx) < 0 or max(idx) >= len(src): continue
        sm = np.abs(np.diff(src[idx], axis=0)).mean((1, 2))
        c = np.corrcoef(om, sm)[0, 1]
        if best is None or c > best[1]: best = (lag, c)
    res.append({'seg': si, 'out_s': round(a / 30, 2), 'frames': n, 'best_lag': best[0], 'corr': round(float(best[1]), 3)})
print(json.dumps(res))
print('lag>0: output shows source frames from LATER than the EDL says (picture early vs audio); lag<0: picture late')
