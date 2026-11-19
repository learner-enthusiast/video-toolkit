# Voice cleaner evaluation

## Automated fixture (2026-11-19)

No real Maono recording was present in the repository. The automated fixture is a 4-second harmonic, gated voice-like signal convolved with a synthetic 650 ms decaying reflection train and mixed with low-level white hiss. It is a deterministic signal-processing regression case, not a realistic recording or a listening study.

At the `studio` WPE blend of 0.35, the active segment RMS changed by −3.43 dB and the selected late-tail segment changed by −11.11 dB (about 7.7 dB relative tail reduction). At the deliberately stronger 0.55 test blend, active RMS changed by −6.26 dB and late-tail RMS by −13.80 dB. This shows the expected tradeoff: stronger late-tail reduction also attenuates the desired signal, so `strong-room` requires listening and should not be used blindly.

The full Studio DSP chain measured −20.4 LUFS / −11.4 dBTP before and −16.2 LUFS / −4.0 dBTP after on that fixture, with 0.000 s duration delta. The true-peak value is below the requested ceiling; the chain does not force peaks up to the ceiling. Integrated loudness landed within 0.2 LU of target.

## Automated checks

`vt-python -m unittest tests.test_clean_audio` covers WPE zero-blend duration/level behavior, synthetic late-tail reduction, 48 kHz mono output, report generation, timeline preservation, loudness measurement, and true-peak ceiling.

## Subjective evaluation still needed

There is no real before/after audio pair or human listening result yet. Before using `strong-room` in a published video, run the cleaner on a representative close-mic sentence and compare matched-loudness source/output for intelligibility, consonants, room tail, breaths, sibilance and metallic/phasey artifacts. Save the source, output and report in that project's ignored `work/audio/` folder and document the selected blend in its project log. Do not describe the synthetic results as proof of improved perceived quality on the creator's voice.
