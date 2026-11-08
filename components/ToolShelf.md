# ToolShelf

**Purpose:** a shelf of container tools/engines that all speak OCI, with one OCI badge stamping onto every one at once, plus an optional terminal chip.

**Props:** `tools` (`[{logo | chip, label, sub, at}]`), `stampAt`, `terminal` (`{cmd, lines:[…], at, tickAt}`), `out`.

**Look**
- A shelf line (2 px `#1A1A1A`) with tool tiles standing on it: white tile, 2 px border, 14 px radius, official logo `object-fit: contain`, label in Inter 600, sub-label in Inter 400 warm grey ("daemonless · rootless").
- Tools without an official logo (nerdctl, BuildKit) use a text chip in JetBrains Mono 600 on a white pill.
- Terminal chip: dark card (`#0D0D0D`, white JetBrains Mono, no shadow), prompt `$` in orange; the pull log lines show digests in orange.
- OCI badge: the official OCI icon on a small white tile with an orange ring.

**Motion**
- Tiles pop in on their spoken names (spring, 5-frame stagger).
- Terminal types the command, then the log lines appear one per 4 frames; orange tick at the end.
- Stamp: all badges drop onto all tiles in the same frame (scale 1.6 → 1 spring, slight rotation −6° → 0).

**Gotchas**
- `podman pull docker.io/library/nginx` exact, lowercase.
