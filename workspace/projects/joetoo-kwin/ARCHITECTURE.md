# joetoo-kwin — architecture and version 1 development contract

This is the project-specific design record for the authorized collaboration project
`joetoo-ai/workspace/projects/joetoo-kwin/`. It distinguishes **accepted
requirements**, **implemented POC evidence**, **proposed contracts requiring
validation**, and **open decisions**. Acceptance of this document does not establish
that a proposed interface or behavior works on Gentoo.

The governing collaboration instructions are in the repository's root
`AGENTS.md`, `workspace/AGENTS.md`, and `workspace/README.md`. Official sources and
packaging belong respectively to `joetoo-upstream` and `joetoo`, which remain
**read-only to AI agents** under their current policies. This document does not
supersede those policies or authoritative architecture after human integration.

## 1. Purpose and release boundary

Replace the legacy X11 `xdotool_open_windows`, `xdotool_close_windows`, and
`xdotool_sizemove_this_window` workflows with `joetoo-kwin`, operating under
KDE Plasma/KWin on **X11 and Wayland**. Support the maintainer's normal interactive
shell workflow, a declarative multi-desktop session layout, independently
manageable SSH and graphical windows, and conservative window closure.

Version 1 **requirements:**
- an OpenRC-supervised management daemon (joetoo-kwind)
- reliable initialization/reconnection of resident KWin JavaScript
- Development may have 0.x prototypes, but neither lifecycle requirement is deferred past version 1.

# to do - move this to project README.md with POC/DT results
- active-window placement, new Konsole placement, interactive
`bash --rcfile` SSH session, an unavailable-target placeholder, return to the
*original* Bash after logout, and termination of recorded SSH/Bash PIDs on
closing the Konsole window were all demonstrated in version 0 proofs of concept (POC). These are maintainer-reported tests of the POCs,**not** proof of the proposed registry, durable recovery, or managed-window behavior.
- OpenRC user-service POC has been validated on gmki91 (KWin/X11) and q552u01 (KWin/Wayland). Native testing established user-service start/stop/restart, broker-only crash recovery, session D-Bus communication, the effective user-owned POC installation paths, and preservation of independent Konsole/SSH processes across broker restarts. Process and cgroup continuity were also verified in the tested scenarios. Step 1.2b subsequently established KWin resident-script initialization and reuse across broker restarts.
- The eventual system-package installation paths, complete dependency and configuration integration, explicit Plasma-readiness guarantees, and automatic recovery of managed-window state remain subject to later validation. The established D-Bus service name `org.joetoo.KWinBridge`, object path `/org/joetoo/KWinBridge`, and existing method interfaces are compatibility contracts; renaming the executable must not silently change them.
- Launch-and-correlate status: the step 1.3 POC matches mainly on class and allows only one outstanding request.
It must be extended before claiming robust same-class multiwindow ownership.
Whether Konsole propagates a deliberately assigned title to the KWin caption
soon enough for correlation, and whether PID correspondence is dependable on
both backends, require native verification. The label is a **hint**, not proof.

## 2. Development platforms
Successful Step 0 native POC tests have been conducted on two joetoo/gentoo Linux machines running KDE/Plasma version 6.7 --
| hostname | system specs |
| --- | --- | 
| gmki91 desktop | OS: Gentoo Linux x86_64<br>Host: NucBox M3 PLUS<br>Kernel: Linux 6.18.57-gentoo-dist-hardened-joetoo<br>Shell: bash 5.3.20<br>Display (SMB2330H): 1920x1080 in 7", 60 Hz [External]<br>**DE: KDE Plasma 6.7.5**<br>WM: KWin (X11)<br>WM Theme: Breeze<br>Theme: oxygen (Oxygen) [Qt], Breeze [GTK2/3]<br>Icons: oxygen [Qt], oxygen [GTK2/3/4]<br>Font: Noto Sans (11pt) [Qt], Noto Sans (11pt) [GTK2/3/4]<br>Cursor: Oxygen_Yellow (24px)<br>Terminal: konsole 26.4.3<br>Terminal Font: Hack (8pt)<br>CPU: 12th Gen Intel(R) Core(TM) i9-12900HK (12+8) @ 5.00 GHz<br>GPU: Intel Iris Xe Graphics @ 1.45 GHz [Integrated]<br>Memory: 5.68 GiB / 31.09 GiB (18%)<br>Locale: en_US.UTF-8 |
| q552u01 laptop | OS: Gentoo Linux x86_64<br>Host: Q552UB (1.0)<br>Kernel: Linux 6.18.57-gentoo-dist-hardened-joetoo<br>Shell: bash 5.3.20<br>Display (LGD046F): 1920x1080 in 16", 60 Hz [Built-in]<br>**DE: KDE Plasma 6.7.5**<br>WM: KWin (Wayland)<br>WM Theme: Breeze<br>Theme: Breeze (Light) [Qt], Breeze [GTK2/3]<br>Icons: Breeze [Qt], breeze [GTK2/3/4]<br>Font: Noto Sans (10pt) [Qt], Noto Sans (10pt) [GTK2/3/4]<br>Cursor: Breeze (24px)<br>Terminal: sshd<br>CPU: Intel(R) Core(TM) i7-6500U (4) @ 3.10 GHz<br>GPU 1: NVIDIA GeForce 940M [Discrete]<br>GPU 2: Intel HD Graphics 520 @ 1.05 GHz [Integrated]<br>Memory: 3.16 GiB / 11.57 GiB (27%)<br>>Battery (ASUS Battery): 102% [AC Connected]<br>Locale: en_US.UTF-8 |

