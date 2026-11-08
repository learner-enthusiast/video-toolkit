# EventStream

**Use:** an agent sending typed events to a frontend (AG-UI, SSE, webhooks). The same Agent → App layout is reused across scenes, so the viewer learns it once.

**Layout (inside the grid card, 9:16 SPLIT)**
- Top: "Agent" box (white card, 2 px border, brand radius), centred over the pipe.
- Middle: a vertical pipe (two 2 px rails, ~70 px apart) from the Agent box down to the App.
- Bottom left: a generic App frame (phone or browser, brand-styled, no real product UI). Its screen has a message area, a status line and a slot for a tool card.
- Right column: the event log. Each landed event is a code chip (JetBrains Mono, near-black on white, 2 px border); the newest is orange, older ones settle to white.

**Props**
- `events: { name: string; at: number; payload?: string }[]`: one chip per spoken event, `at` = output frame of the word.
- `app: { text?: {at,text}[]; status?: {at,text}[]; toolCard?: {at,label} }`: how the screen reacts.
- `mini?: boolean`: a smaller version for an outro or recap.
- `from`, `out` for the entrance and exit.

**Motion**
- A chip is an orange packet that leaves the Agent box ~10 frames before `at`, runs down the pipe on an ease-in-out curve and lands in the log ON `at` (spring pop, one soft tick SFX on key events only).
- App reactions: text types in per `TEXT_MESSAGE_CONTENT`; the status line cross-fades with an upward slide; the tool card springs in.
- Everything exits with a short eased fade + slide when the scene ends.

**Rules**
- Event names use the exact protocol spelling (`RUN_STARTED`, `TOOL_CALL_ARGS`…). Minimum chip text 34 px.
- Keep the Agent box, pipe and App in the same place in every scene that uses them.
- Wildcard names (`THINKING_*`) are shown as written.
