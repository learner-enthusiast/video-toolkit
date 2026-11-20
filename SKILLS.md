# Skills

Third-party skills used by this toolkit, at project level in `.claude/skills/`. `CLAUDE.md` and `brand.md` win over every skill's defaults (see "Skill priority" in `CLAUDE.md`).

| Skill | Source | License | Added | In git? |
|---|---|---|---|---|
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) `skills/frontend-design` @ `dbd4588` | Apache 2.0 (`LICENSE.txt`) | 2026-10-27 | Yes (vendored) |
| `add-zooms` | [louisedesadeleer/add-zooms](https://github.com/louisedesadeleer/add-zooms) @ `34db910` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
| `cut-video` | [louisedesadeleer/cut-video](https://github.com/louisedesadeleer/cut-video) @ `a5a87a6` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
| `clipify` | [louisedesadeleer/clipify](https://github.com/louisedesadeleer/clipify) @ `5f6b75e` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
| `scriptwriting` | [salomonMuriel/media-production-skills](https://github.com/salomonMuriel/media-production-skills) `skills/scriptwriting` @ `6ba4284` | MIT (`LICENSE`) | 2026-11-18 | Yes (vendored) |
| `remotion-*` (12 skills) | [remotion-dev/skills](https://github.com/remotion-dev/skills) | None stated (no LICENSE file, no `license` in `package.json`) | 2026-10-27 | No. Install per clone with `npx skills add remotion-dev/skills` (see `/setup`); gitignored |

Upstream license files are kept inside each vendored skill folder.

**Toolkit skills** (written here, not third-party): `/setup`, `/new-video`, `/coding-video`, `/reel`, and `/carousel` (turns a reel's `script.md` into a 6–8 slide 1080x1350 Instagram carousel with PDF, caption and alt text).

## What I changed

**All three video skills (add-zooms, cut-video, clipify)** now start with a "Linux adaptation (video-toolkit)" section, and the commands below it were rewritten:
- `brew` → `apt` / `/setup`, `open` → `xdg-open`, `-hwaccel videotoolbox` → `-hwaccel cuda`.
- `libx264` / `h264_videotoolbox` → `h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0`.
- `whisper` / `mlx_whisper` → `gpu-run whisper-ctranslate2 --device cuda --compute_type float16` (faster-whisper).
- `python3` → `vt-python` (the shared user venv).
- `/tmp/...` and `<source_dir>/..._out/` → `projects/<name>/work/<skill>/`, because `raw/` is read-only.

**add-zooms**
- Encodes on the GPU by printing the filtergraph (`zoom_lib.py filter`) and running ffmpeg with NVENC, because `zoom_lib.py render` hard-codes libx264. The scripts are unchanged.
- Uses punches and ratchets only. Ken Burns is skipped (the engine ramps it linearly, which CLAUDE.md bans); slow pushes are done in Remotion with ease-in-out.
- Left out `install.sh` (it symlinks into the global `~/.claude/skills`) and the 4 MB `docs/comparison.gif`. README updated to match.

**cut-video**
- MFA is no longer auto-installed via brew + conda. `/setup` installs it once (Miniforge in batch mode, conda env `mfa`, `~/bin/mfa` launcher, `english_mfa` models), and the skill checks for it and stops if it's missing.
- The Tella-upload cross-check is replaced with a second local ASR. Nothing is uploaded.
- "Render without approval" is kept, but the toolkit's rough-cut checkpoint still applies.
- The pause lengths in `pipeline/take-selection.md` (and `/reel`) override the skill's gap table. Default tone for tutorials is `balanced`.

**clipify**
- Choose components from `components/index.md` first (every spec by intent, ✓ = saved code in `components/code/`); single rows from `grep -i '^| \[<Name>\]' components/index-full.md`, never the whole `index-full.md`; open only the specs you will use.
- Captions follow `components/specs/Captions.md` instead of the opus/karaoke presets.
- 16:9 → 9:16 reframing (of a landscape source) prefers `components/specs/FaceTrackedCrop.md`.
- Output is 9:16 only (clips are reels, ≤ 2:59); the 9:16 / 16:9 / 1:1 question is skipped unless I ask for another format.
- Each clip continues through `/reel`.

**frontend-design**
- Added a note: use it for web-style visuals in compositions, and defer to `brand.md` (one grid, radius, shadow and border).

**scriptwriting**
- Copied only `skills/scriptwriting/` (`SKILL.md` and `references/`) plus the repo's root `LICENSE`. No other skill from that repo.
- Frontmatter `description` narrowed to writing, rewriting, tightening or critiquing a video `script.md`, a hook or on-screen text for this toolkit. The ads/podcast/launch-film list and the `video-director` sentence are gone.
- In the body (`SKILL.md` and `references/craft.md`), the `video-director` and `voice-direction` mentions now read: `/coding-video` and `/reel` turn the script into a video; I record it myself on camera.
- New "Toolkit adaptation (video-toolkit)" section right after the frontmatter, which wins over the rest of the skill:
  - Priority: `CLAUDE.md`, `brand.md`, `series/<playlist>.md` and the `templates/script-*.md` format win.
  - Reads `SKILL.md`, `hooks.md` and `craft.md` always; `structures.md` only to choose a structure, `formats.md` only for a beat sheet (replaces upstream's "read every file" rule).
  - Fixed opener: "Namoshkar!" (~1 s hold, half-second pause), then the hook; the greetings anti-hook rule applies to the line after it. Text hook (≤ 6 words) from frame 0; spoken hook by ~1.5 s, landing within 3 s.
  - Fixed closer: a one-line recap, then "Bye bye, sayonara!" with a wave (replaces the CTA and loopable-ending rules).
  - Pace ~140 wpm (~2.3 words/s) with word caps per length (30 s ~60 … 3 min ~390, hard cap ~420); cut points, never speed up.
  - Short-form path for every video (≤ 3 min), but research and the facts file (`work/facts.md`) are never skipped.
  - Story with depth; AI System Design episodes map the series format onto ABT (normal flow / where it breaks with LLMs / the fix).
  - Toolkit template format with `[mm:ss–mm:ss | HEAD|FULL|SPLIT]` cues instead of the A/V two-column format; `**Message:**` line at the top of `script.md`.
  - Ignores the TTS spoken layer, voice casting, localisation and the Spanish sections.
  - Keeps the three-track hook, recognition ladder, re-hooks every 5–8 s, AI-tells bans (no em dashes), swap test and fact audit as-is.

## What each one runs on this machine

- **frontend-design:** nothing. It's instructions only.
- **scriptwriting:** nothing. It's instructions only.
- **add-zooms:** `ffprobe`/`ffmpeg` (zoompan), faster-whisper, and its own `scripts/zoom_lib.py` (stdlib only).
- **cut-video:** `ffmpeg`, faster-whisper, MFA (`~/bin/mfa`, CPU), optional `praatio`, and `make_review.py` (writes a local HTML editor, no server).
- **clipify:** `ffmpeg`, faster-whisper, and small numpy scripts (`analyze.py`, `build_pan.py`, `build_ass.py`, `audio_align.py`, `detect_transients.py`).
- **remotion-\*:** instructions only. Remotion itself is installed per project inside `work/`.

None of the vendored scripts make network calls. I checked their imports and subprocess calls before adding them.

## Ideas borrowed (not vendored)

Rewritten for this toolkit, no source text copied.

| Source @ commit | What was taken | Where it went |
|---|---|---|
| [imtamiliniyan/claude-video-skills](https://github.com/imtamiliniyan/claude-video-skills) @ `69b8f5f` (MIT) | SFX synthesis recipes and the event-to-sound pattern | `pipeline/sound.md` |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) @ `1dcbe5e` (MIT) | SFX timing rules | `pipeline/sound.md` |
| [salomonMuriel/media-production-skills](https://github.com/salomonMuriel/media-production-skills) @ `6ba4284` (MIT) | Music licence rules and voice ducking; the restate test | `pipeline/sound.md`; `pipeline/qa.md` |
