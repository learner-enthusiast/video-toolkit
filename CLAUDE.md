# Standing rules

Per-video code is built inside `projects/<name>/work/`, never in the toolkit. The toolkit holds two shared, git-tracked libraries that every video checks first: `icons/` (logos and icons) and `components/` (specs plus approved Remotion code).

## Icons
- Before downloading any icon or logo, `grep -i '<brand>' icons/icons.md` (never Read it whole). If it is listed, reuse `icons/<File>`. If not, download the **official** version into `icons/logos/` (generic UI icons: `icons/ui/`), add a row (source URL, license, today's date), then use it.
- Never save icons inside project folders (no `assets/logos/`, no `SOURCES.md`). Add the project to "Used in" every time a video uses an icon.
- Remotion reads them through `public/icons` (a symlink to `icons/`): `staticFile('icons/logos/<file>')`.

## Components
- Read order: `brand.md`, `components/index.md` (intent lists, ✓ = saved code), then single rows with `grep -i '^| \[<Name>\]' components/index-full.md` and only the component specs (`components/specs/<Name>.md`) the scene table needs. Never read `components/index-full.md` whole; never bulk-read `components/`.
- Compose: if `index.md` marks a name ✓ (`Code? ✓` in its row), import `shared/<Name>/<Name>` and set props (`src/shared` is a symlink to `components/code/`). If a needed variation fits a new prop, extend the library component and keep old props working. Write new code only when nothing fits. The library is the default, not a limit: Creative direction still applies.
- New component: write the spec first, then the code inside the project (`work/`).
- **Deliver: save components.** After the final render, every new or extended component that worked is cleaned up (variations through props, colors/fonts/radius/border/spacing from `components/code/theme.ts`, no video-specific text, data, timings or asset paths), saved to `components/code/<Name>/<Name>.tsx` with a `preview.png`, and recorded in its spec (`code:`, `props:`, `variants:`, `last_used:`), in its `components/index-full.md` row and with ✓ in `components/index.md`, in the same commit. Only approved code that rendered correctly in a finished video is saved. Update `last_used` on every component the video used.
- Maintenance: whenever a new component spec is created, add its row to `components/index-full.md` and its name to the matching intent group in `components/index.md`, in the same commit.
- Remotion upgrades: after changing the Remotion version, re-render every `preview.png`, fix breaks, update `components/code/REMOTION_VERSION`.

## GPU
- If `nvidia-smi` exists, create `~/bin/gpu-run`: an executable wrapper that exports `__NV_PRIME_RENDER_OFFLOAD=1` and `__GLX_VENDOR_LIBRARY_NAME=nvidia`, prepends the system lib dir to `LD_LIBRARY_PATH`, then `exec "$@"`. Put `~/bin` on PATH.
- Verify before any GPU work: `gpu-run nvidia-smi` shows the card, and torch reports `cuda.is_available() == True`.
- Encode with `h264_nvenc` when `ffmpeg -encoders` lists it.
- Never fall back to the CPU silently. Fix the cause, or stop and tell me. See `pipeline/gpu.md`.
- Exception: when the GPU is busy with another heavy job (a render, Whisper), run small side jobs (stills, thumbnails, rembg, contact sheets) on the CPU instead of waiting (Remotion: no `gpu-run`, `--gl=swangle`). Say so in the log and report. Never move the main render, transcription or final encodes to the CPU.

## Delegation
- You orchestrate. Two kinds of delegated work (`pipeline/delegation.md`): **low-stakes tasks** (scaffolding, renames, ffprobe reads, proxies, logo downloads into `icons/` + `icons/icons.md` rows, SRT wrapping, social JSON scaffold, `log.md`, boilerplate from a final spec) and **heavy jobs** (final renders, Whisper, final encodes, video-inspect runs, installs).
- **Never delegate:** script, cuts, storyboard, creative take, layout states, sound map, `brand.md`, final component visuals, render settings, QA, anything on screen that hasn't been reviewed.
- Low-stakes chain: Copilot → Codex → cursor-agent → Haiku. Check Copilot and Codex usage before each delegation (skip if low or unreadable). cursor-agent has no usage command: run a tiny **canary** before each use; on pass send exactly one small chunk, canary again before the next. CLIs run non-interactively, in the background, with a timeout, logging to `work/delegation/<NN>-<tool>-<task>.log`; on a limit/auth error or a hang, kill and re-run the chunk on the next tool. Verify every result yourself and record tool, usage and fallback in `log.md`.
- Heavy jobs never use the chain. You write the exact batch (`gpu-run`, flags, paths, timeouts); a Haiku runner launches each job detached, writes `work/jobs/<NN>-<job>.status`, stops and reports on any error. It never changes settings. You read the `.status` files and verify outputs; you don't tail logs.
- Vision goes through contact sheets and video-inspect reports, judged by the Opus vision subagent (`pipeline/video-inspect.md`), including final visual QA.

## Inspecting a video
Whenever a prompt asks to check, review, inspect, QA or "look at" a video, its frames, captions, cuts or edits:
1. Run video-inspect first (`pipeline/video-inspect.md`, as a heavy job via the Haiku runner, `pipeline/delegation.md`). Never dump frames as images.
2. Read `report.json` (`summary` and `flags` first).
3. The Opus vision subagent (`pipeline/video-inspect.md`) judges `contact_sheet.jpg`, the flagged frames and one keyframe per scene (framing, colour, pacing, quality) and returns text: `timestamp · what · severity · fix`. Read that, not the images (exceptions: the 3 approval stills, an ambiguous report).
4. Use `--thorough` for the final check before publishing.
5. Report issues with timestamps and a proposed fix for each.

Flags and VLM captions are leads, not verdicts. Judge them against this file and `brand.md`, which win over any tool's or skill's defaults.

## Creative direction
- The visual cues in my script describe **what the viewer must understand** at each moment. They are the baseline, not a limit. Bring your own take wherever it explains better or keeps viewers watching: a sharper metaphor animation, a better reveal order, a cleaner diagram, a stronger transition, sound design, pacing, a visual callback, a punchier end card.
- **You may change:** how a cue is visualised, animation style, reveal order within a beat, the layout state of a beat (HEAD / FULL / SPLIT, `brand.md`) and its switch points (within a beat or two), extra graphics, emphasis, SFX and music beds, zooms.
- **You may NOT change:** spoken lines (never cut or reword any line), the facts or code shown, `brand.md`, the ≤ 2:59 limit, or the intent of a cue (what the viewer must understand).
- **Priority order:** `brand.md` → hard rules (length, never cut lines, never modify raw footage) → intent of my script cues → your creative take → skill defaults.
- **Process:**
  1. In the storyboard step, add a **"Creative take"** list: each idea, the beat it touches, and one line on why it helps the explanation or retention.
  2. Small improvements (polish, timing, SFX, transitions): just do them and list them in the project log.
  3. Bigger changes (a different visual concept for a whole beat, reordering beats, a new recurring motif): show them in the 3 approval stills and wait for my OK.
  4. If my cue and your idea are close, use yours and mention mine as the fallback.
- Don't ask permission for every small choice. Be opinionated, then show me.

## Skill priority
- `CLAUDE.md` and `brand.md` win over any skill's defaults: colors, fonts, caption style, pacing and motion. A skill decides how to do a step, never how the video looks or feels.
- `/coding-video` and `/reel` use `/cut-video` as the cutting engine for take selection, and `/add-zooms` for punch-ins on emphasised words that also hide jump cuts.
- Use `/clipify` to turn a long video into reels. Each clip then goes through `/reel`.
- The Remotion skills drive how compositions are built. `frontend-design` sets taste only where `brand.md` leaves a choice open.
- `/scriptwriting` writes and tightens `script.md` (hooks, AI-phrase scan, timing). The template format and series rules win over it.
- Sources, licenses and local changes are listed in `SKILLS.md`.

## OpenAI
- Transcribe with local Whisper on the GPU. Never use the paid transcription API.
- If an OpenAI model is truly needed, pick a smaller, cheaper model, never the flagship, and tell me which one and why.
- Load keys from `.env`. Never print, log or copy them.

## Voice Recording Cleanup
- **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.** Originals in `raw/` stay untouched; each recording gets its own cleaned WAV and report (`--mode quality` only).

## Installs
- CLIs and models are global or user-wide (apt, `npm i -g`, pipx or one shared user venv; models stay in `~/.cache`).
- Libraries (Remotion, simple-icons) are per project, inside `work/`.

## Workflow
- Never modify `raw/` or `assets/`. Work on copies in `work/`.
- For each paragraph, keep my LAST complete, clean take. Captions follow my actual words, not the script.
- Playlists: a video may belong to a series. Episodes live in `projects/<playlist>/<NN>-<topic>/` (same structure as any project) and obey the tracked rules file `series/<playlist>.md` on top of this file and `brand.md`. See `README.md` (Playlists).
- Work in stages, one session each: Prep, Cut, Compose, Deliver (`pipeline/stages.md`). Start every stage from the latest `### Handoff` and open issues in `log.md` (`grep -n '### Handoff'`, read from the last match; never the whole log), then the project files the stage needs. End it with a handoff in `log.md`: decisions and reasons, rejected options, open issues, files produced, next steps. Use `/compact` only as a fallback.
- Stop at the rough cut (end of Cut) and wait for my OK before composing.
- Logs go to `work/logs/`, never into the chat. Report a summary.
- Every turn on a project gets a `log.md` entry (`pipeline/project-log.md`): hooks save my prompt, write the header and add time and tokens; you write only **Changes / Decisions / Not done / Handoff** under it. Never re-type the prompt or compute tokens. Append only.
- When a video teaches us something (a better setting, a gotcha), update the relevant toolkit `.md`, not just the project.
- When adding a lesson, add it to the matching Gotchas section as one line and merge duplicates; no stories.

## Quality bar
- Hide every jump cut: alternate 100% / ~108% framing, or cover the cut with a screen or graphic.
- One light grade for the whole video: fix white balance, lift shadows, add a little contrast, keep skin natural.
- Motion is spring or ease-in-out only, never linear. Stagger groups by 4–6 frames. Everything has an exit.
- 5% safe margins on one grid, and one radius, shadow and border everywhere (`brand.md`).
- Visuals trigger on the word timestamps of what I say, never on fixed times.
- No screenshot stays static for more than 3 s. No dead air. Use J/L cuts where they smooth the flow.
- Never cover my face. Never stretch me. No text cut off. Captions are always readable.
- Every visible hit that should sound gets one SFX from the kit (`pipeline/sound.md`); music, if any, ducks under my voice.
- Deliver at -16 LUFS with A/V sync verified at the start, middle and end.

## Deliverables
- **Reels (final length ≤ 2:59) are 9:16 only, start to finish:** the main video in 9:16 (1080x1920), exactly one trailer in 9:16 (a short cut defined in the prompt IS the trailer; otherwise the default from `pipeline/trailer.md`; never both), an SRT for each, a 9:16 cover/thumbnail (1080x1920) in `out/thumbnail/` plus the ChatGPT kit (`pipeline/thumbnail.md`), `<name>_social.json` (`pipeline/social-copy.md`) and the carousel twin. No 16:9 renders, stills, QA or layouts for a reel. Don't wait to be asked.
- Long-form (> 3:00) keeps 16:9 + 9:16 as before: every long-form video ships with the main video, exactly one trailer cut rendered in landscape 16:9 and portrait 9:16 (a short cut defined in the prompt IS the trailer; otherwise the default from `pipeline/trailer.md`; never both), an SRT for each, thumbnails in `out/thumbnail/` along with a ChatGPT kit (up to 3 static assets plus a ready prompt and a template for my own) (`pipeline/thumbnail.md`), and `<name>_social.json` with ready-to-paste titles, posts and hashtags for LinkedIn, X, Instagram, Facebook, Threads and YouTube (`pipeline/social-copy.md`). Don't wait to be asked.
- Every 9:16 reel delivery also produces a carousel twin in `projects/<name>/out/carousel/`, built from that project's `script.md` (`pipeline/carousel.md`). `/carousel <project>` can also be run on its own for older projects.
- Keep X posts within 280 chars unless I say I have X Premium.
- All final files go in `projects/<name>/out/`. Intermediates stay in `work/`.
