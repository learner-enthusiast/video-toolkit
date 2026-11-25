# Post-hardening status (reliability pass)

**Historical baseline (audit):** `main` @ `63da97529d024442b9275396694b9913d22449ff` (post–PR #3).  
**This pass:** branch [`reliability-final-pass`](https://github.com/learner-enthusiast/video-toolkit/pull/4), tip @ `4fc7e91`.  
Older reports in this folder are **historical** unless dated after this pass.

## Pull request and CI

| Item | Value |
|------|--------|
| PR | [#4](https://github.com/learner-enthusiast/video-toolkit/pull/4) |
| Required check name | **`test`** (workflow `ci`) |
| Latest green run | [45665941160](https://github.com/learner-enthusiast/video-toolkit/actions/runs/45665941160) |
| Tests | **73** run, **73** passed, **0** skipped |
| Local (no scipy/ffmpeg) | 57 run, 1 skipped (`test_clean_audio` needs venv deps) |

Steps: `compileall`, `model_verify --validate-only`, full `unittest` inside `.ci-venv` + `ci-requirements.txt` (`numpy`, `scipy`, `soundfile`); `apt install ffmpeg` for audio cleaning tests. No GPU, model weights, or paid APIs in CI.

## Fixes delivered (vs audited `main`)

1. **Loudness / true peak** — balanced-brace `loudnorm` JSON parser; `input_i` / `input_tp` only; FFmpeg rc check; CLI rejects required thresholds without criteria.
2. **Inspection cache** — `path_safety`; containment before existence checks; symlink rejection; integrity manifest cross-check; manifest schema validation.
3. **Asset cache** — strict `verify_entry`; unique staging + per-key locks; manifest `entries` must be a dict.
4. **Project state** — shared `log.md.lock` on init/set-stage/approval/sync-handoff; schema validator + quarantine recovery.
5. **Token/time** — `vt_log.py` `compare`, `**Took**` in summaries; `benchmark-protocol.md`; `token-budget.md` separates context estimates vs measured hook usage.
6. **CI** — CPU-safe `test_clean_audio` on every PR.

## Skipped tests (intentional)

| Test | Reason |
|------|--------|
| `test_clean_audio` (entire module) | Skipped only when `numpy`/`scipy`/`soundfile` missing (developer machine without venv). Not skipped in CI. |
| `test_loudnorm_integration` | Skipped when `ffmpeg` absent locally; runs on CI. |

## Cache integrity — guarantees and limits

- **Guarantee:** Relative paths validated platform-independently; resolved paths must stay inside bundle/asset roots; symlinks rejected; report artifacts must match integrity manifest; corrupt/wrong-type manifests → safe miss or explicit failure; final-mode inspect restore still refused (existing tests preserved).
- **Limit:** Cache reuse for non-final inspect still depends on correct report parsing; lock ordering is documented in code but not stress-tested on all platforms.

## State recovery

- `log.md` remains authoritative for approvals; corrupt/invalid JSON quarantined (`project-state.json.corrupt`, numbered backups); rebuild via sync-handoff; set-stage validates allowed stages; no approval inference from stage.

## Loudness / true peak measurement

- Measurement runs only when expectations are configured; required failures propagate; optional → warning; unmeasured when parse/ffmpeg fails.

## Token / time measurement

- **Available:** per-log `summary` / `breakdown` / `compare` on real `**Tokens**` and `**Took**` hook fields.
- **Baseline benchmark:** protocol only (`docs/optimization/benchmark-protocol.md`); no fabricated before/after numbers in this pass (insufficient paired historical logs).

## Branch protection

- **Status:** `main` **not protected** (`gh api …/branches/main/protection` → 404).
- **Action:** repo admin — see [`.github/BRANCH_PROTECTION.md`](../.github/BRANCH_PROTECTION.md); require check **`test`**.

## Production quality (unchanged)

- Fresh final visual QA; no cached final inspect; Opus/creative-tier vision QA; rough-cut gate; WPE + DeepFilterNet 3 audio path; no adaptive transcription by default; no final-render cache.

## Deferred / not in this PR

- Hindi localization; final-render caching; enabling branch protection without admin token; full matrix of hook concurrency tests; measured A/B token benchmark commit; Opus-tier automated diff review (model unavailable on current plan).