Design proofs of concept (POC) and developmental test (DT) results are documented in the project [README.md](./README.md)

## 3. Components and ownership

| Component | Intended name | Owns | Must not do |
| --- | --- | --- | --- |
| Public Bash CLI | `joetoo-kwin` | Options, profile selection, planning, application launch orchestration, user messages | Guess ownership from window class alone; kill unrelated processes |
| Broker daemon | `joetoo-kwind` | Session D-Bus API, transactions, managed-window registry, status, live checkpoint, reconciliation | Become process supervisor/parent of SSH/Konsole sessions; guess window geometry |
| OpenRC user service | `joetoo-kwind` | Supervise broker process; expose service lifecycle and optional diagnostic delegation | Reinterpret the registry file; terminate managed applications on service stop |
| KWin resident JavaScript | `joetoo-kwin-resident.js` | Observe KWin windows, UUIDs, geometry/desktops, KWin move/close actions, window removal | Own the durable launch configuration; infer SSH connectivity from a window's existence |
| Configuration/profile | `/etc/joetoo-kwin/joetoo-kwin.conf` | Selected *desired* layout (symlink to profile under `configs/`) | Store ephemeral PIDs or KWin UUIDs |

**Service lifecycle contract:** stop/restart of `joetoo-kwind` must leave all
managed Konsole, SSH, and graphical client processes running. Restart
reinitializes management and attempts bounded reconciliation; it does **not**
close and reopen windows. No DDNS-style `trap 'kill 0' EXIT` in the broker.
The `joetoo-kwin` CLI must not run as root or initiate root-level SSH.

**Synchrnization of current window inventory:** When the broker starts or reconnects to an already-running KWin resident, it must automatically request a complete current-window inventory. This synchronization must be idempotent, tolerate concurrent window events, and must not confer managed ownership on observed windows. The existing manual joetoo_bridge_observe shortcut remains available for diagnostics. Managed-window checkpoint recovery is a separate responsibility addressed in Step 1.7.

## 4. Identity, ownership; launch configuration and transactions

**Runtime window management schema:** Four separate concepts must be preserved:

| Field | Meaning | Lifetime |
| --- | --- | --- |
| `run_id` | One invocation of `-o` or `-r`; groups intended launches | Registry/history |
| `request_id` | A single asynchronous launch, move, or close transaction | Transaction/history |
| `managed_id` | Human-usable identifier for *one registered window instance* (e.g., `w017`) | Registered instance |
| `window_uuid` | Actual KWin `internalId` of a matched, existing window | KWin compositor/window lifetime |

**Saved configuration:** (Runtime launches each configured entry)
`desktop`, `slot`, `program`, `mode`, and `target` describe a **logical launch
recipe**; they are not sufficient to uniquely identify a runtime window.
A readable window title/label such as **`joetoo_konsole_3.1`** means intended
desktop 3, slot 1. Use this naming shape where it can be set and observed
reliably. It is **not a globally unique key**: repeated runs can create
`joetoo_konsole_3.1` again, and titles can change. Preserve `request_id`,
`managed_id`, and matched UUID independently of visible caption.
| Field | Type | Meaning |
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

