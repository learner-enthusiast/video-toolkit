# Project demo: <project name>

**Message:** <one sentence the viewer could repeat>

**Brand:** 1 <1 | 2 | 3, `brand.md`>

**URL:** <sub.domain> · **Target:** <n> min (word cap: `CLAUDE.md` → House numbers) · **Aspect:** 16:9 + 9:16 trailer if > 3:00 (long-form); 9:16 only if ≤ 2:59 (reel)

## Glossary (exact spellings for captions)
- <term>, <term>

## Opening
**On-screen text (2–5 words, from frame 0):** <bold claim or result>
`[B01 | mm:ss–mm:ss | HEAD]` · "<hook line>" → <cue>
`[B02 | mm:ss–mm:ss | HEAD]` · "Namoshkar!" (timing and delivery: `CLAUDE.md` → House numbers)
`[B03 | mm:ss–mm:ss | SPLIT]` · "<one-line pitch: what it is, who it's for>" → whip-cut to `work/clips/<clip>.mp4`, UrlPill `<url>`

## What it does (one beat per feature)
Beats: `[Bnn | mm:ss–mm:ss | HEAD, FULL or SPLIT]` · spoken text → visual cue (trigger word in quotes). IDs are `B01…`, unique and in order across the whole script; a Hindi twin and the scene cues use them. The state tag is the layout plan (`brand.md` Layout); Claude may improve it (`CLAUDE.md`, Creative direction).

`[B04 | mm:ss–mm:ss | SPLIT]` · "<feature, user's view>" → screen `assets/<shot>.png`, Ken Burns to <region> on "<word>"
`[B05 | mm:ss–mm:ss | FULL]` · "<feature>" → Highlight <region> on "<word>"

## How it works
`[B06 | mm:ss–mm:ss | SPLIT]` · "<architecture in one breath>" → FlowDiagram `<A → B → C>`, travelling dot; IconRail <stack>
`[B07 | mm:ss–mm:ss | FULL]` · "<hardest problem + result>" → Counter / BarCompare + Stamp

## Close (`CLAUDE.md` → House numbers)
`[B08 | mm:ss–mm:ss | HEAD]` · "<one-line recap: the payoff of the hook>" → full frame
`[B09 | mm:ss–mm:ss | HEAD]` · "Bye bye, sayonara!" with a wave
**End card** (5 s) → EndCard

## Trailer order (if any)
`B01 → B02 → B03 → B04 → B07 → B08 → B09 → end card`

## Web captures (Claude takes these with Playwright)
| # | URL (or "find the source") | Capture (element / full page / clip) | For beat | Focus on |
|---|---|---|---|---|
| 01 | <https://…> | <element: the pricing table> | <B2> | <the "per 1M tokens" row> |
