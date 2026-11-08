# ContainerStack

**Purpose:** the one architecture diagram of the container stack, built up across several scenes. Viewers learn it once, so every layer keeps the same position every time it appears.

**Props:** `layers` (which are visible: `kernel`, `runc`, `containerd`, `shims`, `dockerd`, `cli`, `kubelet`, `cri`, `dockershim`, `crio`), `at` (frame per layer reveal), `grey` (`[{layer, at}]`), `lift` (`[{layer, at, label}]`), `paths` (`[{id, nodes:[…], at, side}]`), `blink` (`{layer, at, dur}`), `out`.

**Geometry** (fixed, in grid-card px of the 9:16 SPLIT card, ~972x970; never changes between scenes)
- Right column (x 330–850, 520 wide, so text stays left of the right UI edge): layers 96 px tall: `docker CLI` y 130 · `dockerd` y 250 · `shim` row y 372 (3 boxes 140x48) · `containerd` y 440 · `runc` y 600. `Linux kernel` spans x 20–850 at y 760.
- Left column (x 20–220): side chips ("BuildKit · build", "networking", "volumes"; "runc · Go", "crun · C · faster") at y 150–700; `kubelet` box y 380–600 with a `CRI · gRPC` plug to containerd's left edge (x 220→330, y 488) and `dockershim` inside its lower half; `CRI-O` y 640–724. Timeline chips go under the kernel (y 880).
- Two-path mode: the Docker path runs down x 878; the Kubernetes path kubelet → (x 300) → containerd's left edge → down → runc. Both share the bottom two layers.

**Look**
- Each layer is a white card: 2 px `#1A1A1A` border, 14 px radius, brand shadow. Official logo at the left (containerd, runc, Docker mark, Kubernetes, CRI-O), name in JetBrains Mono 600 lowercase for CLI tools (`runc`, `containerd`, `dockerd`, `kubelet`), Inter 600 for `Linux kernel` and `docker CLI`.
- Grey: card dims to `#8A857C` text, logo at 35% opacity, border warm grey; orange warning mark when it means "removed".
- Path trace: orange 8 px line that draws node to node with a travelling dot; each node it reaches gets an orange 3 px ring. Path labels (`docker run`, `kubelet`) in mono at the path start.
- Highlighted layers (twist): orange fill block behind the name, white text.

**Motion**
- Layer reveal: spring drop from −40 px + fade (damping 14), staggered 5 frames when several land together; shims pop one by one.
- Blink: opacity 1 → 0.2 → 1 over `dur` (ease-in-out); shims stay at full opacity.
- Lift: layer rises 60 px and tilts 4°, then fades to 30% with its label tag.
- Path: draws at ~0.4 s per hop, ease-in-out, synced so each node lights on its spoken word.
- Exit: the whole stack scales to 0.96 and fades over 10 frames.

**Gotchas**
- Never re-layout between scenes: missing layers leave their slot empty. Build the scenes from one shared geometry constant.
- The order on screen must match the script: dockerd → containerd → runc; kubelet → CRI → containerd / CRI-O → runc.
- Logos keep their official colours, `object-fit: contain`.
