# Writes the build_edl config from per-video settings: aligns CTC words to the script (difflib), snaps every
# sentence/beat start to its energy onset, sets the pauses and moves a recording-order greeting after the hook.
# usage (from work/): vt-python tools/cut/build_cfg.py --config config/build_cfg.json [--out config/build_edl.json]
import argparse, json, os, re, difflib, sys, numpy as np, soundfile as sf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.pipeline_config import load_config  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--config", default="config/build_cfg.json"); ap.add_argument("--out", default="config/build_edl.json")
args = ap.parse_args()
C = load_config(args.config, dict(
    beats="transcript/script_beats.json", plain="transcript/script_plain.md", ctc="transcript/ctc_src.txt", wav="audio/clean.wav",
    edl_out="edl.json", skip_beats=[], cuts=[], hold_after=[], pins=[], extra_long_before=[], insert_after=[],
    thresh_db=-29, onset_search=[0.45, 0.06], gap=0.2, long_gap=0.3, tail=0.1, sentence_gap=0.25, beat_gap=0.3, hold_gap=0.5,
    end_pad=1.25, last_hold=1.2,
), required=("first", "bye_end"))

beats = json.load(open(C["beats"]))
plain = open(C["plain"]).read().strip().split("\n")   # spoken form (numbers spelled), one line per beat
beats = [[b[0], p] for b, p in zip(beats, plain) if b[0] not in C["skip_beats"]]   # e.g. a greeting inserted separately
norm = lambda w: re.sub(r"[^a-z]", "", w.lower())

S = []
for bid, text in beats:
    sents = re.split(r"(?<=[.?!])\s+", text)
    for si, sent in enumerate(sents):
        for wi, w in enumerate(sent.split()):
            S.append({"w": norm(w), "beat": bid, "beat_start": si == 0 and wi == 0, "sent_start": wi == 0,
                      "raw": w, "prev_sent": sents[si - 1] if si else None})

FIRST = C["first"]          # first kept source time (the hook's energy onset)
CUTS = C["cuts"]            # explicit retake / stutter removals
# Word times from the windowed CTC decode (Whisper can drift seconds off on a long read)
W, last = [], -1
for ln in open(C["ctc"]).read().strip().split("\n"):
    for tok in ln.split()[1:]:
        w, t = tok.rsplit("@", 1); t = float(t)
        if t > last + 0.05 and t >= FIRST and not any(c0 <= t < c1 for c0, c1 in CUTS): W.append({"word": w, "start": t})
        last = max(last, t)
toks = [norm(w["word"]) for w in W]

x, sr = sf.read(C["wav"]); x = x if x.ndim == 1 else x.mean(1)
hop = int(sr * 0.01); n = len(x) // hop
rms = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
sp = rms > C["thresh_db"]; spd = sp.copy()
for s in (1, 2): spd[s:] |= sp[:-s]; spd[:-s] |= sp[s:]
starts = np.flatnonzero(spd[1:] & ~spd[:-1]) * 0.01 + 0.01
def onset(t):
    c = starts[(starts > t - C["onset_search"][0]) & (starts < t + C["onset_search"][1])]   # CTC emits ~0.05-0.15 s after the onset
    return float(c.max()) if len(c) else None

sm = difflib.SequenceMatcher(a=[s["w"] for s in S], b=toks, autojunk=False)
idx = {}
for a, b, size in sm.get_matching_blocks():
    for k in range(size): idx[a + k] = b + k
HOLD_AFTER = tuple(C["hold_after"])   # sentences followed by a deliberate longer beat
longs, missing, holds = [], [], []
for i, s in enumerate(S):
    if i == 0 or not s["sent_start"]: continue
    if i not in idx: missing.append(f'{s["beat"]}:{s["raw"]}'); continue
    t = onset(W[idx[i]]["start"])
    if t is None: missing.append(f'{s["beat"]}:{s["raw"]}(no onset)'); continue
    prev = s["prev_sent"] or [b for b in beats if b[0] == S[i - 1]["beat"]][0][1]
    hold = any(prev.strip().endswith(h) for h in HOLD_AFTER)
    gap = C["hold_gap"] if hold else (C["beat_gap"] if s["beat_start"] else C["sentence_gap"])
    if hold: holds.append(f'{s["beat"]}:{s["raw"]}@{t:.2f}')
    longs.append([round(t, 2), gap])
# Beat starts CTC misspelled (difflib missed them): CTC time -> energy onset, beat gap
for bid, tc in C["pins"]:
    t = onset(tc)
    if t is None: missing.append(f"{bid}:pin {tc}(no onset)")
    else: longs.append([round(t, 2), C["beat_gap"]])
longs.extend(C["extra_long_before"])   # [t, gap]: keep a recorded beat
BYE = C["bye_end"]   # energy end of the last word, pinned from the 10 ms envelope
cfg = {"wav": C["wav"], "out": C["edl_out"], "start": FIRST, "end": round(BYE + C["end_pad"], 2), "thresh_db": C["thresh_db"],
       "gap": C["gap"], "long_gap": C["long_gap"], "tail": C["tail"], "cuts": CUTS, "long_before": longs,
       "insert_after": C["insert_after"], "first_in": FIRST, "last_out": round(BYE + C["last_hold"], 2)}
json.dump(cfg, open(args.out, "w"))
print("first word", W[0]["word"], W[0]["start"], "| last word end", BYE, "| cuts", CUTS)
print(len(longs), "sentence/beat starts snapped; unmatched:", missing or "none")
print("holds before:", holds)
print("script tokens matched %d/%d" % (len(idx), len(S)))
