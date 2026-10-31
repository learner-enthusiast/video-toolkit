# Server3D

**Purpose:** one 3D scene of database servers for sharding, cross-network latency and vertical scaling with read replicas. Built with `@remotion/three` (Three.js).

**Props:** `phase` timings (all word-triggered): `splitAt`, `labelsAt`, `packetsAt`, `latencyAt`, `growAt`, `replicasAt`, `readsAt`, `out`; `shards` (name, label), `rect`.

**Look**
- Servers are rack-style boxes (a stack of 3–4 slab units with a thin gap), cream/off-white material (`MeshStandardMaterial`, roughness ~0.9), near-black edges via `EdgesGeometry` + `LineSegments` (~2 px look), and a small orange status light per unit.
- Floor: an off-white plane with the notebook grid drawn on it; no visible horizon.
- Isometric-style camera (orthographic, ~35° elevation, 45° azimuth) with a slow orbit of about 10–15° over the scene.
- Lighting: hemisphere + one soft directional light, no hard shadows (or a soft contact-shadow blob only). Background is the page color, so it sits on the brand.
- Labels (server names, "users", "latency", "reads") are HTML overlays placed from projected 3D positions, in brand fonts, not 3D text.

**Motion** (all from `useCurrentFrame()` with `spring()`/`interpolate()`, never R3F `useFrame()`)
- Split: one server scales its units apart and slides into three servers (A, B, C) with springs, staggered 4–6 frames; shard labels pop in.
- Packets: small orange spheres travel along a raised arc between A and B (ease-in-out per trip), with a fading trail. A clock icon ticks and a "latency" `Tag` pulses in scale once per trip.
- Vertical scaling: the primary server grows taller (adds units) with a spring; then three smaller "replica" servers rise from the floor in sequence; orange arrows labelled "reads" draw toward them.
- Exit: the camera eases out slightly while everything fades.

**Gotchas**
- Pass `flat` to `ThreeCanvas` (no ACES tone mapping), or cream and orange turn grey and stop matching the 2D brand.
- Camera: mostly front (azimuth ~16–28°, elevation ~26°). At 45° the shards line up diagonally and labels collide.
- Put server labels on the floor in front of each server, so arcs and packets above stay visible; HUD items (clock, latency) go in an empty corner, never under the headline.
- Drive the camera by copying a frame-computed camera onto R3F's default camera during render (`useThree`), and project HTML labels with that same camera.
- Render with `--gl=angle` through `gpu-run`; verify with `npx remotion gpu`. If ANGLE runs out of memory, render the scene in parts.
- Pass `width`/`height` to `ThreeCanvas` and keep geometry low-poly; no post-processing.
- Project label positions with the same camera every frame, so labels never drift off their servers.
- No logos on servers; names are text labels.
