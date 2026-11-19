# FooterSeal

**Purpose:** the footer is readable but authenticated; a `kid` in it allows key rotation.

**Props:** `at`, `out`, `byteAt` (one byte changes), `failAt` ("✗ verification failed"), `kidAt`, `rotateAt` (k1 → k2 → k3), `noLogoutAt`, `rect`.

**Look**
- Token line with the footer part highlighted; footer card in mono 40 px `{"kid":"k2"}` with a seal icon (orange) and label "readable · authenticated".
- One character flips (`k2` → `k3`, orange caret); the seal cracks (grey), chip "✗ verification failed" (dim + WarnMark).
- Key carousel in the JwksRotation style: k1 (dim), k2 (orange, in use), k3 (outline, next); keys slide left as they rotate; user icons stay with "still logged in" tag.

**Motion:** seal crack draws 6 frames with 2 px shake; keys rotate on a spring, 8-frame stagger. Exit fade.
