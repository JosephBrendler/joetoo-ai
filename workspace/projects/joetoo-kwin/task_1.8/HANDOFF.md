# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-22): ACTIVE; read-only `-s` and `-i` native-smoke-tested;
first `-L under` candidate installed and smoke-tested on q552u01 Wayland:
desktop 3 PASS, desktop 1 protected-layer verification false negative.
Property-based participation follow-on is proposed, untested natively and
not yet accepted.** `-L panel` remains excluded. Step 1.8 is not merged.

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
- **Active branch:** `task/joetoo-kwin-step1.8-cli-completion`, pushed HEAD
  **`f84a8ec`** (maintainer-pushed 2026-11-22 documentation/evidence
  update). The `-L under` candidate is not committed or published.
- **Authoritative design:** [ARCHITECTURE §9](../ARCHITECTURE.md#9-cli-contract-accepted-behavior-and-proposed-step-18-completion),
  [§11](../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../ARCHITECTURE.md#12-version-2-considerations).
- **Task scope and tests:** [Step 1.8 README](README.md); the
  [maintainer-placed outline](step18-branch-outline.md)
  provides the initial work order.
- **Current native evidence:** [q552u01 read-only Wayland](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md),
  [slim2 read-only X11](step1.8-slim2-readonly-x11-evidence-2026-11-22.md), and
  [q552u01 V2/V3 lower feasibility, screenshots](step1.8-q552u01-one-shot-lower-feasibility-2026-11-22.md).
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

**Latest native integration:** On q552u01 KWin 6.7.6 Wayland the maintainer
applied the first candidate, passed focused headless suites (14 Python CLI,
19 Python broker, 40 JavaScript resident), and installed/reloaded it using
`tools/restart_joetoo-kwind notest`. `-L 3 konsole ssh nuthuvia under`
registered `win-014` and completed. `-L 1 ... under` registered and placed
`win-013` but reported incomplete stacking: KWin correctly left a 64x36
`xwaylandvideobridge` protected surface below the newly lowered Konsole.
[Integrated native results and follow-on policy](step1.8-q552u01-under-integrated-participation-2026-11-22.md).

**Next actor: maintainer**, to review and apply the follow-on participation
patch, run focused and full regressions, then repeat `-L under` on desktops
1 (protected lower-layer bridge) and 3 (ordinary peers), including an inactive
third-desktop trial before Step 1.8 acceptance. The
candidate's on-desktop path uses verified active-window lowering; its proposed
inactive-desktop fallback raises eligible existing peers in their prior order,
without desktop/focus switching, then verifies target bottommost and peer
frames/order unchanged. That fallback is a *narrow proposed relaxation* of the
earlier no-peer-restacking rule; it is not yet native-proven/accepted. A smaller
slim2 X11 compatibility run can follow. No service restart is authorized by
this HANDOFF alone.

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
