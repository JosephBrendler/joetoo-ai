# Codex Task — Investigate Delayed KWin Focus Verification

## 1. Authority, scope and starting point

Continue the current `joetoo-kwin` graphical-layers implementation on the existing task branch:

`task/joetoo-kwin-step1.5c4-graphical-launch`

This is a **focused native-failure investigation and correction**, not a new feature increment or architectural redesign.

Read applicable `AGENTS.md`, relevant project instructions, HANDOFF and the current source. Inspect the existing initial-layout transaction and the recent compatibility correction.

The existing uncommitted graphical-layers implementation and its accumulated evidence must be preserved.

Do not assume the historical HEAD or working-tree state is unchanged without checking.

## 2. New native X11 evidence

The maintainer has successfully tested, first on desktop 4 and then on desktop 2:

- Initial panel/under stacking.
- Five-window under/panel/over stacking.
- Interleaved desktop-group execution.
- Correct UUID-based placement and relative stack verification.
- Manual raising, lowering, movement and resizing without layout enforcement.

One remaining issue concerns **focus verification on the currently displayed desktop**.

On `gmki91` (KWin X11), the maintainer launched two Dolphin windows using:

`task_step1.5/layers-examples/cascade_joe2.conf`

Configuration:

```bash
screen_width=1920
screen_height=1080
desktop_limit=20
dt_win_limit=4
min_window_exposure_px=32

D=${TEST_DESKTOP:-2}

desktop_session_list=(
    "$D|dolphin|local||panel"
    "$D|dolphin|local||under"
)
# End of configuration

```

The maintainer was already on the target desktop (4) before launching, manually opened and used an unmanaged konsole terminal to issue the launch command.

Both windows registered and placed successfully. The initial-layout transaction reported:

joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ TEST_DESKTOP=4 ./joetoo-kwin -vv -o -f task_step1.5/layers-examples/cascade_joe2.conf
 ℹ * verbosity increased: [6]
 ℹ * verbosity increased: [7]
 ✨ Validating configured launch intent ...
 ✨ Validating configured launch intent result: (completed)                                   [ ✅ ]
 ℹ Calculating shared geometry ...
 🔍 Planned desktop [4] slot [1]: 19,54 1670x918
 🔍 Planned desktop [4] slot [2]: 96,32 1804x972
 * Desktop [4]: implicit [0], explicit [2]; initial stack slots bottom-to-top [2 1 ], preferred focus slot [1] (intent only)
 ℹ Calculating shared geometry result: (completed)                                           [ ✅ ]
 ⚠ Unmanaged window may obscure desktop [4] slot [1]
 ⚠ Unmanaged window may obscure desktop [4] slot [2]
 🔍 - in show_config
