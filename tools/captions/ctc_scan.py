"""Diff a windowed CTC decode of the cut voice against script.md; print CTC runs not in the script (repeats/retakes).
usage: vt-python tools/captions/ctc_scan.py ctc_full.txt script.md"""
import re, sys, difflib
lines = open(sys.argv[1]).read().strip().split('\n')
words = []  # (t, w) deduped across 1 s overlaps
last_t = -1
for ln in lines:
    for tok in ln.split()[1:]:
        w, t = tok.rsplit('@', 1); t = float(t)
        if t > last_t + 0.05: words.append((t, w)); last_t = t
paras = re.findall(r'^### \d+\..*?\n\n(.+?)\n', open(sys.argv[2]).read(), flags=re.M)
if not paras: paras = [l for l in open(sys.argv[2]).read().split('\n') if l.strip()]  # one spoken line per row
S = [re.sub(r"[^a-z]", '', w.lower()) for p in paras for w in p.split()]
S = [w for w in S if w]
C = [re.sub(r"[^a-z]", '', w) for _, w in words]
sm = difflib.SequenceMatcher(None, S, C, autojunk=False)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'insert' and j2 - j1 >= 2:
        print(f"INSERT @{words[j1][0]:.2f}-{words[j2-1][0]:.2f}s: {' '.join(C[j1:j2])}")
    elif op == 'replace' and (j2 - j1) - (i2 - i1) >= 2:
        print(f"REPLACE+ @{words[j1][0]:.2f}s: script '{' '.join(S[i1:i2])}' <- ctc '{' '.join(C[j1:j2])}'")
print('ratio', round(sm.ratio(), 3))
