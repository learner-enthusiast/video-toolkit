# RequestFlood

**Purpose:** many requests hitting a cache and falling through to the database (stampede, penetration), with an optional gate that lets one through.

**Props:** `count` (counter target, e.g. 5,00,000), `from`, `via` (Redis node), `to` (Postgres node), `passThrough` {from, to} (frames when dots skip the cache), `gate` {at, token, admit: 1}, `queue` {at, label "~50 ms"}, `rect`, `out`.

**Look**
- Small orange dots (6–10 px) streaming from a crowd of user icons; a `Counter` in Inter 800 with Indian grouping.
- Gate: a slim bar at the cache with a `LeaseToken` slot.

**Motion**
- Dots follow eased paths with deterministic per-dot offsets (index arithmetic, no `Math.random`). Pass-through: dots skip the cache and pile at the database.
- Gate: one dot takes the token and travels alone; the rest bunch into a queue, then are served from the cache.

**Gotchas**
- Cap drawn dots at ~120; the counter carries the scale, not the dot count.
