# LoadMeter

**Purpose:** a small gauge on the database node showing load through a whole video: problems push it to red, fixes bring it back.

**Props:** `events` (one list for the whole video: {at, level 0–1}), `shakeAbove` (default 0.85), `rect`.

**Look**
- A semicircle gauge (2 px border) with a needle and a short label "DB load". Fill: orange up to ~0.6, red above. (Per the project's colour decision there is no green: calm = orange at a low level.)

**Motion**
- The needle springs between levels (critically damped, ~12 frames).
- Above `shakeAbove` the database node shakes (2–3 px, deterministic from `frame`), stopping with a spring when the level drops.

**Gotchas**
- Replay `events` from one shared list so every scene shows the same level at the same moment.
- Size the Postgres node that hosts the gauge from its content (`minWidth`, not a fixed `width`). At 270 px with a 130 px gauge, "DB load" stuck out past the node's border all through `redis-invalidation` Part 2, and inspect only caught it on one transition frame. Anchor a pinned node from the right edge (`right: 40`) so it grows inward.
