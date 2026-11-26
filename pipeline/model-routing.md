# Model routing

**Goal:** use the right model for each decision. Sonnet runs most production work; Opus owns creative direction, hard problems, and final visual QA; Haiku is the last resort for bounded, verifiable boilerplate. Deterministic scripts beat any LLM when the answer is checkable.

**Authority:** `config/model-routing.json` is the only place **model IDs** and CLI selectors are defined. This file uses **tiers** only. Verify locally: `vt-python tools/model_verify.py`.

## Tiers

| Tier | Default effort | Use for |
|---|---|---|
| **production** | medium | Implementation, debugging, manifests, FFmpeg batches, normal Remotion, subtitles, social scaffolding, stage handoffs |
| **creative** | high | Story direction, novel storyboard choices, architectural forks, approval stills judgment, visual QA |
| **worker** | low | Log summaries, JSON extraction, boilerplate-chain last resort |
| **escalation** (rare) | high | Only when Opus escalation failed or I ask; not routine production |

Long context: use the production tier's `long_context_id` in config when a single stage needs the full script + timeline without `/compact`.

**Start a production stage** on the **production** tier: `.claude/settings.json` sets it as the session model. Cursor: Composer/Sonnet-class unless I open a creative session.

## Haiku must never

Approve creative work, pick final cuts, pass storyboard or visual/audio quality, or sign off a finished video. The primary session (production or creative tier) verifies every worker output.

## Bounded Opus checkpoints

| When | What |
|---|---|
| Compose · storyboard start | `creative-director`: creative take, beat-level concepts, major layout changes |
| Compose · 3 approval stills | `creative-director`: bigger visual departures from script cues |
| Deliver · final QA | `vision-qa` on every contact sheet (`pipeline/video-inspect.md`) |

Do **not** spawn Opus for every component tweak, file rename, or validator run.

## Escalation (production → creative)

See `pipeline/escalation.md`. Escalate when two materially different fixes failed or quality risk is high.

## Effort

Use `--effort` per `config/model-routing.json` → `default_by_task_class`. Do not use `high` effort for grep, ffprobe, or validators.

## Subagents

| Subagent | Tier | Notes |
|---|---|---|
| `vision-qa` (`.claude/agents/`) | **creative** | Never `same_as_main`; read-only tools |
| `creative-director` (`.claude/agents/`) | **creative** | Storyboard and stills review; writes only `work/storyboard.md` |
| Restate test | worker + vision | Pre-screen only |

Heavy jobs use no model: `tools/jobs/batch.sh` runs them (`pipeline/delegation.md` §5).

## Verification

- Routing does **not** replace validators (`tools/validate/vt_validate.py`) or ffprobe/loudness checks.
- A successful render is not QA. Opus pass is not a substitute for measurements.

## Maintenance

After a Claude Code upgrade: `vt-python tools/model_verify.py`. `--validate-only` (CI) also checks that each agent's `model:` and the session model in `.claude/settings.json` match their tiers. Update `verified_at` in config only after reviewing the report.