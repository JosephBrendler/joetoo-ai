# Step 1.8 (new) — Complete the Version 1 CLI contract

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-21): SCOPE IDENTIFIED; NOT YET IMPLEMENTED OR ACCEPTED.**
The maintainer created `task/joetoo-kwin-step1.8-cli-completion` after
publishing the revised architecture and Step 1.9 scope on `main` at
**`7fdd2cf`**. The earlier Step 1.8 was folded into Step 1.7; this is a
**new, distinct Step 1.8** to finish three remaining Version 1 CLI behaviors.

**Accepted foundation:** All Steps **1.1–1.7 are accepted and closed**.
Step 1.5d's `-L over`/`-l` behavior is accepted
([PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30));
Step 1.6 managed `-d`/`-x` close is accepted
([PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)); and
Step 1.7 checkpoint/recovery and `-S`/`-r` is accepted
([PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33)).
This task must preserve all of those decisions and their evidence.
The [active HANDOFF](HANDOFF.md) owns task dispatch and authorization;
[ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md) owns product requirements.
The [initial planning outline](step18-branch-outline.md)
is supplemental to this task scope.

## Objective and smallest useful change

Deliver these three remaining Version 1 CLI capabilities **without
introducing a new registry, window selector, geometry engine, or general
stacking framework**:

| CLI invocation | Current `7fdd2cf` source | New Step 1.8 result |
| --- | --- | --- |
| `joetoo-kwin -s` | Parsed, then reports not yet integrated | Read-only, validated broker/registry status |
| `joetoo-kwin -i MANAGED_ID` | Parsed, then reports not yet integrated | Read-only detail for exactly one managed record |
| `joetoo-kwin -L DESKTOP PROGRAM MODE TARGET under` | Rejected before launching | Verified one-shot lower of the **newly** registered window |
| `joetoo-kwin -L ... [over]` | **Accepted** default/explicit `over` | Preserve behavior and native regression evidence |
| `joetoo-kwin -L ... panel` | Unsupported | **Remain unsupported; Version 2**, with explicit refusal before side effects |

The user has approved **one-shot `under`** as a narrow revised Version 1
target. This is a deliberate change to Step 1.5d's earlier Version 2
classification of `under`, not proof it is currently implemented. Do not
rewrite the Step 1.5d acceptance record to pretend it already supported it.

## A. `-s` — read-only broker status

Reuse the existing session-bus method
`org.joetoo.KWinBridge.RegistryStatus()` in
[`libexec/joetoo-kwind`](../libexec/joetoo-kwind). That method already
returns in-memory managed counts, observation synchronization, placement
transaction state, recovery, relevant protocol/capability and cleanup fields.
It is a broker snapshot, **not** an independent remote-connection check.

- Preserve existing CLI options and joetoo `j_msg` / announce–act–report
  idioms; no new daemon API is needed for ordinary `-s`.
- Require no operands; never start the broker, load KWin effects or source a
  launch plan merely to display status.
- Parse a complete, allowlisted, bounded response. Distinguish an unavailable
  broker, malformed/inconsistent JSON, and available status. Display Busy or
  uncertain state faithfully rather than reporting unconditional readiness.
- Do not imply working SSH, RDP, VNC authentication or remote application
  health from a managed window's presence or placement.

**Focused acceptance:** valid empty and populated status, Busy/uncertain
state, disconnected broker, missing dependency, malformed/error replies,
extra operands, correct exit status, and no state-changing broker calls.

## B. `-i MANAGED_ID` — read-only managed-window information

Reuse the existing broker `GetManaged(identifier)` method, which returns a
bounded allowlist with `state:FOUND` and a managed record, or
`state:UNKNOWN`. The broker's interface accepts broader identifiers, but
the **public CLI** must accept exactly one canonical `win-NNN`-style
managed ID, not an arbitrary raw KWin UUID, title, class or PID.

- Validate the argument before querying the broker. Reject missing, extra or
  malformed IDs without launching an application or selecting a window.
- Show managed ID, original desktop/slot, presence and placement, and
  available allowlisted identity/observation information without disclosing
  private recipes, credentials or unapproved fields.
- Label recovered/historical observations **last-known** where appropriate;
  `presence:missing` and `presence:uncertain` must not be portrayed as live
  authenticated windows. `UNKNOWN` is distinct from broker unavailability.
- Remain read-only: no focus, movement, adoption, close, launch, slot
  retirement or selector/profile modification.

