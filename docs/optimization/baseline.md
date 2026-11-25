# Token-diet baseline audit

**Date:** 2026-11-25  
**Branch:** `token-diet` @ `9963409` (clean working tree; 2 commits ahead of `origin/token-diet`)  
**Scope:** Phase 0 architecture map before the optimization implementation on this branch.

## Executive summary

The repository is **instruction-driven**: Markdown skills and pipeline docs tell Claude how to produce videos; **deterministic work** runs through `vt-python`, FFmpeg, faster-whisper, Remotion, and per-project copies of heavy scripts (e.g. `video_inspect.py`). A **`token-diet`** pass (Nov 2026) already shrank always-loaded docs (`components/index.md`, skill references, handoff-only `log.md` reads) and added **automated project logging** (`tools/hooks/projlog.py`). This mission adds **central model routing**, **structured project state**, **shared validators**, **compact job reports**, and **inspection caching** without weakening quality gates.

## Repository snapshot

| Item | Value |
|---|---|
| Global rules | `CLAUDE.md` (~14.5 KB auto-loaded every turn) |
| Brand | `brand.md` (~5.8 KB) |
| Stages | `pipeline/stages.md` (~3.8 KB after diet) |
| Token policy | `pipeline/token-budget.md` (measured stage load savings) |
| Components discovery | `components/index.md` (~10.7 KB intent groups); full table `index-full.md` (~46 KB, grep-only) |
| Icons | `icons/icons.md` (~34 KB, grep-only) |
| Python in repo | `tools/clean_audio.py`, `tools/voice_preflight.py`, `tools/hooks/projlog.py`, skill scripts under `.claude/skills/*/scripts/` |
| Tests | `tests/test_clean_audio.py` only (no validator tests yet) |
| `docs/optimization/` | Created by this mission |

## Lifecycle map

```
/new-video → script.md + work/
    → Stage 1 Prep: probe, voice-cleaning gate, Whisper (multi-pass), web captures
    → Stage 2 Cut: take-selection, /cut-video, rough cut → CHECKPOINT OK
    → Stage 3 Compose: storyboard, Remotion in work/remotion/, sound, render
    → Stage 4 Deliver: subs, trailer, QA/video-inspect, thumbnail, social, carousel, save components
```

**Durable outputs:** `projects/<name>/out/`, approved rows in `components/`, `icons/icons.md` updates.  
**Temporary:** almost everything under `projects/<name>/work/`.  
**Authoritative human history:** `projects/<name>/log.md` (hooks write prompt/tokens; Claude writes Changes/Handoff).

## Who does what

| Actor | Role |
|---|---|
| **Primary session (Claude Code)** | Decisions, creative direction, cut approval, QA interpretation, exact heavy-job batches |
| **Copilot → Codex → cursor-agent → Haiku** | Low-stakes file/scaffold work (`pipeline/delegation.md`) |
| **Haiku runner (detached)** | Whisper, renders, encodes, video-inspect; `.status` files |
| **Opus vision subagent** | Final visual QA; main session never loads images (`pipeline/video-inspect.md`) |
| **vt-python / FFmpeg / Remotion** | Transcription, alignment, composition, measurement |
| **Ollama qwen2.5vl** | Scene hints only inside video-inspect (not verdict) |

## Model usage (verified 2026-11-25)

Claude Code **2.1.331** on this machine. Subscription: `claude_pro` (individual).

**Identifiers observed** in `~/.claude.json` session cache (not API catalog):

| Tier | Alias / ID | Notes |
|---|---|---|
| Production default | `claude-sonnet-5-5` | Primary implementation; also `claude-sonnet-5-5[1m]` for long context |
| Creative / QA authority | `claude-opus-5-5` | Vision subagent, creative checkpoints |
| Bounded worker | `claude-haiku-5-5` | Delegation chain terminal, heavy-job runner |
| Optional escalation | `claude-fable-5-2[1m]` | Offered in UI; not routine production |
| CLI | `--model <id>`, `--effort <level>` | `per_turn_effort: true` in client cache |

**Before this mission:** No `pipeline/model-routing.md`; video-inspect hard-codes Opus for vision; delegation says "Haiku" without version IDs; main sessions have historically run on Opus for full videos (user intent: default Sonnet, bounded Opus).

