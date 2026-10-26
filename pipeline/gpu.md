# GPU

**Goal:** every GPU-capable step runs on the NVIDIA card, verified, never a silent CPU fallback.

**Do**
- Run only if `nvidia-smi` exists (otherwise say there is no NVIDIA GPU and ask how to proceed).
- Create `~/bin/gpu-run` (chmod +x) that exports `__NV_PRIME_RENDER_OFFLOAD=1`, `__GLX_VENDOR_LIBRARY_NAME=nvidia`, prepends `/usr/lib/x86_64-linux-gnu` to `LD_LIBRARY_PATH`, then runs `exec "$@"`.
- Make sure `~/bin` is on PATH for both login shells and new terminals.
- Prefix every GPU command with it: Whisper, torch scripts, ffmpeg with NVENC, Remotion renders.
- If the Python env ships its own cuBLAS/cuDNN wheels, the launcher must also put those lib dirs on `LD_LIBRARY_PATH`, or CTranslate2 fails to load them.

**Checks** (all must pass before continuing)
- `gpu-run nvidia-smi` shows the card and its VRAM.
- `gpu-run python -c "import torch; print(torch.cuda.is_available())"` prints `True`.
- `ffmpeg -hide_banner -encoders | grep nvenc` lists `h264_nvenc`. If not, use `libx264 -preset veryfast -crf 20` and say so.

**Gotchas**
- On a 4 GB card (GTX 1650), Whisper large-v3 does not fit in float16. Use `compute_type int8_float16`.
- MediaPipe's Python face detector runs on the CPU only. That is expected; report it rather than hiding it.
- Run one heavy GPU job at a time on small cards.
- If a check fails, find the cause (driver, PATH, missing libs). If it truly cannot be fixed, stop and tell me.
