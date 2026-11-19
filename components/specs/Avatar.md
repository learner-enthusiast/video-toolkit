# Avatar

**Purpose:** a story character drawn as a simple, generic illustrated face with a name label, in brand style. For series that cast real or fictional characters as system actors (user, server, owner) where stills or likeness are not allowed. For supplied face stills use `FaceAvatar`.

**Props:** `who` (character id), `mood` (neutral | worried | happy), `size`, `label` (true = the character's name, or a custom string), `focus` (0–1 orange ring), `at`, `out`, `shakeAt`, `bounceAt`, `dim`.

**Look**
- Circle, 2 px near-black border, warm off-white `#EFEAE0` behind. Flat SVG face (viewBox 100): shirt, neck, ears, head, hair, brows, eyes, nose line, mouth. One skin tone per character; no gradients.
- Characters differ by **hints only**: hair shape, a mustache, glasses, shirt colour from the brand palette (orange, ink, white, cream `#F1E6CF`, warm grey `#B9B2A6`). Never a likeness, a show costume or a catchphrase prop.
- Name label: a white pill, 2 px border, Inter 900, overlapping the bottom of the circle by ~12% of the size.
- Sizes: ~96–130 px as a speaker badge or in a list, ~170–230 px as a scene's subject.
- Generic extras (customers, users) use the same kit with different hair and shirts, and no name (or "Customer").

**Motion**
- Enter: pop (spring, damping 11) from 0.8 scale with a fade; exit fades over 8 frames.
- shake (bad news): horizontal sine, 12 px, decays over 18 frames. bounce (relief): one 24 px hop over 14 frames.
- Mood swaps on a spoken word (worried on the problem, happy on the fix), on the same frame as a shake or bounce.

**Gotchas**
- A name label under an avatar that sits behind a prop (a counter, a desk) gets hidden: put the name on the prop instead.
- On dark style the 2 px near-black border vanishes; the light circle fill still reads, so keep it.
- Keep one look per character across the whole series (reuse the project's `ui/avatar.tsx` from the previous episode; add new characters there).
