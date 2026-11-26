# Video inspect

**Goal:** see a video's content and measure its defects for a few thousand tokens, instead of reading frames one by one. Local tools scan every frame into a compact text report, and `vision-qa` looks at the images that matter. An image read is re-sent every later turn, so images stay out of the main session (exceptions below).

**Inputs:** a video path, optional `--start/--end` (seconds), optional `--thorough` (final pre-publish check).
**Output:** `work/inspect/<deliverable>/` (`<deliverable>` = the file's stem): `report.json`, `contact_sheet.jpg`, `keyframes/` (one per scene, plus every flagged frame), and `sheet_NN.jpg` for beat QA.

**Cache (unchanged video):** `tools/inspect_cache.py` caches the **whole** `work/inspect/<deliverable>/` bundle when inputs match (video hash, mode, range, script hashes, implementation fingerprint; `integrity.json` checksums every artifact). **Intermediate** QA may `lookup` / `restore` a valid hit. **Final pre-publish QA:** `lookup --for-final` and `restore --for-final` **always refuse** cache reuse (`reason: final_qa_requires_fresh_run`). Flow: fresh final render → fresh `--thorough` inspect → Opus vision QA → your approval. Cache never equals approval (`pipeline/job-results.md`, `pipeline/qa.md`).

**Transcript provenance gate:** this Whisper pass is a QA transcript only. For talking-head production footage, it may run only on a deliverable whose audio comes from the Prep-verified cleaned recording (`pipeline/stages.md`, `pipeline/voice-cleaning.md`); it must never be used to bootstrap Prep or to transcribe raw/unverified source audio. If provenance is unknown, omit the transcript stage and report why.

**Run the tracked tool** from `work/` (never copy or rebuild it): `gpu-run vt-python tools/inspect/video_inspect.py <video> [--thorough] [--start S --end E] [--glossary ../script.md]` (tool paths here are relative to the toolkit root). It calls `tools/inspect/video_inspect_ocr.py` through `vt-ocr-python` (PaddleOCR's own venv, `setup.md`) and writes `inspect/<deliverable>/`. Run it as a heavy job (`tools/jobs/batch.sh`, `pipeline/delegation.md` §5). `--cpu-test` is for CI only and is never a QA result. Run the GPU stages one after another, never at the same time (4 GB card). All times are in source seconds (add `--start`), 2 decimals; boxes are normalised 0–1, 3 decimals.

**Stages** (all in the tool, one decode for the FFmpeg detectors): probe → black / freeze / silence / loudness → scenes (PySceneDetect) → keyframes (`--thorough` adds scene edges and every 1 s) → caption band → Whisper large-v3 → PaddleOCR → MediaPipe face (CPU) → qwen2.5vl captions (a hint only, never a verdict) → flags → 48-tile contact sheet. Exact settings: `tools/inspect/README.md` (only needed when changing the tool).

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
- `caption_desync`: a caption's first word seen > 0.4 s after, or > 0.6 s before, Whisper's start for it (resolution is the sample rate). `caption_not_spoken`: no transcript match within ±2 s. Band text counts as a caption only if it has ≥ 3 characters and ≥ 50% of its words are spoken within ±2 s.
- `eyes_closed`: both blink scores > 0.5 on a keyframe or on a scene's first/last frame (a cut on a blink).
- `face_edge`: face box within 1% of an edge. `face_lost`: no face where the neighbouring samples in the same scene had one. `text_over_face`: an OCR box overlapping the face box.

**Contact sheets for QA**
- One frame from the middle of every beat (or every 5 s for a cut without beats), scaled to 480 px wide, with its output timestamp burned in at the bottom-left. Tile them 4x3 (12 frames per sheet) into `work/inspect/<deliverable>/sheet_NN.jpg`.
- The vision subagent looks at sheets, not single frames. It pulls a full-size frame only to settle something a sheet or a flag raises (text near the margin, face under an overlay, caption legibility).

**Who looks**
- A delegated helper (order in `pipeline/delegation.md`) may **pre-screen** sheets during a stage and list the timestamps worth a look. A pre-screen never passes anything.
- **Final visual QA before deliverables is done by the `vision-qa` subagent below, looking at every contact sheet** (and one keyframe per scene in `--thorough`), plus the report's flags and intervals. Every flag, freeze, silence or black interval is either explained (an intended hold, the end card) or fixed.

## When I ask you to look at a video
Whenever a prompt asks to check, review, inspect, QA or "look at" a video, its frames, captions, cuts or edits:
1. Run video-inspect first (`pipeline/video-inspect.md`, as a heavy job, `pipeline/delegation.md`). Never dump frames as images.
2. Read `report.json` (`summary` and `flags` first).
3. The `vision-qa` subagent (Opus; `pipeline/video-inspect.md`) judges `contact_sheet.jpg`, the flagged frames and one keyframe per scene (framing, colour, pacing, quality) and returns text: `timestamp · what · severity · fix`. Read that, not the images (exceptions: the 3 approval stills, an ambiguous report).
4. Use `--thorough` for the final check before publishing.
5. Report issues with timestamps and a proposed fix for each.

## Vision subagent (images stay out of the main session)
Every look at stills, contact sheets, keyframes, flagged frames or carousel slides runs in a subagent; the main session reads its text report, never the images.
- **Agent:** always the `vision-qa` subagent (`.claude/agents/vision-qa.md`). Its frontmatter pins the creative tier (Opus), whatever the main session runs (`config/model-routing.json` → `subagents.vision_qa`, `same_as_main: false`), and gives it read-only tools. Never a cheaper model for final judging (the restate test in `pipeline/qa.md` is the one exception). Final QA is always fresh: never an `inspect_cache` bundle.
- **Its prompt:** the image paths; `report.json` `summary` + `flags` when there is one; the beat list (storyboard rows or script beats with times and layout state); and the instruction to read and follow `brand.md`, `CLAUDE.md` (Quality bar, Inspecting a video, Creative direction) and the checklist that applies (`pipeline/qa.md` Frames, `pipeline/composition.md` Checks, or `pipeline/carousel.md` QA). Those rules win over its own taste.
- **It returns text only:** one line per issue, `timestamp · what · severity (blocker / fix / nit) · proposed fix`, then the OK beats listed briefly (`0:00–0:12 OK`). Flags it can't settle say "ambiguous" with the frame path.
- **Main session:** reads the report, decides fixes, re-runs the subagent on the fixed frames. A pre-screen or report is still a lead; a pass means `vision-qa` looked at every sheet.
- **Exceptions that stay in the main session:** the **3 approval stills** (and the carousel slide-1 look) that I must see, and opening one specific frame when a subagent report is ambiguous.
- Look at sheets in the stage that needs them, then hand off; don't carry sheets from an earlier stage (`pipeline/stages.md`).

**Checks**
- The job's batch or log includes `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` sampled during the Whisper and OCR stages, and the Ollama log line `offloaded N/N layers to GPU`. Any stage on the CPU (except MediaPipe) is a failure, not a pass (`pipeline/gpu.md`).

**Gotchas**
- Never name a script `inspect.py` (shadows the stdlib; numpy import fails).
- Phone footage has a 90° rotation flag: read rotation and swap width/height.
- Use `qwen2.5vl:3b` (7b on ≥ 8 GB), not moondream; partial GPU offload on 4 GB is a stated limit, not a silent fallback.
- Unload Ollama models before Whisper (kept-alive VRAM causes OOM); the tool does it.
- Never `ollama run` from a non-TTY with open stdin (hangs): use the HTTP API or `< /dev/null`.
- `pip check` complaining that scenedetect needs `opencv-python` is expected (headless OpenCV).
- The first PaddleOCR run downloads its models (~30 s).
- B-roll needs a manual quality pass per scene (sharpness, luma, camera shake, motion); no tracked tool does it yet.
- Shake measures: zero the jitter within 0.4 s of each scene boundary (hard cuts read as shake).
- `freezedetect` omits `freeze_end` at end of file: close it at the duration (the tool does).
- Desk footage can show private screens: check monitors on the sheet before any punch-in, and blur when unsure.
- No flag catches an unbuilt scene: match every storyboard row to a component and look for blank SPLIT cards.
- `text_over_face` on tiny strings like `ATX3` is the wall sticker: false positive.
- `caption_desync` can match an earlier short word, and `misspelling` fires on code/tokens: check the timeline time first.
- Spring-morph reels give few scenes: always view the 48-tile contact sheet too.
- With CTC captions, `caption_desync` +0.5–1.4 s is usually Whisper bias or footer text: check 2–3 against the envelope before touching the timeline.
- Between back-to-back inspect runs, wait for an empty `--query-compute-apps` (OOM).
- `--thorough` keyframes stop at `DUR − 0.1` (an end frame comes back empty); keep that in the tool.
