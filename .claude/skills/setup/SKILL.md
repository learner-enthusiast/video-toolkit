---
name: setup
description: Check which video tools are installed, ask before installing the missing ones, then re-check. Run once per machine.
---

# Setup

1. **Check.** Have a Haiku subagent report each item as present (with version) or missing, without installing anything:
   - `ffmpeg`/`ffprobe`, and whether `-encoders` lists `h264_nvenc` and `-filters` lists `arnndn`/`afftdn`/`loudnorm`
   - `nvidia-smi`, `~/bin/gpu-run`, and `~/bin` on PATH
   - Node ≥ 20 and `npx`
   - A Python env with torch + CUDA, faster-whisper (or whisper-ctranslate2), mediapipe, opencv, and transformers (for forced alignment)
   - Cached models: faster-whisper large-v3, wav2vec2 alignment model
   - `cursor-agent` (optional), and `rembg` (optional, used for thumbnails)
   - `praatio` in the shared venv, and `~/bin/mfa` with the `english_mfa` acoustic model and dictionary (for `/cut-video`)
   - The Remotion skills: `.claude/skills/remotion-best-practices/SKILL.md` resolves (they're gitignored, so a fresh clone lacks them)
2. **Ask me.** Show one table of what is missing and the proposed install method for each (see the Installs rule in `CLAUDE.md`). Wait for my answer.
3. **Install** only what I approved. On Ubuntu 24.04, `pip install --user` is blocked (PEP 668): use one shared user-level venv with small launcher scripts in `~/bin`, not a venv per project.
   - **Remotion skills** (no license upstream, so not committed; install per clone, from the repo root): `npx skills add remotion-dev/skills`, then choose all skills and Claude Code. They land in `.agents/skills/`, symlinked from `.claude/skills/remotion-*`.
   - **praatio:** `vt-pip install praatio`
   - **MFA** (Montreal Forced Aligner; there's no apt package, conda-forge is the supported route). Install Miniforge in batch mode, which doesn't touch `~/.bashrc`:
     ```bash
     D=$(mktemp -d) && cd "$D"
     curl -fsSLO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
     curl -fsSLO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh.sha256
     sha256sum -c Miniforge3-Linux-x86_64.sh.sha256 && bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3
     ~/miniforge3/bin/conda create -n mfa -c conda-forge montreal-forced-aligner -y
     printf '#!/bin/bash\n# Montreal Forced Aligner launcher (conda env "mfa"). Used by /cut-video.\nexport PATH="$HOME/miniforge3/envs/mfa/bin:$PATH"\nexec "$HOME/miniforge3/envs/mfa/bin/mfa" "$@"\n' > ~/bin/mfa && chmod +x ~/bin/mfa
     mfa model download acoustic english_mfa && mfa model download dictionary english_mfa
     ```
4. **GPU.** Create `gpu-run` as described in `pipeline/gpu.md` and run its checks.
5. **Re-check.** Run step 1 again and show the final table. Anything still failing gets named, with its cause.

Write install logs to a temp folder or `work/logs/`. Never paste them into the chat.
