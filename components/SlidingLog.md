# SlidingLog

**Purpose:** sliding window log: a 60-s window slides over a stream of timestamp ticks; a memory bar fills up.

**Props:** `slideFrom`, `slideTo`, `memAt`, `warnAt`, `rect` (card-local), `at`, `out`.

**Look**
- Tick stream of small timestamp pills.
- Translucent orange-outlined window bracket labelled "last 60 s".
- Memory bar below, labelled "memory", filling in dim grey; orange warning mark at the end.

**Motion**
- Window slides with eased motion.
- Ticks enter from the right and pile up.
- Bar fills, eased.

**Gotchas**
- Tick labels ≥ 24 px, or drop the labels.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
