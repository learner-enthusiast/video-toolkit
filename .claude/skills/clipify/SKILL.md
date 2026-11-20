---
name: clipify
description: Find compelling moments in a video — funny dialogue OR repeated impact actions like axe chops, hits, throws, drumbeats — cut them as standalone clips, optionally reformat 16:9 ↔ 9:16, time-warp pans for tighter reveals, and burn opus-style word-by-word captions. Use when the user mentions "clipify," "cut clips from this video," "make shorts from this," "find funny moments," "action montage," "cut on each chop/hit/punch," "reframe to 9:16," "vertical clips," or pastes a video file path and wants social-ready cuts.
---

# Clipify

## Linux adaptation (video-toolkit)

Changed from upstream for this machine; these notes win over anything below.

- **Platform:** Ubuntu 24.04, NVIDIA GPU. `apt` instead of `brew`; `xdg-open` instead of `open`; `-hwaccel cuda` instead of `videotoolbox`; `h264_nvenc` instead of `libx264`/`h264_videotoolbox`. Never fall back to the CPU silently (`pipeline/gpu.md`).
- **Whisper:** `gpu-run whisper-ctranslate2 --device cuda --compute_type float16` (faster-whisper, same flags and JSON shape as openai-whisper) instead of `whisper`/`mlx_whisper`. Models are cached in `~/.cache`.
- **Python:** `vt-python` (the shared user venv with numpy, Pillow, faster-whisper) instead of `python3`.
- **Paths:** work in `projects/<name>/work/<skill>/`, never `/tmp` or next to the source. `raw/` and `assets/` are read-only.
- **Priority:** `CLAUDE.md` and `brand.md` win over this skill's defaults (colors, fonts, caption style, pacing, motion).
- **Use it for:** turning a long video into reels. Each picked clip then goes through `/reel` (hook, safe zones, captions per `components/specs/Captions.md`).
- **Captions:** use `components/specs/Captions.md` (reel mode) instead of the opus/karaoke/minimal ASS presets. Use `build_ass.py` only for quick drafts.
- **Reframing:** 16:9 → 9:16 must never stretch me or crop my face. Prefer `components/specs/FaceTrackedCrop.md`. The hard-cut pan is fine for two-person dialogue.

Find compelling moments in a video, cut them as standalone clips, optionally reformat 16:9 → 9:16 (face-pan or split-screen), time-warp pans for tighter reveals, and burn opus-style word-by-word captions.

## Modes

Pick one before Step 1. The choice changes how you find moments and whether captions apply.

- **Dialogue mode** (default for podcasts, interviews, talking-heads): Whisper transcribes, you scan for punchlines / reactions / awkward pauses. → Step 1A. Captions in Step 5.
- **Action mode** (woodchopping, sports, percussion, drumming, anything with repeated impact sounds): skip Whisper entirely, run `detect_transients.py` to find each strike, cut on each one. → Step 1B. Skip Step 5; the strike sounds *are* the rhythm.
- **Hybrid**: dialogue mode for talking sections, action mode for the rest, intercut. Use both 1A and 1B.

If the user says "I'm not talking in this," you're in action mode. If they say "cut on each X" (chop, hit, punch, drumbeat, swing, footstep), you're in action mode. Default to dialogue mode otherwise.

## Inputs

- A video file path (the user will provide it; otherwise ask)
- Format: 9:16 (toolkit default for clips/reels; see Step 3)
- Optional: subtitle style preference — if not given, ask before captioning

## Tooling (use only the fastest path)

- **Whisper:** `gpu-run whisper-ctranslate2 --device cuda --compute_type float16 --model tiny.en --word_timestamps True --output_format json` (≈10× faster than `small.en`; quality fine for English). For non-English: `--model base` (drop `--language`).
- **ffmpeg:** add `-hwaccel cuda` for decode and `h264_nvenc -preset p1` for draft renders. Use `-c:v h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0` for the final master.
- **Numpy** for audio alignment (FFT cross-correlation). No scipy/cv2 needed.
- **Scripts:** `<skill-dir>/scripts/` (where `<skill-dir>` is the directory containing this SKILL.md — here `.claude/skills/clipify/` in the video-toolkit repo)
  - `analyze.py` — speaker timeline from two ROI motion files
  - `build_pan.py` — ffmpeg crop x-expression with hard cuts
  - `build_ass.py` — opus-style ASS captions from whisper JSON
  - `audio_align.py` — find offset of a sub-clip in a longer source
  - `detect_transients.py` — find sharp impact sounds (action mode); see `--help`

