# Token/time benchmark — status

## Automated microbenchmarks (this pass)

Run locally:

```bash
python3 -m unittest tests.test_transcript_incremental.TranscriptIncrementalTest.test_benchmark_table -v
```

The test prints JSON with full-scan vs incremental bytes read and wall time on a 500-line history fixture. Token totals must match exactly.

Asset-cache: `tests.test_asset_cache.AssetCacheTest.test_single_input_hash_per_store` asserts one input SHA-256 per store command.

Real production A/B logs remain **pending** (no paired `log.md` with hook tokens in the repo).

# Token/time benchmark — status (historical)

**As of gap-closure pass (`main` @ `9cf4a54`):** no paired baseline/candidate `log.md` files with hook `**Tokens:**` / `**Took**` lines were found in this repository clone. A valid A/B comparison cannot be reported without fabricated numbers.

## Baseline commit (pre-optimization reference)

| Commit | Role |
|--------|------|
| `63da975` | Pre–reliability-pass `main` (audit baseline) |
| `9cf4a54` | Post–PR #4 merge (`main` at gap-closure start) |

Use `git log --oneline 63da975..9cf4a54` for intervening hardening commits.

## How to record the next benchmark

1. Pick one project and one stage (e.g. Compose) per [`benchmark-protocol.md`](benchmark-protocol.md).
2. Run two fresh sessions on the **same** media and instructions with the **same** model IDs (cache-cold vs cache-warm noted separately).
3. Ensure hooks emit `**Stage:**`, `**Tokens:**`, and `**Took**` in `log.md`.
4. Compare:

   ```bash
   vt-python tools/vt_log.py compare projects/<name>/log.md.baseline projects/<name>/log.md
   ```

5. Judge quality with the checklist in `benchmark-protocol.md` (separate from token deltas).

## Quality gate

Lower token usage without maintaining editing, audio, subtitle, and final fresh visual QA is a **failed** optimization.