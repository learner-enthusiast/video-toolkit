# Token budget

**Why:** Claude Code re-sends the whole context every turn, so a file read at turn 1 is paid again on every later turn, and model-written boilerplate costs output tokens.

**Two kinds of numbers:**
1. **Estimated context size** (below): `bytes / 4` of fixed repo reads. Useful for scoping, **not** measured spend.
2. **Measured usage:** the hook `**Tokens:**` lines and `vt-python tools/vt_log.py summary|compare` (`docs/optimization/benchmark-protocol.md`).

## Rules that keep it small
- `CLAUDE.md` is auto-loaded: never Read it again. Read only what the current stage needs.
- Stage start uses the SessionStart brief, not the log (`pipeline/stages.md`).
- `components/index.md` for intent + ✓; rows by `grep -i '^| \[<Name>\]' components/index-full.md`. Icons by `grep -i '<brand>' icons/icons.md`. Never read `components/index-full.md` or `icons/icons.md` whole.
- Images only in `vision-qa` (`pipeline/video-inspect.md`); the main session reads text.
- Run tracked tools from `tools/` with a `work/config/` file; read a tool's code only to change it.
- Incident evidence lives in `docs/lessons.md`, which no stage reads; pipeline Gotchas are one-line rules.
- Size budgets are enforced in CI (`tests/test_doc_lint.py`): `CLAUDE.md` 9 KB, `brand.md` 6 KB, the `/reel` and `/coding-video` skills 7 KB each, `components/index.md` 7 KB, each `pipeline/*.md` 10 KB (allow-list with a reason).

## Fixed repo reads per stage (reel)

**Before** = `main` before PR #10 (`3a4738b`). **After** = PR #13. Both use the same files: `CLAUDE.md`, `brand.md`, `pipeline/stages.md` and `/reel` for every stage, plus that stage's docs and skills.

Not counted on either side, because they depend on the video: the prompt, the handoff or session brief (≤ 4 KB), grep rows, component specs, tool output and images. `pipeline/job-results.md` (about 2 KB) is also left out: it is read when writing a tool config.

| Stage | Before bytes (~tokens) | After bytes (~tokens) | Change |
|---|---:|---:|---:|
| Prep | 72,045 (18,011) | 48,256 (12,064) | -23,789 B (-33%) |
| Cut | 81,815 (20,454) | 59,575 (14,894) | -22,240 B (-27%) |
| Compose | 101,670 (25,418) | 72,173 (18,043) | -29,497 B (-29%) |
| Deliver | 95,733 (23,933) | 69,218 (17,304) | -26,515 B (-28%) |

Each saved token is saved again on every later turn of the session. Not measured here: output tokens no longer spent writing or adapting pipeline scripts on each video (`tools/`), which is likely the larger saving but needs a real benchmark.

## Per file (bytes)

| File | Before | After | Change |
|---|---:|---:|---:|
| `CLAUDE.md` | 15,023 | 9,190 | -5,833 |
| `brand.md` | 5,768 | 5,768 | +0 |
| `pipeline/stages.md` | 4,419 | 4,478 | +59 |
| `.claude/skills/reel/SKILL.md` | 8,914 | 5,126 | -3,788 |
| `pipeline/voice-cleaning.md` | 8,957 | 9,067 | +110 |
| `pipeline/probe-and-trim.md` | 1,332 | 1,332 | +0 |
| `pipeline/transcribe.md` | 8,732 | 4,131 | -4,601 |
| `pipeline/gpu.md` | 4,800 | 3,020 | -1,780 |
| `pipeline/delegation.md` | 14,100 | 6,144 | -7,956 |
| `pipeline/take-selection.md` | 10,260 | 5,611 | -4,649 |
| `.claude/skills/cut-video/SKILL.md` | 23,331 | 23,258 | -73 |
| `pipeline/composition.md` | 13,379 | 8,727 | -4,652 |
| `components/index.md` | 10,745 | 5,262 | -5,483 |
| `components/specs/layout-states.md` | 5,300 | 5,300 | +0 |
| `pipeline/sound.md` | 13,982 | 9,454 | -4,528 |
| `.claude/skills/add-zooms/SKILL.md` | 8,882 | 8,651 | -231 |
| `pipeline/video-inspect.md` | 15,258 | 10,217 | -5,041 |
| `pipeline/subtitles.md` | 3,941 | 2,539 | -1,402 |
| `pipeline/trailer.md` | 3,266 | 2,421 | -845 |
| `pipeline/qa.md` | 8,019 | 5,098 | -2,921 |
| `pipeline/thumbnail.md` | 6,090 | 4,690 | -1,400 |
| `pipeline/social-copy.md` | 3,124 | 3,124 | +0 |
| `pipeline/carousel.md` | 2,668 | 2,668 | +0 |
| `.claude/skills/carousel/SKILL.md` | 2,853 | 2,827 | -26 |
| `pipeline/project-log.md` | 5,645 | 5,810 | +165 |
| `.claude/skills/coding-video/SKILL.md` | 9,115 | 5,385 | -3,730 |
| `.claude/skills/scriptwriting/SKILL.md` | 10,762 | 10,510 | -252 |
