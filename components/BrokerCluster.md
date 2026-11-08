# BrokerCluster

**Purpose:** who owns which partition, and how that changes when a machine dies: an external coordinator (ZooKeeper) versus the brokers keeping the list themselves (KRaft).

**Props:** `brokers` (ids, partition tags), `manager` (logo, `at`), `assign` (list of `P → Broker` lines), `fail` {broker, at}, `reassign` {partition, to, at}, `absorb` {into, at} (manager leaves, clipboard moves in), `votes` {at}, `rect`, `out`.

**Look**
- Three broker boxes in a row (brand radius, 2 px border, off-white), title `Broker 1/2/3` in Inter 700, partition tags (`P0`, `P1`, `P2`) as small pills inside.
- Manager: a separate box outside the row with the official logo on a white tile, holding a clipboard card whose lines are JetBrains Mono (`P1 → Broker 2`).
- Failed broker: red border and red title, contents dimmed to warm grey.
- After `absorb`: the clipboard sits inside one broker, with small "vote ✓" chips on the links between brokers.

**Motion**
- Brokers pop in staggered 4–6 frames; tags drop in with a spring.
- Reassign: the clipboard line rewrites (old target struck through, new one written in), and the `P1` tag travels along an arc to its new broker.
- Absorb: an orange strike-through draws across the manager, the manager slides out of the card (ease-in), and the clipboard flies along an arc into the chosen broker.
- Votes: chips pop one after another on the links, 4–6 frames apart.

**Gotchas**
- Keep the logo undistorted (`object-fit: contain`) on its tile; the strike-through goes over the tile, never recolours it.
- Clipboard lines ≥ 28 px mono at phone width; show at most 3 lines.
