# CommandPipe

**Purpose:** show a single-threaded queue: fast commands pass one by one, one slow command blocks everybody (here: Redis, `KEYS *`).

**Props:** `w`, `h`, `noLocksAt`, `setAt`, `getAt`, `incrAt`, `usAt`, `keysAt`, `stampAt`, `out`.

**Look**
- A wide orange-outlined pipe (110 px tall) mid-box with a label above it. Command blocks are white, 2 px border, radius 14, mono 700.
- A "No locks" pill with a crossed-out padlock at top-left. A small orange "µs" pill under each block while it is in the pipe.
- The jammed block is 3× wide with an orange border; the queue behind it turns dim (page background, dim border/text) with one "waiting…" label.

**Motion**
- The pipe draws on `noLocksAt`. Blocks slide through left to right, ~34 frames each, eased, then fade.
- The fat block enters in 18 frames, stops, and shakes for 5 frames. Four queued blocks slide in staggered 5 frames and dim.
- The existing `Stamp` lands low in the box on `stampAt`.

**Gotchas**
- Blocks are clipped at the box edges (overflow hidden), so they start off-box.
- Queue width assumes `w` ≈ 876; widen the fat block's stop position if `w` changes a lot.
- Dim means "blocked": no red.
