# SharedIpFunnel

**Purpose:** many user icons (college, office, mobile tower) funnel into ONE IP badge; a block icon on the IP greys out all users at once.

**Props:** `groupsAt` (college, office, tower frames), `natAt`, `blockAt`, `rect` (card-local), `at`, `out`.

**Look**
- Three groups of small person icons at the top, labelled "College", "Office", "Mobile tower".
- Curved lines drawing into one IP pill "203.0.113.7" in the middle-bottom.
- Tag "Carrier-grade NAT"; "1000s of users".

**Motion**
- Groups pop in on their words.
- Packets (orange dots) travel down the lines.
- On block: a stop/ban icon stamps on the IP; all person icons dim to grey within 6 frames; orange warning mark.

**Gotchas**
- The "1000s of users" swarm must not overlap labels.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
