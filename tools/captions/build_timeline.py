# Build remotion/public/data/timeline.json from edl.json + CTC-aligned voice words + script.md.
# Caption words are the SCRIPT tokens (glossary spellings, intended words for slips) timed by the transcript.
# usage (from work/): vt-python tools/captions/build_timeline.py transcript/words_ctc_fixed.json K --config config/build_timeline.json
# Config keys (all optional): tail_frames; num {digit: word}; fix [[[heard,...], word]]; pins [[phrase, [[s, e], ...]]];
# time_fix [[token, near_s, s, e]]; highlights ["phrase", "is [one] word", "x@first", "x@last"]; warn [phrase];
# display [[phrase, [token, ...]]] ("" hides a merged token); word_fix {word: shown}. A shown token starting
# with "~" is literal: word_fix never changes it and the "~" is stripped.
import argparse, json, os, re, sys, difflib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.pipeline_config import load_config  # noqa: E402
from tools.script_beats import BEAT_ID  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument('words'); ap.add_argument('k', type=float)
ap.add_argument('--config', default='config/build_timeline.json'); ap.add_argument('--edl', default='edl.json')
ap.add_argument('--captions', default='transcript/caption_text.md'); ap.add_argument('--out', default='remotion/public/data/timeline.json')
args = ap.parse_args()
C = load_config(args.config, dict(tail_frames=60, num={}, fix=[], pins=[], time_fix=[], highlights=[], warn=[], display=[], word_fix={}))
words = json.load(open(args.words)); K = args.k; FPS = 30
TAIL_FRAMES = C['tail_frames']  # 2 s end card by default (reel: ≤ 2 s, counts toward 2:59)

# --- caption tokens, per section (transcript/caption_text.md: script with spoken variants applied, slips corrected) ---
txt = open(args.captions).read()
toks, beat_of = [], []
BEATS = re.findall(r'^### (\S+)', txt, flags=re.M)
if any(BEAT_ID.match(b) for b in BEATS):  # beat IDs (older projects use other headings); sections are in output order
    if not all(BEAT_ID.match(b) for b in BEATS): sys.exit(f'{args.captions}: mix of beat IDs and other headings: {BEATS}')
    repeated = sorted({b for b in BEATS if BEATS.count(b) > 1})
    if repeated: sys.exit(f'{args.captions}: repeated beat IDs: {repeated}')
NUMW = {}
for bi, sec in enumerate(re.split(r'^###.*$', txt, flags=re.M)[1:]):
    line = sec.replace('"', '').replace('“', '').replace('”', '').replace('...', ' ')
    for t in line.split():
        toks.append(t); beat_of.append(BEATS[bi])
NUM = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', **C['num']}  # Whisper digits -> script words
def norm(s):
    t = re.sub(r'[^a-z0-9]', '', s.lower())
    return NUM.get(t, t)

# --- heard words: merge / respell Whisper's mishearings so they line up with the script tokens ---
# The greeting's usual mishearings are built in; the episode's own respellings come from the config.
FIX = [(['namaskar'], 'namoshkar'), (['namashkar'], 'namoshkar'), (['namoskar'], 'namoshkar')] + [(list(a), b) for a, b in C['fix']]
H = [[s, e, norm(w)] for s, e, w in words if norm(w)]
for seq, rep in FIX:
    i = 0
    while i <= len(H) - len(seq):
        if [h[2] for h in H[i:i + len(seq)]] == seq:
            H[i:i + len(seq)] = [[H[i][0], H[i + len(seq) - 1][1], rep]]
        i += 1

A = [h[2] for h in H]
B = [norm(t) for t in toks]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
timed = [None] * len(toks); report = []
for op, a0, a1, b0, b1 in sm.get_opcodes():
    if op == 'equal':
        for j in range(b1 - b0): timed[b0 + j] = (H[a0 + j][0], H[a0 + j][1])
    elif op == 'replace':
        s, e = H[a0][0], H[a1 - 1][1]; n = b1 - b0
        for j in range(n): timed[b0 + j] = (s + (e - s) * j / n, s + (e - s) * (j + 1) / n)
        report.append(f"REPLACE heard {' '.join(A[a0:a1])!r} -> script {' '.join(toks[b0:b1])!r} @ {s:.2f}")
    elif op == 'delete':
        report.append(f"EXTRA heard {' '.join(A[a0:a1])!r} @ {H[a0][0]:.2f} (dropped from captions)")
    elif op == 'insert':
        report.append(f"MISSING script {' '.join(toks[b0:b1])!r} near {H[min(a0, len(H)-1)][0]:.2f}")
# runs of untimed (missing) script words: spread evenly over the gap between their neighbours
# (Whisper drops "kab khulega" in "Now kab khulega and when do you open"; the words sit in that gap)
j = 0
while j < len(toks):
    if timed[j] is not None: j += 1; continue
    k = j
    while k < len(toks) and timed[k] is None: k += 1
    p = timed[j - 1][1] if j > 0 else 0.0
    q = timed[k][0] if k < len(toks) else p + 0.3 * (k - j)
    if q - p < 0.06 * (k - j): q = p + 0.3 * (k - j)
    step = (q - p) / (k - j)
    for m in range(j, k): timed[m] = (p + step * (m - j), p + step * (m - j + 1))
    report.append(f"FILLED {' '.join(toks[j:k])!r} over {p:.2f}-{q:.2f}")
    j = k

