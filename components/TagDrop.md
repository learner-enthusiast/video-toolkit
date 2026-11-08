# TagDrop

**Purpose:** reason tags drop onto a thing, one per spoken reason (Cost · Latency · Lost in the middle).

**Props:** `tags` (label, `at`, `dim`, `note`), `rect` (landing row), `out`.

**Look**
- Pill tags (Inter 700 ~34 px, white fill, 2 px border); dimmed tags are warm grey with a small "later" note in Instrument Serif Italic.

**Motion**
- Each tag falls from above the card with a spring (bounce), lands on its row slot; stagger by word timing.

**Gotchas**
- Tags appear in the order spoken, even if the script lists them differently.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
