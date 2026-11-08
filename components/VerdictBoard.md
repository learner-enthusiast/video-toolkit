# VerdictBoard

**Purpose:** the verdict: JWT is everywhere (OIDC requires it); PASETO is the safer default for your own APIs.

**Props:** `at`, `out`, `signInAt`, `oidcAt`, `logos` ([{file, at}]), `oktaAt`, `oidcReqAt`, `decideAt`, `localAt`, `publicAt`, `rect`.

**Look**
- Generic sign-in button in brand style (white, 2 px border, brand radius) with the official Google "G" mark and the text "Sign in" (no Google button copy); arrow to chip "OIDC ID token = JWT".
- Logo row (official): Google, Microsoft Entra ID, AWS Cognito, Firebase, Auth0; each with a small tag "issues JWT".
- Okta logo centred, two arms: left "built JPaseto", right "issues JWTs", under it "OIDC requires it" (OpenID logo).
- Decision card: "One service → v4.local" and "Microservices → v4.public" in mono, both orange; title "safer default".

**Motion:** three stacked sections; each new one pushes the previous up and dims it; logos pop 5-frame stagger. Exit fade.
