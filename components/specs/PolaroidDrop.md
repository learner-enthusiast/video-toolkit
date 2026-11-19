# PolaroidDrop

**Purpose:** polaroid-style photos drop onto the card one by one ("won an iPhone", "a MacBook Pro", the ₹20k swag), small, slightly rotated.

**Props:** `photos` (src, caption | null, `at`, rotate), `rect`, `out`.

**Look**
- White polaroid frame (2 px `#1A1A1A` border, brand radius, soft shadow), image inside with object-fit cover, ~360 px wide on the 972 px card, small caption strip in Inter 700 (product name only, no Apple logo: "iPhone", "MacBook Pro").
- Images are used exactly as supplied (poster text and names included, user decision 2026-11-14), never stretched or cropped to hide anything.
- Rotations −7° / +5° / −3°, overlapping a little in a staggered pile.

**Motion**
- Each photo drops from above: spring (low damping, small bounce) on its word, with `sfx-receipt-drop-swish.wav` low; the previous ones shift down/aside 12 px.
- The third (swag) has no spoken line: it lands ~12 frames after "Students just like me" begins, as a visual-only beat.
- Exit: the pile slides down and fades.

**Gotchas**
- Polaroid-sized, never full-frame (they are other students).
- At most the top ~55% of a FULL card is used so captions stay clear.
