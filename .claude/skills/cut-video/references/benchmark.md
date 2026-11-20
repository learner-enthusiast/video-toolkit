# Benchmark reference

Moved from `SKILL.md` (token diet, 2026-11-20). The self-check targets in `SKILL.md` → Step 3 are derived from this.

**Style target** (calibrated from `AI mogging my dad.mp4`):
- ~1 cut every 1.3–1.5 seconds (median cut duration ~1.1s)
- ~40–60% total runtime reduction from raw
- Cuts happen mid-sentence, not just between sentences
- Word-by-word tightening — fillers, hedges, and weak openers get sliced

`AI mogging my dad.mp4` (2026-05-03, CapCut project `0501`):
- 335 cuts in 460s = 1 cut / 1.37s
- Median 1.13s, mean 1.37s
- 41% of cuts < 1s, 12% < 0.5s
- Only 3 cuts > 5s
- Raw source compressed ~60%

Use this as ground-truth for "aggressive" mode tuning.
