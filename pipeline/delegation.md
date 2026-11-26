# Delegation

**Goal:** the Sonnet session makes every decision; mechanical work goes wherever it costs the fewest tokens.

## 1. Who does what

| Work | Who |
|---|---|
| One command or small edit: ffprobe, renames, proxies, `log.md`, SRTs (`tools/captions/make_srt.py`), scaffolding (`tools/scaffold_remotion.py`), social JSON, a logo into `icons/` + its row | **Claude, directly.** One Bash call costs less than usage check + canary + launch + monitor + verify. |
| Multi-file boilerplate from a **final** spec | CLI chain (§2). Claude reviews every line before use. |
| Heavy jobs: voice cleaning (`tools/clean_audio.py`, exact command from `pipeline/voice-cleaning.md`), final renders, Whisper, final encodes, video-inspect, installs | `tools/jobs/batch.sh` (§5). No LLM runner. Never the chain: its timeouts, sandboxes and quotas can kill a long GPU job. |

**Never delegated:** script, cuts, storyboard, creative take, layout states, `brand.md`, final visuals, render settings, QA, the voice-cleaning gate decision, final vision judgment, or anything on screen not yet reviewed. (`creative-director` and `vision-qa` are the creative tier, not delegation.)

## 2. Boilerplate chain

Copilot → Codex → cursor-agent (canary) → Haiku subagent (only when all three are unavailable or failing). If the permission classifier refuses a tool, try the next, else write it yourself and say so. Never work around a refusal.

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

**Check usage before every delegation.** Skip a tool that is low or unreadable (don't retry it) and say why in `log.md`.
- **Copilot:** OK at `percent_remaining ≥ 15` with no overage needed; endpoint error = unreadable.
- **Codex:** OK when logged in, `rate_limit_reached_type` is null and any `used_percent` is < 85 (`grep -o '"rate_limits":{.*' <newest rollout> | tail -1`). Often partial on this plan: one small chunk per call.
- **cursor-agent:** no usage command, so before **each** use: `timeout 60 cursor-agent -p --force --sandbox disabled --workspace <dir> "Reply with exactly: OK"`. On `OK`, send **one** small chunk (timeout ≤ 300 s).
- Size each chunk to finish on its own.

## 4. Running one

Non-interactive, in the background, with a hard timeout, output to `projects/<name>/work/delegation/<NN>-<tool>-<task>.log` ending in `EXIT <code>`. The prompt names the exact files, the expected output (name and format) and "Do not touch `raw/`, `script.md`, `brand.md`, `CLAUDE.md`, or anything outside `<dir>`." A limit/auth error from the table, no output for 120 s or a permission prompt → kill it and re-run the chunk on the next tool. Verify every result yourself, and log task, tool, usage before, result and fallback in `log.md`.

## 5. Heavy jobs: `batch.sh`

1. Claude writes the exact batch to `work/jobs/<stage>.batch`, one job per line: `NN-name | timeout-seconds | output-path | command`. Every GPU command is wrapped in `gpu-run`, with all flags and paths. Commands run from `work/`.
2. Launch it with the **Bash tool in the background** (`run_in_background: true`): `tools/jobs/batch.sh projects/<name>/work/jobs/<stage>.batch` (toolkit-root path). Jobs run strictly one at a time; the first failure or timeout stops the batch.
3. **Don't poll.** You are notified when it ends. Then read `vt-python tools/job_report.py <status>` per job and verify outputs (ffprobe streams and duration, size). Read a `.log` only on a failure or an odd number (duration off by > 1 frame, wrong fps/resolution, loudness outside House numbers, tiny file).
4. Change settings only for a diagnosed reason. Installs are global.

`tools/jobs/run.sh` writes each `<NN>-<job>.log` and, only when the job ends, its `.status`. `batch.sh` clears old results and won't start beside another batch in the same folder.

## Gotchas
- Never stop jobs with `pkill -f <pattern>`: it matches your own shell and other sessions' identical scripts. `pgrep -f`, check `readlink /proc/<pid>/cwd`, kill only this project's PIDs.
- A delegated "verified SVG" can be a docs-template placeholder (grep `docusaurus|mintlify|<text`, view a still); use the product's README or brand-folder logo, not a GitHub avatar.
- Non-interactive Copilot can't write outside its cwd: launch icon tasks from the toolkit root, and grep a stalled run's log for `Denied`.
