# TypedKeyGate

**Purpose:** keys are typed and the parser accepts exactly one version + purpose, so algorithm confusion can't happen.

**Props:** `at`, `out`, `typedAt`, `tryAt` (key tries the wrong keyhole), `refuseAt`, `cantAt` (the RS256→HS256 card dims: "can't happen"), `gateAt`, `rejects` ([{label, at}]), `passAt`, `cryptoAt`, `rect`.

**Look**
- Top half: a key tag "v4.public key" (orange) and a lock with keyhole tag "v4.local"; the key bounces back off it, "library refuses" chip (near-black). Small card from AlgAttack "RS256 → HS256" dims grey with an orange WarnMark and "can't happen".
- Bottom half: a gate (two posts + bar) labelled "parser accepts: v4.public"; queue of token chips in mono 34 px: `v2.public`, `v3.public`, `v4.local` each bounce off the gate with a grey ✗ + orange warn mark, `v4.public` passes with an orange ✓ into a "crypto" box behind the gate.

**Motion:** key slides right, hits, springs back (overshoot); rejected chips bounce back and drop to a dim pile (stagger 6 frames); pass chip glides through. Exit fade.

**Gotchas:** "✗" is warm grey, never red. The top half compresses (spring) when the gate opens so both fit in 970 px.
