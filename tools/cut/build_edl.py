# Energy EDL for a teleprompter read (pipeline/take-selection.md, one-take mode + explicit retake cuts).
# usage: vt-python tools/cut/build_edl.py config/build_edl.json  -> writes the EDL named by "out", prints durations
# `end` defaults to `last_out` (never the source length). A two-part recording is one config per part
# (its own start/end range, cuts and "out" name); a cut outside that range is an error.
import json, os, sys, numpy as np, soundfile as sf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.pipeline_config import load_config  # noqa: E402

KEYS = dict(end=None, thresh_db=-32, gap=0.25, long_gap=0.5, tail=0.10, long_before=[], first_in=None, last_out=None,
            hold_inserts=[], insert_after=[])
cfg = load_config(sys.argv[1], KEYS, required=("wav", "out", "start", "cuts"))
if cfg["end"] is None:
    if cfg["last_out"] is None: sys.exit("config needs `end` or `last_out`")
    cfg["end"] = cfg["last_out"]
for a, b in cfg["cuts"]:
    if b <= cfg["start"] or a >= cfg["end"]: sys.exit(f"cut [{a}, {b}] is outside this config's range")
x, sr = sf.read(cfg["wav"]); x = x if x.ndim == 1 else x.mean(1)
HOP = 0.01; w = int(sr * HOP); n = len(x) // w
rms = 20 * np.log10(np.sqrt((x[: n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)
sp = rms > cfg.get("thresh_db", -32)
# smooth +-2 frames (dilate) so soft consonants count as speech
k = 2
spd = sp.copy()
for s in range(1, k + 1):
    spd[s:] |= sp[:-s]; spd[:-s] |= sp[s:]
# hard limits and explicit removals
t = np.arange(n) * HOP
keep = (t >= cfg["start"]) & (t < cfg["end"])
for a, b in cfg["cuts"]:
    keep &= ~((t >= a) & (t < b))
spd &= keep
# speech runs
runs = []; i = 0
while i < n:
    if spd[i]:
        j = i
        while j < n and spd[j]: j += 1
        runs.append([i * HOP, j * HOP]); i = j
    else: i += 1
# drop tiny isolated blips (<60 ms) far from neighbours (clicks/breaths)
runs = [r for idx, r in enumerate(runs) if (r[1] - r[0]) >= 0.06 or
        (idx > 0 and r[0] - runs[idx - 1][1] < 0.3) or (idx + 1 < len(runs) and runs[idx + 1][0] - r[1] < 0.3)]
G = cfg.get("gap", 0.25); LONG = cfg.get("long_gap", 0.5); TAIL = cfg.get("tail", 0.10)
longs = cfg.get("long_before", [])
segs = []
cur = [max(cfg["start"], runs[0][0] - 0.12), None]
for a, b in zip(runs, runs[1:]):
    gap = b[0] - a[1]
    tgt = G  # long_before entries: t (uses long_gap) or [t, gap]
    for L in longs:
        t_, g_, tol = (L[0], L[1], 0.3) if isinstance(L, list) else (L, LONG, 0.6)
        if abs(b[0] - t_) < tol: tgt = g_
    # was anything removed between them? (explicit cut) -> always split
    removed = any(a[1] - 0.05 <= c0 and c1 <= b[0] + 0.05 for c0, c1 in cfg["cuts"])
    if gap <= tgt and not removed:
        continue
    inside = [c for c in cfg["cuts"] if a[1] - 0.05 <= c[0] and c[1] <= b[0] + 0.05]
    if inside:  # silence available on each side of the removed span
        avail_t = min(c[0] for c in inside) - a[1]
        avail_h = b[0] - max(c[1] for c in inside)
        tail = min(TAIL, avail_t)
        head = min(tgt - tail, max(avail_h - 0.01, 0.0))
        tail = min(avail_t - 0.01, tgt - head)
    else:
        tail = min(TAIL, gap / 2)
        head = max(tgt - tail, 0.06) if gap > tgt else gap - tail
        head = min(head, gap - tail)
    cur[1] = a[1] + tail
    segs.append(cur)
    cur = [b[0] - head, None]
cur[1] = min(cfg["end"], runs[-1][1] + 0.15)
segs.append(cur)
# snap to 30 fps frame boundaries, at the quietest boundary within +-2 frames
F = 1 / 30
def q(tt):
    c = [round(tt / F) + d for d in (-1, 0, 1)]
    return min(c, key=lambda f: rms[min(n - 1, int(f * F / HOP))]) * F
out = []
for a, b in segs:
    a2, b2 = q(a), q(b)
    if b2 - a2 >= F: out.append([round(a2, 4), round(b2, 4)])
# merge segments that touch
m = [out[0]]
for a, b in out[1:]:
    if a <= m[-1][1] + 1e-6: m[-1][1] = b
    else: m.append([a, b])
tot = sum(b - a for a, b in m)
edges = []
for a, b in m:
    for e in (a, b):
        i0 = int(e / HOP); edges.append(rms[max(0, i0 - 2): i0 + 2].max())
bad = [(round(m[i // 2][i % 2], 2), round(float(edges[i]), 1)) for i in range(len(edges)) if edges[i] > -35]
if cfg.get("first_in") is not None: m[0][0] = cfg["first_in"]; tot = sum(b - a for a, b in m)
if cfg.get("last_out") is not None: m[-1][1] = cfg["last_out"]; tot = sum(b - a for a, b in m)  # hold a closing gesture (wave) past the last word
# hold_inserts: [[split_t, sil_a, sil_b]] -> split the segment holding split_t and insert source silence [sil_a, sil_b]
# (a beat pause before a word spoken with no gap before it)
for st, sa, sb in cfg.get("hold_inserts", []):
    for i, (a, b) in enumerate(m):
        if a < st < b:
            m[i:i + 1] = [[a, st], [sa, sb], [st, b]]; break
    else: sys.exit(f"hold_insert {st} not inside a segment")
# insert_after: [[after_t, a, b]] -> move source range [a, b] to right after the segment ending nearest after_t (|d| < 0.4 s)
# (hook-first reorder: a greeting recorded first is played after the hook line)
for at, sa, sb in cfg.get("insert_after", []):
    i = min(range(len(m)), key=lambda k: abs(m[k][1] - at))
    if abs(m[i][1] - at) > 0.4: sys.exit(f"insert_after {at}: no segment ends near it")
    m.insert(i + 1, [round(round(sa * 30) / 30, 4), round(round(sb * 30) / 30, 4)])
tot = sum(b - a for a, b in m)
assert all(b > a for a, b in m), "segment with end <= start"
print("after hold_inserts:", f"segments={len(m)} cut_duration={tot:.2f}s")
json.dump({"segments": m, "fps": 30}, open(cfg["out"], "w"))
print(f"segments={len(m)} cut_duration={tot:.2f}s ({int(tot//60)}:{tot%60:05.2f})")
for kk in (1.0, 1.05, 1.10, 1.20, 1.30, 1.40, 1.50, 1.55, 1.60, 1.65, 1.70):
    print(f"  at {kk:.2f}x -> {tot/kk:.2f}s")
print("loud edges (>-35 dB):", bad)
