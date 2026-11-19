# Voice recording cleaning gate

Every talking-head source recording must pass this workflow before any Whisper transcription or editing. Follow the ordered gate in `pipeline/stages.md`; a documentation reference alone does not satisfy it.

## Run once for each recording

Keep the source in `raw/` unchanged. Give each recording a stable, filesystem-safe ID and write a distinct cleaned WAV and JSON report so multi-recording runs never overwrite one another:

```bash
vt-python tools/clean_audio.py "projects/<name>/raw/<recording>" \
  "projects/<name>/work/audio/cleaned/<recording-id>.wav" \
  --preset studio \
  --mode quality \
  --report "projects/<name>/work/audio/reports/<recording-id>-clean-report.json"
```

Create output directories as needed. Use a separate report path for every recording; do not reuse a generic report filename. Use the cleaned WAV as the audio source for all later Whisper and editing work. When a workflow requires a single canonical audio path, point/copy the verified WAV to that workflow's working path without altering the raw source, and retain the unique original cleaned WAV and report.

## Required report checks

Open and inspect every report. Match its `input` and `output` to the recording inventory, then confirm:

- `dereverberation.applied` is `true` (WPE ran).
- `speech_enhancement.status` is `processed` and `speech_enhancement.model` is `DeepFilterNet3`.
- `duration_delta_seconds` is small enough to preserve synchronization; investigate any material change.
- `input_measurements` and `output_measurements` include integrated LUFS and true peak; review clipping indication and output levels.

If the cleaner fails, a required stage is disabled/skipped/unavailable, the report is absent or invalid, or the report does not confirm both required stages, stop. Report which recording and stage failed. Do not change modes, use another pipeline, or transcribe original audio without the user's explicit approval. Do not reinstall dependencies or make processing substitutions on your own.

## Listening gate

Listen to the original and cleaned recording, preferably at matched loudness. Check room echo/reverberation, background hiss, speech clarity, voice naturalness and identity (pitch, timbre and dynamics), clipping/distortion, and start/middle/end synchronization. If the output sounds worse, stop and investigate; do not accept it just because the command succeeded.

If the current environment cannot play/listen to both files, tell the user explicitly which checks could not be performed and request approval before starting transcription. A report, waveform, or automated metric does not replace listening approval.

For a new room, unfamiliar microphone, or significant recording-condition change, make and listen to an original-versus-processed comparison. Studio is the default. Use Natural or Strong Room only when appropriate; Strong Room requires actual stronger room reverb and the same listening check.

Record each recording ID, source, cleaned WAV, report path, stage statuses, report findings, and listening result in the Prep handoff. Only recordings with a passed gate may be used for Whisper or editing.