Working dir: `projects/<name>/work/clipify/` (mkdir at start, leave artifacts for debugging).

---

## Workflow

### Step 0 — Gate dialogue/hybrid transcription on voice cleaning

Before Step 1A (or the dialogue portion of Hybrid): If the Prep handoff in `log.md` already maps this recording to a cleaned WAV whose gate passed, use that WAV (`projects/<name>/work/audio/cleaned/<recording-id>.wav`) and skip to the next step. Otherwise (standalone use) run the gate in `pipeline/voice-cleaning.md`: run `vt-python tools/voice_preflight.py` (stop on `NOT READY`), probe the original, assign each talking-head recording an ID, run `vt-python tools/clean_audio.py "$SRC" "projects/<name>/work/audio/cleaned/<recording-id>.wav" --preset studio --mode quality --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"` once per recording, check every report (`status: succeeded`, matching `run_id`, `stages.wpe` and `stages.deepfilternet3` both `processed`, `production_gate.automated_checks_passed: true`), and listen to each original/cleaned pair at matched loudness unless the approved-setup exemption in `pipeline/voice-cleaning.md` applies. A non-zero exit or any failed check: stop and report. If listening is unavailable, disclose it and request explicit approval before Whisper. Never switch modes, transcribe source audio, or overwrite another recording's output/report without explicit approval. Use only the verified cleaned WAV for all ASR, including the full-source candidate scan and clip-level caption timestamps, and for the clip's delivered audio. Keep each recording's files separate. Action mode's transient detector does not invoke Whisper; if Hybrid contains talking-head dialogue, gate that portion before its Whisper pass.

### Step 1A — Find dialogue moments (dialogue mode)

```bash
mkdir -p projects/<name>/work/clipify
ffmpeg -y -i projects/<name>/work/audio/cleaned/<recording-id>.wav -ac 1 -ar 16000 projects/<name>/work/clipify/audio.wav
gpu-run whisper-ctranslate2 --device cuda --compute_type float16 projects/<name>/work/clipify/audio.wav --model tiny.en --word_timestamps True --output_format json --output_dir projects/<name>/work/clipify --language en
```

Read the resulting JSON (or `.txt`) and pick 3–5 candidate clips. Funny signals to scan for:

- **Punchlines and reactions:** words like "what", "wait", "no way", laughter, "haha", swearing
- **Reversal moments:** setup question → unexpected answer
- **Awkward pauses:** Whisper segment with long gap, or filler ("uh", "um")
- **Self-roast / quotable one-liners:** short declarative sentences that stand alone
- **Audio peaks:** detect via `ffmpeg -af volumedetect` or look for rapid back-and-forth (alternating short Whisper segments)

For each candidate, propose: `[start, end, why-it's-funny, suggested title]`. Aim for 10–25s clips. Show the list and let the user confirm/pick.

### Step 1B — Find each strike (action mode)

Action/hybrid mode only: read `references/action-mode.md` (transient detection, tuning, shot timing).

### Step 1.5 — Verify each candidate is in frame

**Always do this before rendering**, in either mode. Audio detection finds the *sound* of an event; the camera might not have captured it. Skipping this is the #1 way to get user feedback like "you cut on chops where I'm not even visible."

```bash
# Sample one frame at each candidate strike time T:
for T in $STRIKE_TIMES; do
  ffmpeg -y -ss "$T" -i "$VIDEO" -frames:v 1 -vf scale=320:-1 \
    projects/<name>/work/clipify/verify_${T}.jpg
done
```

Have the verify images checked by the vision subagent (`pipeline/video-inspect.md`, Vision subagent; one batch, text report back) and drop the candidate if:

- The subject is bent down, off-frame, or behind an obstacle
- A thumb is on the lens (yes, this happens — and you only catch it visually)
- It's clearly a different sound source (door slam, dropped tool) that triggered the detector

For ~30 candidates this is one fast `ffmpeg` call each plus a single batch image read. Cheap insurance.

### Step 2 — Trim each chosen clip

```bash
ffmpeg -y -ss "$START" -t "$DURATION" -i "$VIDEO" -an -c:v copy projects/<name>/work/clipify/clip_$N.mp4
```

