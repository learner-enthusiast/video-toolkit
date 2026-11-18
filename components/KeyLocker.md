# KeyLocker

**Purpose:** an exact-key cache as a locker: the label is the key; a request opens it only if its key is the same string. Shows why exact keys hit (everyone builds the same key) and why they miss (same question, different letters).

**Props:** `label` (mono key, e.g. `product:101`), `w`, `h`, `glow` (0–1), `logo` (Redis logo in the label strip), children (what's stored: a count, an answer card).
Scene modes: **many → one** (`arrivals`: dots that fly in and light the locker) and **wrong key** (`keyLabel`, `tryAt`, `bounceAt`).

**Look**
- White box, 2 px border, brand radius; a 64 px label strip on top (`#FBFAF7`, 2 px rule) with the mono key; a vertical handle at the right edge.
- Glow: border goes 4 px orange and a soft orange halo (22% opacity, 6 px blur) pulses behind the box; the handle turns orange.
- Wrong key: a key icon with its own mono hash chip (ink) and the question bubble above it; after the bounce, an orange ⚠ over the locker corner and `a91f… ≠ 3c07…` under it.

**Motion**
- Many → one: ~30 dots, staggered 4 frames, each flies 14 frames ease-in-out into the locker and fades; each arrival pulses `glow` 1 → 0 over 10 frames. A hit counter in the locker and a hit-rate pill below count up.
- Wrong key: the key slides in (12 frames), stops at the locker, bounces back (12 frames) with a 6 px shake; ⚠ pops on the bounce word.

**Gotchas**
- Fake hashes are shown truncated with "…" and stay consistent across scenes (the same question always maps to the same chip).
- Keep the stored answer readable inside the locker (≥ 40 px); it is the point of the "it's already sitting there" beat.
