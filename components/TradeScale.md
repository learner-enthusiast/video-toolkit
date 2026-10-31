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
