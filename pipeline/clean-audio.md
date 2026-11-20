# Clean audio

**Goal:** produce a natural, intelligible 48 kHz mono voice track on the exact source timeline. Room reverb is treated as a separate problem from stationary noise.

**Execution authority:** for production order, per-recording paths, report checks, listening approval, and fail-stop behavior, follow [`pipeline/voice-cleaning.md`](voice-cleaning.md). This file describes implementation details only.

## Entry point

Use `vt-python tools/clean_audio.py INPUT work/audio/cleaned/<recording-id>.wav --preset studio --mode quality --report work/audio/reports/<recording-id>-clean-report.json`, one unique WAV and report per recording (`pipeline/voice-cleaning.md`). Every talking-head source must be cleaned and the report reviewed before Whisper or editing. Preserve the source recording; the cleaner refuses to write inside `raw/` or `assets/`, or onto a report that belongs to another recording. The video flow still reads `work/audio/clean.wav`: that is a copy of one verified cleaned WAV. Quality mode requires WPE and DeepFilterNet 3 and fails with a non-zero exit if either stage cannot run. Do not select the explicit `balanced` or `performance` alternate modes for production without first asking the user to approve that substitute. The cleaner detects the global `deep-filter` executable or user venv and accepts `--deepfilter-executable` / `--deepfilter-python` (also `DEEPFILTERNET_EXECUTABLE` / `DEEPFILTERNET_PYTHON`). Temporary WAVs are isolated and removed automatically; source files are never modified. Output and report are staged and published only after every stage passes. A failed run publishes nothing, writes `<report>.run-<run_id>.failed.json` and marks `<wav>.run-status.json` `failed`, with each stage `processed`, `failed`, `not_attempted` or `disabled`, and exits 1. A preserved WAV from an earlier run is not current unless its report's `run_id` matches a `succeeded` run-status.

The CLI probes input stream rate/channels/duration, measures loudness and true peak before and after, and reports duration delta. It converts the processing copy to mono/48 kHz and does not trim silence. Keep the original video timeline and use the resulting WAV as the replacement audio track.

## Processing stages

1. **Input analysis:** FFprobe checks audio presence, channel count, sample rate and duration. FFmpeg EBU R128 reports integrated loudness, LRA and true peak. Clipping and room-reverb severity are not yet robustly auto-classified; listen and inspect the report.
2. **Dereverberation (separate stage):** offline single-channel WPE (taps 10, delay 3 frames, 3 iterations, 512-point STFT at 16 kHz) predicts late reverberation from delayed STFT frames. It is CPU-only and uses the shared venv's NumPy/SciPy/soundfile. The predicted reverb (16 kHz input − WPE output) is upsampled and subtracted from the 48 kHz signal at the preset strength. Below 8 kHz that equals a dry/WPE blend; above 8 kHz the original passes through, so the voice keeps its air and sibilance. (Before 2026-11-19 the whole voice came back band-limited to 8 kHz.) A clip too short for the filter (under about 0.12 s), a singular solve (`LinAlgError`), non-finite values or an unchanged signal fail the run. WPE chiefly targets the late tail; it does not erase strong early reflections or a discrete slapback echo, and can sound phasey when overused. It is not an inverse-room model.
3. **Neural speech enhancement:** invoke the globally installed DeepFilterNet3 CLI in its own cached Python environment, independent from WPE; conservatively blend the result using `enhancement_strength`. The run counts as processed only if the CLI exits 0, logs a completed enhancement (`RT factor`), writes exactly one WAV of the input's duration (±0.05 s) and that WAV differs from its input. The report records backend, device and real-time factor; a CPU device is reported as a warning. DeepFilterNet3 is a general speech-enhancement model trained with reverberant examples, not a dedicated dereverberator. It can help residual noise and roominess but is not guaranteed to remove a long room tail. Missing/incompatible dependencies stop quality processing; fix the installation or ask before using a substitute.
4. **Residual noise:** modest `afftdn` only; do not treat it as dereverberation. If the recording has a steady hum, inspect it and use a separately targeted notch rather than increasing broadband suppression.
5. **Vocal tone and dynamics:** high-pass at 78 Hz; subtle 260 Hz cut and 3.2 kHz presence lift; gentle compression (2.2:1); mild FFmpeg de-esser. Optional tone/dynamics settings may be adjusted when needed, but do not disable WPE or DeepFilterNet 3 in quality mode without explicit user approval.
6. **Loudness:** single-pass `loudnorm` targets −16 LUFS and −1.5 dBTP. The report measures the output; do not infer compliance from the requested target alone. Shorts/reels may specify another target in their brief.

The cleaner does not time-stretch or trim, so synchronization and pauses remain. WPE uses centered STFT processing and may change edge samples by a few milliseconds; report the duration delta and verify start/middle/end sync before delivery.

## Automated tone check

The report's `tone_change_db` compares the whole cleaned file's per-band tonal shape (80 Hz–20 kHz, level-independent) with its own decoded input, and the cleaner warns past ±6 dB in any band. On `07-provider-failover` the broken run (int16 wrap clicks) scored +11.7 dB at 6–10 kHz and the fixed run at most +2.8 dB. It catches clicks, added hiss and dullness, not subtle artifacts, so it backs up listening only for approved setups (`pipeline/voice-cleaning.md`).

