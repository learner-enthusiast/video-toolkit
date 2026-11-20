---
code: components/code/TokenStream/TokenStream.tsx
preview: components/code/TokenStream/preview.png
props: "w, chips, cutTail, from, to, capAt, cap, payAt, perTok, prefix, labels {header,tokens,pay,wall,never,cap}, at, out"
variants: "hard cap mid-answer"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# TokenStream

**Purpose:** show that an LLM writes (and bills) one token at a time and that `max_tokens` is a hard wall: the run stops exactly at the cap, even inside a word.

**Props:** `w`, `words` (answer text split into token chunks, e.g. ["Morn","ing",":"," take"," the"," ferry"," to"," Ch","apora"]), `from`/`to` (frames over which tokens arrive, eased), `cap` (token count where it stops, e.g. 1000), `capAt` (frame the wall slams), `shownTokens` (how many chunks of `words` represent the last tokens before the cap), `perTok` (₹ per token, illustrative), `prefix` ('₹'), `tokLabel`, `at`, `out`.

**Look**
- White card, 2 px border. Top: answer line built from token chips (white chips, 2 px border, JetBrains Mono 700; the newest chip orange). Middle: two counter boxes side by side (tokens · ₹ paid), Inter 900 numbers, tabular. Right edge: the cap wall, a near-black bar labelled `max_tokens: 1000` that drops in on `capAt`; the chip it cuts is split in two, its right half dim and hatched (never generated).
- No red/green; the cut half is dim grey with an orange ⚠.

**Motion**
- Chips drop in from above one at a time (spring, 4-frame stagger at most visible), counters tick with each chip (ease-out between chips, never linear). Wall: fast spring with a 6 px shake on landing; counters freeze and bump.

**Sound:** `typing-tick` per visible chip, `stamp-thud` (or the `bell` callback) on the wall.

**Gotchas**
- Counters must agree with the script (1,000 at the stop) and `work/facts.md` (₹ rate marked illustrative).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/TokenStream/TokenStream.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: w, chips, cutTail, from, to, capAt, cap, payAt, perTok, prefix, labels {header,tokens,pay,wall,never,cap}, at, out.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
