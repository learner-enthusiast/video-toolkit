# CheckpointTicket

**Purpose:** a flat price per unit of work, as a physical ticket ("checkpoint · $0.25") that can repeat, sit unchanged under very different jobs, and later morph into a range. One object carries the pricing story.

**Props:** `price`, `label` (uppercase kicker), `w`, `h`, `tone` (`plain` | `orange` | `dim`), `ring` (0..1 orange outline pulse), `at`, `out`.

**Look**
- White ticket with rounded corners and two half-circle notches at a perforation ~28% from the left (dashed warm-grey line). Stub: a small flag icon (orange fill). Body: Inter 800 kicker (dim, ~17% of h), Inter 900 price (~42% of h, tabular).
- `orange` = 4 px orange edge + orange price (the "big job" end of a range); `dim` = grey edge and text (retired price).

**Motion**
- Pops in (popIn) on its word; repeats stagger by 6–8 frames and stack identically. `ring` pulses on "both are one checkpoint". A retired ticket dims, shrinks ~15% and gets a CrossOut on "dropped".

**Gotchas**
- Keep identical tickets truly identical (same size, same price) until the story says otherwise: the sameness is the point.
- Real prices only (Replit $0.25 → 6¢ … a few $, June 2025); illustrative ones get an "example" tag.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
