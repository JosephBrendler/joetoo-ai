# Step 1.5 — Active task dispatcher

**Task:** Step 1.5c.5d / Increment 3 — exact-UUID SDL FreeRDP placement, native validation and focused correctness closeout.  
**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Reviewed candidate commit:** `e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1` (five Increment 3 source/test files pushed by the maintainer). This is a reviewed code baseline, **not** a claim of formal Increment 3 acceptance. Inspect current branch HEAD and dirty state; do not reset the maintainer's checkout.

**Current state (2026-11-09):** Increment 1 (native-Wayland SDL registration-only) and Increment 2 (native-X11 `auto`/`software` SDL registration-only) remain **ACCEPTED**. Increment 3's operator-confirmed placement implementation is pushed and **headless-validated** (191 focused Python, 676 full Python, 158 JavaScript); its **native X11 exact-UUID placement/lifecycle passes for both `software` and `auto`**. Increment 3 is **NOT YET ACCEPTED overall**, due to a reproducible sequential-registration preflight defect, a reproducible requested-versus-final-size discrepancy, and absent native-Wayland placement evidence.

**Primary native evidence:** [Increment 3 X11 placement, closure, sequential-reuse defect and geometry transcript](step1.5c5d-increment3-native-x11-placement-2026-11-09.md). Preserve the recorded UUIDs/results and distinctions rather than redoing the accepted X11 tests. Earlier background: [Increment 2 registration evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md), [strategy decision](step1.5c5d-increment3-strategy-decision.md), [authentication contract](increment2-deferred-authentication-workflow-section.md), [project architecture](../ARCHITECTURE.md), [task README](README.md).

## Implementation and confirmed native behavior

- The placement implementation adds `SubmitSdlPlacement`, `TakeSdlPlacement`, `PollSdlPlacement`, `CancelSdlPlacement` and `tools/joetoo-sdl-release-placement.py`. The operator names an existing managed ID and explicitly confirms; the broker verifies ownership/source/original child and targets only its original exact KWin UUID. Registration alone never moves the viewer.
- On `gmki91` native Plasma X11, `software` registered `win-001` / `4480282f-c283-4edb-bd92-75f98b080240`, moved it to `(0,0)` on desktop 1 with `placement=succeeded,reason=verified`, retained the same UUID with `presence=missing` after titlebar closure, and rejected a new placement of that closed viewer with `InvalidRequest`.
- After a broker restart to work around a separate preflight defect, `auto` registered `win-001` / `2482a3db-ae8f-488a-a752-02de3ed52711`, placed the same UUID at `(120,90)` on desktop 1, retained it after closure with `presence=missing`, and preserved `placement=succeeded`. GDM was visible within the viewer; `remote_session=unverified` correctly remained separate from window placement.
- Both tests requested `800×600` but subsequently observed `1032×804` KWin frame size (four 2-second `auto` observations). **Do not claim stable 800×600 geometry** or imply the same resize mechanism has been proved. No continuous geometry/focus enforcement was requested or implemented.

## Next bounded engineering task — confirmed defect

**Fix the two overly restrictive development-launcher preflights** in `tools/joetoo-sdl-registration-launch.py`. They currently require `placement_transaction == {"id":null,"state":"IDLE"}` both before `BeginSdlRegistration` and while monitoring pending registration. A previous completed `OK` placement causes a new registration for a **different** desktop/slot to fail `SDL development launcher FAILED: Broker is busy`. The actual tested status was `state=OK`, `initial_layout_active=false`, `request_counts.pending=0`, `request_counts.running=0`, `viewer_cleanup_uncertain=false`. The established configured-launch preflight permits clean terminal `IDLE|OK|ERROR`.

**Required correction:** permit clean terminal placement history without assuming a null request ID; still prohibit `PENDING/RUNNING/VERIFYING`, live registration/correlation, active initial layout, uncertain cleanup, owner/source loss and slot conflicts. Preserve the original SDL launcher supervision and fail-closed ownership validation. Add explicit headless tests for back-to-back SDL registrations with no broker restart after successful placement, and a previous terminal `ERROR` with certain cleanup; retain negative tests for genuinely active/uncertain transactions. Avoid unrelated RDP/VNC supervisor changes.

## Remaining Increment 3 acceptance work

1. **Investigate the reproducible frame-size discrepancy** with a narrowly scoped native experiment: determine whether the 1024×768 remote client area and X11 frame decorations account for observed 1032×804; distinguish point-in-time broker verification from subsequent SDL/client sizing. The development FreeRDP argv omits `/size`. Do not implement continuous resize loops or silently substitute dimensions. Report whether a client launch-size setting belongs in later configured `-o` integration, and what exact geometry contract Increment 3 can truthfully guarantee.
2. **Run one native-Wayland placement/lifecycle test on `q552u01`**, after the focused correction has been reviewed and installed by the maintainer. That run uses the existing native-Wayland SDL registration path (no X11 profile/renderer flags). Establish positive exact UUID, explicit release, observed geometry/desktop membership, closure and safe rejection; do not retest the X11 500 ms heuristic on Wayland.
3. **Rerun targeted and full headless regressions** on the corrected candidate, retain the current 191/676/158 baseline for comparison, and record maintainer-native results. Only then decide whether Increment 3 is accepted or whether a separately justified geometry correction is required.

**Actor/authority:** The maintainer owns local desktop actions, credentials, installation, restarts, remote connections and publication. This HANDOFF records the actual next code-review/correction scope; it does **not** assert Codex has already been dispatched for the new fix, nor grant unattended native or push/merge authority. Codex may be given the bounded correction after explicit maintainer dispatch. No more planning of the already accepted launch strategy is required.

## Settled later milestones — do not conflate with Increment 3

**Increment 4:** integrate RDP with the existing per-desktop slot/geometry planner and confirmed `-o` sequential Konsole/Dolphin/TigerVNC/RDP workflow. One owned registration/placement transaction finishes before the next entry; several minutes or longer of genuine human NLA/VNC/SSH credential entry **must not itself terminate the owned client/tunnel**. Keep bounded mechanical D-Bus/correlation/placement/cleanup, genuine failures, operator cancellation and remote server timeout as distinct outcomes. Existing RDP/VNC pre-authentication deadlines are a known *unimplemented* Increment 4 correctness issue.

**Increment 5:** RDP security, trusted certificate/NLA and native/regression closure. **Step 1.5d:** broader X11/Wayland integration and `-L`/`-l`. **Phase 2:** optional measured concurrency/prompt staging, not a prerequisite to the working serial baseline.

**Hard stops:** Do not replace exact UUID checks with active-window, title/class-only or same-PID fallback; do not mistake GDM content for an SDL credential dialog or proof of authentication; do not embed credentials or bypass certificate policy; do not silently change RDP client settings or kill a live viewer to resolve a placement bookkeeping error. Separate any native trial from headless code authorization.
