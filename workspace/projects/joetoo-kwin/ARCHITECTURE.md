# joetoo-kwin — architecture and version 1 requirements

This is the project-specific design record for `joetoo-ai/workspace/projects/joetoo-kwin/`.
It distinguishes accepted requirements, implemented and accepted contracts, proposed
future capabilities, and open design questions. The [project README](README.md)
records current implementation status. The [accepted Step 1.6 archive](archive/task_step1.6/README.md)
and [Step 1.7 archive](archive/task_step1.7/README.md) preserve their merged
results and evidence. The [active Step 1.9 HANDOFF](task_1.9/HANDOFF.md)
tracks version 1 packaging/integration; [Step 1.5c.4 native closure](archive/task_step1.5/step1.5c4-native-acceptance.md)
and other task evidence retain the earlier acceptance history.

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
`joetoo_bridge_observe` shortcut remains diagnostic. Private same-session
checkpoint/reconciliation is implemented and accepted in Step 1.7; this does
not authorize adoption of stale identities after a new KWin session.
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

**The following recipe combinations include accepted configured RDP support.**

```bash
desktop_session_list=(
    "2|konsole|ssh|nuthuvia"
    "2|dolphin|local||under"
    "2|konsole|local|btop|over"
    "4|dolphin|local|Documents|panel"
    "4|dolphin|sftp|sftp://joe@nuthuvia.brendler/etc|panel"
    "4|vncviewer|ssh|ssh://joe@yorsqui/display/2|panel"
    "5|sdl-freerdp|rdp|rdp://joe@opi6plus01:3389|under"
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

### `TARGET` grammar

`TARGET` is interpreted together with the exact `PROGRAM|MODE` pair. It is **not** a generic executable argument string. Square brackets below indicate optional syntax, except brackets around an IPv6 literal (`[IPv6]`) are literal URI syntax. `[:PORT]` is a per-recipe decimal TCP port (1..65535), not a new pipe-delimited field. Ports not explicitly provided follow the selected application's documented default or its permitted transport configuration.

| `PROGRAM\|MODE` | `TARGET` syntax | Port and interpretation |
| --- | --- | --- |
| `konsole\|local` | `EXECUTABLE` | Executable **basename** on `PATH`, for example `btop`; no command arguments or port. |
| `konsole\|ssh` | `[USER@]HOST` | Hostname, SSH alias or user-qualified host. **No explicit `[:PORT]` syntax is currently supported.** Existing precheck probes TCP 22, even where SSH configuration could choose a different port; fix that mismatch separately. |
| `dolphin\|local` | `[DIRECTORY]` | Empty means home; absolute directories are literal; relative directories resolve against home. No port. |
| `dolphin\|sftp` | `sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH]` | Optional SFTP endpoint port; omitted uses Dolphin/KIO/SSH configuration (ordinarily SSH port 22). Missing path requests login directory; `/` requests remote root. |
| `vncviewer\|ssh` | `ssh://[USER@]HOST[:SSH_PORT]/display/N` or `ssh://[USER@]HOST[:SSH_PORT]/port/P` | `[:SSH_PORT]` selects the **SSH** port, not VNC. `/display/N` reaches remote VNC TCP `5900+N`; `/port/P` names remote VNC TCP `P`. The worker allocates the local loopback forwarding port, never the recipe. |
| `sdl-freerdp\|rdp` | `rdp://USER@HOST[:PORT]` | Explicit username required; omitted port means RDP TCP 3389. No password, query, fragment, path or arbitrary client switches. This pair is accepted and implemented in configured `-o` and single-recipe `-L`. |

URI parsers validate hosts (including bracketed IPv6 literals where supported), port ranges, user information and path rules **before** launch. They must reject embedded passwords and avoid reflecting untrusted targets or credentials in error messages. SFTP path encoding and VNC forwarding behavior remain client-specific. A `TARGET` URI does not supply the desktop, derived slot, layer or final geometry; those remain common planner responsibilities.


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
state-machine framework. Broker-lifetime IDs and the accepted Step 1.7
same-session checkpoint/recovery remain distinct from fresh-instance restore.
A window may support multiple application sessions over its life; generalized
transport telemetry was not implemented by Step 1.5c.4.

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
required window makes the layout incomplete. Step 1.7 `-r` creates new
connections/windows; it cannot revive old SSH processes. Application
connection and window management remain independent.

## 8. Recovery and restorable layout (combined version 1 Step 1.7)

