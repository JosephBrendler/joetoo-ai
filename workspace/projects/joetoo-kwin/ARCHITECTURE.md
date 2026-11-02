# joetoo-kwin — architecture and version 1 requirements

This is the project-specific design record for `joetoo-ai/workspace/projects/joetoo-kwin/`.
It distinguishes accepted requirements, implemented and accepted contracts, proposed
future capabilities, and open design questions. The [project README](README.md)
records implementation status; the [Step 1.5c.4 closure](task_step1.5/HANDOFF.md)
and associated acceptance records retain test history.

Repository-root, workspace and project `AGENTS.md` instructions govern AI collaboration.
Official sources and Gentoo packaging belong in `joetoo-upstream` and `joetoo`,
respectively. Their repository-specific AI restrictions take precedence; no new
write authorization is granted by this architecture.

## 1. Purpose and release boundary

Replace the legacy X11 `xdotool_open_windows`, `xdotool_close_windows`, and
`xdotool_sizemove_this_window` workflows with `joetoo-kwin` on KDE Plasma/KWin
under **X11 and Wayland**. Support interactive local shells, declarative
multi-desktop launches, independently manageable SSH and graphical windows,
and conservative managed closure.

Version 1 requires an OpenRC-supervised `joetoo-kwind` management daemon and
reliable activation/reconnection of resident KWin JavaScript. Intermediate
prototypes are permitted; these are not deferred beyond version 1.

## 2. Supported development environment

Development and acceptance address Gentoo Linux, KDE Plasma/KWin on X11 and
Wayland, and an OpenRC user session. Native host and version information is
reported in the README and task evidence, not imposed as permanent product
requirements.

## 3. Components and ownership

| Component | Intended name | Owns | Must not do |
| --- | --- | --- | --- |
| Public Bash CLI | `joetoo-kwin` | Options, configuration selection, planning, launch orchestration, reporting | Infer ownership from class; kill unrelated processes |
| Broker daemon | `joetoo-kwind` | Session D-Bus API, transactions, managed registry, result history, future checkpoint/reconciliation | Parent or supervise SSH/Konsole sessions; independently calculate layout geometry |
| OpenRC user service | `joetoo-kwind` | Broker process supervision and user-session lifecycle | Terminate managed applications on service stop |
| KWin resident JavaScript | `joetoo-kwin-resident.js` | KWin observations, exact UUID resolution, window placement, one-shot initial stack/focus, future safe close | Own launch configuration; infer transport connection from window presence |
| Configuration/profile | `joetoo-kwin.conf` | Desired layout and configurable operational parameters, user override plus system fallback | Persist transient PID/UUID identity or credentials |

**D-Bus compatibility:** The service `org.joetoo.KWinBridge`, object
`/org/joetoo/KWinBridge`, and established method signatures are compatibility
contracts. Additive, specifically approved methods may extend this interface.

**Service lifecycle:** Broker restart must not kill Konsole, SSH or graphical
clients, close their windows, or relaunch them as a side effect. The resident
and broker shall synchronize a complete observed-window inventory on startup
and reconnection without adopting observations as managed windows. The manual
`joetoo_bridge_observe` shortcut remains diagnostic. Durable registry
reconstruction is future Step 1.7 work, not an assertion about current support.
The CLI must not invoke root-level SSH or require root for GUI management.

