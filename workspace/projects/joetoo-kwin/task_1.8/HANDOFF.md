# Step 1.8 (new) — Version 1 CLI completion HANDOFF

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-21): TASK ESTABLISHED; IMPLEMENTATION AND ACCEPTANCE PENDING.**
The maintainer reports creating branch
`task/joetoo-kwin-step1.8-cli-completion` and placing the planning outline in
`task_1.8/`. These HANDOFF/README drafts await maintainer review/integration;
no Step 1.8 implementation, tests, native acceptance or merge is claimed.

**Historical boundary:** **All Steps 1.1–1.7 are accepted and closed.**
Step 1.6 (`-d`/`-x`) was accepted and merged via
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32); Step 1.7
(recovery, `-S` and `-r`, *including the former Step 1.8*) was accepted and
merged via [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33).
The **new** Step 1.8 is not a reopening or re-acceptance of either step.

## Authority, baseline and scope

- **Repository/project:** `JosephBrendler/joetoo-ai`,
  `workspace/projects/joetoo-kwin/`.
- **Accepted base:** maintainer-pushed `main` commit **`7fdd2cf`** (Step 1.9
  scope/documentation update). The maintainer reports an existing local task
  branch; verify that branch HEAD and worktree before implementation. Do not
  assume its unpublished outline is available remotely.
- **Active branch (maintainer-reported):**
  `task/joetoo-kwin-step1.8-cli-completion`.
- **Authoritative design:** [ARCHITECTURE §9](../ARCHITECTURE.md#9-cli-contract-accepted-behavior-and-proposed-step-18-completion),
  [§11](../ARCHITECTURE.md#11-numbered-implementation-and-review-gates),
  and [§12](../ARCHITECTURE.md#12-version-2-considerations).
- **Task scope and tests:** [Step 1.8 README](README.md); the
  [maintainer-placed outline](joetoo-kwin-new-step18-branch-and-acceptance-outline.md)
  provides the initial work order. Check its actual basename locally.
- **Accepted predecessor evidence:** [Step 1.5 archive](../archive/task_step1.5/README.md),
  [Step 1.6 closure](../archive/task_step1.6/README.md), and
  [Step 1.7 closure](../archive/task_step1.7/README.md) are completed history,
  not active implementation instructions.

**Bounded new behavior:** implement read-only `-s` using existing broker
`RegistryStatus()`, read-only `-i MANAGED_ID` using existing `GetManaged()`, and
verified one-shot `-L ... under` for **only the newly managed window**. Preserve
`-L` omitted/explicit `over` and configured `-o` layer behavior. `-L panel`
and all peer geometry/reflow remain Version 2.

## Next actor, assignment and stop conditions

**Next actor: maintainer**, to review/integrate these documents and designate
implementation authority. A suitable first bounded implementation assignment
is `-s` and `-i` CLI parsing, rendering and headless tests using the existing
broker methods. The second bounded portion is the minimal `-L under`
broker/resident extension plus focused tests; **native X11 and Wayland
execution requires separate maintainer approval**.

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
