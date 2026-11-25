# Final hardening report — `hardening-final-optimizations`

## A. Repository state

| Item | Value |
|---|---|
| Starting HEAD (`main`) | `717cd29` |
| Branch | `hardening-final-optimizations` |
| Final commit | `31aa2943a2c37777e29865b14e435c458b06a93c` |
| Pull request | https://github.com/learner-enthusiast/video-toolkit/pull/2 |
| GitHub Actions (PR) | https://github.com/learner-enthusiast/video-toolkit/actions/runs/45657464314 — **success** |

## B. Implemented changes (by phase)

### Phase A — CI / FFmpeg-independent tests
- `tools/inspect_cache.py`: `probe_meta` catches `FileNotFoundError` → `probe: unavailable`.
- `tests/test_inspect_cache.py`: mocks `probe_meta`; dedicated test for missing ffprobe.

### Phase B — Final QA cache bypass blocked
- `lookup --for-final` and `restore --for-final` always refuse with `final_qa_requires_fresh_run`.
- Docs: `pipeline/video-inspect.md`, `pipeline/job-results.md`, `pipeline/qa.md`.

### Phase C — Cache integrity
- Inspect cache schema 3: `integrity.json` per bundle, checksum verify on lookup/restore, implementation fingerprint, flagged-frame requirements from `report.json`.
- Asset cache v2: output size/sha256, tool/script fingerprint, checksum verify, atomic manifest writes.
- Tests: `test_inspect_cache.py`, `test_asset_cache.py`.

### Phase D — Project state / validation
- `record-approval` appends `**Approval:**` to `log.md`, then `sync-handoff`.
- `set-approval` deprecated (exit 2).
- `try_load_state`, `INVALID_STATE_JSON`, defensive `check_stage` / schema validation.
- Docs: `pipeline/context-handoffs.md`, `pipeline/project-log.md`.

### Phase E — Render validation
- Rational FPS, pixel format, audio stream fields, true peak / LUFS via `measure_loudness`, mock-based unit test.

### Phase F — Token observability
- `projlog.py`: model attribution from `message.model`, compact `; models:` suffix.
- `vt_log.py`: `by_model` in summary.

### Phase G — CI / docs
- Local: `compileall`, `model_verify --validate-only`, full `unittest` (no GPU/FFmpeg required for unit tests).

## C. Test results

```bash
python3 -m compileall -q tools tests
python3 tools/model_verify.py --validate-only
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Local run: **36 tests, OK (1 skipped)**.

GitHub Actions PR run `45657464314`: **passed** (ubuntu-latest, no FFmpeg/GPU).

## D. Token-efficiency impact

- **Inspect cache**: intermediate QA skips re-running video-inspect when fingerprint + integrity match; final QA never reuses cache (policy enforced in code).
- **Asset cache**: deterministic probes/transcodes reuse verified outputs; misses are explicit (`checksum_mismatch`, `missing_file`, etc.).
- **Measurement**: repeated work avoided when cache hit; token savings are not extrapolated here (no before/after session counts in this pass).

## E. Remaining limitations

- `ffprobe` integration in `asset_cache ffprobe` subcommand still needs FFmpeg at runtime (not in unit tests).
- Stage token rollup in `vt_log.py` still attributes main-session totals per handoff stage; subagent tokens are in `totals.subagents` / per-line `subagents:`.
- Inspect cache schema bump invalidates prior schema-2 manifest entries (by design).

## F. Quality confirmation

**No production quality gate was weakened.** Final QA requires fresh thorough inspect + Opus vision + human approval. Rough-cut approval remains log-authoritative. No raw footage or deliverables were modified.