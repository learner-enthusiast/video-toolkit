# GPU

**Goal:** every GPU-capable step runs on the NVIDIA card, verified, never a silent CPU fallback.

**Do**
- Run only if `nvidia-smi` exists (otherwise say there is no NVIDIA GPU and ask how to proceed).
- Create `~/bin/gpu-run` (chmod +x) that exports `__NV_PRIME_RENDER_OFFLOAD=1`, `__GLX_VENDOR_LIBRARY_NAME=nvidia`, prepends `/usr/lib/x86_64-linux-gnu` to `LD_LIBRARY_PATH`, then runs `exec "$@"`.
- Make sure `~/bin` is on PATH for both login shells and new terminals.
- Prefix every GPU command with it: Whisper, torch scripts, ffmpeg with NVENC, Remotion renders.
- `gpu-run` is equivalent to setting these for every GPU command (Whisper, Remotion render, FFmpeg GPU encode). Prepend rather than overwrite `LD_LIBRARY_PATH`, so venv CUDA libs still load:
  ```bash
  export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
  export __NV_PRIME_RENDER_OFFLOAD=1
  export __GLX_VENDOR_LIBRARY_NAME=nvidia
  ```
- Three.js / `@remotion/three` scenes: render with `--gl=angle` (or `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts`) and confirm with `gpu-run npx remotion gpu` that the NVIDIA card is the renderer. If ANGLE runs out of memory on a full render (likely on a 4 GB card), render in parts with `--frames` and concat.
- `npx remotion gpu` fails in the default headless shell (it can't open chrome://gpu). Prove the renderer instead with a 1-frame still that prints WebGL's `UNMASKED_RENDERER_WEBGL`: it must name the NVIDIA card (e.g. "ANGLE (NVIDIA … GTX 1650 …)"), not SwiftShader.
- A 4 GB GTX 1650 renders a 3:23 1080x1920 composition with Three.js scenes at `--concurrency=6` with ANGLE in ~12 min, no split needed. Don't run a second Chrome/ANGLE job at the same time.
- If the Python env ships its own cuBLAS/cuDNN wheels, the launcher must also put those lib dirs on `LD_LIBRARY_PATH`, or CTranslate2 fails to load them.

**Checks** (all must pass before continuing)
- `gpu-run nvidia-smi` shows the card and its VRAM.
- `gpu-run python -c "import torch; print(torch.cuda.is_available())"` prints `True`.
- `ffmpeg -hide_banner -encoders | grep nvenc` lists `h264_nvenc`. If not, use `libx264 -preset veryfast -crf 20` and say so.

**Gotchas**
- 4 GB card: Whisper large-v3 doesn't fit in float16; use `int8_float16` or `int8`.
- MediaPipe face detection is CPU-only: expected, report it.
- One heavy GPU job at a time; small side jobs may then use the CPU (Remotion `--gl=swangle`) and are logged (`CLAUDE.md` GPU exception).
- If a check fails, fix the cause; if you can't, stop and tell me.
- Shared card: never kill another project's job; wrap GPU steps in `tools/jobs/gpu_wait.sh` (wait, retry on OOM).
- `whisper-ctranslate2` exits 0 on OOM: judge by the output JSON, wait for a free card, retry.
- 4 GB card: pass `--best_of 1` (the temperature fallback samples 5 at once and OOMs).
- A `pgrep -f whisper-ctranslate2` wait loop matches itself: match the interpreter path.
- If a pass leaves no JSON, test a 40 s window: try `int8` (beam 5) or `int8_float16 --beam_size 2`.
