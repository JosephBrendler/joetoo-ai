| Layer | Current implementation | Codex proposal | chatgpt recommendation | joe decision  |
|---|---|---|---|---|
| Recipe grammar | Common four/five-field format | Add sdl-freerdp|rdp | Approve for this increment, program=sdl-freerdp, mode=rdp |
| Offline validation | Common planner plus capability-specific validators | Add RDP target/settings validator | Approve | Approve |
| Geometry calculation | One common planner | Unchanged | Approve | Approve |
| Launch orchestration | Common -o, special VNC dispatch | Add RDP dispatch | Approve, minimize special cases | Approve; vnc-rdp normalization/consolidation is a future objective |
| Application ownership | Generic applications direct; VNC worker | Add RDP worker | Approve | Approve (but my understanding is this should replace three .py scripts that can be retained as work contributed to the poc but need not be deployed in production solution, is that correct?) |
| Authentication wait | Different bounded VNC/RDP timers | Proposed unbounded awaiting-viewer | Change to common five-minute default | Change to common five-minute default |
| Window identification | Generic, VNC and SDL-specific mechanisms | Reuse existing | Approve | Approve |
| Placement | Shared KWin geometry mechanism | Reuse existing | Approve | Approve |
| Cohort stacking/focus | Common initial-layout transaction | Reuse existing | Approve | Approve |
| Graphics backend | SDL explicit profile | Explicit per-host setting | Prefer validated auto plus overrides | Approve (but conditional: if easily accomplished, else defer to future and go with Explicit per-host setting) |
| Remote scaling | Client-specific; RDP smart sizing tested | Configurable RDP dimensions | Approve, define common scaling intent | Approve, define common scaling intent |
| Missing-window reservations | All historical records block original slot | Keep existing policy | Design verified release without losing history | Design verified release without losing history (but conditional: if easily accomplished, else keep existing policy) |
| Async multiple missions | Not implemented | Deferred Option D | Agree: Version 2 | Agree: Deferred Option D, Version 2 |

Notice what's not changing: the planner, the definition of slot, the KWin placement mechanism, and the cohort stacking model.

That means the future code can remain modular without becoming a new framework.
11. What I would settle before Codex starts implementation
My proposed near-term agreement is:

| Question | Recommended decision |
|---|---|---|
| Recipe | "sdl-freerdp\|rdp\|rdp://USER@HOST[:PORT]" | Agreed |
| RDP video backend | Validated automatic discovery, with explicit overrides | Agreed |
| Initial sizing | Configurable remote resolution and smart-sizing dimensions | Agreed |
| Final local geometry | Always owned by the existing planner | Agreed |
| Authentication wait | Five-minute configurable default for both RDP and VNC | Agreed |
| Authentication timeout | Terminate owned pending job, verify cleanup, report failure and continue | Agreed |
| Uncertain cleanup | Stop -o; do not start potentially conflicting work | Maybe disagree |
| Remote GDM login | After viewer registration/placement; does not block -o | Agreed |
| Persistent worker | Use Codex's design, consistent with existing TigerVNC | Agreed |
| Verified closed window | Retain history but make slot release possible | Agreed |
| Uncertain missing window | Continue reserving the slot | Agreed |
| Version 2 | Mission lifecycle, asynchronous launch, authentication-window roles, retries and out-of-order completion | Agreed |
