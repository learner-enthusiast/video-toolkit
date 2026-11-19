# TransactionBox

**Purpose:** explain an atomic transaction: two balance changes locked in one box that either both happen or both roll back.

**Props:** `steps` (label, amount, `at`), `title` (e.g. "ALL or NOTHING"), `failAt`, `rollbackAt`, `commitAt` (optional), `rect`, `out`.

**Look**
- Two account rows (e.g. "You −₹500", "Friend +₹500"), each a white card with the name in body font and the amount large in Inter Black.
- A 3 px accent-bordered box with the brand radius wraps both; the `title` sits on an accent block on its top edge.
- A failed step dims to warm grey and gets an accent cross mark; rolled-back amounts show the original balance with a strike-through on the change.

**Motion**
- Steps pop in on their words; the box draws around them (stroke) and its title drops in with a spring.
- `failAt`: the second step shakes once (4 px, 6 frames) and dims; the cross draws in.
- `rollbackAt`: the first step's amount counts back to its original value (ease-in-out) and both rows return to neutral. An optional "rolled back" `Tag`.
- `commitAt` (if used instead): both amounts lock with a small accent tick.
- Exit: fade with a slight lift.

**Gotchas**
- Use the brand's no-red rule: failure is grey + orange mark, never red.
- Show the rupee sign ₹ correctly; check the font has the glyph (Inter does).
