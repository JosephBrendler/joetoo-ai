# joetoo-kwin — architecture and version 1 requirements

This is the project-specific design record for the authorized collaboration project
`joetoo-ai/workspace/projects/joetoo-kwin/`. It distinguishes **accepted requirements**, **proposed design contracts**,
and **open questions**. A proposed interface is not evidence that it has been
implemented or tested; development status and native results belong in the
[project README](README.md).

The governing collaboration instructions are in the repository's root
`AGENTS.md`, `workspace/AGENTS.md`, and `workspace/README.md`. Official sources and
packaging belong respectively to `joetoo-upstream` and `joetoo`, which remain
**read-only to AI agents** under their current policies. This document does not
supersede those policies or authoritative architecture after human integration.

## 1. Purpose and release boundary

Replace the legacy X11 `xdotool_open_windows`, `xdotool_close_windows`, and
`xdotool_sizemove_this_window` workflows with `joetoo-kwin`, operating under
KDE Plasma/KWin on **X11 and Wayland**. Support the maintainer's normal
interactive shell workflow, a declarative multi-desktop session layout,
independently manageable SSH and graphical windows, and conservative window
closure.

Version 1 requires an OpenRC-supervised `joetoo-kwind` management daemon and
reliable initialization/reconnection of resident KWin JavaScript. Intermediate
0.x prototypes are permitted; neither requirement is deferred past version 1.

## 2. Supported development environment

Development and validation must address both KWin/X11 and KWin/Wayland under
Gentoo Linux, KDE Plasma, and an OpenRC user session. The specific host
platforms and observed test outcomes are recorded in the
[project README](README.md), not maintained as architectural requirements.

## 3. Components and ownership

| Component | Intended name | Owns | Must not do |
| --- | --- | --- | --- |
| Public Bash CLI | `joetoo-kwin` | Options, profile selection, planning, application launch orchestration, user messages | Guess ownership from window class alone; kill unrelated processes |
| Broker daemon | `joetoo-kwind` | Session D-Bus API, transactions, managed-window registry, status, live checkpoint, reconciliation | Become process supervisor/parent of SSH/Konsole sessions; guess window geometry |
| OpenRC user service | `joetoo-kwind` | Supervise broker process; expose service lifecycle and optional diagnostic delegation | Reinterpret the registry file; terminate managed applications on service stop |
| KWin resident JavaScript | `joetoo-kwin-resident.js` | Observe KWin windows, UUIDs, geometry/desktops, KWin move/close actions, window removal | Own the durable launch configuration; infer SSH connectivity from a window's existence |
| Configuration/profile | `/etc/joetoo-kwin/joetoo-kwin.conf` | Selected *desired* layout (symlink to profile under `configs/`) | Store ephemeral PIDs or KWin UUIDs |

**D-Bus compatibility:** The established service name `org.joetoo.KWinBridge`,
object path `/org/joetoo/KWinBridge`, and existing method signatures are
compatibility contracts. Renaming executables must not silently change them.

**Service lifecycle contract:** stop/restart of `joetoo-kwind` must leave all
managed Konsole, SSH, and graphical client processes running. Restart
reinitializes management and attempts bounded reconciliation; it does **not**
close and reopen windows. No DDNS-style `trap 'kill 0' EXIT` in the broker.
The `joetoo-kwin` CLI must not run as root or initiate root-level SSH.

**Synchronization of current window inventory:** When the broker starts or reconnects to an already-running KWin resident, it must automatically request a complete current-window inventory. This synchronization must be idempotent, tolerate concurrent window events, and must not confer managed ownership on observed windows. The existing manual joetoo_bridge_observe shortcut remains available for diagnostics. Managed-window checkpoint recovery is a separate responsibility addressed in Step 1.7.

## 4. Identity, ownership; launch configuration and transactions

**Runtime identities:** joetoo-assigned logical identifiers and
externally assigned identities have distinct purposes.

| Identifier | Assigned by | Meaning | Lifetime |
| --- | --- | --- | --- |
| `run_id` | joetoo | Groups coordinated operations when needed | Execution/reporting |
| `request_id` | joetoo | Identifies one requested operation or transaction | Operation and bounded result history |
| `managed_id` | joetoo | Human-readable alias for one registered window (e.g. `win-004`) | Registered instance |
| `window_uuid` | KWin | Identifies the actual KWin window | Compositor/window lifetime |

