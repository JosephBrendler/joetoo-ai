# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

> **Archive closure — 2026-11-23: ACCEPTED, MERGED, CLOSED.**
> The maintainer reviewed and merged [PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36)
> into `main` at `67c054c`. The whole task directory, including its original
> evidence and screenshots, is retained here as history. This HANDOFF is
> **not an active task dispatcher**. The current dispatcher is
> [Step 1.9 packaging](../../task_1.9/HANDOFF.md).
>
> [PR #36 merge and closure record](step1.8-pr36-merge-closure-2026-11-23.md) ·
> [Step 1.8 evidence index](README.md) ·
> [November 23 Wayland closeout evidence](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md).

The new Step 1.8 completed read-only `-s` and `-i MANAGED_ID`, verified
one-shot `-L ... under` on X11 and Wayland, and restoration of focus to the
eligible originating control Konsole at the end of serialized launch missions.
The maintainer expressly accepted the Version 1 limitation that an intervening
manual activation can be overridden by final controller focus restoration;
more nuanced focus policy is deferred to Version 2. `-L panel` remains
unsupported. Production installed-path and package QA are **Step 1.9** work.

**Historical boundary:** **All Steps 1.1–1.7 are accepted and closed.**
Step 1.6 (`-d`/`-x`) was accepted and merged via
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32); Step 1.7
(recovery, `-S` and `-r`, *including the former Step 1.8*) was accepted and
merged via [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33).
The **new** Step 1.8 is not a reopening or re-acceptance of either step.

## Authority, baseline and scope

- **Repository/project:** `JosephBrendler/joetoo-ai`,
  `workspace/projects/joetoo-kwin/`.
- **Accepted merged baseline:** `main` `67c054c` after [PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36).
  The branch was `task/joetoo-kwin-step1.8-cli-completion`, with the final
  pre-merge integration commit `fe60d46` (merging the intervening `main` change).
  The former task branch was deleted after merge; source and evidence remain
  in the Git history and this archive.
