# PublicVerify

**Purpose:** v4.public: the auth service signs with an Ed25519 private key, every other service only verifies.

**Props:** `at`, `out`, `signAt`, `privAt`, `othersAt`, `pubAt`, `readableAt`, `onlyAt` ("Create token" greyed), `rect`.

**Look**
- Tag "v4.public · Ed25519" (mono pill).
- Auth Service card (server icon) holding an orange private key; a token leaves it with an orange signature seal.
- Three service cards (Posts, Orders, Payments) each with a near-black outline key "public key"; two buttons per card: "Verify ✓" (orange) and "Create token" (dim, struck).
- Token payload shown readable in mono with tag "readable, like JWT".

**Motion:** keys copy out to the three services with a 5-frame stagger; Verify lights on the verify word; Create token dims on "only the auth service". Exit fade.
