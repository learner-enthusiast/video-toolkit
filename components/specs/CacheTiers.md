# CacheTiers

**Purpose:** a layered read path: a request goes down the tiers and is answered by the first one that has the file.

**Props:** `tiers` (label, sub, logos?, `at`), `hitAt` (frame the "99%+" badges tick in), `failAt` (frame one cache fails), `rect`, `out`.

**Look**
- Four stacked rounded bars (brand radius, 2 px border), top to bottom: "Your machine", "Node cache", "Regional cache", "Main server". The server bar is darker (near-black, white text) with the official Spanner and Cloud Storage logos on small white tiles under it.
- A small orange packet (with a soft glow) drops from the top; the answering tier flashes an orange outline and the packet bounces back up.
- "99%+" pills on the right of each cache tier.
- Failure: one regional cache (a second regional box beside the first) dims to warm grey with an orange warning mark; an orange "wall" bar slides in under it so its misses never reach the server; the server shows an orange ✓.

**Motion:** each tier springs in on its spoken word (stagger by the words, not by a fixed 5 frames). Packet travel is ease-in-out between tiers. 99%+ pills pop 4 frames apart.

**Gotchas:** no green/red. Keep tier labels ≥ 40 px. Leave the right ~15% of the frame free of text (platform buttons) when the card is wide: badges sit inside the card's right padding.
