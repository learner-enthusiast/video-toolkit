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
- On a 4 GB card (GTX 1650), Whisper large-v3 does not fit in float16. Use `compute_type int8_float16`.
- MediaPipe's Python face detector runs on the CPU only. That is expected; report it rather than hiding it.
- Run one heavy GPU job at a time on small cards.
- If a check fails, find the cause (driver, PATH, missing libs). If it truly cannot be fixed, stop and tell me.
- The card may be shared with another Claude session (another project transcribing at the same time). An OOM in Whisper usually means someone else holds VRAM: check `nvidia-smi --query-compute-apps=pid,used_memory` and `readlink /proc/<pid>/cwd`. Never kill another project's job; wait for it, or transcribe short windows (a few seconds each fit beside it).
- Whisper large-v3 at `int8` peaked at ~3.3 GB on the GTX 1650 on one video, but see the next point: it is not always the safer choice.
- `whisper-ctranslate2` exits 0 on "CUDA failed with error out of memory". Judge a pass by its output JSON existing, not the exit code. Wait for an empty `--query-compute-apps` before each pass (another project may run passes back to back) and retry a pass that left no JSON.
- Whisper OOM at the same spot on every try, alone on a free card, is the temperature fallback: it samples `best_of` (default 5) candidates at once. On `graphql-vs-rest` both `int8` and `int8_float16` died ~1 min in; `--best_of 1` finished at 2.2 GB. Pass `--best_of 1` by default on a 4 GB card.
- A wait loop like `while pgrep -f whisper-ctranslate2` matches its own shell's command line and never ends. Match the interpreter path instead (`pgrep -f '^/home/…/venv/bin/python3'`).
