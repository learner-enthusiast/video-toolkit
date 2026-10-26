# Clean audio

**Goal:** a natural, clean voice track at -16 LUFS, used for everything after this step.

**Do**
- Extract the voice to a 48 kHz mono WAV in `work/audio/raw.wav`.
- Measure the noise floor first (a quiet stretch with `astats` or `silencedetect`). A clean lav at around -65 dB needs very little denoise.
- Chain: high-pass at 80 Hz → denoise (`arnndn` with a model if available, otherwise `afftdn` at a modest `nr`) → gentle compression (about 3:1, slow attack) → `loudnorm` to I=-16, TP=-1.5, LRA=11.
- Use two-pass `loudnorm` (measure, then apply with `linear=true`).
- Write `work/audio/clean.wav`.

**Checks**
- Listen to 3 short windows (start, middle, end) via spectrum images: no robotic or watery artifacts. If denoise hurts the voice, use less of it.
- Save a raw-vs-clean spectrum comparison to `work/qa/` and look at it.
- Measure the integrated loudness of the result: -16 ±0.5 LUFS.

**Gotchas**
- The working video and the clean WAV must share the same timeline (same start, CFR source), or every later cut drifts.
- Don't normalize clips that have no voice; strip their audio instead.
