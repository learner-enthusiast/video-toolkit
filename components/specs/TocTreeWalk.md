# TocTreeWalk

**Purpose:** vectorless / reasoning-based retrieval: a document becomes a table-of-contents tree, and a model walks it node by node to the answer.

**Props:** `nodes` (id, title, sub, parent), `mode` (index | build | walk), index: `rows`, `stops`; build: `llmAt`, `treeAt`, `nodeAt`, field times; walk: `stops` (node id + frame), `thoughts`, `openAt`, `answerAt`, `citeAt`.

**Look**
- Index mode: a book page (thick dark spine) titled "Index", chapter and section rows; an orange pointer steps down the rows and visited rows stay orange.
- Tree: root → chapters → sections, white node cards (title + sub), 3 px elbow edges. One shared geometry for build and walk.
- Node card (build): title · pages · summary · children, mono orange keys, each field revealed when spoken. Mark invented values "illustrative".
- Walk: an orange ring cursor travels node to node; visited nodes keep an orange border and their edges turn orange (the breadcrumb stays lit); the answer node fills orange. Thought bubbles are serif-italic pills with an orange border.
- Answer row: a bot bubble with a mono citation pill ("Sec 17(5)(a)").

**Motion**
- Build: an orange scan line reads the document once, the page shrinks into the root, then levels pop top-down (4-frame stagger).
- Cursor moves on one spring per hop, on the spoken node name.

**Gotchas**
- Keep ≤ 3 nodes per level at 9:16 (972 px card); longer titles wrap badly.
- Thought bubbles live in the gaps between levels; give each an exit before the next element needs the space.
- Dim the branches that were not taken once the walk starts, so the path reads at a glance.
