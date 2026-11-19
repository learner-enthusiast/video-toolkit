# IconMorph

**Purpose:** one idea turning into the next on the same spot: an office building (Kerberos, office network) becomes a signed XML card (SAML). Reusable for any "A became B" history beat.

**Props:** `from` ({icon: line-icon id, label, at}), `to` ({node: React node or card spec, label, at}), `dimAt` (optional: a caveat row dims grey), `caveat` ({text, at}), `out`, `rect`.

**Look**
- `from`: a generic line icon (2.6 px near-black stroke, orange accent detail), ~300 px, with a label under it in Inter 600 40 px and a dim year chip ("1980s").
- `to`: a white card (2 px border, brand radius) with JetBrains Mono ≥ 30 px content. For SAML: `<Assertion>` / `<Subject>this is Arnab</Subject>` / `<Signature/>`, the subject text on an orange block. Year chip "2000s".
- Caveat row under the card: "✓ corporate browsers" in near-black, "mobile apps and APIs" dimmed warm grey with a WarnMark (no red/green; the tick is an orange line icon, not a character).

**Motion**
- `from.at`: icon strokes draw in (stroke-dashoffset, ~12 frames), label rises 16 px with `pop`.
- `to.at` (morph): the icon squashes (scale 1 → 0.6, opacity → 0) while the card springs up from the same centre (scale 0.6 → 1), overlapping 6 frames. The year chip flips (rotateX) to the new year.
- Card lines reveal one by one, staggered 5 frames; the subject block wipes in left to right.
- `caveat.at` / `dimAt`: the good row pops, then the bad row dims and its WarnMark lands.
- Exit at `out`: everything fades with a 20 px lift.

**Gotchas**
- Never a hard swap: the two shapes must overlap in time, or it reads as a cut.
- Keep the morph centred on the same point so the eye doesn't travel.
