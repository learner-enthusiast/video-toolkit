# LibraryAnalogy

**Purpose:** explain "every clone holds the whole history" vs "fetch only what you read" with one flat library building that returns as a callback across scenes.

**Props:** `mode` (`a` photocopies | `b` balloon | `c` reader inside), `at` (per beat word frames), `out`, `rect`.

**Look**
- Flat line-style building in brand colours: off-white fill, 2 px `#1A1A1A` strokes, a pediment roof, 4 columns, a door; orange only for the moving/important part (the copies, the one book, the "huge" label).
- Same building geometry in every mode, so the callback reads instantly.

**Modes**
- `a` photocopies: 3–4 small reader figures walk out of the door one after another (staggered 5 frames), each carrying a mini copy of the whole building (orange outline). A small "full copy" tag rides on the first one.
- `b` balloon: the building scales up with a spring (to ~1.8x, clipped by the card) while floor lines multiply; a size label counts up ("100 GB"). Readers' mini copies strain (squash) under it.
- `c` reader inside: camera pushes into the open door; a seated reader pulls one orange book from a shelf row (the rest stay grey), "only what you read" tag.

**Motion:** springs only; walk cycle is a 2-frame bob on a spring path (no linear tweens). Everything exits with a fade + slight lift.

**Gotchas:** draw in card-local coordinates (972 wide). Keep figures ≥ 60 px tall, they vanish at phone size otherwise.
