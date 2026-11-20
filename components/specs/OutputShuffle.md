---
code: components/code/OutputShuffle/OutputShuffle.tsx
preview: components/code/OutputShuffle/preview.png
props: "OutputShuffle {at,out,shuffleAt,mapAt,rewindAt,fixAt,snapAt,matchAt,rows,order,files,labels,item} · ReportGlyph"
variants: "shuffled output, wrong mapping by line number (⚠), rewind, custom_id tags, right mapping (✓)"
last_used: system-design-of-ai/10-batch-inference
---
# OutputShuffle

**Purpose:** the batch-output ordering bug. An input file (line 1 Ramesh, line 2 Priya, line 3 Arjun) and an output file that comes back shuffled. Mapping by line number sends the wrong report to the wrong phone (data leak). Re-mapping by `custom_id` snaps each report onto the right phone with an orange ✓.

**Props:** `x`, `y`, `w`, `h`, `rows` ([{name, id}]), `order` (output permutation, e.g. [1, 2, 0]), `shuffleAt`, `mapByLineAt` (wrong arrows), `leakAt` (DATA LEAK flash: dark frame + Stamp, ~20 frames), `fixAt` (custom_id tags appear on every line), `snapAt` (reports re-route to the right phones), `at`, `out`.

**Look**
- Two mono file cards side by side (`input.jsonl`, `output.jsonl`), line numbers in a grey gutter, names in Inter 800.
- Three generic phones on the right (outline, initials chip; no faces).
- Wrong mapping: dim grey arrows + orange ⚠ on the wrong phone; right mapping: orange arrows + orange ✓.
- Leak flash: #0D0D0D frame, white text, Stamp "DATA LEAK" with an orange ⚠ (dark style, no shadow).

**Motion**
- Shuffle: output rows swap places with springs (stagger 4 frames).
- Arrows draw ease-in-out ~10 frames; the wrong report slides into the wrong phone, the phone shakes once.
- Fix: a quick rewind (rows return, ~8 frames), mono `custom_id: user_…` tags pop on every line, arrows redraw to the right phones.
- Exit with a fade on `out`.

**Sound:** `whoosh` on the shuffle, `soft-pop` per arrow, `sub-boom` on the DATA LEAK flash, `pop` per ✓.

**Gotchas**
- Never red: the wrong state is grey + orange ⚠.
- Names are made up; keep them generic Indian first names, no surnames.

## Code

Saved: `components/code/OutputShuffle/OutputShuffle.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: OutputShuffle {at,out,shuffleAt,mapAt,rewindAt,fixAt,snapAt,matchAt,rows,order,files,labels,item} · ReportGlyph.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