## Gotchas

- **Phone audio is dual mono, and FFmpeg's `-ac 1` adds the two channels at 1/√2 each (+3 dB).** On `system-design-of-ai/07-provider-failover` each channel peaked at 0.802, and the mono fold-down hit 1.134 (+1.09 dBFS, 74,734 samples over full scale). DeepFilterNet 0.5.6 saves int16 without clamping (`df/io.py`), so every over wrapped into a loud click. The cleaned voice came out about 15 dB too bright, crackly and thin, while every report check still passed. Only listening caught it. The cleaner now scales the decoded mono to a −3 dBFS peak before WPE (`processing_headroom_gain_db`; loudnorm restores the level). It also fails the DeepFilterNet stage if its output has full-scale samples or sample jumps > 1.0.
- For any other mono copy of a phone recording (a raw reference, a comparison file), average the channels instead: `-af "pan=mono|c0=0.5*c0+0.5*c1"`. A plain `-ac 1` to 24-bit clips those overs.

## Presets

- `natural`: very low WPE blend, light noise reduction, no compression.
- `studio` (default): conservative WPE, light residual denoise, gentle compression.
- `strong-room`: stronger WPE blend for significant late reverberation; listen for phasey vowels and softened consonants and back off if audible.

Example overrides (`work/audio/clean-config.json`):

```json
{
  "dereverb_enabled": true,
  "dereverb_strength": 0.35,
  "speech_enhancement_enabled": true,
  "enhancement_strength": 0.35,
  "noise_enabled": true,
  "noise_strength": 0.35,
  "eq_enabled": true,
  "compression_enabled": true,
  "deess_enabled": true,
  "loudness_enabled": true
}
```

Strength values are bounded to 0–1. Unknown keys are rejected (a typo can't silently do nothing). Tone and dynamics settings may be adjusted, but quality mode rejects `dereverb_enabled: false`, `speech_enhancement_enabled: false` and a strength of 0 for either stage. No auto-strength classifier is enabled: a reliable room-severity estimate needs real representative recordings and listening calibration. Start at Studio; compare source and processed audio before choosing Strong Room.

## Model evaluation and limitations

- **DeepFilterNet3:** chosen as the required, lightweight local enhancer: full-band 48 kHz, low-complexity, Linux support and CPU inference, with GPU support through its PyTorch backend where available. It is not selected as the sole dereverberator: the published architecture uses short multi-frame filtering and does not establish strong late-tail removal. GTX 1650 4 GB is adequate for this small model, but shared GPU memory can be constrained by Whisper/Ollama.
- **Resemble Enhance:** MIT-licensed, local and trained with room impulse responses; two models (denoiser + enhancer) and 44.1 kHz pipeline. However its published evaluation is speech enhancement/denoising and does not demonstrate robust dereverb on untreated-room creator speech. Its Python dependency stack (including DeepSpeed/Gradio) is heavier than this toolkit needs, so it is not the default.
- **ClearerVoice/MossFormer2:** Apache-2.0 package and published 48 kHz enhancement option, but the reported benchmark tables are mainly noise test sets, not a dedicated late-reverberation evaluation. Package dependencies and model stack are heavier. Not selected.
- **WPE:** open classical signal processing; no model download, runs on CPU, and separates late-reverb prediction from ordinary noise filtering. It is practical here, but blind single-channel WPE is intentionally conservative and can only reduce, not remove, difficult room acoustics.
- **GTCRN:** very small and fast, but general enhancement rather than a validated late-reverb solution. Not selected.
- **Personalized dereverberation research systems:** promising where a room impulse response and speaker calibration are available, but not a simple maintained pretrained Ubuntu batch dependency for this workflow.

Treat these as evidence-based engineering choices, not claims of studio sound. WPE and neural processing can introduce artifacts; only A/B listening on the Maono recordings can validate the chosen strength.

## Audio QA

Synthetic measurements and the limits of the current evaluation are recorded in `pipeline/audio-cleaner-evaluation.md`.

Before transcription, inspect each `work/audio/reports/<recording-id>-clean-report.json` with the checks in `pipeline/voice-cleaning.md`: both stages processed, before/after LUFS and true peak, clipping indication, warnings and duration delta. Listen to source and processed audio for room echo, hiss, speech clarity, natural voice identity, clipping/distortion and artifacts. For each new room/mic setup or significant recording change, preserve a raw sample and make a matched-loudness comparison. Listen to a consonant-rich sentence, a sustained vowel, and a pause at the beginning, middle and end. Do not transcribe or edit until this review is complete. Automated metrics do not replace subjective listening.

Do not claim room-reflection removal when only `afftdn` ran. If WPE or the model harms the voice, lower its blend (`dereverb_strength` / `enhancement_strength` in `--config`, still above 0) or try `natural`, and re-listen. Disabling either stage leaves quality mode and needs the user's explicit approval. A close microphone (10–15 cm, slightly off-axis), soft furnishings behind/around the speaker, and recording away from bare walls are more reliable than increasingly aggressive restoration.
