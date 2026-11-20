# Voice cleaner evaluation

## Automated fixture (2026-11-19)

No real Maono recording was present in the repository. The automated fixture is a 4-second harmonic, gated voice-like signal convolved with a synthetic 650 ms decaying reflection train and mixed with low-level white hiss. It is a deterministic signal-processing regression case, not a realistic recording or a listening study.

At the `studio` WPE blend of 0.35, the active segment RMS changed by −3.43 dB and the selected late-tail segment changed by −11.11 dB (about 7.7 dB relative tail reduction). At the deliberately stronger 0.55 test blend, active RMS changed by −6.26 dB and late-tail RMS by −13.80 dB. This shows the expected tradeoff: stronger late-tail reduction also attenuates the desired signal, so `strong-room` requires listening and should not be used blindly.

The full Studio DSP chain measured −20.4 LUFS / −11.4 dBTP before and −16.2 LUFS / −4.0 dBTP after on that fixture, with 0.000 s duration delta. The true-peak value is below the requested ceiling; the chain does not force peaks up to the ceiling. Integrated loudness landed within 0.2 LU of target.

## Automated checks

`vt-python -m unittest tests.test_clean_audio` (16 tests, about 1 min, CPU) uses a stub `deep-filter` with the real CLI's flags and log lines. It covers:

- WPE zero-blend and synthetic late-tail reduction
- the full quality pipeline: statuses, run_id, 48 kHz mono, duration, −16 LUFS, true peak, content above 8 kHz kept
- balanced mode never passing the gate
- quality mode rejecting disabled, zeroed or unknown settings
- no `--no-neural` in `--help`
- fail-closed exits for a missing WPE dependency, a WPE `LinAlgError` and a too-short clip
- fail-closed exits for a DeepFilterNet that is missing, exits non-zero, writes no output, returns its input unchanged or never logs a completed run
- preservation of an earlier output after a failed run
- refusal to write in `raw/` or onto another recording's report
- a hot dual-mono input (fold-down over full scale) getting headroom, with no wrap-around clicks, against a stub that saves int16 the way DeepFilterNet does; and the wrap guard failing the run when headroom is skipped
- `tools/voice_preflight.py` failing with a fix line when DeepFilterNet is missing, and the lock pinning torch/torchaudio 2.6.0+cu126 with DeepFilterNet 0.5.6

## Audit fixes (2026-11-19)

- The staged master was written to a `.tmp` name, so FFmpeg couldn't pick an output format (exit 234). Every run failed at mastering until `-f wav` and a `.tmp.wav` suffix were added.
- WPE ran at 16 kHz and the 16 kHz signal *was* the output, so energy above 9 kHz fell from −14.6 dB to −57.9 dB of the total on a broadband fixture. Now only the predicted reverb is upsampled and subtracted. The late-tail numbers above are below 8 kHz and still hold.
- **First real recording (`07-provider-failover`, same day): listening failed.** The user heard the cleaned file as unusable. Cause: the mono fold-down went over full scale and DeepFilterNet's unclamped int16 save wrapped the overs into clicks (6–10 kHz +15 dB versus the original). Fixed with input headroom and a wrap guard (`pipeline/clean-audio.md`, Gotchas). After the fix, the same recording differs from the original by −1 to +3.8 dB per band, with no clicks.
- A real DeepFilterNet 3 smoke run on a synthetic fixture (`gpu-run`, `cuda:0`) passed every new check: −16.1 LUFS, −5.9 dBTP, 0.000 s delta, no warnings. This checks the plumbing only, not perceived quality.

## Subjective evaluation still needed

There is no real before/after audio pair or human listening result yet. Before using `strong-room` in a published video, run the cleaner on a representative close-mic sentence and compare matched-loudness source/output for intelligibility, consonants, room tail, breaths, sibilance and metallic/phasey artifacts. Save the source, output and report in that project's ignored `work/audio/` folder and document the selected blend in its project log. Do not describe the synthetic results as proof of improved perceived quality on the creator's voice.
