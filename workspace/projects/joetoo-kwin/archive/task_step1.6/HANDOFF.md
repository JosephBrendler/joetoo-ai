# Step 1.6 — Managed operations HANDOFF (accepted)

> **Archive closure (2026-11-18):** Step 1.6 was accepted and merged into `main` by [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32) (`a6999e2`). This document preserves its historical stage and may refer to then-pending publication or authorization; the current work is [Step 1.7](../../task_1.7/HANDOFF.md).

**Status (2026-11-18): ACCEPTED by the maintainer.** The implementation and its
principal native validation are complete. This is the accepted Step 1.6 scope,
not a request for more implementation or native testing. **PR publication and
merge remain pending**, independently of acceptance.

## Identity, baseline and authority

- Repository: `JosephBrendler/joetoo-ai`.
- Project: `workspace/projects/joetoo-kwin/`.
- Task branch: `task/joetoo-kwin-step1.6-managed-close`.
- Base: `main` at `cdcdc9e8` (PR #31 archive/init transition).
- Latest published branch inspected for this documentation review:
  `65e4e6be1af7eb94a472f86c08372874e5236b43` (2026-11-18).
- The maintainer reports that `slim2` and `q552u01` have been synchronized
  and subsequent documentation/evidence changes pushed; no old `8849e59`
  fast-forward work remains.
- Acceptance is a maintainer decision; this HANDOFF does not authorize repo
  publication, native execution, protected-repository integration or a new task.

## Accepted functionality

`-d MANAGED_ID` requests one authenticated graceful close and retains its
managed registration, original desktop/slot reservation and history (present
becomes missing on verified removal). `-x` confirms a fixed set once, then
**progressively retires** each authenticated missing entry and each verified
closed entry. Failed or unresolved entries remain; uncertain native cleanup
stops unsafe further dispatch without undoing prior verified retirement.
No force kill, title/PID-only adoption or application/broker lifecycle conflation.
No `-D`, restore, new checkpointing or extra general lifecycle framework in 1.6.

## Acceptance evidence

- [q552u01 Wayland/XWayland progressive sweep](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md):
  maintainer-run 1,016 Python OK, 163 JavaScript PASS; 8 verified live closes
  and 1 authenticated missing retirement (9/9); empty `-l` without restart.
- [slim2 native X11, refusal and confirmation evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md):
  KWin X11 6.7.6 native plugin build/install/owner checks; 1,016 Python OK,
  163 JavaScript PASS; 15/15 configured launches; two successful retained `-d`
  closes; 2 already-missing + 14 verified closes in `-x` (16/16 retired);
  empty `-l` without restart and status queryable after CLI exit; declined `-d`
  and `-x`; real Konsole close dialog/refusal with truthful timeout and
  retained registration.
- Supporting [original logs and screenshots](supporting-originals) are indexed
  in the slim2 evidence. Earlier [Wayland observations](step1.6-native-wayland-evidence-2026-11-16.md)
  remain historical evidence, not current instructions.

**Acceptance qualification (explicit, not a defect):** live-compositor fixtures
for absent `WM_DELETE_WINDOW`, stale/reused XID, mid-sweep invoking-terminal
loss and independently traced SSH/RDP/VNC worker/remote-session behavior were
not all demonstrated. Corresponding focused headless safety tests passed where
implemented. The maintainer has accepted Step 1.6 with those evidence limits
recorded; they are **not** prerequisites to this accepted milestone. Any future
reproduction of a real failure should be addressed narrowly on its merits.

## Next action and actor

**Next actor: maintainer — review documentation diff, commit/push if approved,
then open the Step 1.6 PR against `main`.** Inspect the PR diff/CI; merge is
separate from acceptance. No new Codex implementation task is necessary.
After integration, the next version 1 development objective is recovery and
last-good snapshots (the *proposed combined* Step 1.7–1.8 workstream).
Its same-session checkpoint and durable restorable plan remain separate data
and safety contracts within one potential delivery. See
[ARCHITECTURE.md](../../ARCHITECTURE.md#8-recovery-and-restorable-layout-proposed-combined-step-17-18-workstream)
for requirements, unanswered version 1 choices and the separate
[Version 2 Considerations](../../ARCHITECTURE.md#12-version-2-considerations).
This is a recommendation for subsequent maintainer scoping, **not an
implementation authorization**. Step 1.9 packaging remains future version 1.

**Closed milestone boundary:** do not create new Step 1.6 implementation
stages or treat historical draft prompts/older HANDOFFs as active work.
