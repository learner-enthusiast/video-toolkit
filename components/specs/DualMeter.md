---
code: components/code/DualMeter/DualMeter.tsx
preview: components/code/DualMeter/preview.png
props: "req, reqMax, tok, reqText, tokText, reqTitle, tokTitle, counterO, counterDx, dark, geometry; BudgetBar: x, y, w, h, segs [{frac,kind,label?,lock?}], dark, radius"
variants: "pair meters, dark, budget bar (BudgetBar export)"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# DualMeter

**Purpose:** the running motif for "count vs cost": a grey Request counter next to an orange Token (cost) meter. The same object returns through a video: rising together, splitting apart, then the counter fades and the token meter becomes a budget bar.

**Props:** `events` ([{at, tokens, label}]: each adds +1 request and `tokens` to the meter), `scale` (tokens for a full bar), `mode` (`pair` | `frozen` | `budget`), `counterOutAt` (fade the counter), `budget` ({total, label, holds: [{at, amount}], refunds: [{at, amount}]}), `rect` (card-local), `at`, `out`.

**Look**
- Two vertical bars with a shared baseline, same width, 2 px border, brand radius. Left: "Requests", dim grey fill, numeral above (tabular). Right: "Tokens" (or "Cost"), orange fill, numeral above.
- Identical geometry in every scene: same x, width, labels and type sizes, so it reads as one object.
- `budget`: the token bar alone, wider, labelled "50,000 tokens / min"; held chunks are orange hatch with a lock icon, spent is solid orange, free is white.

**Motion**
- Each event: the counter steps up one notch (soft tick SFX) and the token fill springs by its real size. Equal-cost events move both the same amount.
- Overflow: when the fill passes the bar's top it keeps going past the card edge (clip at the card, not the bar), with the numeral counting up ease-out.
- `frozen`: both hold; "+1 / +1" under the counter, "10 vs 100,000" under the meter.
- Counter → out: fades and slides left 8 frames; the token bar springs to the centre and widens into the budget bar (one morph, never a cut).

**Gotchas**
- The token scale must be honest inside one scene (10 vs 100,000 = a sliver vs overflow); never rescale mid-scene.
- Numerals in Indian/thousands grouping from one helper.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/DualMeter/DualMeter.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: req, reqMax, tok, reqText, tokText, reqTitle, tokTitle, counterO, counterDx, dark, geometry; BudgetBar: x, y, w, h, segs [{frac,kind,label?,lock?}], dark, radius.
- Code takes fractions + printed text (not `events`); the caller computes them from word frames. Budget mode is the separate BudgetBar export.