(Use `-c copy` for instant trim. Re-encode only if cuts must be frame-accurate.)

### Step 3 — Decide the output format

**Toolkit rule:** clips are reels (≤ 2:59), so the output is **9:16 only**. Don't ask and don't render 16:9 or 1:1 (`CLAUDE.md`, Deliverables). Use another format only if the user explicitly asks for it.

Upstream default (only when the user asks for a non-reel format): "9:16 (TikTok / Reels), 16:9 (YouTube), or 1:1 (Insta feed)?"

### Step 4 — If 16:9 → 9:16: pan-between-faces vs split-screen

Detect source aspect with `ffprobe`. If source is 16:9 and target is 9:16, ask:

> "Two options: **(a) hard-cut pan** that follows whoever is speaking (single face on screen at a time), or **(b) split-screen** stack with both faces visible. Which do you want?"

Skip the question if there's only one face (single-talker clip). For single-talker, just center-crop.

#### Step 4a — Pan-between-faces (recommended for fast-cut talking-head dialogue)

1. **Locate the two face ROIs.** Sample one frame: `ffmpeg -ss <middle> -i <clip> -frames:v 1 projects/<name>/work/clipify/probe.jpg`. Read it. Eyeball each face's mouth+chin area as `x,y,w,h` in the source's pixel space. (No cv2 needed — camera is static within a clip; one frame is enough.) Verify by drawing boxes:

   ```bash
   ffmpeg -i probe.jpg -vf "drawbox=x=$LX:y=$LY:w=$LW:h=$LH:color=cyan@0.9:t=4,drawbox=x=$RX:y=$RY:w=$RW:h=$RH:color=magenta@0.9:t=4" verify.jpg
   ```

   Iterate **at most twice**. Boxes should cover mouth + chin and avoid hands/mics. Don't over-tune — frame differencing is forgiving.

2. **Extract per-frame motion energy in each ROI:**

   ```bash
   ffmpeg -y -i clip.mp4 -filter_complex "
   [0:v]split=2[a][b];
   [a]crop=$LW:$LH:$LX:$LY,format=gray,tblend=all_mode=difference,signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=projects/<name>/work/clipify/L.txt[la];
   [b]crop=$RW:$RH:$RX:$RY,format=gray,tblend=all_mode=difference,signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=projects/<name>/work/clipify/R.txt[ra]
   " -map "[la]" -f null - -map "[ra]" -f null -
   ```

3. **Build speaker timeline** (min dwell 1.0s — short interjections merge into the prior speaker):

   ```bash
   vt-python <skill-dir>/scripts/analyze.py projects/<name>/work/clipify/L.txt projects/<name>/work/clipify/R.txt 1.0 > projects/<name>/work/clipify/segments.json
   ```

4. **Pick pan x-coordinates** for a 9:16 vertical strip from the source. With source W=1920 and target W=1080, crop strip width = 608.
   - LEFT_X = `face_left_center_x - 304` (clamp ≥ 0)
   - RIGHT_X = `face_right_center_x - 304` (clamp ≤ source_W - 608)

5. **Generate the hard-cut x expression and render:**

   ```bash
   EXPR=$(vt-python <skill-dir>/scripts/build_pan.py projects/<name>/work/clipify/segments.json $LEFT_X $RIGHT_X)
   ffmpeg -y -hwaccel cuda -i clip.mp4 -filter_complex \
     "[0:v]crop=608:1080:x='$EXPR':y=0,scale=1080:1920:flags=lanczos[v]" \
     -map "[v]" -an -c:v h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0 -pix_fmt yuv420p \
     projects/<name>/work/clipify/clip_panned.mp4
   ```

   Source 1920×1080 assumed; for 4K source either downscale first or double all coordinates.

#### Step 4b — Split-screen (both faces always visible)

Only when split-screen is chosen: read `references/split-screen.md` (filtergraph, tile crops, audio from the verified cleaned WAV).

### Step 4c — Time-warping reveals (optional)

Only when asked to tighten a slow reveal without trimming: read `references/time-warp.md` (speed-ramp commands and rules of thumb; never retain source-video audio).

### Step 5 — Add subtitles

Skip this step in action mode — the strike sounds are the rhythm and captions just clutter the visual.

