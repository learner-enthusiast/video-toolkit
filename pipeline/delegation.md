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

## Two kinds of delegated work

| Kind | Examples | Who runs it |
|---|---|---|
| Low-stakes tasks | scaffolding, renames, ffprobe reads, proxies, logo downloads + `SOURCES.md`, SRT wrapping, social JSON scaffold, `log.md`, boilerplate from a final spec | CLI chain: Copilot → Codex → cursor-agent (canary) → Haiku |
| Heavy jobs | final renders, Whisper, final encodes, video-inspect runs, installs | Haiku runner (section 6); Claude only observes |

Heavy jobs never go through the CLI chain: command timeouts, sandboxes and quota limits can kill a long GPU job midway.

## 2. Low-stakes chain

1. GitHub Copilot CLI (`copilot`)
2. OpenAI Codex CLI (`codex`)
3. Cursor agent (`cursor-agent`)
4. Haiku subagent: only when all three are out of usage, not installed, not logged in, or failing

```
 task ──▶ low-stakes? ──no──▶ heavy: Haiku runner (§6) · else Claude does it
              │yes
              ▼
   Copilot usage ok? ──yes──▶ run (bg, timeout, log) ──▶ monitor ──▶ verify
         │no / error                                        │fail/hang
         ▼                                                  ▼
   Codex usage ok?   ──yes──▶ same ...              kill → next tool
         │no
         ▼
   cursor canary ok? ──yes──▶ ONE small chunk, short timeout, re-canary before the next
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
| Usage check | `gh api /copilot_internal/user` → `.quota_snapshots.premium_interactions.percent_remaining` and `.quota_reset_date` | `codex login status`, then the `rate_limits` object in the newest `~/.codex/sessions/*/*/*/rollout-*.jsonl` (see below) | **none confirmed** (`cursor-agent about` shows login and tier only). Its check is the **canary**, below |
| Hard spend cap | `--max-ai-credits <n>` (**minimum 30**; a probe-sized task used ~0.3) | none (use the timeout) | none (use the timeout) |
| Limit/auth errors to grep | `quota`, `rate limit`, `429`, `premium`, `exceeded`, `not authenticated`, `login` | `rate_limit_reached_type` non-null, `usage limit`, `429`, `not logged in`, `"type":"error"` | `usage limit`, `rate limit`, `429`, `not logged in`, `Error:` |

**Usage-check rules (mandatory before every delegation)**
- **Copilot:** OK when `percent_remaining ≥ 15` and overage isn't needed. `gh api /copilot_internal/user` is an undocumented endpoint; it worked here. If it errors, treat Copilot as unreadable → skip.
- **Codex:** `rate_limits` is only partly filled on this plan (`plan_type: go`, `primary`/`secondary` null, so no percentage). Run `codex login status`; read the last `rate_limits` line with `grep -o '"rate_limits":{.*' <newest rollout> | tail -1`. OK when logged in and `rate_limit_reached_type` is null and, if `primary`/`secondary` carry `used_percent`, both are < 85. Treat it as a **partial reading**: send one small chunk per call.
- **cursor-agent (canary):** no usage-read command is confirmed, so a canary is its check. Before **each** use run `timeout 60 cursor-agent -p --force --sandbox disabled --workspace <dir> "Reply with exactly: OK"`. If it fails, times out, doesn't print `OK`, or shows a limit/auth error, skip to Haiku. If it passes, send exactly **one small chunk** with a short timeout (≤ 300 s), monitored; run the canary again before the next chunk. If a real usage/status command turns up, use it instead and update the table.
- **Haiku:** no check.
- A low-headroom or unreadable tool (Copilot, Codex) is skipped, not retried. Say which tool was skipped and why in `log.md`.

**Size the batch to the headroom.** Split big jobs into chunks that each finish on their own (one logo set, one folder, one SRT), so a limit hit loses one chunk, not the job.

## 4. How to run one

Always non-interactive (prompt as an argument, auto-approve scoped to the project folder), in the background, with a hard timeout, output to `projects/<name>/work/delegation/<NN>-<tool>-<task>.log`:

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

## 6. Heavy jobs: Haiku runner, Claude observes

```
Claude ─ writes exact command batch (gpu-run, flags, paths, timeouts)
   ▼
