# Standing rules

Per-video code lives in `projects/<name>/work/`, never in the toolkit. Every video first checks the git-tracked `icons/` and `components/` (specs, approved Remotion code).

## House numbers
The only copy of these values; other files point here.
- **Reel length:** a reel is any video with final length ≤ 2:59 (or the prompt's limit). No shorter target, no "cut to one idea". Pauses tighten to 0.2–0.3 s.
- **Opener:** hook first (text hook on screen from frame 0, spoken hook lands within 3 s), then "Namoshkar!" (hands folded, smile, ~1 s hold, half-second pause).
- **Close:** one-line recap, then "Bye bye, sayonara!" with a wave.
- **Pace:** ~160 wpm. Max spoken words = 160 × minutes, minus room for clips (3 min ≈ 430–450). If over, cut points; never plan to speed up the script.
- **Loudness:** every deliverable is −16 ± 0.5 LUFS integrated, true peak ≤ −1.5 dBTP.
- **Music:** instrumental only; 20 dB under my voice (fail < 15 dB), 1.5 s fade-in, ducking holds 0.3 s pauses (`pipeline/music.md`).

## Icons
- Before downloading any icon or logo, `grep -i '<brand>' icons/icons.md`; reuse `icons/<File>` if listed. Else download the **official** version into `icons/logos/` (generic UI: `icons/ui/`) and add a row (source URL, license, date). Never Read the table whole (a hook blocks it; to edit it or `components/index-full.md`, Read ≤ 40 lines).
- Never save icons inside project folders (no `assets/logos/`, no `SOURCES.md`). Add the project to "Used in" every time a video uses an icon.
- Remotion reads them through `public/icons` (a symlink to `icons/`): `staticFile('icons/logos/<file>')`.

## Components
- Read `brand.md` + only the active `brands/brand-N.md`, then `components/index.md` (✓ = saved code), single rows with `grep -i '^| \[<Name>\]' components/index-full.md` (never Read it whole; never bulk-read `components/`), and only the specs (`components/specs/<Name>.md`) the scene table needs.
- ✓ components: import `shared/<Name>/<Name>` and set props; fit a variation with a new prop (old props keep working). New code only when nothing fits, spec first, inside `work/`. The library is the default, not a limit.
- After the final render, save every new or extended component that worked, in the same commit (`components/code/README.md`, Library rules).

## GPU
- Prefix GPU work with `gpu-run` (create it if missing, `pipeline/gpu.md`). Verify first: `gpu-run nvidia-smi` shows the card and torch reports `cuda.is_available() == True`.
- Never fall back to the CPU silently. Fix the cause, or stop and tell me.
- Exception: when the GPU is busy with another heavy job (a render, Whisper), run small side jobs (stills, thumbnails, rembg, contact sheets) on the CPU instead of waiting (Remotion: no `gpu-run`, `--gl=swangle`). Say so in the log and report. Never move the main render, transcription or final encodes to the CPU.

## Model routing
- **Sonnet** by default (`.claude/settings.json`). **Opus** only at creative checkpoints and visual QA, via the `creative-director` and `vision-qa` subagents; **Haiku** only as the boilerplate chain's last resort (`pipeline/model-routing.md`).
- Deterministic checks first (`tools/validate/vt_validate.py`, ffprobe, reports on disk). Never spend Opus on what a script can verify.

## Delegation
- `pipeline/delegation.md`. Run single commands yourself; only multi-file boilerplate from a final spec goes to the chain Copilot → Codex → cursor-agent → Haiku (check usage first, verify and log results).
- **Never delegate:** script, cuts, storyboard, creative take, layout states, sound map, `brand.md`, final component visuals, render settings, QA, anything on screen that hasn't been reviewed.
- **Heavy jobs** (voice cleaning, renders, Whisper, final encodes, video-inspect, installs): `tools/jobs/batch.sh` as a background command; no runner subagent, no polling, no changed settings.
- Pipeline scripts live in `tools/` and read `work/config/`; never copy or rewrite one in a project.

## Inspecting a video
- Any request to check, review, QA or "look at" a video, frames, captions or cuts: follow `pipeline/video-inspect.md` (When I ask you to look at a video). Run video-inspect first, never dump frames as images, and let `vision-qa` judge the images.
- Flags and VLM captions are leads, not verdicts. This file and `brand.md` win over any tool's or skill's defaults.

## Creative direction
- My script's visual cues say **what the viewer must understand**. They are the baseline, not a limit: bring your own take where it explains better or holds attention (process: `pipeline/composition.md`).
- **You may change:** how a cue is visualised, animation style, reveal order within a beat, the layout state of a beat (HEAD / FULL / SPLIT, `brand.md`) and its switch points (within a beat or two), extra graphics, emphasis, SFX, zooms.
- **You may NOT change:** spoken lines (never cut or reword any line), the facts or code shown, `brand.md`, the length limit, or the intent of a cue (what the viewer must understand).
- **Priority order:** `brand.md` → hard rules (length, never cut lines, never modify raw footage) → intent of my script cues → your creative take → skill defaults.

## Skills
- `CLAUDE.md` and `brand.md` win over any skill's defaults: colors, fonts, caption style, pacing, motion. A skill decides how to do a step, never how the video looks or feels. How the skills fit together: `SKILLS.md`.

## OpenAI
- Transcribe with local Whisper on the GPU. Never use the paid transcription API.
- If an OpenAI model is truly needed, pick a smaller, cheaper model, never the flagship, and tell me which one and why.
- Load keys from `.env`. Never print, log or copy them.

## Voice cleanup
- **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.**

## Installs
- CLIs and models are global or user-wide (apt, `npm i -g`, pipx or one shared user venv; models stay in `~/.cache`).
- Libraries (Remotion, simple-icons) are per project, inside `work/`. Exception: Playwright and its Chromium are global (`npm i -g playwright`, browsers in `~/.cache/ms-playwright`).

## Web captures
- Take every web screenshot and screen clip yourself with Playwright (`pipeline/web-capture.md`); I only supply what's private or behind my login, in `assets/`. Never alter a page's content.

## Workflow
- Never modify `raw/` or `assets/`. Work on copies in `work/`.
- For each paragraph, keep my LAST complete, clean take. Captions follow my actual words, not the script.
- Series episodes live in `projects/<playlist>/<NN>-<topic>/` and also obey `series/<playlist>.md` (`README.md`, Playlists).
- One session per stage: Prep, Cut, Compose, Deliver (`pipeline/stages.md`). Start from the session brief, never the whole log (`log.md` wins on conflict); end with a handoff in it. `/compact` only as a fallback.
- Stop at the rough cut (end of Cut) and wait for my OK before composing.
- Logs go to `work/logs/`, never into the chat. Report a summary.
- Every project turn gets a `log.md` entry (`pipeline/project-log.md`): hooks write the prompt, header, time and tokens; you write only **Changes / Decisions / Not done / Handoff**. Append only.
- When a video teaches us something, update the toolkit, not just the project: a one-line rule (≤ 200 chars) in the pipeline file's Gotchas, merged with duplicates; the story in `docs/lessons.md`.

## Quality bar
- Hide every jump cut: alternate 100% / ~108% framing, or cover the cut with a screen or graphic.
- One light grade for the whole video: fix white balance, lift shadows, add a little contrast, keep skin natural.
- Motion is spring or ease-in-out only, never linear. Stagger groups by 4–6 frames. Everything has an exit.
- 5% safe margins on one grid, and one radius, shadow and border everywhere (`brand.md`).
- Visuals trigger on the word timestamps of what I say, never on fixed times.
- No screenshot stays static for more than 3 s. No dead air. Use J/L cuts where they smooth the flow.
- Never cover my face. Never stretch me. No text cut off. Captions are always readable.
- Every visible hit that should sound gets one SFX from the kit (`pipeline/sound.md`).
- Deliver at House numbers loudness with A/V sync verified at the start, middle and end.

## Deliverables
- **Reels (see House numbers) are 9:16 only:** the main video (1080x1920), exactly one trailer (a short cut defined in the prompt IS the trailer; otherwise the default from `pipeline/trailer.md`; never both), an SRT for each, a cover/thumbnail (1080x1920) in `out/thumbnail/` plus the ChatGPT kit (`pipeline/thumbnail.md`), `<name>_social.json` (`pipeline/social-copy.md`), the carousel twin and the text posts (`pipeline/text-posts.md`). No 16:9 renders, stills or QA for a reel. Don't wait to be asked.
- Long-form (> 3:00): the 16:9 + 9:16 set in `/coding-video`.
- Hindi twins (`/hindi-twin`) ship only video, trailer and SRTs. Other reels also get a carousel twin (`pipeline/carousel.md`); other videos get text posts, extras (`pipeline/text-posts.md`).
- X Premium: **yes**.
- All final files go in `projects/<name>/out/`. Intermediates stay in `work/`.
