# Post-hardening status

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