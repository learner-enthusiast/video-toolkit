# HoldSettle

**Purpose:** "hold first, settle later": an amount is locked, then split into what was really used (charged) and the rest (released). One component for the hotel card (₹) and the token budget.

**Props:** `unit` (₹ | tokens), `total` (optional bar total), `hold` ({amount, at}), `settle` ({used, at}), `releaseAt`, `labels` ({held, charged, released}), `variant` (`card` | `bar`), `leak` ([{at}] failures that keep a hold locked), `fixAt` (all leaked holds return), `rect`, `at`, `out`.

**Look**
- `card`: a generic payment card (no bank or network logos) with a lock icon and "₹5,000 held".
- `bar`: the DualMeter budget bar; held = orange hatch + lock, charged = solid orange, released = white.
- Labels in Inter 800, amounts tabular.

**Motion**
- Hold: the chunk lifts off the balance and locks (lock closes, thud SFX).
- Settle: the chunk splits at the used amount; the charged part turns solid, the released part slides back (spring) and the lock opens.
- `leak`: each failure greys a call card with an orange warning mark and leaves its chunk locked; `fixAt` returns every locked chunk, staggered 4 frames.
- `card` → `bar`: the card morphs into the bar (shared rect) when the story moves from the hotel to the server.

**Gotchas**
- Numbers must add up on screen (5,000 = 3,200 + 1,800; 50,000 − 2,200 = 47,800; + 300 back = 48,100 when 1,900 are used).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
