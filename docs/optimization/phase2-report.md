# Phase 2 — token-efficiency hardening report

**Branch:** `token-diet-phase2` (based on `main` @ `2de339a`)  
**Date:** 2026-11-25

## 1. Executive summary

Fixed model-routing contradictions (vision QA always **creative** tier), made **log.md** authoritative for approvals, completed inspect artifact caching, expanded validators and scaffold, added asset probe cache, hook/usage tests, and GitHub Actions CI. Adaptive transcription remains non-default; Hindi not implemented.

## 2. Repository changes

See git log on `token-diet-phase2`. Key areas: `tools/project_state.py`, `tools/validate/vt_validate.py`, `tools/inspect_cache.py`, `tools/model_verify.py`, `tools/routing_config.py`, `tools/asset_cache.py`, `tools/scaffold_remotion.py`, `tools/vt_log.py`, `tests/test_*.py`, `.github/workflows/ci.yml`, pipeline docs, `README.md`.

## 3. Model routing

- IDs only in `config/model-routing.json`.
- `pipeline/model-routing.md` uses tiers; vision subagent **never** `same_as_main`.
- `tools/routing_config.py` validates config; `tools/model_verify.py` reports CLI support + `unverified`/`seen_in_recent_sessions` per model (not account proof). Optional `--probe` for live check.

## 4. Project-state safety

- Explicit `**Approval:** rough_cut=approved` in `log.md` (`pipeline/project-log.md`).
- `sync-handoff` mirrors log; does **not** infer approval from Compose stage.
- `vt_validate.py` → `check_stage` reconciles log vs JSON (`STATE_OUT_OF_SYNC`, `APPROVAL_UNVERIFIABLE`, `ROUGH_CUT_NOT_APPROVED`).

## 5. Inspection cache

- Schema 2 bundle under `work/inspect/.cache/<key>/`.
- Fingerprint: video hash, size, duration, mode, range, script file hashes.
- `lookup --for-final` rejects non-thorough bundles.
- Atomic manifest writes via `os.replace`.

## 6. Validators

Modular checks: project, state schema, stage+approval, subtitles (expanded), render (ffprobe + ffmpeg decode, optional ebur128), phrases (normalized lookup, skip `node_modules`).

## 7. Remotion scaffold

Generates `layout.ts`, `Root.tsx`, `index.ts`, package scripts; version from `REMOTION_VERSION`; refuses non-empty dir.

## 8. Logging and token measurement

`vt_log.py summary` and `breakdown` by stage; hook dedup tested in `tests/test_projlog.py`. Model ID not inferred in logs unless transcript schema provides it (future).

## 9. Asset cache

`tools/asset_cache.py` for deterministic outputs (e.g. ffprobe JSON); manifest under `work/cache/`.

## 10. Test results

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**Result:** 25 tests, 24 pass, 1 skipped (`test_clean_audio` without numpy in system Python). CI uses same discover + `model_verify.py --validate-only`.

`vt-python -m unittest tests.test_clean_audio` on machine with venv: run locally for audio tests.

## 11. Token-efficiency impact

Phase 1 byte estimates remain in `pipeline/token-budget.md`. Phase 2 reduces **rework risk** (approval validation, full inspect cache, compact job reports). No new end-to-end session token comparison in this pass — use `vt_log.py breakdown` on projects with hook history.

## 12. Quality impact

All Part 13 gates preserved. Cache and validators cannot approve creative work. Final thorough inspect + Opus vision unchanged in policy.

## 13. Remaining limitations

- `model_verify.py` cannot prove subscription access without `--probe`.
- Adaptive transcription benchmark data not collected yet.
- Incremental Remotion plate cache not implemented.
- Transcript model attribution requires schema inspection per Claude Code release.

## 14. Git status

Document at commit time on branch `token-diet-phase2` (not merged to `main` until reviewed).