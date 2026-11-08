# CookieToss

**Purpose:** show cookie tossing: a page on a sibling subdomain sets a cookie for the shared parent domain, and the browser sends it to the victim. Wall mode: the Public Suffix List stops the toss.

**Props:** `mode` (`toss` | `wall`), `tabs` (`{ host, label, at }[]`), `parent` (`{ host, at }`), `script` (`{ code, at }`), `packet` (`{ from, to, at, dur }`), `replaceAt`, `deliver` (`{ to, at }`), `wall` (`{ label, at }`), `bounceAt`, `rect`, `at`, `out`.

**Look**
- Tabs: two simple browser-window cards (white, 2 px border, radius 14, a top bar with three dim dots and the host in JetBrains Mono ~34 px). The victim tab shows a session chip (`session=you`, mono, white on near-black); the attacker tab's host has its subdomain label in orange.
- Parent: a dashed-border box labelled with the parent host in mono (`.vercel.com`), "cookie jar" in dim Inter, holding the session chip.
- Script: a mono code chip (`document.cookie="session=evil; domain=vercel.com"`, ~30 px, wraps to 2 lines) under the attacker tab.
- Packet: an orange rounded cookie chip (`session=evil`) that travels along a curved path with a short dotted trail.
- Wall mode: two site cards (`bob.vercel.app` → `alice.vercel.app`) side by side; the wall is a near-black vertical slab with the label on it (`Public Suffix List`, Inter Medium white) and `vercel.app` on an orange block.

**Motion**
- Tabs pop in on the word that names them (spring), the script chip types in on "a tiny script".
- Packet: eased flight along a quadratic arc over `dur` frames (never linear), lands with a squash spring; on `replaceAt` the old session chip dims to warm grey and slides out, the packet chip springs into its slot.
- `deliver`: the jar's chip copies along a second path to the victim tab; the victim chip flips to the attacker's value with an orange warning mark.
- Wall: rises from below with a spring on `wall.at`; on `bounceAt` the packet hits it, squashes, and bounces back along the arc with one dim trail. A 2 px shake on impact (4 frames).
- Exit: fade before `out`.

**Gotchas**
- "Bad" is dim + orange warning mark; never red/green.
- Keep the packet path inside the card; arcs that leave the card get clipped.
- Hosts must match the narration exactly (`evil.vercel.com`, not `attacker.com`).
