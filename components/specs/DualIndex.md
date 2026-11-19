# DualIndex

**Purpose:** a chunk splits into two indexes: a vector index (dot cloud clustering) and a BM25 keyword index (keyword list).

**Props:** `splitAt`, `vectorAt`, `bm25At`, `highlight` ("S24"), `logo` (pgvector → PostgreSQL elephant + "pgvector" label), `rect`, `out`.

**Look**
- Two cards side by side. Vector: ~60 dots that cluster into 3–4 groups, one cluster orange. BM25: a mono keyword list (JetBrains Mono ~30 px) with term counts; the highlight term on an orange block.
- Logo tile under the vector card.

**Motion**
- The chunk card splits into two copies that fly left/right; dots spring from random to clustered positions (seeded).

**Gotchas**
- Generic icons for BM25 and the vector cloud, no vendor logos.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (`brand.md`). No emojis.
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`). Motion is spring or ease-in-out only.
