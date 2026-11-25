# Post-hardening status (reliability pass)

> **Scope:** `main` @ `63da975` + branch `reliability-final-pass` (this document updated per pass).  
> Historical reports remain labeled in place; see `benchmark-protocol.md` for measured usage comparisons.

## CI (job name: `test`)

- `python3 -m compileall`, `model_verify --validate-only`, full `unittest`.
- CPU deps for audio tests: `.github/workflows/ci-requirements.txt` (`numpy`, `scipy`, `soundfile`).
- No GPU, FFmpeg (unit), Ollama, or paid APIs required for default unit tests.

## Loudness / true peak (`tools/validate/vt_validate.py`)

- Multi-line `loudnorm` JSON extracted via balanced-brace parsing (`input_i`, `input_tp` only).
- FFmpeg non-zero exit → measurement failure; no pass when parse fails.
- `--lufs-required` / `--true-peak-required` require matching threshold flags.

## Inspection cache

- Shared `tools/path_safety.py` (POSIX/Windows/UNC/`..` rejected).
- Artifacts resolved under bundle root only; symlinks forbidden.
- Report-required paths must appear in `integrity.json`.
- Cache manifest validates `entries` dict; bundle_dir must match `work/inspect/.cache/<key>`.

## Asset cache

- Strict entry schema (checksum required, path containment).
- Per-key output lock + `mkstemp` staging; manifest lock → read → write.

## Project state

- `log.md.lock` for init, set-stage, record-approval, sync-handoff.
- Invalid JSON **or** schema → quarantine `.corrupt` / `.corrupt-N`, rebuild from log.

## Token / time measurement

- `vt-python tools/vt_log.py summary|breakdown|compare`
- Elapsed time from `**Took**`; explicit `**Stage:**` only (no handoff inference for new entries).

## Branch protection

- Instructions: `.github/BRANCH_PROTECTION.md`
- Required check name: **`test`**
- Apply via repo admin (`gh api` or GitHub UI); status recorded when enabled.

## Production quality

Final QA cache refusal, log approvals, Opus vision QA policy, audio pipeline — unchanged.