Each active managed-window record has exactly one `managed_id`
and one `window_uuid`, with a unique bidirectional association
within the broker's active registry.

A `managed_id` is an alias, not proof of ownership or authorization
for destructive operations. Linux PIDs and KWin observation-source
identifiers are separate runtime metadata.

Runs need not be retained beyond completion, and not every CLI
invocation requires a broker-visible `run_id`.

**Saved configuration:** (Runtime launches each configured entry)
`desktop`, `slot`, `program`, `mode`, and `target` describe a **logical launch
recipe**; they are not sufficient to uniquely identify a runtime window.
A readable window title/label such as **`joetoo_konsole_3.1`** means intended
desktop 3, slot 1. Use this naming shape where it can be set and observed
reliably. It is **not a globally unique key**: repeated runs can create
`joetoo_konsole_3.1` again, and titles can change. Preserve `request_id`,
`managed_id`, and matched UUID independently of visible caption.
| Field | Type | Meaning |
| --- | --- | --- |
| desktop | integer | KDE/Plasma virtual desktop number |
| slot | integer | Layout position within/on virtual desktop |
| program | string | basename of executable program |
| mode | string | one-word descrption of role of program |
| target | string | hostname of remote target |

`joetoo-kwin -m ...` on an arbitrary preexisting window changes its geometry; it does **not**
automatically enroll that window for subsequent `-x` closure. Only a window
created by an authorized joetoo launch and **positively correlated** with that
launch becomes managed. Uncertain matches must not become close targets.

### Launch-and-correlate contract

1. Validate the requested layout/launch, allocate a request_id and, when coordinated operations require one, a run_id
2. Capture existing KWin window identities, arm a specific pending request in the broker, and launch one application instance independently of the daemon's process group.
3. Observe `windowAdded` and subsequent changes if needed. Poll/await a **bounded** period for a *unique* match using available evidence: new UUID, application class/desktop file, launch PID when trustworthy, and optionally an explicit title token such as `joetoo_konsole_3.1`.
4. Record matched `window_uuid` and current metadata, request KWin placement, verify readback when settled, and complete the transaction with a structured result. Keep launch and placement outcomes distinct.
5. On timeout or ambiguous matches, report **unmatched/ambiguous** and never take ownership of an arbitrary class-matching window.


## 5. Working registry and operation outcomes

The broker maintains distinct kinds of runtime information:

- `observed_windows`: KWin-reported windows, regardless of whether
  joetoo manages them.
- `managed_windows`: positively correlated and registered window
  instances, indexed by KWin UUID with a unique secondary lookup
  by `managed_id`.
- `requests`: pending operations and bounded completed results.
- `runs`: transient contexts for coordinated operations, retained
  only as necessary for execution and reporting.
- `application_sessions`: activities established within windows,
  where application-specific reporting supports them.
- `graphical_context`: broker/KWin observation-source and
  graphical-environment metadata, distinct from application sessions.

These are logical responsibilities; exact Python structures remain
implementation details. The broker validates observations,
correlates launches, maintains the records, and reports outcomes.
KWin is authoritative for actual window existence and geometry.

### registry contract (Implementation Step 1.4a)

1. A window becomes managed only after a broker-associated launch
   is positively correlated with a newly observed KWin UUID.
2. Registration requires a synchronized prelaunch inventory,
   unique qualifying correlation, no relevant observation-history
   gap, and confirmation that the UUID remains present.
3. Unresolved or ambiguous requests do not create managed-window
   registrations. Observation, inspection, or movement of an
   existing window does not confer managed ownership.
4. Each active registration has a unique, one-to-one association
   between `managed_id` and `window_uuid`. Duplicate or conflicting
   registrations must be rejected without altering existing records.
5. Window existence, placement, operation outcome, and application
   session state are independent. Successful window registration
   does not imply successful placement or connection.
6. A failed SSH/VNC connection does not invalidate an otherwise
   successfully registered window. An unsuccessful connection
   attempt does not create an established application session.
