---
code: components/code/PhoneLine/PhoneLine.tsx
preview: components/code/PhoneLine/preview.png
props: "AppTile {at,label,screen,dark,ring} · SrvTile {at,label,glow,dim,logos,children} · Wire {calls [{drawAt,pulseTo,silentAt,closeAt,snipAt,snipX,marks,greyAt}], travels [{t0,t1,dir,node,drop}]} · Booths {booths [{x,logo,lw,lh,label,at,limit,limitAt,timer,scissorsAt,scissorsDimAt,lockAt,badge,dimAt}]} · Tap {x,y,at} · GEO"
variants: "open/pulsing/silent/closed/snipped + dangling, cut marks, dropped reply; booths with limit, timer, scissors (on/grey), lock, badge"
last_used: system-design-of-ai/08-long-running-requests
---
# PhoneLine

**Purpose:** the episode-long "a request is a phone call" picture: the app (a phone) on the left, the server on the right, one wire between them. The same drawing returns beat after beat, so the viewer watches the same line open, go silent, get cut, then get replaced. Middlemen sit on the wire as small "booths" (logo + silence timer) that can hang up.

**Props:** `app`/`server` (tile entrance frames + labels), `dialAt` (wire draws from phone to server), `pulse` (frame ranges where orange dots run along the wire: line open), `silentAt` (dots stop, wire goes calm grey-orange), `replies` (a packet travelling server → app; `drop` makes it fall off at the snip instead), `booths` (x on the wire, official logo file, label, optional silence timer that counts `timerFrom → timerTo` seconds from `timerAt`, scissors icon from `scissorsAt`, greyed scissors from `scissorsDim`, a lock + small label from `lockAt`), `snip` (x and frame where the wire is cut: the two ends spring apart, the app-side half drops and dangles), `closeAt` (line closes cleanly: wire fades out from both ends), `dimAt`, `at`, `out`, `w`, `h`.

**Look**
- Brand grid card. App tile: a generic phone outline (2 px near-black, 14 px radius). Server tile: white tile with a generic server line icon. Labels Inter 800 under each.
- Wire: a 6 px gently sagging cord; open = orange, silent = orange at 45%, dead/cut = warm grey #8A857C.
- Booths: small white tiles on the wire, 2 px border, logo `object-fit: contain`, label under; timer as a small mono pill ("0 s" … "30 s"), orange when it hits its limit; scissors as a near-black line glyph that turns orange when active.
- No red/green. "Bad" = grey + orange warning mark.

**Motion**
- Tiles pop in (spring). Wire draws with stroke-dashoffset, ease-in-out ~12 frames.
- Snip: scissors close (4 frames), the cut ends spring apart; the app-side half rotates down ~35° and settles with a damped swing (dangle).
- Replies travel eased; a dropped reply falls with gravity past the cut end and fades to grey.
- Everything exits with a fade on `out`.

**Sound:** `pop` on tiles, `tick` per timer step that lands on a spoken number, `stamp-thud` on the snip.

**Gotchas**
- Keep the drawing in fixed logical coordinates (972 px card space) and reuse the same geometry in every beat; only the state props change.
- Logos are official files from `icons/logos/`; never recolour them.
- Every trigger is a spoken-word frame (`at(phrase)`), never a typed time.

## Code

Saved: `components/code/PhoneLine/PhoneLine.tsx` (preview: `preview.png`). Import it, set props; extend with a new prop rather than copying. Brand values from `components/code/theme.ts`.

- Code props: AppTile {at,label,screen,dark,ring} · SrvTile {at,label,glow,dim,logos,children} · Wire {calls [{drawAt,pulseTo,silentAt,closeAt,snipAt,snipX,marks,greyAt}], travels [{t0,t1,dir,node,drop}]} · Booths {booths [{x,logo,lw,lh,label,at,limit,limitAt,timer,scissorsAt,scissorsDimAt,lockAt,badge,dimAt}]} · Tap {x,y,at} · GEO.
- First built and rendered in `system-design-of-ai/08-long-running-requests`.
