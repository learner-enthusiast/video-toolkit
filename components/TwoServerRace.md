# TwoServerRace

**Purpose:** two server boxes both read 99 from one Redis box, both say "yes", counter jumps to 101 with an orange warning.

**Props:** `readAt`, `yesAt`, `writeAt`, `qAt`, `rect` (card-local), `at`, `out`.

**Look**
- Redis official logo in the centre box with counter "99".
- Two server boxes left and right, with arrows; speech tags "99 < 100 → yes".
- Counter flips to "101" with an orange warning; big orange "?" at the end.

**Motion**
- Read arrows draw simultaneously.
- Writes land together.
- Counter flips 99 → 100 → 101 quickly.

**Gotchas**
- The Redis logo is red (official colour, brand.md logo exception); list as a deviation.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
