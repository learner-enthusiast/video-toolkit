# Composition (Remotion)

**Goal:** a Remotion project for this video only, built from the approved EDL, with only the components it needs.

**Setup**
- Create a fresh Remotion project in `projects/<name>/work/remotion/` (`npx create-video@latest`, blank TypeScript template). Install libraries here, per project.
- Add the official Remotion skills before writing code: `npx skills add remotion-dev/skills`. Follow them for APIs (`OffthreadVideo`, `Sequence`, `spring`, fonts, `staticFile`).
- Add `@remotion/google-fonts` and `simple-icons` (plus a v13 alias if an icon is missing from the latest release).
- Copy media into `public/` (clips, screenshots, clean voice WAV). Never reference `raw/` or `assets/` directly.

**Data in, not hard-coded**
- A build script turns the EDL into `public/data/timeline.json`: segments (source in/out → output frames), beats, and every kept word with its output time. Add `face.json` from `components/FaceTrackedCrop.md`.
- Every visual triggers on a word's output frame, found by phrase lookup (e.g. `at('indexes')`), never on a typed number.
- The voice plays as one continuous WAV laid out on the output timeline. Picture segments are cut separately, which makes J/L cuts easy.

**Build**
- Read `brand.md` into one `theme.ts` (colors, fonts, radius, shadow, border, FPS).
- Read the `script.md` cues. Build only the components they need, each from its `components/*.md` spec.
- Use one geometry module for the layout modes (TALK, SCREEN + BUBBLE, GFX + BUBBLE) on the 5% grid. Components take rects; they don't invent positions.
- Use one composition per deliverable (full, trailer 16:9, trailer 9:16) sharing the beats.
- Add a `music` prop (path or null, default null) at about -24 dB, ducked under speech.
- Synthesize SFX (pop, whoosh, key click, stamp, tick) with ffmpeg at low volume, or use clearly royalty-free sounds.

**Checks**
- `npx tsc --noEmit` passes. Render stills of 3–4 beats and look at them before any full render.

**Gotchas**
- Code in a 9:16 grid card (972 px wide) needs ≥ 28 px JetBrains Mono to read on a phone; 23–26 px looked fine in the editor and was unreadable at half scale. Wrap long lines and drop trailing comments instead of shrinking the font (`graphql-vs-rest` resolvers card).
- A still `N` frames after a trigger word can land in the next scene; pick still frames inside the scene's own window (between its trigger and the next scene's).
- Draw scenes once in a fixed logical card (972x900) and scale it into each aspect's card: one scene file serves 9:16 and 16:9.
