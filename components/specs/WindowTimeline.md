# WindowTimeline

**Purpose:** fixed window: minute blocks with a counter 1→5 that resets; boundary zoom showing 5 dots at 12:00:59 and 5 at 12:01:00, tag "2× limit".

**Props:** `tickAt`, `resetAt`, `zoomAt`, `burstAt`, `tagAt`, `rect` (card-local), `at`, `out`.

**Look**
- Horizontal timeline with minute blocks labelled 12:00 / 12:01; counter box above.
- Zoom: magnified 2-second strip with 10 orange dots split by the boundary line; timestamps "12:00:59" and "12:01:00" in JetBrains Mono.
- Tag "2× limit".

**Motion**
- Counter ticks with a spring; reset flips to 0.
- Camera-style zoom (scale + translate, eased).

**Gotchas**
- "2× limit" uses an orange warning mark, not red.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
