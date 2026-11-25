# Model routing

**Goal:** use the right model for each decision. Sonnet runs most production work; Opus owns creative direction, hard problems, and final visual QA; Haiku runs bounded, verifiable tasks. Deterministic scripts beat any LLM when the answer is checkable.

**Authority:** `config/model-routing.json` is the only place model IDs are defined. Skills and pipeline docs refer here; they do not hardcode IDs.

## Tiers

| Tier | ID (Nov 2026 on this machine) | Default effort | Use for |
|---|---|---|---|
| Production | `claude-sonnet-5-5` | medium | Implementation, debugging, manifests, FFmpeg batches, normal Remotion, subtitles, social scaffolding, stage handoffs |
| Creative | `claude-opus-5-5` | high | Story direction, novel storyboard choices, architectural forks, approval stills judgment, vision subagent QA |
| Worker | `claude-haiku-5-5` | low | Log summaries, JSON extraction, heavy-job runner, delegation chain last resort |
| Escalation (rare) | `claude-fable-5-2[1m]` | high | Only when Opus escalation failed or I ask; never routine production |

Long context: `claude-sonnet-5-5[1m]` when a single stage needs the full script + timeline without `/compact`.

**Start a production stage** in Sonnet (`claude --model claude-sonnet-5-5`). Cursor sessions should use Composer/Sonnet-class models for the same role unless I explicitly open an Opus session for creative work.

## Haiku must never

Approve creative work, pick final cuts, pass storyboard or visual/audio quality, or sign off a finished video. The primary session (Sonnet or Opus) verifies every worker output.

## Bounded Opus checkpoints

| When | What |
|---|---|
| Compose · storyboard start | Creative take, beat-level concepts, major layout changes |
| Compose · 3 approval stills | Bigger visual departures from script cues |
| Deliver · final QA | Vision subagent on every contact sheet (`pipeline/video-inspect.md`) |

Do **not** spawn Opus for every component tweak, file rename, or validator run.

## Escalation (Sonnet → Opus)

Escalate when **all** apply:

1. At least two materially different fixes were tried and failed, or the issue is novel/ambiguous.
2. Wrong choice would hurt final quality or cross multiple pipeline stages.
3. A compact **escalation dossier** is ready (≤ 2k words): problem, files, errors, attempts, constraints, proposed options — not full chat history.

Opus returns a decision or spec; Sonnet implements unless I ask otherwise.

Optional **Fable** only if Opus could not resolve and the task is architectural/long-horizon (see `config/model-routing.json`).

## Effort

Claude Code supports `--effort low|medium|high` when `per_turn_effort` is enabled. Match effort to task depth (`config/model-routing.json` → `default_by_task_class`). Do not use `high` effort for grep, ffprobe, or running validators.

## Subagents

| Subagent | Model | Notes |
|---|---|---|
| Vision QA | `claude-opus-5-5` | Same policy as `pipeline/video-inspect.md` |
| Restate test | worker + vision | Pre-screen only |
| Heavy jobs | `claude-haiku-5-5` | Exact commands only (`pipeline/delegation.md` §6) |

## Verification

- Routing does **not** replace validators (`tools/validate/vt_validate.py`) or ffprobe/loudness checks.
- A successful render is not QA. Opus pass is not a substitute for measurements.

## Maintenance

After a Claude Code upgrade, run:

```bash
vt-python tools/model_verify.py
```

Update `config/model-routing.json` `verified_at` and IDs if the client reports changes. Log the result in the toolkit `log.md` entry for that maintenance turn.