# Token-diet optimization — engineering report

**Date:** 2026-11-25  
**Branch:** `token-diet` (implementation session; not committed unless requested)  
**Baseline:** `docs/optimization/baseline.md`

## A. Original architecture

Instruction-driven video production: four sessions per video (Prep → Cut → Compose → Deliver), Markdown skills + `pipeline/` docs, per-project `work/` artifacts, shared `components/` and `icons/`. Token diet (Nov 2026) split component index, externalized skill references, automated `log.md` headers/tokens via hooks, and measured stage-start byte reductions in `pipeline/token-budget.md`.

## B. Baseline inefficiencies

See baseline § "Largest inefficiencies": repeated session context, per-project validator duplication, verbose job logs, no inspect cache, unstructured state, single-tier model sessions, non-optional transcription depth.

## C. Model routing

| Role | ID | Effort default |
|---|---|---|
| Production | `claude-sonnet-5-5` | medium |
| Creative / final visual QA | `claude-opus-5-5` | high |
| Worker | `claude-haiku-5-5` | low |
| Escalation (optional) | `claude-fable-5-2[1m]` | high |

Authoritative config: `config/model-routing.json`, policy: `pipeline/model-routing.md`. Verified Claude Code **2.1.331**; `--model` and `--effort` available.

**Limitation:** Cursor/Claude Code session model is user-selected at launch; routing is enforced by documentation and checkpoints, not by automatic runtime switching inside one session.

## D. Files changed (this mission)

| Path | Description |
|---|---|
| `docs/optimization/baseline.md` | Phase 0 audit |
| `docs/optimization/final-report.md` | This report |
| `config/model-routing.json` | Model IDs and task classes |
| `pipeline/model-routing.md` | Tier policy and escalation |
| `pipeline/context-handoffs.md` | State + context packets |
| `pipeline/instruction-hierarchy.md` | Conflict resolution order |
| `pipeline/job-results.md` | Compact job/validate conventions |
| `pipeline/transcribe-adaptive.md` | Experimental; not default |
| `tools/project_state.py` | `project-state.json` |
| `tools/validate/vt_validate.py` | Shared validators |
| `tools/job_report.py` | JSON from `.status` |
| `tools/inspect_cache.py` | Inspect report cache |
| `tools/vt_log.py` | Token sums from log.md |
| `tools/model_verify.py` | Verify IDs vs client |
| `tools/scaffold_remotion.py` | Remotion starter |
| `templates/remotion-starter/README.md` | Starter docs |
| `tests/test_project_state.py`, `tests/test_validate.py` | Unit tests |
| `CLAUDE.md`, `pipeline/stages.md`, `delegation.md`, `composition.md`, `video-inspect.md`, `.claude/skills/new-video/SKILL.md` | Wiring |

## E. New production architecture

- **State:** `project-state.json` mirrors handoffs; `log.md` authoritative.
- **Context:** latest handoff + state; optional `work/context/*-context.md`.
- **Components:** unchanged intent index; no extra fragmentation.
- **Validation:** `vt_validate.py` before expensive steps where applicable.
- **Jobs:** prefer `job_report.py` JSON.
- **Caching:** inspect report content keys in `work/inspect/.cache/`.
- **Logging:** hooks unchanged; `vt_log.py summary` for aggregates.
- **Remotion:** `scaffold_remotion.py` + symlinks to shared libraries.

## F. Token savings

| Kind | Status |
|---|---|
| Measured (prior token-diet) | Stage-start instruction bytes −21% to −49% per stage (`token-budget.md`) |
| Measured (this mission) | No new production sessions run in this audit pass |
| Estimated | Sonnet-default sessions vs all-Opus: depends on user session choice |
| Call reduction | Validators + job JSON + inspect cache reduce re-reads and log paste |
| Rework reduction | Stage gate validator blocks Compose without rough_cut approval |

No invented percentage for this mission's code changes.

## G. Model economics

Subscription (`claude_pro`); hooks log tokens, not dollars. Compare tiers using `log.md` after Sonnet-default production sessions.

## H. Production quality

Unchanged gates: voice cleaning, rough cut OK, Opus vision QA, GPU policy, deliverables, transcription depth (default path). Model routing is efficiency, not waiver of QA.

## I. Tests

| Test | Result |
|---|---|
| `python3 -m unittest tests.test_project_state tests.test_validate` | Run in CI/local |
| `vt-python tools/model_verify.py` | Run manually |
| Full video dry run | Not executed (per instruction) |
| Adaptive transcription | Not enabled |
| Cache on real MP4 | Not executed in this pass |

## J. Remaining opportunities

- Promote project-local `check_phrases.py` / `align_ctc.py` into toolkit with golden tests.
- Benchmark adaptive transcription then opt-in via `project-state.json`.
- Incremental Remotion scene renders with content-addressed plate cache.
- Hook extension for effort/model per turn in `vt_log.py`.
- **Hindi / Roman Hindi pipeline:** explicit separate mission (not started).