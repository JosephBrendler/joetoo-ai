# Step 1.8 — launch-control focus loss and restoration evidence

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22 (America/New_York). **Host:** `gmki91`, Gentoo/KDE Plasma 6.7.6, native `kwin_x11` 6.7.6. **Branch:** `task/joetoo-kwin-step1.8-cli-completion`; tested baseline `5ab6ea6` (implementation `73afa19`). **Status:** reproducible defect / design decision recorded; *not yet repaired*. All observations are maintainer-supplied, not independent tool execution by this author.

**Related:** [gmki91 native X11 stacking acceptance](step1.8-gmki91-x11-native-validation-2026-11-22.md) and [q552u01 Wayland acceptance](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md). This focus finding does **not** invalidate the earlier successful identity, geometry and one-shot stacking checks. A completed initial-layout transaction is not proof that the launching terminal subsequently retained keyboard focus.

## 1. Reproduced X11 focus loss after an inactive-desktop `-L under`

The maintainer invoked `./joetoo-kwin -L 2 konsole local btop under` **from desktop 1**, with a pre-existing Konsole as the launching control window. The new managed window was positively registered on desktop 2, with verified placement and initial stacking. The launching Konsole's cursor became *hollow* and required a mouse click before further commands could be typed.

A read-only `focus_snapshot` function captured EWMH desktop/active-window values and actual X11 input focus (`xdotool getwindowfocus`) without clicking:

```text
=== FOCUS SNAPSHOT: BEFORE ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x4400008
X11 input-focus window: 0x4400008
joetoo-kwin : bash — Konsole

$ ./joetoo-kwin -L 2 konsole local btop under
... Registered [win-008] UUID [acb0828c-7bf6-487c-8f4a-4d6d4d6f35f1]
... Desktop [2] initial stacking/focus result: (completed)
... Configured layout: [1/1] windows completed ... (completed)

=== FOCUS SNAPSHOT: AFTER ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x0
X11 input-focus window: 0x1800007
```

**Established:** desktop 1 remained displayed at the two snapshots; EWMH active window became `None` (`0x0`), and X11 input focus moved away from the control Konsole (`0x4400008`). `0x1800007` has **not been identified**. The hollow cursor corroborates lost usable keyboard focus. The snapshot pair alone does not prove whether there was a transient intermediate desktop switch or which event caused the focus loss.

## 2. Guarded `xdotool` restoration experiment — succeeds on X11

A subsequent inactive-target test saved the original EWMH active XID and desktop before launch. It restored focus *only if* the launch completed, the displayed desktop remained the same, the active XID was `0`, and the original control XID still existed. This is an **experiment**, not a proposed product dependency or an adequate user-activation guard.

```text
Original launcher XID: 0x4400008
=== FOCUS SNAPSHOT: BEFORE ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x4400008
X11 input-focus window: 0x4400008
joetoo-kwin : bash — Konsole

$ ./joetoo-kwin -L 2 konsole local btop under
... Registered [win-012] UUID [460cab6b-6fc4-4277-8714-408031d17c85]
... Desktop [2] initial stacking/focus result: (completed)
... Configured layout: [1/1] windows completed ... (completed)

=== FOCUS SNAPSHOT: AFTER_LAUNCH ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x0
X11 input-focus window: 0x1800007

Requesting restoration of original launcher focus
=== FOCUS SNAPSHOT: AFTER_RESTORE ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x4400008
X11 input-focus window: 0x4400008
joetoo-kwin : joetoo-kwin — Konsole

=== FOCUS SNAPSHOT: AFTER_ONE_SECOND ===
_NET_CURRENT_DESKTOP(CARDINAL) = 0
_NET_ACTIVE_WINDOW(WINDOW): window id # 0x4400008
X11 input-focus window: 0x4400008
joetoo-kwin : joetoo-kwin — Konsole
```

**Established:** `xdotool windowactivate "$launcher"` can restore the original X11 control window's EWMH active state and actual keyboard input focus, still correct one second later. This demonstrates *feasibility*, not a cross-backend production solution. It did not independently recheck relative peer stacking after the restoration request. Do not add an `xdotool` dependency to `joetoo-kwin`.

