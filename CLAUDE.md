# Standing rules

This repo is instructions only. Build code per video inside `projects/<name>/work/`, never in the toolkit itself.

## Components
- Read order: `CLAUDE.md`, `brand.md`, `components/INDEX.md`, then only the component specs the scene table needs.
- Never bulk-read `components/`. Read `INDEX.md`, then open only the specs used in this video's scene table.
- Maintenance: whenever a new component spec is created (including by a video prompt's new-component section), add its row to `components/INDEX.md` and to the matching intent group in the same commit.

## GPU
- If `nvidia-smi` exists, create `~/bin/gpu-run`: an executable wrapper that exports `__NV_PRIME_RENDER_OFFLOAD=1` and `__GLX_VENDOR_LIBRARY_NAME=nvidia`, prepends the system lib dir to `LD_LIBRARY_PATH`, then `exec "$@"`. Put `~/bin` on PATH.
- Verify before any GPU work: `gpu-run nvidia-smi` shows the card, and torch reports `cuda.is_available() == True`.
- Encode with `h264_nvenc` when `ffmpeg -encoders` lists it.
- Never fall back to the CPU silently. Fix the cause, or stop and tell me. See `pipeline/gpu.md`.
- Exception: when the GPU is busy with another heavy job (a render, Whisper), run small side jobs (stills, thumbnails, rembg, contact sheets) on the CPU instead of waiting (Remotion: no `gpu-run`, `--gl=swangle`). Say so in the log and report. Never move the main render, transcription or final encodes to the CPU.

## Delegation
- You orchestrate. Hand shell work (probing, ffmpeg, Whisper, Python, installs, renders) to a Haiku subagent as one batch of exact commands per step (`pipeline/delegation.md`). Don't run it from the main session.
- Haiku only runs the commands you wrote. It never chooses takes, edits a command, or fixes an error. It saves full output to `work/logs/<step>.log` and returns exit codes, key numbers, and every error or warning verbatim.
- If anything fails or looks off, read the log and debug it yourself; you may run commands while debugging.
- Code helpers, in this order: try `cursor-agent` first; if it is not installed, is refused, or fails, use GitHub Copilot CLI (`copilot -p "<spec>"`). Give either one exact component specs (props, geometry, timing) to write code from.
- Hand a helper only work that can't lower video quality (boilerplate, data files, helper scripts from exact specs). Claude does the heavy lifting: visual components, timing, layout, and reviews every line a helper writes before it's used.
- Judgment, vision, take selection, QA and every creative or quality decision stay with you.
- Vision goes through contact sheets and video-inspect reports (`pipeline/video-inspect.md`). A subagent may pre-screen, but you do the final visual QA before deliverables by looking at the sheets yourself.

## Inspecting a video
Whenever a prompt asks to check, review, inspect, QA or "look at" a video, its frames, captions, cuts or edits:
1. Run video-inspect first (`pipeline/video-inspect.md`, as a Haiku batch). Never dump frames as images.
2. Read `report.json` (`summary` and `flags` first) and `contact_sheet.jpg`.
3. Open with Read only the flagged frames plus one keyframe per scene, to judge framing, colour, pacing and visual quality.
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
- Sources, licenses and local changes are listed in `SKILLS.md`.

## OpenAI
- Transcribe with local Whisper on the GPU. Never use the paid transcription API.
- If an OpenAI model is truly needed, pick a smaller, cheaper model, never the flagship, and tell me which one and why.
- Load keys from `.env`. Never print, log or copy them.

## Installs
- CLIs and models are global or user-wide (apt, `npm i -g`, pipx or one shared user venv; models stay in `~/.cache`).
- Libraries (Remotion, simple-icons) are per project, inside `work/`.

## Workflow
- Never modify `raw/` or `assets/`. Work on copies in `work/`.
- For each paragraph, keep my LAST complete, clean take. Captions follow my actual words, not the script.
- Playlists: a video may belong to a series. Episodes live in `projects/<playlist>/<NN>-<topic>/` (same structure as any project) and obey the tracked rules file `series/<playlist>.md` on top of this file and `brand.md`. See `README.md` (Playlists).
- Work in stages, one session each: Prep, Cut, Compose, Deliver (`pipeline/stages.md`). Start every stage by reading `log.md` and the project files. End it with a handoff in `log.md`: decisions and reasons, rejected options, open issues, files produced, next steps. Use `/compact` only as a fallback.
- Stop at the rough cut (end of Cut) and wait for my OK before composing.
- Logs go to `work/logs/`, never into the chat. Report a summary.
- At the end of every turn on a project, append an entry to `projects/<name>/log.md`: date and time, my prompt verbatim, what changed, how long it took, and token usage (`pipeline/project-log.md`). Append only.
- When a video teaches us something (a better setting, a gotcha), update the relevant toolkit `.md`, not just the project.

## Quality bar
- Hide every jump cut: alternate 100% / ~108% framing, or cover the cut with a screen or graphic.
- One light grade for the whole video: fix white balance, lift shadows, add a little contrast, keep skin natural.
- Motion is spring or ease-in-out only, never linear. Stagger groups by 4–6 frames. Everything has an exit.
- 5% safe margins on one grid, and one radius, shadow and border everywhere (`brand.md`).
- Visuals trigger on the word timestamps of what I say, never on fixed times.
- No screenshot stays static for more than 3 s. No dead air. Use J/L cuts where they smooth the flow.
- Never cover my face. Never stretch me. No text cut off. Captions are always readable.
- Deliver at -16 LUFS with A/V sync verified at the start, middle and end.

## Deliverables
- Every video ships with: the main video, exactly one trailer cut rendered in landscape 16:9 and portrait 9:16 (a short cut defined in the prompt IS the trailer; otherwise the default from `pipeline/trailer.md`; never both), an SRT for each, thumbnails in `out/thumbnail/` along with a ChatGPT kit (up to 3 static assets plus a ready prompt and a template for my own) (`pipeline/thumbnail.md`), and `<name>_social.json` with ready-to-paste titles, posts and hashtags for LinkedIn, X, Instagram, Facebook, Threads and YouTube (`pipeline/social-copy.md`). Don't wait to be asked.
- Every 9:16 reel delivery also produces a carousel twin in `projects/<name>/out/carousel/`, built from that project's `script.md` (`pipeline/carousel.md`). `/carousel <project>` can also be run on its own for older projects.
- Keep X posts within 280 chars unless I say I have X Premium.
- All final files go in `projects/<name>/out/`. Intermediates stay in `work/`.
