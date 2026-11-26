# Direct picture sync: in HEAD at 100% framing the output frame IS a source frame. For sampled output frames, find the source-frame offset (vs the EDL + speed mapping) with the smallest image difference.
# Config (config/qa_sync.json): head = [[from, to], ...] spans at 100% framing, emphasis = [frame, ...] punch-in zooms to skip.
# A frame is a number, "total", or {"at": "phrase", "edge": "start"|"end", "offset": n, "from": min_frame} (mirrors plan.ts).
# usage (from work/): vt-python tools/qa/qa_sync_direct.py --video ../out/<name>_9x16.mp4 [--config ...] [--source clips/main.mp4]
import argparse, json, os, re, sys, cv2, numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.pipeline_config import load_config  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument('--video', required=True); ap.add_argument('--config', default='config/qa_sync.json')
ap.add_argument('--source', default='clips/main.mp4'); ap.add_argument('--timeline', default='remotion/public/data/timeline.json')
args = ap.parse_args()
C = load_config(args.config, dict(emphasis=[], rows=[760, 1400], step=9, max_lag=4, emphasis_before=4, emphasis_after=44), required=('head',))
TL = json.load(open(args.timeline)); K = TL['k']; S = TL['segments']
W_ = TL['words']; nn = lambda x: re.sub(r'[^a-z0-9]', '', x.lower()); WN = [nn(w['raw']) for w in W_]
def find(ph, which='s', frm=0):  # mirrors lib/timeline.ts at()/end()
    t = [nn(x) for x in ph.split()]
    i = next((i for i in range(len(WN)) if W_[i]['s'] >= frm and WN[i:i + len(t)] == t), None)
    if i is None: sys.exit(f'phrase not in timeline: {ph!r}')
    return round(W_[i]['s'] if which == 's' else W_[i + len(t) - 1]['e'])
def point(p):
    if p == 'total': return TL['total']
    if isinstance(p, dict): return find(p['at'], 'e' if p.get('edge') == 'end' else 's', p.get('from', 0)) + p.get('offset', 0)
    return p
HEAD = [(point(a), point(b)) for a, b in C['head']]
EMPH = [point(p) for p in C['emphasis']]
LAG = C['max_lag']
def grab(cap, i):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
    return cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)[C['rows'][0]:C['rows'][1]].astype(np.float32) if ok else None
out = cv2.VideoCapture(args.video); src = cv2.VideoCapture(args.source)
res = []
for si, g in enumerate(S):
    if si % 2: continue  # odd segments are punched in to 108%
    for a0, b0 in HEAD:
        a, b = max(g['from'], a0) + 4, min(g['to'], b0) - 4
        for f in range(a, b, C['step']):
            if any(e - C['emphasis_before'] <= f < e + C['emphasis_after'] for e in EMPH): continue
            o = grab(out, f); base = g['srcIn'] + (f - g['from']) * K
            d = {k: float(np.abs(o - grab(src, int(round(base)) + k)).mean()) for k in range(-LAG, LAG + 1)}
            best = min(d, key=d.get); res.append(best)
            print(f'out {f} seg {si} best src offset {best:+d} (diff {d[best]:.2f}; at 0: {d[0]:.2f}; frac {base - round(base):+.2f})')
print('n', len(res), 'median', np.median(res) if res else None, 'hist', {k: res.count(k) for k in sorted(set(res))})
