---
code: components/code/PhoneMockup/PhoneMockup.tsx
preview: components/code/PhoneMockup/preview.png
props: "w, h, app, variant ('plan' | 'home'), days [{title,text}], typeFrom, typeTo, prefilled, blinkFrom, emptyDays, subtitle, tagline, cta, heroA, heroB, placeholder, dark, at, out"
variants: "plan (types, freezes mid-sentence, empty day slots) · home; shopping variant spec-only"
last_used: system-design-of-ai/11-max-tokens-and-truncation
---
# PhoneMockup

**Purpose:** a generic shopping-app screen showing what the customer sees (product + price), to make "users see the old price" concrete.

**Props:** `product` (ProductCard data), `price` (PriceTag), `clock` (status-bar time text), `refreshAt` (list of {at, price}), `rect`, `at`, `out`.

**Look**
- Rounded phone frame (near-black bezel, 2 px), status bar with the clock, a plain brand-styled app header ("Diwali Sale"), the product image area and the price. No real app logos or UI.

**Motion**
- Enters with a spring slide-up. `refreshAt`: a small pull-to-refresh spinner, then the price swaps (PriceTag flip).

**Gotchas**
- Price ≥ 56 px inside the phone so it reads at phone width; keep the phone ≤ 45% of the card width when two sit side by side.

## Variant: `plan` (added for system-design-of-ai/11-max-tokens-and-truncation)

**Purpose:** an AI trip-planner screen that types a day-by-day plan and freezes mid-word, so "the answer stopped, silently" is visible.

**Props (plan variant):** `variant: 'plan' | 'home'`, `app` (invented brand name, e.g. "TripMate"; never a real app), `w`, `h`, `days` ([{title, text}]), `typeFrom`, `typeTo` (frames the visible text types across), `stopAt` (0–1 share of the total text where typing freezes), `blinkFrom` (cursor blinks 3× then freezes), `emptyDays` (number of trailing day slots drawn as dim dashed outlines), `dark`, `at`, `out`. `home` variant: `tagline`, `cta`.

**Look**
- Same frame as the base (near-black bezel, 2 px border, brand radius inside), invented app header with a plain line-icon (no logo). Day cards: white, 2 px border, "Day N" kicker in orange Inter 800, body Inter 600. Frozen cursor = orange bar. Empty days = dashed `#8A857C` outline, label dim. Dark: screen stays light, frame on #0D0D0D, no shadow.

**Motion**
- Typing at word granularity between `typeFrom` and `typeTo` (eased, never linear per frame); auto-scroll keeps the cursor line visible; freeze is a hard stop (no ease), then the cursor blinks 3× (8-frame period) and stays on.

**Sound:** `typing-tick` every ~5 frames while typing; nothing on the freeze (silence is the point).

## Code

Saved: `components/code/PhoneMockup/PhoneMockup.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values come from `components/code/theme.ts`.

- Code props: w, h, app, variant ('plan' | 'home'), days [{title,text}], typeFrom, typeTo, prefilled, blinkFrom, emptyDays, subtitle, tagline, cta, heroA, heroB, placeholder, dark, at, out.
- First built and rendered in `system-design-of-ai/11-max-tokens-and-truncation`.
