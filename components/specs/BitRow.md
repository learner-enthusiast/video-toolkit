# BitRow

**Purpose:** a row of bits (Bloom filter, bitmap, bitset) whose state builds up as I name each bit, and stays the same across scenes.

**Props:** `n` (default 10), `events` (each: `bit`, `at`, `kind` = set | pulse | check | miss | label | try-clear, plus `who` for set/label), `rect`, `out`.

**State**
- Derive every box's value by replaying `events` up to the current frame, from one shared list for the whole video. Never keep per-scene copies, or a later scene shows bits an earlier one never set.
- Only `set` turns a bit to 1. Checks, pulses and labels never change a bit.
- Track who set each bit (a bit can have several owners), so later scenes can label it.

**Look**
- `n` square boxes on one row, centred in the rect, equal gaps, the brand radius and 2 px border. Index numbers 0…n−1 under each in JetBrains Mono, dim.
- 0: off-white box, grey outline, "0" in dim JetBrains Mono. 1: orange fill, white "1".
- `check`: the box glows (soft orange ring + lift). `miss`: a 0 found during a check flashes in the "no" tone (per the project's color override), then settles back.
- `label`: a tiny lowercase name chip (JetBrains Mono) above the box, saying who set it.

**Motion**
- Flip 0 → 1: a spring scale 1 → 1.15 → 1 with the fill wiping up, on the exact frame of the spoken number.
- `pulse`: a single scale bump on a bit that is already 1 (it stays 1).
- When I say "1, 4 and 8", each box triggers on its own word, so they ripple in speech order.
- Enter: boxes pop in left to right, staggered 2–3 frames. Exit: fade with a slight lift.

**Gotchas**
- Bit numbers trigger on word timestamps (`at('four')`), never on the start of the sentence.
- Keep the row the same size and position while it persists between scenes, so it reads as one object; move it with a spring if a scene needs the space.
- Index labels must stay readable at phone width: at 10 bits on a 970 px card, boxes ≈ 78 px.
