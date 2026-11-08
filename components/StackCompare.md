# StackCompare

**Purpose:** one or two layer stacks (VM vs container) built bottom-up, to compare what each one carries.

**Props:** `stacks`: `[{title, x, w, layers: [{label, at, tone ('neutral'|'heavy'|'accent'|'dim'), split?: string[]}]}]`, `chips`: `[{text, at, tone, x, y}]`, `greyAt` (per layer), `at`, `out`.

**Look**
- Each layer = a full-width block (2 px border, brand radius, Inter 700 ≥ 34 px). Hardware at the bottom.
- `heavy` (Guest OS) is twice as tall with a hatched fill; it greys to warm grey with an orange warning mark when it becomes the problem.
- `split` layers draw as several side-by-side boxes on one row (App A | App B | App C).
- The container's kernel layer is orange ("ONE shared Linux kernel").
- Size/time chips are `Tag`s (orange = good, dim = bad) beside the stacks.

**Motion**
- Layers drop from above with a spring (small overshoot) bottom-up, 4–6 frames apart, or each on its spoken word.
- Greying: colour crossfade over 10 frames.
- Exit: the whole stack fades and rises 14 px.

**Gotchas**
- Two stacks share one baseline so heights compare honestly.
- Fit the 972 x 970 card with ≥ 34 px labels; abbreviate rather than shrink.
