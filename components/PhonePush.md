# PhonePush

**Purpose:** a mid-task approval on your phone (CIBA): the phone buzzes with a push notification, you tap Approve, and a token for that one action flies back to the agent.

**Props:** `title` ("Refund ₹50,000?"), `body` (e.g. "Agent request · order #4821"), `at`, `buzzAt`, `tapAt`, `token` ({label, at}), `out`, `rect`.

**Look**
- A generic phone (near-black 2 px bezel, radius 56, ~460×920), lock-screen style: off-white wallpaper with the notebook grid, a clock in Inter 300 120 px, no real OS chrome or app logos.
- The notification: a white card (brand radius, 2 px border, shadow) with a generic shield line icon, `title` in Inter 800 40 px, `body` in Inter 500 28 px dim, and two buttons: "Deny" (outlined, near-black text) and "Approve" (orange block, white text).
- Token chip: JetBrains Mono 28 px pill on the orange block with a small key icon.

**Motion**
- `at`: the phone slides up 80 px with `pop`.
- `buzzAt`: the notification drops from the top of the screen (spring), the phone shakes ±6 px horizontally for 3 cycles over 12 frames (eased), faint 2 px vibration arcs at both sides fade out.
- `tapAt`: a soft finger-tap circle (orange ring, scale 0.6 → 1.2, fades) on Approve; Approve presses (scale 0.94 → 1) and its label swaps to "Approved ✓"-style text with an orange line tick (no green).
- `token.at`: the chip springs out of the notification and travels along an eased arc out of the phone.
- Exit at `out`: phone slides down 60 px and fades.

**Gotchas**
- Money in the title: use the exact spoken amount and symbol (₹), Inter supports it.
- Not PhoneMockup.md (a shopping app screen); keep the two separate.
