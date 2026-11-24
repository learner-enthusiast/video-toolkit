---
code: components/code/BillCard/BillCard.tsx
preview: components/code/BillCard/preview.png
props: "amount, strike, blur (0..1), line, w, logo (icons/logos file), title, tag, totalLabel"
variants: "blurred total (the bill arrives) · struck old → orange new (the bill drops)"
last_used: system-design-of-ai/09-prompt-caching
---
# BillCard

**Purpose:** a provider's usage bill as one card, so a money beat has a concrete object: the bill arrives (amount blurred, then revealed), or the bill drops (old amount struck and dim, new amount orange).

**Props:** `amount` (the big total), `strike` (old amount shown struck above it; the total then turns orange), `blur` (0..1, hides the total until revealed), `line` (mono line item, e.g. what the money paid for), `w`, `logo` (file in `icons/logos/`), `title` (header text), `tag` (small dim pill, e.g. "example"), `totalLabel`.

**Look**
- White card, brand border/radius/shadow; paper header row with logo + title + tag; "TOTAL" small caps label; total Inter 900 72 px; struck amount 44 px dim.

**Motion**
- None inside; enter/exit through the scene wrapper or a parent `popIn`. Animate `blur` from 1 to 0 for the reveal.

**Sound:** `cash`/`soft-pop` on the reveal or the drop, per `pipeline/sound.md`.

**Gotchas**
- Rupee numbers must match `work/facts.md`; tag illustrative numbers ("example").
- Keep amounts ≤ ~10 characters at w 560, or raise `w`.
