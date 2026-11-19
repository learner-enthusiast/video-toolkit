# RationBags

**Purpose:** identical units make counting enough: five 1 kg rice bags on a shop counter.

**Props:** `drops` (frames, one per bag), `tallyLabel` ("kg"), `cardAt` (ration card chip "5 kg / card"), `sameAt` (equal marks between bags), `rect`, `at`, `out`.

**Look**
- Flat line illustration: a counter line, five identical sacks (off-white, 2 px border, "1 kg" label), a ration-card chip, a big tally numeral "1 … 5 kg" in orange.

**Motion**
- Bags drop one by one with a spring and a soft thud, staggered on the words; the tally steps with each.
- On "the same": small "=" marks pop between the bags.

**Gotchas**
- Bags must be pixel-identical; the point is that they are the same.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
