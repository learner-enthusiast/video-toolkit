# Composition (Remotion)

**Goal:** a Remotion project for this video only, built from the approved EDL, with only the components it needs.

**Setup**
- Scaffold with `vt-python tools/scaffold_remotion.py projects/<name> --aspect 9:16` (reel) or `--aspect 16:9` (long-form), then `npm i` inside `work/remotion/`. Or create manually with `npx create-video@latest` if the scaffold is insufficient.
- Add the official Remotion skills before writing code: `npx skills add remotion-dev/skills`. Follow them for APIs (`OffthreadVideo`, `Sequence`, `spring`, fonts, `staticFile`).
- Add `@remotion/google-fonts` and `simple-icons` (plus a v13 alias if an icon is missing from the latest release).
- Copy media into `public/` (clips, screenshots, clean voice WAV). Never reference `raw/` or `assets/` directly.

**Data in, not hard-coded**
- A build script turns the EDL into `public/data/timeline.json`: segments (source in/out → output frames), beats (by script beat ID: `### B07` headings in `caption_text.md`, in output order), and every kept word with its output time. Add `face.json` from `components/specs/FaceTrackedCrop.md`.
- Every visual triggers on a word's output frame, never on a typed number. Scenes call `cue('B07.tableScan')` (`src/lib/cues.ts`); `beatAt('B07', 0.4)` covers a moment no word marks. No spoken words in TSX, and saved components take frames as props.
- Cue phrases live in `public/data/cues.json`: `{"B07.tableScan": {"beat": "B07", "phrase": "full table"}}`, with optional `from` (a frame or `"B07.other+5"`) and `"edge": "end"`.
- After every timeline step, from `work/remotion/`: `vt-python tools/captions/resolve_cues.py --src src`. It writes `cue_frames.json` and fails on a missing or ambiguous phrase. Projects made before named cues keep `at()` and `tools/captions/check_phrases.py`.
- The voice plays as one continuous WAV laid out on the output timeline. Picture segments are cut separately, which makes J/L cuts easy.

