# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-23): ACTIVE — native functional and regression evidence
collected; final focus-policy decision and maintainer acceptance pending.**
Current branch `task/joetoo-kwin-step1.8-cli-completion` at pushed
`4be1b0b` (`fix restore focus step1.8`), plus four uncommitted local files.
Native X11/Wayland `-L under`, CLI `-s`/`-i`, configured `-o`, and
managed-close recovery checks have positive evidence. q552u01's latest full
suites: **1,113 Python + 180 JavaScript PASS**, plus **54** focused POC
installer tests PASS. The original Konsole regained usable keyboard focus
on Wayland after both `-L` and `-o`.

**OPEN acceptance decision:** a displayed-desktop configured `-o` `panel`
launch successfully verified its preferred new Konsole, but the shared
completion path then activated the *original control Konsole*. This
conflicts with the prior requirement to preserve intentional preferred
focus; the current restore path also lacks proven competing-user-activation
protection. The maintainer must either authorize a documented policy change
(with its safety implications reviewed) or authorize a narrow guard/fix and
focused revalidation. **Do not mark Step 1.8 accepted yet.**

**New evidence:** [2026-11-23 q552u01 focus, managed-close and regression
record](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md), with
[console transcript](step1.8-q552u01-acceptance-console-2026-11-23.txt)
and [preferred-focus screenshot](screenshots/20261123-q552u01-wayland-panel-focus-override.png).
`-L panel` remains unsupported. Step 1.9 production packaging remains paused.

**Historical boundary:** **All Steps 1.1–1.7 are accepted and closed.**
Step 1.6 (`-d`/`-x`) was accepted and merged via
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32); Step 1.7
(recovery, `-S` and `-r`, *including the former Step 1.8*) was accepted and
merged via [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33).
The **new** Step 1.8 is not a reopening or re-acceptance of either step.

## Authority, baseline and scope

- **Repository/project:** `JosephBrendler/joetoo-ai`,
  `workspace/projects/joetoo-kwin/`.
- **Accepted `main` reference:** maintainer-pushed `7fdd2cf` (Step 1.9
  scope/documentation update). The task branch's actual merge-base is
  `24cd67f`; reconcile ancestry when preparing the Step 1.8 PR, not by an
  unreviewed rebase during native testing.
- **Active branch:** `task/joetoo-kwin-step1.8-cli-completion`, pushed
  HEAD **`4be1b0b`** (focus restoration), following `1747017`, `5ab6ea6`
  and `73afa19`. Four additional files are locally modified and uncommitted
  as of the 2026-11-23 maintainer status review.
- **Authoritative design:** [ARCHITECTURE §9](../ARCHITECTURE.md#9-cli-contract-accepted-behavior-and-proposed-step-18-completion),
  [§11](../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../ARCHITECTURE.md#12-version-2-considerations).
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
## Current next actions — 2026-11-23

1. **Focus-policy decision is the only identified substantive acceptance
   blocker.** Current `-o` `panel` initially activated its preferred new
   Konsole (UUID `d84c39fe-64cd-4d58-b58b-860565bfd693`), then the
   global completion path requested control restoration, and the maintainer
   typed in the original Konsole without clicking. Determine whether
   returning to the controller after `-o` is now explicitly accepted, or
   whether `-o` should retain intentional preferred focus. Separately review
   competing user/client activation: source does not establish a distinct
   user-intent veto before its final KWin activation. Record the policy
   disposition; if code changes are needed, apply narrowly and rerun focused
   tests/native revalidation. Do not reinterpret passing launch/stacking
   transactions as failed merely because post-mission focus policy is open.
2. **Review and incorporate pending four-file local diff:**
   `tools/joetoo-kwind-install-poc`, `tests/test_openrc_user_setup.py`,
   `tools/restart_joetoo-kwind`, and the Step 1.9 packaging-inventory draft.
   The POC now installs/verifies/archives `joetoo_kwin_sftp_target.py` (15
   user-owned files); Step 1.9 retains the independent production `${ED}`
   installed-tree completeness/isolation gate. Development restart now checks
   `joetoo_managed_close` and polls KWinBridge/KWinCloseNative D-Bus readiness.
   The already-loaded branch and service readiness passed on q552u01; the
   restart helper's automatic-load branch was not separately tested.
3. **Documentation and review:** reconcile `ARCHITECTURE.md`'s stale `-L
   under` text and the chosen preferred-focus policy; retain Step 1.8 native
   evidence links. Human `-s` display of `single_lower=1` is optional polish.
   One isolated earlier desktop-3 RDP failure was not attributed to stacking;
   do not treat unverified remote connectivity as a Step 1.8 gate.
4. **Reconcile branch ancestry:** `main` at `7fdd2cf`, Step 1.8 branch at
   `4be1b0b`, merge-base `24cd67f`. `main`'s one intervening commit touches
   `ARCHITECTURE.md` and three Step 1.9 docs. Both sides changed
   `ARCHITECTURE.md`; the local Step 1.9 packaging-inventory edit also
   overlaps `main`. Compare deliberately; do not assume conflict-free merge
   or perform an unreviewed rebase.
5. **After explicit maintainer policy and technical acceptance:** review
   final diff and evidence, commit/push authorized changes, prepare/review the
   PR and merge. On accepted merge, close Step 1.8 and resume Step 1.9.

  and **[2026-11-23 q552u01 closeout evidence](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md)**.
- **Accepted predecessor evidence:** [Step 1.5 archive](../archive/task_step1.5/README.md),
  [Step 1.6 closure](../archive/task_step1.6/README.md), and
  [Step 1.7 closure](../archive/task_step1.7/README.md) are completed history,
  not active implementation instructions.

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

## Review and completion boundary

For maintainer review, provide one bounded diff, focused test results,
explicit limitations, and native Wayland/X11 results (when authorized),
including unaffected `-o`, `-L over`, `-l`, managed close and Step 1.7
recovery behavior. The maintainer alone decides acceptance/merge.

**On accepted merge:** Step 1.8 is closed, and the next active dispatcher
returns to [paused Step 1.9](../task_1.9/HANDOFF.md) for source stabilization,
human maintainability-comment review, curated transfer, `tarup` and packaging.
No KWin 6.8 upgrade, new remote client or Version 2 panel feature is a Step
1.8 or initial 0.1.0 prerequisite.
