# Step 1.6 — Managed operations HANDOFF

**Status (2026-11-16, evening): Step 1.6 candidate pushed, with substantial maintainer-native Wayland/XWayland close evidence. NOT ACCEPTED: the confirmed `-x` operation still retains records/reservations and requires the approved progressive clean-sweep refinement. Remaining native gates and publication are reserved.**

## 1. Task identity and authority

**Repository:** `JosephBrendler/joetoo-ai`\
**Project:** `workspace/projects/joetoo-kwin/`\
**Implementation branch:** `task/joetoo-kwin-step1.6-managed-close`\
**Reviewed base:** `cdcdc9e8c842d0be04447c06b90a25d3cc59f107` (PR #31 merged)\
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

## 3. Documentation transition (completed)

PR #31 merged the archive/init transition at `cdcdc9e`; the
[initial historical HANDOFF](step1.6_initial_historical_HANDOFF.md) preserves
that work. The maintainer subsequently pushed the Step 1.6 candidate with
corrected KWin plugin packaging, and executed q552u01 native tests.
See [2026-11-16 evidence](step1.6-native-wayland-evidence-2026-11-16.md).
Native evidence does not imply Step 1.6 acceptance or authorize publication.

## 4. Step 1.6 objective

- `-d MANAGED_ID`: positively authenticated graceful close of **one** managed
  window; **retain** registration, desktop/slot reservation and history.
- `-x`: broker-owned **progressive clean sweep** of the fixed snapshot after
  one confirmation. Retire each *already-missing* record/reservation as
  encountered and each eligible present record/reservation **immediately after
  verified graceful closure**. Do not wait for every other target before
  retiring independently verified entries. Flag individual failures and retain
  only minimal safety-critical unresolved state; continue other work whenever
  native dispatch can be performed safely. Full success leaves `-l` empty
  without broker restart.

Preserve exact UUID/owner proof, one confirmation, truthful bounded results
surviving CLI exit, isolated unrelated windows and graceful-only behavior.
A genuinely uncertain helper/owner/source is **not** proof of closure and may
block unsafe *native dispatch*, but must not roll back earlier verified cleanup.
Never force-kill, close by title/class/PID alone, or erase uncertain ownership.
`-D` individual close-and-retire is version 2; no `-a`, `-S`, `-r`, restore,
new native subsystem or general checkpoint/recovery in Step 1.6.

Current implementation retains all records for `-x`; this is the **first
remaining coding discrepancy**. See [Codex draft](DRAFT_Codex-Step1.6-x-progressive-sweep.md),
[evidence](step1.6-native-wayland-evidence-2026-11-16.md) and
[native adapter design](../native/managed-close/README.md).

## 5. Invariants and exclusions

Preserve source/owner/exact-UUID validation, the fixed authenticated snapshot,
existing broker serialization, and protection of unrelated windows. `-d`
retains missing reservations; **confirmed `-x` retires them progressively**.
No registration/slot mutation before explicit confirmation; no implied
rollback or forced process termination. Keep application, placement, RDP/VNC
connection and broker lifetime outcomes separate.

Step 1.7 checkpoint/reconciliation, Step 1.8 snapshots/restore and Step 1.9
packaging remain out of scope. `-x` must not erase a future last-good snapshot.

## 6. Development and native testing hosts

- **q552u01:** Maintainer-native KWin Wayland/XWayland tests performed 2026-11-16; remaining cases pending.
- **slim2:** Subsequent native X11 testing.
- **gmki91:** Additional X11 development and testing when available.

Host assignments do not themselves authorize native test execution, service changes or destructive operations.

## 7. Next actor and authorization

**Next actor:** maintainer to review and **explicitly authorize** the bounded
[`-x` Codex prompt](DRAFT_Codex-Step1.6-x-progressive-sweep.md).
After that authorization, Codex implements only the registry/retirement,
aggregate reporting and small CLI-preview correction on the existing task
branch; runs focused headless regressions; and returns a reviewable diff.
Codex must not perform native operations, deployment, commit, push or PR
without separate maintainer authority.

**First next action:** implement confirmed progressive `-x` record/slot
retirement without changing `-d` or adding version-2 `-D`.
**Then:** cloud code/test review; maintainer repeats q552u01 native `-x`
(mixed already-missing + present, post-run empty `-l`), refusal and
self-terminal/CLI-loss/worker-cleanup tests. Native X11 on `slim2` (optional
`gmki91`) remains outstanding, including XID reuse/fence and unsupported
`WM_DELETE_WINDOW` cases. All these are separate approval/test gates.

## 8. Recent decisions

- No `-a` requirement; `-L` already launches a new managed window. Older
  archived `-a` references are historical only.
- **2026-11-16 maintainer clarification:** `-x` is a destructive *managed
  collection sweep*, not simply repeated `-d`; confirmed safe removals occur
  progressively. `-d` retains registrations; `-D` is deferred to version 2.

## 9. Latest candidate result

**Maintainer native on q552u01 (2026-11-16):** corrected compiled effect
`joetoo_managed_close` discovered, supported and loaded after fresh Wayland
login; same D-Bus owner as KWin; OpenRC broker started with all close methods.
Declined `-d` closed nothing. Verified exact-UUID selective closes included
Dolphin, Konsole, SDL FreeRDP (Wayland) and TigerVNC (local XWayland); repeat
close was safely excluded. Confirmed `-x` closed **6/6** eligible targets,
but returned `partial` due to six already-missing exclusions, retained **all
12** records as `missing` and required a broker restart workaround for empty
inventory. Nano/Kate attempts were **not** a direct application-refusal test;
RDP/VNC/SSH worker cleanup and native X11 are not yet verified. Evidence:
[maintainer-native record](step1.6-native-wayland-evidence-2026-11-16.md).

**Prior Codex headless candidate (not rerun for this documentation or the
refinement):** 999 Python tests (998 PASS/1 SKIP due sandbox SO_PASSCRED),
107 focused (106 PASS/1 SKIP), 163 JavaScript PASS; both KWin 6.7.6 native
variants compiled; syntax and ShellCheck passed. These are pre-refinement
results, not evidence for corrected `-x`. See [task README](README.md).

## 10. Next decision

Review/authorize the focused `-x` implementation; then inspect its diff,
headless regression and subsequent maintainer-native evidence. Align stale
`-x` wording in the project architecture and native adapter README when the
code changes. **Step 1.6 is not yet accepted.** Commit/push/PR/merge and native
operations are separately reserved; historical records grant no authority.

Historical evidence and earlier draft instructions must not override this HANDOFF or subsequent explicit maintainer decisions.
