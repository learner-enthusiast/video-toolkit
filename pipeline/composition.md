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
- Read the `script.md` cues. Choose components from `components/INDEX.md` first, never bulk-read `components/`. Build only the components the cues need, each from its `components/*.md` spec.
- **Storyboard first.** Write `work/storyboard.md`: one line per beat with its layout state (HEAD / FULL / SPLIT, from the script's `[mm:ss–mm:ss | STATE]` tags, moved if another state explains better) and the visual. Add a **Creative take** list: each idea, the beat it touches, one line on why it helps the explanation or retention (`CLAUDE.md`, Creative direction). Small improvements are just done and logged; bigger ones (a different visual concept for a whole beat, reordered beats, a new recurring motif) are shown in 3 approval stills, and I wait for my OK.
- Use one geometry module for the three layout states (HEAD, FULL, SPLIT; `components/layout-states.md`) on the 5% grid; 16:9 TALK / SCREEN + BUBBLE map onto HEAD / SPLIT-style states the same way. Components take rects; they don't invent positions.
- Be a co-director, not an executor: the script's cues are the baseline; bring a better visual take where it explains better, within the limits in `CLAUDE.md`.
- Use one composition per deliverable (full, trailer 16:9, trailer 9:16) sharing the beats.
- Add a `music` prop (path or null, default null) at about -24 dB, ducked under speech.
- Synthesize SFX (pop, whoosh, key click, stamp, tick) with ffmpeg at low volume, or use clearly royalty-free sounds.

**Checks**
- `npx tsc --noEmit` passes. Render stills of 3–4 beats and look at them before any full render.

**Gotchas**
- Code in a 9:16 grid card (972 px wide) needs ≥ 28 px JetBrains Mono to read on a phone; 23–26 px looked fine in the editor and was unreadable at half scale. Wrap long lines and drop trailing comments instead of shrinking the font (`graphql-vs-rest` resolvers card).
- A still `N` frames after a trigger word can land in the next scene; pick still frames inside the scene's own window (between its trigger and the next scene's).
- Draw scenes once in a fixed logical card (972x900) and scale it into each aspect's card: one scene file serves 9:16 and 16:9.
- A dark question card with a kicker ("Today's interview question:") must start TYPING after the words the kicker already shows, but the kicker itself lands on the first spoken word. Typing from the first word duplicated the kicker; delaying both left the card empty for 1.4 s (`rate-limiter`: `kickerAt` prop on Question).
- `at()` throws only at render time, so `tsc` passing proves nothing about phrases. Render one still per scene (a bundle-once still script, half scale) right after writing the scenes; it catches missing phrases and layout collisions in one pass.
- "HEAD, dark style" punch on a portrait talking head (`ag-ui`): keep me full frame, dimmed (`brightness(0.38) saturate(0.6)` via the layout blend), and put the punch graphic on the wall above my head (y ≈ 96–500). Hiding me (bloom-filter's DARK) loses the HEAD beat the brief asked for.
- Whisper on the cut voice parks short words ("a" before "spinner") in the preceding pause, up to 1 s early; video-inspect's `caption_desync` catches it. Pin it from the energy envelope in `build_words.py`, and recheck any trailer segment that starts there.
- A wordmark logo inside a small UI element (a sign-in button, a 56 px lane header) shrinks to unreadable; use the company's official mark there (Google's four-colour "G", saved as `google-g.svg`) and keep the wordmark for logo walls (`oidc`).
- An SVG whose `width`/`height` don't match its `viewBox` aspect (`oidc` `openid.svg`: 320×120 around a portrait viewBox) renders at its declared box. Size the tile to the declared aspect; editing the attributes clipped the wordmark to "Op".
- Lane headers that start larger for an intro beat overlap once three share a 972 px card; move them (spring the y) but keep their size (`SequenceFlow`).
- Hyphenated and possessive words are one token in the word data ("platform-issued", "company's", MFA-merged "a one-time"), so `at("or a platform")` or `at("lets the company")` throws at render time. Write the token as spoken (`at("a-one-time")`, `at("lets the company's")`) and run a phrase check over every `at("…")` against `timeline.json` before any still render (`oidc` `remotion/scripts/check_phrases.py`): one crash costs a whole bundle + render pass.
- A wide wordmark (MCP 1338×195) in a square logo slot shrinks to a hairline. Give wide logos a wide box (`logoW`), never a square.
- Rows scrolling out of a clipped list leave half-chips under the header; fade the list's top edge with a CSS mask (`linear-gradient(to bottom, transparent 0, black 56px)`).
- Spreading `style={{ opacity: undefined }}` into a component whose own `style` sets opacity from its spring wipes the entrance (React drops the key). Wrap the component in a div for extra opacity or filter instead.
- An unscoped `at("its client id")` resolves to the FIRST time I say it: in `oidc` Part 2 that was the login step 2 line, 1 min early, so a later scene showed a row before I spoke it. Scope repeated phrases to their beat (`at(phrase, from)`); the phrase check lists every unscoped phrase spoken more than once.
- Remotion composition ids allow only a-z, A-Z, 0-9 and `-`: `Short_p1` throws at bundle time (validateCompositionId), and every still/render in that batch dies with it. Use `Short-p1`.
- Word data stores number words as digits ("one" → `1`, "five" → `5`, "fifty" → `50`), so `at("best one first")` and `at("two indexes")` throw. Apply the same number map inside `at()` and the phrase check, and in the highlight-phrase matcher, or highlight words like "top five" silently never light up (`rag-pipeline`).
- Running canvas (`components/PipelineCanvas.md`): stations have transparent backgrounds, so connectors drawn centre-to-centre cut through titles and gauges. Draw them edge-to-edge inside the gaps.
- The phrase lookup's number map turns "Three" into "3", so `at('Three')` matched "under 3 minutes" in the hook and idea 3's card rendered over every scene from 0:09 on (`scion`). Anchor numbered list items with the next word (`at('Three source')`) or a `from` frame.
- An element whose `style` sets a positioning `transform` (`translate(-50%,-50%)`, a flip) and then spreads `enter()`/`popIn()` loses the positioning: the entrance transform overwrites it, and the "Works offline" badge slid half off-frame (`scion`). Put the positioning transform on an outer div and the entrance on an inner one.
- Check the contact sheets for scenes whose first visual waits for a later word: a SPLIT card sat nearly empty for 1–2 s at the start of 4 scenes (`scion`). Bring the scene's base layout in on the scene's first word; trigger only the details on later words.
- A 10-frame overlap between card scenes (old one fading while the new one springs in) ghosts a busy card under the next one on the beat sheet (`jwt-is-dead`: PublicVerify under TypedKeyGate). Use a 2-frame overlap.
- An end-card links panel "over my chest" at y 1250 covered my chin and the mic on `vectorless-rag` (I sat lower in frame than on `bloom-filter`). Place it from the face track: top edge ≥ face centre y + 0.75 × face width (y 1340 here), and check the last frame's still.
- A sentence that starts a dark HEAD/FULL punch needs its first word's time verified against CTC before the first render (see `pipeline/transcribe.md`, sentence-first words): state switches trigger on those words more than on any others.
- Stamps have an opaque panel: a 78 px BLOCKED stamp hid the whole sedan it was stamping. Size the stamp to ≤ 60% of the object's width and land it on the lower half so the object still reads.
- Step badges (①②③) on a full-width code card: anchor them on a SHORT line of each step (`res.flushHeaders();`, `stream: true,`, the `for await` line) and light the long line with a highlight instead. A badge at the right edge of a 52+ char line at 28 px covered its last characters (`sdai-01-streaming` SSE card).
- Something that "drops" from one panel into another (tokens falling from a server box onto a phone) must be rendered AFTER the target panel in the JSX: an opaque panel drawn later hid the falling chips completely (`sdai-01-streaming` two-lanes scene).
