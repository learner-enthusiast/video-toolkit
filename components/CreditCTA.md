# CreditCTA

**Purpose:** credit the original creator in summary shorts: their thumbnail above me at the hook, and "full video in comments" at the end.

**Props:** `mode` ('hook' | 'cta'), `thumb` (file), `name` (credit tag), `at`, `out`, `arrowAt`, `handle`.

**Look**
- Thumbnail in a white frame (2 px border, brand radius, shadow), 16:9, ~720 px wide, on the wall above my head in HEAD (y ≈ 90–500 in 9:16); credit pill under it ("Piyush Garg", near-black filled).
- Hook mode: an orange arrow draws from my head up to the thumbnail (stands in for a point-up gesture when the footage has none).
- CTA mode: the thumbnail returns, an orange arrow points down with the text "Full video in comments" (Inter 900) and a follow handle pill.

**Motion:** thumbnail pops in (spring) on frame 0 in hook mode (visible on frame 1, no fade-in from 0), arrow draws 8 frames; exits by sliding up + fade. Never covers the face (keep its bottom edge ≥ 40 px above the face box).
