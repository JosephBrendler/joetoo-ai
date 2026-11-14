# joetoo-kwin — architecture and version 1 requirements

This is the project-specific design record for `joetoo-ai/workspace/projects/joetoo-kwin/`.
It distinguishes accepted requirements, implemented and accepted contracts, proposed
future capabilities, and open design questions. The [project README](README.md)
records current implementation status. The [active Step 1.5c.5 handoff](task_step1.5/HANDOFF.md)
records current task permissions, while [Step 1.5c.4 native closure](task_step1.5/step1.5c4-native-acceptance.md)
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

**(rdp is Increment 4 proposed)**

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
| `sdl-freerdp\|rdp` **(Increment 4 proposed)** | `rdp://USER@HOST[:PORT]` | Explicit username required; omitted port means RDP TCP 3389. No password, query, fragment, path or arbitrary client switches. This pair is **not yet implemented** in configured `-o`. |

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
| `-L DESKTOP PROGRAM MODE TARGET [LAYER]` | Confirm then launch one managed window above existing windows; `over` is the only implemented layer (also the default), no live-desktop reflow |
| `-m l|r` | Two-panel active-window geometry on current desktop |
| `-m DESKTOP` | Change active window's desktop, preserve geometry |
| `-m DESKTOP l|r` | Two-panel placement on specified desktop |
| `-m DESKTOP X Y` | Change desktop/position and preserve size |
| `-m X Y WIDTH HEIGHT` | Change position/size and preserve desktop |
| `-m DESKTOP X Y WIDTH HEIGHT` | Specify desktop, position and size |
| `-x` | Gracefully close all positively managed windows, not unrelated ones (future 1.6) |
| `-a` | Add one managed window (future; syntax TBD) |
| `-d MANAGED_ID` | Close one safely validated managed window (future 1.6) |
| `-l` | List broker-managed windows read-only, one record per fixed-width table row, including stable managed ID, desktop/slot, presence, placement and UUID (Step 1.5d) |
| `-i MANAGED_ID`, `-s` | Additional detail/application-status interfaces, not implemented in Step 1.5d |
| `-S` | Export reusable layout (future 1.8) |
| `-r` | Restore a saved last-good layout using new instances (future 1.8) |
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

