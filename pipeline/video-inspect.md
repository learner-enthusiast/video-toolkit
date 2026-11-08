# Video inspect

**Goal:** see a video's content and measure its defects for a few thousand tokens, instead of reading frames one by one. Local tools scan every frame and write a compact text report; Opus reads the report and opens only the frames that matter. Every image read stays in the session context for every later turn.

**Inputs:** a video path, optional `--start/--end` (seconds), optional `--thorough` (final pre-publish check).
**Output:** `work/inspect/<deliverable>/` (`<deliverable>` = the file's stem): `report.json`, `contact_sheet.jpg`, `keyframes/` (one per scene, plus every flagged frame), and `sheet_NN.jpg` for beat QA.

**Build it per project** in `work/scripts/video_inspect.py` (shared venv, `gpu-run vt-python`) plus `work/scripts/video_inspect_ocr.py` (`gpu-run vt-ocr-python`: PaddleOCR has its own venv, see `setup.md`). Haiku runs it from exact commands Opus writes (`pipeline/delegation.md`). Run the GPU stages one after another, never at the same time (4 GB card). All times are in source seconds (add `--start`), 2 decimals; boxes are normalised 0–1, 3 decimals.

| Stage | Tool and exact settings |
|---|---|
| Probe | `ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,sample_rate,channels -of json` |
| Detectors (one decode) | `ffmpeg -hide_banner -nostats -hwaccel cuda [-ss S -to E] -i V -vf "blackdetect=d=0.03:pix_th=0.10,freezedetect=n=-60dB:d=3" -af "silencedetect=n=-40dB:d=0.6,ebur128=peak=true" -f null -`; parse stderr (`black_start/end`, `lavfi.freezedetect.freeze_start/end`, `silence_start/end`, the ebur128 Summary I / LRA / Peak) |
| Scenes | PySceneDetect API: `detect(V, AdaptiveDetector(adaptive_threshold=3.0, min_scene_len=8), start_time=S, end_time=E)`. CLI for a quick look: `scenedetect -i V detect-adaptive list-scenes -n` |
| Frames | one ffmpeg seek per sample: `ffmpeg -v error -ss T -i V -frames:v 1 -vf scale=960:-2 -q:v 3 out.jpg`. Default: middle of each scene. Thorough: also scene start+2 and end−2 frames, and every 1 s |
| Caption band | `ffmpeg -ss S -to E -i V -vf "fps=2,crop=iw:ih*0.30:0:ih*0.70" cap_%05d.jpg` (fps=6 thorough). Reels: the band from the face track and brand layout, not a fixed crop |
| Transcript | faster-whisper `WhisperModel("large-v3", device="cuda", compute_type="int8_float16")`, `transcribe(wav, language="en", word_timestamps=True, vad_filter=True, best_of=1, condition_on_previous_text=False)` on a 16 kHz mono WAV (`ffmpeg -vn -ac 1 -ar 16000`). Free the model before OCR |
| OCR | PaddleOCR 3.x: `PaddleOCR(lang="en", device="gpu:0", use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False, text_detection_model_name="PP-OCRv5_mobile_det", text_recognition_model_name="PP-OCRv5_mobile_rec")`; `r = ocr.predict(path)[0]` → `rec_texts`, `rec_scores`, `rec_boxes`. Keep score ≥ 0.6. Fallback: `easyocr.Reader(["en"], gpu=True)` |
| Face | MediaPipe Tasks `FaceLandmarker` (`~/.cache/mediapipe/face_landmarker.task`, `output_face_blendshapes=True`, `num_faces=2`), CPU. Per frame: face count, box, `eyeBlinkLeft/Right` |
| VLM | Ollama `POST localhost:11434/api/generate` `{"model":"qwen2.5vl:3b","prompt":"Describe this video frame in one short sentence.","images":[b64 of the 512 px keyframe],"stream":false,"keep_alive":"30s","options":{"temperature":0,"num_predict":40,"num_ctx":2048}}`. After the first call, read `/api/ps` and put `size_vram/size` in `summary.notes` if < 100%. Unload every Ollama model (`keep_alive: 0`) before Whisper and after this stage. A hint only, never a verdict |
| Contact sheet | `ffmpeg [-ss S -to E] -i V -vf "fps=48/DUR,scale=320:-2,drawtext=text='%{pts\:hms\:S}':x=6:y=h-th-6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=8x6" -frames:v 1 -q:v 3 contact_sheet.jpg` (48 tiles, one image, ~1.5k tokens). Portrait: `scale=-2:320` and `tile=12x4` (an 8x6 portrait sheet is ~4k tokens) |

**report.json** (compact JSON, no indent)
- `summary`: duration, resolution, fps, LUFS/TP/LRA, scene count, flag counts by type. Read this first.
- `scenes`: `[{i, t:[in,out], kf, vlm, ocr:[[text,score,box]], face:{n, box, blink:[l,r]}}]`.
- `words`: `[[start,end,"word"]]`; `captions`: `[[first_seen,last_seen,"text"]]`; `black`, `freeze`, `silence`: `[[start,end]]`.
- `flags`: `[{t, type, detail, frame}]`, sorted by time. Read slices with `jq '{summary,flags}'` and `jq '.scenes'`, not the whole file.

**Flags** (each visual flag writes `keyframes/flag_<t>_<type>.jpg`)
- `black_flash`: black < 0.5 s that isn't at the start or end. `short_scene`: a scene < 0.25 s (flash cut).
- `static_hold`: freeze ≥ 3 s (the "no screenshot holds still > 3 s" rule). `dead_air`: silence ≥ 0.6 s inside the video.
- `text_cut_off`: an OCR box within 0.5% of a frame edge. `outside_margin`: an OCR box outside the 5% safe margin.
- `misspelling`: an OCR word (score ≥ 0.9, ≥ 3 letters, box ≥ 2% of frame height, so background text like a monitor behind me is skipped) that is not in the transcript, the `script.md` glossary or `/usr/share/dict/american-english`.
- `caption_desync`: a caption's first word seen > 0.4 s after, or > 0.6 s before, Whisper's start for it (resolution is the sample rate). `caption_not_spoken`: no transcript match within ±2 s. Band text counts as a caption only if it has ≥ 3 characters and ≥ 50% of its words are spoken within ±2 s (a lone "5" matched a spoken "5" on IntroVideo).
- `eyes_closed`: both blink scores > 0.5 on a keyframe or on a scene's first/last frame (a cut on a blink).
- `face_edge`: face box within 1% of an edge. `face_lost`: no face where the neighbouring samples in the same scene had one. `text_over_face`: an OCR box overlapping the face box.

**Contact sheets for QA**
- One frame from the middle of every beat (or every 5 s for a cut without beats), scaled to 480 px wide, with its output timestamp burned in at the bottom-left. Tile them 4x3 (12 frames per sheet) into `work/inspect/<deliverable>/sheet_NN.jpg`.
- Opus looks at sheets, not single frames. Pull a full-size frame only to settle something a sheet or a flag raises (text near the margin, face under an overlay, caption legibility).
- For QA and the face/margin checks, the beat frames come from `pipeline/qa.md`; this file only defines how they're laid out.

**Who looks**
- A Haiku subagent may **pre-screen** sheets during a stage and list the timestamps worth a look. A pre-screen never passes anything.
- **Final visual QA before deliverables is done by Opus, looking at every contact sheet itself** (and one keyframe per scene in `--thorough`), plus the report's flags and intervals. Every flag, freeze, silence or black interval is either explained (an intended hold, the end card) or fixed.
- Look at sheets in the stage that needs them, then hand off; don't carry sheets from an earlier stage (`pipeline/stages.md`).

**Checks**
- Haiku's report includes `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` sampled during the Whisper and OCR stages, and the Ollama log line `offloaded N/N layers to GPU`. Any stage on the CPU (except MediaPipe) is a failure, not a pass (`pipeline/gpu.md`).

**Gotchas**
- Never name the script `inspect.py`: it shadows the stdlib `inspect`, and numpy's import then fails as a circular import of scenedetect.
- Phone footage stores 1920x1080 with a 90° rotation flag, and ffmpeg auto-rotates on decode. Read `stream_side_data=rotation` (or the `rotate` tag) and swap W/H, or the summary says landscape while every frame is portrait (IntroVideo `main.mp4`).
- moondream (100% GPU, 1.2 GB) captioned me as "urn of flowers on a desk…" on IntroVideo; qwen2.5vl:3b got "A man in a blue hoodie… talking". Use qwen. On the 4 GB GTX 1650 it runs ~57% on the GPU whatever `num_ctx` is (the weights don't fit): ~25 s to load, then fast per frame. That's a hardware limit, stated in the report's notes, not a silent fallback. Use `qwen2.5vl:7b` on ≥ 8 GB.
- An Ollama model still loaded from earlier (keep-alive) holds ~2 GB: Whisper then dies with "CUDA failed with error out of memory". The script unloads Ollama first.
- `ollama run <model> "prompt"` from a non-TTY shell with open stdin waits forever. Use the HTTP API, or `< /dev/null`.
- `pip check` reports "scenedetect requires opencv-python". That's expected: it was installed `--no-deps` and uses the headless OpenCV.
- The first PaddleOCR run downloads PP-OCRv5 mobile into `~/.paddlex/official_models` (~30 s). After that it does ~0.1 s per frame in ~0.4 GB VRAM.
- B-roll / vlog footage (no talking head) also needs a quality pass, which the table above doesn't cover: at 5 fps on 480 px greyscale, Laplacian variance (sharpness), mean luma (dark < 40, blown > 215), `cv2.phaseCorrelate` shift between frames minus its 1 s moving average (camera shake, % of width), and mean abs frame diff (content motion). Report it per scene and per second; it's what ranks shots. `fannout-day-01` has the reference implementation in `work/scripts/video_inspect.py`.
- On an edited cut, every hard cut reads as a huge phase-correlation jump, so `shaky` fired on 9 cuts of `fannout-day-01`'s rough cut. Zero the jitter within 0.4 s of each scene boundary.
- `freezedetect` prints no `freeze_end` when the freeze runs to the end of the file (an end card, a slate). Close it at the video's duration, or the report shows a nonsense length.
- Phone desk footage can show private screens (Gmail inbox, Google account recovery on `fannout-day-01`). Look at the monitors on the contact sheet before you plan any punch-in on a screen, and blur them when you're unsure.
- No flag catches a scene that was never built. On `redis-invalidation` Part 1, the storyboard beat D8 (Facebook memcache leases) had no component, so the SPLIT grid card sat empty for ~6 s and inspect raised nothing. Before the final render, check every storyboard row against a component, and on the contact sheet look for blank cards in SPLIT.
- `text_over_face` with tiny OCR strings like `ATX3`, `AYAD`, `AT23` is the red wall sticker behind me (and the signature at the end), not overlay text. Treat it as a false positive.
- `caption_desync` pairs a caption's first word with the nearest same word within 2 s, so a short word ("a", "the") can match an earlier occurrence and report +1.7 s (`jwt-explained` "a JWKS"). Check the timeline word time before acting. `misspelling` fires on intentional strings (a JWT token, `wordlist.txt`): treat code/token text as false positives.
- PySceneDetect finds very few scenes on a reel whose cuts are spring morphs (9 scenes in 2:51), so keyframes alone miss most beats: always look at the 48-tile contact sheet as well.
- Once captions are CTC-aligned (`pipeline/transcribe.md`), `caption_desync` at +0.5…+0.7 s is Whisper's early-start bias, not a late caption: on `jwt-explained` (thorough, 6 fps band) all 19 flags had the caption within 1–3 frames of the CTC onset. Check flagged words against the CTC word times before changing anything; consider comparing to CTC-corrected starts in the script itself.
- Back-to-back inspect runs in one shell loop can OOM at the next run's Whisper load while the previous process is still freeing VRAM. Wait for an empty `--query-compute-apps` between runs.
