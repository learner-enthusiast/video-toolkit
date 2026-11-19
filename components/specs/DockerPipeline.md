# DockerPipeline

**Purpose:** the Docker flow: a Dockerfile whose lines light up as spoken, then Dockerfile → build → image → push → Docker Hub → run → server, ending in a fan-out.

**Props:** `lines` (`[{code, at}]`), `steps` (`[{label, cmd, at}]`), `fanAt`, `at`, `out`.

**Look**
- Dockerfile card: white card, title chip "Dockerfile", JetBrains Mono ≥ 30 px, the current line on an orange-tint row with an orange left bar; spoken lines stay black, unspoken ones dim grey.
- Flow: nodes in a vertical zig-zag that fits the 9:16 card (Dockerfile → image → Docker Hub → server), each edge labelled with its command chip (`docker build`, `docker push`, `docker run`) in mono.
- Image node = the orange box with a lock; Docker Hub node = official Docker mark + "Docker Hub" text chip; server = line icon.
- Fan-out: the box multiplies onto a laptop, a teammate's PC and a grid of small server icons that fills in, each with a small orange check.

**Motion**
- Line highlight moves with a spring (row y) on each spoken step.
- Edges draw themselves (10 frames); an orange packet travels each edge on its command word.
- Fan-out grid fills in a staggered wave (2 frames per icon), ease-out.

**Gotchas**
- The Dockerfile text must match `script.md` exactly (package files copied before `npm install`).
- Code ≥ 28 px (composition.md gotcha); wrap rather than shrink.
