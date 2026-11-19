---
code: components/code/GraphBuild/GraphBuild.tsx
preview: components/code/GraphBuild/preview.png
props: "nodes [{id,label,x,y,w?}], show {id: frame}, edges [{a,b,at,dashed?,tone?,arrow?,dur?,hot?}], clusters [{label,ids,at,pad?}], tags [{edge,text,at,tone?,dx?,dy?}], lit {ids,at,out?}, dimOthers {at,out?}, pulse {id,at}, packet {path,at,per}, nodeW, size, w, h, dark"
variants: "hop trail (ordered show + orange edges + packet), full graph (edges + clusters + found/guessed tags), god node (pulse + hot inbound edges + dimOthers), blast radius (lit callers + dimOthers), recap path (lit path)"
last_used: Graphify
---
# GraphBuild

**Purpose:** a code map built in front of the viewer: nodes (functions, classes, files) pop in, edges (calls, imports) draw, neighbourhoods wrap them, and edges carry a tag (found in code / guessed). The same node positions serve every later beat, so a hop trail the viewer watched turns into the map.

**Props:** `nodes` (id, label, centre x/y in card-local px, optional width), `show` (frame each node pops; missing = hidden), `edges` (from, to, frame, `dashed` = guessed, `tone`, `hot` = never dimmed), `clusters` (label + node ids, dashed orange area), `tags` (pill on an edge's midpoint), `lit` (ring these nodes orange; edges between two lit nodes turn orange), `dimOthers` (fade everything not lit), `pulse` (god node: breathing orange halo), `packet` (orange dot travelling along a path, hop by hop).

**Look**
- Nodes: white rounded boxes (brand radius, 2 px border, soft shadow), JetBrains Mono 700 labels. Lit/pulsed nodes fill orange with white text.
- Edges are drawn edge-to-edge (exit points on the box outline, never through labels), 4 px near-black with arrowheads; guessed edges are dashed; lit edges 6 px orange.
- Clusters: dashed orange outline, 6% orange wash, small-caps Inter 900 label above the top-left.
- Dark style: node fill #1A1A1A, white text, light edges.

**Motion**
- Nodes pop with the brand spring (scale 0.82 → 1); edges grow from source to target over ~12 frames, arrowhead appears at the end; clusters scale 0.94 → 1.
- Packet eases between hops; dim/lit transitions ease over ~8–10 frames. Everything exits with its Scene.

**Gotchas**
- Three columns of 240 px nodes in a 972 px card leave ~60 px gaps: horizontal neighbours' edges are short, so put tags on diagonal or vertical edges.
- Hot inbound edges (god node) need `hot`, or `dimOthers` fades them with the rest.
- Scale the whole graph (CSS transform on a 972x970 wrapper) for SPLIT beats; never re-position nodes per beat.

## Code

Saved: `components/code/GraphBuild/GraphBuild.tsx` (preview: `preview.png`). Import it, set props. Brand values come from `components/code/theme.ts`.