---[ joetoo-kwin-1.0.14 (configuration) ]------------------------------------------------------------
 * PN ........................: [ joetoo-kwin ]
 * BUILD .....................: [ 1.0.14 ]
 * config ....................: [ task_step1.5/layers-examples/cascade_joe2.conf ]
 * verbosity .................: [ 7 ]
 * screen_width ..............: [ 1920 ]
 * screen_height .............: [ 1080 ]
 * desktop_limit .............: [ 20 ]
 * dt_win_limit ..............: [ 4 ]
 * min_window_exposure_px ....: [ 32 ]
 * terminal_width_percent ....: [ 87 ]
 * terminal_gap_percent ......: [ 2 ]
 * terminal_height_percent ...: [ 85 ]
 * terminal_left_percent .....: [ 1 ]
 * terminal_top_percent ......: [ 5 ]
 * terminal_row_gap_percent ..: [ 3 ]
 * graphical_left_percent ....: [ 5 ]
 * graphical_top_percent .....: [ 3 ]
 * graphical_width_percent ...: [ 94 ]
 * graphical_height_percent ..: [ 90 ]
 ✨ LAUNCH PLAN: [2] windows; confirmation required
 ✨ Execution desktop groups: [4]; preserve entry order within each group
 ✨ Exposure is a frame-rectangle prediction; compositor visibility and decoration hit targets require native validation
 ✨ The sourced trusted Bash configuration may have side effects.
 ✨ Configured display: [1920x1080] (not autodetected); terminal width budget: [87%]
 * Desktop  Slot  Program  Mode   Target  Layer  X   Y   Width  Height
 * 4        1     dolphin  local  -       panel  19  54  1670   918
 * 4        2     dolphin  local  -       under  96  32  1804   972
 ✨ KWin desktops: current [20], required [4]; existing desktop capacity is adequate

 ✨ Do you want to continue? [Y/n]: y                                                                
 ✨ Affirmative response from user; continuing
 ⚠ Unmanaged window may obscure desktop [4] slot [1]
 ⚠ Unmanaged window may obscure desktop [4] slot [2]
 ✨ Launching desktop [4] slot [1]
 ✨ Armed managed launch [28d8f49a04b443feb284b9921ff807fb], placement [f41d8b1f6f204a2e8cd8c0b5c6aef5d4]
 ✨ Launched [dolphin] operation; launch-process PID [2457483]
 ✨ Registered [win-001] UUID [9980f666-9c7b-4f79-bd94-2d2aef434f43]
 ✨ OK launch: Home — Dolphin (pid=2457483) before=[4] (16,72) 1804x972 after=[4] (19,54) 1670x918 tiled=false fullscreen=false
 ⚠ Unmanaged window may obscure desktop [4] slot [2]
 ✨ Launching desktop [4] slot [2]
 ✨ Armed managed launch [c81d275c00ec442cb430111fdcae335b], placement [ae2fbd967cf34dcc8e8cb611cb67038b]
 ✨ Launched [dolphin] operation; launch-process PID [2457708]
 ✨ Registered [win-002] UUID [1546d51d-cb88-48dc-93e0-13649689ae06]
 ✨ OK launch: Home — Dolphin (pid=2457708) before=[4] (58,36) 1804x972 after=[4] (96,32) 1804x972 tiled=false fullscreen=false
 ✨ Initializing desktop [4] stack/focus; geometry remains separately verified
 ✨ Desktop [4] initial stacking/focus result: (failed)                                       [ ❌ ]
 * Initial layout: {"id": "0ba4eb7506d54090aa745ce114f6a71d", "state": "FAILED", "geometry": "unchanged", "stacking": "verified", "focus": "failed", "detail": "", "preferred_uuid": "9980f666-9c7b-4f79-bd94-2d2aef434f43", "observed_active_uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "focus_attempted": true, "order": ["1546d51d-cb88-48dc-93e0-13649689ae06", "9980f666-9c7b-4f79-bd94-2d2aef434f43"], "observed_order": ["1546d51d-cb88-48dc-93e0-13649689ae06", "9980f666-9c7b-4f79-bd94-2d2aef434f43"], "before_active_uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "current_desktop": 4, "entries": [{"uuid": "9980f666-9c7b-4f79-bd94-2d2aef434f43", "layer": "panel", "desktop": 4}, {"uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "layer": "under", "desktop": 4}]}
 💥 Initial stack/focus incomplete: {"id": "0ba4eb7506d54090aa745ce114f6a71d", "state": "FAILED", "geometry": "unchanged", "stacking": "verified", "focus": "failed", "detail": "", "preferred_uuid": "9980f666-9c7b-4f79-bd94-2d2aef434f43", "observed_active_uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "focus_attempted": true, "order": ["1546d51d-cb88-48dc-93e0-13649689ae06", "9980f666-9c7b-4f79-bd94-2d2aef434f43"], "observed_order": ["1546d51d-cb88-48dc-93e0-13649689ae06", "9980f666-9c7b-4f79-bd94-2d2aef434f43"], "before_active_uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "current_desktop": 4, "entries": [{"uuid": "9980f666-9c7b-4f79-bd94-2d2aef434f43", "layer": "panel", "desktop": 4}, {"uuid": "1546d51d-cb88-48dc-93e0-13649689ae06", "layer": "under", "desktop": 4}]}
 💥 Initial stacking/focus incomplete for [1] desktop groups; window placement results remain separate
 ✨ Configured layout: [2/2] windows completed ... (failed)                                   [ ❌ ]
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ 


The expected and observed stack orders matched exactly:

`underlay → panel`

However, immediately after the resident assigned `workspace.activeWindow` to the preferred panel, the resident's readback still identified the underlay as active.

The maintainer repeated the experiment on fresh desktop 2, pressed **Ctrl+L without clicking either Dolphin window**, and observed the foreground panel Dolphin's location bar activate and select `/home/joe/`.

joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ TEST_DESKTOP=2 ./joetoo-kwin -vv -o -f task_step1.5/layers-examples/cascade_joe2.conf
 ℹ * verbosity increased: [6]
 ℹ * verbosity increased: [7]
 ✨ Validating configured launch intent ...
 ✨ Validating configured launch intent result: (completed)                                   [ ✅ ]
 ℹ Calculating shared geometry ...
 🔍 Planned desktop [2] slot [1]: 19,54 1670x918
 🔍 Planned desktop [2] slot [2]: 96,32 1804x972
 * Desktop [2]: implicit [0], explicit [2]; initial stack slots bottom-to-top [2 1 ], preferred focus slot [1] (intent only)
 ℹ Calculating shared geometry result: (completed)                                           [ ✅ ]
 ⚠ Unmanaged window may obscure desktop [2] slot [1]
 ⚠ Unmanaged window may obscure desktop [2] slot [2]
 🔍 - in show_config
---[ joetoo-kwin-1.0.14 (configuration) ]------------------------------------------------------------
 * PN ........................: [ joetoo-kwin ]
 * BUILD .....................: [ 1.0.14 ]
 * config ....................: [ task_step1.5/layers-examples/cascade_joe2.conf ]
 * verbosity .................: [ 7 ]
 * screen_width ..............: [ 1920 ]
 * screen_height .............: [ 1080 ]
 * desktop_limit .............: [ 20 ]
 * dt_win_limit ..............: [ 4 ]
 * min_window_exposure_px ....: [ 32 ]
 * terminal_width_percent ....: [ 87 ]
 * terminal_gap_percent ......: [ 2 ]
 * terminal_height_percent ...: [ 85 ]
 * terminal_left_percent .....: [ 1 ]
 * terminal_top_percent ......: [ 5 ]
 * terminal_row_gap_percent ..: [ 3 ]
 * graphical_left_percent ....: [ 5 ]
 * graphical_top_percent .....: [ 3 ]
 * graphical_width_percent ...: [ 94 ]
 * graphical_height_percent ..: [ 90 ]
 ✨ LAUNCH PLAN: [2] windows; confirmation required
 ✨ Execution desktop groups: [2]; preserve entry order within each group
 ✨ Exposure is a frame-rectangle prediction; compositor visibility and decoration hit targets require native validation
 ✨ The sourced trusted Bash configuration may have side effects.
 ✨ Configured display: [1920x1080] (not autodetected); terminal width budget: [87%]
 * Desktop  Slot  Program  Mode   Target  Layer  X   Y   Width  Height
 * 2        1     dolphin  local  -       panel  19  54  1670   918
 * 2        2     dolphin  local  -       under  96  32  1804   972
 ✨ KWin desktops: current [20], required [2]; existing desktop capacity is adequate

 ✨ Do you want to continue? [Y/n]: y                                                                
 ✨ Affirmative response from user; continuing
 ⚠ Unmanaged window may obscure desktop [2] slot [1]
 ⚠ Unmanaged window may obscure desktop [2] slot [2]
 ✨ Launching desktop [2] slot [1]
 ✨ Armed managed launch [b891204229d14f729fe051c20025f3d2], placement [47f964e5f70a42888e00900c65112fca]
 ✨ Launched [dolphin] operation; launch-process PID [2471448]
 ✨ Registered [win-003] UUID [4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8]
 ✨ OK launch: Home — Dolphin (pid=2471448) before=[2] (125,63) 1670x918 after=[2] (19,54) 1670x918 tiled=false fullscreen=false
 ⚠ Unmanaged window may obscure desktop [2] slot [2]
 ✨ Launching desktop [2] slot [2]
 ✨ Armed managed launch [d928c886f5e045928b11964c9e7e5b67], placement [8b5498db61ec49f3bcfef7b4d5cc43e5]
 ✨ Launched [dolphin] operation; launch-process PID [2471678]
 ✨ Registered [win-004] UUID [aacc1bf7-ff18-4d13-bfb2-d5b825b370cf]
 ✨ OK launch: Home — Dolphin (pid=2471678) before=[2] (165,84) 1670x918 after=[2] (96,32) 1804x972 tiled=false fullscreen=false
 ✨ Initializing desktop [2] stack/focus; geometry remains separately verified
 ✨ Desktop [2] initial stacking/focus result: (failed)                                       [ ❌ ]
 * Initial layout: {"id": "bda3928babc946658fc6e219a3178e29", "state": "FAILED", "geometry": "unchanged", "stacking": "verified", "focus": "failed", "detail": "", "preferred_uuid": "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8", "observed_active_uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "focus_attempted": true, "order": ["aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8"], "observed_order": ["aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8"], "before_active_uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "current_desktop": 2, "entries": [{"uuid": "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8", "layer": "panel", "desktop": 2}, {"uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "layer": "under", "desktop": 2}]}
 💥 Initial stack/focus incomplete: {"id": "bda3928babc946658fc6e219a3178e29", "state": "FAILED", "geometry": "unchanged", "stacking": "verified", "focus": "failed", "detail": "", "preferred_uuid": "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8", "observed_active_uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "focus_attempted": true, "order": ["aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8"], "observed_order": ["aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8"], "before_active_uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "current_desktop": 2, "entries": [{"uuid": "4cdbc54c-fc25-4d21-8549-d3bb62f0ddd8", "layer": "panel", "desktop": 2}, {"uuid": "aacc1bf7-ff18-4d13-bfb2-d5b825b370cf", "layer": "under", "desktop": 2}]}
 💥 Initial stacking/focus incomplete for [1] desktop groups; window placement results remain separate
 ✨ Configured layout: [2/2] windows completed ... (failed)                                   [ ❌ ]
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $

This observation that the address bar highlighted on the top window in response to ctrl-L with no prior click to any window is strong evidence that the intended panel received keyboard input shortly after initial-layout completion.

It is **not yet conclusive proof** that the resident's activation request caused that later focus state.

## 3. Investigation objective

Determine whether the failure reflects:

1. Delayed/asynchronous focus convergence after a valid activation request.
2. A request that KWin rejected or ignored.
3. A competing client/window activation.
4. An inaccurate or prematurely sampled focus observation.
5. Possible activation or focus contention involving the unmanaged launch-control Konsole on the same desktop.
6. Another source-grounded cause.

Inspect relevant KWin scripting APIs and actual current transaction code rather than presuming the first explanation.

Distinguish the time of the activation request from the time of its observed result.

Review the interaction between KWin's active-window state, X11 keyboard focus, window raising and asynchronous activation.

Do not assume that the launching Konsole reclaimed focus: the immediate recorded active UUID belonged to the newly launched underlay Dolphin.

## 4. Approved focus policy — unchanged

Preserve the existing focus-selection policy:

- Last successfully registered `over` entry, otherwise last successfully registered `panel`.
- Never automatically select an `under` entry.
- Do not switch virtual desktops merely to focus a window.
- Do not introduce a sixth configuration field.
- Do not impose persistent focus or stacking constraints.

Preserve the approved one-time stacking order:

`under → panel → over`

with original configuration order retained within each layer.

Preserve unrestricted manual overrides after initialization.

## 5. Evaluate bounded delayed verification

Investigate the smallest implementation that can observe whether the requested focus eventually becomes active.

The preferred model is:

1. Resolve and validate the existing broker-owned cohort.
2. Apply initial stacking once.
3. Request activation of the selected focus target **once**.
4. Observe active-window state immediately.
5. If the target is not immediately active, perform a short, bounded, nonblocking observation phase. Investigate mechanisms in this order:
   - **Event-driven verification:** Use an appropriate temporary KWin focus/activation signal handler if supported by the deployed API, with bounded timeout and guaranteed cleanup.
   - **Nonblocking polling:** Otherwise use a KWin-supported asynchronous timer or equivalent to inspect `workspace.activeWindow` periodically without blocking KWin's event loop.
   - Neither mechanism may repeatedly request activation or enforce focus after the initial-layout transaction completes.
6. Declare focus verified only after a KWin observation identifies the preferred UUID as active.
7. Recheck stack order and geometry before declaring full success.
8. Complete the transaction with a truthful, terminal outcome.

Important constraints:

- **Do not repeatedly assign `workspace.activeWindow`.**
- Do not repeatedly raise the window as a substitute for activation.
- Do not install a persistent desktop-switch listener or focus controller.
- Do not retain background layout-enforcement behavior after transaction completion.
- Do not allow a late callback from an expired transaction to change focus or geometry.
- Do not hold the transaction open indefinitely.
- Preserve the invocation lock and broker single-flight Busy rules through finalization.
- Preserve positive UUID ownership and current observer-source consistency.

Choose a bounded observation duration supported by the existing transaction lease and KWin API behavior. Explain the timeout choice instead of introducing an arbitrary long wait. If such timing is needed, assign to a configurable global variable and place a default assignment in the template user configuration file.

All new operational timing parameters shall be user-configurable, with documented default assignments in the joetoo-kwin template user configuration file, consistent with the new "Configuration and operational bounds" requirement in `ARCHITECTURE.md` and the updated repository `AGENTS.md`.

For this increment, expose any new focus-observation timeout, polling interval or related timing value through appropriately named configuration variables. Validate their values and explicitly convey the effective values to whichever component uses them, respecting the existing transaction interfaces and deadline constraints.

Do not hardcode a new operational timeout exclusively in the resident or broker, and do not assume those processes inherit Bash configuration variables.

Do not expand this focused correction into a wholesale migration of existing timing constants.

Consider whether KWin's existing scripting/event facilities allow a bounded follow-up observation without persistent subscriptions. If a temporary subscription is used, require guaranteed cleanup on success, failure, interruption and expiry.

**Do not use repeated activation as a polling mechanism.**

## 6. User intervention and competing focus

Distinguish delayed convergence from user intervention wherever the available evidence supports it.

In particular:

- Stop or report interruption when the displayed desktop changes.
- Stop safely if the preferred UUID disappears or changes to an incompatible state.
- Detect observer-source replacement or transaction expiry.
- Do not automatically reclaim focus after another window becomes active. Distinguish the preexisting active-window state from a subsequent focus change during the observation period. Treat a newly observed competing activation as a possible interruption, using available event evidence; do not classify the unchanged preexisting active UUID as user intervention merely because it differs from the preferred target.
- Do not treat an unrelated window's activation as permission to manipulate that window.
- Avoid claiming that every non-target focus observation is intentional user intervention; another application's delayed activation may be indistinguishable.

If KWin does not expose enough information to reliably distinguish these cases, report the uncertainty explicitly rather than inventing a definitive reason.

## 7. Architectural compatibility

Prefer an extension of the **existing bounded initial-layout transaction**, not a new independent focus-management system.

Review:

- `joetoo-kwin-resident.js`
- `libexec/joetoo-kwind`
- Existing initial-layout launcher orchestration.
- Current initial-layout JavaScript and Python tests.

Determine whether delayed verification can be implemented without consequential changes to approved D-Bus signatures or registry semantics.

If ordinary internal changes within the existing transaction are sufficient, implement the narrow correction.

If a consequential new interface or persistent component is genuinely necessary, stop and present the exact minimum proposed change for maintainer approval.

Do not weaken UUID, geometry, desktop membership or ownership checks to achieve success.

## 8. Verification and tests

Add focused regressions covering:

- Immediate focus success.
- Delayed focus success after a single activation request.
- Focus that never converges within the bounded interval.
- Another window becoming active.
- Displayed desktop changing during verification.
- Preferred window disappearing.
- Observation-source replacement.
- Expired transaction or stale callback.
- Focus convergence that changes stacking unexpectedly.
- Correct cleanup of any temporary observation mechanism.
- Preservation of manual control after completion.

Where practical, assert that **exactly one activation request** was issued, even when several observations were required.

Maintain distinct geometry, stacking and focus outcomes. A focus failure must not erase a successful placement or verified stack result.

Run the affected JavaScript/Python regressions, full applicable headless suites, syntax/compilation checks and `git diff --check`. Report actual counts and any skips.

Do not claim native X11 or Wayland acceptance from mocked tests.

## 9. Documentation and handoff

Record:

- Findings about KWin focus timing and observation.
- The cause established by source or tests, distinguishing it from hypotheses.
- Any changed transaction behavior and deadline.
- How immediate versus delayed convergence is reported.
- How interruption, expiration and nonconvergence are classified.
- The exact native retest the maintainer should run.

Update relevant focused evidence and HANDOFF without rewriting historical acceptance records or expanding unrelated documentation.

## 10. Authorization and stop conditions

You are authorized to implement a **narrow, bounded delayed-focus verification correction** within the approved initial-layout transaction, provided it preserves the constraints above.

This does not authorize broader architectural changes, persistent focus management or changing the user-approved layer semantics.

Preserve the existing dirty task-branch work.

**Stop with uncommitted changes for maintainer review.**

Do not deploy, restart the broker, perform native GUI tests, commit, push, merge or open a PR.

Return the source-grounded diagnosis, changed-file inventory, headless test results, any unresolved questions, and a precise maintainer-operated X11 retest procedure.

The maintainer will review the correction and repeat the two-Dolphin displayed-desktop experiment before continuing the remaining X11 acceptance battery.
