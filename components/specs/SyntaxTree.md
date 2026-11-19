---
code: components/code/SyntaxTree/SyntaxTree.tsx
preview: components/code/SyntaxTree/preview.png
props: "file, code string[], codeAt, nodes [{id,label,kind,x,y,parent?,at}], w?"
variants: "kind colours: class/call filled orange, others white"
last_used: Graphify
---
# SyntaxTree

**Purpose:** how a parser (tree-sitter, an AST) reads code: a short source file on top, then its syntax tree unfolds node by node underneath, each node labelled with its kind.

**Props:** `file` (tab name), `code` (lines), `codeAt`, `nodes` (label, kind, position in the component's box, parent id, frame).

**Look**
- Code card: white, brand border/radius, a grey tab with the file name, JetBrains Mono 600 28 px.
- Tree nodes: small rounded tiles, kind in small caps above the mono label; `class` and `call` kinds filled orange, others white. 3.5 px near-black connectors from parent to child.

**Motion**
- The code card enters first; each connector grows from parent to child (~10 frames) just before its node pops.

**Gotchas**
- Keep the tree inside whatever frame the scene draws around it (Graphify: a laptop outline); 4 levels at ~90 px spacing fit under a 4-line code card in ~560 px.

## Code

Saved: `components/code/SyntaxTree/SyntaxTree.tsx` (preview: `preview.png`).
