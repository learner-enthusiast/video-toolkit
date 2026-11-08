# OtpSpam

**Purpose:** hook: a generic phone where "Resend OTP" is tapped 3 times and a toast says "Too many attempts"; each tap spawns a ₹ SMS-cost chip that flies off.

**Props:** `taps` (3 frames), `toastAt`, `chipsAt`, `rect` (card-local), `at`, `out`.

**Look**
- Generic phone: near-black 2 px bezel, status bar, plain app header "Verify your number", 6 OTP boxes, orange "Resend OTP" text button. No real bank or app branding.
- Toast: dark pill at the bottom of the screen with an orange warning mark.

**Motion**
- Tap = finger-dot ripple + button press scale 0.94.
- Chip "₹" pops from the button and flies up-right on an eased arc, fading.
- Toast springs up.

**Gotchas**
- Toast must be readable by output 0:01 (hook rule).
- Phone ≤ 55% of card width.
- Brand: no red/green; bad = dim grey #8A857C + orange warning mark, good = orange #E4572E (brand.md).
- All timings trigger on spoken-word frames (`at(phrase)`), never fixed times; every element has an exit (`out`).
