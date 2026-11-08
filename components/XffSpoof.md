# XffSpoof

**Purpose:** an attacker sends requests whose X-Forwarded-For header value changes each time (1.1.1.1 → 2.2.2.2 → 3.3.3.3), each getting a fresh empty counter.

**Props:** `flipsAt` (3 frames), `warnAt`, `rect` (card-local), `at`, `out`.

**Look**
- Attacker icon left; request cards in JetBrains Mono ≥ 30 px, "X-Forwarded-For: 1.1.1.1".
- Server on the right with per-IP counters "1.1.1.1: 1/5"; each new IP opens a fresh "0/5" row.
- Orange "Spoofable" tag.

**Motion**
- Header value flips like a split-flap.
- A new counter row slides in on each flip.

**Gotchas**
- Code text ≥ 28 px at 972 px card width (pipeline/composition.md).
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
