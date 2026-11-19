# Step 1.7 — Combined recovery and last-good snapshot

**Status:** next version 1 workstream, **not yet implemented**. The maintainer
agreed that the former Steps **1.7 (same-session checkpoint)** and **1.8
(durable restorable layout)** should be developed and reviewed as one Step 1.7
milestone with **two separate data and trust contracts**. See the
[current HANDOFF](HANDOFF.md) for decisions and actor; it does not itself grant
code, native-operation or publication authorization.

## What this milestone covers

| Responsibility | Artifact and scope | Key acceptance distinction |
| --- | --- | --- |
| Same-session recovery | Private, atomic `$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json` checkpoint of authenticated managed identity and reservations | Reconcile **existing exact UUIDs** only after verifying unchanged KWin session/source; never close/relaunch on broker restart |
| Last-good layout | Separate trusted `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf` of validated desired launch recipes | `-S` exports only approved intent; `-r` confirms and launches **new** instances without adopting old windows/PIDs/UUIDs |

Keep the shared planner, existing configuration precedence and registration
security model. A correctly placed unreachable-SSH placeholder may be a
valid recipe despite unavailable transport; window/placement success remains
independent of remote login. Avoid an additional generic lifecycle framework.

## Continuity and sources

- [Architecture §8 and unresolved version 1 decisions](../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
- [Step 1.6 archived HANDOFF](../archive/task_step1.6/HANDOFF.md) and
  [accepted task index](../archive/task_step1.6/README.md).
- [Native X11 acceptance and original logs/screenshots](../archive/task_step1.6/step1.6-slim2-native-x11-evidence-2026-11-18.md).
- [Wayland/XWayland progressive-sweep evidence](../archive/task_step1.6/step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
- [Project README](../README.md), [project instructions](../AGENTS.md).

**Previous milestone:** Step 1.6 accepted and merged through
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)
(`a6999e2`). No additional Step 1.6 tests or implementation are prerequisites
for starting the next *authorized* work. Step 1.9 packaging follows this
version 1 objective; [Version 2](../ARCHITECTURE.md#12-version-2-considerations)
remains deferred.
