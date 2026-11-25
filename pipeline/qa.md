# QA

Any Whisper pass here is post-production verification only and must consume a deliverable whose audio derives from the Prep-verified cleaned recording. It does not replace or bypass the Stage 1 voice-cleaning gate; do not use QA transcription on raw or unverified footage to bootstrap production.

**Goal:** catch every visible or audible defect before telling me it's done.

**Frames**
- Extract one frame from the middle of every beat of every deliverable to `work/qa/final/`. Tile them into contact sheets of about 12 frames, with a video-inspect report for each deliverable (`pipeline/video-inspect.md`). Extraction and tiling are low-stakes (delegation order in `pipeline/delegation.md`); measuring and video-inspect runs are heavy jobs (detached Haiku runner, `pipeline/delegation.md` §6).
- The **creative** tier vision subagent reviews every sheet (`pipeline/video-inspect.md`, `config/model-routing.json`); the main session (often **production** tier) reads its text report only. A cheaper pre-screen can point at timestamps but never passes anything. Explain or fix every freeze, silence and black interval in the report.
- Check: no overlay covers my face, no text is cut off or outside the 5% margin, captions are readable and not under the bubble, no stretched video, and the grade is consistent.
- For screen beats, check that the zoom target is the thing being talked about.
- Render one still per beat in a single bundle (`renderStill` in a loop, half scale) and tile them; it catches layout bugs before the full render. Also sample the delivered MP4 every 5 s: gaps between two scenes (an empty card during a pause) only show up there.

**A/V sync**
- Compare against the source at the start, middle and end: correlate picture motion and the audio envelope of the output vs. the source segment it came from. The offset must be 0 ±1 frame.
- Push-ins on the face defeat motion correlation. Note those beats instead of forcing a number.

**Audio**
- Integrated loudness is -16 ±0.5 LUFS and true peak ≤ -1.5 dBTP.
- Listen at every cut point in the rough sheet for clicks or clipped words.
- Run the sound checks in `pipeline/sound.md` (SFX onsets 1–3 frames early, music ≥ 15 dB under the voice in speech, mix spectrogram in `work/qa/`).

**Restate test (fresh eyes)**
- Run once per video, on the main video, after its 5 s beat sheet exists.
- Spawn one fresh sub-agent with no project context: it must not read `script.md`, `log.md`, `CLAUDE.md` or anything else. Give it only the beat sheet images. Use the cheapest model with vision.
- Ask it: "In three lines: what does this video teach, who is it for, and what is the one takeaway?"
- Compare its answer with the `**Message:**` line in `script.md`. If they don't match, name the beats whose visuals don't carry the point and propose a fix for each.
- Its answer is a lead, never a pass (same rule as every sub-agent pre-screen). Log the result.

**Report**
- Final durations and loudness, choices made, lines worth re-recording, and anything not done exactly as specified (with the reason).
- Fix failures and re-run the failing checks. Never report a pass that wasn't measured.
- Re-transcribing the delivered (sped-up) video with Whisper to check script coverage: it hallucinates ("Bye. Bye. …" over the end card, "free" for "cheap to write", "REST" for "while the frontend waits" on `graphql-vs-rest`). Settle every missing line with `ctc_score.py` on the final audio before calling it missing.
- Sped-up edits (`setpts=PTS/k` + `atempo=k`, output `-r 30`): ffmpeg's CFR output duplicated the first 2 frames, so the picture ran a constant ~60 ms behind the voice (`redis-interview`). Audio checks against the voice track don't catch it. Also compare plate frames against the source frames the EDL + speed map them to (`work/scripts/qa_sync.py` in that project): the best match must be offset 0. Fix: drop the extra leading frames (`trim=start_frame=N,setpts=PTS-STARTPTS`) so the frame count equals round(cut frames / k). Better: put an `fps=30` filter right after `setpts` (`setpts=PTS/k,fps=30`); it gives exactly round(cut frames / k) frames at offset 0 with no trim (`bloom-filter`, 1.10x: 5,830 → 5,300). Don't combine it with the trim, or the picture runs early.
- Lip-sync by jawOpen-vs-audio-envelope correlation is useless for a teleprompter talker: corr 0.04–0.27 with lags −8…+5 frames even on the raw source (`scion`). Measure picture sync instead with motion energy: the output face panel's mean abs frame diff vs the source frames the EDL + speed map to, inside 4–11 s uncut segments, lag search ±8 (`scion` `work/scripts/qa_sync2.py`, corr 0.63–0.87).
- Remotion `OffthreadVideo` with `trimBefore` + `playbackRate` 1.23 showed the picture a constant 1–2 output frames LATE vs the voice (no drift) on `scion`. An advance of 2 source frames over-corrected (median lag −1.5 → +1.5 over 8 segments); 1 source frame centres it. One segment's lag is noisy (±1.5 frames): always take the median over ≥ 8 segments with corr > 0.5 before and after a fix.
- `SYNC_SRC_FRAMES` in `Presenter.tsx` is per plate, not a constant to copy: scion's +1 made `docker-explained`'s picture ~0.7 frames early on average (lags −1…+2). Measure both sides before changing it: `qa_sync2.py` (picture) and `qa_audio_lag.py` (voice envelope vs the source segment, time-scaled: +10 ms on every segment there, so the voice was exact and only the picture offset needed fixing). Same lesson: The "advance 1 source frame" fix from `scion` over-corrected on `jwt-explained` (Remotion 4.0.541, `playbackRate` 1.05): the motion-energy check measured the picture +1 source frame EARLY in 5 of 6 HEAD windows (corr 0.75–0.89). Without the advance it measured −1 (picture late) in 5 of 6 windows, so the true offset is ~½ frame either way: both pass 0 ±1. Measure first; don't chase a half-frame with re-renders. Only correlate FULL-mode windows on a reel: in SPLIT the face is a scaled square crop, and a fixed crop compares the graphic card against the face (corr ≈ 0.1, meaningless).
- The 5 s beat sheet (`fps=1/5,…tile`) samples ~2.5 s AFTER the burned-in timestamp (the `fps` filter rounds to the nearest tick), so a tile stamped 0:10 is the frame at 0:12.5. Read the caption in the tile to place it before calling a scene late or empty (`vectorless-rag`).
- Sheets of the delivered file caught three "base layout arrives late" scenes that the per-scene stills (taken near each scene's end) could not: a title card empty for 0.5 s, bars with nothing on screen for 6 s, a stopwatch row missing for 3.6 s. Also render one still ~12 frames after every scene START.
- The restate test catches "wrong vs right" beats that only read through narration: on `system-design-of-ai/06-cancellation` the fresh agent said the fix is to "listen for req close" (the WRONG one), because the 5 s sample landed while only the struck-through grey `req.on("close")` card was on screen and the right card came 5 s later. Grey + strikethrough was too quiet; a `Stamp` "wrong" on the bad card when the word is said fixed it. Mark a wrong option loudly the moment it's called wrong.
- Fixed-height blocks clip what is inside them: a compact `PromptStack` row (84 px) cut the tool chips' underscores in every request card on `system-design-of-ai/09-prompt-caching`, and the stills QA missed it because the cut chips still read as plain text. Zoom into chip and code rows at full size in the vision pass.
- Scripts copied from the previous episode keep its phrases and file names (`qa_sync_direct.py` HEAD/EMPH spans crashed on #11's words; `deliver.sh` still named `04-cost-metering`): after copying, grep for the old slug and re-take the spans from this episode's `plan.ts` (`system-design-of-ai/09-prompt-caching`).
