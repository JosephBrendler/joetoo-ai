# Step 1.6 — Managed operations HANDOFF

**Status (2026-11-14): Step 1.6 INITIALIZED — documentation/archive transition prepared; publication pending. Detailed implementation scope not yet approved.**

## 1. Task identity and authority

**Repository:** `JosephBrendler/joetoo-ai`\
**Project:** `workspace/projects/joetoo-kwin/`\
**Transition branch:** `task/joetoo-kwin-step1.5-archive-step1.6-init`\
**Reviewed base:** `231e3c3c7e77839ef9220cf1c128f7a1572726d0`\
**Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)\
**Task index:** [README.md](README.md)

Step 1.6 is the active development milestone. This HANDOFF records the current assignment and authorization boundaries; it does not independently grant permission. Neither the architecture roadmap nor historical task instructions authorize implementation, native operations or publication.

## 2. Accepted predecessor

Step 1.5 is complete.

- Step 1.5c.5d accepted and merged through [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29) at `3e9c4bf311bc65b32d332a00d3b50163a9043303`.
- Step 1.5d accepted and merged through [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30) at `f72407278fa0a9c923079f3b38ce834440d2fef2`.
- Accepted behavior includes configured managed launches, exact-UUID registration and placement, remote access integration, single-window `-L` launch, read-only `-l` inventory, and verified one-shot raising of newly launched managed windows.
- Final XCB test-fixture correction and regression evidence are preserved in the [native acceptance record](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md) and [fixture addendum](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md): 7 focused Python, 1,000/1,000 stress repetitions, 100 additional leak-check repetitions, 949 full Python and 163 JavaScript passes. These recorded results were not rerun during this documentation task; the original 948/949 result and eleven passing reruns remain intact.

Historical records: [archived Step 1.5 README](../archive/task_step1.5/README.md) and [closed HANDOFF](../archive/task_step1.5/HANDOFF.md).

These completed milestones are accepted foundations, not outstanding work.

## 3. Documentation transition

The Step 1.5 archival and Step 1.6 initialization changes have been prepared on the transition branch.

The initial transition was checkpointed by the maintainer at `cfb3a7b13276a31a9092b70f2f0a7334443f33d5`. This final documentation acceptance-preparation round preserves that checkpoint and the initial historical HANDOFF.

Transition validation:

- All 213 tracked Step 1.5 artifacts moved to `archive/task_step1.5/`, with filenames and modes preserved.
- Historical evidence retained and closure notices added; 205 artifacts are byte-identical, with eight Markdown files changed only for closure/navigation and one equivalent Markdown hard-break spelling.
- Project README, architecture, configuration reference and archive navigation updated.
- New Step 1.6 HANDOFF and README created.
- Relative Markdown navigation rechecked, with no newly broken targets. The initial scan's 27 pre-existing missing-target occurrences are distinguished from the 23 retained historical occurrences; four were repaired or removed from current navigation.
- Runtime code, tests, installers and configuration behavior unchanged.
- Complete rename-aware diff, file-mode checks, whitespace validation and reverse-apply consistency check prepared for review, including all new files.

**Current publication state:** The documentation transition is locally prepared and checkpointed by the maintainer; this round's final HANDOFF/README edits remain uncommitted and unstaged. Remote publication state is not asserted. Final file review and explicit authorization to commit, push, create a PR and merge remain required; Codex has performed none of those actions.

Upon PR merge, record the final merge commit and update this status to reflect the accepted documentation baseline.

## 4. Step 1.6 objective

The intended milestone is safe management of existing and newly added managed windows through:

- `-a` — add a managed window; precise interface and relationship to accepted `-L` require review.
- `-d MANAGED_ID` — selective graceful close.
- `-x` — graceful closure of positively identified managed windows.

Detailed CLI semantics, ownership proof, missing-window handling, timeout behavior, partial failures and application-specific lifecycle consequences remain to be established and approved.

## 5. Invariants and exclusions

Preserve exact managed UUID identity, source and ownership validation, retained missing reservations, existing broker protections and isolation of unrelated windows.

Never close or adopt a window using class, title or PID alone, or substitute an observed UUID for the managed identity.

Keep separately scoped outcomes distinct: window placement, managed-window lifecycle, RDP/VNC connection state, and independent broker/service lifetime.

Step 1.7 runtime checkpoint/restart reconciliation, Step 1.8 durable last-good layout/restore, Step 1.9 packaging, and unrelated architectural redesign remain outside this task.

## 6. Development and native testing hosts

- **q552u01:** Primary development host, native KWin Wayland; first planned native testing.
- **slim2:** Subsequent native X11 testing.
- **gmki91:** Additional X11 development and testing when available.

Host assignments do not themselves authorize native test execution, service changes or destructive operations.

## 7. Next actor and authorization

**Immediate next actor:** maintainer, for final file review and an explicit publication decision. No publication action is authorized by this HANDOFF.

**Next engineering actor:** Codex, only upon separate maintainer authorization, for a read-only Step 1.6 source and contract review after the documentation transition is merged. That review is not started by this documentation assignment.

The review should establish:

1. Current implementation status of `-a`, `-d`, `-x`, `-L` and `-l`.
2. Relevant CLI, managed registry, broker and resident interfaces.
3. Safe-closure identity and authorization requirements.
4. Unsettled behavioral choices requiring maintainer decisions.
5. Proposed incremental implementation and headless/native acceptance strategy.

**Not yet authorized:** Step 1.6 implementation, native host operations, service restarts, destructive window tests, commit, push, PR creation or merge.

## 8. Next decision

First, review and publish the documentation/archive transition.

Then approve a separate read-only Step 1.6 architecture/source review. Decide the detailed implementation contract before authorizing code changes.

Historical evidence and earlier draft instructions must not override this HANDOFF or subsequent explicit maintainer decisions.
