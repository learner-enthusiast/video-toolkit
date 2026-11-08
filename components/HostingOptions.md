# HostingOptions

**Purpose:** the three ways to host user code (path, subdomain, separate domain) as a stack of option cards, each revealing what the browser isolates.

**Props:** `options` (`{ n, title, url, at, checks: { label, ok, at }[] }[]`), `focus` (`{ n, at }[]`), `verdict` (`{ n, at, kind: "bad" | "good" }[]`), `rect`, `at`, `out`.

**Look**
- Three stacked cards (white, brand border/radius/shadow), each: a big number in Instrument Serif Italic orange, a title in Inter 700 (≥ 44 px), and the example URL as a JetBrains Mono chip with the varying part orange (`/alice`, `alice.`, `.app`).
- Checks: small rows (`cookies`, `localStorage`, `same-site`) with a line icon: shared/readable = warm grey text + orange warning mark; blocked = orange check. No green/red.
- Focused card grows to full width and height share; the others shrink to a single-line header and dim to 45%.
- Verdict `bad`: card dims to warm grey with an orange warning mark; `good`: orange 4 px ring.

**Motion**
- Cards slide up staggered 5 frames, each on the word that names it ("One", "Two", "Three").
- Focus change: one layout spring (heights, opacity) so cards never snap.
- Check rows pop on their words.
- Exit: fade before `out`.

**Gotchas**
- Keep text left of the right 15% zone in 9:16; long URLs shrink to 44 px minimum, never below.
