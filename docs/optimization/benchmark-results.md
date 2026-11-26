# Token/time benchmark: status

**Status after PRs #10–#14 (2026-11-26): the instrumentation is in place; no production benchmark has been run.** No paired baseline and candidate `log.md` files exist, so no measured token or time saving is claimed.

## What is measured so far
- **Fixed repo reads per stage:** 27–33% smaller after PR #13 (`pipeline/token-budget.md`). This is a `bytes/4` estimate of file sizes, not usage.
- **Script equivalence:** the tracked tools in `tools/` reproduced one delivered episode's timeline and SRTs exactly, and an identical video-inspect report (PR #12). That shows behaviour was kept; it measures no saving.

## What the next benchmark can use (new in PR #14)
- Per turn: tokens by model, API call counts and a cost-weighted total in `log.md`.
- Per stage: `work/metrics/<stage>-<run_id>.json` (`benchmark-protocol.md`, Per-stage record), with cache hits and misses, delegated-CLI usage and quality results.
- Logs written before PR #14 have no `**Calls:**` or `**Cost:**` lines: their totals for those are `null`. A baseline from before PR #10 can be compared on tokens and time only.
- Before PR #14, `vt_log.py` also returned no per-model breakdown for any log entry except one at the very end of the file.

## How to record it
1. Pick one project and one stage, and follow [`benchmark-protocol.md`](benchmark-protocol.md): at least 3 fresh sessions per arm, same media, instructions and models.
2. At each stage end run `vt-python tools/vt_log.py record projects/<name> --stage <stage>`.
3. Compare the logs: `vt-python tools/vt_log.py compare <baseline-log.md> <candidate-log.md>`.
4. Judge quality with the protocol's checklist, separately from tokens.

## Quality gate
Lower usage without the same editing, audio, subtitle and fresh final visual QA is a **failed** optimization.

## Microbenchmarks
`python3 -m unittest tests.test_transcript_incremental.TranscriptIncrementalTest.test_benchmark_table -v` prints full-scan vs incremental bytes read and wall time; token totals must match exactly. `tests.test_asset_cache` asserts one input hash per store.

## Baseline commits
| Commit | Role |
|---|---|
| `3a4738b` | `main` before PR #10 (token-efficiency baseline) |
| `63da975`, `9cf4a54` | earlier reliability-pass references |
