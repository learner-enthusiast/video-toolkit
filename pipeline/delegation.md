# Delegation

**Goal:** Claude makes every decision. Low-stakes work goes to outside CLIs so the main session doesn't spend its (expensive, whole-session) turns on it. Haiku is the last resort.

## 1. What may be delegated

**Low-stakes** = a task whose result can't lower the quality of the final video if it's slightly off, because Claude checks it afterwards:
- folder/project scaffolding, renaming, moving files, cleaning up `work/`
- ffprobe/metadata reads, duration measurements, proxy/low-res transcodes
- downloading official logos and filling `assets/logos/SOURCES.md`
- SRT formatting/line-wrapping, social copy JSON scaffolding, `log.md` updates
- boilerplate for a component whose spec is already final (Claude reviews every line before use)

**Never delegated (Claude keeps these):** script, cut decisions, storyboard, creative take, layout states, `brand.md` decisions, final component visuals, render settings, QA, and anything visible on screen that hasn't been reviewed. Vision is never delegated for a final judgment (`pipeline/video-inspect.md`).

**Heavy exact-command jobs** (final renders, Whisper, final encodes, installs, video-inspect runs) are not low-stakes and must not go to an outside CLI. Claude writes the exact commands and a **Haiku batch** runs them verbatim (section 6). *(Open decision: if you'd rather Claude run these itself, say so.)*

## 2. Order

1. GitHub Copilot CLI (`copilot`)
2. OpenAI Codex CLI (`codex`)
3. Cursor agent (`cursor-agent`)
4. Haiku subagent: only when all three are out of usage, not installed, not logged in, or failing

```
 task ──▶ low-stakes? ──no──▶ Claude does it (or Haiku batch if heavy exact commands)
              │yes
              ▼
   Copilot usage ok? ──yes──▶ run (bg, timeout, log) ──▶ monitor ──▶ verify
         │no / error                                        │fail/hang
         ▼                                                  ▼
   Codex usage ok?   ──yes──▶ same ...              kill → next tool
         │no
         ▼
   cursor-agent ok?  ──yes──▶ same ...
         │no
         ▼
       Haiku subagent
```

## 3. Per-tool commands (verified on this machine, Nov 2026)

| | Copilot CLI | Codex CLI | cursor-agent |
|---|---|---|---|
| Install (global) | `npm i -g @github/copilot` | `npm i -g @openai/codex` (or the standalone installer) | `curl https://cursor.com/install -fsS \| bash` |
| Login check | `gh auth status` and `copilot login` once | `codex login status` → `Logged in using ChatGPT` | `cursor-agent status` → `Logged in as …` |
| Non-interactive run | `copilot -p "<task>" --allow-all-tools --no-ask-user --no-color --max-ai-credits <n> --usage-output-file <json>` | `codex exec --json -s workspace-write -C <dir> --skip-git-repo-check --ephemeral -o <last-msg-file> "<task>"` | `cursor-agent -p --force --sandbox disabled --workspace <dir> --output-format text "<task>"` |
| Scope to the project | run with `cwd` = project dir; without `--allow-all-paths` it stays in cwd (add more with `--add-dir`) | `-C <dir>` + `-s workspace-write` (use `-s read-only` for pure reads) | `--workspace <dir>`. `--sandbox enabled` **fails here** (AppArmor), so scope is by prompt only: keep tasks tiny |
| Usage check | `gh api /copilot_internal/user` → `.quota_snapshots.premium_interactions.percent_remaining` and `.quota_reset_date` | `codex login status`, then the `rate_limits` object in the newest `~/.codex/sessions/*/*/*/rollout-*.jsonl` (see below) | **none**: the CLI shows login and tier only (`cursor-agent about`); usage lives on cursor.com |
| Hard spend cap | `--max-ai-credits <n>` (**minimum 30**; a probe-sized task used ~0.3) | none (use the timeout) | none (use the timeout) |
| Limit/auth errors to grep | `quota`, `rate limit`, `429`, `premium`, `exceeded`, `not authenticated`, `login` | `rate_limit_reached_type` non-null, `usage limit`, `429`, `not logged in`, `"type":"error"` | `usage limit`, `rate limit`, `429`, `not logged in`, `Error:` |

**Usage-check rules (mandatory before every delegation)**
- **Copilot:** OK when `percent_remaining ≥ 15` and overage isn't needed. `gh api /copilot_internal/user` is an undocumented endpoint; it worked here. If it errors, treat Copilot as unreadable → skip.
- **Codex:** `rate_limits` is only partly filled on this plan (`plan_type: go`, `primary`/`secondary` null, so no percentage). Run `codex login status`; read the last `rate_limits` line with `grep -o '"rate_limits":{.*' <newest rollout> | tail -1`. OK when logged in and `rate_limit_reached_type` is null and, if `primary`/`secondary` carry `used_percent`, both are < 85. Treat it as a **partial reading**: send one small chunk per call.
- **cursor-agent:** no way to read remaining usage, so by the "unreadable → skip" rule it is **skipped** and the chain goes to Haiku. To allow it anyway, say so in the prompt (then it gets one tiny chunk per call, canary first: `cursor-agent -p --force --sandbox disabled --workspace <dir> "Reply with exactly: OK"`).
- **Haiku:** no check.
- A low-headroom or unreadable tool is skipped, not retried. Say which tool was skipped and why in `log.md`.

**Size the batch to the headroom.** Split big jobs into chunks that each finish on their own (one logo set, one folder, one SRT), so a limit hit loses one chunk, not the job.

## 4. How to run one

Always non-interactive, in the background, with a hard timeout, output to `projects/<name>/work/delegation/<NN>-<tool>-<task>.log`:

```bash
D=projects/<name>/work/delegation; mkdir -p $D
# example: Copilot, 10-minute cap
( cd projects/<name> && timeout 600 copilot -p "<task>" --allow-all-tools --no-ask-user --no-color \
    --max-ai-credits 30 --usage-output-file work/delegation/01-copilot-probe.usage.json \
    > work/delegation/01-copilot-probe.log 2>&1; echo "EXIT $?" >> work/delegation/01-copilot-probe.log ) &
```

Every task prompt contains: the exact files/paths, the exact expected output (file name and format), and **"Do not touch `raw/`, `script.md`, `brand.md`, `CLAUDE.md`, or anything outside `<dir>`."**

**Monitor**
- `tail` the log every 30–60 s (Monitor with an until-loop, no sleep polling). No new output for 120 s, an `EXIT` marker ≠ 0, or any limit/auth/rate error from the table → `kill` it, mark the chunk failed, re-run that chunk on the next tool in the order.
- A tool that asks for permission and waits is a hang: kill it and fix the flags, don't wait.

**Verify every result yourself** before using it (files exist, `ffprobe`/`diff`/spot-check). The other tool only did the work.

**Log it** in the project's `log.md`: task, tool used, usage before (e.g. `copilot premium 99.6%`), result, any fallback.

## 5. Code helpers

Boilerplate for a component with a final spec goes through the same order. Give exact specs (props, geometry, timing). Claude writes the visual components and reviews every line a helper writes. If a tool is refused by Claude Code's auto-mode permission classifier (it sends code to an outside service), go to the next tool; if all are refused, do it yourself and tell me. Never work around a refusal.

## 6. Haiku fallback and heavy-job batches

Haiku runs the exact commands Claude wrote, in order, and reports back. It never chooses takes, edits or "fixes" a command, retries with different flags, or judges quality.

**Batch the handoff:** one handoff per step, commands verbatim in a numbered list, **stop at the first non-zero exit** unless a command is marked `(continue on error)`.

```text
Step: <step>   Project: projects/<name>   CWD: projects/<name>/work
Run these commands exactly, in order. Do not change, add, or skip anything. Run ONE command per message.
Save all stdout+stderr to work/logs/<step>.log (append each command with a "### <n> <command>" header).
On the first non-zero exit, stop and report.
1. <command>
2. <command>
Report (nothing else):
- each command: exit code
- key numbers: <list exactly which: duration, resolution, fps, LUFS / true peak, file sizes, frame counts…>
- every line containing error / warning / failed / invalid / mismatch / non-monotonic / deprecated, copied VERBATIM with its command number
- files produced, with sizes
```

- Full output goes to the log, never into the reply. No opinions.
- Any non-zero exit, unexpected warning, or number outside spec (duration off by > 1 frame, wrong fps/resolution, LUFS off target, suspiciously small file): Claude reads the log and debugs directly, then the corrected batch goes back.
- Wrap every long encode in `timeout <s>`, in the foreground. A background batch once sat on a hung ffmpeg for an hour.
- Haiku may send two numbered commands in one message and run them in parallel (a 33-segment 1080x1920 plate encode ran beside the voice encode at 0.25x and timed out). Always write "run ONE command per message"; give such an encode ≥ 2400 s.
- A Haiku runner polling a `nohup` job can stall between steps, and stopping it kills the encode it launched. For long render chains write one chain script, run it detached, and check the log for its EXIT markers.