Haiku runner ─ launches each job DETACHED (setsid/nohup) ─ watches logs
   │  on error/stall: STOP, report. Never change settings or retry differently.
   ▼
work/jobs/<NN>-<job>.status  (done/failed, duration, output path, last 20 log lines)
   ▼
Claude ─ reads .status ─ verifies output (ffprobe streams/duration, size) ─ next step
```

- Claude hands Haiku an **exact** batch: full commands, every GPU job wrapped in `gpu-run`, all flags, input/output paths and a timeout per job.
- Haiku runs them exactly as written. It must not change flags, codecs, quality, resolution, paths or order, and must not retry with different settings.
- Every job is launched **detached** (`setsid nohup … &`) and writes its own log to `work/jobs/<NN>-<job>.log` and its own `.status` file, so it keeps running even if the Haiku session ends.
- On fail or stall Haiku stops the batch and reports. Any fix is Claude's decision.
- Claude does not tail logs. It reads the `.status` files and verifies outputs (ffprobe streams/duration, size); only on a failure or an odd number does it read the log and debug.
- Installs are always global (not per project); Haiku runs them from Claude's exact list.

**Job wrapper.** Claude writes this once per project as `work/jobs/run.sh` (a project file, never in the toolkit) and every heavy job is launched through it, so `.status` is identical for all jobs:

```bash
#!/bin/bash
# usage: run.sh <NN-job> <timeout-seconds> <output-path> -- <command...>
N=$1; T=$2; OUT=$3; shift 4; D="$(cd "$(dirname "$0")" && pwd)"
t0=$(date +%s); timeout "$T" "$@" > "$D/$N.log" 2>&1; rc=$?
{ echo "state=$([ $rc = 0 ] && echo done || echo failed)"; echo "exit=$rc"
  echo "seconds=$(( $(date +%s) - t0 ))"; echo "output=$OUT"; echo "log_tail<<"; tail -20 "$D/$N.log"
} > "$D/$N.status.tmp" && mv "$D/$N.status.tmp" "$D/$N.status"
```

Launch (the runner does exactly this): `setsid nohup work/jobs/run.sh 01-render 1200 out/x.mp4 -- gpu-run ffmpeg … > /dev/null 2>&1 &`. The `.status` file appears only when the job ends (atomic `mv`); while it's absent the job is running (`pgrep -f <NN-job>`). Delete stale `.status` files before a re-run.

**Handoff template (Haiku)**

```text
Step: <step>   Project: projects/<name>   CWD: projects/<name>/work
Run these jobs exactly as written, in order, ONE per message. Do not change, add, or skip anything.
Launch each detached through `work/jobs/run.sh` as shown. Wait for its .status file (check every 15 s, hard limit = its timeout + 30 s).
On a failed/stalled job: stop the batch and report. Never retry with different settings.
1. <job command with wrapper>
2. <job command with wrapper>
Report (nothing else): for each job the .status path, state, exit, seconds; and every error/warning line verbatim.
```

**Gotchas**
- Haiku may send two numbered commands in one message and run them in parallel (a 33-segment 1080x1920 plate encode ran beside the voice encode at 0.25x and timed out). Always write "ONE per message"; give such an encode ≥ 2400 s.
- Stopping a polling runner kills jobs it launched unless they were started with `setsid`; that is why every job is detached.
- Any non-zero exit, unexpected warning, or number outside spec (duration off by > 1 frame, wrong fps/resolution, LUFS off target, suspiciously small file): Claude reads the log, debugs, and sends a corrected batch.
- **Haiku fallback for low-stakes tasks** (when the chain is exhausted) uses the same runner and report format, with output in `work/logs/<step>.log`.
