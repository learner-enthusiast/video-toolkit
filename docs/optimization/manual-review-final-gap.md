# Manual review — final gap closure

**Reviewer:** Composer agent (Opus-tier automated review unavailable on current plan).  
**Branch:** `final-gap-closure` vs `main` @ `9cf4a54`.  
**Date:** 2026-11-25.

## Symlink handling

- Inspect bundles: `path_safety.assert_no_symlinks_under` + `lstat` on walk; symlinked directories no longer skipped silently.
- Restore: staging copy via `resolve_contained`; no `copytree` followlinks.
- Asset cache: `resolve_in_asset_bundle` + `lstat` on lexical path; bundle root symlink rejected on install.

## Manifest / restore

- `cmd_restore` repeats full manifest + entry + bundle validation (not trusting prior lookup).
- Malformed JSON top-level types yield safe miss / integrity failure (no `AttributeError`).
- Corrupt asset/inspect manifests quarantined to `.corrupt[-N]` before replacement.

## Locks / concurrency

- No new lock ordering changes; existing manifest lock → per-key lock preserved on asset writes.
- Project state: `set-stage` rebuilds from `log.md` when mirror invalid; `show` read-only on errors.

## Token attribution

- Stage from explicit `**Stage:**` only; handoff lines no longer attributed.
- Compare surfaces model mismatches and excludes `unknown` from stage deltas.

## Production gates

- Final inspect cache refusal tests pass; no weakening of render/audio validation observed in diff.

## Residual risk

- Hook concurrency stress not exhaustive on all platforms.
- Benchmark pending until real paired logs exist.