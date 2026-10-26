# QA

**Goal:** catch every visible or audible defect before telling me it's done.

**Frames**
- Extract one frame from the middle of every beat of every deliverable to `work/qa/final/`. Tile them into contact sheets of about 12 frames and look at each sheet.
- Check: no overlay covers my face, no text is cut off or outside the 5% margin, captions are readable and not under the bubble, no stretched video, and the grade is consistent.
- For screen beats, check that the zoom target is the thing being talked about.

**A/V sync**
- Compare against the source at the start, middle and end: correlate picture motion and the audio envelope of the output vs. the source segment it came from. The offset must be 0 ±1 frame.
- Push-ins on the face defeat motion correlation. Note those beats instead of forcing a number.

**Audio**
- Integrated loudness is -16 ±0.5 LUFS and true peak ≤ -1.5 dBTP.
- Listen at every cut point in the rough sheet for clicks or clipped words.

**Report**
- Final durations and loudness, choices made, lines worth re-recording, and anything not done exactly as specified (with the reason).
- Fix failures and re-run the failing checks. Never report a pass that wasn't measured.