7. The broker updates registered windows using exact UUID-based
   observations. Missing or uncertain windows must not be silently
   re-adopted through class, title, desktop, or slot matching.
8. Registration does not itself authorize destructive operations.
   Stronger validation is required before managed close operations
   are introduced.
9. Multiple managed windows and completed requests must coexist.
   Correlation and registration operations may initially be
   serialized; no arbitrary fixed window-count requirement applies.
10. Read-only managed-window list, detail, and status semantics
    are defined during Step 1.4a and exposed in Step 1.4c.

### Independent state dimensions

| Dimension | Candidate states |
| --- | --- |
| Request | `pending`, `running`, `succeeded`, `failed`, `timeout`, `ambiguous` |
| Window observation | `present`, `missing`, `uncertain` |
| Placement | `not_requested`, `pending`, `succeeded`, `failed` |
| Application connection | `not_attempted`, `connecting`, `connected`, `unavailable`, `exited`, `unknown` |

Exact state representations and permitted transitions are to be
finalized and tested during Step 1.4a. Avoid redundant flags or
a generalized state-machine framework without demonstrated need.

An application window may be associated with zero or more
application sessions over its lifetime. General session tracking
is not required for Step 1.4.

Managed IDs are broker-lifetime identifiers initially; safe
same-session recovery and stale-ID protection are addressed
before destructive operations are enabled.


## 6. Geometry and visibility

`-c`, `-o`, and interactive `-m l|r` must use **one shared geometry policy**.
Do not duplicate calculations inside aliases, the broker, and the planner.

- Allocate **87% of usable screen width by default** to the total terminal
  region for 1–3 terminals, with configurable width percentage and inter-window
  gutters. Leave clickable space **between** terminals and **to the right** so
  desktop widgets (clocks, CPU/network monitors, etc.) remain visible and
  underlying windows remain selectable. This is deliberate usable space, not
  wasted pixels.
- Four terminals use two-by-two quadrants; more than four terminals on one
  desktop is initially rejected. Count intended terminal windows, **not**
  reachable SSH connections. Graphical apps do not consume terminal slots.
- Permit graphical windows such as VNC beneath terminals but **protruding**
  enough for independent mouse selection; actual stacking and focus policy
  require native tests, not merely proposed geometry.
- `joetoo-kwin -m l` and `-m r` move/resize the **active** window to the
  corresponding two-terminal left/right slot **on its current desktop**, using
  this shared policy; expose `mw` as `alias mw='joetoo-kwin -m'` or an equivalent
  shell function, not as a separate geometry implementation.
- `-m DESKTOP X Y` preserves current window **width and height**;
  `-m DESKTOP X Y WIDTH HEIGHT` explicitly resizes. The `-m` parser must
  accept precisely 1 (`l|r`), 3, or 5 operands. No guessed pixel dimensions
  from `termwidth()`/`termheight()`; resident KWin reads actual
  `frameGeometry` for the preserve-size case.
- Screen selection and work-area/panel deductions (especially multiple
  monitors) are not yet established; the current candidate uses explicit
  `screen_width`/`screen_height` from configuration. Do not present them as
  autodetected.

## 7. Unavailable SSH is a valid placeholder

For a configured SSH target that cannot be reached, keep the correctly placed
Konsole window, identifying **which connection was attempted and why** (its
"what-for" function). Retain the *original* local Bash and permit manual retry,
as validated in the POC. No `tmux`, no extra Bash replacement, no always-enabled
Konsole security-sensitive D-Bus API. Continue using the established
`ssh_wrapper` and `bash --rcfile` pattern.

A layout is **complete** when each intended window was positively identified
and placed, **even if some SSH connections are unavailable or have exited**.
An absent, unmatched, ambiguously identified, or unplaced required window
makes the launch incomplete. Persist the intent for placeholders, so a later
`-r` makes a **new connection attempt** rather than trying to revive old SSH
processes. Do not mistake network health for window-management success.

## 8. Runtime checkpoint versus restorable layout

### 8.1 Working state and private runtime JSON (accepted direction)