**Focused acceptance:** found-present, found-missing, found-uncertain,
unknown ID, broker-unavailable, malformed response, invalid identifier,
absence of optional observation keys, safe redaction and nonmutation.

## C. `-L ... under` — new one-window stacking behavior

Extend the **existing** one-recipe launch path and its broker/resident
initial-layout protocol, rather than replacing accepted `-L over` machinery.
The new `under` option is available only for a valid, confirmed single launch
and applies to **the exact original UUID** positively registered by that
launch on the requested desktop.

- Reuse existing recipe/target validation, confirmation, desktop capacity,
  free logical-slot selection (including retained missing reservations),
  application ownership, placement, timeout, cleanup and Busy guards.
- Prove the KWin **6.7.6** native X11 and Wayland APIs support a bounded
  one-shot lower without a permanent `keepBelow` rule or geometry change.
  Check focus/activation interactions: a later activation must not silently
  defeat the requested final stack position and still count as success.
- Verify the final order against the actual compositor's eligible normal
  windows on that desktop, using the existing UUID/source/transaction
  evidence. Do not classify a class/title match or unverified request as a
  successful lower. If safe lowering or readback is unavailable, fail
  explicitly (do not substitute `over`).
- Do **not** move, resize, reallocate, recascade, adopt or deliberately
  restack any pre-existing managed or unmanaged peer; do not create a live
  panel insertion policy, persistent keep-below or new focus machinery.
- Continue supporting omitted LAYER=`over`, explicit `over`, and the
  separate configured `-o` `under/panel/over` layers unchanged. Keep
  `-L panel` a clear pre-launch validation error.

**Native acceptance (maintainer-operated):** on both KWin 6.7.6 Wayland and
native X11 sessions, demonstrate positive new-window UUID correlation,
correct one-shot lower and post-operation readback, existing peers' geometry
unchanged, a retained/missing reservation not reused, ordinary launch
failure/refusal preserving previous state, competing focus/activation handling,
and clear unsupported/timeout/fail-closed results. Test `-L over`, configured
`-o`, `-l`, managed close and Step 1.7 recovery for regressions relevant to
the modified protocol. Avoid a complete repeat of historical RDP/VNC
acceptance tests without a demonstrated need.

## Implementation and validation sequence

1. **Establish exact baseline:** verify branch, HEAD and working tree; read
   `ARCHITECTURE.md`, this task's HANDOFF and the existing CLI/broker/resident
   code. Keep the archived Step 1.5–1.7 acceptance records intact.
2. **Finish the read-only commands:** wire `-s` and `-i` into the existing
   parser and broker methods; add headless tests and update `-h`/user manual.
3. **Implement the bounded `under` extension:** confirm native API
   feasibility, then extend the existing single-launch payload/broker/resident
   path with necessary validation/readback. Do not introduce new selection or
   transport frameworks.
4. **Run focused regressions:** `bash -n`, applicable ShellCheck/Joetoo
   `validate_scripts`, Python tests, JavaScript syntax/tests, D-Bus mock
   checks, and tests of old `over` plus `-o` initial layers.
5. **Obtain native evidence:** maintainer-authorized Wayland and native-X11
   disposable-window checks. Record the actual compositor versions, steps,
   successes, failures, invariants and any accepted limitations.
6. **Review and merge:** present complete diff, test/evidence summary,
   remaining risks and documentation changes; only the maintainer accepts
   Step 1.8 and merges. Then resume Step 1.9 source stabilization.

## Non-goals and stop conditions

No `-L panel`, dynamic panel occupancy/reflow, existing-peer geometry
modification, keep-below policy, general reset-layout command, new RDP/VNC
clients, different window identity authority, Step 1.6 close redesign,
Step 1.7 recovery rewrite, KWin 6.8 migration, `tarup`, Portage ebuild work or
production system integration. Those remain outside this task.

Stop and seek maintainer review if `under` requires anything beyond a
verified one-shot change to the *new* window, changes security assumptions,
or cannot pass the same fail-closed safety boundary on both accepted
compositor backends. A correct explicit unsupported result is preferable
to substituting different behavior and claiming success.

## Completion and transition

Step 1.8 is complete **only** when the maintainer accepts `-s`, `-i`, and
verified `-L under` on both supported KWin 6.7.6 compositor backends,
including focused non-regression evidence. At that point update the task
HANDOFF/README with the actual result, close the task and resume
[Step 1.9](../task_1.9/HANDOFF.md), which retains the human
maintainability-comment/source audit and packaging gates.
