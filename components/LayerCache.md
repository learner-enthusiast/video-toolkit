# LayerCache

**Purpose:** show image layers and the build cache: each Dockerfile step becomes a layer block; on rebuild the lower ones are CACHED.

**Props:** `layers` (`[{label, at}]`), `build1At`, `editAt`, `cachedAt`, `rebuildAt`, `fastAt`, `at`, `out`.

**Look**
- A vertical stack of 5 blocks (bottom = base `node:20-alpine`), each a white block with mono label; a filling orange-tint progress bar inside while it builds.
- Timer chip top-right in Inter 800 tabular figures ("45 s", then "3 s").
- CACHED: an orange solid `Tag` that flashes onto each lower block; rebuilt blocks refill.
- Edit: a small `index.js` file chip with a pencil mark slides in beside the code layer.

**Motion**
- Build 1: blocks fill bottom-up, staggered (~5 frames), timer counts to 45.
- Rebuild: CACHED tags pop up the stack staggered 4–6 frames, then only the top two refill while the timer counts 0 → 3.

**Gotchas**
- Triggers on spoken words ("layers", "caches", "Change only your code", "second build").
- Use the same five line labels as the DockerPipeline Dockerfile card so the step carries over.
