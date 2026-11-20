# Step 1.6 — Accepted managed-close milestone

> **Archive closure (2026-11-18):** Step 1.6 was accepted and merged into `main` by [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32) (`a6999e2`). This document preserves its historical stage and may refer to then-pending publication or authorization. Step 1.7 is [also archived](../task_step1.7/README.md); current work is [Step 1.9](../../task_1.9/HANDOFF.md).

**Maintainer decision: ACCEPTED on 2026-11-18.** The feature is accepted on
`task/joetoo-kwin-step1.6-managed-close`; a pull request and merge into
`main` are separate, still-pending publication actions. The task branch
inspected for this documentation pass is `65e4e6be1af7eb94a472f86c08372874e5236b43`.

## Delivered contract

- `-d MANAGED_ID`: confirm one exact-identity graceful close; retain its
  managed ID, desktop/slot reservation and historical record.
- `-x`: confirm one fixed snapshot; retire authenticated missing records and
  verified gracefully closed windows **progressively**; retain failed or
  unresolved entries, stop only where cleanup uncertainty makes further
  native dispatch unsafe; full success gives an empty `-l` without restart.
- Confirmations are mandatory; no force kill, PID/title-based adoption, or
  implicit remote-session/broker termination. `-D` individual retirement is
  deferred to Version 2, not Step 1.6.

## Maintainer-executed native acceptance

| Host/backend | Reported verification | Result |
| --- | --- | --- |
| `q552u01` KWin Wayland/XWayland | 1,016 Python, 163 JS; 8 native closes and 1 already-missing retirement | **9/9 retired**, empty inventory without broker restart |
| `slim2` KWin X11 6.7.6 | Native effect installation/owner proof, 1,016 Python, 163 JS, 15/15 configured launches, two retained `-d` closes | **16/16** (2 missing + 14 verified X11 closes); retained result query passed |
| `slim2` negative paths | Declined `-d` and `-x`, Konsole's real quit-confirmation/refusal and timeout | No forced close or premature retirement; truthfully retained unresolved record |

The live unsupported-`WM_DELETE_WINDOW`/stale-XID race fixture,
mid-transaction invoking-terminal disappearance, and independently traced
SSH/RDP/VNC worker/remote-session cleanup were not fully demonstrated.
Headless safeguards were tested; the maintainer explicitly accepted this
milestone without treating unperformed native edge tests as passes.

## Authoritative evidence and references

- [slim2 X11 native evidence (November 17–18)](step1.6-slim2-native-x11-evidence-2026-11-18.md),
  including [supporting-originals](supporting-originals) for screenshots and
  operator-captured logs.
- [q552u01 progressive-sweep implementation and native evidence](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
- [Earlier q552u01 Wayland evidence](step1.6-native-wayland-evidence-2026-11-16.md) — historical result before the correction.
- [Native adapter contract and regression checklist](../../native/managed-close/README.md).
- [Accepted predecessor Step 1.5](../task_step1.5/README.md) and
  [native acceptance evidence](../task_step1.5/step1.5d-native-acceptance-2026-11-12.md).
- [Active accepted-milestone HANDOFF](HANDOFF.md), [project README](../../README.md),
  [architecture](../../ARCHITECTURE.md).

Historical Step 1.6 candidate drafts, initial HANDOFF and test addenda remain
available as evidence of how the implementation evolved. They are **not**
active assignments, permission to reimplement successful behavior, or a source
of new release gates. Deferred design belongs in
[Version 2 Considerations](../../ARCHITECTURE.md#12-version-2-considerations),
not in this task index.

## Closure and next work

Review this documentation update, commit/push if approved, open the Step 1.6
PR into `main`, inspect the PR diff/CI, and merge through the normal maintainer
process. No additional Step 1.6 implementation or native test is required for
this acceptance decision.

Next **version 1** planning: treat Steps 1.7 and 1.8 as one proposed
recovery-and-snapshot delivery, with distinct private same-session checkpoint
and durable restorable-configuration responsibilities. Its open design choices
and Step 1.9 packaging remain future scope; no implementation is authorized
merely by this accepted Step 1.6 record.