1. Validate the requested layout/launch and allocate a `run_id` and
   `request_id`; record the expected program, desktop/slot, and optional
   application-specific correlation signature.
2. Capture existing KWin window identities, arm a specific pending request in
   the broker, and launch one application instance independently of the daemon's
   process group.
3. Observe `windowAdded` and subsequent changes if needed. Poll/await a **bounded**
   period for a *unique* match using available evidence: new UUID, application
   class/desktop file, launch PID when trustworthy, and optionally an explicit
   title token such as `joetoo_konsole_3.1`.
4. Record matched `window_uuid` and current metadata, request KWin placement,
   verify readback when settled, and complete the transaction with a structured
   result. Keep launch and placement outcomes distinct.
5. On timeout or ambiguous matches, report **unmatched/ambiguous** and never
   take ownership of an arbitrary class-matching window.

## 5. Working registry and operation outcomes (proposed schema)

Maintainer note: project data structures and schema are "under development" and expected to evolve as development and DT experience dictate.  Any changes must be approved by maintainer, and the change decision is to be documented in the project README.md"

The authoritative **joetoo ownership registry** lives in broker memory,
conceptually as Python mappings such as `runs`, `windows`, `requests`, and
`session`, with `windows` indexed by KWin UUID (and a secondary lookup by
`managed_id`). These are *proposed logical structures*, not current variables
in the implementation or a POC. KWin remains authoritative for **actual window existence and
current geometry**. The broker reconciles its claims against KWin observations.

A managed entry is expected to carry:

- Identity: `run_id`, `request_id`, `managed_id`, `window_uuid` and a compositor/
  graphical-session epoch for safe reconciliation.
- Recipe: `desktop`, `slot`, `program`, `mode`, `target` and validated
  launch/geometry policy; readable window label if supported.
- Observation: KWin PID when available; optionally shell/SSH PIDs from the
  tested Bash launcher; last observed desktop, geometry, and window presence.
- Operation records: requested action, timestamp, outcome, diagnostic; keep
  actual launch/placement status distinct from connection status.

Suggested independent state dimensions (exact enums remain design candidates):

| Dimension | Candidate values | Interpretation |
| --- | --- | --- |
| Window | `planned`, `launching`, `matched`, `placed`, `closing`, `closed`, `missing`, `uncertain` | Existence, correlation and KWin placement |
| Launch transaction | `pending`, `running`, `OK`, `ERROR`, `timeout`, `ambiguous` | One operation's outcome |
| SSH transport | `not_attempted`, `connecting`, `connected`, `unavailable`, `exited`, `unknown` | Never inferred solely from a Konsole window or TCP probe |

The registry records **reported, observed facts**; avoid claiming a connected
SSH transport solely because a PID or open TCP port was observed. Individual
SSH session events may be reported from the interactive `--rcfile` launcher,
with exact semantics verified during implementation.

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

### 7.1 Working state and private runtime JSON (accepted direction)

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

### 7.2 Durable last-known-good `.conf` (accepted direction)

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
`script_header_joetoo-CLI` skill. The current merged Step 1 candidate
implements only `-c`, `-f`, `-m` with **five** operands, and a deliberately
unimplemented `-o`; the table above is a **target**, not a description of
current capabilities. Retire the POC `move` subcommand when `-m` coverage is
validated; use `mw` as an alias/function and preserve `ow`/`cw` shorthands.

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

New candidate work is under `workspace/projects/joetoo-kwin/`; each substep
uses the accepted baseline and the **branch-and-review** workflow described in
`workspace/AGENTS.md`. Suggested names: `task/joetoo-kwin-step1.1-architecture`,
`task/joetoo-kwin-step1.2a-openrc`, etc. Prepare a full diff and validation
report; seek explicit approval **before** commit, push and draft PR. Human
maintainer alone merges and integrates protected repositories.

