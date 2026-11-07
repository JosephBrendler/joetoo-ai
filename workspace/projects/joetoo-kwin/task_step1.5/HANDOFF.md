# Step 1.5 — Active task dispatch

**Active task:** Step **1.5c.5d, Increment 1** — native-Wayland SDL FreeRDP registration of the exact KWin viewer UUID, **without placement**.

**Phase:** Four-method SDL development interface and ten-component installer implemented; native Begin/Cancel smoke **ACCEPTED** (2026-11-06); persistent direct-child SDL development launcher implemented and headlessly validated. **First positive native-Wayland SDL registration and post-exit registry review PASS on q552u01.** Remaining negative/lifecycle verification and complete Increment 1 acceptance are **pending**.

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

## Current authority and boundaries

**Previously accepted:** Maintainer accepted the q552u01 native Begin/Cancel smoke gate on 2026-11-06. Its two terminal `failed` records were deliberate cancellations, not failures of the smoke test.

**Previously authorized and implemented:** Bounded Codex headless implementation of a persistent development-only SDL launcher, using Begin → direct child → Bind → Poll/Cancel on one local D-Bus connection. Codex reported 178 focused, 613 full Python and 99 JavaScript passes. Maintainer subsequently reproduced the 178/613/99 passes on both gmki91 and q552u01.

**Maintainer-operated first positive native test:** The maintainer executed the direct SDL launcher from a local non-root Wayland Konsole on q552u01 and observed successful positive registration and a usable Ubuntu graphical session. This **records an action already performed**, not a blanket authorization for additional native tests or for Codex to connect remotely.

**Next authorized actor:** Codex may review source, the new native evidence record and existing tests, and propose the next small acceptance/diagnostic gate **without native execution or repository modifications**. Any actual code change, new native operation or broader test matrix requires separate maintainer direction.

**Reserved decisions:** Unapproved new process-provenance mechanism or public signature; production TLS/NLA/certificate policy; further native SDL/RDP runs; X11 role identity; placement/desktop/geometry/stack/focus changes; configured `-o` recipes; later increments; production deployment and publication into `main`.

**Invariants:** Exact positively verified launch-owned native-Wayland UUID only; fail closed on ambiguity/lost evidence; no registration-driven placement; preserve generic and TigerVNC behavior. Do not equate successful local window registration with remotely authenticated/secure transport.

**Stop/escalate:** Missing or contradictory process/log/UUID proof, unexpected source/owner changes, unresolved backend evidence, regressions, unknown child exit cause affecting acceptance, or actions outside the stated gate.

## Latest result — maintainer native verification, 2026-11-06

**Sync/install/regressions:** q552u01 fast-forwarded `2bb9c74 → 5244949`. Both gmki91 and q552u01 independently passed **178 focused Python, 613 full Python and 99 JavaScript** tests. q552u01 installer updated/checked ten managed files, OpenRC service started, and all four SDL D-Bus method signatures appeared. The maintainer's restart wrapper now reported successful D-Bus introspection (prior session-address failure no longer reproduced in this run).

**First native SDL registration — positive PASS:**

- Local non-root Wayland launcher targeted `raspiubuntu401`, user `joe`, default RDP port 3389, intended desktop 1/slot 1 and registration timeout 300000 ms.
- Direct SDL child PID `863250`; request `099e8607f5b6481a8701d87288c70318`; returned `state="registered"`, `reason="registered"`, managed ID `win-001`, exact UUID `3d8dd95f-2fbb-4aef-870d-c6dba31dd16f`, `placement="not_requested"`, `remote_session="unverified"`.
- Maintainer screenshot shows a usable GNOME/Ubuntu desktop inside the SDL FreeRDP viewer, including a working remote terminal; visible title marker agrees with the broker's later stored caption.
- Launcher ultimately printed `child_exit=2`; this is **not** reclassified as an established remote-security or exit-cause result without log/exit-path verification.

**Post-exit broker verification — PASS:** `RegistryStatus` synchronized, `request_count=1`, `succeeded=1`, `pending=running=0`, `placement_transaction=IDLE`, `managed_count=1`. `ListManaged` and `GetManaged win-001` retain the exact UUID/request/child identity while explicitly reporting `presence="missing"`. This is historical managed registration, **not** a live viewer. The registry field `connection="not_attempted"` is not a measurement of the visually working remote session.

**Still outstanding:** Independent live KWin Debug Console UUID comparison; direct Terminal-B PID/FD/backend readback while the viewer lives; independent pre/post geometry/stack/focus comparison; precise `child_exit=2` interpretation; negative/cancel/refused/competing viewer tests and bounded cleanup evidence; production connection/security policy. No placement, X11 or configured RDP acceptance is implied.

**Detailed evidence:** [2026-11-06 native SDL registration report](step1.5c5d-native-wayland-sdl-registration-evidence-2026-11-06.md), including exact JSON returned by the launcher, `RegistryStatus`, `ListManaged`, `GetManaged` and a screenshot at `screenshots/18-sdl-native-wayland-viewer-2026-11-06.png`. Retained private SDL log directory is not committed to Git.

## Next actor and decision

**Codex — review only:** Inspect the evidence report and current source, reconcile the positive result with the published contract, examine the child-exit/cleanup semantics and propose one bounded next native diagnostic/negative test. Report whether the evidence supports the exact-UUID registration claim and explicitly identify any unproven parts. Do not run RDP, modify implementation, commit or push.

**Next maintainer decision:** Select/authorize the next bounded native diagnostic or negative case, after reviewing Codex's analysis. **Increment 1 remains open** until its remaining approved acceptance matrix is satisfied. No automatic progression to Increment 2 or placement.

---

**Maintenance convention:** Keep HANDOFF to the current task, current authority, latest result and next actor. Preserve detailed technical evidence in focused reports and durable accepted milestones in the task README; do not recreate the historical iteration table.

