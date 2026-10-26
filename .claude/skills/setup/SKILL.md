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
2. **Ask me.** Show one table of what is missing and the proposed install method for each (see the Installs rule in `CLAUDE.md`). Wait for my answer.
3. **Install** only what I approved. On Ubuntu 24.04, `pip install --user` is blocked (PEP 668): use one shared user-level venv with small launcher scripts in `~/bin`, not a venv per project.
4. **GPU.** Create `gpu-run` as described in `pipeline/gpu.md` and run its checks.
5. **Re-check.** Run step 1 again and show the final table. Anything still failing gets named, with its cause.

Write install logs to a temp folder or `work/logs/`. Never paste them into the chat.
