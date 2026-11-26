# SRTs from the final timeline words (pipeline/subtitles.md). Main + trailer, 9:16 only (reel).
# usage (from work/): vt-python tools/captions/make_srt.py --out ../out/<name>_9x16.srt
#   [--trailer-ranges audio/trailer_ranges.json --trailer-out ../out/<name>_trailer_9x16.srt] [--timeline ...]
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument('--timeline', default='remotion/public/data/timeline.json'); ap.add_argument('--out', required=True)
ap.add_argument('--trailer-ranges'); ap.add_argument('--trailer-out')
args = ap.parse_args()
if bool(args.trailer_ranges) != bool(args.trailer_out): ap.error('--trailer-ranges and --trailer-out go together')
TL = json.load(open(args.timeline))
W = TL['words']; FPS = 30
for w in W: w['t'] = (w['w'].rstrip('!') + ('' if w['w'].endswith('?') else w['p'])) if w['w'] else ''

def cues(words, offset=0):
    out, cur = [], []
    def flush():
        if cur: out.append(cur[:]); cur.clear()
    for i, w in enumerate(words):
        if not w['t']: continue
        txt = ' '.join(x['t'] for x in cur + [w])
        prev = ' '.join(x['t'] for x in cur)
        gap = cur and w['s'] - cur[-1]['e'] > 18 and (cur[-1]['p'] or len(prev) >= 24)  # short CTC words leave fake gaps mid-phrase
        if cur and (len(txt) > 76 or gap or (w['s'] - cur[0]['s']) > 5.5 * FPS): flush()
        cur.append(w)
        if w['p'] in '.?!' and w['p'] and len(' '.join(x['t'] for x in cur)) > 20: flush()
        elif w['p'] == ',' and len(' '.join(x['t'] for x in cur)) > 40: flush()
    flush()
    res = []
    for c in out:
        text = ' '.join(x['t'] for x in c)
        if len(text) > 42:  # two lines, break near the middle at a space (prefer after punctuation)
            words_ = text.split(' '); best, bi = 1e9, 1
            for k in range(1, len(words_)):
                a = ' '.join(words_[:k]); score = abs(len(a) - len(text) / 2) - (8 if a[-1] in ',.:?' else 0)
                if words_[k - 1].lower() in ('a', 'an', 'the', 'your', 'to', 'of', 'in', 'with'): score += 20
                if score < best: best, bi = score, k
            text = ' '.join(words_[:bi]) + '\n' + ' '.join(words_[bi:])
        s = c[0]['s'] - offset; e = c[-1]['e'] - offset + 6
        res.append([s, e, text])
    for i in range(len(res) - 1):  # no overlaps; min 1 s where possible
        res[i][1] = min(max(res[i][1], res[i][0] + FPS), res[i + 1][0])
    return res

def ts(f):
    ms = round(f / FPS * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def write(path, cs):
    with open(path, 'w') as fh:
        for i, (s, e, t) in enumerate(cs, 1): fh.write(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n")
    print(path, len(cs), 'cues, last ends', ts(cs[-1][1]))

write(args.out, cues(W))
if args.trailer_ranges:
    # = TRAILER in remotion/src/plan.ts (the short cut mapped to recorded lines), exported as {"ranges": [[from, to], ...]} in frames
    TR = [tuple(r) for r in json.load(open(args.trailer_ranges))['ranges']]
    allc, off = [], 0
    for a, b in TR:
        seg = [w for w in W if a <= w['s'] < b]
        for s_, e, t in cues(seg, a): allc.append([max(0, s_) + off, min(e, b - a) + off, t])
        off += b - a
    print('trailer frames (without end card):', off, f'{off/FPS:.2f}s')
    write(args.trailer_out, allc)
