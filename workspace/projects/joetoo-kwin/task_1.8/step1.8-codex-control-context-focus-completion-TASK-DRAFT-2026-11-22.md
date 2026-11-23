# Codex next task (DRAFT) — shared control context and guarded mission-completion focus

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Task context:** active **new Step 1.8** CLI completion, `task/joetoo-kwin-step1.8-cli-completion` on `gmki91`. Last confirmed maintainer-pushed baseline `5ab6ea6` (one-shot `-L under` implementation `73afa19`). Do not assume there is no more recent local work: inspect Git and the working tree first. Existing Steps 1.1–1.7 are **accepted and closed**; Step 1.9 is paused. The project is native KWin **X11 and Wayland**, not X11-only.

## Mandatory discovery before implementation

Read the applicable repository/workspace/project `AGENTS.md`, `workspace/README.md`, current `ARCHITECTURE.md` §9/§11/§12, `task_1.8/HANDOFF.md`, `task_1.8/README.md`, [focus evidence](step1.8-launch-control-focus-evidence-2026-11-22.md), and [gmki91 X11 native evidence](step1.8-gmki91-x11-native-validation-2026-11-22.md). Inspect the *current* CLI dispatch and its relevant helpers, KWin resident JavaScript, broker D-Bus protocol, existing focus/stacking tests, and actual installed KWin API compatibility. Treat earlier POCs and historical `xdotool_open_windows` as references, not product implementation authority.

**Do not deploy, restart services, mutate host KWin state, invoke native window tests, commit, push, rebase, merge, alter `joetoo-upstream`/`joetoo`, or perform cleanup without the maintainer's explicit direction.** Do not assume that this DRAFT alone authorizes merging or production integration.

## Problem and verified evidence

On gmki91 native KWin X11 6.7.6, a completed `-L 2 konsole local btop under` from desktop 1 returned a healthy broker status, but `_NET_ACTIVE_WINDOW` changed from `0x4400008` to `0x0`, and *actual X11 keyboard input focus* changed from `0x4400008` to `0x1800007`. The launching Konsole cursor was hollow; clicking was required for further input. Reproduced twice in instrumented commands (managed IDs `win-008`, `win-012`). An **experimental** post-launch `xdotool windowactivate` of the captured original XID restored focus immediately and one second later; **do not use `xdotool` in production**. The maintainer also observed the hollow cursor after configured `-o` on X11 and recalls similar behavior on q552u01 Wayland; the Wayland finding is not yet instrumented. Native X11 stacking/placement tests, including active/inactive `under`, VNC `under`, RDP `over`, and default `over`, passed. Full post-repair suites passed **1,094 Python / 169 JavaScript**. Do not redesign or weaken the verified stack.

## Agreed architectural direction

**Do not limit the control-context concept to `-o` and `-L`.** Treat it as a shared CLI mission lifecycle facility where there is an authentic interactive graphical caller. Capture its identity **early, before possible focus-changing operations**; then decide **at mission completion** whether focus should be restored according to *mission semantics* and *subsequent user activity*. Capture should be broadly available; restoration is **not unconditional**.

Important: the process executing a Bash CLI is **not automatically identical** to `workspace.activeWindow`. An active window may be unrelated (SSH/TTY/headless/automation, focus-follow-mouse, tab/pane or timing). Never silently adopt an arbitrary active normal window or guess by class/title/desktop/PID. Propose an identity/provenance and fallback contract that is feasible on **both X11 and Wayland**. If reliable initiating-window identity cannot be proved, safely skip restoration.

## Requested Codex work

**Phase A — inspect and propose first, before substantive edits:**

1. Map the full CLI mission dispatch (`-o`, `-L`, `-r`, `-m`/`move`, `-d`, `-x`, read-only `-s`/`-l`/`-i`/`-c`/`-S`/`-h`, and test commands) and identify the proper shared capture and completion boundaries. Explain how to guarantee capture before launch, including any asynchronous D-Bus trip, how it works when no graphical caller is reliable, and how the operation's original return status is preserved.
2. Propose an **exact KWin UUID**, current desktop and activation/focus context contract, with minimal authenticated broker/resident communication. Avoid making the CLI user-provided arbitrary UUID into an ownership or activation privilege. Reuse existing protocols where safe, or explicitly justify a new narrowly scoped one. Distinguish KWin active window from real keyboard focus, especially on Wayland where `xdotool` is not available.
3. Specify a bounded **focus-completion policy**. Example categories: `restore_control` (only if safe), `retain_mission_focus`, `none`. Define behavior for each command, especially configured `-o`'s already intentional preferred focus, `-m`'s active-window behavior, closing/sweeping of the original control window, `-r`'s multiple launched windows, and read-only commands. Do not silently overturn the already accepted `-o` preferred-focus contract; flag any proposed change for maintainer decision.
4. Define **competing-activity safeguards**: operator switches desktops, explicitly activates another window, closes or minimizes the original, changes focus during long authentication/launch, or cancels an operation. Simply seeing active UUID `null` at completion is not proof that the user wants restoration. If the source of activation cannot be distinguished reliably, skip rather than steal focus. Any timers/observers must be bounded and cleaned up.
5. Account for KWin 6.7.6 fact: `workspace.activeWindow = savedWindow` calls `activateWindow`, which **raises** the window and may switch desktop or affect normal stack. Describe how this interacts with verified `-L under` peer order and protected BelowLayer windows. Do not inject focus code into the existing lower/raise algorithms. Preserve source and registered UUID identities, geometry, desktop membership, peer ordering, snapshot/restore policy, and close security.
6. Propose the smallest tests and file changes, *separate* native X11 and Wayland acceptance recipes, and explicit fail-closed/skip outcomes. Provide the plan and unresolved design decisions for maintainer review. **Wait for approval of any behavior-changing architectural choice before implementing it.**

**Phase B — implementation only after design approval:** deliver a narrow, reviewable diff with focused Python and JS tests for capture, provenance rejection, user focus override, disappearing caller, active/inactive launches, `-o` preferred focus, read-only and headless no-op, no focus stealing on failure/cancel, retained exit status, no unintended restack, no `xdotool` dependency. Run only non-native/unit/syntax/static tests authorized under project instructions; report exact pass/fail totals and risks. The maintainer performs any native X11 and Wayland tests, service restarts and Git operations.

## Acceptance / stop conditions

- Restoring focus is **mission-aware** and **user-activity-aware**, not a blanket `EXIT` trap or final `workspace.activeWindow` write.
- The original initiating window is positively identified and is still eligible; otherwise restoration skips with a useful, nonfatal reason. Never adopt arbitrary foreign/unmanaged windows by heuristic identity.
- Preserve exact registered application identities, one-shot `under` and `over` semantics, protected layers, desktop/slot/geometry, original mission return status and error reporting. Report focus completion separately from launch/stack success.
- Do not introduce X11-only dependencies, broad new permissions, resident polling loops or config/CLI-option proliferation without justification.
- If protecting the no-focus-steal/no-restack contract requires a new authorization primitive, or if KWin API limitations make the design unsafe, **stop and explain** instead of weakening the guard.
- Keep task documentation truthful: proven native focus defect, experimentally successful X11 recovery, Wayland observation not instrumented, implementation and final acceptance still pending.

**Deliverable to maintainer now:** concise Phase A design proposal, tradeoffs, impact/risk table, candidate code touch points, proposed non-native tests, exact open questions and an explicit authorization gate. Do not claim Step 1.8 complete or resume Step 1.9.
