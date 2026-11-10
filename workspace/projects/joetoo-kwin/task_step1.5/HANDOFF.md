# Step 1.5 — Active task dispatcher

**Task:** Step 1.5c.5d / Increment 3 — Option C: consolidate serial RDP placement following completed native-Wayland diagnostic evidence.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Relevant source commits:** `e7f63ce2` (original controlled placement), `5a2e152` (sequential X11 reuse fix), `0c9aad7` (KWin caller executable lookup correction), `51ceda4` (architecture/handoff), **`6516a31` (diagnostic instrumentation; native Wayland tested)**. Verify actual checkout/HEAD and preserve any later maintainer documentation edits; never force reset or overwrite a dirty tree.

**State as of 2026-11-09 (after native diagnostic):** Native-Wayland and native-X11 **RDP viewer registration** remain accepted; native X11 `software`/`auto` placement and sequential A/B reuse remain accepted. On `q552u01`, diagnostic revision **`6516a31`** passed **763 Python / 161 JavaScript tests**, installation checks and introspection. The original registered Wayland viewer UUID was correctly claimed; KWin selected it and attempted geometry assignment; `Complete(VERIFY)` was accepted and the broker entered `VERIFYING` in ~5 ms. The **outer `guard_deadline` expired at 15 s** with identity/source still valid. The same present UUID was observed at the requested **position** at 54.343 s (after failure), but the frame stayed **1024×796**, not requested **800×600**. This is **diagnostic acceptance, not placement acceptance**. Increment 3 remains OPEN; actual late-effect mechanics and size contract are unresolved. The maintainer agrees this evidence is sufficient to proceed to **Option C implementation review** without another diagnostic-only native rerun. Configured RDP `-o` and Option D concurrency are not implemented.

**Primary evidence:** [native-Wayland timing/geometry diagnostic and full sanitized trace](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md); [native X11 sequential A/B closeout](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md); [earlier X11 placement evidence](step1.5c5d-increment3-native-x11-placement-2026-11-09.md); [native Wayland registration acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md). Also [task README](README.md), [engineering scope](Step1.5c5_implementation_scope.md), and [settled serial-workflow decision](step1.5c5d-increment3-strategy-decision.md).

## Closed X11 defect — native acceptance summary

On `gmki91` kernel 6.18.62, after publishing `5a2e152` and restarting/installing the service (691 Python / 158 JS PASS), the maintainer:
- Registered viewer **A**, `software`, `win-001`, desktop 1/slot 2, UUID `2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2`; explicitly placed it at (0,0) (`reason=verified`), closed it, and observed `presence=missing` with UUID retained and `placement=succeeded`.
- **Without restarting `joetoo-kwind`**, registered viewer **B**, `auto`, `win-002`, desktop 1/slot 3, UUID `5a893ce2-5cec-4b20-b7d0-01626385df42`, while A's previous `placement_transaction={state:"OK",id:"c32cddcc7d6848759890ad9210047f5e"}` remained. B was intentionally **not placed** (`placement=not_requested`).
- Closed B: both records were `missing` with original distinct UUIDs, two successful and zero failed/ambiguous/timed-out registrations, synchronized observation and no viewer-cleanup uncertainty.

**Sequential-launch defect CLOSED.** Retain the old `Broker is busy` evidence as a historical pre-fix finding, not a current blocker.

## Next active task — Option C serial RDP placement consolidation

**Maintainer decision:** The single native diagnostic at `6516a31` is sufficient. The previous diagnostic-only task is **complete**; do not repeat that task or reopen positive viewer selection. The **next Codex assignment** is to design and implement a focused Option C candidate with local headless regression tests, **when separately instructed by the maintainer**. The updated architecture establishes the agreed C → D roadmap; this HANDOFF is not independent permission to write/publish/deploy.

**Option C boundary:** Preserve accepted native Wayland/X11 FreeRDP exact-UUID viewer registration and source/ownership correlation. Consolidate redundant RDP placement guard checks, overlapping placement deadlines and independent finalization around the existing shared managed-window transaction. Distinguish actual identity/source failure from deadline expiry, and report geometry non-convergence truthfully. Maintain separate registration, placement and remote authentication outcomes; an issued geometry change may be observed after terminal failure and must never retroactively revive that transaction. Keep the working Konsole, Dolphin and TigerVNC workflows unchanged.

**Review/test requirements:** Explain each removed/retained security check, preserve D-Bus compatibility where practical, add focused pending/running/verifying/late-geometry and serial reuse regressions, and capture expected diagnostic stderr inside headless tests so normal Python test output is readable. Report the full source diff and headless results. **Do not install, restart services, run remote/viewer/native tests, commit or push** without a separate maintainer authorization. After review/publication, the maintainer will control native Wayland and X11 acceptance.

**Deferred:** Configured RDP `-o` launch integration and human-wait handling belong to Increment 4; Option D's concurrent pending launches and common RDP/VNC lifecycle are a later milestone, not Option C. Do not change TigerVNC, implement concurrency or introduce a plugin framework now.

## Outstanding geometry question

Earlier X11 tests requested `800×600` but later observed `1032×804` KWin frames. In the **controlled native-Wayland trace** at `6516a31`, the original viewer started at `(448,119) 1024×796`, was requested at `(300,160) 800×600`, and remained at its old frame when the outer placement deadline failed at ~15 s. The same UUID was subsequently **observed** at `(300,160) 1024×796` at 54.343 s, without size convergence. We do not yet know when physical movement occurred or whether client configure/commit or observation delivery caused the delay. Position correctness is not full-frame-size verification; do not infer a confirmed `800×600` frame from a moved window. See [native trace evidence](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md). **No endless resizing, focus or stacking repair loop.**

## Settled later roadmap — not current implementation

**Option C — next implementation objective, separately authorized:** Consolidate serial RDP placement around the existing KWin managed placement lifecycle, retaining accepted SDL FreeRDP positive viewer registration. Current single-flight registration is sufficient for serial operation. Preserve per-launch reservation, exact UUID association, original `-o` placement intent, fail-closed ownership and independent remote-session outcome. For a confirmed configured `-o` launch, readiness of the correct viewer triggers placement; a second operator release is a standalone POC test gate, not the desired configured workflow. Keep working TigerVNC unchanged.

**Increment 4:** integrate the existing `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]` grammar, derived slots/geometry, confirmed serial mixed Konsole/Dolphin/TigerVNC/RDP `-o` launches, and human-interactive NLA/VNC/SSH prompts. Genuine human credential wait must **not terminate a client/tunnel solely on an arbitrary automated timeout**; mechanical identity, placement and cleanup deadlines remain bounded. **Increment 5:** RDP TLS/NLA/security and native regression. **Step 1.5d:** broader regression and `-L`/`-l`.

**Option D — future architectural target, NOT authorized now:** independently keyed multiple pending remote launches, out-of-order human authentication completion mapped to original reservations, and common RDP/VNC viewer-readiness and placement lifecycle management. Preserve each client's separate viewer-role selector; evaluate possible Remmina integration separately. Redesign broker per-launch state when concurrency is authorized, rather than embedding authentication-completion order into identity. Do not modify TigerVNC or implement a generic plugin framework during Option C.

**Hard stops:** No active-window, title/class/PID-only replacement for exact UUID; no placement from registration-only POC, no credential injection, TLS bypass or false remote login claims. Confirmed configured `-o` intent may later authorize placement after positive viewer registration; that integration is not implemented yet. No automatic change to unrelated config, source history or local workstation state. Maintainer authorizes any future code change, publication or native operation separately.
