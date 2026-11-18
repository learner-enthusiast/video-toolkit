# ContextOverflow

**Purpose:** show that an approach which puts every index/tree into the prompt stops scaling: the items no longer fit in the context window.

**Props:** `label` ("context window"), `groups` (label, count, `at`), `manyAt`, `fitAt`, `out`.

**Look**
- A dashed near-black box labelled with an ink pill. Tree glyphs (small root + three leaves) fill it in a tidy grid.
- Group pills above the box name what is being added ("+ every GST circular", "+ every court case").
- Overflow: dozens of warm-grey glyphs land outside the box at random angles, a counter pill reads "1,000s of trees".
- On `fitAt` the box border turns solid orange, shakes once, and an orange warning stamp ("WON'T FIT") lands.

**Motion**
- Glyphs pop in 2 frames apart per group, ~1 frame apart in the overflow burst. One stamp, one shake.

**Gotchas**
- Seed the random positions (deterministic renders).
- Keep the stamp over the box, not over the group pills.
- No red: overflow is orange + warm grey.
