# 2a-legacy — gap table history

Moved from `SKILL.md` (token diet, 2026-11-20). **The gap table itself is still live and stays in `SKILL.md` → 2a** (it drives every tone preset); only this note moved. In this toolkit the pause lengths in `pipeline/take-selection.md` (and `/reel`) override the table.

### 2a-legacy. Silence gaps between words (TIGHT thresholds)

| Gap | `aggressive` (default) | `balanced` | `sentimental` | `documentary` |
|---|---|---|---|---|
| `< 0.25s` | keep | keep | keep | keep |
| `0.25–1s` | trim to **0.1s** | trim to 0.3s | trim to 0.5s | keep |
| `1–3s` | trim to **0.2s** | trim to 0.8s | trim to 1.5s | trim to 2s |
| `> 3s` | trim to **0.2s** | trim to 0.5s | trim to 1s | trim to 3s |

The aggressive thresholds match the reference video's pacing (median cut 1.13s).
