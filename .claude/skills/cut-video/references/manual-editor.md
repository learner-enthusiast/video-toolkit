# Step 3.5 — Manual timeline editor (optional)

Load only when the user asks to review or adjust the cut by hand. Moved verbatim from `SKILL.md` (token diet, 2026-11-20).

(Demoted from always-on 2026-07-02: Louise found the editor fiddly in practice and prefers the pipeline to just cut tighter automatically — the intra-take pause trimming in Step 2.5 came out of that. Generate the editor only if she asks to review/adjust by hand.)

A timeline editor so she can trim silences and drop anything she doesn't want, before (or after) the render:

```bash
# keeps.json must be [start, end, "transcript text"] triplets in the working dir;
# needs proxy.mp4 (and ideally audio.wav) in the same dir. Generates wave.png once.
vt-python .claude/skills/cut-video/make_review.py projects/<name>/work/cut-video
xdg-open projects/<name>/work/cut-video/review.html
```

What the page gives her (self-contained HTML next to `proxy.mp4`, no server needed — waveform peaks and silence suggestions are embedded in the file, so it works on `file://`):
- **Canvas waveform timeline of the FULL source**, crisp at every zoom. **Pinch or ctrl/⌘+wheel zooms centered on the cursor** (continuous, fit → 400px/s); mouse wheel pans; +/−/Fit buttons too. Click to scrub; playhead synced to the video.
- **Drag ACROSS the waveform to delete that range** — the primary silence-removal gesture: see a flat stretch, swipe it, gone. Works across block boundaries (trims/splits/removes whatever it covers).
- **Amber hatched bands = auto-suggested silences inside keep blocks** (peak-based, adaptive threshold — computed by the generator and embedded). Click a band to cut it (leaves 0.1s of pause at each side), or **"✂ Cut all"** with a min-duration slider to sweep every suggestion at once. On noisy mics the suggestions degrade — they're visual candidates, she judges.
- **Drag a block's edges** to trim; the video seeks live while dragging so she hears the cut point. Selected edge nudges ±0.05s (buttons or ←/→, shift = 0.25s).
- **Split at playhead** (`S`), **drop/restore** a block (`D`/⌫ or click its card), **double-click a gap** to resurrect cut footage, **undo** (`Z`, 60 levels).
- Card list below with per-segment ▶ and transcript text; **"Preview final cut"** plays kept blocks back-to-back, skipping cuts — the render, live, without rendering.
- **"Copy decisions for Claude"** copies `{"keeps": [[a,b], ...]}` — the full edited keep list in source-proxy seconds.

Applying her decisions: the pasted `keeps` array REPLACES the old keep list — carry transcript text over by time-overlap with the previous `keeps.json` (blocks she created from gaps have no text; label them "(restored)"), rebuild `filter.txt`, re-render. The proxy is already there, so a revision costs seconds.

Boundary hygiene: her hand-dragged edges are intentional — do NOT re-snap them to MFA/ASR word boundaries. Only warn if an edge lands mid-word per the ground-truth words (say which word and offer the nearest clean boundary).
