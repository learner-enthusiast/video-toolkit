---
code: components/code/TerminalCard/TerminalCard.tsx
preview: components/code/TerminalCard/preview.png
props: "w, cmd {text,at,cps}, keys {text,at,note?}, log [{text,at,tone,mark?,label?}], labels, pulse {line,at}, note {line,at,text}, at, out"
variants: "bad/good log lines, key-cap, pulse + note on a line"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# TerminalCard

**Purpose:** "prove it yourself": a two-pane terminal with a command typed in the top pane and the server log in the bottom pane, so viewers can copy a test.

**Props:** `cmd` (`{text, at, cps}`), `keys` (`{text, at}` e.g. "^C"), `log` (`{text, at, tone: 'dim' | 'orange', mark?: 'warn'}` lines), `labels` (pane titles, default "client" / "server log"), `run` (optional run labels per log group), `at`, `out`.

**Look**
- Dark panel (#0D0D0D, brand radius, 2 px border, no shadow on dark) with the window-dot header; two panes split by a thin rule, each with a small dim pane title.
- Command in JetBrains Mono 500 ≥ 28 px, white, prompt "$" orange; typed characters with an orange caret. "^C" lands as an orange key-cap.
- Log lines in JetBrains Mono: dim grey for the bad case (with the orange warning mark), orange for the good case.

**Motion**
- Command types on its words (char budget per frame), the caret blinks on frame parity; key-cap pops; log lines appear on their words with a short slide.

**Sound:** `typing-tick` across typing, `pop` per log line, `tick` on "^C".

**Gotchas**
- Code/command text must match the script exactly; wrap with a trailing "…" rather than shrinking below 28 px.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/TerminalCard/TerminalCard.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`; glyphs (server, user, handset, chip, warning) from `glyphs.tsx`.

- Code props: w, cmd {text,at,cps}, keys {text,at,note?}, log [{text,at,tone,mark?,label?}], labels, pulse {line,at}, note {line,at,text}, at, out.
- First built and rendered in `system-design-of-ai/06-cancellation`.
