# AccountQuotaBar

**Purpose:** a shared account quota used up by one user, so everyone else is blocked.

**Props:** `label` ("Your account: tokens per minute"), `floodAt`, `users` (count, default 12), `heavyIndex`, `blockAt` (first card flip; the rest stagger), `caption` ({text, at}), `rect`, `at`, `out`. Dark style.

**Look**
- One wide bar with a 100% mark; small neutral segments for normal users, one orange segment for the heavy user.
- Below: a grid of generic user tiles (line icon, no faces). Blocked = dim grey tile + orange warning mark + "429" in mono.

**Motion**
- Flood: the orange segment grows to fill the bar (ease-in-out ~18 frames), squeezing the others out.
- Tiles flip one by one (rotateX, 4-frame stagger) to the 429 state; the heavy user's tile stays orange.
- Caption lands last.

**Gotchas**
- 12 tiles at ≥ 150 px in a 972 px card: 4 × 3 grid.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
