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
- Teleprompter recordings: pauses carry room noise and breaths around −45 dB, so the "room tone + 10 dB" silence threshold finds no silence and keeps multi-second gaps. Raise the margin until the pauses go (20 dB on `kafka` and `redis-invalidation`, speech ≈ −12 dB), then check every cut edge's 20 ms is below −35 dB and nudge the rest to the quietest frame boundary within ±100 ms.
- MFA also parks short words ("then", "the", "one") on breaths inside long pauses, which keeps the pause as "speech". Look for words that start > 1 s from Whisper's time and sit at < −30 dB; pin them from the 50 ms energy envelope (a `TIME_FIX` list in the EDL config) rather than trusting either aligner.
- Whisper can invent repeats ("cache cash logic"): settle every "repeat" with CTC before cutting it (`redis-invalidation`: one "cache").
- Don't align a whole recording as one MFA utterance. On `rate-limiter` (5:27, one utterance) MFA drifted 1–8 s around retakes and put a kept retake inside the cut take. Split the corpus into utterances at real pauses (energy gaps ≥ 0.5 s; place each word by its Whisper end − 0.1 s, since Whisper stretches starts back into silence; merge one-word chunks) and align a TextGrid. Then compare MFA to a CTC greedy decode over every chunk: median offset ≈ −0.07 s, and any word off by > 0.35 s marks a problem.
- All Whisper passes (plain, VAD, disfluency) can collapse a real restart ("once someone logs in, the… once someone logs in, limit…"; "user, key… user, key, or phone"). The CTC chunk scan (difflib against the corpus, look for inserted words) found both on `rate-limiter`; MFA drift in a stretch with no retake is the tell.
- One-take teleprompter reads (no retakes, `ag-ui`): skip MFA. An energy EDL is enough: 10 ms RMS, speech threshold −24 dB (±2 frame smoothing), compress gaps to 0.25 s, then snap each cut to the quietest 30 fps frame boundary inside its gap (plain rounding put 15 edges into speech). Don't merge short "breath" bursts between gaps: a −19 dB burst was the soft "th" of "they" and merging it clipped the word.
- Before cutting a "stumble" Whisper reports inside continuous speech, check the duration and energy: on `oidc`, "OpenID 2 bundle 2.0" was 0.9 s of unbroken speech (no dip below -17 dB), the natural length of "OpenID 2.0", and pass B heard just that. MFA squeezing the extra words into 0.03–0.07 s each is the tell. Don't cut it.
- Two-part recordings (`RANGE`/`SUFFIX` configs): give each part only its own `CUTS` (`build_edl.py` exits on a phrase outside its range), and list `TIME_FIX` pins latest-first. A word already moved can otherwise land within 0.3 s of a later pin for the same word and make it ambiguous (`oidc` step-6 retake).
- Re-transcribe the cut voice (plate `voice.wav`) and read it against `script.md` before composing. On `rag-pipeline`, all three source passes collapsed "evaluation, measure… measure retrieval" (3 s apart) into one "measure"; the energy EDL then cut "evaluation" and kept a stray "measure". Only the cut-voice pass showed it ("ask about measure measure retrieval").
- Rendering a cut's PICTURE with one `trim` branch per segment from a single 1080x1920 input buffers every branch's frames in RAM: 44 segments hit the kernel OOM killer at 16 GB (`jwt-explained`, exit 137). Audio `atrim` branches are fine. For picture use one `select='between(n,f0,f1-1)+…',setpts=N/(30*TB)` stream (frame-exact, no buffering).
- Look at frame 0 of the cut: on `jwt-is-dead` it landed mid-blink, 0.1 s before the first word. Start the first segment on an open-eyes frame a few frames earlier (`first_in` in the EDL config), then shift the word times by the added frames / speed.
