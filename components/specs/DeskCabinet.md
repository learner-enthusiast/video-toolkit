# DeskCabinet

**Purpose:** a near vs far analogy for memory and disk: a desk within arm's reach, a cabinet in another building.

**Props:** `w`, `h`, `ramAt`, `deskAt`, `diskAt`, `cabinetAt`, `out`.

**Look**
- Left third: a desk with a sheet of paper and an orange "RAM = desk" tag, a hand that grabs the paper, and a dim "~100 ns" label.
- Far right: a small building with a filing cabinet inside and a neutral "Disk = another building" tag.
- A dotted road links the two. All line drawing, 3 px strokes; orange only on the tag and the opened drawer.

**Motion**
- The scene is a world 1.4× the box width. At `diskAt` it translates left by 40% of `w` (ease, 18 frames).
- The hand springs in and lifts the paper. The road draws as dots over 30 frames. The drawer springs open at `cabinetAt`.

**Gotchas**
- Dots are sampled along the path with `getPointAtLength` (a dashed stroke cannot be drawn progressively).
- World coordinates assume `w` ≈ 876; scale them if the box changes.
- The desk ends up off-screen after the pan; hold the hand beat until `diskAt`.
