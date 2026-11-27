# Component code library

Approved Remotion code, one folder per component, linked to its spec in `../specs/<Name>.md`. Registry: `../index.md` (✓ marks) and `../index-full.md` (rows; grep, never read whole).

- `theme.ts` (the active brand's tokens), `themes/` (one file per brand, docs in `/brands/`), `fonts.ts`, `anim.ts` (spring / ease-in-out helpers), `glyphs.tsx` (shared small drawings, `Logo`).
- `REMOTION_VERSION`: the Remotion version these components were rendered on.
- `<Name>/<Name>.tsx` + `<Name>/preview.png` (default look). Variations are props, not copies.
- `_preview/`: harness with one composition per component (`Preview-<Name>`).

**Use in a project:** `src/shared` is a symlink to this folder, `public/icons` a symlink to `/icons`. Import `../shared/Tag/Tag`. (Setup: `pipeline/composition.md`.)

**Render a preview** (from any project's `work/remotion/`, through `gpu-run`; previews render in Brand 1 by default, set `REMOTION_BRAND=2` or `3` in `.env` for the others; `brand2/` and `brand3/` pieces keep a preview in their own brand):
`gpu-run npx remotion still src/shared/_preview/index.ts Preview-<Name> ../../../../components/code/<Name>/preview.png --frame=60` (adjust the relative path).

**Rules:** no hard-coded colors, fonts, radius, border or spacing (use `theme.ts`); no video-specific text, data, timings or asset paths (props); each `.tsx` starts with a comment pointing to its spec; change code, update the spec in the same commit; save only code that rendered correctly in a finished video.

## Library rules
- **One shared component per idea** in `components/code/<Name>/`: every colour, font, border, radius and shadow comes from the active theme, with no hard-coded colours and no brand checks. Props are content only (text, numbers, frames, rects, logos), never a brand look (existing `dark` props keep working). `brand2/` and `brand3/` hold only signature pieces; if one is needed elsewhere, move it to shared. Never two copies.
- Each `index-full.md` row lists the props and the brands it is tested in. One `preview.png` per component (Brand 1), one contact sheet per brand in `docs/brands/`.
- **Deliver: save components.** After the final render, every new or extended component that worked is cleaned up (variations through props, colors/fonts/radius/border/spacing from `components/code/theme.ts`, no video-specific text, data, timings or asset paths), saved to `components/code/<Name>/<Name>.tsx` with a `preview.png`, and recorded in its spec (`code:`, `props:`, `variants:`, `last_used:`), in its `components/index-full.md` row and with ✓ in `components/index.md`, in the same commit. Only approved code that rendered correctly in a finished video is saved. Update `last_used` on every component the video used.
- Maintenance: whenever a new component spec is created, add its row to `components/index-full.md` and its name to the matching intent group in `components/index.md`, in the same commit.
- Remotion upgrades: after changing the Remotion version, re-render every `preview.png`, fix breaks, update `components/code/REMOTION_VERSION`.
