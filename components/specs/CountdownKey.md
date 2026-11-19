# CountdownKey

**Purpose:** explain a time-to-live: a key, a ring timer counting down, and what is left once it hits zero (here: `otp:42`, Redis TTL).

**Props:** `w`, `h`, `keyAt`, `ttlAt`, `codeAt`, `timerFrom`, `zeroAt`, `out`.

**Look**
- Key card (white, 2 px border, radius 14) with a key line icon and the key name in mono 700 56 px.
- "TTL = time to live" label, a 260 px ring (grey track, orange arc) with a big tabular-nums number, then a mono 34 px command line with the duration in orange.
- At zero the card goes grey (dim border and text, page background) but stays; a dim "still in memory" pill with an orange "!" pops beside it.

**Motion**
- Card and label pop in; the ring draws in 14 frames.
- Between `timerFrom` and `zeroAt` the arc depletes and the integer counts 60 → 0 on one eased curve.
- Grey-out is an 8-frame crossfade; the warning pill pops 6 frames later.

**Gotchas**
- Number is rounded, so it shows 0 only at the end; the arc is hidden at 0.
- Keep `zeroAt` > `timerFrom` or the count never moves.
- The card must stay on screen after zero: that is the point of the beat.
