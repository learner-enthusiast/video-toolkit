# StickyNote

**Purpose:** an orange sticky note slides onto a card and attaches (contextual note on a chunk).

**Props:** `text`, `at`, `target` rect, `out`.

**Look**
- Orange #E4572E note, white or near-black Inter 600 ~30 px, slight rotation (−3°), folded-corner detail, brand shadow.

**Motion**
- Slides in from the right with a spring, rotates to rest, small press-down scale when it attaches.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
