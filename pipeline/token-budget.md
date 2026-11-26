# Token budget

**Why:** Claude Code re-sends the whole context every turn, so a file read at turn 1 is paid again on every later turn, and model-written boilerplate costs output tokens. Keep always-read files small and let hooks write the log boilerplate.

**Two kinds of numbers:**

1. **Estimated context savings** (below): `bytes / 4` on always-read files — useful for scoping, **not** measured production spend.
2. **Measured usage:** hook `**Tokens:**` lines + `vt-python tools/vt_log.py summary|compare` (`docs/optimization/benchmark-protocol.md`).

## Rules that keep it small
- `CLAUDE.md` is auto-loaded: never Read it again. Skills say "read only what the current stage needs".
- Stage start: latest `### Handoff` in `log.md`, not the whole log (`pipeline/stages.md`).
- `components/index.md` for intent + ✓; rows by `grep -i '^| \[<Name>\]' components/index-full.md`. Icons by `grep -i '<brand>' icons/icons.md`. Never read `components/index-full.md` or `icons/icons.md` whole.
- Images only in the Opus vision subagent (`pipeline/video-inspect.md`); the main session reads text.
- Prompt, time and tokens are logged by hooks (`pipeline/project-log.md`). Each turn records **`Stage:`** from `project-state.json` at prompt time. Token footers separate **main** vs **subagent** models (`; models main: … | sub: …`). Aggregate with `vt-python tools/vt_log.py summary projects/<name>/log.md` (`by_stage`, `by_model`, `by_stage_model`).
- Optional skill material lives in `references/`; load it only when that path is used.
- Editing prompts follow `templates/editing-prompt.md`; fixed rules live in `/reel` and `/coding-video`.

## Fixed starting cost per stage (reel, before → after)

