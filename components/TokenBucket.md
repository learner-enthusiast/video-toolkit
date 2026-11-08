# TokenBucket

**Purpose:** bucket holds 10 tokens, one drips in per second, requests take one each; a quiet period fills it, then a burst of 10 arrows; AWS logo.

**Props:** `dripAt`, `takeAt`, `quietAt`, `burstAt`, `logoAt`, `rect` (card-local), `at`, `out`.

**Look**
- Line-drawn bucket; tokens as orange coins with count "7/10".
- Request arrows from the left.
- AWS official logo for "AWS API Gateway".

**Motion**
- Coins drop with a spring.
- Burst = 10 arrows fly out, staggered 2 frames.

**Gotchas**
- Count label must match the coins shown.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
