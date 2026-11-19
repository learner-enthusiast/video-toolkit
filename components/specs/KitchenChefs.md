# KitchenChefs

**Purpose:** a "many workers, one tool" scene that flips to "one worker, no waiting" (here: many chefs and one knife vs one fast Redis chef).

**Props:** `w`, `h`, `crowdAt`, `waitAt`, `swipeAt`, `fastAt`, `logoAt`, `out` (absolute frames).

**Look**
- Line-drawing chefs (circle head, toque, rounded body, line arms), 3 px near-black strokes, white fills, round caps.
- Five chefs in a semicircle round one orange knife on a small board. "waiting…" bubbles (white, 2 px border, Inter 500 26 px, dim) on four of them.
- Hero chef is bigger, has his own orange knife; a ticket rail of five white mono tickets (#1–#5) runs along the top. A logo tile sits on his apron.

**Motion**
- Chefs draw in staggered 4 frames; bubbles pop staggered 5 frames; heads dim slightly.
- At `swipeAt` the crowd slides left and fades (12 frames, eased); the hero springs in from the right.
- At `fastAt` the knife arm chops on a 6-frame eased cycle; tickets fly right one every 10 frames (ease + fade) and recycle.
- Logo stamps on the apron: scale 1.6 → 1 with a stiff spring. Whole scene fades out at `out`.

**Gotchas**
- Root clips with overflow hidden so tickets and the crowd can leave the box.
- Bubble and crowd positions come from the `w` centre; keep `w` ≥ 800 so side chefs stay 20 px inside the edges.
- Chop is a periodic loop from `fastAt`, so a cut mid-cycle looks fine.
