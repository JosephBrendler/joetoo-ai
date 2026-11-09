# Step 1.5 — Active task dispatcher

**Task:** Step 1.5c.5d / Increment 3 — controlled placement of registered SDL RDP viewers.
**Repository:** `JosephBrendler/joetoo-ai`
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`
**Project:** `workspace/projects/joetoo-kwin/`
**Published baseline inspected for this handoff:** `ab444365f6a3e33626f5fe47cf17d92adb4355ce` (2026-11-08). The completed Increment 2 implementation code was recorded at `13e532c5d80c5beef69451f77d44dd4b36e1b50d`; later commits include documentation. Always inspect actual checkout, HEAD and dirty state; do not reset to either SHA.

**State at handoff:** Increment 1 native-Wayland registration **ACCEPTED**. Increment 2 native-X11 registration **ACCEPTED** for both explicit `auto` and `software` renderer modes, subject to the documented best-effort X11 role-identity limitation. The maintainer has selected **sequential, operator-interactive** launch orchestration as the first complete RDP/VNC workflow; concurrent prompt staging/queueing belongs to a later measured optimization, not to Increment 3. The current assignment is a bounded placement implementation, not further renderer research or architecture negotiation.

## Accepted evidence and boundaries

- The explicit native-X11 profile is `sdl-x11-a1c-v1`; its child-local renderer can be `auto` or `software`, with the shared configurable `rdp_x11_identity_settle_ms` of 500 ms in the accepted test. The broker registers a positively correlated exact UUID **without placement**. The previous OpenRC `XDG_SESSION_TYPE=tty` false guard was removed, while actual child/backend identity validation remains mandatory.
- On `gmki91` native Plasma X11, `auto` registration was demonstrated twice with before/after registry retention. On 2026-11-08, a managed `software` test against `opi6plus01.brendler` registered `win-001`, child PID `2640147`, KWin UUID `be27f183-c8a2-4772-a802-1cc5e2fb2f30`, with `placement=not_requested`. The live registry reported `presence=present`, one successful registration and an idle placement transaction. After titlebar-X closure, the **same** managed ID and UUID remained with `presence=missing`, synchronized observation, `succeeded=1`, `failed=0`, `ambiguous=0`, `timeout=0`, and `viewer_cleanup_uncertain=false`. The foreground launcher's final `child_exit` output was not retained; do not invent it or mistake that omission for an unsuccessful UUID lifecycle result.
- The last full maintainer-provided regression for this code path: **644 Python tests passed, 145 JavaScript tests passed**, with installation/check/introspection observations. These results predate the next Increment 3 implementation; they are **not** tests of that new feature.
- X11 UUID dwell is a pragmatic heuristic, **not proof** of completed renderer handover. A marked temporary window surviving 600 ms can be registered at a 500 ms threshold; if replaced, never silently adopt the successor. Preserve this limitation for both renderer settings.
- Detailed records: [Increment 2 native evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md), [Increment 3 strategy decision](step1.5c5d-increment3-strategy-decision.md), [authentication/serial-workflow decision](increment2-deferred-authentication-workflow-section.md), [implementation scope](Step1.5c5_implementation_scope.md), [architecture](../ARCHITECTURE.md), and [task history](README.md).

## Next actor and approved design

**Next implementation task: Codex, when the maintainer explicitly dispatches the accompanying [Codex Increment 3 assignment](Codex-Increment3-RDP-Placement.md).** Increment 3 establishes **reliable operator-controlled placement** of an already registered, live SDL FreeRDP viewer on the original exact KWin UUID. It is a bounded code-and-headless-tests task. The new operator action must work while the original SDL launcher continues supervising its viewer, require independent explicit operator confirmation, and honor existing broker/resident transaction, source, owner, slot, geometry and UUID checks. No automatic placement on registration, no inference of completed NLA/GDM login, no prompt relocation, no refocus/re-stack of unrelated windows. Support accepted native-Wayland and explicit legacy native-X11 registration paths.

The maintainer has **already accepted the architectural sequence**; Codex should not repeat the strategy-selection exercise. Product decisions (as opposed to tested implementation claims):

1. **Increment 3:** positively registered RDP viewer → exact-UUID operator-controlled placement; code + focused headless tests, later maintainer-native placement test.
2. **Increment 4:** integrate RDP into the existing configured `-o` **sequential** mixed Konsole/Dolphin/TigerVNC/RDP launch plan; wait for human authentication rather than implementing concurrent prompt scheduling.
3. **Increment 5:** security and RDP-native/regression closure, including trusted TLS/NLA.
4. **Step 1.5d:** broader integrated X11/Wayland regression and `-L`/`-l` features.
5. **Phase 2:** *optional, measured* launch-throughput optimization, including staging/queuing remote prompts if justified.

**Correctness requirement for Increment 4, already decided:** an owned RDP/VNC client deliberately waiting for interactive credentials must **not** be killed simply because a fixed automated human-wait deadline expires. Genuine child/transport failure, operator cancellation, and loss of verified ownership remain distinct from human inactivity. Retain bounded deadlines for D-Bus calls, mechanical UUID-correlation/placement and cleanup. Existing development RDP/VNC supervisors currently contain deadlines that can expire during human authentication (`rdp_registration_timeout_ms` 120 s; VNC SSH startup 10 s and viewer readiness 120 s): this is a **known unimplemented requirement**, not a reason to invalidate Increment 2 and not permission to change unrelated supervisors in Increment 3. Server-side timeouts are independent and cannot be guaranteed away.

## Hard stops / deliverable

The Codex assignment authorizes only the described **local candidate implementation and headless tests after the maintainer invokes it**. It does **not** authorize host-native RDP, installation, restart, service/desktop actions, remote connection, TLS/NLA changes, upstream FreeRDP/KWin patches, client secret handling, protected-repository edits, commit/push/PR/merge, or changes to project architecture/task documents. If the exact registered UUID cannot be safely placed using a narrow additive interface, stop and report the blocker rather than weakening ownership checks.

Return the complete diff, touched paths, exact tests/results, residual risks and smallest proposed maintainer-native acceptance procedure. Publication/native execution remain separate maintainer gates. `HANDOFF.md` dispatches the current task; it is **not** an instruction to re-open completed design work.
