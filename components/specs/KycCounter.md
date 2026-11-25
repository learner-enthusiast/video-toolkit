---
code: components/code/KycCounter/KycCounter.tsx
preview: components/code/KycCounter/preview.png
props: "mode (every/shared), visits, docs[], payLabel, desk, deskSub, sharedLabel, sharedDone, users, visitLabel(n), everyNote, sharedNote"
variants: "every · shared"
last_used: system-design-of-ai/09-prompt-caching
---
# KycCounter

**Purpose:** the bank-KYC analogy for prompt caching. `every`: each visit the customer slides the full KYC pile (ID, Address, Photo, Form) across the counter for one small cheque. `shared`: User A's pile goes into one shared file at the counter; User B hands over only a cheque and uses the shared file.

**Props:** `mode` ('every' | 'shared'), `visits` (frames of each visit; spoken-word frames).

**Look**
- 900×760 group: near-black counter bar, white "BANK counter" card with an orange-outlined "shared file" folder in `shared` mode, generic UserGlyph customer (no faces), white doc tiles (≥ 28 px labels), orange-outlined cheque tile.
- Caption line: dim "full KYC again, for one cheque" (`every`), orange "→ uses the shared file" (`shared`, visit 2).

**Motion**
- Each visit: pile and cheque slide in (ease-in-out, 16 frames); in `shared` the pile flies into the folder (scale down, fade) 18 frames after visit 1, folder shows "KYC ✓".

**Sound:** `pop` per visit; `soft-pop` when the pile lands in the shared file.

**Gotchas**
- The second appearance (`shared`) must use the same counter as the first (`every`) so the analogy reads as a state change.
- Generic glyphs only (series rule: no avatars).
- The pile fans upward (−90 px overlap, +46 px per card) with labels on each tile's bottom band; a flat row of four tiles ran into the BANK box.
