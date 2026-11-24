---
code: components/code/ChatBubble/ChatBubble.tsx
preview: components/code/ChatBubble/preview.png
props: "role, text, at, typeTo, out, w, size, dark, dim, children, style"
variants: "user · assistant, typed or static, trailing mark slot"
last_used: system-design-of-ai/09-prompt-caching
---
# ChatBubble

**Purpose:** a generic chat UI bubble that types a customer question and later shows the assistant answer.

**Props:** `role` (user | assistant), `text`, `typeFrom`, `typeTo` (word frames), `rect`, `chips`, `out`.

**Look**
- User bubble: near-black fill, white Inter 500 ~38 px, right aligned, 14 px radius with a tail. Assistant: white fill, 2 px border, left aligned, small generic bot icon.
- Blinking caret while typing (frame-based on/off, 15 frames).

**Motion**
- Characters reveal in sync with the spoken words (map each word's frame to its char index), bubble height springs as lines wrap.

**Gotchas**
- No real app UI or brand styling; generic chat only.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/ChatBubble/ChatBubble.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: role, text, at, typeTo, out, w, size, dark, dim, children, style.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
