# video-toolkit

**Markdown instructions and shared libraries for producing coding videos with Claude Code and Cursor.**

Long-form exports are **16:9** (over 3:00). Reels are **9:16 only**, start to finish, with a hard cap of **2:59**. Each video is a self-contained folder under `projects/<name>/` (gitignored on your machine). This repository holds standing rules (`CLAUDE.md`), stage workflows (`pipeline/`), reusable Remotion components (`components/`), official logos (`icons/`), deterministic Python helpers (`tools/`), and agent skills (`.claude/skills/`).

**Repository:** [github.com/learner-enthusiast/video-toolkit](https://github.com/learner-enthusiast/video-toolkit)

---

## Table of contents

1. [Who this is for](#who-this-is-for)
2. [Quick start](#quick-start)
3. [Per-project folder anatomy](#per-project-folder-anatomy)
4. [Four stages and approvals](#four-stages-and-approvals)
5. [Skills (slash commands)](#skills-slash-commands)
6. [Model routing and tiers](#model-routing-and-tiers)
7. [Project memory: log, state, and hooks](#project-memory-log-state-and-hooks)
8. [Python tooling reference](#python-tooling-reference)
9. [Caching, safety, and accounting](#caching-safety-and-accounting)
10. [Shared Remotion libraries](#shared-remotion-libraries)
11. [Pipeline documentation index](#pipeline-documentation-index)
12. [Delegation and heavy jobs](#delegation-and-heavy-jobs)
13. [GPU policy](#gpu-policy)
14. [Inspection and QA](#inspection-and-qa)
15. [Deliverables checklist](#deliverables-checklist)
16. [Playlists and series](#playlists-and-series)
17. [Layout states and creative direction](#layout-states-and-creative-direction)
18. [Machine setup](#machine-setup)
19. [Development, tests, and CI](#development-tests-and-ci)
20. [Instruction hierarchy](#instruction-hierarchy)
21. [Troubleshooting](#troubleshooting)
22. [What this repo is not](#what-this-repo-is-not)
23. [Further reading](#further-reading)

---

## Who this is for

You record talking-head (and screen) takes, write a tight script, and want a **repeatable, agent-driven pipeline** that:

- Never edits your raw camera files in place
- Transcribes with **local Whisper on the GPU**, not a paid API
- Cleans voice with a **fail-closed quality gate** (WPE + DeepFilterNet 3 when available)
- Cuts jumpy takes, adds emphasis zooms, composes motion graphics in **Remotion**
- Delivers platform-ready outputs (main video, trailer, SRT, thumbnail kit, social JSON, carousel, text posts)
- Logs prompts, decisions, and **token usage** per turn for cost and audit

The default orchestration model is **Sonnet**; creative checkpoints and **final visual QA** use the **creative** tier (Opus-class vision). Heavy/ffmpeg/render jobs run under explicit commands with status files—not improvised shell in the main session.

English production only today; schemas leave room for Hindi and other languages later.

---

## Quick start

| Step | Action |
|------|--------|
| 1 | Clone this repo. Open **Claude Code** or **Cursor** with the repo root as the workspace. |
| 2 | Run **`/setup`** once per machine (`setup.md`, `.claude/skills/setup/SKILL.md`). Confirm `vt-python`, GPU offload (`gpu-run nvidia-smi` when NVIDIA is present), and `vt-python tools/model_verify.py --validate-only`. |
| 3 | **`/new-video <name>`** — creates `projects/<name>/` with `raw/`, `assets/`, `script.md`, `work/`, `out/`, `log.md`, `project-state.json`. |
| 4 | Put recordings in `projects/<name>/raw/` and private files in `assets/`. List public URLs in the script’s **Web captures** section; agents capture them with Playwright (`pipeline/web-capture.md`). |
| 5 | Fill **`script.md`** (templates in `templates/`, or **`/scriptwriting`**). |
| 6 | **`/coding-video <name>`** (long-form) or **`/reel <name>`** (9:16). Work proceeds in **four stages** (see below). Production **stops at the rough cut** for your OK before Compose. |
| 7 | Ship from **`projects/<name>/out/`** (and extras under `out/carousel/`, `out/text-posts/`). |

**Do not** build video-specific Remotion code in this repo root. Per-video code lives in `projects/<name>/work/`. Only **approved** components that survived a finished render are promoted into `components/code/`.

---

## Per-project folder anatomy

```
projects/<name>/
├── raw/                 # Camera/screen originals — NEVER modified by the pipeline
├── assets/              # Private inputs you supply (logos, licensed media, logins)
├── script.md            # Spoken lines + visual cues (source of truth for intent)
├── brand.md             # Optional per-video overrides; defaults come from repo brand.md
├── log.md               # Audit trail: prompts, handoffs, token footers, approvals
├── project-state.json   # Stage, artifact paths, approval flags (tools/project_state.py)
├── work/                # All intermediates (copies, transcripts, Remotion, jobs, caches)
│   ├── prompts/         # Verbatim user prompts (hook)
│   ├── logs/            # hooks.log, delegation logs, stage logs
│   ├── transcripts/     # Whisper JSON, SRT sources, word timings
│   ├── remotion/        # npm project; symlinks to repo icons/ and components/code/
│   ├── jobs/            # Job batches + *.log / *.status (tools/jobs/batch.sh)
│   ├── captures/        # Playwright screenshots/clips + captures.md
│   └── cache/           # Asset manifest, inspect cache, operation bundles
└── out/                 # Deliverables only
    ├── *.mp4            # Main, trailer, variants
    ├── *.srt
    ├── thumbnail/
    ├── carousel/        # Reels: script-derived carousel
    └── text-posts/      # LinkedIn hook photo + posts, X article
```

**Authoritative context** for the next session: latest **`### Handoff`** in `log.md` plus `project-state.json` (`pipeline/context-handoffs.md`). On conflict, **`log.md` wins**.

---

## Four stages and approvals

Full policy: `pipeline/stages.md` and `CLAUDE.md`.

| Stage | Primary work | You approve |
|-------|----------------|-------------|
| **1 · Prep** | ffprobe, proxy paths, **voice-cleaning gate**, Whisper, web captures, scaffolding | Implicit via handoff; voice gate is mandatory before ASR on talking-head audio |
| **2 · Cut** | Take selection, `/cut-video`, punch-ins (`/add-zooms`), rough-cut preview | **Rough cut** — no Compose until you OK |
| **3 · Compose** | Storyboard, Remotion scenes, sound map, preview renders | **3 approval stills** when creative direction changes a whole beat or motif |
| **4 · Deliver** | Final render, loudness (`CLAUDE.md` → House numbers), subs, trailer, thumbnail, social, carousel, library save | **Final visual QA** (creative-tier vision subagent on contact sheets) |

Each stage should end in `log.md` with a **`### Handoff`**: decisions, rejected options, open issues, files produced, next steps.

**Quality bar (summary):** hide jump cuts; one light grade; spring/ease motion only; 5% safe margins; captions on word timestamps; no static screenshot > 3s; never cover the presenter’s face; deliver at house loudness with A/V sync spot-checks. Details in `CLAUDE.md` and `brand.md`.

---

## Skills (slash commands)

Skills live under `.claude/skills/`. They route work; they do **not** override `brand.md` or reel/long-form deliverable rules.

| Skill | Role |
|-------|------|
| `/setup` | Machine check: venv, GPU, Whisper, inspect stack, hooks |
| `/new-video` | Scaffold project tree |
| `/scriptwriting` | Tighten `script.md`, hooks, timing |
| `/coding-video` | Long-form pipeline (16:9 + portrait deliverables where applicable) |
| `/reel` | 9:16-only pipeline ≤ 2:59 |
| `/cut-video` | Take selection and tight cut (used by coding-video and reel) |
| `/add-zooms` | Emphasis punch-ins on transcript words |
| `/clipify` | Find clips in a long recording → per-clip `/reel` |
| `/carousel` | Build carousel from `script.md` |
| `/text-posts` | LinkedIn hook image + posts, X article |
| Remotion `/*` skills | Compose, render, captions, upgrade, etc. (`remotion-best-practices` router) |

Vendor provenance and local patches: `SKILLS.md`.

---

## Model routing and tiers

| Tier | Config id (example) | Use |
|------|---------------------|-----|
| **production** | `claude-sonnet-5-5` | Default implementation, cuts after your OK, Remotion, FFmpeg, most pipeline steps |
| **creative** | `claude-opus-5-5` | Story direction, approval stills, **final visual QA** (vision subagent — always creative, never main session) |
| **worker** | `claude-haiku-5-5` | Last resort of the boilerplate chain |
| **escalation** | (configured) | Rare escalation path (`pipeline/escalation.md`) |

- **Single source of truth for model IDs:** `config/model-routing.json`
- **Policy:** `pipeline/model-routing.md`
- **Verify CLI vs config:** `vt-python tools/model_verify.py` (add `--validate-only` in CI)

**Scripts before models:** run `vt-python tools/validate/vt_validate.py`, ffprobe, and read `.status` / `report.json` on disk instead of re-deriving file shapes in chat (`pipeline/job-results.md`).

---

## Project memory: log, state, and hooks

### Files

| Location | Purpose |
|----------|---------|
| `projects/<name>/log.md` | Human-readable audit: section headers, prompts, Finished/Took/Tokens footers, handoffs |
| `projects/<name>/project-state.json` | Machine-readable stage and artifact registry |
| `work/prompts/*.md` | Full prompt text per turn (written by hook) |
| `.hook-state/<session>.json` | Ephemeral turn state between UserPromptSubmit and Stop |
| `.hook-state/checkpoints/<session>.json` | Incremental transcript scan checkpoints |
| `work/logs/hooks.log` | Hook errors (per-project or repo `.hook-state`) |

### Claude Code hooks

Configured in `.claude/settings.json`:

| Event | Script | Behavior |
|-------|--------|----------|
| **UserPromptSubmit** | `tools/hooks/projlog.py prompt` | Resolves `projects/…` mention, writes log header + saves prompt |
| **Stop** | `tools/hooks/projlog.py tokens` | Scans session transcript(s), appends **Finished / Took / Tokens** under the matching entry |

Hook contract (`pipeline/project-log.md`):

- Reads hook JSON from **stdin**; never prints to stdout (would pollute the chat); exits **0** even on failure (errors go to `hooks.log`).
- **Lock order:** session checkpoint lock **before** `log.md` project lock when both are needed.
- **Idempotency:** each turn has a stable key (`started_utc` + `prompt_ref`). Duplicate or concurrent Stop hooks must not replace a committed token footer with empty totals.
- **Deduplication:** message IDs are tracked in a **session-level** ledger so the same assistant message is not counted twice across parent transcript, sidechain rows, and subagent JSONL files—or across separate Stop invocations.
- **Incremental scans:** JSONL checkpoints store file identity, byte offset, boundary fingerprint, and content hash of processed prefix; invalid checkpoints trigger full rescan without crashing the hook.

Token roll-up for humans:

```bash
vt-python tools/vt_log.py summary projects/<name>/log.md
```

Context diet notes: `pipeline/token-budget.md`, `docs/optimization/baseline.md`.

---

## Python tooling reference

Launcher: **`vt-python`** → `~/video-toolkit/venv` (see `setup.md`). From repo root you can also use `python3` if dependencies match CI.

| Tool | Purpose |
|------|---------|
| `tools/project_state.py` | `init`, `show`, `set-stage`, `record-approval`, `sync-handoff` |
| `tools/validate/vt_validate.py` | Layout, stage gates, SRT, render specs, loudness expectations |
| `tools/project_log_lock.py` | Exclusive lock for `log.md` (shared with hooks and approvals) |
| `tools/hooks/projlog.py` | Prompt + token hooks |
| `tools/hooks/transcript_ckpt.py` | Incremental transcript accounting |
| `tools/vt_log.py` | Parse and sum token footers; compare runs |
| `tools/job_report.py` | Compact JSON from `work/jobs/<NN>-*.status` |
| `tools/inspect_cache.py` | Reuse video-inspect `report.json` when source MP4 unchanged (final QA **refuses** cache) |
| `tools/asset_cache.py` | Content-addressed cache for probes and deterministic preprocess (`store`, `lookup`, `ffprobe`) |
| `tools/path_safety.py` | JSON load helpers, bundle path resolution, symlink guards |
| `tools/scaffold_remotion.py` | Create `work/remotion` with symlinks to shared libraries |
| `tools/clean_audio.py` | Quality-mode voice cleaning (WPE + DeepFilterNet path) |
| `tools/voice_preflight.py` | Quick readiness check for cleaners |
| `tools/model_verify.py` | Validate `config/model-routing.json` against CLI hints |
| `tools/routing_config.py` | Load routing config for tools and tests |

**Audio:** Production talking-head path requires passing `pipeline/voice-cleaning.md` before Whisper. Alternate modes exist for experiments but **do not** pass the automated gate without explicit approval.

---

## Caching, safety, and accounting

Three complementary systems reduce redundant I/O and token-heavy re-analysis:

| System | Location | Invariant |
|--------|----------|-----------|
| **Transcript checkpoints** | `.hook-state/checkpoints/` | Incremental token scan matches full-scan totals; corrupt schema → rescan, no silent trust |
| **Inspect cache** | `work/inspect/.cache/` | Reuse reports when fingerprint matches; **no** reuse for final thorough QA |
| **Asset cache** | `work/cache/asset-manifest.json` | ffprobe and deterministic ops keyed by input hash + identity; refuses stale results if input changed during probe |

Manifest corruption quarantines to `*.corrupt` when recovery succeeds; failed quarantine aborts the store without clobbering the original manifest (`tools/asset_cache.py`).

---

## Shared Remotion libraries

### Components (`components/`)

**Read order (token-efficient):**

1. Repo `brand.md`
2. `components/index.md` — intent groups; **✓** means saved code exists
3. `grep -i '^| \[<Name>\]' components/index-full.md` — one row at a time
4. `components/specs/<Name>.md` only for scenes you are building

**Compose rule:** if `index.md` marks a component ✓, import from `shared/<Name>/<Name>` inside the project (`src/shared` → symlink to `components/code/`). Extend via props before writing new components. After a successful final render, promote cleaned code back to `components/code/` with `preview.png` and update index rows in the **same commit**.

### Icons (`icons/`)

- **Never** read `icons/icons.md` whole — `grep -i '<brand>' icons/icons.md`
- Reuse `icons/logos/` or `icons/ui/` when listed; otherwise download **official** assets, add license + date row, update **Used in**
- Remotion: `staticFile('icons/logos/<file>')` via `public/icons` symlink

---

## Pipeline documentation index

| Topic | File |
|-------|------|
| Stages and handoffs | `pipeline/stages.md`, `pipeline/context-handoffs.md` |
| Project log & hooks | `pipeline/project-log.md` |
| Transcription | `pipeline/transcribe.md`, `pipeline/transcribe-adaptive.md` (experimental) |
| Voice cleaning | `pipeline/voice-cleaning.md`, `pipeline/clean-audio.md` |
| Take selection & cut | `pipeline/take-selection.md`, skill `/cut-video` |
| Composition | `pipeline/composition.md` |
| Sound & SFX | `pipeline/sound.md` |
| Subtitles | `pipeline/subtitles.md` |
| Render & loudness | `pipeline/render.md` |
| Trailer | `pipeline/trailer.md` |
| Thumbnail | `pipeline/thumbnail.md` |
| Social copy | `pipeline/social-copy.md` |
| Carousel | `pipeline/carousel.md` |
| Text posts | `pipeline/text-posts.md` |
| Web capture | `pipeline/web-capture.md` |
| Video inspect | `pipeline/video-inspect.md` |
| QA | `pipeline/qa.md` |
| Delegation | `pipeline/delegation.md` |
| Heavy jobs | `pipeline/job-results.md` |
| GPU | `pipeline/gpu.md` |
| Model routing | `pipeline/model-routing.md` |
| Token budget | `pipeline/token-budget.md` |
| Instruction priority | `pipeline/instruction-hierarchy.md` |
| Probe / trim | `pipeline/probe-and-trim.md` |

Standing rules that apply to every video: **`CLAUDE.md`** (auto-loaded in Claude Code).

---

## Delegation and heavy jobs

Single deterministic commands are run directly. Only multi-file boilerplate from a final spec goes through **Copilot → Codex → cursor-agent → Haiku**, with timeouts and logs in `work/delegation/`; the orchestrator verifies every result.

**Heavy jobs** (final renders, Whisper, encodes, video-inspect) never use that chain. The main agent writes an exact batch; `tools/jobs/batch.sh` runs it one job at a time, writes `work/jobs/<NN>-<job>.status` and stops at the first failure. Pipeline scripts live in `tools/` and read per-video settings from `work/config/`.

**Never delegate:** script, storyboard, creative take, layout states, sound map, `brand.md`, final component visuals, render settings, final QA, or anything on screen not yet reviewed.

Details: `pipeline/delegation.md`.

---

## GPU policy

When `nvidia-smi` exists, use **`~/bin/gpu-run`** so offloaded rendering and CUDA tools see the discrete GPU (`pipeline/gpu.md`).

- Encode with **`h264_nvenc`** when FFmpeg lists it
- **Never** fall back to CPU silently for GPU work—fix the environment or stop and report
- Exception: if the GPU is busy with another heavy job, small CPU side work (stills, thumbnails, rembg) is allowed; **main** renders, transcription, and final encodes stay on GPU

Whisper and video-inspect OCR branches expect CUDA on production machines.

---

## Inspection and QA

1. Run **video-inspect** (heavy job) per `pipeline/video-inspect.md`
2. Read `report.json` (`summary`, `flags` first)
3. **Creative-tier vision subagent** judges contact sheets and flagged frames; main session reads **text**, not raw frame dumps
4. Use `--thorough` before publish
5. Propose fixes with timestamps

Cache: `vt-python tools/inspect_cache.py` for unchanged intermediates. **Final QA cache reuse is forbidden.**

---

## Deliverables checklist

### Reels (≤ 2:59) — 9:16 only

| Deliverable | Location / notes |
|-------------|------------------|
| Main video | `out/*.mp4` 1080×1920 |
| One trailer | 9:16 (prompt-defined short cut or `pipeline/trailer.md` default) |
| SRTs | Main + trailer |
| Thumbnail kit | `out/thumbnail/` + ChatGPT kit (`pipeline/thumbnail.md`) |
| Social JSON | `<name>_social.json` (`pipeline/social-copy.md`) |
| Carousel | `out/carousel/` (`/carousel` or automatic in Deliver) |
| Text posts | `out/text-posts/` (extras; video posts still use social JSON captions) |

No 16:9 reel renders.

### Long-form (> 3:00)

| Deliverable | Notes |
|-------------|--------|
| Main 16:9 | Primary export |
| Trailer 16:9 + 9:16 | Exactly one trailer cut each orientation |
| SRTs, thumbnails, social JSON, text posts | As for reels where applicable |
| 9:16 cut | Per legacy long-form rules in `CLAUDE.md` |

**X Premium:** video caption ≤ 280 chars plus `post_long`; text post and article may exceed 280 (`pipeline/text-posts.md`).

---

## Playlists and series

Episodes can live under `projects/<playlist>/<NN>-<topic>/` with extra rules in `series/<playlist>.md`.

Example: **System Design of AI** → `series/system-design-of-ai.md`.

When running `/new-video`, answer the playlist prompt or choose none.

---

## Layout states and creative direction

Every beat uses a layout state from `brand.md`:

- **HEAD** — face fills frame  
- **FULL** — graphic full frame  
- **SPLIT** — graphic on top, face below  

Script cues `[mm:ss–mm:ss | STATE]` set intent. Agents may improve **how** a cue is shown (motion, reveal order, metaphor) but **must not** change spoken lines, on-screen facts/code, `brand.md`, the 2:59 reel cap, or the pedagogical intent of a cue.

Priority: `brand.md` → hard rules → script cue intent → agent creative take → skill defaults (`pipeline/instruction-hierarchy.md`).

---

## Machine setup

**Preferred:** `/setup` in Claude Code.

**Manual:** `setup.md` covers:

- Shared venv `~/video-toolkit/venv` and `~/bin/vt-python`
- Isolated DeepFilterNet 3 venv and `~/bin/deep-filter`
- FFmpeg, Whisper (faster-whisper, CUDA), inspect stack (PySceneDetect, PaddleOCR venv, MediaPipe, Ollama VLM)
- Playwright + Chromium in `~/.cache/ms-playwright`
- Optional `img2pdf` for carousel PDFs

Voice cleaner rebuild pins: `tools/deepfilternet.lock.txt`.

---

## Development, tests, and CI

### Run tests locally

```bash
python3 -m compileall -q tools tests
python3 tools/model_verify.py --validate-only
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Representative modules: `test_validate`, `test_clean_audio`, `test_projlog_stop`, `test_transcript_dedup`, `test_asset_cache`, `test_hook_concurrency`, `test_inspect_cache`, `test_parent_sidechain_accounting`.

Some tests skip when `ffmpeg` or optional ML stacks are absent (`test_loudnorm_integration`).

### Continuous integration

GitHub Actions workflow **`.github/workflows/ci.yml`** on push/PR:

1. Install FFmpeg + Python 3.12 venv from `.github/workflows/ci-requirements.txt`
2. `compileall` on `tools/` and `tests/`
3. `model_verify.py --validate-only`
4. Full `unittest` discover

Branch protection notes: `.github/BRANCH_PROTECTION.md`.

### Optimization docs

Engineering audits and benchmark protocol: `docs/optimization/` (baseline, phase reports, benchmark-protocol.md, post-hardening-status.md).

---

## Instruction hierarchy

When instructions conflict:

1. **`CLAUDE.md`** and project/repo **`brand.md`**
2. **Hard rules** (never modify `raw/`, never cut spoken lines, reel length, deliverable formats)
3. **Script cue intent**
4. **Agent creative take** (within rules)
5. **Skill defaults** (lowest)

Skills decide **how** to execute a step, not how the video **looks** unless `brand.md` leaves a choice open.

---

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Hook did not write tokens | `work/logs/hooks.log`; session transcript path in Stop payload; `PROJLOG_INCREMENTAL=0` for forced full scan |
| Tokens show “not available” but subagents ran | Ensure sidechain/subagent rows exist after `started_utc`; upgrade to build with session dedup + sidechain footer fix |
| `vt-python` not found | `setup.md` — venv and `~/bin` on `PATH` |
| Whisper fails / no CUDA | `gpu-run nvidia-smi`; torch `cuda.is_available()` inside venv |
| Voice gate blocks Prep | `vt-python tools/voice_preflight.py`; DeepFilterNet lock file and WPE deps |
| Validate fails stage gate | `vt-python tools/validate/vt_validate.py projects/<name>` — fix listed artifacts before advancing stage |
| Inspect cache miss | Input fingerprint changed; for final QA, miss is **expected** |
| Remotion cannot find icons | `public/icons` symlink in project `work/remotion` |
| Double token counts | Stale checkpoint — delete `.hook-state/checkpoints/<session>.json` once; file bug reports go to toolkit issues |

---

## What this repo is not

- **Not** a catalog of finished videos (`projects/` is local and gitignored).
- **Not** a hosted render farm or CI that builds your MP4s on push.
- **Not** a multilingual/Hindi production pipeline yet (English defaults).
- **Not** a place to commit per-video Remotion sources (only shared library promotions).
- Instructions and `brand.md` **beat** vendored skill aesthetics and generic Remotion tutorials.

---

## Further reading

| Topic | File |
|-------|------|
| Standing rules (full) | `CLAUDE.md` |
| Visual system | `brand.md` |
| Install & tool versions | `setup.md` |
| Skill sources | `SKILLS.md` |
| Token / context diet | `pipeline/token-budget.md` |
| Optimization report | `docs/optimization/final-report.md` |
| Voice gate | `pipeline/voice-cleaning.md` |
| Adaptive transcription (experimental) | `pipeline/transcribe-adaptive.md` |

---

*Maintained for the learner-enthusiast video toolchain. Issues and PRs welcome on GitHub; keep changes scoped—accounting fixes do not relax editorial or QA standards.*