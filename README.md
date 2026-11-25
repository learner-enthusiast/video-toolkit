# video-toolkit

Markdown instructions and shared libraries for producing **coding videos** with Claude Code (and Cursor): long-form **16:9** (over 3:00) and **reels** **9:16 only** (≤ 2:59). Per-video work lives in `projects/<name>/`; this repo holds rules, pipeline docs, reusable Remotion components, and deterministic Python helpers.

Repository: [github.com/learner-enthusiast/video-toolkit](https://github.com/learner-enthusiast/video-toolkit)

## Quick start

1. Open **Claude Code** (or Cursor) in this folder. Production sessions should use **Sonnet** as the default model (`pipeline/model-routing.md`). Run **`/setup`** once per machine (details: `setup.md`, `.claude/skills/setup/SKILL.md`).
2. **`/new-video <name>`** — scaffolds `raw/`, `assets/`, `script.md`, `work/`, `out/`, `log.md`, and `project-state.json`.
3. Drop recordings in `projects/<name>/raw/` and private assets in `assets/`. Public pages go in the script’s **Web captures** list; Claude captures them with Playwright (`pipeline/web-capture.md`).
4. Fill or tighten **`script.md`** (`templates/`, or **`/scriptwriting`**).
5. Run **`/coding-video <name>`** or **`/reel <name>`**. Work happens in **four stages** (one session each). Production **stops at the rough cut** for your OK before Compose.
6. Collect deliverables from **`projects/<name>/out/`** (see [Deliverables](#deliverables)).

## Four stages

| Stage | What happens | Checkpoint |
|-------|----------------|------------|
| **1 · Prep** | Probe footage, **voice-cleaning gate**, Whisper, web captures | Handoff in `log.md` |
| **2 · Cut** | Take selection, `/cut-video`, rough-cut preview | **You approve the rough cut** |
| **3 · Compose** | Storyboard, Remotion, sound, renders | 3 approval stills for big creative changes |
| **4 · Deliver** | Subs, trailer, QA, thumbnail, social, carousel, save components | Final visual QA (Opus vision subagent) |

Details: `pipeline/stages.md`, `CLAUDE.md`. Start each session from **`project-state.json`** and the latest **`### Handoff`** in `log.md` — not the full log (`pipeline/context-handoffs.md`).

## Model routing (token-efficient, quality-preserving)

| Role | Typical model | Used for |
|------|----------------|----------|
| **Production** | Sonnet (`claude-sonnet-5-5`) | Implementation, cuts after your OK, Remotion, FFmpeg, most pipeline steps |
| **Creative / QA** | Opus (`claude-opus-5-5`) | Story direction, approval stills, **final** visual QA (vision subagent) |
| **Worker** | Haiku (`claude-haiku-5-5`) | Heavy GPU jobs (exact commands), delegation-chain fallback |

Authoritative IDs and effort defaults: **`config/model-routing.json`**, policy: **`pipeline/model-routing.md`**. After Claude Code upgrades: `vt-python tools/model_verify.py`.

**Scripts before models:** run validators and ffprobe instead of re-reasoning about file shape (`tools/validate/vt_validate.py`, `pipeline/job-results.md`).

## Project memory and logging

| File | Purpose |
|------|---------|
| `projects/<name>/log.md` | Full audit trail (hooks save prompts and token usage; you read handoffs here) |
| `projects/<name>/project-state.json` | Current stage, approvals, artifacts — updated via `tools/project_state.py` |
| `work/prompts/` | Verbatim prompts (hook) |
| `work/logs/hooks.log` | Hook errors |

- Per-turn tokens are appended automatically (`.claude/settings.json` → `tools/hooks/projlog.py`).
- Roll-up: `vt-python tools/vt_log.py summary projects/<name>/log.md`.
- Context savings: `pipeline/token-budget.md`, architecture notes: `docs/optimization/baseline.md`.

## Tooling (`vt-python`)

Global venv launcher: `~/bin/vt-python` (see `setup.md`).

| Tool | Use |
|------|-----|
| `tools/project_state.py` | `init`, `show`, `set-stage`, `sync-handoff` |
| `tools/validate/vt_validate.py` | Project layout, stage gates, SRT, render specs |
| `tools/job_report.py` | Compact JSON from `work/jobs/*.status` |
| `tools/inspect_cache.py` | Reuse `report.json` when the MP4 unchanged |
| `tools/scaffold_remotion.py` | `work/remotion` with symlinks to `icons/` and `components/code/` |
| `tools/clean_audio.py` / `voice_preflight.py` | Voice-cleaning gate (required before Whisper on talking-head audio) |
| `tools/vt_log.py` | Sum token lines from `log.md` |

Tests: `python3 -m unittest tests.test_clean_audio tests.test_project_state tests.test_validate`

## Repository layout

```
CLAUDE.md              Standing rules (auto-loaded in Claude Code; do not re-read in session)
brand.md               Visual system (fonts, captions, HEAD / FULL / SPLIT)
SKILLS.md              Vendored skills and local changes
setup.md               Machine setup (GPU, Whisper, inspect stack, DeepFilterNet)

config/                model-routing.json
docs/optimization/     Baseline audit and engineering report
pipeline/              Stage workflows (transcribe, composition, QA, delegation, …)
templates/             Script and editing prompt templates; remotion-starter notes
series/                Playlist rules (e.g. system-design-of-ai.md)

icons/                 Shared logos (grep icons/icons.md; never read whole file)
components/
  index.md             Intent groups (read first; ✓ = saved code)
  index-full.md        Full table — grep rows only
  specs/               Per-component specs
  code/                Approved Remotion source (symlinked into each project)

.claude/skills/        /new-video, /coding-video, /reel, /cut-video, …
tools/                 Hooks, validators, audio cleaner, scaffolding
projects/              Per-video folders (gitignored)
```

**Components:** find by intent in `components/index.md`; row details: `grep -i '^| \[<Name>\]' components/index-full.md`; open only specs you need.

**Icons:** `grep -i '<brand>' icons/icons.md`; official downloads go in `icons/logos/` with a row in `icons/icons.md`.

## Layout and creative direction

Every beat is **HEAD** (face fills frame), **FULL** (graphic full frame), or **SPLIT** (graphic on top, face below). Script cues `[mm:ss–mm:ss | STATE]` are the plan; Claude may improve visuals within `CLAUDE.md` (never change spoken lines, facts on screen, or `brand.md`).

## Playlists

Videos can belong to a series. Run `/new-video <topic>` and answer "Which playlist? (or none)". Episodes: `projects/<playlist>/<NN>-<topic>/` (gitignored) with rules in `series/<playlist>.md`. Example: **System Design of AI** (`series/system-design-of-ai.md`).

## Deliverables

**Reels (≤ 2:59):** 9:16 only — main MP4, one trailer (9:16), SRTs, thumbnail kit, `<name>_social.json`, `out/carousel/`, and `out/text-posts/` (`CLAUDE.md` Deliverables).

**Long-form (> 3:00):** 16:9 main, 16:9 + 9:16 trailer, thumbnails, social JSON, text posts as applicable.

Extras on older projects: `/carousel <name>`, `/text-posts <name>`.

## Delegation and GPU

- **Low-stakes** work (scaffolding, ffprobe, SRT wrap): CLI chain Copilot → Codex → cursor-agent → Haiku (`pipeline/delegation.md`).
- **Heavy jobs** (Whisper, renders, encodes, video-inspect): Haiku runner with exact commands, `gpu-run`, `work/jobs/run.sh`, `.status` files.
- **Never** silent CPU fallback for GPU work (`pipeline/gpu.md`).

## Inspection and QA

Video-inspect produces compact `report.json` and contact sheets (`pipeline/video-inspect.md`). The **main session reads text**; **Opus vision subagent** judges sheets. Cache unchanged outputs: `tools/inspect_cache.py`. Final QA checklist: `pipeline/qa.md`.

## What this repo is not

- Not a monorepo of finished videos (`projects/` is local/gitignored).
- Not a Hindi/multilingual pipeline yet (English production only; schema leaves room for later).
- Instructions win over skill defaults; `brand.md` wins over instructions where layout and look are defined (`pipeline/instruction-hierarchy.md`).

## Further reading

| Topic | File |
|-------|------|
| Token / context diet | `pipeline/token-budget.md` |
| Optimization mission report | `docs/optimization/final-report.md` |
| Adaptive transcription (experimental) | `pipeline/transcribe-adaptive.md` |
| Voice gate | `pipeline/voice-cleaning.md` |