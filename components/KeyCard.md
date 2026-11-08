# KeyCard

**Purpose:** OAuth's access token as a hotel key card: it opens a room until a date and says nothing about who holds it. Then it gets misused as an ID card.

**Props:** `room` ("Room 304"), `until` ("until Sunday"), `at`, `blankAt` (name field highlighted as empty), `stamp` ({text: "ID CARD", at}), `misuse` ({at}: card dims, orange WarnMark), `logo` (optional LogoTile, e.g. facebook, with `at`), `out`, `rect`.

**Look**
- A credit-card-shaped key card (ratio 1.586:1, ~640 px wide), white, 2 px border, brand radius and shadow. Left: an orange magnetic stripe/chip shape; a generic key line icon.
- Text: `room` in Inter 800 64 px, `until` in Inter 500 36 px dim. A `Name:` row with an empty dashed field.
- `blankAt`: the empty field gets a dashed orange outline and a small "?" in Instrument Serif Italic orange.
- `stamp`: Stamp.md ("ID CARD", orange, −6°) over the card's right half.
- `misuse`: the card body dims to warm grey (opacity 0.55), stamp stays orange, a WarnMark lands top-right.

**Motion**
- `at`: slides in from the right 120 px with `pop`, a slight 6° tilt settling to −3°.
- Room and until lines reveal staggered 5 frames; the name row last.
- Stamp lands per Stamp.md (scale 1.6 → 1, small shake, stamp SFX).
- Exit at `out`: slides left 80 px and fades.

**Gotchas**
- The card must not move while the stamp lands, or the stamp looks pasted on.
- "Room 304" and "until Sunday" are the spoken words; trigger each on its word.
