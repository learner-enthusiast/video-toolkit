# ImplicitAssertion

**Purpose:** v3/v4 implicit assertions bind extra data into the signature without putting it in the token; plus PASETO's ISO 8601 times.

**Props:** `at`, `out`, `bindAt`, `replayAt`, `failAt`, `claimsAt`, `isoAt`, `rect`.

**Look**
- Tag "v3 + v4".
- Token card (mono) with a dashed "ghost" chip "tenant: acme" connected by a dotted line into the signature seal, not inside the token string; label "signed, not sent".
- Replay: the token slides to a second server "tenant: globex"; seal dims grey, chip "✗ fails" with WarnMark.
- Claims compare: two cards side by side: JWT `"exp": 1762412400` (dim) vs PASETO `"exp": "2026-11-06T10:00:00Z"` (orange), tag "ISO 8601". Mono ≥ 30 px; wrap the PASETO value under the key if needed.

**Motion:** ghost chip fades in at 50% opacity with dashed border marching; replay slides on a spring; compare cards pop with 5-frame stagger. Exit fade.