- Broker's Python memory is the active authority for managed ownership and
  operation records. Serialize a private checkpoint atomically to
  `$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json`.
- Checkpoint is a **copy of live registry state**, including UUIDs, PIDs,
  requests/results and current-session identifiers, not the template for a
  clean reboot. File mode/directory permissions must restrict other users;
  do not persist SSH secrets or environment dumps.
- On same-session broker restart, load and validate checkpoint, verify active
  KWin session and live UUIDs, and mark missing/ambiguous entries uncertain.
  An uncertain record is **not** eligible for automatic destructive operations.
- Broker or OpenRC stop/restart **must not close** managed windows. Treat
  compositor corruption/session replacement as outside the bounded recovery
  guarantee; no broad class-based recreation or forced adoption.

### 8.2 Durable last-known-good `.conf` (accepted direction)

- A separate, reusable Bash-layout snapshot is stored in a user-writable
  persistent state area, proposed path
  `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf`.
  It contains launch recipes and layout policy, **not prior UUIDs or PIDs**.
- Generate the snapshot from a **complete and validated intended layout**;
  unreachable SSH targets whose Konsole placeholders are created and placed
  **count as valid**. Do not overwrite the previous good snapshot with a
  partial launch or an empty shutdown inventory. Write updates atomically.
- `-r` restores that last good **set of windows**, through the same internal
  plan/launch implementation as `-f FILE -o`, yielding new PIDs, KWin UUIDs,
  request IDs and run ID. It does not resume an old SSH transport, shell
  process, or remote login state.
- `-S` explicitly exports a chosen current arrangement to reusable config,
  including verified current geometry as supported by the future config
  schema; handle trusted Bash sourcing and user-writable storage safely.
- `-x` closes managed windows but **does not delete** the restorable snapshot.
  `-d` changes live state, without implicitly rewriting the saved layout.

The **exact trigger** for automatically advancing `last-session.conf` and the
representation of manually adjusted per-window geometry remain to be
specified in milestone 1.8. Do not conflate user-issued `-S` with every registry
write. The exported file is a *trusted* Bash configuration and should not
silently be writable by unrelated processes.

## 9. CLI contract (target; not all flags implemented)

| Invocation | Intended action |
| --- | --- |
| `-c [-f CONFIG]` | Validate config and display a colorized **dry run** (no programs launched) |
| `-o [-f CONFIG]` | Open/record a managed layout, each window positively matched |
| `-x` | Gracefully close **all managed** windows; never unrelated windows |
| `-m l|r` | Two-terminal left/right placement on current virtual desktop |
| `-m DESKTOP X Y [WIDTH HEIGHT]` | Move active window; optional size preservation |
| `-a` | Add one newly launched managed window; exact operands TBD |
| `-d MANAGED_ID` | Gracefully close one managed window |
| `-l` | List managed windows with readable IDs and states |
| `-i MANAGED_ID` | Show info for one managed window |
| `-s` | Broker/application status (not OpenRC process status) |
| `-S` | Save reusable current layout; selection/path options TBD |
| `-r` | Recreate last-known-good layout with new window/process IDs |
| `-f FILE` | Select configuration path without modifying default `eselect` symlink |
| `-v`, `-q` | Adjust verbosity using existing `script_header_joetoo` `_pc_action_verbosity()` |

Preserve established `j_msg`, `separator`, status-color styling and the
application-specific `getopts` pattern, referencing the
`script_header_joetoo-CLI` skill. This table is a **target**, not a description of currently implemented CLI
capabilities. Retire the POC `move` subcommand when `-m` coverage is
validated; use `mw` as an alias/function and preserve `ow`/`cw` shorthands.
See the [project README](README.md) for the current implementation status.

## 10. Supervision, safety and identity invariants

1. A managed UUID must be matched to a *specific* launch transaction before
   that UUID is eligible for `-d` or `-x`.
2. A KWin UUID is a runtime identity, not a stand-alone ownership token.
   Registration, compositor epoch and positive observation establish scope.
3. A broker restart does not imply relaunch, and application close does not
   imply daemon shutdown.
4. A user-requested close is graceful first, with removal confirmation.
   Do not translate uncertainty into indiscriminate class matching or
   force-killing process groups.
