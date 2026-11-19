---
code: components/code/MathStrip/MathStrip.tsx
preview: components/code/MathStrip/preview.png
props: "terms [{text, at, op?}], size, style; also exports inr()"
variants: "none"
last_used: system-design-of-ai/05-model-routing
---
# MathStrip

**Purpose:** an equation that builds term by term as it is spoken, with the result as the punch.

**Props:** `terms` ([{text, at, op?}]), `result` ({text, at}), `rect`, `at`, `out`, `dark`.

**Look**
- Terms as mono chips on one or two lines (white on dark, 2 px border), operators in dim text between them.
- Result on its own line, Inter 900, large orange, tabular; ₹ in Indian grouping.

**Motion**
- Each term pops on its spoken number (soft tick). The result counts up ease-out over ~20 frames and lands with a small scale bump.

**Gotchas**
- The arithmetic on screen must be exact and match what is said (₹20 × 20 / min × 60 min = ₹24,000).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/MathStrip/MathStrip.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: terms [{text, at, op?}], size, style; also exports inr().
- No `result` prop: pass the result as the last term with op '='.
