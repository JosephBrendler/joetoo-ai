# Step 1.6 — Managed operations HANDOFF

**Status (2026-11-14): Step 1.6 INITIALIZED — documentation/archive transition prepared; publication pending. Detailed implementation scope not yet approved.**

## 1. Task identity and authority

**Repository:** `JosephBrendler/joetoo-ai`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Transition branch:** `task/joetoo-kwin-step1.5-archive-step1.6-init`  
**Reviewed base:** `231e3c3c7e77839ef9220cf1c128f7a1572726d0`  
**Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)  
**Task index:** [README.md](README.md)

Step 1.6 is the active development milestone. This HANDOFF controls the current assignment and authorization boundaries. Neither the architecture roadmap nor historical task instructions independently authorize implementation, native operations or publication.

## 2. Accepted predecessor

Step 1.5 is complete.

- Step 1.5c.5d accepted and merged through PR #29 at `3e9c4bf`.
- Step 1.5d accepted and merged through PR #30 at `f724072`.
- Accepted behavior includes configured managed launches, exact-UUID registration and placement, remote access integration, single-window `-L` launch, read-only `-l` inventory, and verified one-shot raising of newly launched managed windows.
- Final XCB test-fixture correction and regression evidence are preserved in the historical task archive.

Historical records: [archived Step 1.5 README](../archive/task_step1.5/README.md) and [closed HANDOFF](../archive/task_step1.5/HANDOFF.md).

These completed milestones are accepted foundations, not outstanding work.

## 3. Documentation transition

The Step 1.5 archival and Step 1.6 initialization changes have been prepared on the transition branch.

Codex reports:

- All 213 tracked Step 1.5 artifacts moved to `archive/task_step1.5/`, with filenames and modes preserved.
- Historical evidence retained and closure notices added.
- Project README, architecture, configuration reference and archive navigation updated.
- New Step 1.6 HANDOFF and README created.
- 468 relative link targets checked, with no newly broken targets.
- Runtime code, tests, installers and configuration behavior unchanged.

**Current publication state:** Local changes prepared, uncommitted and unstaged as of the initial completion report. Final maintainer review and separate Git publication authorization remain required.

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

Step 1.7 restart reconciliation, Step 1.8 checkpoint/recovery, Step 1.9 packaging, and unrelated architectural redesign remain outside this task.

## 6. Development and native testing hosts

- **q552u01:** Primary development host, native KWin Wayland; first planned native testing.
- **slim2:** Subsequent native X11 testing.
- **gmki91:** Additional X11 development and testing when available.

Host assignments do not themselves authorize native test execution, service changes or destructive operations.

## 7. Next actor and authorization

**Next actor:** Codex, upon separate maintainer authorization, for a read-only Step 1.6 source and contract review after the documentation transition is merged.

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
