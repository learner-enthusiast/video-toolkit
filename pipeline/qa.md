# QA

**Goal:** catch every visible or audible defect before telling me it's done.

**Frames**
- Extract one frame from the middle of every beat of every deliverable to `work/qa/final/`. Tile them into contact sheets of about 12 frames, with a video-inspect report for each deliverable (`pipeline/video-inspect.md`). Extraction and tiling are low-stakes (delegation order in `pipeline/delegation.md`); measuring and video-inspect runs are heavy exact-command jobs (Haiku batch).
- Opus looks at every sheet itself. A subagent pre-screen can point at timestamps but never passes anything. Explain or fix every freeze, silence and black interval in the report.
- Check: no overlay covers my face, no text is cut off or outside the 5% margin, captions are readable and not under the bubble, no stretched video, and the grade is consistent.
- For screen beats, check that the zoom target is the thing being talked about.
- Render one still per beat in a single bundle (`renderStill` in a loop, half scale) and tile them; it catches layout bugs before the full render. Also sample the delivered MP4 every 5 s: gaps between two scenes (an empty card during a pause) only show up there.

**A/V sync**
- Compare against the source at the start, middle and end: correlate picture motion and the audio envelope of the output vs. the source segment it came from. The offset must be 0 ±1 frame.
- Push-ins on the face defeat motion correlation. Note those beats instead of forcing a number.

**Audio**
- Integrated loudness is -16 ±0.5 LUFS and true peak ≤ -1.5 dBTP.
- Listen at every cut point in the rough sheet for clicks or clipped words.

**Report**
- Final durations and loudness, choices made, lines worth re-recording, and anything not done exactly as specified (with the reason).
- Fix failures and re-run the failing checks. Never report a pass that wasn't measured.
- Re-transcribing the delivered (sped-up) video with Whisper to check script coverage: it hallucinates ("Bye. Bye. …" over the end card, "free" for "cheap to write", "REST" for "while the frontend waits" on `graphql-vs-rest`). Settle every missing line with `ctc_score.py` on the final audio before calling it missing.
- Sped-up edits (`setpts=PTS/k` + `atempo=k`, output `-r 30`): ffmpeg's CFR output duplicated the first 2 frames, so the picture ran a constant ~60 ms behind the voice (`redis-interview`). Audio checks against the voice track don't catch it. Also compare plate frames against the source frames the EDL + speed map them to (`work/scripts/qa_sync.py` in that project): the best match must be offset 0. Fix: drop the extra leading frames (`trim=start_frame=N,setpts=PTS-STARTPTS`) so the frame count equals round(cut frames / k). Better: put an `fps=30` filter right after `setpts` (`setpts=PTS/k,fps=30`); it gives exactly round(cut frames / k) frames at offset 0 with no trim (`bloom-filter`, 1.10x: 5,830 → 5,300). Don't combine it with the trim, or the picture runs early.
- Lip-sync by jawOpen-vs-audio-envelope correlation is useless for a teleprompter talker: corr 0.04–0.27 with lags −8…+5 frames even on the raw source (`scion`). Measure picture sync instead with motion energy: the output face panel's mean abs frame diff vs the source frames the EDL + speed map to, inside 4–11 s uncut segments, lag search ±8 (`scion` `work/scripts/qa_sync2.py`, corr 0.63–0.87).
- Remotion `OffthreadVideo` with `trimBefore` + `playbackRate` 1.23 showed the picture a constant 1–2 output frames LATE vs the voice (no drift) on `scion`. An advance of 2 source frames over-corrected (median lag −1.5 → +1.5 over 8 segments); 1 source frame centres it. One segment's lag is noisy (±1.5 frames): always take the median over ≥ 8 segments with corr > 0.5 before and after a fix.
- `SYNC_SRC_FRAMES` in `Presenter.tsx` is per plate, not a constant to copy: scion's +1 made `docker-explained`'s picture ~0.7 frames early on average (lags −1…+2). Measure both sides before changing it: `qa_sync2.py` (picture) and `qa_audio_lag.py` (voice envelope vs the source segment, time-scaled: +10 ms on every segment there, so the voice was exact and only the picture offset needed fixing).
- The "advance 1 source frame" fix from `scion` over-corrected on `jwt-explained` (Remotion 4.0.541, `playbackRate` 1.05): the motion-energy check measured the picture +1 source frame EARLY in 5 of 6 HEAD windows (corr 0.75–0.89). Without the advance it measured −1 (picture late) in 5 of 6 windows, so the true offset is ~½ frame either way: both pass 0 ±1. Measure first; don't chase a half-frame with re-renders. Only correlate FULL-mode windows on a reel: in SPLIT the face is a scaled square crop, and a fixed crop compares the graphic card against the face (corr ≈ 0.1, meaningless).