**ACCEPTED AND MERGED (2026-11-19, [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33),
`df118da`).** The maintainer combined the formerly separate Steps 1.7 and 1.8
into one delivered recovery/snapshot milestone. The two responsibilities retain
**distinct data representations, trust and verification contracts**. See the
[Step 1.7 archive](archive/task_step1.7/README.md),
[formal acceptance](archive/task_step1.7/step1.7-maintainer-acceptance-2026-11-19.md)
and [PR #33 merge closure](archive/task_step1.7/step1.7-pr33-merge-closure-2026-11-19.md).

### 8.1 Private same-session checkpoint and reconciliation

Broker memory remains authoritative while the broker runs. The private,
atomically replaced runtime checkpoint at
`$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json` stores validated
managed identities, desktop/slot reservations and bounded last-known metadata
for same-session reconciliation. It excludes credentials; historical PIDs,
UUIDs and observations never become standalone destructive authority.

On broker restart **within the same still-running KWin session**, reconcile
against the current authenticated compositor/source and exact live UUIDs.
Reconstruct only what current authenticated evidence proves; missing or
uncertain identities are retained non-destructively, never adopted as new
managed windows. Neither broker stop nor checkpoint replay closes or relaunches
application windows. A reboot/new KWin session is not an old-UUID recovery
target; any later restore uses fresh instances through `-r`.

### 8.2 Durable last-good launch plan and fresh-instance restore

The separate durable last-good store uses
`${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf` as a
relative pointer to immutable timestamped snapshot files. Protocol 2 saves
normalized *launch intent*: verified managed recipes and shared effective
settings, **not** old UUIDs, PIDs, active connections, credentials or
operator-adjusted window geometry. Private modes, atomic publication and
configurable history retention protect the store. Legacy protocol-1 snapshots
remain readable/migratable. Partial, failed or empty arrangements cannot
silently replace last-good; `-d` and `-x` do not save or erase it.

`-S` explicitly exports a complete, authenticated, positively registered and
placed managed arrangement, refusing incomplete/missing entries; it does not
copy arbitrary unmanaged windows. `-r` validates the saved plan through the
normal preflight, confirmation and launch path, creating **new** windows,
identifiers and remote connections. A correctly placed unreachable-SSH
placeholder may be an eligible recipe; transport success remains independent
of layout validity. Restore never revives an old remote process.

### Accepted Step 1.7 boundary and evidence

The delivered contract uses authenticated KWin source/UUID reconciliation for
an unchanged session and complete managed launch recipes for new-instance
restore. It refuses incomplete snapshots and occupied desktop/slot restores;
manual frame adjustments are not promised by `-r`. The accepted native X11 and
Wayland tests, including failed-save preservation and retained missing-record
history, are documented in the [Step 1.7 archive](archive/task_step1.7/README.md).
A fresh KWin session must never inherit destructive authority over old UUIDs.

Step 1.9 packaging is the next distinct version 1 workstream; these accepted
Step 1.7 decisions are not Version 2 deferrals.

## 9. CLI contract (target; not all flags implemented)

| Invocation | Intended action |
| --- | --- |
| `-c [-f CONFIG]` | Validate config and display a colorized dry-run plan without launching |
| `-o [-f CONFIG]` | Confirm then launch and positively register/position managed windows |
| `-L DESKTOP PROGRAM MODE TARGET [LAYER]` | Confirm then launch one managed window above existing windows; `over` is the only implemented layer (also the default), no live-desktop reflow |
| `-m l\|r` | Two-panel active-window geometry on current desktop |
| `-m DESKTOP` | Change active window's desktop, preserve geometry |
| `-m DESKTOP l\|r` | Two-panel placement on specified desktop |
| `-m DESKTOP X Y` | Change desktop/position and preserve size |
| `-m X Y WIDTH HEIGHT` | Change position/size and preserve desktop |
| `-m DESKTOP X Y WIDTH HEIGHT` | Specify desktop, position and size |
| `-x` | **Accepted 1.6:** confirmed fixed-set progressive retirement of authenticated absences and verified graceful closes; retain failed/unresolved entries |
| `-d MANAGED_ID` | **Accepted 1.6:** confirmed graceful close of one authenticated managed window; record/slot retained |
| `-l` | List broker-managed windows read-only, one record per fixed-width table row, including stable managed ID, desktop/slot, presence, placement and UUID (Step 1.5d) |
| `-i MANAGED_ID`, `-s` | Additional detail/application-status interfaces, not implemented in Step 1.5d |
| `-S` | **Accepted Step 1.7:** export a complete verified managed arrangement as private last-good launch intent with timestamped history; refuse incomplete saves |
| `-r` | **Accepted Step 1.7:** preflight and confirm restore of saved recipes as **new** managed instances, never adopting old UUIDs or PIDs |
| `-f FILE` | Explicit configuration precedence, no implicit symlink edits |
| `-v`, `-q` | Adjust verbosity using established joetoo CLI conventions |

**Step 1.5d CLI decisions (maintainer, revised 2026-11-11).** The `-L` operands
are the same logical fields as one `-o` recipe, but supplied as **separate
positional arguments**, not a single pipe-delimited argument:
`DESKTOP PROGRAM MODE TARGET [LAYER]`. **Only `over` is implemented for `-L`**:
an omitted LAYER defaults to `over`; explicit `over` is supported; explicit
`panel` or `under` must be rejected before launch with a helpful diagnostic
such as `-L: layer 'panel' is not implemented yet; use 'over' or omit LAYER`.
Do not promise a release/version for unsupported layers. Crucially, `-o`
retains its accepted `under`/`panel`/`over` layers and implicit `panel` default.

`-L` launches **one** new window, using the existing program/mode/target
validators, graphical-region geometry, confirmation, broker reservation,
positive exact-UUID registration, placement and cleanup machinery. It chooses
an unused logical slot without modifying any existing or retained reservation;
there is no sixth SLOT operand. It places the new window on its requested
desktop and performs a bounded, verified **one-shot raise** so it appears above
existing windows, without a permanent keep-above rule. It must not change the
geometry, ownership or identity of existing managed **or unmanaged** windows,
and must not perform live-desktop panel reflow, peer recascading or a new
application-independent managed-ID geometry transaction. Before launching or
contacting a remote endpoint, report the specific invalid field/requirement
(desktop/program/mode/target/layer), safely redacting sensitive input.
Preserve already-accepted `-o` behavior and fail-closed Busy/source/identity
requirements. If a one-shot raise cannot be positively targeted and verified
on both KWin backends, report the constraint instead of adopting a different
window or weakening ownership.

Live reflow beyond accepted `-L` behavior is deferred; see
[Version 2 Considerations](#12-version-2-considerations) and the archived
Step 1.5 task evidence for the earlier investigation.

The `-l` command displays the broker's **managed** inventory read-only as
aligned, fixed-width columns, **one row per managed record**. At minimum
include `MANAGED_ID`, `DESKTOP`, `SLOT`, `PRESENCE`, `PLACEMENT` and the
full `WINDOW_UUID`, clearly showing retained missing records and original
desktop/slot reservation. Human operators need the stable ID to refer to
other managed windows in future `-d`/close commands; listing must not
silently select, activate, or change any window. Preserve authoritative
broker status without inventing remote connection or authentication state;
distinguish an empty registry from unavailable or inconsistent broker state.
Additional fields may be shown if actually exposed and safe.

Retain `j_msg`, announce/act/report, `separator`, color styling, effective
`varlist`/`show_config`, and the script-header joetoo CLI conventions. A
configured launch presents its effective configuration/plan and seeks
confirmation **before** any application/network side effects. The table
contains targets for later milestones as well as accepted features; see README
for the implemented subset. Preserve `mw` and legacy convenience shorthands
without introducing a second geometry implementation.

## 10. Supervision, safety and identity invariants

1. A managed UUID must be correlated to a specific launch and validated against
   current authenticated native UUID/source before it is eligible for `-d` or `-x`.
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

### Version 1 — Initial implementation

| Gate | Deliverable | Acceptance / status |
| --- | --- | --- |
| **1.1–1.4d** | Architecture, OpenRC user service, resident KWin observation, UUID correlation, managed registry/queries, multiwindow placement | Completed; see project README and Step 1.4 closure |
| **1.5a** | Configuration precedence, shared planner and colorized `-c` | Accepted |
| **1.5b** | Interactive `-m` forms and independent omitted-value preservation | Accepted on X11 and Wayland |
| **1.5c.1** | `-o` preflight, plan, confirmation and invalid-plan refusal | Accepted |
| **1.5c.2** | Sequential managed launches, positive UUID registration, geometry and duplicate-slot safety | Accepted |
| **1.5c.3** | Original local Bash, `ssh_wrapper` and unavailable SSH placeholders | Accepted |
| **1.5c.4** | Desktop capacity, Dolphin local launches, XDG discovery, application-independent `under/panel/over`, grouped launches, bounded initial stack/focus | Accepted, merged; native X11/Wayland closure evidence in Step 1.5 task |
| **1.5c.5a** | Dolphin SFTP integration | Accepted and closed; managed X11/Wayland launches and remote browsing demonstrated; optional post-confirmation NSS/TCP advisories remain non-enforcing diagnostics |
| **1.5c.5b** | TigerVNC viewer over authenticated SSH | Accepted and retained as a peer-level managed graphical remote-access option; native X11 and Wayland/XWayland identity, placement, SSH tunnel and teardown demonstrated |
| **1.5c.5c** | Comparative RDP feasibility and decision | **Closed:** affirmative feasibility accepted; SDL3 FreeRDP selected for first RDP implementation, not as a preferred/default client |
| **1.5c.5d** | Managed SDL FreeRDP under configured `-o` | **ACCEPTED, CLOSED AND MERGED (2026-11-11, PR #29)**: exact UUID/placement/lifecycle on native X11/Wayland, layered configuration, bounded clean-failure continuation, strict `/sec:nla /cert:deny` defaults, successful trusted GDM connection and automatic invalid-certificate refusal with verified cleanup; see final Increment 5 evidence |
| **1.5d** | Implement `-L` one-recipe single-window launch (`over` only; no reflow), retain read-only `-l` inventory; run integrated native X11/Wayland regression | **ACCEPTED, CLOSED AND MERGED (2026-11-12, PR #30)**: `-l` implemented; `-L` implemented under simplified scope, preserving field-specific validation, safe logical-slot reservation, exact-UUID placement, one-shot raise, existing-window geometry and accepted `-o` semantics |
| **1.6** | Managed `-d`, `-x` | **ACCEPTED AND MERGED** (2026-11-18, [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32), `a6999e2`); [archived evidence](archive/task_step1.6/README.md) on Wayland/XWayland and native X11 |
| **1.7 (includes former 1.8)** | Private same-session checkpoint/reconciliation **plus** durable `.conf` last-good snapshot, `-S`, `-r` | **ACCEPTED AND MERGED** (2026-11-19, [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33), `df118da`); [archived Wayland/X11 evidence](archive/task_step1.7/README.md) |
| **1.9** | Packaging of the accepted optional `eselect` selector, installation/ebuild and complete integration | **NEXT (kickoff/planning):** maintainer-led joetoo/joetoo-upstream packaging, templates and version 1 lifecycle; [active HANDOFF](task_1.9/HANDOFF.md) |

### Accepted remote-resource contract (Step 1.5; historical detail archived)

Every supported `program|mode|target` recipe retains exact input validation,
separately bounded launch/placement/transport outcomes, positive managed
PID/UUID/source ownership, and safe owned-process teardown. Unsupported
recipes fail before confirmation and network/application side effects.

- **Dolphin SFTP:** validate `sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH]`,
  safely encode/redact URL components, and launch *local*
  `dolphin --new-window -- URL`. Preserve KIO/libssh authentication and host
  trust, not a second root-level SSH path. Post-confirmation reachability
  advisories separately test bounded DNS and TCP only when the *effective*
  endpoint can be established. Never run advisories in `-c`, before `-o`
  confirmation or during offline validation. Explicitly distinguish success,
  failure and indeterminate/not-attempted for each advisory; direct DNS/TCP
  may be misleading with SSH aliases, proxies or nonstandard transports.
  Failure/uncertainty **cannot block** a valid Dolphin/SFTP launch or turn a
  successful local placement into a claim of authenticated SFTP usability.
  No silent fallback to a local path is authorized.
- **TigerVNC-over-SSH:** validate
  `ssh://[USER@]HOST[:SSH_PORT]/display/N` (or `/port/P`) and use one owned,
  loopback-only SSH forward; no direct/raw VNC or competing TigerVNC `-via`
  tunnel. Positive persistent viewer-role evidence, original PID/UUID,
  compositor source and launch transaction are required; an authentication
  popup sharing a process/class is never silently adopted as the desktop
  viewer. Own and clean up only the forward/viewer processes of this launch,
  without broad PID/class killing. Viewer presence, network/authentication,
  and actual remote usability remain independent outcomes.
- **SDL FreeRDP:** first supported RDP peer, not a preferred/default over
  TigerVNC. X11 and Wayland have positive, client-specific viewer-role and
  exact-UUID selectors; configured serial launches require independently
  bounded readiness/placement/cleanup and verified safe continuation. Accepted
  built-in `rdp_security_protocol=nla` and `rdp_certificate_policy=strict`
  map to `/sec:nla` and `/cert:deny`; alternate supported `negotiate`/`prompt`
  are explicit configuration choices and do not turn permissive TLS into a
  default. Registration and local geometry never prove remote login or trust.

The accepted detailed requirements and their chronological decisions are
preserved in [Step 1.5 archive](archive/task_step1.5/README.md),
[final managed RDP acceptance](archive/task_step1.5/step1.5c5d-increment5-final-native-acceptance-2026-11-11.md),
and the current [configuration reference](docs/configuration-reference.md).
No superseded Option C/diagnostic-gate text is an active requirement.

**Step 1.6 accepted contract:** A confirmed `-d MANAGED_ID` gracefully closes
one exact managed window while retaining its original record and slot. A
confirmed `-x` uses a fixed set, retires authenticated missing windows and
verified closed windows progressively, and retains failed/uncertain targets
without force kill or false rollback. The native adapter and X11 fence are
specified in [native managed-close](native/managed-close/README.md); evidence
and qualifications are in [the archived Step 1.6 task](archive/task_step1.6/README.md).

## 12. Version 2 Considerations

This section is the **single current holding place** for explicitly deferred
or exploratory changes. These are **not** version 1 requirements, release
blockers, or implicitly authorized development tasks. The accepted original
decisions remain traceable in archived Step 1.5/1.6/1.7 evidence; historical
files should not be rewritten to imply different past outcomes. Accepted
Step 1.7 recovery and snapshot work is complete; Step 1.9 packaging remains
version 1 work, **not** deferred to Version 2.

### Settled deferrals and design principles

1. **Individual close-and-retire `-D MANAGED_ID`:** deferred to Version 2.
   It would retire an individual verified-close reservation without performing
   the whole collection sweep; it needs explicit command semantics and the
   same native identity/no-force guarantees as `-d`/`-x`. `-L` already supplies
   one-window launch; the earlier proposed `-a` is *unnecessary*, not deferred.
2. **Concurrent interactive remote launches (historical Option D):** consider
   independently keyed pending VNC/RDP viewer registrations so human
   authentication can finish in an order different from recipe order. Any
   consolidation of RDP and TigerVNC viewer-readiness/placement must preserve
   each client's distinct role-identity and SSH/TLS/transport policies and
   avoid a speculative generic plugin framework. Keep version 1's accepted
   serial behavior unless a measured need warrants change.
3. **Managed live-layout reflow:** `-L` intentionally supports only `over`;
   panel/under live placement and rebalancing/reordering existing managed
   *and unmanaged* windows are deferred. Do not equate an initial configured
   `-o` layer with authority to rearrange windows later. A future explicit
   reset-to-intended-layout action requires separate user intent and rules for
   changed geometry/slots.
4. **Broader managed applications:** assess additional GUI/terminal clients
   individually, not from installed status alone. Reported on `gmki91` in
   November 2026: QTerminal 2.4.0; Krusader 2.9.0; FileZilla 3.70.6;
   Nautilus 49.6-r1; Nemo 6.6.4; KRDC 26.04.3; and `mc` 4.8.33 (reported
   without SFTP). Evaluate Remmina, KRDC and other RDP/VNC clients as
   independent peers, with real launch/window role/transport trust proofs.
   `mc` is text-mode and would run *inside* a managed terminal, not own a
   KWin window by itself. Versions are historical observations, not current
   platform requirements.
5. **Optional broader session status/reconnect:** distinguish one window
   across multiple remote/application sessions and fresh reconnects from the
   live KWin window. Never claim remote usability merely from local placement;
   no general transport telemetry framework is required for version 1.
6. **Performance refinement:** measure startup, D-Bus, launch/placement,
   polling, CPU/memory and human-visible latency; pursue bounded changes
   only on real measurements, preserving X11/Wayland safety and regression
   behavior. Version 2 optimization does not postpone version 1 correctness.
7. **Non-KWin backends:** possible separate evaluation of shared Bash
   planning for LXQt/GNOME, without promising KWin-specific identity/movement
   support or version 1 portability.

### Open Version 2 decisions (maintainer)

- Which live reflow operations, monitor/work-area/scaling policies, and
  clickable-exposure guarantees would actually provide value beyond the
  accepted one-shot layout?
- What new authorization and selection rules would allow reset-to-intended
  layout or per-window retirement without disturbing unrelated windows?
- Is out-of-order human authentication materially limiting current RDP/VNC
  usage, and what evidence justifies adding concurrency or common lifecycle
  abstractions?
- Which additional graphical applications are worth first-class managed
  launch support, and what exact positive identity and credential policy can
  each demonstrate on both KWin backends?
- Is non-KWin shell planning valuable enough to justify a separately scoped
  effort, or should version 2 stay focused on KWin?

Version 2 decisions should be taken from concrete usage and evidence,
not from previously explored but superseded design alternatives.
