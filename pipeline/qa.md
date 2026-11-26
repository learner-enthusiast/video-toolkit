# QA

Any Whisper pass here is post-production verification only and must consume a deliverable whose audio derives from the Prep-verified cleaned recording. It does not replace or bypass the Stage 1 voice-cleaning gate; do not use QA transcription on raw or unverified footage to bootstrap production.

**Goal:** catch every visible or audible defect before telling me it's done.

**Frames**
- Extract one frame from the middle of every beat of every deliverable to `work/qa/final/` (these are also the face and margin checks). Tile them into contact sheets of about 12 frames, with a video-inspect report for each deliverable (`pipeline/video-inspect.md`). Extract and tile directly; measuring and video-inspect runs are heavy jobs (`pipeline/delegation.md` §5). **Final pre-publish inspect is never restored from cache:** run a fresh `--thorough` video-inspect on the current deliverable (`tools/inspect_cache.py lookup --for-final` always reports `final_qa_requires_fresh_run`).
- The **creative** tier vision subagent reviews every sheet (`pipeline/video-inspect.md`, `config/model-routing.json`); the main session (often **production** tier) reads its text report only. A cheaper pre-screen can point at timestamps but never passes anything. Explain or fix every freeze, silence and black interval in the report.
- Check: no overlay covers my face, no text is cut off or outside the 5% margin, captions are readable and not under the bubble, no stretched video, and the grade is consistent.
- For screen beats, check that the zoom target is the thing being talked about.
- Render one still per beat in a single bundle (`renderStill` in a loop, half scale) and tile them; it catches layout bugs before the full render. Also sample the delivered MP4 every 5 s: gaps between two scenes (an empty card during a pause) only show up there.

**Tools** (run from `work/`; paths relative to the toolkit root)
- `tools/qa/qa_inspect.sh ../out/<main>.mp4 ../out/<trailer>.mp4`: decode check, video-inspect (`--thorough` on the first) and 5 s contact sheets. A heavy job.
- Sync: `vt-python tools/qa/qa_sync_direct.py --video ../out/<main>.mp4` (this episode's HEAD spans and zooms from `plan.ts` go in `config/qa_sync.json`); `tools/qa/qa_sync2.py` (picture, SPLIT panel) and `tools/qa/qa_audio_lag.py` (voice).

**A/V sync**
- Compare against the source at the start, middle and end: correlate picture motion and the audio envelope of the output vs. the source segment it came from. The offset must be 0 ±1 frame.
- Push-ins on the face defeat motion correlation. Note those beats instead of forcing a number.

**Audio**
- Integrated loudness and true peak meet `CLAUDE.md` → House numbers.
- Listen at every cut point in the rough sheet for clicks or clipped words.
- Run the sound checks in `pipeline/sound.md` (SFX onsets 1–3 frames early, mix spectrogram in `work/qa/`) and the voice-over-music checks (`pipeline/music.md`).

**Restate test (fresh eyes)**
- Run once per video, on the main video, after its 5 s beat sheet exists.
- Spawn one fresh sub-agent with no project context: it must not read `script.md`, `log.md`, `CLAUDE.md` or anything else. Give it only the beat sheet images. Use the cheapest model with vision.
- Ask it: "In three lines: what does this video teach, who is it for, and what is the one takeaway?"
- Compare its answer with the `**Message:**` line in `script.md`. If they don't match, name the beats whose visuals don't carry the point and propose a fix for each.
- Its answer is a lead, never a pass (same rule as every sub-agent pre-screen). Log the result.

**Report**
- Final durations and loudness, choices made, lines worth re-recording, and anything not done exactly as specified (with the reason).
- Fix failures and re-run the failing checks. Never report a pass that wasn't measured.

**Gotchas**
- Don't judge script coverage by re-transcribing the sped-up delivery (Whisper hallucinates): CTC-decode each 'missing' line (`tools/captions/ctc_window.py`).
- Speed-up chain is `setpts=PTS/k,fps=30` + `atempo=k` (offset 0, no trim). Also compare plate frames with their source frames; voice checks miss it.
- Measure picture sync by motion energy (`tools/qa/qa_sync2.py`, 4–11 s uncut segments, ±8 lag), not jaw-open correlation.
- `OffthreadVideo` + `playbackRate` can lag 1–2 frames: take the median over ≥ 8 segments with corr > 0.5 before and after any fix.
- `SYNC_SRC_FRAMES` is per plate: measure picture and voice first; only FULL-frame face windows (never SPLIT). 0 ±1 passes; don't re-render for half a frame.
- A 5 s beat-sheet tile shows ~2.5 s after its stamp: read its caption before calling a scene late or empty.
- Also render a still ~12 frames after every scene start: late base layouts pass end-of-scene stills.
- Mark a wrong option loudly (e.g. a `Stamp`) the moment it's called wrong; grey strikethrough reads as the answer.
- Fixed-height blocks clip silently: zoom into chip and code rows at full size in the vision pass.
- Never copy a tool into a project; re-take HEAD/emphasis spans from `plan.ts` into `work/config/qa_sync.json`.
