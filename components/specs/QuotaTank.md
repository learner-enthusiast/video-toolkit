---
code: components/code/QuotaTank/QuotaTank.tsx
preview: components/code/QuotaTank/preview.png
props: "QuotaTank {x,y,w,h,at,out,labelAt,drainAt,dryAt,splitAt,flowAgainAt,label,logo,taps,splitLabels,errorText}"
variants: "one tank draining, thin tap dry + 429, split into two tanks with flow restored"
last_used: system-design-of-ai/10-batch-inference
---
# QuotaTank

**Purpose:** vertical-tank variation of AccountQuotaBar: one shared provider limit drawn as a water tank, with one tap per consumer. A thick tap ("Report job") drains it; a thin tap ("Live assistant") sputters dry to an orange ⚠ 429. It can split into two tanks ("Live limit" / "Batch queue") so the live tap flows again.

**Props:** `x`, `y`, `w`, `h`, `label` ("OpenAI limit · per organization"), `level` (0..1 fill, or keyframes [{t, v}]), `taps` ([{label, thick, flowFrom, flowTo, dryAt, errorText}]), `inflowAt` (arrows/requests pour in at the top), `splitAt` + `split` ({left: {label, level}, right: {label, level}}), `at`, `out`, `dark`.

**Look**
- Tank: tall rounded rectangle (brand radius), 2 px near-black outline, a few level tick marks; water = orange at ~80% opacity with a gentle surface wave.
- Taps: pipes out of the bottom; thick tap = wide orange stream; thin tap = narrow stream. Dry = dim grey pipe, a couple of grey drips, orange ⚠ + "429" mono chip.
- Labels: Inter 800 under each tap, tank label in a white pill on top.
- Split: the tank divides with a vertical wall into two narrower tanks, each with its own label pill.

**Motion**
- Level changes ease-in-out; the surface wave is a slow sine (no linear motion).
- Thick tap drains the level in sync with its stream; thin tap sputters (stream width pulses, then breaks into drips) before going dry.
- Split: the wall draws top to bottom (~12 frames), the halves spring apart ~20 px; the live tap's stream returns.
- Exit with a fade on `out`.

**Sound:** `tick` as the level steps down on spoken numbers, `stamp-thud` on the 429 chip, `whoosh` on the split.

**Gotchas**
- Bad = dim grey + orange ⚠, never red. Good flow = orange.
- Keep the 429 chip clear of the tap labels (≥ 24 px).
- Triggers on spoken-word frames; every element exits.

## Code

Saved: `components/code/QuotaTank/QuotaTank.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: QuotaTank {x,y,w,h,at,out,labelAt,drainAt,dryAt,splitAt,flowAgainAt,label,logo,taps,splitLabels,errorText}.
- First built and rendered in `system-design-of-ai/10-batch-inference`.
