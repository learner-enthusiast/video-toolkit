# ZoomCard

**Purpose:** zoom on one card (a chunk) to read it, with a grey question mark for missing context.

**Props:** `card` (text), `zoomAt`, `questionAt`, `label`, `labelAt`, `rect`, `out`.

**Look**
- The chunk card enlarged to fill most of the card width, text Inter 600 ~44 px with the key phrase highlighted.
- "which product?" in warm grey with a small orange warning mark.
- Label pill ("Contextual chunk") in orange when resolved.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
