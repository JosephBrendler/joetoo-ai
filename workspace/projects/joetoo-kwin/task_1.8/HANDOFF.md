# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-22): ACTIVE; read-only `-s` and `-i` IMPLEMENTED and
native-smoke-tested on Wayland and X11; maintainer acceptance PENDING.**
Step 1.8's remaining functional work is verified one-shot `-L ... under`.
`-L ... panel` remains excluded. No Step 1.8 merge or acceptance is claimed.

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
  **`cadf992`** and confirmed clean/synchronized on `q552u01` and `slim2`
  in the maintainer's 2026-11-22 console output.
- **Authoritative design:** [ARCHITECTURE §9](../ARCHITECTURE.md#9-cli-contract-accepted-behavior-and-proposed-step-18-completion),
  [§11](../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../ARCHITECTURE.md#12-version-2-considerations).
- **Task scope and tests:** [Step 1.8 README](README.md); the
  [maintainer-placed outline](step18-branch-outline.md)
  provides the initial work order.
- **Current native evidence:** [q552u01 Wayland](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md)
  and [slim2 X11](step1.8-slim2-readonly-x11-evidence-2026-11-22.md).
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

**Next actor: maintainer**, to review/integrate this documentation update and
continue the already scoped Step 1.8 work. **Next technical action:** establish
on KWin 6.7.6 Wayland and X11 whether a safe one-shot `lowerWindow` operation
and trustworthy bottom-to-top stack readback are available, initially by a
nonmutating capability probe. If feasible, extend existing single-`over`
launcher/broker/resident transaction to support exact-UUID `under` with focused
tests; no peer reflow, new selector or persistent keep-below policy. Native
operations and restarts remain maintainer-controlled.

## Implementation envelope and stop conditions

**Permitted implementation envelope, once authorized:** project CLI,
necessary existing broker/resident/single-launch modules, matching focused
tests, CLI help and user-facing reference documentation, with this task's
status/evidence. Do not modify Step 1.6/1.7 archived acceptance records;
modify authoritative architecture only to record a reviewed decision.

**Stop and return for review** if `under` cannot be implemented with a
positively identified, bounded and read-back-verified lower on either
supported KWin 6.7.6 backend; if achieving it requires rearranging peers,
new permanent stacking policy, unsafe activation or a different identity
mechanism; or if new security/API scope is necessary. Never silently fall
back to `over` or treat an unverified stack position as success.

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
