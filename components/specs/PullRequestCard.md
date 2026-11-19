---
code: components/code/PullRequestCard/PullRequestCard.tsx
preview: components/code/PullRequestCard/preview.png
props: "title, files, add, del, diff, diffAt, tone (plain|risky|dim), dimT, tag, warn {at,text}, w, size; also exports MiniPR, SizeChip"
variants: "tone x3, with/without diff, warn"
last_used: system-design-of-ai/05-model-routing
---
# PullRequestCard

**Purpose:** a GitHub-style pull request card in the brand look, so a code review story can show *what* changed at a glance: title, files touched, size, and (optionally) the diff itself. Used as a feed of boring PRs, as the one risky PR, and side by side to show that size is not risk.

**Props:** `title`, `files` (1–2 paths, mono), `add` / `del` (the `+N −M` size chip), `diff` (optional, 2–4 lines `{op: '-' | '+' | ' ', text}`), `tone` (`plain` | `risky` = orange outline | `dim` = whole card greyed), `tag` (optional chip on the right, e.g. a grey `₹100`), `warn` (optional orange warning mark + short reason, e.g. "no idempotency key"), `w`, `at`, `out`.

**Look**
- White panel, 2 px `#1A1A1A` border, brand radius and shadow. Header row: a small PR glyph (two dots joined by a branch line, near-black line icon, not the GitHub logo) + title in Inter 800. Under it the file path(s) in JetBrains Mono 500, dim grey.
- Size chip: pill with `+N` in orange and `−M` in warm grey `#8A857C`, mono. Never green/red.
- Diff block (optional): mono ≥ 28 px on a 972-wide card. Removed lines: grey text on a light grey band with a `−` gutter. Added lines: near-black text on a pale orange band (`#E4572E` at ~14%) with an orange `+` gutter. No red/green, ever.
- `risky`: 4 px orange outline. `dim`: whole card at warm grey (text `#8A857C`, border `#8A857C`, no shadow).

**Motion**
- Drops in from above with a spring (slight overshoot, 2–3° tilt that settles to 0); in a feed, each card on the word that names it and earlier cards shift down with a spring. Diff lines reveal top to bottom, 4–6 frames apart. The `warn` mark pops after the diff. Tone changes (plain → dim) ease over ~8 frames. Exit: fade + small drop.

**Sound:** `pop` on the card landing; `soft-pop` per card in a feed; `pen-scratch` if a diff line is highlighted.

**Gotchas**
- File paths are long: keep them ≤ 30 chars at 28 px on a 972 card, or show only the file name.
- A diff with long lines must wrap or shorten; never shrink the code below 28 px (`pipeline/composition.md`).
- Keep the card's geometry identical everywhere it recurs so viewers read it as the same object.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.

## Code

Saved: `components/code/PullRequestCard/PullRequestCard.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: title, files, add, del, diff, diffAt, tone (plain|risky|dim), dimT, tag, warn {at,text}, w, size; also exports MiniPR, SizeChip.
- dimT greys the card at a frame ('not this one').
