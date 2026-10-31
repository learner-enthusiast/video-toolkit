# HashMachine

**Purpose:** a hash function shown as a machine: a name goes in, a number comes out. Used singly ("same input, same output") or as a bank of k machines feeding a `BitRow`.

**Props:** `input` (text), `outputs` (one number per machine, each with `at`), `count` (1 or k), `rect`, `at`, `out`.

**Look**
- A rounded box (brand radius, 2 px border, off-white) with a small hopper slot on top and an output chute at the bottom. Label "hash" or "h1 / h2 / h3" in JetBrains Mono, dim.
- The input is a lowercase code chip (JetBrains Mono). Outputs are orange numbers in Inter 800.
- With k machines, they sit side by side above the bits they feed.

**Motion**
- The chip slides into the slot (ease-in-out), the machine gives a small shake (2 px, 4 frames), the number drops out of the chute with a spring.
- k machines: the chip splits into k copies that fan out to each slot, staggered 4 frames.
- Output numbers then travel along a short drawn arrow to their box in the `BitRow`, landing on the spoken number's frame.

**Gotchas**
- Repeating the same input must produce the identical output on screen (same number, same position), or the "deterministic" point is lost.
- Keep the machines narrow enough that the input chip (up to ~10 chars) fits above them at phone width.
