# Delegation

**Goal:** Opus makes every decision; Haiku runs the commands. Every Opus turn re-reads the whole session, so running `ls`, ffmpeg or a render from the main session is the most expensive way to run it.

**Who does what**
- **Opus:** writes every command, chooses takes, sets every parameter, reads the frames, judges quality, and debugs.
- **Haiku:** runs the exact commands Opus wrote, in order, and reports back. It never chooses takes, never edits or "fixes" a command, never retries with different flags, and never decides whether something looks right.
- Opus may run commands itself only when debugging a failure (see below) or for a single read of a file it must judge, such as `cutlist.md` or a log.

**Batch the handoff**
- One handoff per step, not per command: e.g. "render the rough cut, ffprobe it, measure loudness, build the contact sheets" is one Haiku run.
- Give the commands verbatim in a numbered list, with the working directory and the step name.
- Say what to do on failure: **stop at the first non-zero exit** unless a command is marked `(continue on error)`.

**Handoff template**

```text
Step: <step>   Project: projects/<name>   CWD: projects/<name>/work
Run these commands exactly, in order. Do not change, add, or skip anything.
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

**Haiku's report**
- Exit codes, the key numbers Opus asked for, and every error or warning line **verbatim**: copied, never paraphrased or summarised.
- Full output goes to `work/logs/<step>.log`, never into the reply.
- No opinions ("looks good", "should be fine").

**When something fails or looks off**
- Any non-zero exit, any warning Opus didn't expect, or a number outside spec (duration off by > 1 frame, wrong fps or resolution, LUFS outside target, a file size that's suspiciously small): **Opus reads `work/logs/<step>.log` and debugs directly**, running commands itself as needed.
- Once the cause is fixed, the corrected batch goes back to Haiku.

**Vision** is never delegated for a final judgment. See `pipeline/video-inspect.md`.
- Wrap every long encode or render in a Haiku batch with `timeout <s>` and run it in the foreground. A batch Haiku pushed to the background sat on a hung ffmpeg for an hour before reporting.
- `cursor-agent -p --force` can be refused by Claude Code's auto-mode permission classifier (it runs commands and sends code to an outside service). If it is, try Copilot CLI (`copilot -p "<spec>"`) next (CLAUDE.md order); if that is refused or fails too, write the components yourself from the same specs and tell me. Never work around a refusal (`kafka`, `redis-invalidation`).
- Haiku sometimes sends two numbered commands in one message, so they run in parallel (`rag-pipeline`: the 33-segment plate encode ran beside the voice encode at 0.25x and hit its timeout). Write "run ONE command per message" in every batch with a long encode, and give a 30+ segment 1080x1920 plate encode ≥ 2400 s (it does ~1.7x alone).
- A Haiku runner that polls a `nohup` job can stall between steps (it stopped after the first of three renders on `scion`), and stopping that agent also killed the encode it had just launched. For long render chains, write one chain script and run it detached; check the log for its EXIT markers.
