# Standing rules

This repo is instructions only. Build code per video inside `projects/<name>/work/`, never in the toolkit itself.

## GPU
- If `nvidia-smi` exists, create `~/bin/gpu-run`: an executable wrapper that exports `__NV_PRIME_RENDER_OFFLOAD=1` and `__GLX_VENDOR_LIBRARY_NAME=nvidia`, prepends the system lib dir to `LD_LIBRARY_PATH`, then `exec "$@"`. Put `~/bin` on PATH.
- Verify before any GPU work: `gpu-run nvidia-smi` shows the card, and torch reports `cuda.is_available() == True`.
- Encode with `h264_nvenc` when `ffmpeg -encoders` lists it.
- Never fall back to the CPU silently. Fix the cause, or stop and tell me. See `pipeline/gpu.md`.

## Delegation
- You orchestrate. Hand shell work (probing, ffmpeg, installs, renders) to a Haiku subagent with exact commands and expected output.
- If `cursor-agent` is installed, give it exact component specs (props, geometry, timing) to write code from.
- Judgment, vision (looking at frames and screenshots), take selection and QA stay with you.

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
- Stop at the rough cut and wait for my OK before composing.
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
- Every video ships with: the main video, two trailers (landscape 16:9 and portrait 9:16, see `pipeline/trailer.md`), an SRT for each, thumbnails in `out/thumbnail/` along with a ChatGPT kit (up to 3 static assets plus a ready prompt and a template for my own) (`pipeline/thumbnail.md`), and `<name>_social.json` with ready-to-paste titles, posts and hashtags for LinkedIn, X, Instagram, Facebook, Threads and YouTube (`pipeline/social-copy.md`). Don't wait to be asked.
- Keep X posts within 280 chars unless I say I have X Premium.
- All final files go in `projects/<name>/out/`. Intermediates stay in `work/`.