## Token measurement (existing)

- **Hooks:** `UserPromptSubmit` → `log_prompt.sh`; `Stop` → `log_tokens.sh` → `projlog.py` reads `~/.claude/projects/.../<session>.jsonl`, dedupes assistant messages, splits main vs subagent usage.
- **Manual check:** `jq` recipe in `pipeline/project-log.md`.
- **Budget table:** `pipeline/token-budget.md` — Compose/Deliver ~47–49% lower *stage-start* instruction bytes vs pre-diet (reel); saved bytes re-paid every turn in long sessions.
- **Not tracked yet:** escalations between tiers, effort level, per-stage aggregates, render/QA iteration counts (added in `tools/vt_log.py` + `project-state.json`).

## Largest inefficiencies (evidence)

1. **Repeated context on every turn** — anything Read once stays in the session; `CLAUDE.md` always re-sent (~3.2k tokens). Mitigation already: don't re-read it; grep components/icons; latest handoff only.
2. **Per-project script duplication** — `video_inspect.py`, `check_phrases.py`, `align_ctc.py`, `compose_data.sh` re-created per video; no shared toolkit validators (composition.md references project-local phrase check only).
3. **Verbose tool output** — FFmpeg/Whisper logs forwarded to chat; delegation expects `.status` tail but format is ad-hoc text.
4. **No inspection cache** — identical MP4 re-inspected on every QA iteration.
5. **Unstructured state** — new session must grep `log.md`; no machine-readable stage/approvals (handoff text is authoritative but not parsed).
6. **Model over-tiering** — creative and implementation work on same tier when session defaults to Opus; no documented escalation dossier.
7. **Transcription** — multi-pass Whisper + CTC is quality-critical (`pipeline/transcribe.md` gotchas); cannot shorten without benchmark; adaptive path documented separately, not default.

## Deterministic automation already present

- Voice cleaning gate: `tools/clean_audio.py`, `tools/voice_preflight.py`, reports JSON.
- Job wrapper pattern: `work/jobs/run.sh` in delegation.md.
- Token logging: `tools/hooks/projlog.py` (302 lines, file lock on `log.md`).
- Cut/clip/zoom: skill Python scripts (local to skills).

## Instruction duplication (intentional vs redundant)

| Topic | Source of truth | Also appears in |
|---|---|---|
| Quality bar | `CLAUDE.md` | skills, `pipeline/qa.md` (keep safety) |
| Layout HEAD/FULL/SPLIT | `brand.md` | composition, layout-states spec |
| Stage gates | `pipeline/stages.md` | coding-video, reel skills |
| Voice gate | `pipeline/voice-cleaning.md` | transcribe, stages, skills (mandatory repeat) |
| Delegation | `pipeline/delegation.md` | stages.md summary |
| Components workflow | `CLAUDE.md` + `components/index.md` | composition.md |

Deliberate duplication at **safety gates** (voice cleaning, never modify raw) should remain.

## Caching today

- **Prompt cache:** Claude Code usage fields `cache_creation_input_tokens` / `cache_read_input_tokens` logged in `log.md`; no repo-level analyzer until `vt_log.py`.
- **Asset/render cache:** none at toolkit level; Remotion re-renders full compositions.
- **Inspect cache:** none; report always regenerated.

## Backward compatibility

- Existing projects unchanged on disk unless Claude updates `project-state.json` during a new stage.
- `index.md` + `index-full.md` split preserved; no mandatory index file split into `indexes/` (intent groups already in `index.md`).
- Hindi/multilingual: not in scope; schema leaves `master_language: "en"` for future use.

## What this mission adds (pointer)

See `pipeline/model-routing.md`, `config/model-routing.json`, `tools/validate/`, `tools/project_state.py`, `tools/job_report.py`, `tools/inspect_cache.py`, `tools/vt_log.py`, `pipeline/context-handoffs.md`, `templates/remotion-starter/`, `pipeline/transcribe-adaptive.md` (experimental).

Final measured savings: reported in `docs/optimization/final-report.md` after tests; no invented percentages here.