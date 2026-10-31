# Take selection

**Goal:** a tight edit decision list (EDL) of my best takes, in `work/edl.json` and `work/cutlist.md`.

**Do**
- Match the transcript to `script.md` paragraph by paragraph.
- For each paragraph keep the **LAST complete, clean take**. Earlier takes are rehearsals.
- Remove false starts ("a story, ranked set…" → "ranked set…"), fillers, coughs, restarts and dead pauses.
- Compress pauses over 0.4 s to about 0.22 s between sentences and 0.15 s within one. Leave about 0.25 s between beats.
- Snap every cut to a 30 fps frame boundary. Cut in the silence just before a word's onset, never mid-word.
- Keep what I actually said. Captions follow my real words. If a slip changes the meaning, prefer cutting the phrase over faking it, and tell me.
- `work/cutlist.md`: per beat, the output range, then a table of source in/out and spoken text.

**Gotchas**
- MFA word edges can sit inside speech (about 1 in 5 cuts on `sql-vs-nosql`). Snap every cut to measured silence: the first quiet 10 ms run (≥ 60 ms, below room tone + 10 dB) after the last kept word, and the last one before the next. Then check that the 20 ms at every edge is near room tone.
- Don't start the silence search before the word's end, or a stop-consonant closure inside the word (the "d" in "decide") reads as silence.
- A false start often runs straight into its retake with no silence ("…interviewer then the interviewer asked"). Search for silence on each side of the removed span separately; searching the whole gap finds the pause BEFORE the false start and keeps it in. Where there is no silence, cut on the MFA edge, then nudge to the 10 ms energy dip within ±100 ms and list those cuts for a listen (`bloom-filter`).
- MFA parks the first word in the leading silence; take Whisper's time for it. Don't "fix" other words from Whisper, because Whisper collapses repeats ("you say, you say").
- Render cuts with `trim=start_frame/end_frame` and `atrim=start_sample/end_sample` (1,600 samples per frame at 48 kHz). Time-based `trim` sometimes takes one boundary frame too many, and `concat` then pads the audio to match (+10 frames over 48 cuts).

**Report at the checkpoint**
- Durations before and after.
- Missing paragraphs.
- Lines where my delivery was weak or misspoken (candidates to re-record), and how each was handled if I won't re-record.

**Checks**
- Render the 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4` and listen through it.
- No clipped word starts or ends. Then stop and wait for my OK.
