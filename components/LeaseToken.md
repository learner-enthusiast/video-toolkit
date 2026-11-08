# LeaseToken

**Purpose:** a fill-permission token (memcache-style lease) handed to one request.

**Props:** `id` (`L1`), `state` (valid | cancelled), `handTo` {rect, at}, `cancelAt`, `rect`, `at`, `out`.

**Look**
- An orange ticket with notched ends, white JetBrains Mono `lease: L1`. Cancelled: warm grey fill, dashed border.

**Motion**
- Hand-over: flies along an arc to the holder and settles with a small spring tilt.
- Cancel: a 6-frame crossfade to grey plus a slight shrink.
- Rejected write: the ticket shakes once (2 px, 4 frames).
