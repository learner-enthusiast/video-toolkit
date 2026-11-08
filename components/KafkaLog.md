# KafkaLog

**Purpose:** an append-only log shown as a dispatch register (Kafka topic → partitions, offsets, consumer pointers). One object whose state persists across scenes.

**Props:** `events` (one shared list for the whole video: `append` {partition, text, at}, `split` {at}, `pointer` {id, label, partition, offset, at}, `crash` / `resume` {id, at}, `seek` {id, offset | "yesterday", at}, `glow` {partition, offset, at}, `label` {target, text, at}), `rect`, `out`.

**State**
- Derive rows, partitions and pointer positions by replaying `events` up to the current frame. Never keep per-scene copies, or a later scene shows rows an earlier one never wrote.
- Rows are never removed. Offsets count per partition from `#0`.
- Keyed events always land in the same partition (e.g. every `order_101` event in `P1`), decided once in the event list.

**Look**
- Off-white ruled-paper card (brand radius, 2 px border), thin ruled lines `#DCD8D0`, a narrow margin rule. Header in Inter 700 ("Topic: orders", later `P0`/`P1`/`P2`).
- Each row: offset in JetBrains Mono, dim (`#3`), then the event text; key ids as mono code chips (`order_101`).
- Pointer: a small labelled tag (`Billing → 5`) with an orange arrow at its row, on the side of the register. Several pointers move independently.
- Crashed pointer: red tag + ✕, frozen. Resumed: back to orange.
- `glow`: soft orange ring + slight lift on the row while it's spoken about.

**Motion**
- Append: the row writes in left to right (clip wipe, ~8 frames, ease-in-out) at the bottom; the card grows or scrolls with a spring.
- Split: the single register slides apart into three narrower registers side by side (~0.5 s spring); existing rows redistribute by key, then the headers change to `P0`/`P1`/`P2`.
- Pointer moves: spring from row to row; catch-up runs row by row (42 → 43 → 44 → 45), ~4 frames each.
- Seek back ("replay"): one longer ease-in-out slide up the register.

**Gotchas**
- At 3 partitions on a 972 px card, each register is ~290 px wide: row text ≥ 28 px, ids shortened (`101 placed`) rather than shrunk.
- Pointers and their arrows sit outside the registers' text area so they never cover row text.
- Every row, pointer or glow triggers on its spoken word (`at('offset')`, `at('five')`), never on the sentence start.
- `clip-path: inset()` (the write-in wipe) also clips to the element's box, so long row text silently disappears in a narrow column. In the three-column view rows shorten to "101 placed" (plain text, `white-space: pre`) and the offset gutter narrows to 60 px (`kafka`).
