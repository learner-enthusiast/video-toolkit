# AnswerGrid

**Purpose:** final recap: "1. Limit by what?" (User · Key · Phone, IP as backup) and "2. How to count?" (Login/OTP → Sliding counter · APIs → Token bucket · Fragile backend → Leaky bucket).

**Props:** `part1At`, `keysAt` (3), `backupAt`, `part2At`, `rowsAt` (3), `holdTo`, `rect` (card-local), `at`, `out`.

**Look**
- Two sections on the grid card; headings in Instrument Serif Italic orange.
- Key chips black on white; "IP · backup" smaller and dim.
- Rows "Login / OTP → Sliding window counter", "APIs → Token bucket", "Fragile backend → Leaky bucket", with arrows.

**Motion**
- Builds row by row as spoken.
- Full grid holds 1 s at the end (`holdTo`).

**Gotchas**
- This full frame is the thumbnail base; keep text ≥ 44 px and inside the 5% margin.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
