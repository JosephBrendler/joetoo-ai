# Step 1.5 — Active task dispatch

**Active task:** Step **1.5c.5d, Increment 1** — native-Wayland SDL FreeRDP registration of the exact KWin viewer UUID, **without placement**.

**Phase:** Four-method SDL development interface and ten-component installer implemented; native Begin/Cancel smoke **ACCEPTED** (2026-11-06); persistent direct-child SDL development launcher implemented and headlessly validated. **First positive native-Wayland SDL registration PASS; independent Gate A live UUID/backend/FD verification PASS; native NLA-dialog cancellation PASS; controlled Gate B1 refused connection PASS on q552u01.** **Gate B2 Ctrl+C pending-registration cancellation PASS** on q552u01. Coexistence/isolation and full Increment 1 acceptance remain **pending**.

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`

**Current published checkpoint:** `5244949` — maintainer-published task branch, fast-forward synchronized on `q552u01` from `2bb9c74`. Verify the current HEAD, working tree and origin before subsequent work. No implementation merge into `main`.

## Authoritative references

| Purpose | Document |
| --- | --- |
| Governing instructions | Repository-root, workspace and project `AGENTS.md`; `workspace/README.md` |
| Product architecture | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Requirements and incremental gates | [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), §5A |
| Historical task record | [Task README](README.md) |
| Remote-desktop feasibility research | [Remote-desktop research](README_remote_desktop_research.md) |
| SDL interface, development launcher and proposed native procedure | [SDL interface contract](step1.5c5d-sdl-interface-contract.md), §§1–7 |
| **Actual native positive registration and post-exit findings** | [2026-11-06 native-Wayland SDL evidence](step1.5c5d-native-wayland-sdl-registration-evidence-2026-11-06.md) |
| **Independent live Gate A UUID/backend and close-log evidence** | [2026-11-06 Gate A identity evidence](step1.5c5d-native-wayland-sdl-gateA-identity-evidence-2026-11-06.md) |
| **Native Gate B1 refused-endpoint evidence** | [2026-11-06 Gate B1 negative test](step1.5c5d-native-wayland-sdl-gateB1-refused-connection-evidence-2026-11-06.md) |

## Current authority and boundaries

**Previously accepted:** Maintainer accepted the q552u01 native Begin/Cancel smoke gate on 2026-11-06. Its two terminal `failed` records were deliberate cancellations, not failures of the smoke test.

**Previously authorized and implemented:** Bounded Codex headless implementation of a persistent development-only SDL launcher, using Begin → direct child → Bind → Poll/Cancel on one local D-Bus connection. Codex reported 178 focused, 613 full Python and 99 JavaScript passes. Maintainer subsequently reproduced the 178/613/99 passes on both gmki91 and q552u01.

**Maintainer-operated native tests:** (1) Initial positive native registration with usable Ubuntu GNOME desktop — PASS; (2) NLA-dialog cancellation before authentication — PASS, no registration or leaked child; (3) independent live Gate A KWin UUID / process / stdout FD / actual `wayland` log readback — PASS; (4) Gate B1 refused local endpoint — PASS, no false registration or leaked child; (5) Gate B2 Ctrl+C during NLA prompt — PASS, owner cancellation and child cleanup. These **record actions already performed**, not blanket approval for further native tests or Codex network execution.

**Next authorized actor:** Codex may review source, the new native evidence record and existing tests, and propose the next small acceptance/diagnostic gate **without native execution or repository modifications**. Any actual code change, new native operation or broader test matrix requires separate maintainer direction.

**Reserved decisions:** Unapproved new process-provenance mechanism or public signature; production TLS/NLA/certificate policy; further native SDL/RDP runs; X11 role identity; placement/desktop/geometry/stack/focus changes; configured `-o` recipes; later increments; production deployment and publication into `main`.

**Invariants:** Exact positively verified launch-owned native-Wayland UUID only; fail closed on ambiguity/lost evidence; no registration-driven placement; preserve generic and TigerVNC behavior. Do not equate successful local window registration with remotely authenticated/secure transport.

**Stop/escalate:** Missing or contradictory process/log/UUID proof, unexpected source/owner changes, regressions, unexpected placement, leaked children, unsafe certificate/security exceptions, or actions outside the stated gate. Exit 131 is documented separately and not automatically a registration failure.

## Latest result — maintainer native verification, 2026-11-06

**Sync/install/regressions:** q552u01 fast-forwarded `2bb9c74 → 5244949`. Both gmki91 and q552u01 independently passed **178 focused Python, 613 full Python and 99 JavaScript** tests. q552u01 installer updated/checked ten managed files, OpenRC service started, and all four SDL D-Bus method signatures appeared. The maintainer's restart wrapper now reported successful D-Bus introspection (prior session-address failure no longer reproduced in this run).

**First native SDL registration — positive PASS:**

- Local non-root Wayland launcher targeted `raspiubuntu401`, user `joe`, default RDP port 3389, intended desktop 1/slot 1 and registration timeout 300000 ms.
- Direct SDL child PID `863250`; request `099e8607f5b6481a8701d87288c70318`; returned `state="registered"`, `reason="registered"`, managed ID `win-001`, exact UUID `3d8dd95f-2fbb-4aef-870d-c6dba31dd16f`, `placement="not_requested"`, `remote_session="unverified"`.
- Maintainer screenshot shows a usable GNOME/Ubuntu desktop inside the SDL FreeRDP viewer, including a working remote terminal; visible title marker agrees with the broker's later stored caption.
- Launcher ultimately printed `child_exit=2`; this is **not** reclassified as an established remote-security or exit-cause result without log/exit-path verification.

**Post-exit broker verification — PASS:** `RegistryStatus` synchronized, `request_count=1`, `succeeded=1`, `pending=running=0`, `placement_transaction=IDLE`, `managed_count=1`. `ListManaged` and `GetManaged win-001` retain the exact UUID/request/child identity while explicitly reporting `presence="missing"`. This is historical managed registration, **not** a live viewer. The registry field `connection="not_attempted"` is not a measurement of the visually working remote session.

**Native NLA cancellation — PASS:** Under a fresh broker baseline, `raspiubuntu401` displayed its NLA dialog; the maintainer clicked Cancel without submitting credentials. Launcher PID `884517` exited; its terminal result was `failed` / `child_identity_rejected` and launcher exit 1, with no registered viewer or lingering child, `pending=running=0`, synchronized source and placement IDLE. That run did **not** exercise preservation of the earlier `win-001` record, because the service had been restarted before the baseline.

**Independent Gate A identity verification — PASS:** On q552u01, a second positive SDL launch targeted `raspiubuntu401.brendler`, desktop 1/slot 2, child PID `914978`, request `5976103a7320411d902286375414ab96`; broker registered `win-001` / UUID `0ce195e1-f284-40d9-8e25-cef7b1a4d1a1`. Live process executable `/usr/bin/sdl-freerdp`, private stdout FD, PID/application/title marker, `BackendEvidence` returning `wayland`, and KWin Debug Console `{0ce195e1-f284-40d9-8e25-cef7b1a4d1a1}` all agreed. KWin and broker geometry agreed at `448,119 1024×796`. Registration was `not_requested` for placement; broker placement remained IDLE. After exit, child absent, observation synchronized, `succeeded=1`, `pending=running=0`, retained managed entry marked `presence=missing`.

**Native Gate B1 connection refused — PASS:** On local q552u01 Wayland, preflight verified that `127.0.0.1:65001` refused TCP connections. Launcher spawned child `927671`, request `5db38e1e418d42d2acd095f4c4f25017` (desktop 1/slot 1, timeout 15000 ms), then returned terminal `failed` / `child_identity_rejected`, launcher exit 1. Post-test: managed count zero, one failed request, no pending/running requests, child absent, observation synchronized with unchanged source/revision, placement IDLE, no cleanup uncertainty. See [Gate B1 evidence](step1.5c5d-native-wayland-sdl-gateB1-refused-connection-evidence-2026-11-06.md). B1 does **not** require repetition merely because the broker was subsequently restarted.

**Native Gate B2 Ctrl+C — PASS:** In a local q552u01 Plasma Wayland Konsole, the launcher targeted `raspiubuntu401.brendler:3389` (desktop 1/slot 2), spawning SDL child PID `928382`, request `281720675dc34bc7a6c3046880b4c515`. While the NLA dialog was displayed, the maintainer pressed Ctrl+C without entering credentials; the dialog disappeared approximately **1.5–2 seconds** later. Launcher reported terminal `state=failed`, `reason=cancelled`, followed by `Operator cancellation` and exit status 1 (expected for this negative test). Broker after-test: `failed=1`, `pending=running=0`, `managed_count=0`, `ListManaged` empty; observation `synchronized=true` with unchanged source `1794025502561-e37c3mhdkzoo` (revision 12 → 16); placement `IDLE`; `pgrep` found no remaining `sdl-freerdp` child. **No repeat required.** The broker restart occurred **before the B2 baseline**; it prevents claims of *cross-test* registry continuity from B1 through B2, but does not invalidate either independent test.

**FreeRDP exit 131 — investigated:** Private log shows `SDL_EVENT_WINDOW_CLOSE_REQUESTED` and “Window closed, terminating RDP session...” immediately before `ERRCONNECT_CONNECT_CANCELLED` and network-disconnect reporting at 22:42. Source-level exit enum labels 131 `CONN_FAILED`, but the observed local close request strongly suggests closure-triggered cancellation. Do not call 131 a successful transport exit, nor misclassify the earlier positive UUID registration as failed. Raw private log remains outside Git.

**Detailed evidence:** [First positive native SDL registration](step1.5c5d-native-wayland-sdl-registration-evidence-2026-11-06.md); [Gate A — live UUID/backend/FD and close-log evidence](step1.5c5d-native-wayland-sdl-gateA-identity-evidence-2026-11-06.md); [Gate B1 — refused connection](step1.5c5d-native-wayland-sdl-gateB1-refused-connection-evidence-2026-11-06.md). **Gate B2** verified results are recorded above from the maintainer's terminal transcript; no separate B2 report is asserted. Gate A screenshot: `screenshots/19-sdl-native-wayland-kwin-uuid-gateA-2026-11-06.png`. First-positive screenshot: `screenshots/18-sdl-native-wayland-viewer-2026-11-06.png`. Raw FreeRDP logs remain private outside Git.

**Still outstanding:** Independently test unrelated-viewer coexistence and prior-record isolation with an explicitly declared no-restart prerequisite **before any commands**; consider wrong-password behavior only if separately justified and authorized, respecting lockout policy; review full headless coverage and native no-placement invariants. Full Increment 1 not yet accepted. PKI/client-certificate checks, X11 role identity, placement and configured production RDP are separate policy/increment gates.

## Next actor and decision

**Next actor — maintainer review:** Preserve Gate A/B1/B2 completed PASS evidence and plan a single bounded Gate C unrelated-viewer coexistence/prior-record isolation test. If Codex is tasked, its authority is **read-only analysis** of evidence, source and tests; no native operations, source changes, install/restart, commit or push. Do not broaden the test matrix unilaterally.

**Next maintainer decision:** Separately authorize a controlled Gate C coexistence/isolation test and specify its baseline and expected record preservation. **Any requirement not to restart or preserve state across runs must appear at the top of the procedure before Step 1**, not after the commands. The earlier restart between B1 and B2 does not require either test to be repeated. **Increment 1 remains open** until accepted by the maintainer. No automatic progression to Increment 2 or placement.

---

**Maintenance convention:** Keep HANDOFF to the current task, current authority, latest result and next actor. Preserve detailed technical evidence in focused reports and durable accepted milestones in the task README; do not recreate the historical iteration table.

