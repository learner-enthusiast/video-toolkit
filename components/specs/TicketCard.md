---
code: components/code/TicketCard/TicketCard.tsx
preview: components/code/TicketCard/preview.png
props: "id, title, meta?, kicker?, at, w?, size?, done? (frame for the DONE stamp)"
variants: "open ticket, small context ticket (scaled + dimmed by the scene), done (stamp)"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# TicketCard

**Purpose:** the task the story is about (a Jira/Linear-style ticket), shown when it is assigned and stamped DONE when the story pays off; a bookend for a video's opening and recap.

**Props:** `id` (mono pill, e.g. FEAT-412), `title`, `meta` (dim line), `kicker` (small caps label, default "Your first ticket"), `at`, `w`, `size` (title px), `done` (frame the DONE stamp lands).

**Look**
- White card, brand border/radius/shadow, a 22 px orange stub on the left edge. Id as a dark mono pill, title Inter 900 near-black, meta Inter 600 warm grey.
- DONE stamp: orange 5 px outline, Inter 900, rotated −8°, on the right half so the title still reads.

**Motion**
- Enters with a spring: rise 30 px and a −2° rotation settling to 0. The stamp pops (scale) on its word.

## Code

Saved: `components/code/TicketCard/TicketCard.tsx` (preview: `preview.png`).
