# HubSpoke

**Purpose:** one central party exchanging one thing for many (ID-JAG: the company's identity provider swaps your ID token for grants to other apps).

**Props:** `hub` ({label, sub?, at}), `spokes` ([{label, logo?, at}], 3–5), `input` ({label, at}: the chip that arrives at the hub), `swapAt` (input turns into grant chips), `grant` (chip label), `note` ({text, at}), `out`, `rect`.

**Look**
- Hub: a white rounded box (~360×200), 2 px border, label Inter 800 40 px, `sub` dim 28 px, an orange ring when active.
- Spokes: smaller app boxes (~220×120) evenly on an arc below/around the hub (generic app line icons, or LogoTile when the app is named), connected by 2.5 px near-black lines.
- `input`: a JetBrains Mono chip ("ID token") coming in from "You" at the top-left. `grant` chips: orange block chips ("grant").
- `note`: a small dim line ("no consent-screen spam") under the hub; "Still being standardised" may be a dim Tag.

**Motion**
- Hub pops at `hub.at`; spokes pop staggered 4–6 frames, each line drawing from the hub out (10 frames).
- `input.at`: the chip travels to the hub along an eased path and lands with a pulse.
- `swapAt`: the chip flips (rotateY) into a grant chip, then copies travel down each spoke, staggered 5 frames; each spoke box gets a brief orange ring on arrival.
- Exit at `out`: spokes fade staggered 3 frames, then the hub.

**Gotchas**
- Lay spokes from rects (centre-to-edge lines), never at fixed pixels, so changing their count keeps the arc even.
