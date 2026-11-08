# LocalSeal

**Purpose:** v4.local: one shared key, payload encrypted with XChaCha20 then sealed with a BLAKE2b MAC.

**Props:** `at`, `out`, `optionsAt` ("Only two options: local · public"), `localAt`, `keyAt`, `encAt`, `sealAt`, `tagsAt` (private ✓ tamper-proof ✓), `loopAt` (one backend creates → checks), `rect`.

**Look**
- Top pills "local" (orange, focused) · "public" (outline, dims).
- One orange key icon labelled "one shared key".
- Pipeline left→right (or top→bottom in the card): JSON payload card (mono 34 px `{"sub":"42"}`) → "XChaCha20" box that scrambles the text into random glyphs → BLAKE2b wax-seal badge (orange circle, near-black border) stamped on the scrambled card.
- Tags "private ✓" and "tamper-proof ✓" (orange ticks).
- Bottom: one server icon with a circular arrow "create → check".

**Motion:** packet travels along the path (orange), text scrambles over 10 frames (deterministic per frame), seal stamps with a StampMark-like spring. Exit fade.
