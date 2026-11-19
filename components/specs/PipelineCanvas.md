# PipelineCanvas

**Purpose:** one large running canvas that every diagram scene draws onto, so a closing zoom-out shows the real pipeline built so far (`rag-pipeline`).

**Props:** `stations` (id, canvas rect, label, `at` reveal frame), `camera` keyframes (`at`, target station id or rect, zoom), `card` rect.

**Look**
- A big notebook-grid plane (e.g. 3×4 card widths) inside the grid card, the card clips it. Each station is a small framed area (14 px radius, 2 px border) with its stage label in Inter 600 and an icon.
- Stations are connected by thin near-black lines with orange packets once both ends exist.

**Motion**
- The camera (translate + scale of the plane) springs from station to station (~0.6 s, ease-in-out), triggered on the step's first spoken word.
- Each station's detailed scene renders inside it at full size while the camera is on it; once the camera leaves, the scene collapses to its compact summary state (icon + label), so the zoom-out reads cleanly.

**Gotchas**
- Lay out stations in reading order (zig-zag down), so the camera never jumps backwards across the plane.
- Scenes keep card-local coordinates of their station; the plane transform is applied once by the canvas, never inside scenes.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
- Connectors run edge-to-edge in the gaps between stations, never centre-to-centre (they showed through transparent stations on `rag-pipeline`).
- 3×3 snake of 972×960 stations with 150 px gaps fits the card at ~0.28 scale; compact labels at 150 px Inter 900 read at ~40 px. To make room for a stat card, shrink to ×0.7 and lift the plane (centre 94 px up).
