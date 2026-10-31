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
