# SessionMapScale

**Purpose:** why server-side sessions struggle: a stranger request, the in-memory session map and cookie round-trip, the map ballooning, a restart wiping it, and a load balancer sending you to a server that never heard of you.

**Props:** `strangersAt`, `statelessTag` ({at}), `serverAt`, `mapRowAt`, `cookieAt`, `lookupAt`, `balloonAt`, `restartAt`, `lbAt`, `server2At`, `rect`, `out`.

**Look**
- Stranger requests: 3 grey faceless person line icons with a small "?" each; a Tag "HTTP is stateless".
- Server: a line-icon server card with a white inset "memory" table in JetBrains Mono ≥ 34 px: `sess_8f2a → { id: 42 }`.
- Cookie: a small orange chip `sid=sess_8f2a` travelling server → browser card and back; a magnifier icon over the row on lookup.
- Balloon: the table grows (scale + extra ghost rows) and a counter rolls to "1,000,000 entries".
- Restart: a circular-arrow icon; rows wipe top-down; small user icons fly to a "Login" card.
- Load balancer: an LB box fanning to Server 1 / 2 / 3; Server 2 dims to warm grey with a bubble "Who are you?" and an orange WarnMark.

**Motion**
- Each sub-beat triggers on its spoken word; earlier parts slide up / shrink to make room (spring), never all at once.
- Counter rolls with ease-in-out; packets travel along a curved path.
- Exit: fade + lift 8 frames.

**Gotchas**
- No red/green: the failure state is dim grey + orange WarnMark.
- Keep the LB fan readable in a 972 px card: three servers on one row, labels ≥ 30 px.
