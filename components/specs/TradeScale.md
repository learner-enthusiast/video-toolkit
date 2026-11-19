---
code: components/code/TradeScale/TradeScale.tsx
preview: components/code/TradeScale/preview.png
props: "x, y, at, angle, left, right, leftAt, rightAt, half, label"
variants: "none"
last_used: system-design-of-ai/05-model-routing
---
# TradeScale

**Purpose:** a trade-off in one picture: one side is heavier, the other costs something (here: Speed vs Memory + Durability).

**Props:** `w`, `h`, `scaleAt`, `speedAt`, `costAt`, `tipAt`, `out`.

**Look**
- Balance scale in the line style: base, post, beam with a pivot dot, strings and two bowl-shaped pans.
- Left card is orange with a bolt badge and white text; right card is white with near-black text. Cards sit on the pans.
- "trade" in serif italic orange above the pivot.

**Motion**
- Post, beam, strings and pans draw themselves, staggered.
- Cards drop onto the pans with a pop.
- At `tipAt` the beam rotates 10° by spring so the heavy (left) side goes down; pan positions are recomputed from the beam ends so the pans stay vertical.

**Gotchas**
- Beam half-length 290 keeps the cards 20 px inside a 876 px box.
- Rotation is applied to the beam only; pans and strings use computed endpoints.
- Spring overshoot is expected; do not clamp it.

## Code

Saved: `components/code/TradeScale/TradeScale.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: x, y, at, angle, left, right, leftAt, rightAt, half, label.
- Generic balance scale: the two pans take any node, the tilt `angle` is animated by the caller. The older spec's w/h/scaleAt/speedAt/costAt/tipAt describe one video's use of it.
