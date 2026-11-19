# ChunkSlicer

**Purpose:** a document page slices along its headings into chunk cards; a table drops out as its own chunk.

**Props:** `headings` (e.g. Returns › Electronics › Phones), `sliceAt`, `sizeAt`, `tableAt`, `rect`, `out`.

**Look**
- A white page with bold heading bars and grey text lines plus one small grid table.
- Chunk cards: white, 2 px border, heading as a breadcrumb pill on top; table chunk tagged "table" in orange.

**Motion**
- An orange scan line cuts along each heading (draw), then the slices separate vertically with springs (stagger 5 frames).
- On `sizeAt`, a long slice splits once more (by size). On `tableAt`, the table lifts out, drops into its own card.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
