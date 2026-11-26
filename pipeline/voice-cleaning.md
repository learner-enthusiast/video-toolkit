# Voice recording cleaning gate

Every talking-head source recording must pass this gate before any Whisper transcription or editing. It runs as Stage 1 (Prep) steps 2–7 in `pipeline/stages.md`, and every production entry point (`/coding-video`, `/reel`, `/cut-video`, `/clipify`, `/add-zooms`) runs it or reuses its verified result. A documentation reference alone does not satisfy it. Implementation details live in `pipeline/clean-audio.md`.

## Order (Stage 1 · Prep)

1. Probe the originals (`pipeline/probe-and-trim.md`); never modify `raw/` or `assets/`.
2. Inventory every talking-head recording/audio stream; give each a stable ID and record its source and intended cleaned path.
3. Preflight (below). 4. Clean each recording once (below). 5. Inspect every report and 6. confirm the required stages (Required report checks). 7. Listening gate (or the approved-setup exemption).
8. Only then transcribe, from each verified cleaned WAV (`pipeline/transcribe.md`; GPU preflight from `pipeline/gpu.md` right before Whisper if it hasn't passed). Never a raw source, proxy/video audio extraction or unverified cleaned file, for any ASR: full transcripts, candidate scans, caption timestamps, cut windows.
9. Review each transcript and its word timestamps, then write the per-recording table (Handoff, below). Cut (stage 2) may not start on a recording missing from that table; no reel candidate search or edit may use a transcription that bypassed this gate.

Applies to `/coding-video`, `/reel`, `/cut-video`, `/add-zooms` and `/clipify` dialogue/hybrid modes (action mode runs no Whisper; a Hybrid's dialogue portion is gated). Skills invoked inside a production reuse the Prep-verified WAVs; they run the gate themselves only when invoked standalone. Cleaning runs and Whisper are heavy jobs (`pipeline/delegation.md`); report inspection, listening and the gate decision stay with Claude, and Whisper is not launched until Claude has recorded that every source passed.

## Preflight first

Before cleaning anything, run `vt-python tools/voice_preflight.py` (about 5 s, read-only). It checks FFmpeg, the WPE libraries, the DeepFilterNet 3 launcher and environment, the versions pinned in `tools/deepfilternet.lock.txt`, CUDA and the cached model. `READY` (exit 0): go on. `NOT READY` (exit 1): stop Prep, show the user the `FAIL` lines and their `fix:` commands, and install or rebuild nothing without approval. Don't debug a failed cleaning run when the preflight would have caught it. `WARN` lines (e.g. no CUDA) don't block; note them in the log.

## Reuse before re-cleaning

If the project's Prep handoff in `log.md` already maps a recording to a cleaned WAV whose gate passed (report checks and listening), reuse that WAV. Don't clean it again into a skill-specific folder. Clean only recordings without a passed mapping.

## Run once for each recording

Keep the source in `raw/` unchanged (the cleaner refuses to write inside `raw/` or `assets/`). Give each recording a stable, filesystem-safe ID (`recording-01`, `recording-02`, … in inventory order; record which source each ID means) and write a distinct cleaned WAV and JSON report:

```bash
vt-python tools/clean_audio.py "projects/<name>/raw/<recording>" \
  "projects/<name>/work/audio/cleaned/<recording-id>.wav" \
  --preset studio \
  --mode quality \
  --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"
```

Playlist episodes use `projects/<playlist>/<NN>-<topic>/` in place of `projects/<name>/`. The cleaner refuses a report or output path that already belongs to another recording. A re-run of the same recording keeps the earlier WAV/report as `*.previous-<run_id>`. Use the cleaned WAV for all later Whisper and editing work. When a workflow needs one canonical path (`work/audio/clean.wav`), copy the verified WAV there and record which recording it is. Never edit the unique WAV or report.

The run is a heavy job (`pipeline/delegation.md`) or a direct command. The checks below are always Claude's.

## Required report checks

A non-zero exit means the gate failed: read the `*.run-<run_id>.failed.json` next to the report and stop. On exit 0, open every report and confirm all of:

- `status` is `succeeded`, and `<wav>.run-status.json` shows `status: succeeded` with the same `run_id` (so the WAV is from this run, not a preserved earlier one).
- `input` is the inventoried source and `output` is that recording's cleaned WAV.
- `mode` is `quality`; `stages.wpe` and `stages.deepfilternet3` are both `processed`; `production_gate.automated_checks_passed` is `true`.
- `dereverberation.applied` is `true` with a finite `predicted_reverb_energy_db`; `speech_enhancement.model` is `DeepFilterNet3` with `backend`, `device` and `real_time_factor` filled in. `device: cpu` is allowed but must be stated in the log (it is never silent).
- `duration_delta_seconds` within ±0.02 s (the cleaner fails above 0.1 s).
- `output_measurements`: integrated LUFS about −16 (±1), true peak ≤ −1.0 dBTP; `input_clipping_suspected` and `output_clipping_suspected` false.
- `warnings` is empty, or each warning is explained in the handoff.

Stop if the cleaner fails, if a stage is `failed`, `disabled` or `not_attempted`, or if a report is missing, unparsable, mismatched or fails any check above. Report the recording ID, failed stage, report/error and the next blocking action. Do not change modes, bypass the cleaner, route around the gate through another skill, use another pipeline, transcribe original audio, reinstall dependencies or edit the cleaner's settings without the user's explicit approval. `balanced` and `performance` never pass this gate.

## Listening gate

**Approved-setup exemption (saves a stop per video).** Skip the listening stop and go straight to Whisper only when all of these hold:
- the recording matches a row in **Approved setups** below (same device, same audio-stream signature, same room), and the user hasn't said anything changed;
- the report passes every check above, its only warning is the headroom note (`applied … dB headroom`), and every `tone_change_db` band is within ±6 dB (the cleaner warns past that).

Record "listening: approved-setup exemption (<setup>), tone change max <x> dB" in the handoff. Otherwise do the full listening stop below. A new phone, mic, room or mic placement means a new setup: listen once, then add a row when the user approves.

**Approved setups**

| Setup | Signature (ffprobe + check) | Approved |
|---|---|---|
| Phone talking head, home room (Maono on boom in frame) | MP4, H.264 1920x1080 + 90° rotation, VFR ~29.9; AAC 48 kHz stereo with L = R (dual mono: channel correlation ≈ 1.000) | 2026-11-19, `system-design-of-ai/07-provider-failover`: original and cleaned "almost similar, either is fine" (tone change max +2.8 dB) |

**Full listening stop**

Listen to the original and the cleaned recording at matched loudness: the cleaned file sits at −16 LUFS, so level-match the original (`loudnorm` on a scratch copy in `work/`) before comparing. Louder is not better. Listen at the start, middle and end, including a consonant-rich sentence, a sustained vowel and a pause. Check:

- room echo and reverberant tails
- background hiss
- speech clarity
- natural voice identity: pitch, timbre, dynamics
- metallic, phasey or robotic artifacts
- clipping and distortion
- start/middle/end sync against the original

If the output sounds worse, investigate: lower the blend in a `--config` override or try the `natural` preset, and re-run in quality mode. Don't accept it just because the command succeeded.

If the environment cannot play audio for you to listen to (the usual case for Claude Code), say so plainly. List the checks that could not be done, give the user both file paths and the matched-loudness scratch copy, and wait for explicit approval before transcription. A report, waveform, spectrogram, metric or successful run does not replace listening. Resume transcription only after the required stages pass and listening is done, or the user explicitly approves a documented exception.

## Presets and comparisons

`studio` is the default. `natural` is for clean recordings that need little help. `strong-room` is only for genuinely strong room reverb and is never chosen automatically. When the room, microphone or mic placement changes significantly, render the same source excerpt with each candidate preset (quality mode, separate output/report names such as `recording-01-natural.wav`), compare at matched loudness for echo, hiss, clarity and naturalness, and record the choice and reason in the log.

## Handoff

Record a table in the Prep handoff with one row per recording: ID, source path, cleaned WAV, report, run_id, stage statuses, LUFS/true peak/duration delta, warnings, listening result (or the user's approval of the exception), and transcript path. Only recordings with a passed gate may be used for Whisper or editing.

**Files:** Originals in `raw/` stay untouched; each recording gets its own cleaned WAV and report (`--mode quality` only).
