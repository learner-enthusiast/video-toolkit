# RegistryCalls

**Purpose:** the OCI distribution spec: one client sends the same two HTTP calls to three registries, and all three answer.

**Props:** `registries` (`[{logo, label, at}]`, default Docker Hub, GHCR, Amazon ECR), `calls` (`[{text, at}]`), `tickAt`, `out`.

**Look**
- Three registry boxes in a row (white cards, 2 px border, 14 px radius) with the official logo and an Inter 600 label; a client box above them.
- Request chips: dark pill (`#111` fill, white JetBrains Mono 600, ~26 px, `GET` in orange). Chips must fit the card width: wrap the path after `/v2/library/nginx/` if needed, never shrink below 24 px.
- Tick: orange round badge with a white check on each registry.

**Motion**
- Boxes pop in on their spoken names (spring, 5-frame stagger).
- Each chip types in (mono, ~2 chars/frame), then copies of it fly to the three boxes along eased curves (orange dot travels the path).
- Ticks pop on the three boxes 4 frames apart.

**Gotchas**
- Text exact: `GET /v2/library/nginx/manifests/latest` and `GET /v2/library/nginx/blobs/sha256:a1b4…`.
- Docker Hub has no own logo: Docker mark + "Docker Hub" label. GHCR = official GitHub mark + "GHCR".