The legacy `/usr/sbin/xdotool_open_windows` includes `xdotool windowactivate --sync "${control_window}"` in its control-window return path. This is **historical design evidence**, not permission to port X11 commands into the Wayland-capable implementation.

## 3. Wider than `-L under`

- The maintainer reproduced the hollow cursor / loss of usable focus after configured `./joetoo-kwin -o` on gmki91 X11. The screenshot and CLI output show a successful `-o` group; **no direct input-focus XID trace was provided for `-o`**. The problem is thus not clearly specific to one-shot `under`.
- The maintainer recalls seeing the same hollow-cursor behavior on `q552u01` Plasma **Wayland** the previous day. This is a **user-reported cross-backend observation**, not instrumented Wayland UUID/focus evidence.
- For earlier gmki91 `-L` trials, `_NET_CURRENT_DESKTOP` and `_NET_ACTIVE_WINDOW` sometimes remained unchanged before/after. Those EWMH snapshots alone cannot establish usable keyboard focus. The later direct `getwindowfocus` measurements supersede any earlier inference that focus was preserved solely because `_NET_ACTIVE_WINDOW` was unchanged.
- The identity/stack/geometry results remain positive; do not classify them as failed merely because focus restoration is an open, **separately reported** completion concern.

## 4. Mechanistic source findings (explanation, not proven cause)

On KWin 6.7.6, the resident JavaScript already uses `workspace.activeWindow = target` for exact-window activation. `WorkspaceWrapper::setActiveWindow()` delegates to KWin's `Workspace::activateWindow()`, which can **raise** a window, request focus, and potentially switch desktops. Thus it is *not a focus-only setter*. On the displayed-desktop `under` path, `workspace.slotWindowLower()` deliberately lowers its active target and KWin may focus another window afterward. However, the instrumented reproduction targeted an **inactive** desktop and used the *peer-raising* path, not `slotWindowLower()`. Consequently the source alone does not identify the cause of this particular loss.

References: `joetoo-kwin-resident.js` (`initialLayoutFromBroker`, `singleLowerFromBroker`), `libexec/joetoo-kwin-launch-functions` (`open_plan`, `InitialLayoutStatus` poll), KDE `kwin-x11` `v6.7.6` `src/scripting/workspace_wrapper.cpp`, `src/activation.cpp`, and `src/useractions.cpp`.

## 5. Maintainer-approved design direction, with implementation pending

The maintainer approved a **shared mission lifecycle** approach rather than patching only `-L under`, `-L over` or `-o`:

1. **Capture control context early**, before any operation that can launch, close, move, raise or activate windows: exact KWin UUID of the initiating graphical control window *when reliably established*, current desktop, and observed focus/activation context. The active KWin window is not necessarily the process's true initiating window (e.g. SSH, TTY, background automation); where provenance cannot be established, no unsafe adoption or guessing by class/title/PID.
2. **Execute and independently verify the selected mission** with existing identity/placement/stack/security and terminal-status behavior unchanged.
3. **At completion, evaluate mission-specific focus policy and subsequent activity**: restore the saved control window only when semantically appropriate, it still exists/is eligible, the desktop context permits, and a competing user activation/focus intent has *not* superseded it. If user intent cannot be distinguished reliably, fail closed (skip restoration) and report why. Avoid permanent focus forcing, timers that steal focus later, or unbounded polling.
4. **Report a separate focus-completion outcome** without retroactively turning a successful registration/placement/stack into a failure. Preserve original CLI exit behavior and avoid applying a focus policy to read-only commands or commands intended to leave another window active.

**Open design choices for Codex/maintainer review:** `-o` already has a preferred-focus target; `-m` intentionally operates on the active window; `-d`/`-x` may close the control window; `-r` launches new instances; CLI invocations may originate outside the active GUI. `workspace.activeWindow = ...` raises and could alter same-desktop `under` peer ordering, so restoration may need to be skipped or explicitly verified depending on mission semantics. No `xdotool`/X11-only production dependency, no arbitrary window selection, no change to existing stacking algorithms. Full design/implementation acceptance is not yet recorded.

**Next:** see [Codex next-step task draft](step1.8-codex-control-context-focus-completion-TASK-DRAFT-2026-11-22.md). The maintainer controls authorization, native experiments, deployment, commits and merge. Step 1.8 remains ACTIVE and not accepted.
