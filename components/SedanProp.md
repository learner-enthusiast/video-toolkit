# SedanProp

**Purpose:** a line-art sedan in brand style, the "thing being argued about" in a story (here: the car Jethalal wants GST credit on). Carries tags and a seat counter.

**Props:** `w`, `dim` (accent turns warm grey), `dark`, children (tags), plus `CarTag`: `label`, `x`, `y`, `at`, `out`, `fallAt`, `tone`.

**Look**
- Side view drawn in a 400x150 box: white body, near-black 4.5 px outline, off-white windows, orange details only (door handles, lights, wheel hubs), a dotted ground line.
- Tags are pills hung on the car at a slight angle: "NEW" (orange), "₹ GST credit" (white or orange), "ITC blocked" (orange).
- Seat counter beside it: a white card with "SEATS, UP TO", a big orange mono number ticking 1 → 13 and a 13-dot grid filling with it.

**Motion**
- Car slides/fades in with the scene. Tags pop (spring). `fallAt`: the tag drops with a quarter spin and fades (16 frames, ease-in).
- BLOCKED lands as a `Stamp` across the car; the accent details dim to grey on the same frame.

**Gotchas**
- One stamp per beat. Keep the tag clear of the stamp's landing spot.
- The seat counter ticks on the spoken number, never before it.
- No brand badge or recognisable model; it is a generic sedan.
