# ShippingContainer

**Purpose:** the shipping-container analogy: one standard box that every vehicle can carry, which opens to show what a software container packs.

**Props:** `rideAt` ([truck, train, ship] frames), `openAt`, `contents` (list of `{label, at}`), `closeAt`, `landAt` ([3 frames]), `at`, `out`.

**Look**
- A flat, front-facing orange steel box (corrugation lines in a darker orange, 2 px near-black outline, brand radius on the corners), ~420 x 220 px.
- Vehicles are simple near-black line drawings on white (truck cab, train bogie, ship hull with waterline), never photos.
- Before-1956 dock: a sepia-tinted panel with small line workers carrying sacks, "before 1956" date `Tag`.
- Open: the front doors swing (scaleX on two halves); contents slide out as stacked white chips (JetBrains Mono).
- Closed lid: the official Docker mark on a white tile on the box face.

**Motion**
- Box drops in with a stiff spring; between vehicles the box stays put and the vehicle slides under it (ease-in-out ~14 frames), with wheels/waves moving by frame.
- Contents pop in staggered 4–6 frames on their spoken words; doors close with a spring; the box then hops to three targets along arcs.

**Gotchas**
- Keep the box the same size across truck/train/ship: "same box" is the point.
- The sepia panel is the only off-palette element; keep it desaturated and light (a deliberate archival look, note it as a brand deviation).
