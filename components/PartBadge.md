# PartBadge

**Purpose:** a persistent series marker for multi-part shorts: "OIDC · Part 1/2".

**Props:** `topic` ("OIDC"), `part` (1), `of` (2), `at` (default 0), `hideFrom` (e.g. the end card).

**Look**
- A small white pill (2 px near-black border, full radius, brand shadow): `topic` in Inter 800 26 px, a dot, "Part 1/2" in Inter 600 26 px with the number in orange. ~56 px tall.
- Position: frame coordinates, top-left inside the 5% margin (x = 54, y = 120), so it clears the platform's top bar. In SPLIT it overlaps the grid card's top-left corner, so scenes keep a 320×90 px corner clear.
- In dark punches it stays white (it is already a white tile).

**Motion**
- Enters once at `at` (slide in from the left 24 px, `pop`), then holds; it does not move with the HEAD ↔ SPLIT switch.
- Hides at `hideFrom` with a fade.

**Gotchas**
- Never over the face: in HEAD the face sits at y ≈ 600–1000, so the badge is clear.
