# PhoneMockup

**Purpose:** a generic shopping-app screen showing what the customer sees (product + price), to make "users see the old price" concrete.

**Props:** `product` (ProductCard data), `price` (PriceTag), `clock` (status-bar time text), `refreshAt` (list of {at, price}), `rect`, `at`, `out`.

**Look**
- Rounded phone frame (near-black bezel, 2 px), status bar with the clock, a plain brand-styled app header ("Diwali Sale"), the product image area and the price. No real app logos or UI.

**Motion**
- Enters with a spring slide-up. `refreshAt`: a small pull-to-refresh spinner, then the price swaps (PriceTag flip).

**Gotchas**
- Price ≥ 56 px inside the phone so it reads at phone width; keep the phone ≤ 45% of the card width when two sit side by side.
