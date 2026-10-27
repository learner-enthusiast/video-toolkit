# Project log

**Goal:** `projects/<name>/log.md` records every prompt I give on this video and what Claude did about it, so the project's history is readable later.

**When**
- At the end of every turn that touched the project, append one entry. Never edit or delete old entries.
- Log turns that only answer a question too, with "No changes".

**Entry format**

```markdown
## 2026-10-27 10:43 IST · <short title>

**Prompt:** (verbatim; trim only pasted logs or huge blocks, and say so)
> ...

**Changes**
- `work/cutlist.md`: dropped take 2 of paragraph 3 (stumble at 00:41)
- Rendered `out/roughcut_preview.mp4` (720p, 4:12)

**Decisions:** anything chosen for me, with a one-line reason.
**Not done / blocked:** what failed or was skipped, and why.

**Started** 10:43:05 · **Finished** 10:51:40 · **Took** 8 m 35 s
**Tokens:** input 1,204 · cache write 18,845 · cache read 412,330 · output 9,876 (main session; subagents: ~42,000)
```

- Times are local, with the timezone. "Took" is from the prompt's timestamp to the last reply.
- Changes name files relative to the project and say what changed in each, not just "edited".
- Never put API keys, `.env` values or full command logs in the log. Link to `work/logs/<file>` instead.

**Tokens**
- Claude can't see its own usage directly, but Claude Code's session transcript records it per message: `~/.claude/projects/<cwd with / replaced by ->/<session-id>.jsonl`. Sum the turn with:

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

- Run it as the last step of the turn, so the final reply is the only part not counted. Write "(approx.)" after the numbers.
- Subagent usage: if subagent transcripts exist (in the session's folder next to the `.jsonl`), sum them the same way and give the total separately. If they can't be found, write "subagents: not measured".
- If the transcript can't be read, write "Tokens: not available" with the reason. Never guess numbers.
