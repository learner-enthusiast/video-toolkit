---
code: components/code/IncidentCard/IncidentCard.tsx
preview: components/code/IncidentCard/preview.png
props: "w, tag, rows [{text,at}], stat {value,unit,at,from?,to?}, source {text,at,logo?}, children, at, out"
variants: "static stat or count-up (from/to), optional source logo, child slot"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# IncidentCard

**Purpose:** a real-world incident shown as evidence: a brand grid card tagged "real incident", a few short fact rows, one big stat, and a small source line, so the viewer sees it's a documented case without a screenshot.

**Props:** `tag` (default "real incident"), `rows` (`{text, at}`, short facts joined by "·"), `stat` (`{value, unit, at}`, e.g. "12,000+" "tokens each"), `source` (`{text, at, logo?}`), `children` (slot for a DefinitionChip under the stat), `at`, `out`.

**Look**
- White card with the brand border, radius and shadow, on the grid. Tag pill top-left (ink fill, orange dot).
- Rows in Inter 700 ~40 px, each prefixed with a small orange bar. Stat in Inter 900 ~150 px orange with the unit in Instrument Serif Italic beside or under it.
- Source line at the bottom: Inter 500 ~26 px dim grey, optional small logo (e.g. GitHub mark) in its official colours.

**Motion**
- Card springs in on the first word of the beat; rows reveal on their words (stagger 4–6 frames when they share one); the stat counts up (ease-out) and lands with a 4% bump; source line fades in.

**Sound:** `pop` on the card, `soft-pop` per row, `stamp-thud` (low) when the stat lands.

**Gotchas**
- Say "one report" in the source line or tag if it's a single case; never imply it is every app.
- Keep rows ≤ 34 chars so they fit the 972 px card at 40 px.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/IncidentCard/IncidentCard.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`; glyphs (server, user, handset, chip, warning) from `glyphs.tsx`.

- Code props: w, tag, rows [{text,at}], stat {value,unit,at,from?,to?}, source {text,at,logo?}, children, at, out.
- First built and rendered in `system-design-of-ai/06-cancellation`.
