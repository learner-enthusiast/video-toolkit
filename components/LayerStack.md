# LayerStack

**Purpose:** three stacked rows: Login = IP (loose) + Account (strict) · OTP = Phone + IP · API = Key.

**Props:** `rowsAt` (3 frames), `partsAt`, `rect` (card-local), `at`, `out`.

**Look**
- Each row = label pill on the left (Login / OTP / APIs) + key chips.
- "loose" chip in dim grey outline; "strict" chip solid orange.

**Motion**
- Rows build one by one as spoken.
- Chips pop, staggered 4–6 frames.

**Gotchas**
- Rows must fit the GRAPHIC card with ≥ 48 px text.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
