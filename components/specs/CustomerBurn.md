---
code: components/code/CustomerBurn/CustomerBurn.tsx
preview: components/code/CustomerBurn/preview.png
props: "tagAt, gridAt, leaveAt, countAt, countTo, fewAt, unit, unitNote, gridLabel, leaveTo, leaveNote, counterNote, fewLabel, prefix"
variants: "none"
last_used: system-design-of-ai/07-provider-failover
---
# CustomerBurn

**Purpose:** turn an outage into rupees: cost to win one customer × customers lost = money burned.

**Props:** `at`, `unit` (`{label, at}`, e.g. ₹2,000), `grid` (`{n, cols, at}`), `leaveAt`, `leaveShare` (0–1), `counter` (`{to, at, label}`), `out`.

**Look**
- Dark style (`#0D0D0D`, white text, orange accent). One generic customer glyph with an orange price tag.
- The grid multiplies the glyph (draw a representative grid, e.g. 10×10, with a "× 5,000" label; never 5,000 tiny dots).
- Leaving customers dim to grey and slide right toward a generic "Other loan app" icon.
- Counter in Inter Black, orange, tabular numerals, Indian grouping (₹50,00,000).

**Motion**
- Tag pops, grid fans out from the single glyph (staggered spring), the leaving share slides out on `leaveAt`, the counter counts with ease-in-out and lands with a bump.

**Gotchas**
- Label example numbers as "Illustration" (Tag) for the whole beat.
- No logos for the competitor; it's generic.

## Code

`components/code/CustomerBurn/CustomerBurn.tsx` (saved from `system-design-of-ai/07-provider-failover`). Building blocks: `../ProviderNode/ProviderNode` (card, packet, line), `XMark`/`TickMark`/`WarnMark` from `../glyphs`, `tween`/`shake` from `../anim`.