# pinned word times (cut-voice seconds) from the 10 ms energy envelope, for words the aligners park early or drop
PINS = [(ph, [tuple(t) for t in times]) for ph, times in C['pins']]
for ph, times in PINS:
    pt = [norm(x) for x in ph.split()]
    for j in range(len(B) - len(pt) + 1):
        if B[j:j + len(pt)] == pt:
            for k in range(len(pt)): timed[j + k] = times[k]
            print(f'PIN {ph!r} @ {times[0][0]:.2f}')

# TIME_FIX: pin one script token nearest `near` seconds (list latest-first when a token repeats)
for tok, near, ns, ne in C['time_fix']:
    cand = [k for k in range(len(toks)) if toks[k] == tok]
    if not cand: sys.exit(f'time_fix: no caption token {tok!r}')
    timed[min(cand, key=lambda k: abs(timed[k][0] - near))] = (ns, ne)
    print(f'TIME_FIX {tok!r} near {near} -> {ns:.2f}')

# orange-block caption words: every occurrence of these exact words/phrases ('@first' / '@last' keep one;
# '[x]' marks the highlighted words inside a longer context phrase)
HL = C['highlights']
WARN = C['warn']
hl = [False] * len(toks)
for ph in HL:
    last = ph.endswith('@last'); first = ph.endswith('@first'); ph = ph.replace('@last', '').replace('@first', '')
    pt, mark, on = [], [], False
    for x in ph.replace('[', ' [ ').replace(']', ' ] ').split():
        if x == '[': on = True
        elif x == ']': on = False
        else: pt.append(norm(x)); mark.append(on)
    if not any(mark): mark = [True] * len(pt)
    hits = [j for j in range(len(B) - len(pt) + 1) if B[j:j + len(pt)] == pt]
    for j in (hits[-1:] if last else hits[:1] if first else hits):
        for k in range(len(pt)):
            if mark[k]: hl[j + k] = True
    print(f'HL {ph!r}: {len(hits)}{" (last only)" if last else ""}')

# display rules: script phrase -> caption tokens (numerals, rupee sign); '' hides a merged token (still found by at())
DISP = C['display']
disp = [None] * len(toks)
for ph, rep in DISP:
    pt = [norm(x) for x in ph.split()]; found = 0
    for j in range(len(B) - len(pt) + 1):
        if B[j:j + len(pt)] == pt and all(disp[j + k] is None for k in range(len(pt))):
            for k in range(len(pt)): disp[j + k] = rep[k]
            found += 1
    print(f'DISP {ph!r}: {found}')
warn = [False] * len(toks)
for ph in WARN:
    pt = [norm(x) for x in ph.split()]
    for j in range(len(B) - len(pt) + 1):
        if B[j:j + len(pt)] == pt:
            for k in range(len(pt)): warn[j + k] = True; hl[j + k] = False
out_words = []
for j, t in enumerate(toks):
    s, e = timed[j]
    p = t[-1] if t[-1] in '.?!:,' else ''
    w = t if t.endswith('?') else t.rstrip('.,:')
    if disp[j] is not None: w = disp[j].rstrip('.') if disp[j] != '' else ''
    if w.startswith('~'): w = w[1:]  # literal: never word-fixed
    elif C['word_fix']:
        core = w.rstrip('?')
        w = C['word_fix'].get(core.lower(), core) + w[len(core):]
    out_words.append({'raw': t, 'w': w, 's': round(s * FPS), 'e': max(round(e * FPS), round(s * FPS) + 1), 'p': p, 'hl': hl[j], 'warn': warn[j], 'b': beat_of[j]})
# a shown token followed by hidden ones takes their end time, punctuation and question mark
for j in range(len(out_words) - 1, 0, -1):
    if out_words[j]['w'] == '':
        k = j - 1
        while out_words[k]['w'] == '': k -= 1
        out_words[k]['e'] = max(out_words[k]['e'], out_words[j]['e'])
        if out_words[j]['p']: out_words[k]['p'] = out_words[j]['p']
        out_words[j]['p'] = ''

segs = json.load(open(args.edl))['segments']; cum = 0; S = []
for a, b in segs:
    f0, f1 = round(a * FPS), round(b * FPS)
    S.append({'srcIn': f0, 'srcOut': f1, 'from': round(cum / K), 'to': round((cum + f1 - f0) / K)}); cum += f1 - f0
total = round(cum / K) + TAIL_FRAMES
# beats in output order, as word index ranges (indices survive the later retime steps; frames would not)
beats = []
for j, w in enumerate(out_words):
    if beats and beats[-1]['id'] == w['b']: beats[-1]['words'][1] = j
    else: beats.append({'id': w['b'], 'words': [j, j]})
json.dump({'fps': FPS, 'k': K, 'total': total, 'segments': S, 'words': out_words, 'beats': beats}, open(args.out, 'w'))
print(f"words={len(out_words)} segments={len(S)} total_frames={total} ({total/FPS:.2f}s)")
print('\n'.join(report))