5. `joetoo-kwind` runs with ordinary graphical-user privileges and uses the
   correct user session bus. Do not use root SSH or system-wide OpenRC merely
   to simplify implementation.
6. Keep window state, SSH transport state and launch transaction state
   independent; each can succeed or fail separately.
7. Do not expose private host secrets or credentials in the public `joetoo-ai`
   review repository or debug dumps. Status/dumps must filter sensitive data.
8. Preserve verified POCs unchanged as regression references unless their
   modification is explicitly in scope and documented.

## 11. Numbered implementation and review gates

These gates describe intended deliverables and acceptance criteria.
Current completion status and supporting evidence are recorded in the
[project README](README.md); collaboration procedures are governed by
`AGENTS.md` and the parent workspace instructions.

| Gate | Deliverable | Native/validation gate |
| --- | --- | --- |
| **1.1** | This architecture/registry/CLI contract and project `AGENTS.md` | Source-referenced review; accepted decisions distinguished from proposals |
| **1.2a** | Early OpenRC **user** service `joetoo-kwind` prototype | Safe start/stop/restart, supervised restart, no Konsole/SSH loss |
| **1.2b** | Session-bus and resident JS activation/reconnection | Correct KWin session, no double registration, idempotence across restart |
| **1.3a** | KWin UUID, geometry and `windowRemoved` observation | gmki91 X11 and q552u01 Wayland identity tests |
| **1.3a.1** | Separate lifecycle history and coalesce window changes by UUID | Bounded history unaffected by dragging; X11 and Wayland regression tests |
| **1.3a.2** | Automatic broker-start/reconnect synchronization of current KWin window inventory | Full inventory restored without manual refresh; no duplicate subscriptions or implicit ownership |
| **1.3b** | Launch-and-poll unique correlation; title-token feasibility | Same-class Konsole stress/ambiguity tests; no false adoption |
| **1.4a** | In-memory registry data model, identity rules, state transitions, and headless contract tests | Unique UUID/managed-ID association; lifecycle and registration safety tests |
| **1.4b** | Multiwindow registration and UUID-based observation reconciliation | Multiple independent registrations; duplicate rejection; conservative missing/uncertain handling |
| **1.4c** | Read-only managed-window list, detail, and status interfaces | Structured broker queries; existing D-Bus compatibility preserved |
| **1.4d** | Multiwindow integration and native validation | Representative mock scenarios, then X11 and Wayland tests; no fixed capacity requirement |
| **1.5** | Shared geometry + `mw l/r`; colorized `-c`; `-o` with tested SSH placeholders | Native layout/SSH/underlay tests; `-v/-q` |
| **1.6** | Managed `-a`, `-d`, `-x` | Close one/all managed, leave unrelated Konsole untouched |
| **1.7** | Private atomic JSON checkpoint and same-session reconciliation | Daemon restart preserves all running windows; registry revalidated |
| **1.8** | Durable `.conf` snapshot, `-S` and `-r` | Clean-reboot launch with new UUID/PIDs, including SSH placeholders |
| **1.9** | `eselect`, packaging and full regression | Maintainer-driven joetoo/joetoo-upstream integration; version 1 lifecycle gate |

## 12. Open questions and explicit verification tasks

- Can a per-launch Konsole title token such as `joetoo_konsole_3.1` be
  made KWin-visible in time for correlation? A title alone is only a hint;
  direct-PID Konsole correspondence has been tested on both backends.
- What additional Plasma-readiness guarantees are needed at OpenRC
  user-session startup? Broker stop/restart and client-process survival have
  been validated in the POC scenarios.
- What compositor/session identity sufficiently bounds checkpoint
  reconciliation? What can be recovered after an intermediate KWin restart?
- Which layout work area and screen should drive shared geometry on multi-
  monitor setups? How should panel reserved areas and scaling be considered?
- What is the validated, non-ambiguous way to request **preserve size** from
  the existing five-integer broker protocol while retaining compatibility?
- When should automatic last-good snapshots advance, and how is manual
  rearrangement encoded in a reusable `.conf`?
- What are the exact `-a` and `-S` operands and safe selection behavior?
