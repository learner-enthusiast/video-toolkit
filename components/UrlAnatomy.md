# UrlAnatomy

**Purpose:** take a URL apart on the words that name its parts (scheme, host, port, registrable domain), then bracket what makes an **origin** and what makes a **site**, and compare two URLs row by row.

**Props:** `url` parts `{ scheme, sub, domain, tld, port }`, `lights` (`{ part, at }[]`: scheme | host | port | registrable), `brackets` (`{ kind: "origin" | "site", at }[]`), `rows` (`{ a, b, origin, site, at, swapAt? }[]`), `rect`, `at`, `out`.

**Look**
- The URL on one white card line in JetBrains Mono 500, ~46–52 px (the whole `https://alice.vercel.com:443` must fit left of the right 15% zone in 9:16). Unlit parts in near-black; the lit part sits on the orange block with white text; parts already explained stay orange text.
- Each part gets a small Inter Medium label (≥ 30 px, dim) under it when it lights: `scheme`, `host`, `port`, `eTLD+1`.
- Brackets: a 4 px orange line under the covered characters with end ticks, the label in Instrument Serif Italic orange (`Origin`, `Site`). Origin covers scheme + host + port; Site covers scheme + registrable domain only (the subdomain stays dim).
- Compare rows: two mono chips (`alice.vercel.com` vs `vercel.com`) and two verdict tags (`origin`, `site`): same = black text on white, different = orange. No green/red.

**Motion**
- Characters type in once (12–18 frames), then parts light on the exact word timestamps (spring scale 1 → 1.06 → 1 on the block).
- Brackets draw from left to right (eased, 10 frames), label pops after.
- Rows slide up staggered 5 frames; `swapAt` springs the TLD `.com` → `.app` (old text flips up and out, new in, orange), then the `site` tag flips to "different".
- Exit: fade + lift before `out`.

**Gotchas**
- Measure the mono advance (~0.6 em) to place brackets; never guess character offsets in px by eye.
- Domains in the URL are lower case exactly as spoken; never `https://` dimmed here (UrlPill hides it; here it's the point).
