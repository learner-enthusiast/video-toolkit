# StorageDrawers

**Purpose:** where to keep tokens in the browser: not localStorage (XSS), the access token in memory, the refresh token in an HttpOnly · Secure · SameSite cookie.

**Props:** `browserAt`, `lsAt`, `xssAt`, `memAt`, `cookieAt`, `rect`, `out`.

**Look**
- A browser window card (top bar with dots) containing three stacked drawers, each a labelled tray: `localStorage`, `memory`, `cookie` (mono labels ≥ 34 px).
- localStorage: token chip inside; on `xssAt` a script line icon `<script>` reaches in and pulls it out; the drawer dims to warm grey with an orange WarnMark and an "XSS" tag.
- memory: orange access-token chip slides in.
- cookie: orange refresh-token chip with a lock, the drawer label `HttpOnly · Secure · SameSite`.

**Motion**
- Drawers slide open (translateX spring) on their words; chips drop in; the steal is an ease-in-out path out of the frame.
- Exit: fade 8 frames.
