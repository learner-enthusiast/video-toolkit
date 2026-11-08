# ComposeServices

**Purpose:** Docker Compose: one `compose.yaml` that starts several containers together on one network.

**Props:** `services` (`[{name, logo?, at}]`), `upAt`, `at`, `out`.

**Look**
- A code card titled `compose.yaml` (mono ≥ 30 px) listing `services:` with `app`, `postgres`, `redis`.
- Below: three container boxes (orange box motif, small) with the service's official logo on a white tile (Node.js for app, PostgreSQL, Redis), joined by thin near-black lines to a "private network" bar.
- On `docker compose up`: a terminal chip with the command, and an orange check on each container.

**Motion**
- YAML lines reveal on spoken words; containers pop (spring) together on "starts them all", 4 frames apart; links draw; orange packets pulse along the network bar.

**Gotchas**
- Logos untouched, object-fit contain, on white tiles.
