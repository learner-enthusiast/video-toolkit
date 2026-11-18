# ReceiptStack

**Purpose:** purchase receipts slam down one by one with an ENROLLED stamp each while a counter ticks (2 → 3 → 4); the 4th is a dark punch.

**Props:** `receipts` (src, label, `at`), `counter` (CohortCounter values), `darkLast`, `fan` (frame to fan all four), `rect`, `out`.

**Look**
- Receipts are the user's purchase screenshots (253×296 px sources): shown ≤ 2× (~440 px wide), 2 px border, brand radius, soft shadow, slight rotations (−4°, +3°, −2°).
- An orange ENROLLED `Stamp` lands on each; the 4th lands over a dark `#0D0D0D` card (dark-style punch) and the scene returns to light on the next beat.
- Receipt 01 (Web Dev) is already at the bottom of the pile from the hook; 02–04 stack on it.

**Motion**
- Each receipt drops from above (spring, small bounce) on its spoken course name ("System Design", "Generative AI", "Mobile Development") with the thud SFX; the stamp lands ~8 frames later (`Stamp` spring); the counter ticks on the stamp.
- Optional `fan`: all four spread into a fan (used by the "NOT SPONSORED" beat).

**Gotchas**
- One stamp per receipt, never over the course title. ENROLLED, not "SCAMMED".
- Do not upscale past 2× (soft source); no Apple/Google logos added.
