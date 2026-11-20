---
code: components/code/ExamSheet/ExamSheet.tsx
preview: components/code/ExamSheet/preview.png
props: "ExamSheet: w, h, lines, fillFrom, bellAt, penStopAt, title, blank, stopLabel, at, out · RoughSheet: w, h, drawFrom, drawTo, title, at, out"
variants: "answer sheet (bell + pen stop) · blank · RoughSheet"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# ExamSheet

**Purpose:** the exam analogy for a hard output cap. The bell is `max_tokens`; the pen stops mid-line however good the answer was. A `rough` variant shows thinking tokens as rough work that used up the time while the answer sheet stayed blank.

**Props:** `w`, `h`, `lines` (number of ruled answer lines), `fillFrom` (frame the pen starts writing), `bellAt` (bell rings), `penStopAt` (pen lifts; the current line stops mid-way), `variant` ('answer' | 'rough'), `roughAt` (rough page scribbles start), `blankAt` (blank answer sheet pops with a dim ⚠), `labels` ({answer, rough}), `at`, `out`.

**Look**
- Sheet: white paper card, 2 px border, brand radius, ruled lines in `#DCD8D0`, a header strip "ANSWER SHEET" (Inter 800, dim). Handwriting = rounded near-black strokes (SVG paths, no font). Bell: a line-icon hand bell in the top-right, orange when ringing, with 3 small orange ring arcs. Pen: simple line-icon pen at the writing point; lifts and tilts on `penStopAt`. Rough variant: a second page titled "ROUGH WORK" full of grey scribbles and crossed-out sums; the answer sheet next to it stays empty with a dim ⚠ "blank".

**Motion**
- Lines draw left→right one after another (ease-in-out per line, 4–6-frame gaps). Bell swings ±14° with a decaying spring. Pen lifts 30 px with a spring. Rough scribbles draw fast (stroke-dashoffset), then the blank sheet pops.

**Sound:** `bell` (kit v2) on `bellAt`, `pen-scratch` while writing (one per 2 lines), `soft-pop` on the blank sheet.

**Gotchas**
- No real exam board or school branding. Keep handwriting abstract (no readable fake text).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/ExamSheet/ExamSheet.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: ExamSheet: w, h, lines, fillFrom, bellAt, penStopAt, title, blank, stopLabel, at, out · RoughSheet: w, h, drawFrom, drawTo, title, at, out.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
