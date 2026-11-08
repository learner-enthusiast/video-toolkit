# UpdateRace

**Purpose:** show two updates reaching the database in order but reaching the cache reversed over the network (why "update the cache" is unsafe, and why delete is order-proof).

**Props:** `source` (icon + label), `left` (Postgres node), `right` (Redis node), `envelopes` (id, label, `leaveAt`, `dbAt`, `cacheAt`), `mode` (set | del), `rect`, `out`.

**Look**
- Source on top, Postgres bottom-left, Redis bottom-right (official logos). A straight path to Postgres; a wavy "network" path (a sine curve, dashed) to Redis.
- Envelopes: small white cards with an orange flap, label `#1 ₹54,999` or `DEL price:iphone` in JetBrains Mono.

**Motion**
- Envelopes travel along the paths with ease-in-out; on the wavy path #2 is faster and overtakes #1 (computed from progress, not random).
- On arrival: set mode → the node's `PriceTag` flips to that value; del mode → the key card dissolves (both times the same result).

**Gotchas**
- Arrival order must match the narration: DB gets #1 then #2; cache gets #2 then #1.
