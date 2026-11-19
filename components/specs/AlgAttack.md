# AlgAttack

**Purpose:** JWT's core flaw: the token's own header tells the server how to verify it, shown as two forgeries (`alg: none`, RS256 → HS256).

**Props:** `at`, `out`, `arrowAt` ("token → server: verify me like this"), `noneAt`, `skipAt` (signature deleted, server "✓ valid"), `swapAt` (RS256 → HS256), `secretAt` (public key → HMAC secret), `adminAt` ("✓ role: admin"), `dateAt` ("2015 · Tim McLean" chip), `stampAt` ("Forged admin token"), `rect`.

**Look**
- Top: header card in JetBrains Mono ≥ 40 px `{"alg": "RS256"}`, value on an orange block. Right: server line icon. A dashed arrow between them labelled "verify me like this" (Inter 600, dim).
- Beat 1: the value retypes to `"none"`; the signature segment of a token strip below is struck and slides away; server answers with a near-black chip "✓ valid".
- Beat 2: value retypes to `"HS256"`; a pinned noticeboard (cork-free: white card, 2 px border, pin dot orange) holds a key icon labelled "public key"; the key flies into a "HMAC secret" slot; server chip "✓ role: admin".
- Chip "2015 · Tim McLean" (dim pill, top right). `StampMark` "Forged admin token" (orange) across the bottom.

**Motion:** retype 2 chars/frame; strike draws 6 frames; key flies on a spring arc; chips pop. Beat 1 dims to 0.35 when beat 2 starts. Exit fade 8 frames.

**Gotchas:** the forged-but-accepted state is the "bad" state: never green ticks; the server chips are near-black, the forgery warning is orange.
