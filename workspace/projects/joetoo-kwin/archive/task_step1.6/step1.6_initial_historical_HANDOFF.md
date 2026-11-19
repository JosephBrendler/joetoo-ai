# Step 1.6 — Managed operations dispatcher

> **Archive closure (2026-11-18):** Step 1.6 was accepted and merged into `main` by [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32) (`a6999e2`). This document preserves its historical stage and may refer to then-pending publication or authorization; the current work is [Step 1.7](../../task_1.7/HANDOFF.md).

## Status, current authority and next actor

**2026-11-14: Step 1.6 is the active milestone; detailed implementation scope
is not approved.** The maintainer authorized the Step 1.5 archive/documentation
transition and initial Step 1.6 records only. That candidate awaits review.

**Next actor: maintainer**, to review this transition and separately authorize
a **read-only Step 1.6 source/contract review**. Do not begin that engineering
review merely because this HANDOFF exists. No `-a`, `-d` or `-x` implementation,
destructive operations, native tests, host/service actions or publication
(commit/push/PR/merge) are authorized.

## Baseline and references

- Repository: `JosephBrendler/joetoo-ai`.
- Reviewed clean `main`: `231e3c3c7e77839ef9220cf1c128f7a1572726d0`.
- Documentation candidate branch:
  `task/joetoo-kwin-step1.5-archive-step1.6-init`.
- Step 1.5d accepted and merged through
  [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30) at
  `f72407278fa0a9c923079f3b38ce834440d2fef2`.
- [Architecture](../../ARCHITECTURE.md), [project status](../../README.md),
  [task index](README.md), [completed Step 1.5](../task_step1.5/README.md).
- Verify actual branch, HEAD, worktree and maintainer feedback before any
  separately authorized assignment. Preserve newer changes.

## Objective and existing source foundation

The architecture targets managed `-a`, `-d MANAGED_ID` and `-x`.
The precise `-a` syntax and relationship to accepted `-L` require review and
maintainer approval; do not assume adoption of preexisting windows.

Current `-L` and `-l` are implemented. `-d` and `-x` remain CLI stubs;
`-a` is not implemented. Existing `ListManaged`, `GetManaged` and
`RegistryStatus` are read-only foundations, not destructive capabilities.
The registry itself does not grant close authorization.

Preserve exact UUID ownership, source/owner validation, retained reservations,
graceful confirmed closure, unrelated-window protection and service/application
lifetime separation. Preserve accepted launch, placement, stacking, configuration,
RDP security and VNC/SSH lifecycle contracts. Detailed close authorization,
bounded failure handling and any additive API require an approved scope.

## Development and acceptance hosts

| Host | Maintainer-designated role | Native backend |
| --- | --- | --- |
| `q552u01` | Initial development and acceptance host | KDE Wayland |
| `slim2` | Subsequent native X11 testing | KDE X11 |
| `gmki91` | Additional native X11 validation | KDE X11 |

Host roles are planning context, not permission for native execution.
Historical Step 1.5 acceptance remains attributed to its actual hosts.

## Boundaries and progress

No Step 1.6 implementation, tests or native acceptance are claimed.
Step 1.7 checkpoint/restart recovery, Step 1.8 durable restore, Step 1.9
packaging and Option D concurrent remote missions remain separate work.
Do not modify protected repositories, install/restart services or publish
without explicit maintainer authorization.
