# Step 1.5c.5d — Increment 3/4 launch strategy decision (2026-11-08)

**Status: HISTORICAL — SUPERSEDED for Increment 4 (2026-11-10).** This 2026-11-08 strategy record is retained below as originally decided; it is no longer authoritative for current implementation, particularly its former open-ended human-authentication wait policy or task-dispatch references. The [Increment 4 maintainer decisions](step1.5c5d_Increment_4_decisions.md) carry forward the applicable strategy and establish finite, configurable five-minute RDP/VNC viewer-readiness defaults. Consult the [active HANDOFF](HANDOFF.md) for the current task and authorization.

## Decision

The first complete RDP/VNC managed-launch workflow will be **sequential, bounded in its machine operations, and deliberately human-interactive**. One candidate launch and broker registration/placement transaction proceeds to a safe terminal outcome before the next configured plan entry. The operator may spend several minutes or longer entering credentials; human inactivity alone does not justify killing the owned viewer/client or tunneling process. Keep authentication, registration, placement and remote-usability outcomes independent.

The purpose is to establish a reliable baseline using the already accepted broker, registry, resident KWin and launch-plan model. The current design favors correctness and clear failure/partial-completion reporting over maximum throughput.

## Considered strategies

| Strategy | Benefit | Cost or limitation | Decision |
| --- | --- | --- | --- |
| **1. Sequential interactive authentication** | Reuses serialized ownership and placement, simplest correctness model | A pending credential dialog pauses later plan entries | **SELECTED** for the first end-to-end implementation |
| 2. Launch all; stage independently identifiable pending prompts on a control desktop | Multiple remote requests can progress concurrently | Requires safe prompt identity, ownership, concurrency, cancellation and placement choreography | **DEFERRED** to measured Phase 2 evaluation |
| 3. Continue local launches while remote authentication is queued | Can improve throughput with bounded concurrency | Adds queue/scheduler state, reserved-slot and launcher-lock complexity | **DEFERRED** to measured Phase 2 evaluation |

The 500 ms X11 identity-settling interval is not the overall per-window launch duration or an operator password-entry limit. It applies only after one UUID begins qualifying as a persistent SDL viewer. There must not be an arbitrary short password-entry watchdog masquerading as a renderer/identity timeout.

## Implemented and planned boundaries

- **Increment 2 ACCEPTED:** On native X11, both `auto` and `software` register a correlated SDL viewer UUID without placement; after `software` titlebar closure, the same UUID stays recorded as missing. Native Wayland Increment 1 remains accepted. The known X11 temporary-viewer counterexample remains a limitation.
- **Increment 3:** implement deliberate, operator-confirmed placement of an *already registered* exact RDP viewer UUID, independently of whether the operator has proceeded past GDM. Do not move credential dialogs or claim remote readiness from window existence. No new configured `-o` RDP recipe.
- **Increment 4:** add RDP configured recipe validation and sequential `-o` orchestration; keep the launch plan patiently pending during human NLA/VNC/SSH authentication. Distinguish no-human-response from genuinely failed/dead/cancelled/ambiguous windows. Bounded *machine* operations still fail closed. This may require changing current human-facing supervisor deadlines as a correctness fix.
- **Increment 5 and Step 1.5d:** test and close security and integrated behavior on native X11 and Wayland.
- **Phase 2:** consider prompt staging, readable target labels, cascading prompt geometry, queuing and concurrent remote launch only after native latency and usability evidence warrant additional complexity.

Local SDL NLA dialogs, VNC/SSH prompts and remote GDM content have separate identities. In particular, the GDM greeter is content *inside* an already existing RDP viewer; it is not a separate local NLA dialog. Never adopt an authentication dialog as the persistent managed viewer by class, PID or title alone. Never embed or automatically supply credentials, disable certificate/SSH trust checks, or invent server-idle guarantees.

## Consequence for task dispatch

The superseded `DRAFT_Codex-Next-Operator-Controlled-RDP-Placement.md` is **not** the live instruction. The bounded [Codex Increment 3 assignment](Codex-Increment3-RDP-Placement.md) and [active HANDOFF](HANDOFF.md) represent the now-settled scope. No concurrent launch scheduler or prompt staging is a prerequisite to Increment 3. This record does not independently authorize code edits or native testing.
