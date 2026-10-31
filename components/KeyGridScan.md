# KeyGridScan

**Purpose:** two ways a system cleans up stale items: lazily when one is read, and by a fast random sweep (here: Redis expiry).

**Props:** `w`, `h`, `leftAt`, `getAt`, `checkAt`, `dissolveAt`, `nilAt`, `rightAt`, `scanAt`, `out`.

**Look**
- Two columns with Inter 700 34 px headers. Left: a vertical flow of `GET` pill, "expired?" with an orange tick, a key tile, and an orange `(nil)` result, joined by drawn arrows.
- Right: a 5×5 grid of small white key tiles; eight are expired (dim, page background, tiny orange dot).
- An orange highlight square hops tile to tile.

**Motion**
- Tiles pop in a diagonal ripple. The key tile breaks into 8 squares that drift down, rotate a little and fade (deterministic offsets).
- From `scanAt` the highlight moves every 4 frames (3-frame eased hop) along a fixed sequence; an expired tile fades out on first visit and stays gone.

**Gotchas**
- The visiting sequence is a fixed list that hits every expired tile within 16 steps; edit it to retime the reveals.
- No `Math.random`: offsets come from index arithmetic.
- The right header wraps to two lines; the grid starts below it.
