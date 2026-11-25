# Post-hardening status (reliability pass)

> **Scope:** `main` after PR #2 (`29e202c`), plus branch `hardening-cache-observability` (this pass).  
> Historical phase reports (`phase2-report.md`, `phase2-audit.md`, `final-report.md`, `hardening-final-report.md`) are snapshots at their stated merges — not rewritten.

## CI

- Workflow: `.github/workflows/ci.yml` (Python compile, `model_verify --validate-only`, `unittest`).
- No GPU, FFmpeg, Ollama, or paid APIs required for unit tests.
- `test_clean_audio` skips when NumPy/SciPy/SoundFile are absent (local full suite: use project `vt-python` venv).

## Inspection cache (`tools/inspect_cache.py`)

- Thorough bundles: requirements derived from `report.json` (scene `kf`, beat `sheet_*.jpg`, flag frames).
- `integrity.json` lists every artifact; lookup rejects unlisted extras, path traversal, symlink escape.
- Manifest updates: lock → read → modify → atomic replace.
- Bundle install: stage → rename with per-bundle lock; prior bundle kept on failure.
- Final QA: `lookup --for-final` / `restore --for-final` → `final_qa_requires_fresh_run` always.

## Project log lock (`tools/project_log_lock.py`)

- Canonical lock: `<project>/log.md.lock`
- Shared by `tools/hooks/projlog.py` and `tools/project_state.py` (`record-approval`, header/footer RMW).

## Project state (`tools/project_state.py`)

- `project-state.json` written atomically; corrupt/missing JSON rebuilt from `log.md` on `sync-handoff`.
- `record-approval` appends `**Approval:**` then syncs mirror (warns if sync fails after log write).

## Asset cache (`tools/asset_cache.py`)

- Manifest transactions under lock; corrupt manifest → safe miss reason.
- Output `cache_key` + checksum verified on lookup; ffprobe output staged atomically.

## Token accounting

- Prompt hook stores stage from `project-state.json` snapshot → `**Stage:**` in log footer.
- Models split: `; models main: … | sub: …` (legacy `; models:` still parsed).
- `vt-python tools/vt_log.py summary` → `by_stage`, `by_model`, `by_stage_model` (main vs subagents separate).

## Render validation (`tools/validate/vt_validate.py`)

- Loudness/true-peak FFmpeg pass only when expectations request it.
- True peak from `loudnorm` JSON `input_tp` when available.
- FPS: `r_frame_rate`, fallback `avg_frame_rate` with documented tolerance.

## Remaining / deferred

- Final render / incremental Remotion caching (no complete invalidation model).
- Hindi localization pipeline.
- Full A/V lip-sync automation without reference alignment.
- `test_clean_audio` in CI without optional scientific stack install.

## Production quality

No production gates weakened in this pass (approvals, fresh final inspect, Opus QA, voice pipeline unchanged).