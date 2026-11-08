# TokenLifetime

**Purpose:** a JWT can't be taken back: short access tokens, refresh tokens, and a Redis blocklist for instant bans.

**Props:** `stolenAt`, `countdownAt` ("valid until exp"), `accessAt` ("15 min"), `refreshAt` ("7 days"), `swapAt`, `redisAt`, `blockAt` (jti drops in), `rect`, `out`.

**Look**
- Stolen token: a token chip with a hooked hand line icon, dim grey + orange WarnMark, and a mono countdown "valid until exp 14:59".
- Two token cards: Access (orange fill, "15 min") and Refresh (white, "7 days").
- Swap: the refresh card emits a fresh access token (old one fades).
- Redis: the official Redis logo (assets/logos) on the card; a "blocked" list card with mono rows `jti a7f3… · TTL 14:12`, the TTL ticking down.

**Motion**
- Countdown ticks every frame-second (digits slide); cards pop on words; the jti chip drops into the list with a bounce on `blockAt`.
- Exit: fade 8 frames.

**Gotchas:** the countdown shown in a trailer segment must not jump; derive it from frames since `countdownAt`.
