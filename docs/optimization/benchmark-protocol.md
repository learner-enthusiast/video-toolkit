# Benchmark protocol (token and elapsed time)

## Purpose

Compare **measured** production usage (hook-written `**Tokens:**` / `**Took**` lines), not estimated context bytes from `pipeline/token-budget.md`.

## Prerequisites

- Same project folder structure and `vt-python tools/vt_log.py summary|compare`.
- Same model IDs as recorded in transcripts (`message.model` in Claude Code JSONL).
- Hook stage capture: `**Stage:**` at prompt time (requires `project-state.json` mirror when the turn starts).

## Procedure

1. Pick a baseline git commit (verify with `git log`; e.g. pre-optimization merge) and a candidate commit/branch.
2. Same sample media and script task instructions; fresh Claude Code session per run.
3. Run the same pipeline stage (Prep, Cut, Compose, or Deliver) with equivalent tool versions.
4. Repeat ≥ 3 runs per arm (cache-cold first, then cache-warm if testing caches).
5. Collect `projects/<name>/log.md` from each run (or copies).
6. Aggregate: `vt-python tools/vt_log.py summary projects/<name>/log.md`
7. Compare: `vt-python tools/vt_log.py compare baseline-log.md candidate-log.md`

## Quality checklist (separate from tokens)

A successful optimization must pass the same creative gates:

- Technical validators (`vt_validate`, subtitles, render specs).
- Spoken content and SRT match actual audio.
- Audio cleaning gate and delivery loudness.
- Final fresh `--thorough` video-inspect + Opus vision QA + human approval.

Lower token counts with worse visuals or skipped QA are **failed** benchmarks.

## Historical data

If no archived logs exist for the chosen baseline commit, state that explicitly. Do not infer savings from `bytes/4` context estimates.