# Transcribe

**Goal:** word-level timestamps you can trust, in `work/transcript.json` and `work/transcript.srt`.

**Do**
- Use local faster-whisper (or the whisper-ctranslate2 CLI) with `large-v3`, language set explicitly, word timestamps on, through `gpu-run`. Never use the paid API.
- Run it on `work/audio/clean.wav`.
- Run 2–3 passes and compare them:
  - a plain pass
  - a VAD-chunked pass (catches words dropped across long pauses)
  - a disfluency pass with an initial prompt full of "um, uh, so…" (Whisper hides fillers otherwise)
- Where passes disagree or a word is doubtful, re-transcribe just that short window. Then settle it with wav2vec2 CTC forced alignment of the candidate phrasings, which scores what was actually said.
- Feed the domain vocabulary (tech names from `script.md`) as the initial prompt so terms come out spelled right.

**Checks**
- Every script paragraph is found in the transcript, or reported as missing.
- Word times are monotonic, with no zero-length words. Spot-check 3 words against the waveform.

**Gotchas**
- Whisper confidently "fixes" misspoken words to the script. When the aligner and the audio disagree with Whisper, trust the audio.
- Keep logs in `work/logs/`; the console output is huge.
- The VAD pass can drop a whole sentence (on `redis-interview` it dropped a 3 s interviewer question) and merge two takes across a part join. Re-transcribe those windows on their own; their word times are better than either full pass.
- whisper-ctranslate2 can die with "CUDA failed with error out of memory" late in a file while still printing "Transcription results written" and leaving the output folder empty. Check the JSON exists and grep the log for "out of memory". On `bloom-filter` the prompt-conditioned pass A died at 2:52 twice on an otherwise idle 4 GB card (also at `int8`); `--condition_on_previous_text False` fixed it.
- The VAD pass (B) can also invent sentences in pauses ("In the end, it was a total failure.", `rate-limiter`). Treat any B-only line as a hallucination until CTC confirms it.
- Whisper word STARTS on the final (cut, sped-up) voice run early: median +0.20 s (p90 +0.38 s) on `scion`, because it stretches each start back into the preceding pause. Captions and every word-triggered visual landed early. Fix before building the timeline: CTC greedy-decode the whole voice (wav2vec2, 20 s windows), match words with difflib, take the CTC onset − 0.03 s, interpolate the offset for unmatched words (`scion` `work/scripts/align_ctc.py`, 70% matched). Spot-check 3 words against a CTC window decode afterwards.
- wav2vec2 CTC (`wav2vec2-large-960h-lv60-self`) in fp16 returns ALL blanks for windows over ~10 s (no error, 0 words; `jwt-explained`). Run it in fp32 with 8 s windows + 1 s overlap (~1.5 GB, fits beside another job), and reject CTC−Whisper offsets outside −0.3…+0.8 s as difflib mismatches (interpolate those instead).
- The cut-voice Whisper pass can ALSO collapse a retake: on `docker-is-dead` it read "He says Docker is dead, and in 2022, Kubernetes… He says Docker is dead and in 2022 Kubernetes really did stop using it" as one sentence, so 3.5 s of a false start survived into the voice. Before building captions, run a windowed CTC decode of the whole cut voice (8 s windows, 7 s hop) and diff it against `script.md` (`docker-is-dead` `work/scripts/ctc_scan.py`): any REPLACE/INSERT block that is longer on the CTC side than the script and isn't a number/acronym spelling ("o c i", "two fifty six") is a hidden repeat. Fix the EDL, then re-run the voice chain.
- Whisper can hide a whole retake inside one stretched word: on `jwt-is-dead` "assertions." ran 2.4 s and swallowed a 3.3 s retake of the same line, leaving 2.5 s of apparent dead air after the cut. After building the timeline, list every word longer than 1 s and CTC-decode its window before trusting it.
- CTC onsets more than +0.45 s after Whisper's start are usually difflib mismatches (`jwt-is-dead`: "default." landed on Whisper's END of the word, so captions ran 0.6–0.8 s late near the end). Don't take Whisper + offset blindly either: sentence starts after a pause are where Whisper stretches back. Take the energy onset between the two times (first rise above −28 dB after ≥ 60 ms below −35 dB), else Whisper + the median offset (`jwt-is-dead` `work/scripts/clamp_ctc.py`).
- CTC onsets (`align_ctc.py`, onset − 0.03 s) still ran a median 0.115 s LATE (p90 0.31 s) against the real speech onset on `docker-is-dead` (1.30x voice), measured on the 103 words that follow a pause. video-inspect's `caption_desync` flags are dominated by its own Whisper running early, so don't trust those numbers; measure against the energy envelope instead. Fix: `work/scripts/retime_onsets.py` snaps each pause-led word to its quiet→loud onset (≥ 50 ms below −35 dB, then > −28 dB, searched in [s − 0.4, s + 0.15] s) minus 0.03 s and interpolates the correction for the words in between (median after: −0.03 s). Run it on `timeline.json` before the first render; every `at()` trigger moves with it.