The formerly proposed live-desktop reflow and broker/resident transaction
extension remain historical design research, **not** Step 1.5d requirements.
See the source review under `task_step1.5/` for that earlier investigation.

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
| **1.5c.5a** | Dolphin SFTP integration | Accepted and closed; managed X11/Wayland launches and remote browsing demonstrated; optional post-confirmation NSS/TCP advisories remain non-enforcing diagnostics |
| **1.5c.5b** | TigerVNC viewer over authenticated SSH | Accepted and retained as a peer-level managed graphical remote-access option; native X11 and Wayland/XWayland identity, placement, SSH tunnel and teardown demonstrated |
| **1.5c.5c** | Comparative RDP feasibility and decision | **Closed:** affirmative feasibility accepted; SDL3 FreeRDP selected for first RDP implementation, not as a preferred/default client |
| **1.5c.5d** | Managed SDL FreeRDP under configured `-o` | **ACCEPTED, CLOSED AND MERGED (2026-11-11, PR #29)**: exact UUID/placement/lifecycle on native X11/Wayland, layered configuration, bounded clean-failure continuation, strict `/sec:nla /cert:deny` defaults, successful trusted GDM connection and automatic invalid-certificate refusal with verified cleanup; see final Increment 5 evidence |
| **1.5d** | Implement `-L` one-recipe single-window launch (`over` only; no reflow), retain read-only `-l` inventory; run integrated native X11/Wayland regression | **ACCEPTED, CLOSED AND MERGED (2026-11-12, PR #30)**: `-l` implemented; `-L` implemented under simplified scope, preserving field-specific validation, safe logical-slot reservation, exact-UUID placement, one-shot raise, existing-window geometry and accepted `-o` semantics |
| **1.6** | Managed `-a`, `-d`, `-x` | **Now active** Selective safe close, never unrelated windows |
| **1.7** | Runtime JSON checkpoint and same-session reconciliation | Broker restart and exact source/UUID reconciliation |
| **1.8** | Restorable `.conf` snapshot, `-S`, `-r` | New-window recovery from validated last-good intent |
| **1.9** | `eselect`, installation/ebuild and complete integration | Maintainer-led joetoo/joetoo-upstream packaging, template guidance and version 1 lifecycle |

### 1.5c.5 — Remote resource and desktop integration (incrementally authorized)

**Common contract:** Each approved new `program|mode|target` combination
must define exact parsing, local process invocation, authentication and
security assumptions, positive unique KWin UUID identity, desktop/slot
placement, layer behavior, transport/session lifecycle, bounded cancellation,
and truthful partial success. Reuse existing CLI/planner/broker/resident
interfaces wherever possible. Do not introduce a generic remote-access
framework or unnecessary broker expansion. Unsupported recipes reject before
confirmation and before process or network side effects.

**1.5c.5a — Dolphin SFTP (first).** The maintainer approved the URL-only
`sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH]` target contract, safe
percent-encoding/redacted diagnostics, native KIO/libssh host trust and
independent remote-outcome reporting. The task-branch implementation launches
local `dolphin --new-window -- URL` using existing positive PID/UUID ownership,
desktop/slot placement and initial layers. Maintainer X11 and Wayland native
runs demonstrated successful managed placement and remote file browsing on the
specified reachable destination. Those observations do not mean that the
launcher verified SFTP authentication or listing, or that untested host-key
prompts and active-desktop focus have been accepted. A remote navigation or
authentication failure is not a KWin placement failure. Do not execute remote
Dolphin or treat KIO file transfer as SSH GUI forwarding.

**Post-confirmation SFTP reachability advisories (follow-up correction).**
The maintainer requires two separately observed, bounded checks: **(1) local
name resolution** and **(2) a TCP connection attempt to the intended SSH
transport endpoint/port**, where the effective destination can be determined
reliably. They are diagnostics, not SFTP authentication or session verification.
They must not run during `-c`, URI validation, offline capability preflight or
before `-o` confirmation. Use configurable bounded timeouts and preserve
separate `succeeded`, `failed`, and `not attempted/inconclusive` outcomes for
each check. Numeric IP addresses need no DNS lookup. SSH aliases, libssh
configuration, proxies and nonstandard ports can make direct NSS/TCP results
incomplete or misleading: do not equate a DNS failure with TCP unreachability,
or a TCP success with a working authenticated SFTP session. A check that cannot
be performed must be reported as such, not silently converted to failure.
Any negative or indeterminate advisory result must leave the accepted launch
policy unchanged: **launch the local Dolphin window with the validated SFTP URL
anyway**, permit KIO to present its own error/retry UI, and report the window's
actual registration/placement separately. No automatic fallback to a local
path or new network-management framework is authorized by these advisories.

**KIO/OpenRC compatibility observation.** The maintainer observed
`kf.kio.gui: Failed to determine systemd version, falling back to extremely legacy forking mode.`
During KDE KIO's application-process launch selection, inability to obtain a
systemd-manager version causes a fallback to its normal forking launcher (see
[KIO process-runner source](https://github.com/KDE/kio/blob/4ef7a0aed32da3c5a365f2d07d637a8d821a678a/src/gui/systemd/systemdprocessrunner.cpp)).
On the tested OpenRC session, this was nonfatal and did not prevent managed
window registration or remote browsing. It is not evidence of a failed SSH/SFTP
connection. No suppression, process-launch redesign or systemd dependency is
authorized as part of Step 1.5c.5a.

**1.5c.5b — TigerVNC over SSH (second).** The implemented recipe
`DESKTOP|vncviewer|ssh|ssh://[USER@]HOST[:SSH_PORT]/display/N[|LAYER]`
(or `/port/P`) validates its endpoint offline and launches a dedicated,
owned SSH forwarding process with a loopback-only local VNC listener. SSH
host-key checks remain in force; raw/direct VNC is not supported, including
on a local LAN. TigerVNC's own `-via` tunnel is disabled so its process and
forwarding lifecycle do not compete with the owned SSH tunnel.

The actual desktop viewer is identified only after the stock TigerVNC
desktop-role signal and correlated with the exact KWin X11/XWayland window
UUID, process, source and launch transaction. The preceding authentication
window is never adopted merely because it shares PID or class. The broker
places the positively identified viewer, verifies geometry and registration,
and preserves independent launch, transport, authentication, remote-usability
and window-placement outcomes. Startup, failure, cancellation and teardown
use bounded checks and owned-process cleanup rather than class-wide killing.

The maintainer natively demonstrated correct viewer registration/placement,
stacking and usable remote desktop on `gmki91` X11 and `q552u01` Wayland,
and confirmed viewer and dedicated SSH process teardown after normal close.
These observations do not imply that the program independently verifies VNC
authentication or remote usability, nor that all failure or host-key paths
have been tested. The accepted TigerVNC-over-SSH implementation remains a
fully supported peer of subsequent managed remote-desktop clients.

**1.5c.5c — RDP feasibility and decision (third; closed).** The maintainer
accepted an affirmative RDP feasibility determination following comparison
of KRDC, Remmina and relevant FreeRDP graphical clients and native X11 and
Wayland SDL FreeRDP investigations. Native-Wayland evidence includes a marked
viewer distinct from the credential dialog, cancellation, failed NLA,
connection refusal and coexistence with an unrelated viewer. X11 evidence
shows successive marker-bearing temporary and persistent windows, requiring
a separate positive role discriminator. These are observation results, not
production registration, placement or certificate-trust acceptance. Fresh-client
connection does not establish in-process reconnect or remote-session identity.
See the [Step 1.5 HANDOFF](task_step1.5/HANDOFF.md) for evidence and limitations.

**Peer-capability policy.** Managed TigerVNC-over-SSH, SDL FreeRDP
(the first RDP client), and any later authorized RDP clients are independent,
user-selectable peers. Implementation order confers no preference or default.
RDP is the capability; SDL FreeRDP is one client implementation, and Remmina
may be evaluated separately. Each client retains its own invocation,
transport/security and positive viewer-role identification contract. Once a
viewer is positively registered, its exact KWin UUID, reserved desktop/slot,
placement, geometry verification, and eventual stacking/focus belong to
shared managed-window infrastructure. Do not impose SDL-specific identity
assumptions on VNC or other RDP clients or introduce a speculative plugin
framework. Preserve the accepted TigerVNC behavior.

**1.5c completed milestone — accepted baseline (2026-11-11).** Steps
1.5c.1–1.5c.5d are complete and maintainer-accepted. The final SDL FreeRDP
increment added serial configured managed RDP for X11 and Wayland, verified
exact-UUID placement/stacking, five-minute readiness and known-clean failure
continuation, system/user/per-run configuration layering, optional non-root
user-owned `eselect` profiles, configuration reference, and two validated
security-policy settings. Built-in `rdp_security_protocol=nla` maps to
`/sec:nla` (the alternate `negotiate` omits `/sec:`), and
`rdp_certificate_policy=strict` maps to `/cert:deny` (the alternate
`prompt` omits `/cert:`). Native `gmki91` verified the strict trusted-name
connection and automatic certificate-name mismatch refusal, including
verified terminal broker/child cleanup; native `q552u01` Wayland RDP
interoperability and managed placement were accepted earlier. Final source
landed in `main` via [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29)
(merge `3e9c4bf311bc65b32d332a00d3b50163a9043303`). See
[final Increment 5 evidence](task_step1.5/step1.5c5d-increment5-final-native-acceptance-2026-11-11.md)
and [current task HANDOFF](task_step1.5/HANDOFF.md).

**Historical design material below:** The earlier Wayland-placement diagnostic,
Option C proposal and historical gate sequence document decisions *before*
completion; statements there that placement/security/configured launch remain
unimplemented are superseded by this accepted milestone. Option D's
multi-pending-client proposal remains deliberately deferred. Do not interpret
historical work-in-progress language as reopening accepted Step 1.5c.

**1.5c.5d — Managed RDP implementation (phased).** SDL FreeRDP is the first
RDP client. Its native-Wayland and native-X11 registration selectors are
implemented and have separate native acceptance evidence; they distinguish
credential/authentication windows from the persistent viewer and establish
positive launch/PID/lifecycle/marker/exact-UUID ownership. Controlled placement
was demonstrated on X11; Wayland placement, timing and exact frame sizing
remain open. Registration-only tooling must not move a window or claim a
remote login, remote usability or validated server identity.

**Immediate diagnostic gate.** On native Wayland a registered viewer remained
present, and the placement request reported an identity/source/owner/expiry
failure after about 15 seconds. The maintainer subsequently observed window
movement after that terminal failure. Whether the resident claimed the request,
when assignment occurred, and why geometry did not converge are not yet
established. First capture bounded, sanitized claim/completion/guard/deadline
transitions and pre-request plus post-terminal geometry observations. Do not
infer a specific cause or simply lengthen timeouts; late effects after a
terminal result require explicit characterization.

**Option C — current serial-consolidation objective (after diagnosis).** Keep
the proven RDP viewer selectors and per-launch reservation/identity evidence.
Use one authoritative, bounded managed placement transaction for a positively
identified exact UUID; consolidate overlapping SDL-specific guard evaluations,
placement deadlines and terminal finalization without weakening genuine
ownership/source/process-loss protections. For confirmed configured `-o`
launches, reservation expresses the operator's placement intent: the correct
viewer is placed when it becomes identifiable, without a second manual
confirmation. The standalone registration-only POC and its separately
confirmed placement test remain distinct development contracts. Preserve
client-specific RDP transport/security handling and independent remote-session
outcomes. This phase processes one unresolved interactive launch at a time;
that serial policy must not be confused with an identity requirement that
human authentication complete in launch order. The later accepted Increment 4
policy uses finite, independently configurable **five-minute (300000 ms)**
defaults for RDP viewer registration and TigerVNC viewer readiness. These
limits bound identification of a persistent viewer, not a verified password-
entry state. At timeout, cancel the pending registration, terminate only owned
pre-registration resources, and continue serially after verified terminal
cleanup; Busy, unresolved ownership or an active transaction still blocks
subsequent launches. Mechanical identity, placement, and cleanup remain
separately bounded and fail closed. TigerVNC was unchanged by Option C;
Increment 4 may align its viewer-readiness default without a general VNC
refactor. See [authoritative Increment 4 decisions](task_step1.5/step1.5c5d_Increment_4_decisions.md).

**Option D — later, separately authorized lifecycle objective.** Extend broker
bookkeeping to support multiple independently keyed pending remote launches,
so human NLA/VNC authentication can finish out of reservation order while
each final viewer still maps to its originating recipe and exact UUID. Unify
RDP and TigerVNC viewer-readiness and placement lifecycle management while
retaining their different positive role selectors and transport policies.
Analyze any future Remmina selector independently; a shared PID or caption
alone is not sufficient ownership. Option D, VNC migration and concurrent
launch orchestration are not authorized by Option C or by this architecture
update. Maintain the working serial VNC path until separate validation.

**Gates:** (1) diagnostic-only late-placement trace; (2) separately reviewed
Option C implementation and native X11/Wayland acceptance; (3) later Option D
concurrency and RDP/VNC lifecycle design/authorization. Documentation here
expresses requirements and roadmap, not permission for code, deployment,
publication or native testing.

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

**Historical pre-production security rationale (superseded by accepted Increment 5):** The affirmative feasibility result did not
establish production TLS certificate trust, server identity or secure
negotiation policy. Validate those for each client/endpoint; do not infer
them from `tls`, NLA or successful remote use, and do not weaken certificate
checks to obtain a passing demonstration. Preserve TigerVNC's independently
approved SSH tunnel/host-key protections. Increment 5 subsequently implemented
and natively verified strict NLA/certificate-refusal defaults, as recorded above.
Step 1.5c.5d is accepted and merged; Step 1.5d integrated X11/Wayland
regression remains subsequent work. This architecture grants no source,
native-execution or publication authority.

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
- How should each managed RDP client establish production certificate trust,
  exact window-role identity and authorized placement release on each KWin
  backend, without claiming remote desktop readiness from local window state?
- Should joetoo's Bash planner be evaluated for non-KWin environments such as
  LXQt/GNOME in a separately authorized later effort? This is not a version 1
  portability commitment.


