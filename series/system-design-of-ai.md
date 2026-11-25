# Series: System Design of AI

Tracked rules for every episode in `projects/system-design-of-ai/<NN>-<topic>/` (the `projects/` folder is gitignored, so the rules live here). They add to `CLAUDE.md` and `brand.md`; where they differ for this series, this file wins on content and format, never on the brand look (`brand.md`) except the choices named below.

**Topics:** tracked in my sheet "AI System Design Shorts – 110 Topics" (no integration; I give you the topic).

**Format of every episode (3 parts, in this order)**
1. **How the normal / traditional flow works.** The old flow gets real explanation time, not a one-line setup: walk through each step of how it works without AI.
2. **Where it breaks with AI / LLMs.** Show the exact point of failure (latency, cost, state, size, nondeterminism…) with the same characters and the same diagram, so the break is visible.
3. **How to solve it.** The fix, shown on the same diagram.

**Money rule:** Every episode carries a business case in rupees (wasted AI spend, retries, lost or churned customers) with concrete numbers, sourced or clearly marked as illustrative, and ties each fix back to what it saves. Every rupee and token number on screen must match the script and the episode's `work/facts.md`.

**Story and characters**
- **From #05 on (current rule):** no Taarak Mehta characters and no avatars of them. Each episode is a simple-product story from the perspective of a junior dev who knows a little about the topic, told to the viewer as "you" ("you're the junior dev at…"). Other people (e.g. "your lead") appear only as generic, name-less elements (an initials chip, a chat sender), never a face.
- #01–#04 (legacy): told with Taarak Mehta Ka Ooltah Chashmah characters as role-players, only as simple, generic illustrated avatars with name labels in the brand style; no show stills, clips, logos or actor likeness, ever.

**Length and hook**
- Open with the hook line (boldest claim, result or problem) from frame 0, then "Namoshkar!" (~1 s hold + ~0.5 s pause). A 2–5 word text hook is on screen from frame 0. If "Namoshkar!" was recorded first, move that take to right after the hook (rule since 2026-11-24, #9).
- Close with a one-line recap (the payoff of the hook), then "Bye bye, sayonara!" with a wave, before the end card.
- 9:16 short; final length ≤ 2:59.

**Visuals**
- Layout states per `brand.md` (HEAD / FULL / SPLIT); creative direction per `CLAUDE.md`.
- Server-side code cards are tagged **"server"** (small pill on the card).
- Official tech logos for every named technology, reused from or added to the shared `icons/` library (`icons/icons.md`).
- Caption highlights are **orange** (`#E4572E`).

**End card**
- Series tag **"AI System Design · #N"** (N = the episode number).
- A next-episode tease: one line naming the next topic.
- Plus the standard links from `brand.md`.

**Deliverables:** the standard set from `CLAUDE.md` for reels (main video, one trailer and the cover/thumbnail, all 9:16 only; SRTs, ChatGPT kit, social JSON, carousel). No 16:9 output. Put "AI System Design · #N" in the social copy and thumbnail.

**Episodes**
| # | Folder | Topic |
|---|---|---|
| 01 | `projects/system-design-of-ai/01-streaming/` | Streaming |
| 02 | `projects/system-design-of-ai/02-token-rate-limiting/` | Token rate limiting. Exception: no Taarak Mehta characters and no avatars; told in plain second person ("you're building an e-commerce app"). |
| 03 | `projects/system-design-of-ai/03-semantic-caching/` | Semantic caching |
| 04 | `projects/system-design-of-ai/04-cost-metering/` | Cost metering. Exception: no Taarak Mehta characters; told with real companies (OpenAI, Replit, Cursor) and "you". Real people only as name + role text on quote cards. |
| 05 | `projects/system-design-of-ai/05-model-routing/` | Model routing. Exception: no Taarak Mehta characters; told in second person ('you're a junior dev at a startup that sells an AI code reviewer'); real companies (Kilo Code, Tessl) only as name + logo + source cards. |
| 06 | `projects/system-design-of-ai/06-cancellation/` | Cancellation (abort the LLM stream when the client leaves). Exception: no characters; plain explanation. |
| 07 | `projects/system-design-of-ai/07-provider-failover/` | Provider failover (retries, circuit breaker, fallback chain across LLM providers). Exception: No Taarak Mehta characters and no character avatars; told in plain second person ('you're a junior dev at an instant-loan app'). |
| 08 | `projects/system-design-of-ai/08-long-running-requests/` | Long-running requests. Exception: no Taarak Mehta characters and no avatars; told in plain second person ("you're a junior dev at an investing app"), with one phone-call analogy running through the whole episode. |
| 09 | `projects/system-design-of-ai/09-prompt-caching/` | Prompt caching. Exception: no characters; told as "you", a junior dev at an insurance company; KYC analogy. |
| 10 | `projects/system-design-of-ai/10-batch-inference/` | Batch inference. Exception: No Taarak Mehta characters and no character avatars; told in plain second person ('you're the junior dev at a stock trading app'). |
| 11 | `projects/system-design-of-ai/11-max-tokens-and-truncation/` | max_tokens and truncation. Exception: no Taarak Mehta characters; second person (junior dev at a travel startup); real incident only as an anonymous IncidentCard. |
| 12 | `projects/system-design-of-ai/12-tokenizers/` | Tokenizers. Exception: no Taarak Mehta characters; told in second person ('you're the junior dev at an online electronics store adding Hindi'); real sources only as name + logo + source cards. |
