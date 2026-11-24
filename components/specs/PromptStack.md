---
code: components/code/PromptStack/PromptStack.tsx
preview: components/code/PromptStack/preview.png
props: "w, at, detail, clauseAt, sysAt, toolsAt, detailsAt, qAt, sysLines, toolLines, k3At, k2At, sysLabel, toolsLabel, detailsLabel, sysCount, toolsCount, tools[], clause, q, changesLabel, reorderAt, pulseAt, outlineAt, lockAt, lockLabel, breakAt, stripGlowAt, changesAt, cursor, dim"
variants: "request stack: built, deck, reading cursor, locked, broken at token one, re-ordered static-first (code covers the request-stack variant only; the RAG `parts` variant is spec-only)"
last_used: system-design-of-ai/09-prompt-caching
---
# PromptStack

**Purpose:** a prompt box stacks its parts in order as they are spoken: Instruction → best chunk → chunks 2–5 → Question. Request-stack variant (SDAI #09): one LLM request as blocks (clause strip · system prompt 3,000 · tools 2,000 · user details · question) used as a recurring motif: built, repeated as a deck, scanned by a reading cursor, locked (cached), broken at token one, and re-ordered static-first.

**Props:** `parts` (label, body, tone, `at`), `rect`, `out`. Request-stack variant: `w`, `at`, `detail` (tall blocks with spoken lines), `clauseAt/sysAt/toolsAt/detailsAt/qAt` (block reveal frames), `sysLines/toolLines` ([{text, at}]), `k3At/k2At` (token counters), `q`, `clause`, `reorderAt` (clauses-on-top → static-first), `pulseAt`, `outlineAt`, `lockAt` + `lockLabel` (orange bracket + lock on the static blocks), `breakAt` (⚠ on the top strip, everything below dims), `stripGlowAt`, `changesAt` ("changes" tags), `cursor` (−1 or 0..1 reading progress), `dim`.

**Look**
- One tall prompt card with a header "prompt"; each part a row block. Best chunk orange, other chunks white with grey lines, question near-black.

**Motion**
- Each block drops into the next slot with a spring when spoken; earlier blocks stay. Instruction lines reveal word by word.

**Gotchas**

- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
- The lock badge sits ~80 px outside the card's right edge: leave that room inside the 5% margin. Compact rows are 124 / 100 px (the #09 project copy used 112 / 84 and clipped the tool chips).
