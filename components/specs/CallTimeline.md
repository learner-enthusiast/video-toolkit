---
code: components/code/CallTimeline/CallTimeline.tsx
preview: components/code/CallTimeline/preview.png
props: "w, seconds, leaveAt, run {start,leave,end}, stopAt, tokRate, money {perTok,prefix}, tag, foot, verdict {at,text,tone}, rewindFrom, labels, at, out"
variants: "before (stopAt = seconds) / after fix (stopAt ≈ leaveAt, rewindFrom), with/without money"
last_used: system-design-of-ai/06-cancellation
---
# CallTimeline

**Purpose:** a request's life on one time axis: what the user read versus what the server paid for. A 0 → N s bar with a moving playhead, a "user left" pin, a token counter and a money counter. It must replay with a different outcome (before vs after a fix) using the same geometry.

**Props:** `seconds` (axis length, e.g. 40), `leaveAt` (seconds, e.g. 2), `run` (`{start, leave, end}` frames: playhead 0 → leave → seconds), `tokens` (`{read, paid}` final values), `stopAt` (seconds where generation stops; = `seconds` before the fix, ≈ `leaveAt` after), `money` (`{perToken, currency, label}` or null), `tag` (e.g. "example"), `foot` (footnote, e.g. "prices vary by model"), `verdict` (`{at, text}`), `at`, `out`.

**Look**
- A white panel on the grid card. Axis: thick track with 0 / leaveAt / seconds tick labels (JetBrains Mono). Filled part of the bar: orange while the model is generating, grey hatched where nobody is reading.
- Pin above the axis at `leaveAt`: a small flag "user left".
- Two counters side by side under the axis: "tokens" (Inter 900, tabular) and the money counter (same size, "≈ ₹" prefix), each with a small caption. A grey "example" tag top-right; the footnote small and dim at the bottom.
- Verdict line: dim grey with an orange warning mark for the bad run ("read: 100 · paid: 2,000"), orange for the good run.

**Motion**
- Playhead eases from 0 to `leaveAt`, pauses on the pin (it drops in with a spring), then runs on (time-skipping ease-in) to `stopAt`. Counters follow the playhead, not a separate curve.
- On a replay the bar resets with a short rewind sweep (ease-in-out, ~10 frames) before running again; when `stopAt` ≈ `leaveAt` the counters freeze with a 4% bump.

**Sound:** `tick` steps while counting (sparse, every ~6 frames), `stamp-thud` on the verdict.

**Gotchas**
- Every number is an example: keep the tag visible the whole time, and money values must match the project's facts file.
- Counters use tabular figures and a fixed width so the layout doesn't jitter.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/CallTimeline/CallTimeline.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`; glyphs (server, user, handset, chip, warning) from `glyphs.tsx`.

- Code props: w, seconds, leaveAt, run {start,leave,end}, stopAt, tokRate, money {perTok,prefix}, tag, foot, verdict {at,text,tone}, rewindFrom, labels, at, out.
- First built and rendered in `system-design-of-ai/06-cancellation`.
