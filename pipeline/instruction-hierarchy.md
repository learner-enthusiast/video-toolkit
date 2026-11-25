# Instruction hierarchy

When instructions conflict, resolve in this order:

1. **`brand.md`** — visual system, fonts, captions, layout states  
2. **Hard rules in `CLAUDE.md`** — never cut lines, never modify `raw/`, GPU policy, deliverables, voice gate  
3. **Series rules** — `series/<playlist>.md` when the project is in a playlist  
4. **`pipeline/stages.md`** — stage order and checkpoints  
5. **Stage pipeline docs** — e.g. `voice-cleaning.md`, `transcribe.md`, `composition.md`  
6. **`pipeline/model-routing.md`** — model tier and checkpoints  
7. **Skills** — `/reel`, `/coding-video`, etc. (Linux adaptations + pointers to pipeline)  
8. **Component specs** — only for components used in the current storyboard  
9. **Skill defaults** — lowest; never override brand or quality bar  

**Safety duplicates kept on purpose:** voice-cleaning gate text appears in `stages.md`, `transcribe.md`, and skills so it cannot be skipped by reading one file only.

**Components:** intent discovery = `components/index.md`; row details = grep `index-full.md`; behaviour = `components/specs/<Name>.md`; code = `components/code/<Name>/`.

**Tokens:** context policy = `pipeline/token-budget.md` + `pipeline/context-handoffs.md`.