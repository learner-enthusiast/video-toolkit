# ImageManifest

**Purpose:** the OCI image spec as a tree: manifest → config + layers, each named by a short digest; then the layers as tarballs, two tools producing one digest, and many images sharing one base layer.

**Props:** `rows` (`[{label, digest, at}]`), `tarAt`, `sameAt` (`{logos:[a,b]}`), `shareAt`, `shareCount` (10), `out`.

**Look**
- Tree card in JetBrains Mono 500, ~34 px: `manifest` root, `├─ config  sha256:9f2c…`, `└─ layers` with three indented rows. Tree lines drawn in `#1A1A1A`; digests in warm grey until highlighted orange.
- Tarball: each layer row turns into a small box icon (white, 2 px border, a folded "tar" tab) with its digest underneath.
- Same digest: two official logos (Docker, Podman) each with an arrow into one digest chip; orange tick.
- Shared base: 10 small app image blocks stacked on one wide `node:20 base` block; a counter tag "1×" (Inter 900) pops on the base.

**Motion**
- Tree rows draw top-down with the line growing first, then the text, 5-frame stagger, each row on its spoken word.
- Row → tarball morph: spring scale 1 → 0.6 with the box fading in (12 frames).
- Shared stack: blocks drop one by one (3 frames apart) with a spring; counter pops last.

**Gotchas**
- Digests on screen must match the script exactly (`sha256:9f2c…`, `a1b4…`, `7c0e…`, `e83d…`) and match later scenes (`a1b4…` reappears in RegistryCalls and the podman pull log).
