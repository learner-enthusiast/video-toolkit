# VerifyChecklist

**Purpose:** what to check when verifying a JWT, plus the one-line code that does it.

**Props:** `items` ([{label, at}]: pin alg · exp · iss · aud), `code` ({text, at}), `warn` ({text: "Never trust the token's alg", at}) optional, `rect`, `out`.

**Look**
- Checklist.md rows with orange ticks, labels in Inter 700 ≥ 40 px, claim names in mono.
- Code chip: near-black card, JetBrains Mono ≥ 34 px white, wrapped:
  `jwt.verify(token, key, {` / `  algorithms: ['RS256'],` / `  issuer, audience })` with `['RS256']` on an orange block.

**Motion**
- Rows per Checklist.md (slide in 24 px + tick stroke) on their spoken words; code chip slides up with a spring.
- Exit: staggered fade 4 frames.
