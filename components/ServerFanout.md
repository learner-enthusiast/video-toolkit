# ServerFanout

**Purpose:** many app servers around one cache, each holding its own in-memory copy, and how one broadcast (pub/sub) or targeted notice (CLIENT TRACKING) clears them.

**Props:** `center` (Redis node), `servers` (count shown, label e.g. "20 servers", each with a mini `PriceTag`), `pulse` {at}, `targets` {ids, at} (tracking: only these clear), `table` (who-read-what rows, `at`), `rect`, `out`.

**Look**
- Six server line icons on a ring around the official Redis logo, each with a mini PriceTag under it. A small mono label `server-3` etc.
- Tracking table: a small white card next to Redis, mono rows `server-3 → price:iphone`.

**Motion**
- Servers pop in around the ring staggered 4 frames.
- Pulse: two or three orange rings expand from Redis; each server's tag clears as the ring reaches it (timing by distance).
- Targeted: thin orange arrows draw only to the listed servers, which clear; the others stay as they are.
