# Escalation dossier (Sonnet → Opus)

When routine Sonnet work fails twice with different approaches, or a decision is high-impact and ambiguous, escalate with a **compact dossier** (≤ ~2,000 words). Do not forward full chat history.

## Template

```markdown
## Escalation
**Problem:** (one paragraph)
**Impact if wrong:** (video quality / stage / deliverable)
**Constraints:** (brand.md, gates, GPU, deadlines)
**Files:** (exact paths only)
**Errors:** (verbatim excerpts, ≤ 20 lines each)
**Attempted:**
1. … → result …
2. … → result …
**Expected:** (what should happen)
**Options:** A … / B … (if any)
**Decision needed:** (one sentence)
```

Opus returns diagnosis, decision, or implementation spec. Sonnet implements unless I override.

Fable tier: only per `config/model-routing.json` escalation policy after Opus is exhausted or on explicit request.