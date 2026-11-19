# Headline

**Purpose:** a big editorial headline ("How RAG really works").

**Props:** `text`, `emph` (words in italic orange), `at`, `out`, `size`.

**Look**
- Instrument Serif Italic, orange, 110–140 px in a 972 px card; non-emphasised words may be near-black Instrument Serif regular.
- Max 3 lines, centred in the card, inside the 5% margin.

**Motion**
- Words rise 24 px and fade in, staggered 4 frames; an orange underline swash draws under the emphasised word.

**Gotchas**
- Measure line width; wrap before the card edge, never shrink below 96 px.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
