# HttpReply

**Purpose:** response card `HTTP 429 Too Many Requests` + `Retry-After: 30`; small NGINX note "default 503 → set 429".

**Props:** `cardAt`, `headerAt`, `nginxAt`, `swapAt`, `rect` (card-local), `at`, `out`.

**Look**
- Response card in JetBrains Mono (status line ≥ 40 px).
- "Retry-After: 30" line highlights with an orange block.
- NGINX logo; "503" dim grey with strike → "429" orange.
- Code chip `limit_req_status 429;`.

**Motion**
- Lines type in.
- Strike draws.
- 429 springs in.

**Gotchas**
- Code ≥ 28 px.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
