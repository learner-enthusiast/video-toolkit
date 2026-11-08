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
- Measure the floor on 10 ms windows (5th percentile), not 0.5 s ones. A slow, dense talker leaves almost no silent half-second, so 0.5 s windows read speech as "floor" (-18.7 dB vs the real -37 dB on `Elastic-search-interview`).
- `afftdn` only accepts `nf` in [-80, -20]; clamp it, or ffmpeg aborts the whole chain.
- Phone recordings with AGC come in already squashed (LRA ~2.7) with hot peaks. Two-pass `loudnorm` then can't stay linear (it needs more gain than the peaks allow) and silently goes `dynamic`. Use: chain without makeup gain → `volume=<target − measured I>dB` → `alimiter=limit=0.79:level=false` → `lowpass=f=16000` (AAC phone audio has nothing above 16 kHz; this removes limiter splatter). Check the result with `ebur128=peak=true`.
- Measure the pause RMS (e.g. a 2 s teleprompter gap with `astats`) before and after the chain. On `vercel-dot-app` the phone's room tone + 100/200 Hz hum sat at −30 dBFS in pauses: `afftdn` (any `nr`/`nf`) and `anlmdn` took off < 2 dB, and the chain's gain lifted the pauses to −23 dBFS. RNNoise fixed it: `arnndn=m=~/.cache/rnnoise-models/bd.rnnn:mix=0.9` right after the high-pass (pause −30 → −54 dB, speech level unchanged). Models from `github.com/GregorR/rnnoise-models` (`bd`, `sh`, `cb` all similar), stored in `~/.cache/rnnoise-models/`.
- Shorts/reels: the brief may ask for -14 LUFS / TP ≤ -1 instead of -16. The project brief wins for that video.
