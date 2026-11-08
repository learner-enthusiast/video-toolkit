# RaceTimeline

**Purpose:** a race between two requests on a time ruler (slow reader vs update), showing a stale write-back and how a lease rejects it.

**Props:** `ruler` (start/end labels, e.g. 11:59 → 12:00), `lanes` (id, label, avatar), `steps` (lane, text, x on the ruler, `at`, kind = op | wait | reject), `tokens` (LeaseToken events), `rect`, `out`.

**Look**
- Two horizontal lanes with labels at the left ("Ravi's request", "Price update"), a clock ruler on top with tick marks and JetBrains Mono time labels.
- Steps are small mono pills (`GET`, `miss`, `DB read ₹79,999`, `SET ₹79,999`) dropped onto the lane at their time; `wait` is an hourglass with a stretched bar.

**Motion**
- Each step drops onto its lane with a spring at its word; the hourglass bar grows across the ruler while it waits.
- Replays (the lease version) reset the lanes with a quick fade and rebuild faster.
- Reject: the arrow hits the target and bounces back with a spring, then a **Rejected** stamp.

**Gotchas**
- Keep ruler positions the same between the stale run and the lease replay so the viewer can compare them.
