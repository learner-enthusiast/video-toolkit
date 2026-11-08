# LeakyBucket

**Purpose:** funnel/tap: messy traffic in on top, steady drip out the bottom, overflow bounced. NGINX logo + `limit_req`.

**Props:** `inAt`, `outAt`, `overflowAt`, `logoAt`, `rect` (card-local), `at`, `out`.

**Look**
- Funnel shape; irregular dots arriving on top.
- Evenly spaced dots leaving the bottom on a flat line, "steady".
- Overflow dots bounce off in dim grey.
- NGINX official logo + JetBrains Mono chip `limit_req`.

**Motion**
- Input bursty (uneven spacing); output metronomic.

**Gotchas**
- The NGINX logo is green (official colour, brand.md logo exception); list as a deviation.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
