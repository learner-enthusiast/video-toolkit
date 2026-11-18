# AvatarRow

**Purpose:** "who are these people?" row of circular photo avatars with name labels that pop in as each name is spoken. Photos only come from the user's `assets/people/`; a missing one falls back to an initials avatar.

**Props:** `people` (name, photo | null, tag, `at`), `focus` (index), `wink` (frame pair for "same person"), `rect`, `out`.

**Look**
- Circles ~220 px, 2 px `#1A1A1A` border, object-fit cover (no stretch, face-centred); name in Inter 800 ~30 px below; small orange pill tag under a name when `tag` is set ("aka BigBoss").
- Initials fallback: a warm-grey `#8A857C` circle with white Inter 900 initials ("PG").
- 4 people in a 2 × 2 grid (9:16 card), staggered.

**Motion**
- Each avatar pops (spring, small overshoot) on its name; the focused one gets an orange ring while the others dim to 55%.
- `wink`: when "BigBoss" and then "Anirudh Jwala" are said, the same avatar lights twice, with a small orange "= same guy" tag swinging in between.
- Exit: all together, 8-frame fade.

**Gotchas**
- BigBoss and Anirudh Jwala are ONE person: one avatar, one "aka BigBoss" tag, never two circles.
- Never add a SCAMMED/blame stamp to any photo. Names are exactly: Piyush Garg, Anirudh Jwala, Suraj, YNTP.
- The user's own photo files only: never fetch people images from the web.
