# Transcribe

**Goal:** word-level timestamps you can trust, in `work/transcript.json` and `work/transcript.srt`.

**Do**
- **Before any Whisper/ASR on talking-head audio, pass the gate in `pipeline/voice-cleaning.md`. No exceptions without my explicit approval.**
- Use local Whisper `large-v3`, language set explicitly, word timestamps on. Never use the paid API. Run each pass through the cache wrapper from `work/` (toolkit-root tool path): `vt-python tools/captions/transcribe.py .. <wav> --out-dir transcript/<pass> -- <whisper-ctranslate2 flags>`. It calls `gpu-run` itself, fails when no JSON appears, and reuses a pass only when the WAV hash, model, flags and wrapper all match.
- Run it on the verified cleaned WAV mapped to that recording in the Prep handoff. `work/audio/clean.wav` is valid only when it is a working copy of a specific verified cleaned WAV. For multiple recordings, maintain distinct cleaned WAVs and reports, and write transcript outputs under `work/transcripts/<recording-id>/` (for example, `transcript.json` and `.srt`); do not reuse one generic input or overwrite prior outputs. Combine transcripts only after preserving each recording's identity and timestamps.
- Run 2–3 passes and compare them:
  - a plain pass
  - a VAD-chunked pass (catches words dropped across long pauses)
  - a disfluency pass with an initial prompt full of "um, uh, so…" (Whisper hides fillers otherwise)
- Where passes disagree or a word is doubtful, re-transcribe just that short window. Then settle it with wav2vec2 CTC forced alignment of the candidate phrasings, which scores what was actually said.
- Feed the domain vocabulary (tech names from `script.md`) as the initial prompt so terms come out spelled right.

**Tools** (run from `work/`; paths relative to the toolkit root)
- Cut voice → caption times: `gpu-run vt-python tools/captions/align_ctc.py audio/voice.wav transcript/cut_words.json transcript/words_ctc.json`, then `tools/captions/clamp_ctc.py`, `tools/captions/build_timeline.py`, `tools/captions/retime_onsets.py` and `tools/captions/fix_starts.py` (both take `audio/voice.wav remotion/public/data/timeline.json`).
- Settle doubts: `tools/captions/ctc_window.py` or `ctc_windows.py` (literal CTC decodes, `gpu-run`); `tools/captions/ctc_scan.py` finds hidden repeats against the script.

- Hindi twin: `transcribe.py --language hi`, then captions only through `tools/captions/hindi_captions.py` (it uses `align_mms.py`, never the English `align_ctc.py`).

**Checks**
- Every script paragraph is found in the transcript, or reported as missing.
- Word times are monotonic, with no zero-length words. Spot-check 3 words against the waveform.

**Gotchas**
- Whisper 'fixes' misspoken words to the script: when the aligner and audio disagree with it, trust the audio.
- Keep logs in `work/logs/`; console output is huge.
- The VAD pass can drop a sentence and merge takes at a part join: re-transcribe those windows alone.
- whisper-ctranslate2 can OOM late yet claim success: check the JSON exists and grep 'out of memory'; `--condition_on_previous_text False` can fix it.
- The VAD pass can invent sentences in pauses: treat a VAD-only line as hallucination until CTC confirms it.
- Whisper starts on the cut voice run ~0.2 s early: align with CTC (onset − 0.03 s) before building the timeline, then spot-check 3 words.
- wav2vec2 CTC: fp32, 8 s windows + 1 s overlap (fp16 returns blanks past ~10 s); drop CTC−Whisper offsets outside −0.3…+0.8 s.
- The cut-voice Whisper can hide a retake: run `tools/captions/ctc_scan.py` on a full CTC decode; a longer CTC-side block that isn't a number spelling is a repeat.
- CTC-decode every word longer than 1 s: Whisper can hide a whole retake in one stretched word.
- CTC onsets > 0.45 s after Whisper are mismatches: take the energy onset between them, else Whisper + median offset (`tools/captions/clamp_ctc.py`).
- Run `tools/captions/retime_onsets.py` before the first render. Measure caption timing against the energy envelope, not video-inspect's Whisper.
- Sentence-first words can stay 0.3–1.3 s early: run `tools/captions/fix_starts.py` after the retime, then list words > 0.3 s off CTC; none may start a beat.
- After the retime, count words starting < 2 frames after the previous one (collapsed onsets).
- `timeline.json` times are fractional frames: round them for cues (`resolve_cues.py` does) and `renderStill`.
- Whisper drops short Hindi phrases: check each `MISSING`/`FILLED` line from `build_timeline`, decode the window with `ctc_window.py` and pin the words (`pins`).
