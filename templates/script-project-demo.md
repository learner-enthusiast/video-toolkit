# Project demo: <project name>

**Message:** <one sentence the viewer could repeat>

**URL:** <sub.domain> · **Target:** <n> min (word cap: `CLAUDE.md` → House numbers) · **Aspect:** 16:9 + 9:16 trailer if > 3:00 (long-form); 9:16 only if ≤ 2:59 (reel)

## Glossary (exact spellings for captions)
- <term>, <term>

## Opening
**On-screen text (2–5 words, from frame 0):** <bold claim or result>
**O1** · "<hook line>", then "Namoshkar!" (timing and delivery: `CLAUDE.md` → House numbers) → HEAD
**P1** · "<one-line pitch: what it is, who it's for>" → whip-cut to SCREEN + BUBBLE `work/clips/<clip>.mp4`, UrlPill `<url>`

## What it does (one beat per feature)
Format: **ID** [TRAILER] · `[mm:ss–mm:ss | HEAD, FULL or SPLIT]` · spoken text → visual cue (trigger word in quotes). The state tag is the layout plan (`brand.md` Layout); Claude may improve it (`CLAUDE.md`, Creative direction).

**F1** · "<feature, user's view>" → SCREEN + BUBBLE `assets/<shot>.png`, Ken Burns to <region> on "<word>"
**F2** · "<feature>" → SCREEN, Highlight <region> on "<word>"

## How it works
**H1** · "<architecture in one breath>" → GFX + BUBBLE: FlowDiagram `<A → B → C>`, travelling dot; IconRail <stack>
**H2** · "<hardest problem + result>" → Counter / BarCompare + Stamp

## Close (`CLAUDE.md` → House numbers)
**C1** · "<one-line recap: the payoff of the hook>" → TALK, full frame
**C2** · "Bye bye, sayonara!" with a wave → HEAD
**End card** (5 s) → EndCard

## Trailer order (if any)
`O1 → P1 → F? → H2 → C1 → C2 → end card`

## Web captures (Claude takes these with Playwright)
| # | URL (or "find the source") | Capture (element / full page / clip) | For beat | Focus on |
|---|---|---|---|---|
| 01 | <https://…> | <element: the pricing table> | <B2> | <the "per 1M tokens" row> |