| Gate | Deliverable | Native/validation gate |
| --- | --- | --- |
| **1.1** | This architecture/registry/CLI contract and project `AGENTS.md` | Source-referenced review; accepted decisions distinguished from proposals |
| **1.2a** | Early OpenRC **user** service `joetoo-kwind` prototype | Safe start/stop/restart, supervised restart, no Konsole/SSH loss |
| **1.2b** | Session-bus and resident JS activation/reconnection | Correct KWin session, no double registration, idempotence across restart |
| **1.3a** | KWin UUID, geometry and `windowRemoved` observation | gmki91 X11 and q552u01 Wayland identity tests |
| **1.3a.1** | Separate lifecycle history and coalesce window changes by UUID | Bounded history unaffected by dragging; X11 and Wayland regression tests |
| **1.3a.2** | Automatic broker-start/reconnect synchronization of current KWin window inventory | Full inventory restored without manual refresh; no duplicate subscriptions or implicit ownership |
| **1.3b** | Launch-and-poll unique correlation; title-token feasibility | Same-class Konsole stress/ambiguity tests; no false adoption |
| **1.4** | `joetoo-kwind` multiwindow in-memory registry and status/list/dump | Accurate 37-window mock; correct transaction/SSH separation |
| **1.5** | Shared geometry + `mw l/r`; colorized `-c`; `-o` with tested SSH placeholders | Native layout/SSH/underlay tests; `-v/-q` |
| **1.6** | Managed `-a`, `-d`, `-x` | Close one/all managed, leave unrelated Konsole untouched |
| **1.7** | Private atomic JSON checkpoint and same-session reconciliation | Daemon restart preserves all running windows; registry revalidated |
| **1.8** | Durable `.conf` snapshot, `-S` and `-r` | Clean-reboot launch with new UUID/PIDs, including SSH placeholders |
| **1.9** | `eselect`, packaging and full regression | Maintainer-driven joetoo/joetoo-upstream integration; version 1 lifecycle gate |

The outputs of Step 1.2a broker/OpenRC implementation and tests now reside in the project root. The six historical POCs, along with the complete Step 1 and Step 1.2a candidate snapshots, reside under archive/. The Step 1 CLI and its coupled planner remain archived prototypes pending integration into the launcher.

Intent for archive/ -- retain candidate and POC products with known-good X11/Wayland behavior as available future-capability integration resources or references and regression tests at each
relevant gate. OpenRC and launch-correlation were advanced to early candidate work as critical-path risks, not optional post-release polishing. As of step 1.2a graduation from candidate to implemented status, the OpenRC components are installed at project root, but the demonstrated launch-correlation capability has not yet been so-promoted.

## 12. Open questions and explicit verification tasks

- Can Konsole reliably expose a title like `joetoo_konsole_3.1` as the
  **KWin-visible window caption**, with enough timing/uniqueness to aid
  launch correlation? Which PID belongs to a Konsole window on each backend?
- What is the precise user-service OpenRC installation/session-startup
  mechanism on the target Gentoo/OpenRC/elogind environment? What happens to
  descendant/application process groups on service stop and restart?
- What compositor/session identity sufficiently bounds checkpoint
  reconciliation? What can be recovered after an intermediate KWin restart?
- Which layout work area and screen should drive shared geometry on multi-
  monitor setups? How should panel reserved areas and scaling be considered?
- What is the validated, non-ambiguous way to request **preserve size** from
  the existing five-integer broker protocol while retaining compatibility?
- When should automatic last-good snapshots advance, and how is manual
  rearrangement encoded in a reusable `.conf`?
- What are the exact `-a` and `-S` operands and safe selection behavior?

Resolve each experimentally and record **actual** tests/decisions in this
file or a linked, reviewed project record before promoting a proposal to an
accepted design invariant.

## 13. Inspected baseline and evidence

At drafting time, the accessible `joetoo-ai/main` baseline was
`252a1569a3c3007212c1dd2ba2c3ef07f35d017b` (2026-10-24). Sources read:

- `workspace/projects/joetoo-kwin/step1-candidate/joetoo-kwin`,
  `joetoo-kwin-plan-functions`, `desktop_sessions.conf`, and `README.md`;
- `workspace/projects/joetoo-kwin/archive/joetoo-kwin-launch-poc/joetoo-kwin-broker.py`,
  `joetoo-kwin-resident.js`, and `README.md`;
- `workspace/projects/joetoo-kwin/archive/joetoo-kwin-ssh-rcfile-poc/README.md`;
- `workspace/projects/joetoo-kwin/archive/joetoo-kwin-plan-poc/README.md`;
- root `AGENTS.md`, `workspace/AGENTS.md`, `workspace/README.md`, and the
  relevant `script_header_joetoo`/CLI/SSH/pseudo-boolean collaboration skills.

No assertions here about a feature being *implemented* rely solely on this
conversation's design discussion. The accepted requirements above include
maintainer-specified decisions that are intentionally ahead of the available
POC code. Reinspect current sources and native test evidence at each gate.
