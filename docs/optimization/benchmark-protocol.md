# Benchmark protocol (token and elapsed time)

## Purpose

Compare **measured** production usage (hook-written `**Tokens:**` / `**Took**` lines), not estimated context bytes from `pipeline/token-budget.md`.

## Prerequisites

- Same project folder structure and `vt-python tools/vt_log.py summary|compare`.
- Same model IDs as recorded in transcripts (`message.model` in Claude Code JSONL).
- Hook stage capture: `**Stage:**` at prompt time (requires `project-state.json` when the turn starts: `project_state.py set-stage`, `pipeline/stages.md`).

## Procedure

1. Pick a baseline git commit (verify with `git log`; e.g. pre-optimization merge) and a candidate commit/branch.
2. Same sample media and script task instructions; fresh Claude Code session per run.
3. Run the same pipeline stage (Prep, Cut, Compose, or Deliver) with equivalent tool versions.
4. Repeat ≥ 3 runs per arm (cache-cold first, then cache-warm if testing caches).
5. Collect `projects/<name>/log.md` from each run (or copies).
6. Aggregate: `vt-python tools/vt_log.py summary projects/<name>/log.md`
7. Compare: `vt-python tools/vt_log.py compare baseline-log.md candidate-log.md`

## Per-stage record

`vt-python tools/vt_log.py record projects/<name> --stage <stage> [--since "YYYY-MM-DD HH:MM"] [--validators pass|fail] [--final-qa pass|fail]` writes `work/metrics/<stage>-<run_id>.json` at the stage handoff. The Stop hook doesn't run it. It covers completed turns tagged with that stage, so the turn that runs it is not included. `--since` (IST) selects one run when a stage was done more than once.

**A value that wasn't measured is `null`.** Nothing is estimated from transcript or file sizes, and a total is `null` if any turn lacks that measure (for example, logs written before `**Calls:**` and `**Cost:**` existed).

| Field (`schema_version` 1) | Content |
|---|---|
| `run_id`, `project`, `stage`, `recorded_at`, `toolkit_commit` | identity of the record |
| `turns`, `window_start` | turns counted; start of the first one |
| `model_calls` | `main`, `sidechain`, `subagents`, `by_model`, `by_tier` (API calls) |
| `tokens` | `main` and `subagents`, each `input`, `cache_read`, `cache_write`, `output` |
| `cost_weighted_usd` | sum of the turns' `**Cost:**` lines |
| `wall_time` | `turn_seconds` (sum of **Took**), `span_seconds` (first prompt to last finish, waiting included) |
| `cache` | `asset` {`hits`, `misses`}, `inspect` {`hits`, `misses`, `final_qa_bypasses`} from `work/cache/events.jsonl` since `window_start` |
| `delegation` | per `work/delegation/*.log` since then: `log`, `tool`, `exit_code`, `usage` (Copilot's `<same name>.usage.json`) |
| `quality` | `validators_passed`, `fresh_final_qa_passed` (only from the flags), `user_approval` (from `**Approval:**` lines for the stage) |

## Quality checklist (separate from tokens)

A successful optimization must pass the same creative gates:

- Technical validators (`vt_validate`, subtitles, render specs).
- Spoken content and SRT match actual audio.
- Audio cleaning gate and delivery loudness.
- Final fresh `--thorough` video-inspect + Opus vision QA + human approval.

Lower token counts with worse visuals or skipped QA are **failed** benchmarks.

## Historical data

If no archived logs exist for the chosen baseline commit, state that explicitly. Do not infer savings from `bytes/4` context estimates.