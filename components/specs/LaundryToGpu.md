---
code: components/code/LaundryToGpu/LaundryToGpu.tsx
preview: components/code/LaundryToGpu/preview.png
props: "Machine {size,load: one|full|none,spinAt,tone} · Shirt {size,color} · Basket {size} · GpuRow {x,y,at,out,n,busy,spareAt,fillAt,size}"
variants: "half-empty (dim) vs full load (orange) machine, shirt, basket; GPU row spare by day, filled at night"
last_used: system-design-of-ai/10-batch-inference
---
# LaundryToGpu

**Purpose:** the "why is waiting cheaper" analogy. Two laundry counters (EXPRESS · 2 hours / REGULAR · 2 days): Express spins one shirt in a mostly empty machine (wasteful, dim grey); Regular waits in a basket until a machine frees up, then runs a full load (orange). The machines then morph into a row of GPU chips: by day several sit empty, marked "spare, for the rush"; at night batch jobs fill every chip.

**Props:** `phase` keyframes: `expressAt`, `regularAt`, `fullLoadAt`, `compareAt` (two identical shirts + price tags), `morphAt` (machines → chips), `spareAt`, `fillAt`; `tags` ({express, regular} labels incl. price marks), `prices` ([a, b], e.g. ₹100 / ₹50), `chips` (count, default 6), `labels` (e.g. "Real-time = express", "Batch = regular"), `at`, `out`.

**Look**
- Machines: front-loader line drawings (2 px near-black, brand radius), round glass door; drum contents as simple shapes (folded shirt, clothes pile).
- Express = dim grey door tint + one shirt; Regular = orange load, full drum.
- Counter tags as Tag pills ("EXPRESS · 2 hours · ₹₹", "REGULAR · 2 days · ₹").
- GPU chips: square chips with pin ticks; empty = grey outline + "spare, for the rush" label; filled = orange with small job blocks.

**Motion**
- Drum spin: rotation with ease-in-out speed ramps, never linear constant spin at a cut.
- Basket → machine: clothes hop in with a spring, staggered 4 frames.
- Morph: each machine scales and squares into a chip (ease-in-out ~16 frames, stagger 4–6).
- Fill: job blocks pour into every chip (stagger), chips light orange.
- Exit with a fade on `out`.

**Sound:** `pop` on counters, `soft-pop` per clothes hop, `whoosh` on the morph, `tick` per chip fill (max every 4 frames).

**Gotchas**
- The analogy is a simplification (real-time requests are batched on GPUs too, with smaller batches and spare headroom): note it in the episode's `facts.md`.
- Prices are illustrative; label them so.
- No emojis; all drawings are line icons in the brand palette.

## Code

Saved: `components/code/LaundryToGpu/LaundryToGpu.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: Machine {size,load: one|full|none,spinAt,tone} · Shirt {size,color} · Basket {size} · GpuRow {x,y,at,out,n,busy,spareAt,fillAt,size}.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
