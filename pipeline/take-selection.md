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

**Report at the checkpoint**
- Durations before and after.
- Missing paragraphs.
- Lines where my delivery was weak or misspoken (candidates to re-record), and how each was handled if I won't re-record.

**Checks**
- Render the 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4` and listen through it.
- No clipped word starts or ends. Then stop and wait for my OK.
