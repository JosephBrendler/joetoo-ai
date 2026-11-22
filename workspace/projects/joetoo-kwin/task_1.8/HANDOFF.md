# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-22): ACTIVE; implementation pushed at `73afa19`.**
Read-only `-s`/`-i` have native Wayland and X11 smoke evidence. Corrected
one-shot `-L under` now has successful q552u01 Wayland integration on the
displayed target desktop (including the protected `xwaylandvideobridge` case)
and on an inactive target desktop with **no desktop switch**. The maintainer
also reports a successful VNC `under` and RDP `over` local launch. Focused
post-repair suites passed; the post-repair *full* suite and slim2 native X11
`-L under` compatibility remain pending. No Step 1.8 acceptance, PR merge,
or `-L panel` support is claimed.

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
- **Active branch:** `task/joetoo-kwin-step1.8-cli-completion`, maintainer-
  pushed HEAD **`73afa19`** (`joetoo-kwin -L ... under implementation`),
  confirmed tracked to `origin/task/joetoo-kwin-step1.8-cli-completion`
  on q552u01. This HANDOFF evidence update is a subsequent *proposed*
  uncommitted documentation change until the maintainer applies/pushes it.
- **Authoritative design:** [ARCHITECTURE §9](../ARCHITECTURE.md#9-cli-contract-accepted-behavior-and-proposed-step-18-completion),
  [§11](../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../ARCHITECTURE.md#12-version-2-considerations).
- **Task scope and tests:** [Step 1.8 README](README.md); the
  [maintainer-placed outline](step18-branch-outline.md)
  provides the initial work order.
- **Current native evidence:** [q552u01 read-only Wayland](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md),
  [slim2 read-only X11](step1.8-slim2-readonly-x11-evidence-2026-11-22.md),
  [q552u01 V2/V3 lower feasibility and screenshots](step1.8-q552u01-one-shot-lower-feasibility-2026-11-22.md),
  [first integrated native lower / protected-bridge failure](step1.8-q552u01-under-integrated-participation-2026-11-22.md),
  and **[corrected Wayland native validation and test logs](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md)**.
- **Accepted predecessor evidence:** [Step 1.5 archive](../archive/task_step1.5/README.md),
  [Step 1.6 closure](../archive/task_step1.6/README.md), and
  [Step 1.7 closure](../archive/task_step1.7/README.md) are completed history,
  not active implementation instructions.

**Bounded new behavior:** implement read-only `-s` using existing broker
`RegistryStatus()`, read-only `-i MANAGED_ID` using existing `GetManaged()`, and
verified one-shot `-L ... under` for **only the newly managed window**. Preserve
`-L` omitted/explicit `over` and configured `-o` layer behavior. `-L panel`
and all peer geometry/reflow remain Version 2.

## Latest result and next actor

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
passed **14/14**. The **full** Python/JS suite has **not** been rerun after
repair. A restart-time D-Bus introspection briefly reported no broker, but
subsequent `rc-service` and `RegistryStatus` confirmed `recovery=ready`,
observer synchronized, `single_lower_protocol=1`, and no Busy/uncertain
flags. Raw `-s` output still omits the `single_lower` capability from its
human summary (presentation-only gap).

**Next actor and priority: maintainer — slim2 native X11 compatibility.**
Synchronize `task/joetoo-kwin-step1.8-cli-completion` at `73afa19` on slim2;
check current native-X11 KWin version/session, source/install coherence,
ready broker and `single_lower_protocol=1`. With disposable new windows,
validate an `-L under` launch on the displayed desktop and, if safe, one
inactive-desktop `under` with no involuntary desktop/focus switch, correct
UUID/slot/geometry and protected-peer behavior. Include a small `-L over`
non-regression check; avoid a wholesale RDP/VNC repeat. Maintainer operates
install, restart and native tests. Stop for an unsupported capability or
failed verifier rather than weakening the policy.

**After slim2:** run full post-repair Python and JavaScript suites, reconcile
all evidence (including the isolated desktop-3 RDP failure), address the
small `-s` capability-display omission, review `-o`/close/recovery risk as
appropriate, and prepare the Step 1.8 PR/ancestry reconciliation. Do not
claim acceptance or resume Step 1.9 until maintainer review/merge.

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
