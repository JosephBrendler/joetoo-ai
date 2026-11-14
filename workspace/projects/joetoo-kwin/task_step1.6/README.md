# Step 1.6 — Managed operations

**Status (2026-11-14): preparation; detailed implementation scope awaiting
maintainer approval.** See [HANDOFF.md](HANDOFF.md) for current authority and
[ARCHITECTURE.md](../ARCHITECTURE.md) for accepted product requirements.

## Accepted foundation

Step 1.5 is complete. Step 1.5c.5d merged through PR #29; Step 1.5d merged
through [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30) at
`f72407278fa0a9c923079f3b38ce834440d2fef2`. The reviewed post-merge
baseline is `231e3c3c7e77839ef9220cf1c128f7a1572726d0`.

The baseline includes configured serial launches, positive exact-UUID
registration and placement, original Bash/SSH placeholders, Dolphin local/SFTP,
TigerVNC over owned SSH, SDL RDP strict security defaults, configuration layering,
`-L` over-only one-shot launch/raise and read-only `-l` managed inventory.
See the [complete Step 1.5 archive](../archive/task_step1.5/README.md),
[native Step 1.5d acceptance](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md)
and [final fixture/regression evidence](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md).
Accepted history is not reopened by this task.

## Intended milestone and next engineering activity

The architecture identifies `-a` for adding a managed window,
`-d MANAGED_ID` for selective graceful closure and `-x` for graceful closure
of positively managed windows. These are intended capabilities, not newly
implemented contracts. `-d` and `-x` are currently stubs; `-a` is absent.

The next engineering activity is a **separately authorized read-only
source/contract review**. It should ground a bounded implementation proposal in
the current CLI, broker, registry, resident and application lifecycle contracts.
This README does not authorize that review or implementation.

Decisions requiring maintainer approval include:

- `-a` syntax and its relationship to accepted `-L`.
- Current source, exact UUID, ownership and caller authorization for closure.
- Missing/uncertain records, refusal, timeout and partial-result semantics.
- Application-specific lifecycle consequences without broad process killing.
- The bounded implementation/test envelope and separate native acceptance.

## Preserved requirements and exclusions

Never adopt or close by class/title/PID alone, substitute another UUID, or
affect unrelated windows. A managed ID or read-only inventory result is not a
standalone close capability. Preserve retained reservations, current ownership
validation, graceful confirmed removal, fail-closed uncertainty and independence
of window, placement and remote-session outcomes. Broker service stop/restart
must not terminate managed applications.

Checkpoint/restart reconciliation, durable restore, packaging and concurrent
remote missions remain outside this milestone's initial preparation.

## Development platforms and evidence

`q552u01` is the initial native KDE Wayland development/acceptance host;
`slim2` is designated for subsequent native X11 testing; `gmki91` provides
additional X11 validation. Native execution is not yet authorized.

No Step 1.6 implementation, regression or native acceptance evidence exists
in this initial record. Add actual results only after separately authorized
work produces them. Publication remains maintainer-controlled.
