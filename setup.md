# Setup

The easy way: open Claude Code in this folder and run `/setup`. It checks what's installed, asks, then installs. This file is the manual route for anyone cloning the repo.

Everything installs **once per machine, globally**: apt, one shared user venv (`~/video-toolkit/venv`) with launchers in `~/bin`, and models in `~/.cache`. Never a venv per project.

## Carousel PDF

`/carousel` joins the slide PNGs into one lossless PDF with `img2pdf`, installed once per machine:
```bash
pipx install img2pdf && img2pdf --version
```

## Video inspection tools

Used by `pipeline/video-inspect.md`: local tools scan every frame and write a text report, so Claude reads a few thousand tokens instead of thousands of images.

| Tool | Does | Installed at |
|---|---|---|
| FFmpeg | black, freeze, silence and loudness detection, contact sheets | apt: `/usr/bin/ffmpeg` |
| PySceneDetect 0.7 | cut and scene detection | shared venv; launcher `~/bin/scenedetect` |
| faster-whisper | transcript with word timings, on CUDA | shared venv; models in `~/.cache/huggingface/hub` |
| PaddleOCR 3 (PP-OCRv5 mobile) | on-screen text and captions, on the GPU | own venv `~/video-toolkit/ocr-venv`; launcher `~/bin/vt-ocr-python`; models in `~/.paddlex/official_models` |
| MediaPipe FaceLandmarker | face present, eyes open/closed, framing (CPU) | shared venv; model `~/.cache/mediapipe/face_landmarker.task` |
| Ollama + qwen2.5vl:3b (moondream as a small fallback) | one-line description per scene | `/usr/local/bin/ollama`, systemd service `ollama`; models in `/usr/share/ollama/.ollama/models` |

**1. System packages**
```bash
sudo apt install ffmpeg python3-venv wamerican
```

**2. Shared venv** (skip if `/setup` already made it; Ubuntu 24.04 blocks `pip install --user`)
```bash
python3 -m venv ~/video-toolkit/venv && mkdir -p ~/bin
printf '#!/bin/bash\nexec "$HOME/video-toolkit/venv/bin/python" "$@"\n' > ~/bin/vt-python && chmod +x ~/bin/vt-python
~/video-toolkit/venv/bin/pip install torch faster-whisper mediapipe opencv-python-headless numpy
# --no-deps: scenedetect's opencv-python clashes with opencv-python-headless
~/video-toolkit/venv/bin/pip install --no-deps scenedetect==0.7.2 && ~/video-toolkit/venv/bin/pip install click platformdirs tqdm
printf '#!/bin/bash\nexec "$HOME/video-toolkit/venv/bin/scenedetect" "$@"\n' > ~/bin/scenedetect && chmod +x ~/bin/scenedetect
curl -fsSL -o ~/.cache/mediapipe/face_landmarker.task --create-dirs \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

**3. PaddleOCR, in its own user-wide venv.** `paddlepaddle-gpu` pins cuDNN 9.5; torch needs a newer one, so sharing a venv breaks one of them. Every project still shares this one.
```bash
python3 -m venv ~/video-toolkit/ocr-venv
# NVIDIA (CUDA 12.6 wheels; the index is slow, give it ~10 min):
~/video-toolkit/ocr-venv/bin/pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
# CPU only instead:  ~/video-toolkit/ocr-venv/bin/pip install paddlepaddle==3.2.0
~/video-toolkit/ocr-venv/bin/pip install paddleocr
cat > ~/bin/vt-ocr-python <<'EOF'
#!/bin/bash
NV="$HOME/video-toolkit/ocr-venv/lib/python3.12/site-packages/nvidia"
for d in "$NV"/*/lib; do LD_LIBRARY_PATH="$d:$LD_LIBRARY_PATH"; done
export LD_LIBRARY_PATH
exec "$HOME/video-toolkit/ocr-venv/bin/python" "$@"
EOF
chmod +x ~/bin/vt-ocr-python
```
If PaddleOCR won't run on your GPU, use EasyOCR in the shared venv instead: `~/video-toolkit/venv/bin/pip install easyocr`.

**4. Ollama and a vision model**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5vl:3b         # 3.2 GB, the default. On a 4 GB card ~57% runs on the GPU; use qwen2.5vl:7b on ≥ 8 GB
ollama pull moondream            # 1.7 GB fallback: fits any card, but its captions are much weaker
```

### NVIDIA on Linux (optional)

Only for laptops/desktops with an NVIDIA card on Linux, especially hybrid (PRIME) graphics. Without these variables, GPU tools can silently run on the CPU or the integrated GPU:
```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```
- Don't put them in `~/.bashrc`. Use the `~/bin/gpu-run` wrapper (`pipeline/gpu.md`): it sets them, prepending to `LD_LIBRARY_PATH` rather than overwriting it, then runs the command. Prefix faster-whisper and PaddleOCR with it: `gpu-run vt-python …`, `gpu-run vt-ocr-python …`.
- Ollama runs as a service, so it gets them from a systemd drop-in instead:
  ```bash
  sudo mkdir -p /etc/systemd/system/ollama.service.d && printf '[Service]\nEnvironment="LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu"\nEnvironment="__NV_PRIME_RENDER_OFFLOAD=1"\nEnvironment="__GLX_VENDOR_LIBRARY_NAME=nvidia"\nEnvironment="OLLAMA_KEEP_ALIVE=30s"\n' | sudo tee /etc/systemd/system/ollama.service.d/gpu.conf
  sudo systemctl daemon-reload && sudo systemctl restart ollama
  ```
  `OLLAMA_KEEP_ALIVE=30s` frees VRAM soon after a run, so Whisper doesn't hit OOM next on a small card.
- Run the sudo commands in your own terminal. Claude Code's `!` prefix has no TTY, so sudo can't ask for the password: the folder gets made, but the file isn't written. Check with `systemctl show ollama -p DropInPaths`.
- Restarting the service kills a running `ollama pull` ("unexpected EOF"). Apply the drop-in before pulling, or just pull again; it resumes.

### CPU only (no NVIDIA GPU)

Everything works, just slower. Skip `gpu-run` and use:
- faster-whisper: `device="cpu", compute_type="int8"`, and the `small.en` or `medium` model instead of `large-v3`.
- PaddleOCR: the CPU `paddlepaddle` wheel above and `device="cpu"`. EasyOCR: `gpu=False`.
- Ollama: moondream only. It runs on the CPU automatically.
- ffmpeg: drop `-hwaccel cuda`.

### Verify
```bash
gpu-run nvidia-smi --query-gpu=name,memory.total --format=csv
gpu-run vt-python -c "import torch, faster_whisper, mediapipe, scenedetect; print('cuda', torch.cuda.is_available())"
gpu-run vt-ocr-python -c "import paddle, paddleocr; print(paddle.device.get_device())"   # gpu:0
ollama run moondream "say ok" && journalctl -u ollama --since -2min | grep -o 'offloaded [0-9]*/[0-9]* layers to GPU'
```
Expected: the card's name, `cuda True`, `gpu:0`, and `offloaded N/N layers to GPU`. On CPU-only machines, `cuda False`, `cpu` and no offload line are expected.
