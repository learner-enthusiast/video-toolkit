# ProtocolStack

**Use:** showing where several protocols sit around one agent (e.g. MCP / A2A / AG-UI).

**Layout:** one round "Agent" node at the left-centre of the grid card; three horizontal layers to its right, stacked with equal gaps. Each layer: protocol logo or name (left), a line that draws from the Agent node to a target box (right: "Tools & data", "Other agents", "User").
- Each layer has an icon slot that lands on a spoken word (e.g. hand, two people, face line icons), drawn as simple 3 px near-black line icons; the active one is orange.

**Props:** `layers: {name, logo?, target, at, icon, iconAt}[]`, `focus?: number` (index of the layer to ring in orange while the others dim), `from`, `out`.

**Motion:** layers draw top to bottom on their words (line draw ~10 frames, target box spring pop); icons pop with a small overshoot; when `focus` is set, the others dim to warm grey over ~8 frames. Exits with a short eased fade.
