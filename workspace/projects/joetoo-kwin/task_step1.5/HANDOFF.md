# Step 1.5 — Active task dispatcher

**Task:** Step 1.5c.5d / Increment 3 — diagnose native-Wayland late movement; Option C serial RDP placement consolidation follows separate review.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Relevant source commits:** `e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1` (Increment 3 placement implementation), `5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c` (sequential registration fix), `0bea3e4` (placement diagnostics), `0c9aad7220bc1ea87493c6fdd0ab92dce0734c5b` (KWin caller `/proc/PID/exe` fix). Inspect actual checkout/HEAD/dirty state; do not reset or force a stale checkout.

**State as of 2026-11-09:** Increment 1 native-Wayland and Increment 2 native-X11 RDP registration-only are **ACCEPTED**. Native X11 `software`/`auto` placement and sequential A/B registration remain accepted; the historical false `Broker is busy` is **CLOSED**. On `q552u01` at `0c9aad7`, the maintainer installed the corrected broker and ran **744 Python / 158 JavaScript tests**, installer checks and D-Bus introspection successfully. Native Wayland registered the intended persistent viewer with exact UUID but controlled placement returned failure after about 15 seconds; subsequent visual observation found movement occurring after the terminal failure. **Increment 3 remains OPEN**. No production serial configured `-o` RDP workflow or concurrent pending authentication is accepted.

**Primary evidence:** [native X11 sequential A/B closeout (2026-11-09)](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md), [earlier X11 `software`/`auto` placement and historical pre-fix Busy transcript](step1.5c5d-increment3-native-x11-placement-2026-11-09.md), [native Wayland Increment 1 registration acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md). Also: [task README](README.md), [engineering scope](Step1.5c5_implementation_scope.md), [settled serial-workflow decision](step1.5c5d-increment3-strategy-decision.md).

## Closed X11 defect — native acceptance summary

On `gmki91` kernel 6.18.62, after publishing `5a2e152` and restarting/installing the service (691 Python / 158 JS PASS), the maintainer:
- Registered viewer **A**, `software`, `win-001`, desktop 1/slot 2, UUID `2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2`; explicitly placed it at (0,0) (`reason=verified`), closed it, and observed `presence=missing` with UUID retained and `placement=succeeded`.
- **Without restarting `joetoo-kwind`**, registered viewer **B**, `auto`, `win-002`, desktop 1/slot 3, UUID `5a893ce2-5cec-4b20-b7d0-01626385df42`, while A's previous `placement_transaction={state:"OK",id:"c32cddcc7d6848759890ad9210047f5e"}` remained. B was intentionally **not placed** (`placement=not_requested`).
- Closed B: both records were `missing` with original distinct UUIDs, two successful and zero failed/ambiguous/timed-out registrations, synchronized observation and no viewer-cleanup uncertainty.

**Sequential-launch defect CLOSED.** Retain the old `Broker is busy` evidence as a historical pre-fix finding, not a current blocker.

## Next active task — diagnostic-only late-placement trace

**Current authorization boundary:** The maintainer may task Codex to add focused diagnostic instrumentation and headless tests for one controlled native-Wayland placement failure. No behavior change, refactor, timeout adjustment, service installation, viewer launch, native execution, commit or push is authorized by this handoff alone. Review the resulting diff before any maintainer-operated native trial.

The next trace must distinguish pending claim, accepted `TakeSdlPlacement`, KWin resident UUID selection and geometry assignment, accepted/rejected `Complete(VERIFY/ERROR)`, entry into `VERIFYING`, exact failing guard versus deadline expiry, geometry/desktop non-convergence, and **post-terminal geometry changes** seen through the existing observation stream. Record a pre-request frame and post-terminal observations for the original UUID, with monotonic relative timestamps; use fixed stages and bounded, sanitized values. No private RDP logs, credentials, captions, remote arguments or general high-volume logging; do not add a new window observer or a movement-repair loop.

**Maintainer-only follow-up:** After reviewing the diagnostic patch, decide separately whether to install it, re-establish the private OpenRC stderr sink (the installer replaces the override), and perform **one** native placement attempt on `q552u01`. Capture the original UUID, before/after frame, transaction trace and any late movement, with no retry on failure. Preserve the running viewer and broker state until evidence has been collected; avoid restarting either during a transaction.

**Then, and only after review:** authorize Option C targeted consolidation, using the existing registered RDP UUID, the proven KWin managed-placement machinery, one coherent deadline/terminal outcome and client-specific identity safeguards. Do not start Option D or modify the accepted TigerVNC lifecycle in this increment.

## Outstanding geometry question

Both earlier X11 renderer tests requested `800×600`, but the observed decorated KWin frame later measured `1032×804`, even though target positions/desktops were correct. On native Wayland, the latest viewer (`win-001`, UUID `531b79e5-6baa-4e52-b300-193283e83f4c`) requested `(120,90) 800×600` and was subsequently observed at `(120,90) 1024×796` with synchronized observation and failed placement. The maintainer later reported apparent movement **well after** a terminal failure on repeated tests with different requested coordinates; its timing and causal mechanism remain unverified. Do not infer movement from coincident coordinates or conflate client-area with decorated KWin frame geometry. Resolve the late-effect/terminal-state discrepancy before selecting a geometry policy. **No endless resizing, focus or stacking repair loop.**

## Settled later roadmap — not current implementation

**Option C — next implementation objective, separately authorized:** Consolidate serial RDP placement around the existing KWin managed placement lifecycle, retaining accepted SDL FreeRDP positive viewer registration. Current single-flight registration is sufficient for serial operation. Preserve per-launch reservation, exact UUID association, original `-o` placement intent, fail-closed ownership and independent remote-session outcome. For a confirmed configured `-o` launch, readiness of the correct viewer triggers placement; a second operator release is a standalone POC test gate, not the desired configured workflow. Keep working TigerVNC unchanged.

**Increment 4:** integrate the existing `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]` grammar, derived slots/geometry, confirmed serial mixed Konsole/Dolphin/TigerVNC/RDP `-o` launches, and human-interactive NLA/VNC/SSH prompts. Genuine human credential wait must **not terminate a client/tunnel solely on an arbitrary automated timeout**; mechanical identity, placement and cleanup deadlines remain bounded. **Increment 5:** RDP TLS/NLA/security and native regression. **Step 1.5d:** broader regression and `-L`/`-l`.

**Option D — future architectural target, NOT authorized now:** independently keyed multiple pending remote launches, out-of-order human authentication completion mapped to original reservations, and common RDP/VNC viewer-readiness and placement lifecycle management. Preserve each client's separate viewer-role selector; evaluate possible Remmina integration separately. Redesign broker per-launch state when concurrency is authorized, rather than embedding authentication-completion order into identity. Do not modify TigerVNC or implement a generic plugin framework during Option C.

**Hard stops:** No active-window, title/class/PID-only replacement for exact UUID; no placement from registration-only POC, no credential injection, TLS bypass or false remote login claims. Confirmed configured `-o` intent may later authorize placement after positive viewer registration; that integration is not implemented yet. No automatic change to unrelated config, source history or local workstation state. Maintainer authorizes any future code change, publication or native operation separately.