Ask once (only if user hasn't already specified a style):

> "Three subtitle styles: **opus** (big bold white, yellow active-word highlight), **karaoke** (4-word chunks, green highlight), **minimal** (clean Helvetica, no highlight). Or paste an example you like."

If they paste a reference image/example: match the font, size, weight, color, position, and animation as closely as possible — write a custom ASS by hand or extend `build_ass.py`.

Else use the preset:

```bash
# Trim the verified cleaned source audio to the selected source interval, then transcribe that cleaned clip.
ffmpeg -y -ss "$START" -i projects/<name>/work/audio/cleaned/<recording-id>.wav -t "$DURATION" -ac 1 -ar 16000 projects/<name>/work/clipify/clip_audio.wav
gpu-run whisper-ctranslate2 --device cuda --compute_type float16 projects/<name>/work/clipify/clip_audio.wav --model tiny.en --word_timestamps True --output_format json --output_dir projects/<name>/work/clipify --language en
# Delivered audio: the same interval from the verified cleaned WAV at 48 kHz (clip_audio.wav is a 16 kHz ASR copy only).
ffmpeg -y -ss "$START" -i projects/<name>/work/audio/cleaned/<recording-id>.wav -t "$DURATION" -c:a pcm_s24le projects/<name>/work/clipify/clip_voice.wav
vt-python <skill-dir>/scripts/build_ass.py projects/<name>/work/clipify/clip_panned.json projects/<name>/work/clipify/captions.ass opus
```

Burn captions:

```bash
ffmpeg -y -i projects/<name>/work/clipify/clip_panned.mp4 -i projects/<name>/work/clipify/clip_voice.wav \
  -vf "subtitles=projects/<name>/work/clipify/captions.ass" -map 0:v -map 1:a \
  -c:v h264_nvenc -preset p5 -rc vbr -cq 20 -b:v 0 -c:a aac -b:a 192k "$OUTPUT.mp4"
```

### Step 6 — Deliver

- Inside a project, save each output to `projects/<name>/work/clipify/out/` (never into `raw/` or `assets/`; chosen clips are finished by `/reel` into `out/`). Outside a project, use `<source_dir>/clipify_out/` (mkdir if missing)
- Print one line per clip: name, duration, what was funny, output path
- Open the first output with `xdg-open <path>` so the user can check it
- Offer to iterate (different style, different ROI, swap to split-screen, retime captions)

---

## Pitfalls (lessons from prior runs — don't repeat)

- **Audio detection ≠ visible event.** Always run Step 1.5 (verify each candidate frame) before rendering. The detector finds the *sound* of a chop, not whether the chopper is in frame. Hits where the subject is bent over, off-camera, or where a thumb is on the lens still trigger the audio detector. Catch them before rendering.
- **Spectral-flux band matters.** Default `--band 1000:6000` covers wood/metal/glass impacts. Heavy low thuds (kick drum, body shots) need `--band 200:2000`. Whistles, clinks, snare cracks need `--band 4000:10000`. If `--min-flux 30` returns nothing, try lowering to 15 first; if it returns thousands, try a different band before raising the threshold.
- **Speed-ramp audio in pairs.** `atempo` accepts only 0.5–2.0 in a single filter; for 4x chain `atempo=2.0,atempo=2.0`. Without `atempo`, `setpts` alone gives chipmunk audio.
- **Don't over-tune ROIs.** Two iterations max. Motion-diff is forgiving — wider ROIs covering mouth+chin work fine even if not perfectly mouth-centered.
- **Watch out for scene cuts inside a clip.** Run `ffmpeg -filter:v "select='gt(scene,0.3)',showinfo" -f null -` to count cuts. If a 16:9→9:16 clip has many cuts, the fixed face ROIs only work for the dominant scene; warn the user, and offer to either pick a single-take clip or accept off-center framing during cuts.
- **Source resolution matters.** If source is 4K, either downscale to 1920×1080 first (faster, fine for 9:16 output) or multiply all ROI/pan coordinates by 2.
- **Burned-in subtitles in source.** Some "raw" clips still have subtitles. If so, find the no-subs master via audio cross-correlation (`audio_align.py`) and trim from there.
- **Don't run whisper on the full feature-length source if a short clip suffices.** Whisper the trimmed clip after Step 2; only whisper the full source in Step 1 if you need a transcript to find funny moments.
- **State the plan in one line, then act.** Don't narrate every iteration.
