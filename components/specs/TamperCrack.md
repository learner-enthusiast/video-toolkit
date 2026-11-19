# TamperCrack

**Purpose:** editing the payload breaks the signature, then JWE is the encrypted version.

**Props:** `editAt` (`"role":"user"` → `"admin"`), `crackAt`, `errorAt` ("401 Invalid signature"), `jweAt` (sealed envelope "JWE = encrypted"), `rect`, `out`.

**Look**
- Reuses DecoderReveal's payload rows and TokenAnatomy's signature card style.
- Edit: `user` gets a caret and is retyped to `admin` (orange text).
- Crack: a jagged SVG crack across the signature card; the card dims to warm grey with an orange WarnMark and a near-black chip "401 Invalid signature" in mono.
- JWE: a sealed envelope line icon with an orange wax seal, label "JWE = encrypted".

**Motion**
- Typing 2 chars/frame; crack line draws (stroke 8 frames) with a 2 px shake.
- Envelope slides up with a spring on `jweAt`; previous content shrinks/dims.
- Exit: fade 8 frames.

**Gotchas:** no red; the error state is dim grey + orange WarnMark.
