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
