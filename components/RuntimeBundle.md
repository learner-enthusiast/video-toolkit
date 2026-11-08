# RuntimeBundle

**Purpose:** the OCI runtime spec: an image unpacks into a bundle (rootfs + config.json), and a low-level runtime (runc) reads it, sets up the process, starts it, and exits while the process keeps running.

**Props:** `bundleAt`, `configLines` (3 strings), `steps` (`[{text, at}]`), `exitAt`, `out`.

**Look**
- Folder card `bundle/` (tab-shaped top, 2 px border) with two entries: `rootfs/` (folder icon) and `config.json` (file icon) that opens into a 3-line code block in JetBrains Mono 500 on white: `"args": ["node","index.js"]`, `"namespaces"`, `"linux.resources.memory"`.
- runc chip: official runc logo + `runc` mono label + small OCI badge.
- Steps as a vertical checklist: "create namespaces" → "apply cgroups" → "start process"; the active one on an orange block.
- Process box `node index.js` with a soft pulsing orange dot (it's running).

**Motion**
- Layers (tarballs) slide into the folder and the folder springs open.
- The runc chip slides down the checklist, each step lighting on its spoken verb; on "exits" the chip slides out right and fades, while the process box stays and keeps pulsing.

**Gotchas**
- Hand off into ContainerStack: the runc chip's final position is the `runc` layer slot of ContainerStack, so the stack can appear around it without a jump.
