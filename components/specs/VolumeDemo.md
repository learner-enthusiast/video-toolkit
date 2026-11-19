# VolumeDemo

**Purpose:** containers are disposable; a volume keeps the data outside them.

**Props:** `deleteAt`, `goneAt`, `volumeAt`, `recreateAt`, `keptAt`, `at`, `out`.

**Look**
- A container box with the PostgreSQL logo holding a small "users" table (3 rows, mono).
- Run 1: the container fades to warm grey, the table crumbles away, `Tag` "data gone" (dim + orange warning mark).
- Run 2: a separate "volume" cylinder (white, 2 px border, orange label) sits outside the container holding the table, joined by a mount line; the container is deleted and a new one pops in and re-attaches; orange `Tag` "✓ data kept".

**Motion**
- Delete: scale .96 + grey crossfade over 10 frames; table rows drop out staggered.
- Recreate: new container pops with spring; mount line redraws; a packet runs volume → container.

**Gotchas**
- Two clearly separated runs (left/top = without, right/bottom = with), so the comparison reads at a glance.
