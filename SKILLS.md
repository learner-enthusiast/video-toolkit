# Skills

Third-party skills used by this toolkit, at project level in `.claude/skills/`. `CLAUDE.md` and `brand.md` win over every skill's defaults (see "Skill priority" in `CLAUDE.md`).

| Skill | Source | License | Added | In git? |
|---|---|---|---|---|
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) `skills/frontend-design` @ `dbd4588` | Apache 2.0 (`LICENSE.txt`) | 2026-10-27 | Yes (vendored) |
| `add-zooms` | [louisedesadeleer/add-zooms](https://github.com/louisedesadeleer/add-zooms) @ `34db910` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
| `cut-video` | [louisedesadeleer/cut-video](https://github.com/louisedesadeleer/cut-video) @ `a5a87a6` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
| `clipify` | [louisedesadeleer/clipify](https://github.com/louisedesadeleer/clipify) @ `5f6b75e` | MIT (`LICENSE`) | 2026-10-27 | Yes (vendored) |
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
- Captions follow `components/Captions.md` instead of the opus/karaoke presets.
- 16:9 → 9:16 reframing prefers `components/FaceTrackedCrop.md`.
- Each clip continues through `/reel`.

**frontend-design**
- Added a note: use it for web-style visuals in compositions, and defer to `brand.md` (one grid, radius, shadow and border).

## What each one runs on this machine

- **frontend-design:** nothing. It's instructions only.
- **add-zooms:** `ffprobe`/`ffmpeg` (zoompan), faster-whisper, and its own `scripts/zoom_lib.py` (stdlib only).
- **cut-video:** `ffmpeg`, faster-whisper, MFA (`~/bin/mfa`, CPU), optional `praatio`, and `make_review.py` (writes a local HTML editor, no server).
- **clipify:** `ffmpeg`, faster-whisper, and small numpy scripts (`analyze.py`, `build_pan.py`, `build_ass.py`, `audio_align.py`, `detect_transients.py`).
- **remotion-\*:** instructions only. Remotion itself is installed per project inside `work/`.

None of the vendored scripts make network calls. I checked their imports and subprocess calls before adding them.
