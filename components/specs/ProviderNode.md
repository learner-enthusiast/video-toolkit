---
code: components/code/ProviderNode/ProviderNode.tsx
preview: components/code/ProviderNode/preview.png
props: "ProviderNode: w, h, icon, logo, logos, label, sub, dim, ring, badge · Packet: x1, y1, x2, y2, t0, t1, size, label · DrawLine: x1, y1, x2, y2, at, dur, dash, arrow"
variants: "dim, ring, badge"
last_used: system-design-of-ai/07-provider-failover
---
# ProviderNode

**Purpose:** the building blocks of a request/provider diagram: a provider or server card, a packet that travels between cards, and a line that draws itself. Shared by RetryStorm, FallbackLadder, ErrorTriage, JsonValidator and the master diagrams.

**Look**
- `ProviderNode`: white card, 2 px near-black border, the brand radius and shadow; official logo(s) or an icon on the left, a bold Inter label, a grey sub-line. `dim` greys it (failed/down); `ring` adds the orange focus ring (the one that answers); `badge` sits on the top-right corner (use `XMark` / `TickMark` from `glyphs`).
- `Packet`: small orange rounded square with a near-black border, optional mono label.
- `DrawLine`: near-black stroke (orange for the active path, dashed grey for a dead one), optional arrowhead.

**Motion**
- Packets travel with ease-in-out (`tween`), never linear; lines draw over `dur` frames.

**Gotchas**
- "Bad" is dim grey + an orange warning or grey ✕, never red (`brand.md`). Dim lowers logo opacity; never recolour a logo.
