# DeliveryTracker

**Use:** the "no tracking vs live tracking" analogy for long-running jobs (agents, uploads, builds).

**Look:** a generic brand-styled phone (off-white screen, 2 px near-black frame, brand radius); no real app logos or screens.
- `variant="none"`: a parcel line icon and a spinner, "No tracking" label; dimmed warm grey with an orange warning mark.
- `variant="live"`: a vertical step list ("Order placed → Preparing → Out for delivery"), each step a circle that fills orange with a check, joined by a line that draws down to the next.
- Optional `call`: an incoming-call card sliding up from the bottom of the screen ("Rider", the question, two buttons; the affirmative is orange, the other outlined).

**Props:** `variant`, `steps: {label, at}[]`, `call?: {at, question, yes, no}`, `from`, `out`, `w`, `h`.

**Motion:** steps tick on the spoken word (spring pop + line draw ~8 frames); the spinner turns with an eased rotation; the call card is a spring slide-up with one soft ring wobble. Used inside `TwinPhones` for the side-by-side.
