---
code: components/code/brand2/AlertFlash/AlertFlash.tsx
preview: components/code/brand2/AlertFlash/preview.png
props: "word, sub, at, out, icon, size"
variants: "default warning icon or custom"
last_used: "—"
---
# AlertFlash

**Purpose:** the failure punch: "POWER FAILURE", "TIMEOUT".

**Props:** `word`, `sub`, `at`, `out`, `icon`, `size`.

**Look**
- Full frame on `punchBg`: an icon, a big caps word in `alert`, a small mono subline.

**Motion**
- A 2-frame flicker in (on, off, on) with a slight settle in scale; the subline follows 6 frames later.
- Exit: fade over 8 frames.

**Gotchas**
- At most once per video, only for a real failure.
- One or two short words; lower `size` for longer ones.

## Code

Saved: `components/code/brand2/AlertFlash/AlertFlash.tsx` (preview: `preview.png`, rendered in Brand 2). A Brand 2 signature piece: import `shared/brand2/AlertFlash/AlertFlash`. If another brand needs it, move its folder up to the shared library, next to the other shared components; never copy. Brand values come from `components/code/theme.ts`.

- Code props: word, sub, at, out, icon, size.
- New for the three-brand setup; not yet used in a finished video.
