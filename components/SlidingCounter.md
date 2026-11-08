# SlidingCounter

**Purpose:** two boxes PREV / CURR with an overlap slider; Cloudflare logo + "400M requests → 0.003% wrong".

**Props:** `boxesAt`, `sliderAt`, `logoAt`, `statAt`, `rect` (card-local), `at`, `out`.

**Look**
- Two big counter boxes "PREV 42" and "CURR 18".
- Slider showing 75% overlap and the formula "42 × 0.25 + 18".
- Cloudflare official logo (assets/logos/cloudflare.svg, object-fit contain, never recoloured).
- Stat line with counting numbers: "400M requests → 0.003% wrong".

**Motion**
- Slider eases to 75%.
- Numbers count up with ease-out.

**Gotchas**
- Logo keeps official colours.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
