# ShatterTransition

**Purpose:** a diagram cracks and shatters on a spoken word ("it breaks"), clearing the card for the next headline.

**Props:** `target` rect, `crackAt`, `shatterAt`, `pieces` (count, ~18), `seed`.

**Look**
- Cracks: thin near-black jagged polylines drawn over the target with an orange glint at the impact point.
- Shards: Voronoi-like polygons clipping a snapshot of the target (render the target inside each shard with `clip-path: polygon()`).

**Motion**
- Cracks draw from the impact point in ~6 frames (ease-out), with a 2-frame 6 px shake of the card.
- Shards fall with per-shard spring-driven velocity, rotation and fade over ~20 frames; deterministic from `seed`.
- Optional low glass-crack SFX (synthesised, quiet).

**Gotchas**
- Everything derived from `useCurrentFrame()` and a seeded random; never Math.random().
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
