# Project log

**Goal:** `projects/<name>/log.md` records every prompt I give on this video and what Claude did about it, so the project's history is readable later.

**Who writes what**
- **Hooks (automatic, `.claude/settings.json`, scripts in `tools/hooks/`):**
  - `UserPromptSubmit` (`log_prompt.sh`): finds the project from a `projects/<…>/` path in the prompt, else from `.current-project` at the repo root, **only if this same Claude session set it** (the file stores the project and the session id); otherwise nothing is logged, so toolkit maintenance never lands in a video's log. In a new session, name the project path in the first prompt. Saves the prompt verbatim to `work/prompts/<YYYY-MM-DD_HHMMSS>.md` and appends the entry header to `log.md`.
  - `Stop` (`log_tokens.sh`): appends `**Finished** · **Took**` and `**Tokens:**` (main session + subagents) under that entry, before its handoff block if there is one.
  - Errors go to `work/logs/hooks.log` (or `.hook-state/hooks.log`); the hooks never print into the conversation and never fail a turn.
- **Claude:** writes only **Changes / Decisions / Not done** (and the handoff at a stage end) under the hook's header. Never re-type the prompt, never compute tokens or times. Log turns that only answer a question too, with "No changes". Never edit or delete old entries.
- If a prompt names a project that doesn't exist yet, the `Stop` hook writes the header once the turn has created it (it then sits below Claude's notes). If the named path is wrong, nothing is logged (see `.hook-state/hooks.log`): write a normal header yourself with `**Prompt:** (not saved by the hook: <reason>)`.

**Entry format** (lines marked *hook* are written for you)

```markdown
## 2026-10-27 10:43 IST · <first 60 chars of the prompt>          ← hook

**Prompt:** work/prompts/2026-10-27_104305.md                     ← hook
**Started** 10:43:05                                              ← hook

**Changes**
- `work/cutlist.md`: dropped take 2 of paragraph 3 (stumble at 00:41)
- Rendered `out/roughcut_preview.mp4` (720p, 4:12)

**Decisions:** anything chosen for me, with a one-line reason.
**Not done / blocked:** what failed or was skipped, and why.

**Finished** 10:51:40 · **Took** 8 m 35 s                          ← hook
**Tokens:** input 1,204 · cache write 18,845 · cache read 412,330 · output 9,876 (main session; subagents: …)  ← hook
```

**Approvals (authoritative in this file)** — record explicit user OK before Compose or deliverable sign-off (`vt-python tools/project_state.py record-approval projects/<name> rough_cut approved`). Do not use deprecated `set-approval` (it only touched the JSON mirror). Hooks and `record-approval` share the canonical lock `log.md.lock` beside this file.

```markdown
**Approval:** rough_cut=approved
```

Allowed keys: `script`, `rough_cut`, `storyboard`, `stills`, `final`. Values: `approved`, `rejected`, `pending`. Newest line wins. `tools/project_state.py sync-handoff` mirrors these into `project-state.json`; validators read **this file**, not inferred stage.

**Stage handoff** (`pipeline/stages.md`)
- The last entry of every stage is a normal entry followed by a handoff block:

```markdown
### Handoff: 2 · Cut → 3 · Compose
**Decisions:** take 3 of ¶4 (cleanest last take; take 4 stumbles at 02:11) · pauses 0.18/0.30 s · …
**Rejected:** take 4 of ¶4 (restart mid-word); 0.25 s phrase gaps (dragged)
**Open issues:** ¶7 "B-tree" slightly clipped at 03:40; consider re-recording
**Files:** `work/cutlist.md`, `work/edl.json`, `out/roughcut_preview.mp4` (4:12, -16.1 LUFS)
**Next:** waiting for OK on the rough cut; then `pipeline/composition.md`, framing = crop (source 3840 px)
```

- The next stage reads this first, so it must stand alone: exact files, timestamps and values, no "as discussed".

- A text-posts run (`/text-posts`) is a normal entry titled `· Text posts`: the approved hooks, the photo approval (or "self-judged" and why), files in `out/text-posts/`, character counts, QA fixes.
- A carousel run (`/carousel`) is a normal entry titled `· Carousel`: slide count, the outline/look approvals (or "self-judged" and why), files in `out/carousel/`, QA fixes.
- Times are local (IST). "Took" is from the prompt hook to the last assistant message.
- Changes name files relative to the project and say what changed in each, not just "edited".
- Never put API keys, `.env` values or full command logs in the log. Link to `work/logs/<file>` instead.

**Tokens** (computed by `tools/hooks/projlog.py`, not by Claude)
- Source: Claude Code's session transcript `~/.claude/projects/<cwd with / replaced by ->/<session-id>.jsonl`, assistant messages from the prompt's timestamp on, deduplicated by message id; subagents from `<session-id>/subagents/*.jsonl` (and sidechain entries) over the same window, totalled separately.
- The same sum by hand, for a check:

```bash
jq -sc '
 [ .[] | select(.isSidechain|not) ] as $all
 | ($all | map(select(.type=="user" and (.message.content|type)=="string")) | last) as $p
 | ($all | map(select(.type=="assistant" and .timestamp >= $p.timestamp)) | unique_by(.message.id)) as $a
 | {started:$p.timestamp, finished:($a|map(.timestamp)|max),
    input:($a|map(.message.usage.input_tokens)|add),
    cache_write:($a|map(.message.usage.cache_creation_input_tokens)|add),
    cache_read:($a|map(.message.usage.cache_read_input_tokens)|add),
    output:($a|map(.message.usage.output_tokens)|add)}' "$TRANSCRIPT"
```

- The `Stop` hook runs after the final reply, so the whole turn is counted. If the transcript can't be read it writes "Tokens: not available" with the reason; it never guesses.
- **Per-project roll-up:** `vt-python tools/vt_log.py summary projects/<name>/log.md` (optional; sums `**Tokens:**` lines only).
