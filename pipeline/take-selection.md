# Take selection

**Goal:** a tight edit decision list (EDL) of my best takes, in `work/edl.json` and `work/cutlist.md`.

**Do**
- Match the transcript to `script.md` paragraph by paragraph.
- For each paragraph keep the **LAST complete, clean take**. Earlier takes are rehearsals.
- "Namoshkar!" and "Bye bye, sayonara!" are script lines. Never cut them as greetings or filler.
- Remove false starts ("a story, ranked set…" → "ranked set…"), fillers, coughs, restarts and dead pauses.
- Compress pauses over 0.4 s to the House numbers pause length (`CLAUDE.md`), between and within sentences and between beats.
- Snap every cut to a 30 fps frame boundary. Cut in the silence just before a word's onset, never mid-word.
- Keep what I actually said. Captions follow my real words. If a slip changes the meaning, prefer cutting the phrase over faking it, and tell me.
- `work/cutlist.md`: per beat, the output range, then a table of source in/out and spoken text.

**Tools** (run from `work/`; paths relative to the toolkit root; settings in `work/config/`, `pipeline/job-results.md`)
- `vt-python tools/cut/build_cfg.py --config config/build_cfg.json` writes `config/build_edl.json` from the CTC source decode: sentence/beat onsets, pauses, `pins`, `insert_after`, `end`/`last_out` from `bye_end`.
- `vt-python tools/cut/build_edl.py config/build_edl.json`, then `tools/cut/nudge_edges.py` (loud edges) and `tools/cut/render_cut.py <K>` (voice and preview filter scripts).

**Report at the checkpoint**
- Durations before and after.
- Missing paragraphs.
- Lines where my delivery was weak or misspoken (candidates to re-record), and how each was handled if I won't re-record.

**Checks**
- Render the 720p rough cut (talking head + clean audio) to `out/roughcut_preview.mp4` and listen through it.
- No clipped word starts or ends. Then stop and wait for my OK.

**Gotchas**
- A cut starting at Whisper's word end can swallow the next word: diff the cut voice against the script and decode each cut edge (CTC window + 20 ms energy).
- MFA edges can sit inside speech: snap each cut to a measured quiet run (≥ 60 ms below room tone + 10 dB) on both sides; check every edge's 20 ms is near room tone.
- Start the silence search at the word's end, or a stop closure inside the word reads as silence.
- False start into retake: search silence on each side of the removed span separately; with none, cut on the MFA edge, nudge to the 10 ms dip (±100 ms) and list for a listen.
- MFA parks the first word in the leading silence: use Whisper's time for that word only (Whisper collapses repeats elsewhere).
- Render cuts with `trim=start_frame/end_frame` and `atrim=start_sample/end_sample` (1,600 samples per frame); time-based `trim` adds frames.
- Teleprompter pauses sit near −45 dB: raise the silence margin (~20 dB) until they go; every edge's 20 ms below −35 dB, else nudge to the quietest frame within ±100 ms.
- MFA parks short words on breaths: for starts > 1 s from Whisper at < −30 dB, pin from the 50 ms envelope (`time_fix` in `work/config/build_timeline.json`).
- Whisper invents repeats: confirm every repeat with CTC before cutting it.
- Never align a recording as one MFA utterance: split at pauses ≥ 0.5 s (word = Whisper end − 0.1 s), then compare to CTC per chunk; > 0.35 s off is a problem.
- Every Whisper pass can collapse a real restart: diff a CTC chunk scan for inserted words; MFA drift with no retake is the tell.
- One-take reads: energy EDL, no MFA (10 ms RMS, −24 dB, ±2 frames, gaps 0.25 s, quietest frame in each gap). Never merge short breath bursts: soft consonants clip.
- Check duration and energy before cutting a 'stumble' inside unbroken speech; MFA squeezing extra words into 30–70 ms each means don't cut.
- Two-part recordings: one `build_edl` config per part (own range, cuts, `out`). List `time_fix` pins latest-first.
- Re-transcribe the cut voice and read it against `script.md` before composing: source passes can all collapse a repeat that only the cut pass shows.
- Never use one video `trim` branch per segment (RAM OOM). Picture: one `select='between(n,f0,f1-1)+…',setpts=N/(30*TB)` stream; audio `atrim` branches are fine.
- Check frame 0 for a mid-blink: start on an open-eyes frame (`first_in`) and shift word times by the added frames / speed.
- A −30 dB breath can pass a −32 dB threshold: any cut-voice word > 1 s → check the source energy and add an explicit cut.
- A requested beat pause with no source silence: find the dip from energy runs (not Whisper) and splice real pause with `hold_inserts: [[split_t, sil_a, sil_b]]`; hide with a punch-in.
- Phone/home-room setup: use `thresh_db` −29 (breaths at −29…−34 dB survive −32); check the cut-voice Whisper for words > 0.9 s.
- Onset snapping uses the EDL's speech threshold and searches up to +0.9 s after Whisper's start (it puts sentence starts on the breath).
- CTC parks the first and last words early: pin them from the 10 ms envelope (`pins` in `work/config/build_timeline.json`) before anchoring the opener hold or end card.
- Keep `end` at `last_out` (sayonara + ~1.25 s). After every EDL, assert no segment has `end <= start` and frame sum = rendered voice length.
- Run the windowed CTC source decode (8 s / 7 s hop) before choosing takes: Whisper can merge a short retake into one sentence.
- Long reads: Whisper drifts seconds. Snap sentence starts from the windowed CTC decode (last energy start −0.45/+0.06 s from the CTC time).
- Hook-first reorder of a first-recorded "Namoshkar!": `insert_after: [[hook_end, a, b]]` in the `build_edl` config.
