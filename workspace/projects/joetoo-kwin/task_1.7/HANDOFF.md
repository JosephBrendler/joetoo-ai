# Step 1.7 — Recovery and last-good layout HANDOFF

**Current status (2026-11-18):** This is the **next version 1 milestone**.
The maintainer accepted and merged Step 1.6 through
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)
(`a6999e2`) and agreed to combine the previously separate Steps **1.7 and
1.8** into **one Step 1.7 recovery/snapshot delivery**. The two underlying
contracts remain distinct. **Implementation has not yet been authorized or
reported as started.**

## Source and authority

- Repository/project: `JosephBrendler/joetoo-ai`, `workspace/projects/joetoo-kwin/`.
- Accepted starting point: `main` at PR #32 merge `a6999e2`; recheck actual
  HEAD/worktree before starting a future task branch.
- Governing instructions: repository root, `workspace/` and project
  `AGENTS.md`; current [architecture](../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
- Accepted predecessor: [archived Step 1.6 HANDOFF](../archive/task_step1.6/HANDOFF.md),
  [task README](../archive/task_step1.6/README.md),
  [native X11 evidence](../archive/task_step1.6/step1.6-slim2-native-x11-evidence-2026-11-18.md)
  and [Wayland/XWayland sweep](../archive/task_step1.6/step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
- This HANDOFF is a planning/continuity record, **not** permission to edit code,
  run native tests, deploy, publish or change protected repositories.

## Objective — one delivery, two bounded responsibilities

**A. Private same-session checkpoint/reconciliation.** Allow a broker restart
inside an unchanged KWin session to recover only authenticated, still-live
managed UUIDs and their logical reservations. Keep broker memory authoritative
while running. Checkpoint privately/atomically; verify source/session and exact
UUID on replay; unknown or changed identity must be non-destructive. Broker
stop/restart must neither close nor automatically relaunch applications.

**B. Durable last-good launch intent.** Maintain a separate validated `.conf`
that describes selected launch recipes and layout without reusing old PIDs,
UUIDs, ephemeral process/connection state or secrets. `-S` exports an authorized
selection; `-r` performs ordinary validated, confirmed launches of **new**
instances after a logout/reboot or explicit restore. Failed or empty activity
must not silently replace last-good state. `-d` / `-x` must not erase it.

These artifacts **must not be conflated**: the runtime checkpoint is a
same-session identity aid, not a reboot restore recipe; the durable plan is
launch intent, not authority to adopt or close an existing window.

## Next actor and decisions before coding

**Next actor: maintainer**, reviewing the four focused open design questions in
[Architecture §8](../ARCHITECTURE.md#version-1-decisions-to-resolve-before-implementing-this-workstream):

1. Which broker/KWin session and source proof is sufficient for conservative
   same-session reconciliation, particularly when a restart races with KWin exit?
2. When does a desired arrangement become **last-good**, including partial
   runs, unreachable SSH placeholders and manually adjusted geometry?
3. What exact selection/permission contract should `-S` provide, and how are
   unmanaged windows, credentials and accidental overwrite excluded?
4. What is the minimal same-session-restart versus new-instance-restore
   acceptance matrix on native X11 and Wayland/XWayland?

Resolve these inside **one** Step 1.7 scope, not by creating another stage or
independent Step 1.8 authorization gate. After a bounded maintainer review,
prepare the existing project branch/diff/test workflow. Do not reimplement
accepted `-d`, `-x`, registry identity, or remote-launch machinery.

**Following Step 1.7:** Step 1.9 version 1 packaging remains separate and
maintainer-led. [Version 2 Considerations](../ARCHITECTURE.md#12-version-2-considerations)
are explicitly deferred and not acceptance criteria here.
