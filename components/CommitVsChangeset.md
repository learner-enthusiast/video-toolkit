# CommitVsChangeset

**Purpose:** compare a Git commit (points at a full tree) with a Scion changeset (lists only the changed files).

**Props:** `at` (left, right, nothingToPush, notTheRepo), `files` (default 3, matching Anthropic's "Shape of a Scion changeset" figure), `rect`, `out`.

**Look**
- Split card, two columns with a thin divider. Left header: official Git logo + "commit"; right header: "Scion changeset".
- Left: a commit node with an arrow to a full tree diagram (root → 3 dirs → ~12 leaf files), drawn line by line.
- Right: a list card "3 files changed" with rows `docs/guide.md`, `src/legacy.rs` (deleted), `tools/build.sh`, each with a mono content-hash chip (orange text, e.g. `3e1f…a2c4`).
- "nothing to push": a push arrow (client → server) gets an orange strike-through and dims.
- "not the repo": two horizontal bars under the columns: "cost" stays short (orange), "repo size" grows long (grey).

**Motion:** tree edges draw (stroke-dashoffset, eased); rows slide in staggered 5 frames; strike draws left→right over 8 frames; bars grow with a spring.

**Gotchas:** mono text ≥ 30 px on 9:16. Hash chips come from the figure; do not invent other numbers.
