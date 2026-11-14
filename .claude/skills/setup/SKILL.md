---
name: setup
description: Check which video tools are installed, ask before installing the missing ones, then re-check. Run once per machine.
---

# Setup

1. **Check.** Run these probes (Haiku runner, per `pipeline/delegation.md`) to report each item as present (with version) or missing, without installing anything:
   - `ffmpeg`/`ffprobe`, and whether `-encoders` lists `h264_nvenc` and `-filters` lists `arnndn`/`afftdn`/`loudnorm`
   - `nvidia-smi`, `~/bin/gpu-run`, and `~/bin` on PATH
   - Node ≥ 20 and `npx`
   - A Python env with torch + CUDA, faster-whisper (or whisper-ctranslate2), mediapipe, opencv, and transformers (for forced alignment)
   - Cached models: faster-whisper large-v3, wav2vec2 alignment model
   - Delegation CLIs (`pipeline/delegation.md`): `copilot --version` and `gh auth status`; `codex --version` and `codex login status`; `cursor-agent --version` and `cursor-agent status`. Each must be installed **and** logged in; also report the Copilot usage reading (`gh api /copilot_internal/user`) and the cursor-agent canary result. Missing ones: ask, then install globally
   - `rembg` (optional, used for thumbnails)
   - `img2pdf` on PATH (for `/carousel` PDFs; install with `pipx install img2pdf`)
   - `praatio` in the shared venv, and `~/bin/mfa` with the `english_mfa` acoustic model and dictionary (for `/cut-video`)
   - The Remotion skills: `.claude/skills/remotion-best-practices/SKILL.md` resolves (they're gitignored, so a fresh clone lacks them)
   - Video inspection (`pipeline/video-inspect.md`): `scenedetect version`; `~/bin/vt-ocr-python` and `gpu-run vt-ocr-python -c "import paddle, paddleocr; print(paddle.device.get_device())"` prints `gpu:0`; `~/.cache/mediapipe/face_landmarker.task`; `ollama list` shows `qwen2.5vl:3b` (default; the 7b on cards with ≥ 8 GB) and `moondream` (fallback); `systemctl cat ollama` shows the drop-in with the PRIME variables; `/usr/share/dict/american-english`
2. **Ask me.** Show one table of what is missing and the proposed install method for each (see the Installs rule in `CLAUDE.md`). Wait for my answer.
3. **Install** only what I approved. Delegation CLIs install **globally**, never per project: `npm i -g @github/copilot`, `npm i -g @openai/codex`, `curl https://cursor.com/install -fsS | bash`. Logins (`copilot login`, `codex login`, `cursor-agent login`) are interactive: print them for me to run with `!`. On Ubuntu 24.04, `pip install --user` is blocked (PEP 668): use one shared user-level venv with small launcher scripts in `~/bin`, not a venv per project.
   - **Remotion skills** (no license upstream, so not committed; install per clone, from the repo root): `npx skills add remotion-dev/skills`, then choose all skills and Claude Code. They land in `.agents/skills/`, symlinked from `.claude/skills/remotion-*`.
   - **praatio:** `vt-pip install praatio`
   - **MFA** (Montreal Forced Aligner; there's no apt package, conda-forge is the supported route). Install Miniforge in batch mode, which doesn't touch `~/.bashrc`:
     ```bash
     # The checksum is only published for the versioned file name (the unversioned .sha256 is a 404).
     # Get the current tag: curl -s https://api.github.com/repos/conda-forge/miniforge/releases/latest | grep tag_name
     V=26.9.4-1; B=https://github.com/conda-forge/miniforge/releases/download/$V
     D=$(mktemp -d) && cd "$D"
     curl -fsSLO $B/Miniforge3-$V-Linux-x86_64.sh && curl -fsSLO $B/Miniforge3-$V-Linux-x86_64.sh.sha256
     sha256sum -c Miniforge3-$V-Linux-x86_64.sh.sha256 && bash Miniforge3-$V-Linux-x86_64.sh -b -p ~/miniforge3
     ~/miniforge3/bin/conda create -n mfa -c conda-forge montreal-forced-aligner -y
     printf '#!/bin/bash\n# Montreal Forced Aligner launcher (conda env "mfa"). Used by /cut-video.\nexport PATH="$HOME/miniforge3/envs/mfa/bin:$PATH"\nexec "$HOME/miniforge3/envs/mfa/bin/mfa" "$@"\n' > ~/bin/mfa && chmod +x ~/bin/mfa
     mfa model download acoustic english_mfa && mfa model download dictionary english_mfa
     ```
   - **Video inspection tools:** the exact commands are in `setup.md` → "Video inspection tools". PySceneDetect goes into the shared venv with `--no-deps` (its `opencv-python` dep clashes with the installed headless OpenCV). PaddleOCR gets its own user-wide venv, `~/video-toolkit/ocr-venv`, because `paddlepaddle-gpu` pins cuDNN 9.5 and would downgrade torch's 9.10. Ollama needs sudo: print the two commands (installer and service drop-in) for me to run, and don't try to run them yourself. Pick the vision models from `nvidia-smi` VRAM.
4. **GPU.** Create `gpu-run` as described in `pipeline/gpu.md` and run its checks. Also prove that each inspection tool uses the card: `nvidia-smi --query-compute-apps` lists the OCR process during a predict, and `journalctl -u ollama` shows `offloaded N/N layers to GPU` after a `moondream` call, and `ollama ps` shows the GPU share of `qwen2.5vl:3b` (partial on 4 GB cards: report it).
5. **Re-check.** Run step 1 again and show the final table. Anything still failing gets named, with its cause.

Write install logs to a temp folder or `work/logs/`. Never paste them into the chat.
