# Context handoffs and project state

**Goal:** a new session continues from verified state without re-reading full `log.md` or re-deriving decisions. Human audit trail stays in `log.md`; machine-readable state is a **convenience mirror**, not a second history.

## Files

| File | Role |
|---|---|
| `projects/<name>/log.md` | Authoritative chronological record (hooks + Claude) |
| `projects/<name>/project-state.json` | Current stage, approvals, artifact status, next actions |
| `projects/<name>/work/context/<stage>-context.md` | Optional compact packet written at stage end |

## project-state.json

Maintained with:

```bash
vt-python tools/project_state.py init projects/<name>
vt-python tools/project_state.py set-stage projects/<name> compose
vt-python tools/project_state.py record-approval projects/<name> rough_cut approved
vt-python tools/project_state.py sync-handoff projects/<name>   # parses latest ### Handoff
```

Schema version in `tools/project_state.py` (`SCHEMA_VERSION`). Fields include `stage`, `status`, `approvals`, `artifacts`, `open_issues`, `next_actions`, `master_language` (default `en` for future Hindi).

**Rules**

- Update state when a stage ends or an approval is recorded in `log.md`.
- If state and `log.md` disagree, **`log.md` wins**. Approvals use explicit `**Approval:** name=approved` lines (`pipeline/project-log.md`); stage alone never implies approval.
- Never delete handoff history from `log.md` to shrink context.

## Stage context packets

At handoff, optionally write `work/context/prep-context.md` (etc.) containing:

- Pointer to latest `### Handoff` line range (not a copy of the whole handoff).
- Decisions that are easy to miss (numbers, paths, speed-up factor).
- **Read next:** list of pipeline files and project artifacts only — no paste of `CLAUDE.md`.

Start each stage with:

1. `project-state.json` (or `vt-python tools/project_state.py show`)
2. Latest `### Handoff` from `log.md` (`grep -n '### Handoff'`, read from last match)
3. Open issues from state or handoff

## Instruction loading order

Stable prefix order (helps prompt cache):

1. `CLAUDE.md` (auto)
2. `brand.md`
3. `pipeline/stages.md` + stage pipeline files
4. `project-state.json` / handoff
5. Task-specific files

See `pipeline/instruction-hierarchy.md` for source-of-truth map.