Sum of what each stage loads before any work: `CLAUDE.md` (auto; before: also re-read), the prompt (#11 brief 19,288 B → its script + 60-s cut + slim header 10,539 B), `log.md` (before: whole, ~9–12 KB by Compose/Deliver; after: one handoff ~1.3 KB), `brand.md`, `stages.md`, `/reel`, and the stage's own files (Prep: voice-cleaning, probe-and-trim, transcribe, gpu, delegation · Cut: take-selection, `/cut-video`, delegation · Compose: composition, index, layout-states, sound, icons, `/add-zooms`, video-inspect · Deliver: subtitles, trailer, qa, thumbnail, social-copy, carousel ×2, video-inspect, index, icons, project-log). After: index = `index.md` + ~10 grep'd rows (~3 KB), icons = grep hits (~1 KB). Images (contact sheets, keyframes, stills) are not counted; they now stay out of the main session entirely.

| Stage | Before (bytes / ~tokens) | After (bytes / ~tokens) | Saved |
|---|---|---|---|
| Prep | 100,663 / 25,166 | 79,179 / 19,795 | 5,371 tokens (21%) |
| Cut | 124,057 / 31,014 | 88,108 / 22,027 | 8,987 tokens (28%) |
| Compose | 214,664 / 53,666 | 113,063 / 28,266 | 25,400 tokens (47%) |
| Deliver | 207,443 / 51,861 | 104,289 / 26,072 | 25,789 tokens (49%) |

Each saved token is saved again on every later turn of the session. Output tokens saved per turn: the re-typed prompt (up to ~5k for a full brief) and the token `jq` call.

## Per file (before → after)

| File | Before bytes | ~tokens | After bytes | ~tokens | Δ tokens |
|---|---:|---:|---:|---:|---:|
| `.claude/settings.json` | 0 | 0 | 384 | 96 | +96 |
| `.claude/skills/add-zooms/SKILL.md` | 9,119 | 2,279 | 8,882 | 2,220 | -60 |
| `.claude/skills/carousel/SKILL.md` | 2,787 | 696 | 2,853 | 713 | +16 |
| `.claude/skills/clipify/README.md` | 3,880 | 970 | 3,689 | 922 | -48 |
| `.claude/skills/clipify/SKILL.md` | 19,303 | 4,825 | 15,641 | 3,910 | -916 |
| `.claude/skills/clipify/references/action-mode.md` | 0 | 0 | 1,532 | 383 | +383 |
| `.claude/skills/clipify/references/split-screen.md` | 0 | 0 | 960 | 240 | +240 |
| `.claude/skills/clipify/references/time-warp.md` | 0 | 0 | 1,361 | 340 | +340 |
| `.claude/skills/coding-video/SKILL.md` | 6,814 | 1,703 | 8,675 | 2,168 | +465 |
| `.claude/skills/cut-video/README.md` | 6,590 | 1,647 | 6,388 | 1,597 | -51 |
| `.claude/skills/cut-video/SKILL.md` | 36,385 | 9,096 | 23,331 | 5,832 | -3,264 |
| `.claude/skills/cut-video/references/2a-legacy.md` | 0 | 0 | 811 | 202 | +202 |
| `.claude/skills/cut-video/references/benchmark.md` | 0 | 0 | 698 | 174 | +174 |
| `.claude/skills/cut-video/references/manual-editor.md` | 0 | 0 | 3,026 | 756 | +756 |
| `.claude/skills/cut-video/references/upstream-notes.md` | 0 | 0 | 16,577 | 4,144 | +4,144 |
| `.claude/skills/reel/SKILL.md` | 6,324 | 1,581 | 8,364 | 2,091 | +510 |
| `.claude/skills/scriptwriting/SKILL.md` | 11,279 | 2,819 | 10,762 | 2,690 | -130 |
| `.claude/skills/scriptwriting/references/upstream-step0.md` | 0 | 0 | 829 | 207 | +207 |
| `CLAUDE.md` | 12,686 | 3,171 | 12,956 | 3,239 | +67 |
| `README.md` | 2,551 | 637 | 2,635 | 658 | +21 |
| `SKILLS.md` | 7,581 | 1,895 | 8,420 | 2,105 | +209 |
| `brand.md` | 5,703 | 1,425 | 5,768 | 1,442 | +16 |
| `components/code/README.md` | 1,255 | 313 | 1,321 | 330 | +16 |
| `components/index-full.md` | 0 | 0 | 44,758 | 11,189 | +11,189 |
| `components/index.md` | 54,164 | 13,541 | 10,387 | 2,596 | -10,945 |
| `icons/icons.md` | 32,870 | 8,217 | 32,821 | 8,205 | -13 |
| `pipeline/carousel.md` | 2,597 | 649 | 2,668 | 667 | +17 |
| `pipeline/clean-audio.md` | 11,111 | 2,777 | 11,159 | 2,789 | +12 |
| `pipeline/composition.md` | 13,002 | 3,250 | 13,297 | 3,324 | +73 |
| `pipeline/gpu.md` | 4,802 | 1,200 | 4,800 | 1,200 | -1 |
| `pipeline/project-log.md` | 3,397 | 849 | 4,647 | 1,161 | +312 |
| `pipeline/qa.md` | 7,000 | 1,750 | 7,118 | 1,779 | +29 |
| `pipeline/stages.md` | 7,659 | 1,914 | 3,824 | 956 | -959 |
| `pipeline/transcribe.md` | 9,100 | 2,275 | 8,732 | 2,183 | -92 |
| `pipeline/video-inspect.md` | 12,881 | 3,220 | 14,464 | 3,616 | +395 |
| `pipeline/voice-cleaning.md` | 7,176 | 1,794 | 8,957 | 2,239 | +445 |
| `templates/editing-prompt.md` | 0 | 0 | 1,118 | 279 | +279 |
| `tools/hooks/log_prompt.sh` | 0 | 0 | 247 | 61 | +61 |
| `tools/hooks/log_tokens.sh` | 0 | 0 | 464 | 116 | +116 |
| `tools/hooks/projlog.py` | 0 | 0 | 9,926 | 2,481 | +2,481 |
