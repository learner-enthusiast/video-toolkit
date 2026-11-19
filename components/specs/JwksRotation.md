# JwksRotation

**Purpose:** asymmetric signing for microservices: the auth service signs with a private key, services fetch public keys from a JWKS endpoint, `kid` picks the key, and keys rotate without logging anyone out.

**Props:** `authAt`, `servicesAt` ([Posts, Orders, Payments]), `jwksAt`, `fetchAt`, `kidAt`, `rotateAt`, `rect`, `out`.

**Look**
- Top: "Auth service" card holding an orange private key icon; RS256 / ES256 chips.
- Middle: a box labelled `/.well-known/jwks.json` (mono ≥ 30 px) holding key chips `kid: k1`, `kid: k2` (white, near-black border, public key icon).
- Bottom: three service cards (Posts, Orders, Payments) in one row.
- A token chip with header `"kid":"k2"`; an orange arrow from it to the `k2` chip, which gets an orange ring.

**Motion**
- Cards pop on their words; dotted fetch lines draw from each service up to the JWKS box, with small key packets travelling down.
- Rotation: `k3` slides in from the right (spring), `k1` fades and slides out left; a small "users stay logged in" tag pops.
- Exit: fade 8 frames.