- **Authoritative design:** [ARCHITECTURE §9](../../ARCHITECTURE.md#9-cli-contract-accepted-version-1-behavior),
  [§11](../../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../../ARCHITECTURE.md#12-version-2-considerations).
- **Task scope and tests:** [Step 1.8 README](README.md); the
  [maintainer-placed outline](step18-branch-outline.md)
  provides the initial work order.
- **Current native evidence:** [q552u01 read-only Wayland](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md),
  [slim2 read-only X11](step1.8-slim2-readonly-x11-evidence-2026-11-22.md),
  [q552u01 V2/V3 lower feasibility](step1.8-q552u01-one-shot-lower-feasibility-2026-11-22.md),
  [initial protected-bridge negative](step1.8-q552u01-under-integrated-participation-2026-11-22.md),
  [corrected Wayland native validation](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md),
  [gmki91 X11 native validation](step1.8-gmki91-x11-native-validation-2026-11-22.md),
  [launch-control focus loss/restoration experiments](step1.8-launch-control-focus-evidence-2026-11-22.md),
  and [2026-11-23 q552u01 closeout evidence](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md).
- **Accepted predecessor evidence:** [Step 1.5 archive](../task_step1.5/README.md),
  [Step 1.6 closure](../task_step1.6/README.md), and
  [Step 1.7 closure](../task_step1.7/README.md) are completed history,
  not active implementation instructions.

## Closure and successor — 2026-11-23

Step 1.8 has **no outstanding implementation, native-validation, policy,
Git-conflict, PR, or merge requirement**. The maintainer settled the
controller-return focus contract and explicitly accepted the intervening
manual-activation limitation for Version 1. Native X11/Wayland evidence,
1,113 Python PASS, 180 JavaScript PASS and 54 focused POC-installer tests
are indexed in the [task README](README.md) and the
[closeout evidence](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md).
These are reported historical results; this documentation transition does
not rerun native tests.

The [PR #36 closure record](step1.8-pr36-merge-closure-2026-11-23.md)
records merged ancestry, known limitations and next-task boundaries.
The **active** HANDOFF is [Step 1.9](../../task_1.9/HANDOFF.md): human
maintainability-comment audit, installed helper/path integration, staged
source transfer, provenance and tarball review, and Gentoo package QA.

### Historical Step 1.8 engineering notes (retained without rewriting)

The following original implementation/review notes were written before the
merge; references to active testing, pending acceptance, and branch review
are historical observations, **not current instructions**.

**Bounded new behavior:** implement read-only `-s` using existing broker
`RegistryStatus()`, read-only `-i MANAGED_ID` using existing `GetManaged()`, and
verified one-shot `-L ... under` for **only the newly managed window**. Preserve
`-L` omitted/explicit `over` and configured `-o` layer behavior. `-L panel`
and all peer geometry/reflow remain Version 2.

## Historical results and next-actor notes through 2026-11-22 (superseded)

**Read-only increment (maintainer-operated):** `-s`/`-i` added in `1670bea`;
`-s` terminal-state false Busy corrected and tested in `f3fef58`;
obsolete Step 1.4d `-o` fixture assertion repaired in `cadf992`.
Wayland: nine Step 1.8 focused tests PASS, present/missing `-i` PASS,
corrected `-s` PASS. X11: broker restart/recovery observed, `-s`/`-l`/`-i`
PASS, extended ShellCheck PASS, JavaScript **163/163 PASS**. Full Python
suite before fixture repair: **1089 run, 1 obsolete-test failure**; focused
fixture test **3/3 PASS** on q552u01 after repair. A post-repair full Python
rerun was not shown. `shellcheck_stub_filter` (joetoolkit 1.0.19) enabled a
consumer-scoped header stub and successful source-following lint; details and
limits are in the linked evidence, not a new Step 1.8 product requirement.

**Latest feasibility result (maintainer-operated):** KWin 6.7.6 Wayland
V2 manual-click guarded lower and V3 automatic exact-UUID activate/verify/lower
both returned `PASS`. At settle the target was bottommost, peer order, frames,
desktop membership and keep flags unchanged. The active-window lower slot
works; direct `lowerWindow(window)` is not exposed. The V3 probe guards the
current desktop and does not lower desktop-3 target from desktop 1, per the
maintainer's report. Full results and screenshots are in linked evidence.

**Latest native integration / corrected participation policy:** The first
q552u01 Wayland candidate passed `-L under` on desktop 3 but the desktop-1
absolute-bottom check rejected a correctly lower-stacked Konsole above a
64x36, invisible `xwaylandvideobridge` protected surface. The property-based
NormalLayer participation follow-on, subsequent fixture/config/broker
regression repairs, and tests were applied. Corrected `-L 1 konsole ssh
yorsqui under` registered `win-015`, completed initial stacking/focus, and
passed the overall launch. The bridge need not be restacked or made visible.

**Inactive-desktop native proof:** `-L 3 konsole ssh yorsqui under` registered
`win-016` (UUID `947fe577-4f75-4291-8871-7e0e8dfbb55b`, desktop 3/slot 6),
placed it and completed the initial stacking/focus transaction. **The
maintainer explicitly confirmed the operation was initiated on desktop 1 and
Plasma remained on desktop 1 throughout.** This supports the one-shot
inactive-desktop peer-raising approach without a desktop switch. An
independent active-window UUID trace was not supplied. The missing desktop
3/slot 1 `win-007` reservation was not reused.

**Viewer regression/native results:** With desktop 1 displayed throughout,
`-L 5 sdl-freerdp rdp rdp://joe@opi6plus01 over` completed locally; an
earlier RDP launch to desktop 3 failed before completing and is *unresolved*,
not proven a stacking regression. `-L 5 vncviewer ssh
ssh://joe@x401/display/2 under` completed its managed viewer launch and
stacking transaction; `-i win-018` confirms the Vncviewer UUID and placement.
Neither local success is proof of current remote authentication/health.
[Full native evidence and raw console logs](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md).

**Regression evidence and outstanding gap:** The participation follow-on
initially produced 3/1,094 Python and 29/169 JavaScript failures (stale
configuration expectations, a test-harness recipe/KWin `layer` collision,
and a broker protected-layer guard). After the repair, the maintainer reported
`test_config_presentation.py` **6/6 PASS**,
`test_initial_layout_broker.py` **20/20 PASS**, and
`test_initial_layout.js` **44/44 PASS**; previously the single-recipe suite
passed **14/14**. The **full** post-repair Python/JS suite was subsequently
rerun on gmki91: **1,094/1,094 Python** and **169/169 JavaScript PASS**. A restart-time D-Bus introspection briefly reported no broker, but
subsequent `rc-service` and `RegistryStatus` confirmed `recovery=ready`,
observer synchronized, `single_lower_protocol=1`, and no Busy/uncertain
flags. Raw `-s` output still omits the `single_lower` capability from its
human summary (presentation-only gap).

**Next actor and priority: Codex — scoped design review of shared
control-window context and mission-completion focus policy.** Read the
[focus evidence](step1.8-launch-control-focus-evidence-2026-11-22.md),
[gmki91 X11 native validation](step1.8-gmki91-x11-native-validation-2026-11-22.md),
and [Codex task draft](step1.8-codex-control-context-focus-completion-TASK-DRAFT-2026-11-22.md).
The maintainer **approved the architectural direction**: early capture of a
reliably identified graphical control window across missions, then conditional
restoration only when mission semantics and subsequent user activity permit.
This does not authorize unconditional activation, a new X11 dependency, or
unreviewed architecture/implementation changes. **Phase A** is source/API
inspection, minimal protocol design, focused test strategy and explicit
questions for maintainer decision. **Phase B** code/native changes need
appropriate approval under project rules. Do not change the already verified
one-shot lower/raise algorithms.

The X11 focus defect is reproducible: `-L 2 konsole local btop under` from
desktop 1 preserved desktop 1 but left `_NET_ACTIVE_WINDOW=0x0` and
X11 keyboard focus at `0x1800007`, rather than the original `0x4400008`.
Experimental `xdotool windowactivate` restored the original focus and
it stayed correct one second later; this is evidence of feasibility, **not**
a production dependency. `-o` visibly reproduces the hollow-cursor symptom;
Wayland has a maintainer-reported but not instrumented observation. Native
stacking and full regression PASS stand separately; Step 1.8 is not accepted.

**After design review/authorized implementation and native X11+Wayland
revalidation:** reconcile `ARCHITECTURE.md`'s obsolete `-L under`
unsupported wording (maintainer-owned architecture decision), include
`single_lower=1` in human `-s` presentation if desired, and review the
isolated q552u01 desktop-3 RDP failure and relevant close/recovery limits.
Then prepare the Step 1.8 PR/ancestry reconciliation against accepted
`main`. slim2 may provide optional second X11 host coverage. No Step 1.9
resumption before maintainer acceptance/merge.

## Shared control context — original approved requirements (historical)

The project-wide concept is **capture early, restore conditionally**.
A CLI process does not automatically own the currently active GUI window:
identification must have reliable provenance or be an explicit nonfatal
skip. The captured initiating KWin UUID, desktop and focus/activation
context are not a managed-window registration and cannot authorize arbitrary
foreign-window adoption. Capture should be shared across `-L`, `-o`, `-r`,
move, managed-close and read-only dispatch where meaningful; do **not** force
a restoration on every command. Do not disturb read-only operations,
intentional preferred focus in `-o`, `-m` target focus, or user changes made
while the mission was in flight.

At mission completion, preserve the original mission result while evaluating
restoration separately. Restore only for an eligible surviving control window,
unchanged permitted desktop, compatible mission semantics and no competing
user activity. KWin `workspace.activeWindow = window` calls an activation
that may **raise** the window or switch desktops; restoring same-desktop
focus could therefore violate one-shot `under` peer order. Require a bounded,
fail-closed design, no `xdotool`, no unconditional `EXIT` trap, no asynchronous
focus stealing and no weakening of source/registration/stack checks. See the
[Codex task draft](step1.8-codex-control-context-focus-completion-TASK-DRAFT-2026-11-22.md).

## Implementation envelope and stop conditions

**Permitted implementation envelope, once authorized:** project CLI,
necessary existing broker/resident/single-launch modules, matching focused
tests, CLI help and user-facing reference documentation, with this task's
status/evidence. Do not modify Step 1.6/1.7 archived acceptance records;
modify authoritative architecture only to record a reviewed decision.

**Participation policy:** Target must be an ordinary visible NormalLayer
window. KWin's `normalWindow` alone is insufficient: KeepBelow/BelowLayer,
KeepAbove/non-NormalLayer, minimized, hidden, and opacity-zero peers are
*observed and protected*, not raised or required to be above the target.
The full raw UUID stack, protected-exclusion reasons, and participating stack
must remain independently checkable. This is a refinement of user-facing
`under`, not a persistent KWin keep-below property or class-specific bypass.

**Stop and return for review** if exact registered UUID authority fails,
focus/desktop ownership changes unexpectedly, settled stack cannot be proved,
peer relative order or geometry changes, or a persistent stacking policy,
new selector/native plugin or security/API expansion is needed. Inactive-
desktop peer raises are an explicit candidate exception, not blanket approval
for peer reflow. Never silently fall back to `over` or report an unverified
position as successful.

**Reserved operations:** the maintainer controls task authorization,
commits/PR/merge, native operations, service restarts and all
`joetoo-upstream`/`joetoo` integration. Neither this HANDOFF nor another
agent's notes grant those permissions.

## Final review and completion

The maintainer accepted the tested Version 1 behavior and merged
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36), creating
`main` commit `67c054c`. All earlier review and stop-boundary discussions
above are historical. See the [closure record](step1.8-pr36-merge-closure-2026-11-23.md).

**Next active dispatcher:** [Step 1.9](../../task_1.9/HANDOFF.md).
No KWin 6.8 upgrade or Version 2 panel feature is required for the initial
0.1.0 package release.
