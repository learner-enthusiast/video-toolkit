# CanvasZoomOut

**Purpose:** the closing zoom-out of a `PipelineCanvas` showing every station, each pulsing orange as it is named.

**Props:** `zoomAt`, `pulses` (station id, `at`), `card`, `out`.

**Look**
- The full plane fits the card with margin; stations in compact state; connector packets travel along the whole path.

**Motion**
- Camera springs from the last station to fit-all (~0.8 s, ease-in-out); each named station scales 1 → 1.06 → 1 with an orange ring.

**Gotchas**
- Stations must be readable at the fit-all scale: labels ≥ 28 px after scaling.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
