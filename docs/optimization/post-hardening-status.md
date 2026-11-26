# Post-hardening status

## Update: token-efficiency pass, PRs #10–#14 (2026-11-26)

| Area | Status |
|---|---|
| Doc drift and size budgets | Enforced in CI (`tests/test_doc_lint.py`) |
| Model routing | Session model and two subagents set in config and validated; stage-start brief and Read guard are hooks |
| Pipeline scripts and heavy jobs | Tracked in `tools/`; `tools/jobs/batch.sh` replaces the Haiku runner |
| Asset and inspect caches | **Wired** into probe, voice reuse and Whisper from PR #14. Before it, neither cache CLI could run from the command line |
| Measurement | Call counts, weighted cost and per-stage JSON records from PR #14 |
| Benchmark | Instrumented, **not yet run** ([`benchmark-results.md`](benchmark-results.md)) |

The sections below are the earlier gap-closure snapshot, kept as history.

**`main` @ gap-closure start:** `9cf4a5473eec86f2ab444a488467ba9bea6334e4` (includes PR #4).  
**Follow-up:** PR from branch `final-gap-closure` (inspect/asset symlink fixes, state recovery, `vt_log` compare, branch protection).

## Branch protection

- **Enabled** on `main`: required check **`test`**, strict up-to-date, admins included, no force-push/delete.
- Verify: `gh api repos/learner-enthusiast/video-toolkit/branches/main/protection`

## CI

- Workflow `ci`, job **`test`**: venv + scipy stack + `ffmpeg`; `actions/checkout@v5`.
- Latest local full CPU run: **85** tests, **0** skipped (venv).

## Gap-closure fixes

| Area | Change |
|------|--------|
| Inspect cache | Symlinked dirs rejected; restore validates entry + staging copy; JSON dict checks |
| Asset cache | `lstat` path checks; bundle-key containment; manifest quarantine; stricter metadata |
| Project state | `set-stage` rebuilds approvals from `log.md`; `show` errors without mutation |
| `vt_log` | No handoff stage inference; full compare (models, stages, timing, %) |
| Hygiene | ResourceWarning fixes in tests / `vt_validate` |
| Benchmark | [`benchmark-results.md`](benchmark-results.md) — **pending** (no paired logs in repo) |
| Review | [`manual-review-final-gap.md`](manual-review-final-gap.md) (manual; no Opus automation) |

## Unchanged production invariants

Fresh final QA, cache refusal for final inspect, Opus vision QA, rough-cut approval, audio pipeline, no final-render cache, centralized model routing.