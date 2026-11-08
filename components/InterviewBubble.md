# InterviewBubble

**Purpose:** an interview exchange as a chat card: the interviewer's question, a wrong answer that gets stamped, and later the corrected answer typing in.

**Props:** `rect` (card-local or frame), `quote`, `state` ('question' | 'wrong' | 'corrected'), `stampAt`, `strikeAt`, `typeAt`, `answer` (list of `{text, hi}` runs), `at`, `out`.

**Look**
- Left: a small "Interviewer" avatar (generic line-icon person in a 2 px circle, label in Inter 600, dim grey). Right of it: a white speech bubble (2 px near-black border, brand radius, soft shadow, tail toward the avatar).
- Quote in Inter 800, large (≥ 64 px in 9:16), near-black, inside curly quotes.
- Wrong state: an orange `Stamp` reading "WRONG" slams across the bubble; the quote dims to warm grey. Grey + orange only, never red.
- Corrected state: the old quote stays (grey) with an orange strike drawn left→right; a second white card types in below, key words on the orange block (white text).

**Motion**
- Bubble springs in (scale .96→1 + rise), or is already on screen at frame 0 when it opens the video.
- Stamp: `Stamp` motion (1.6→1 stiff spring, one shake) on the spoken word "wrong".
- Typing: ~2 characters per frame with a blinking caret (frame-based, not CSS); a highlighted run's orange block springs in when its first letter appears.

**Gotchas**
- Must read on frame 0 in a muted autoplay: no fade-in when it is the hook.
- Never over the face: in FULL it sits on the wall above my head (y ≈ 96–620).
- The typed answer must finish no later than the last spoken word it shows.
