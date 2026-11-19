# Clean audio

**Goal:** produce a natural, intelligible 48 kHz mono voice track on the exact source timeline. Room reverb is treated as a separate problem from stationary noise.

**Execution authority:** for production order, per-recording paths, report checks, listening approval, and fail-stop behavior, follow [`pipeline/voice-cleaning.md`](voice-cleaning.md). This file describes implementation details only.

## Entry point

Use `vt-python tools/clean_audio.py INPUT OUTPUT --preset studio --mode quality --report work/audio/clean-report.json`. Every talking-head source must be cleaned and the report reviewed before Whisper or editing. Preserve the source recording; write the processed audio to a separate path. The existing video flow still reads `work/audio/clean.wav`; render from a copy into that path. Quality mode requires WPE and DeepFilterNet 3 and fails with an actionable error if either stage cannot run. Do not retry with `--no-neural`, `balanced`, or `performance` without first asking the user to approve that substitute. The cleaner detects the global `deep-filter` executable or user venv and accepts `--deepfilter-executable` / `--deepfilter-python` (also `DEEPFILTERNET_EXECUTABLE` / `DEEPFILTERNET_PYTHON`). Temporary WAVs are isolated and removed automatically; source files are never modified.

The CLI probes input stream rate/channels/duration, measures loudness and true peak before and after, and reports duration delta. It converts the processing copy to mono/48 kHz and does not trim silence. Keep the original video timeline and use the resulting WAV as the replacement audio track.

## Processing stages

1. **Input analysis:** FFprobe checks audio presence, channel count, sample rate and duration. FFmpeg EBU R128 reports integrated loudness, LRA and true peak. Clipping and room-reverb severity are not yet robustly auto-classified; listen and inspect the report.
2. **Dereverberation (separate stage):** offline single-channel WPE predicts late reverberation using delayed STFT frames. It is CPU-friendly, uses the shared venv's NumPy/SciPy/soundfile, and is blended with the dry signal at the preset strength. WPE chiefly targets the late tail; it does not erase strong early reflections or a discrete slapback echo, and can sound phasey when overused. It is not an inverse-room model.
3. **Neural speech enhancement:** invoke the globally installed DeepFilterNet3 CLI in its own cached Python environment, independent from WPE; conservatively blend the result using `enhancement_strength`. DeepFilterNet3 is a general speech-enhancement model trained with reverberant examples, not a dedicated dereverberator. It can help residual noise and roominess but is not guaranteed to remove a long room tail. Missing/incompatible dependencies stop quality processing; fix the installation or ask before using a substitute.
4. **Residual noise:** modest `afftdn` only; do not treat it as dereverberation. If the recording has a steady hum, inspect it and use a separately targeted notch rather than increasing broadband suppression.
5. **Vocal tone and dynamics:** high-pass at 78 Hz; subtle 260 Hz cut and 3.2 kHz presence lift; gentle compression (2.2:1); mild FFmpeg de-esser. Optional tone/dynamics settings may be adjusted when needed, but do not disable WPE or DeepFilterNet 3 in quality mode without explicit user approval.
6. **Loudness:** single-pass `loudnorm` targets −16 LUFS and −1.5 dBTP. The report measures the output; do not infer compliance from the requested target alone. Shorts/reels may specify another target in their brief.

The cleaner does not time-stretch or trim, so synchronization and pauses remain. WPE uses centered STFT processing and may change edge samples by a few milliseconds; report the duration delta and verify start/middle/end sync before delivery.

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

Strength values are bounded to 0–1. Tone and dynamics settings may be adjusted, but production quality mode must retain WPE and DeepFilterNet 3. No auto-strength classifier is enabled: a reliable room-severity estimate needs real representative recordings and listening calibration. Start at Studio; compare source and processed audio before choosing Strong Room.

## Model evaluation and limitations

- **DeepFilterNet3:** chosen as an optional, lightweight local enhancer: full-band 48 kHz, low-complexity, Linux support and CPU inference, with GPU support through its PyTorch backend where available. It is not selected as the sole dereverberator: the published architecture uses short multi-frame filtering and does not establish strong late-tail removal. GTX 1650 4 GB is adequate for this small model, but shared GPU memory can be constrained by Whisper/Ollama.
- **Resemble Enhance:** MIT-licensed, local and trained with room impulse responses; two models (denoiser + enhancer) and 44.1 kHz pipeline. However its published evaluation is speech enhancement/denoising and does not demonstrate robust dereverb on untreated-room creator speech. Its Python dependency stack (including DeepSpeed/Gradio) is heavier than this toolkit needs, so it is not the default.
- **ClearerVoice/MossFormer2:** Apache-2.0 package and published 48 kHz enhancement option, but the reported benchmark tables are mainly noise test sets, not a dedicated late-reverberation evaluation. Package dependencies and model stack are heavier. Not selected.
- **WPE:** open classical signal processing; no model download, runs on CPU, and separates late-reverb prediction from ordinary noise filtering. It is practical here, but blind single-channel WPE is intentionally conservative and can only reduce, not remove, difficult room acoustics.
- **GTCRN:** very small and fast, but general enhancement rather than a validated late-reverb solution. Not selected.
- **Personalized dereverberation research systems:** promising where a room impulse response and speaker calibration are available, but not a simple maintained pretrained Ubuntu batch dependency for this workflow.

Treat these as evidence-based engineering choices, not claims of studio sound. WPE and neural processing can introduce artifacts; only A/B listening on the Maono recordings can validate the chosen strength.

## Audio QA

Synthetic measurements and the limits of the current evaluation are recorded in `pipeline/audio-cleaner-evaluation.md`.

Before transcription, inspect `work/audio/clean-report.json` for successful WPE and DeepFilterNet3 stages, before/after LUFS and true peak, clipping indication, and duration delta. Listen to source and processed audio for room echo, hiss, speech clarity, natural voice identity, clipping/distortion and artifacts. For each new room/mic setup or significant recording change, preserve a raw sample and make a matched-loudness comparison. Listen to a consonant-rich sentence, a sustained vowel, and a pause at the beginning, middle and end. Do not transcribe or edit until this review is complete. Automated metrics do not replace subjective listening.

Do not claim room-reflection removal when only `afftdn` ran. If WPE or the model harms the voice, reduce its blend or disable it. A close microphone (10–15 cm, slightly off-axis), soft furnishings behind/around the speaker, and recording away from bare walls are more reliable than increasingly aggressive restoration.