**Configuration discovery (accepted and implemented):** Explicit `-f FILE`
wins. Without `-f`, use
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf` when present;
otherwise fall back to `/etc/joetoo-kwin/joetoo-kwin.conf`. A present but
unreadable/invalid user file must not silently fall back. `XDG_CONFIG_HOME`
need not be set; its standard default is `$HOME/.config`.

**Control surface versus managed windows:** joetoo-kwin's control surface is not inherently a managed window, and it is not inherently singular. The OpenRC service and its broker must be initialized by an entity the broker does not manage, but afterward, any terminal or command line interface with access to the user's login shell can be used to control additional joetoo-kwin actions. "Managed" is an attribute assigned to positively identified application windows through authorized launch transactions. An existing Konsole, KDE application launcher, panel shortcut, or future graphical control interface may initiate those transactions without becoming managed itself. Explicit enrollment of preexisting windows, if implemented later, requires a separately approved identity and ownership contract. Graphical launch entry points must preserve the established confirmation and reporting safeguards.

**Packaging obligation (Step 1.9):** Distribute a documented configuration
template and provide ebuild post-install guidance for optional per-user
configuration. Do not populate HOME, overwrite user configurations, or modify
shell login files during package installation. Final template installation
paths and Gentoo dependency arrangements remain packaging decisions.

## 4. Identity, ownership, launch configuration, and transactions

### Runtime identity

| Identifier | Assigned by | Meaning | Lifetime |
| --- | --- | --- | --- |
| `run_id` | joetoo | Optional coordinated-run identifier | Execution/reporting |
| `request_id` | joetoo | One operation or transaction | Operation and bounded result history |
| `managed_id` | joetoo | Human-readable registered-window alias, e.g. `win-004` | Registered instance |
| `window_uuid` | KWin | Identity of a real compositor window | Window/compositor lifetime |

Each active managed registration uniquely associates one `managed_id` with
one `window_uuid`. Neither a window title nor a bare managed alias proves
ownership for destructive operations. Linux PIDs and observation-source
identities are independent metadata. Runs need not be retained after completion,
and not every CLI operation needs a broker-visible `run_id`.

### Joetoo-kwin window-management terms

**The following is a glossary of window-management concepts defined for
clarity, not a listing of literal configuration fields.** In particular,
`slot` is derived by the planner and is *not* a positional field in a
`desktop_session_list` entry.

| Term | Meaning |
| --- | --- |
| `desktop` | Intended numbered KWin virtual desktop; actual membership is independently observed and may be changed by the user |
| `slot` | One-based position of an entry among **all entries for its intended desktop**, in configuration order; persistent logical launch association, not geometry or a terminal position |
| `program` | Supported local application/executable selected for launch |
| `mode` | Explicitly defined program-specific behavior or transport, e.g. `local`, `ssh`, or a later approved remote mode; acceptance of a descriptive label alone does not grant executable support |
| `target` | Program/mode-specific command, directory, hostname or endpoint; interpretation must be defined per supported combination |
| `layer` | Optional initial stacking/layout classification: `under`, `panel`, or `over`, independent of program and not a persistent keep-above/below rule |

### `desktop_session_list` grammar

A trusted Bash configuration defines an indexed array of pipe-delimited
strings. Each entry has four mandatory positional fields and one optional
fifth field:

`DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`

`TARGET` can be the empty string only for approved program/mode combinations.
The fifth `LAYER` is optional: omitted means `panel`, retaining compatibility
with legacy four-field entries. Supported values are `under`, `panel`, `over`.
An explicit `panel` entry is different from an implicit panel for ordinary
layout-budget accounting where the current policy distinguishes them.

```bash
desktop_session_list=(
    "2|konsole|ssh|nuthuvia"
    "2|dolphin|local||under"
    "2|konsole|local|btop|over"
    "4|dolphin|local|Documents|panel"
)
# End of configuration
```

Here desktop 2 derives slots 1, 2 and 3; desktop 4 derives slot 1.
**There is no `slot` configuration field or sixth pipe-separated field.**
Desktop and slot together identify intended launch association, not an actual
compositor window. A caption such as `joetoo_konsole_3.1` may hint at desktop
3/slot 1 but is not a unique identity or ownership proof.

Entries may interleave desktops. Execution groups entries by desktop in the
order of each desktop's first appearance, retaining configuration order
within each group. Each desktop group finalizes its initial-layout transaction
before the next group begins. The planner assigns slot numbers before any
layer-based stacking reordering; moving a window never changes its slot.

### Layer, focus and one-shot layout semantics

Initial bottom-to-top stacking is **`under → panel → over`**, with
configuration order preserved within each layer. The preferred focus target
is the last successfully registered `over`, otherwise the last successful
`panel`; an `under` entry is never selected as the automatic preferred focus
target. Focus is requested only if the target desktop is currently displayed.
KWin receives at most one focus activation request and its asynchronous
completion is observed for a bounded interval. Placement, stack verification
and focus outcomes are separately reported. No automatic desktop switch is
performed to realize focus. After initialization, KWin and the user control
raising, movement, resizing, focus and desktop assignment without continuous
layout restoration.

### Logical association, duplicate protection and actual state

Positive registration preserves original intended `(desktop, slot)` in the
broker. KWin independently reports actual desktop membership (possibly
multiple desktops), geometry, window presence, stacking and focus. A present
managed window blocks a second launch for its original `(desktop, slot)` even
when moved or resized. Repeated SSH destinations in *different* slots are
valid. Uncertain ownership/presence must not be assumed released. The launcher
checks conflicts during preflight and the broker checks them atomically at
submission; unmanaged visual overlap is a warning, not a managed-slot conflict.
Broker-side logic must not calculate planned geometry. Window presence is not
SSH/RDP/VNC connection state.

Interactive `-m` on a preexisting unmanaged window does not register it,
assign an intended slot or make it eligible for `-x`/`-d`.

### Launch, correlate and complete

1. Validate configuration, effective bounds, whole plan and unsupported
   program/mode combinations before any application/network side effects.
2. Acquire the invocation-wide coordination lock, inspect KWin inventory,
   reserve the exact request and launch the chosen local application without
   joining the broker's process group.
3. Correlate uniquely via new KWin UUID, trustworthy PID, class/desktop file
   and optional diagnostic hints; never adopt an arbitrary matching class.
4. Positively register the UUID, apply requested desktop/geometry, verify
   readback, then finalize each group with a bounded UUID-owned one-shot
   stacking/focus transaction.
5. Distinguish unmatched/ambiguous, application launch, geometry/stack/focus,
   and transport/authentication outcomes. Report partial completion accurately.
   Isolated known failures may permit subsequent entries; uncertain Busy or
   ownership/transaction state must stop further submissions.

### Configuration and operational bounds

User-adjustable operational parameters govern planning, capacity, geometry,
timing and transactions. `desktop_limit`, `dt_win_limit`, percentages/gutters,
`min_window_exposure_px`, and initial-focus observation timing are examples.
Each configurable value needs a documented default in
`joetoo-kwin-template.conf`, units and safe validation bounds. New remote
launch timeouts, retries and leases must follow the same principle.

The CLI passes effective parameters explicitly across the broker/resident
boundary rather than relying on shared Bash globals. New parameters must be
bounded and cannot compromise ownership or coordination. Preexisting hardcoded
timing should be inventoried and migrated in focused, compatible increments.
Configuration values do not confer managed ownership or make unsupported
program/mode combinations executable.

## 5. Working registry and operation outcomes

The broker logically maintains `observed_windows` (all KWin observations),
`managed_windows` (positively identified instances), bounded `requests`,
transient `runs`, future application-specific `application_sessions`, and
`graphical_context` (KWin/broker observation source). Exact Python data
structures are implementation choices. The broker observes changes and
processes explicit operations; it does not automatically restore planned
geometry after a manual change.

### Registry invariants (established in Step 1.4)

1. Registration requires a synchronized prelaunch inventory, unambiguous
   correlation with a new UUID, no material observation gap and confirmation
   the UUID is still present.
2. Only a broker-associated successful correlation grants managed registration;
   diagnostic observation, manual movement, and class/title similarity do not.
3. UUID and managed ID are unique and bidirectionally associated in the live
   registry; conflicting registration leaves prior records unchanged.
4. Window existence, initial placement, operation result and application
   session state are independent. A failed connection does not erase a
   successfully placed window, nor create a connected session.
5. Updates and removal use exact UUID observations. Missing/uncertain windows
   are not silently adopted under another UUID.
6. Managed status alone is not sufficient authorization for future destructive
   operations. Confirm current ownership/source before closure.
7. Multiple records and completed requests coexist; bounded serialization
   is allowed but no arbitrary fixed total window count is required.
8. Read-only `ListManaged`, `GetManaged` and `RegistryStatus` contracts remain
   available without granting new destructive access.

### Independent state dimensions

| Dimension | Representative states |
| --- | --- |
| Request | `pending`, `running`, `succeeded`, `failed`, `timeout`, `ambiguous` |
| Window observation | `present`, `missing`, `uncertain` |
| Placement | `not_requested`, `pending`, `succeeded`, `failed` |
| Application connection | `not_attempted`, `connecting`, `connected`, `unavailable`, `exited`, `unknown` |

Actual API representations and transitions follow the implemented registry;
these are architectural dimensions, not a requirement for a new general
state-machine framework. Broker-lifetime IDs and same-session checkpoint
recovery remain distinct until Step 1.7. A window may support multiple
application sessions over its life; generalized transport telemetry was not
implemented by Step 1.5c.4.

## 6. Shared geometry, layers and visibility

`-c`, `-o` and interactive `-m l|r` share planner geometry calculations. The
broker must not independently generate placement coordinates.

### 6.1 Panel allocation and budget

The panel allocator supports one through four panel entries in ordinary
one/two/three-region layouts and the four-region two-by-two arrangement.
Defaults reserve 87% of the configured screen width for the terminal/panel
region, with configurable gaps, position and dimensions. **Panel allocation
is application-independent**: Dolphin can occupy a panel, and Konsole can
appear in an explicit `under` or `over` layer. The panel limit applies to
panel positions, not the number of accessible SSH connections.

An ordinary `dt_win_limit=4` implicit-entry budget is enforced; explicit
layers may increase the total window count with a warning without bypassing
the four-panel allocator or other safety limits. All configured windows
receive logical slot numbers, regardless of the physical allocator position.

### 6.2 Graphical regions and stacking

`under` and `over` use the configurable graphical region dimensions
(`graphical_left_percent`, `graphical_top_percent`,
`graphical_width_percent`, `graphical_height_percent`) and cascade offsets.
After positive registration, one bounded cohort transaction establishes and
verifies bottom-to-top `under → panel → over`, preserving entry order within
each layer. The last successful `over` or, absent that, last `panel` is
preferred focus when the group desktop is displayed. No permanent keep-above,
keep-below or continuous repair behavior is imposed.

### 6.3 Exposure and its limits

`min_window_exposure_px` is a configurable desired minimum exposed *logical
pixel* rectangle for graphical windows. Planner frame-rectangle predictions
warn about insufficient exposure and possible unmanaged obstructions; these
warnings are not proof of compositor-visible clickable regions and are not
ordinary launch failures. Decorations, scaling, reserved work areas, other
windows and real KWin stacking may affect actual usability. An ergonomically
unhelpful layout can still be technically valid. The obsolete proposed
`underlay_protrusion_percent` is **not** the accepted exposure contract.

### 6.4 Interactive movement and display limitations

The six accepted `-m` forms are `l|r`, `DESKTOP`, `DESKTOP l|r`,
`DESKTOP X Y`, `X Y WIDTH HEIGHT`, and `DESKTOP X Y WIDTH HEIGHT`.
Omitted desktop/position/size fields are preserved independently; the KWin
resident reads actual `frameGeometry`. These moves do not assign managed
slots. Default `screen_width`/`screen_height` remain explicitly configured,
**not autodetected**; multi-monitor output selection, work area deductions,
reserved panels and scale-aware clickable exposure need future specification.

## 7. Unavailable SSH is a valid placeholder

A configured unreachable SSH endpoint may still yield a correctly placed
managed Konsole with the **original local interactive Bash** and a manual
retry instruction. Use `ssh_wrapper` in the original `bash --rcfile` context;
`swr` has different wait/retry semantics and is not an automatic replacement.
Do not use `exec`, a replacement shell, mandatory tmux, root SSH or a new
always-enabled Konsole-sensitive D-Bus interface to simplify lifecycle.
A short bounded network probe must not suppress a usable placeholder.

Known isolated launch failures permit safe continuation; unresolved Busy,
ownership or transaction ambiguity stops further submissions. Preserve
already created windows and report partial success; do not automatically roll
back. Layout completeness means positively registered and placed requested
windows regardless of SSH connection availability. An unregistered or unplaced
required window makes the layout incomplete. Future `-r` creates new
connections/windows; it cannot revive old SSH processes. Application
connection and window management remain independent.

## 8. Runtime checkpoint versus restorable layout

### 8.1 Private runtime checkpoint (Step 1.7 target)

Broker memory is the active authority. A private atomic checkpoint at
`$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json` should copy valid current
registry identifiers, results and compositor/session source, **not** act as a
clean-reboot template. Restrict directory/file permissions and exclude
credentials. On same-session restart, validate KWin source and exact live UUIDs
conservatively; missing/uncertain identity cannot authorize destructive acts.
Broker/service stop must not close applications. This recovery is future scope.

### 8.2 Durable last-good launch layout (Step 1.8 target)

A reusable trusted Bash `.conf` snapshot is proposed at
`${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf`.
It stores validated desired launch recipes and policy, not old UUIDs/PIDs.
An unreachable SSH target with successfully placed placeholder counts as a
valid recipe. Write atomically; do not overwrite a valid snapshot with partial
or empty state. `-r` launches a new set through the normal planner with new
UUIDs/PIDs/connections. `-S` exports a chosen arrangement with verified current
geometry once its schema is approved. `-x`/`-d` should not implicitly erase
last-good history. Automatic advancement triggers and representation of manual
geometry remain open design questions; trusted config files must not be
modifiable by unrelated processes.

## 9. CLI contract (target; not all flags implemented)

| Invocation | Intended action |
| --- | --- |
| `-c [-f CONFIG]` | Validate config and display a colorized dry-run plan without launching |
| `-o [-f CONFIG]` | Confirm then launch and positively register/position managed windows |
| `-L DESKTOP PROGRAM MODE TARGET [LAYER] | Confirm then launch and positively register/position one managed window |
| `-m l|r` | Two-panel active-window geometry on current desktop |
| `-m DESKTOP` | Change active window's desktop, preserve geometry |
| `-m DESKTOP l|r` | Two-panel placement on specified desktop |
| `-m DESKTOP X Y` | Change desktop/position and preserve size |
| `-m X Y WIDTH HEIGHT` | Change position/size and preserve desktop |
| `-m DESKTOP X Y WIDTH HEIGHT` | Specify desktop, position and size |
| `-x` | Gracefully close all positively managed windows, not unrelated ones (future 1.6) |
| `-a` | Add one managed window (future; syntax TBD) |
| `-d MANAGED_ID` | Close one safely validated managed window (future 1.6) |
| `-l`, `-i MANAGED_ID`, `-s` | Readable registry/detail/application-status interfaces as supported |
| `-S` | Export reusable layout (future 1.8) |
| `-r` | Restore a saved last-good layout using new instances (future 1.8) |
| `-f FILE` | Explicit configuration precedence, no implicit symlink edits |
| `-v`, `-q` | Adjust verbosity using established joetoo CLI conventions |

Retain `j_msg`, announce/act/report, `separator`, color styling, effective
`varlist`/`show_config`, and the script-header joetoo CLI conventions. A
configured launch presents its effective configuration/plan and seeks
confirmation **before** any application/network side effects. The table
contains targets for later milestones as well as accepted features; see README
for the implemented subset. Preserve `mw` and legacy convenience shorthands
without introducing a second geometry implementation.

## 10. Supervision, safety and identity invariants

1. A managed UUID must be correlated to a specific launch and validated against
   current observation/source before it is eligible for future `-d` or `-x`.
2. A raw UUID or readable alias is not a standalone destructive capability.
3. Broker restart must not relaunch clients; application close must not imply
   broker shutdown.
4. Destructive operations, when authorized, must be graceful with confirmed
   removal, never arbitrary class matching or process-group killing.
5. The broker runs with ordinary graphical user privileges on the correct
   session bus, without privileged root SSH or system-wide OpenRC shortcuts.
6. Window, launch transaction and remote-session state remain independent.
7. Do not leak private credentials, host secrets or bearer tokens in public
   sources, arguments, D-Bus diagnostics or logs.
8. Preserve established POCs as historical references; don't rewrite them
   without separate authorization.
9. New remote viewers and tunnels must fail conservatively on uncertain
   ownership or authentication and clean up only processes they own.

## 11. Numbered implementation and review gates

Completion history is maintained in README and task evidence. Each gate
identifies a product objective; it is **not** independent permission for an
AI agent to edit code, deploy, connect to remote hosts, or merge. Later
accepted decisions refine older scope outlines without rewriting history.

### Phase 1 — Initial implementation

| Gate | Deliverable | Acceptance / status |
| --- | --- | --- |
| **1.1–1.4d** | Architecture, OpenRC user service, resident KWin observation, UUID correlation, managed registry/queries, multiwindow placement | Completed; see project README and Step 1.4 closure |
| **1.5a** | Configuration precedence, shared planner and colorized `-c` | Accepted |
| **1.5b** | Interactive `-m` forms and independent omitted-value preservation | Accepted on X11 and Wayland |
| **1.5c.1** | `-o` preflight, plan, confirmation and invalid-plan refusal | Accepted |
| **1.5c.2** | Sequential managed launches, positive UUID registration, geometry and duplicate-slot safety | Accepted |
| **1.5c.3** | Original local Bash, `ssh_wrapper` and unavailable SSH placeholders | Accepted |
| **1.5c.4** | Desktop capacity, Dolphin local launches, XDG discovery, application-independent `under/panel/over`, grouped launches, bounded initial stack/focus | Accepted, merged; native X11/Wayland closure evidence in Step 1.5 task |
| **1.5c.5a** | Dolphin SFTP integration | Proposed next increment; approved endpoint/URI grammar and separate remote-access status before implementation |
| **1.5c.5b** | TigerVNC viewer over authenticated SSH | Proposed next increment; inspect existing functioning KDE launcher/POC, verify compatibility, then approve minimal managed-launch translation |
| **1.5c.5c** | Comparative RDP feasibility and decision | Evaluate installed candidates, security, capability and user value; an accepted secure/reliable RDP workflow may supersede legacy VNC as primary graphical remote access; implementation requires explicit follow-up authorization |
| **1.5d** | add -L, -l; conduct integrated native X11/Wayland regression of completed Step 1.5 capabilities | Cross-feature ownership, Busy, focus, desktop membership, failures and completeness; not an implicit feature-development gate |
| **1.6** | Managed `-a`, `-d`, `-x` | Selective safe close, never unrelated windows |
| **1.7** | Runtime JSON checkpoint and same-session reconciliation | Broker restart and exact source/UUID reconciliation |
| **1.8** | Restorable `.conf` snapshot, `-S`, `-r` | New-window recovery from validated last-good intent |
| **1.9** | `eselect`, installation/ebuild and complete integration | Maintainer-led joetoo/joetoo-upstream packaging, template guidance and version 1 lifecycle |

### 1.5c.5 — Remote resource and desktop integration (proposed; not yet authorized)

**Common contract:** Each approved new `program|mode|target` combination
must define exact parsing, local process invocation, authentication and
security assumptions, positive unique KWin UUID identity, desktop/slot
placement, layer behavior, transport/session lifecycle, bounded cancellation,
and truthful partial success. Reuse existing CLI/planner/broker/resident
interfaces wherever possible. Do not introduce a generic remote-access
framework or unnecessary broker expansion. Unsupported recipes reject before
confirmation and before process or network side effects.

**1.5c.5a — Dolphin SFTP (first).** Investigate installed Dolphin/KIO SFTP
behavior, target grammar (user, hostname, IPv6, optional port and remote
path), safe URI encoding and credentials handling, and `--new-window` PID/UUID
correlation. Then, on separate explicit implementation approval, add
`dolphin|sftp|TARGET` to the known safe local-Dolphin launch framework. A
remote file navigation/authentication failure is not a KWin placement failure.
Do not execute remote Dolphin or treat KIO file transfer as SSH GUI forwarding.

**1.5c.5b — TigerVNC over SSH (second).** First inspect the existing archived
`archive/tigervnc-poc/vnc-via-ssh-launch` and the maintainer's *working*,
KDE-application-launcher-integrated TigerVNC-over-SSH invocation. This path is
already demonstrated operational by the maintainer: concentrate on actual
command-line compatibility with the managed launch model, accurate viewer
window identity, and minimal safe translation into script activation. The
candidate is not thereby presumed cryptographically secure or production
ready; determine actual tunnel options, loopback binding, SSH host-key
verification, VNC authentication, child/tunnel ownership and cleanup. No
**direct VNC** is authorized, including on local LAN. Distinguish viewer
existence/placement from tunnel, authentication and remote-display success.
If source inspection reveals material weaknesses in the POC, report them
rather than blindly copying it into a supported executable recipe.

**1.5c.5c — RDP feasibility and decision (third).** Deliberately evaluate
*each viable graphical remote-desktop client candidate* identified in the
original 1.5c.4 inventory and the now-installed toolset; at minimum assess
KRDC, Remmina (if available), and appropriate installed or installable
FreeRDP graphical clients. For each candidate report exact executable and
installed-version evidence per test host, KWin X11/Wayland integration,
RDP/TLS negotiation and certificate verification, authentication and
credential exposure, invocation/endpoint grammar, PID→UUID identity,
window/dialog lifecycle, usability, feature support, failure reporting,
operational complexity, and security advantages/disadvantages. Compare them
with the TigerVNC-over-SSH workflow and present a ranked, reasoned
implementation recommendation. **A reliable and demonstrably secure RDP
client is the preferred prospective primary graphical remote-access method;
legacy TigerVNC-over-SSH remains a compatibility/fallback candidate.**
Feasibility assessment does not itself authorize RDP implementation.
If the maintainer approves an RDP implementation, define a separate bounded
candidate and native acceptance gate before integrating it.

**Implementation scope:** The [Step 1.5c.5 implementation scope](task_step1.5/Step1.5c5_implementation_scope.md) elaborates the proposed remote-access increments and their acceptance gates. It does not supersede this architecture or independently authorize implementation; current task permissions are controlled by the separately approved `HANDOFF.md`.

**Broader application inventory (evaluation, not automatic implementation):**
Newly installed on `gmki91` as reported by the maintainer: QTerminal 2.4.0,
Krusader 2.9.0, FileZilla 3.70.6, Nautilus 49.6-r1, Nemo 6.6.4,
KRDC 26.04.3, and Midnight Commander (`mc`) 4.8.33. Verify the actual
executables, runtime behavior and installed versions on each host before
relying on them. Earlier “not available” assessments must not be treated as
current evidence. Evaluate their potential for safe managed launch, local and
SFTP workflows, application-specific PID/UUID correlation, and value over
supported Dolphin/Konsole paths. Report feasibility and advantages/
disadvantages **per candidate**, recommending implement/defer/reject.
`mc` is a *text-based terminal application*, not an independent KWin graphical
window: evaluate whether joetoo-kwin should offer it as a terminal-launched
workflow and what it adds beyond `konsole|local|...`. On `gmki91`, the
reported `mc` build has `-sftp`; do not assume SFTP support without
rebuilding or inspecting capabilities. Availability does **not** establish
that these candidates belong in the immediate implementation tranche.

**Security and sequencing:** RDP transport protection and certificate
verification must be evaluated as properties of a concrete client and
configured connection, not inferred from the word `tls`. Existing network
reachability/VPN assumptions are not a substitute for verifying SSH tunnel
binding or TLS trust where those properties are part of the chosen contract.
Do not require a new generic VPN detector. Inspect both X11 and Wayland and
report differences. First approve 1.5c.5a interface+implementation, then
inspect/approve 1.5c.5b, then undertake the 1.5c.5c comparison and obtain a
**new** decision for any RDP implementation. Step 1.5d begins after the
selected integrations are accepted or explicitly deferred. No new HANDOFF
permissions are granted by this document.

### Phase 2 — Optimization and refinement

Once essential Phase 1 functionality has been demonstrated on both backends,
measure startup, launch, placement, D-Bus, polling, CPU/memory and user-visible
latencies; then prioritize targeted improvements. Preserve safety, compatibility,
function and both X11/Wayland regressions. Optimization does not defer
correctness/security requirements. Split refinements into reviewable, measured
tasks rather than broad speculative rewrites.

## 12. Open questions and explicit verification tasks

- How should managed-window recovery validate broker/KWin session identities
  across restart, and what should remain unrecoverable without a live UUID?
- Which monitor/work-area, reserved panel and scaling policy should govern
  geometry and actual clickable exposure?
- How should a future explicit reset-to-intended-layout action distinguish
  original slot from current geometry and reordered configuration entries?
- When should last-good snapshots advance, and how should manually adjusted
  coordinates be represented in reusable configuration?
- What are the exact syntax and selection safeguards for `-a` and `-S`?
- Which remote-resource endpoint grammars, connection/credential policies and
  application lifecycles best fit each 1.5c.5 candidate?
- Can any RDP client provide verified secure negotiation, convenient workflow
  and robust managed-window identity under both KWin backends?
- Should joetoo's Bash planner be evaluated for non-KWin environments such as
  LXQt/GNOME in a separately authorized later effort? This is not a version 1
  portability commitment.

