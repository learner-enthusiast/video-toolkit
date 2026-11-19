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
