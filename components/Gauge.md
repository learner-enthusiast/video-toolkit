# Gauge

**Purpose:** a semicircular gauge that fills to a value with a label (evaluation metrics).

**Props:** `label`, `value` (0–1), `at`, `tone`, `warn`, `out`.

**Look**
- 180° arc track #DCD8D0, fill orange, needle near-black, label Inter 600 below, value numeral above (tabular).
- `warn`: a small orange warning mark beside the gauge.

**Motion**
- Arc fills with ease-out over ~0.8 s from its word; needle springs.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
