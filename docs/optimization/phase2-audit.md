# Phase 2 audit checklist

**Base:** `main` @ `2de339a` (after PR #1). Branch: `token-diet-phase2`.

| Requirement | Status before phase 2 | Action |
|---|---|---|
| Vision QA Opus vs main session | **Conflict** in `video-inspect.md` | Fix docs; enforce `subagents.vision_qa` in config |
| Model IDs in multiple docs | Repeated in README, model-routing.md | Roles in docs; IDs only in `config/model-routing.json` |
| `model_verify.py` | Weak availability check | Config schema + ID match against local hints; `unverified` default |
| Rough-cut approval | **Unsafe inference** in `sync_handoff` | Explicit `**Approval:**` in log; validator uses log |
| `check_stage` | Trusts JSON only | Reconcile log vs state |
| Inspect cache | report.json only | Full artifact bundle + fingerprint + atomic store |
| Validators | Minimal SRT/render | Expand; fix phrase `scene_glob` bug |
| Remotion scaffold | No `layout.tsx`, no Root | Align README + minimal Root |
| Hook tests | None | Temp repo tests |
| `vt_log` | Sum only | Breakdown JSON |
| Asset cache | Missing | `tools/asset_cache.py` for probe/json |
| Adaptive transcribe | Doc only | Benchmark method doc |
| CI | None | GitHub Actions unittest |
| Escalation dossier | Not documented | `pipeline/escalation.md` template |

EOF audit — implementation tracked in commits on `token-diet-phase2`.