**Build**
- Read `brand.md` into one `theme.ts` (colors, fonts, radius, shadow, border, FPS).
- Read the `script.md` cues. Choose components from `components/index.md` first (single rows: `grep -i '^| \[<Name>\]' components/index-full.md`; never read `index-full.md` whole), never bulk-read `components/`. For each component the cues need: if `index.md` marks it ✓, import `shared/<Name>/<Name>` (`src/shared` → `components/code/`) and set props, extending the library component with a new prop (old props keep working) when a variation fits; otherwise write its spec (`components/specs/<Name>.md`) first, then the code in the project. The library is the default, not a limit (`CLAUDE.md`, Creative direction).
- Wire the shared libraries when creating the Remotion project: symlink `public/icons` → `icons/` and `src/shared` → `components/code/` (relative links), add `Config.overrideWebpackConfig((c) => ({...c, resolve: {...c.resolve, symlinks: false}}))` to `remotion.config.ts` and `"preserveSymlinks": true` to `tsconfig.json`, so shared code resolves `remotion` from the project's `node_modules`. Use the Remotion version in `components/code/REMOTION_VERSION`.
- **Storyboard first.** At Compose start, spawn the `creative-director` subagent (`.claude/agents/creative-director.md`, Opus) with the project path; the session itself stays on the production tier. Read what it wrote, and send the 3 approval stills back to it for review before showing me. It writes `work/storyboard.md`: one line per beat with its layout state (HEAD / FULL / SPLIT, from the script's `[mm:ss–mm:ss | STATE]` tags, moved if another state explains better) and the visual. It includes the **Creative take** list (Creative direction process, below).
- Write the punch/ratchet map with `/add-zooms` from the word timestamps: it places the ~108% framing that hides each jump cut, applied in the composition. No Ken Burns from add-zooms; slow pushes are Remotion ease-in-out. For long-form HEAD framing, say whether you crop or use `PresenterSplit` (`components/specs/layout-states.md`) and why.
- Use one geometry module for the three layout states (HEAD, FULL, SPLIT; `components/specs/layout-states.md`) on the 5% grid. A reel (≤ 2:59) is laid out for 9:16 only: no 16:9 layout, no dual-aspect geometry, no landscape variant. Long-form (> 3:00) only: 16:9 TALK / SCREEN + BUBBLE map onto HEAD / SPLIT-style states the same way. Components take rects; they don't invent positions.
- Use one composition per deliverable sharing the beats. Reel: main 9:16 and trailer 9:16. Long-form: main 16:9, trailer 16:9, trailer 9:16.
- Sound: follow `pipeline/sound.md`.

## Creative direction process
What may and may not change: `CLAUDE.md` → Creative direction.
- Bring your own take wherever it explains better or keeps viewers watching: a sharper metaphor animation, a better reveal order, a cleaner diagram, a stronger transition, sound design, pacing, a visual callback, a punchier end card.
- **Process:**
  1. In the storyboard step, add a **"Creative take"** list: each idea, the beat it touches, and one line on why it helps the explanation or retention.
  2. Small improvements (polish, timing, SFX, transitions): just do them and list them in the project log.
  3. Bigger changes (a different visual concept for a whole beat, reordering beats, a new recurring motif): show them in the 3 approval stills and wait for my OK.
  4. If my cue and your idea are close, use yours and mention mine as the fallback.
- Don't ask permission for every small choice. Be opinionated, then show me.

**Checks**
- Every stills or sheet check in this file runs through the vision subagent (`pipeline/video-inspect.md`, Vision subagent); only the 3 approval stills are opened in the main session.
- `npx tsc --noEmit` passes. Render stills of 3–4 beats and have them checked before any full render.

**Gotchas**
- Code in a 972 px card is ≥ 28 px JetBrains Mono: wrap lines and drop trailing comments, don't shrink.
- Pick still frames inside the scene's own window, not just N frames after a trigger.
- Draw each scene once in a logical 972x900 card and scale it into every aspect.
- A typing question card starts after the kicker's words, and the kicker lands on the first spoken word (`kickerAt`).
- `tsc` doesn't check cue phrases: after writing scenes, run `resolve_cues.py --src src`, then render one half-scale still per scene from a single bundle.
- Dark HEAD punch: keep me full frame, dimmed (`brightness(0.38) saturate(0.6)`), graphic above my head (y ≈ 96–500).
- Whisper can put short words up to 1 s early in a pause: pin from the envelope (`pins`) and recheck trailer segments starting there.
- Small UI slots take the official mark, not the wordmark; wide wordmarks get a wide box (`logoW`), never a square.
- SVG `width`/`height` that don't match its `viewBox` aspect: size the tile to the declared aspect; don't edit the attributes.
- Oversized intro lane headers overlap once three share a card: move them, keep their size.
- Hyphenated and possessive words are one token: write cue phrases as spoken, and run `resolve_cues.py` before any still.
- Fade a clipped scrolling list's top edge with a CSS mask, or half-chips show under the header.
- Never spread `opacity: undefined` into a spring-animated component: wrap it in a div for extra opacity or filter.
- A cue is scoped to its beat; a phrase repeated inside the beat needs a longer phrase or `from`.
- Remotion composition ids allow only a-z, A-Z, 0-9 and `-`; an underscore fails the whole batch.
- Number words are digits in word data: `resolve_cues.py` maps them, and the highlight matcher needs the same map; anchor list numbers with the next word.
- `PipelineCanvas` stations are transparent: draw connectors edge-to-edge in the gaps.
- Put a positioning `transform` on an outer div and `enter()`/`popIn()` on an inner one, or the entrance overwrites it.
- Bring each scene's base layout in on its first word; trigger only details on later words.
- Overlap card scenes by 2 frames, not 10 (ghosting).
- Place the end-card links panel from the face track: top ≥ face centre y + 0.75 × face width; check the last frame.
- Verify against CTC the first word of any sentence that triggers a dark punch or state switch.
- Stamps are opaque: ≤ 60% of the object's width, on its lower half.
- Anchor step badges on a short code line and highlight the long one.
- An element dropping into a panel renders after that panel in JSX, or the opaque panel hides it.
- A code cue with no spoken words: put the code under the preceding diagram and light lines on the words that name them.
- If a to-scale bar hides the point, show a labelled zoom, never fake proportions; check the script's on-screen arithmetic.
- A dark FULL scene waiting on a late number starts empty: show the counter at zero from its first frame.
- Under the end card, freeze the out-point frame (`<Freeze>` at `srcOut − 1`) and dim it; never play past it.
- Set `fontVariantLigatures: 'none'` on every code and terminal span (done in `CodeCard`).
- `renderStill` bundle scripts ignore `remotion.config.ts`: pass the same `webpackOverride` (`resolve.symlinks: false`) to `bundle()`.
- Key a dark punch that starts on a cut to the segment boundary (`TL.segments[i].from`).
- `FootCap` is one line: ≤ 40 characters at 34 px (≤ 30 at 44 px); sample a still after each footer's trigger.
