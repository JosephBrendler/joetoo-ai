# joetoo-kwin user manual

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

This manual describes the current Version 1 source candidate, including Step 1.7
recovery and snapshot refinements. It is not permission to install, restart a
service or close a working session. Examples are operator instructions; native
examples were not executed to write this manual. Replace `.example` endpoints
with destinations you are authorized to contact. Never put passwords in recipes.

[Configuration reference](configuration-reference.md) · [Architecture](../ARCHITECTURE.md)
· [Step 1.7 results](../archive/task_step1.7/README.md) · [Broker source](../libexec/joetoo-kwind)

## Part A — Concepts, installation and ordinary CLI use

### Components and responsibilities

| Component | Responsibility |
| --- | --- |
| Bash CLI `joetoo-kwin` | Load trusted configuration, calculate geometry, show plans, confirm operations and report results. |
| Python broker `joetoo-kwind` | Session-bus transactions, managed registry, reservations, authentication, verified placement, close results and private runtime checkpoint. |
| KWin resident script | Observe the actual compositor windows and execute supported placement/one-shot stacking requests. An observation alone does not enroll a window. |
| Native KWin effect | Authenticated exact-UUID inspection and graceful-close boundary. X11/XWayland uses the fenced `WM_DELETE_WINDOW` helper, without a force-kill fallback. |
| User OpenRC service | Supervise the broker only. Stopping it must not terminate managed applications, SSH, RDP or VNC workers. |
| Application-specific launchers | Own their clients, identity evidence and remote-resource cleanup. RDP and VNC remain separate existing adapters. |

KWin UUID identifies a compositor window. `win-001` is a broker-managed alias;
`desktop,slot` is the original logical reservation. These are different from
request IDs, OS PIDs, readable captions, panel positions and remote sessions.
A managed record can outlive its window. A missing record still reserves its
slot until an explicitly confirmed `-x` retires it. Manual movement does not
reassign its intended slot or enroll an unmanaged window.

Native KWin Wayland, native KWin X11 and XWayland clients are distinguished.
An XWayland window inside a Wayland session does not make that session native
X11. SDL's actual backend evidence and existing native identity checks remain
mandatory; `DISPLAY` or `XDG_SESSION_TYPE` alone is not proof. OpenRC can inherit
`XDG_SESSION_TYPE=tty` in a legitimate graphical session.

### Installation and prerequisites

Use an ordinary graphical user's session bus, never root or a freshly invented
D-Bus session. The environment needs the project's Bash/joetoo header helpers,
Python/dbus-python/GLib, `qdbus6`, `jq`, and the application-specific prerequisites
for selected recipes. Remote commands also need their established SSH/KIO,
TigerVNC or SDL FreeRDP integration. Private recovery/close operations require
D-Bus ProcessFD support. Configuration must provide screen dimensions; the CLI
does not autodetect monitor layout or decoration offsets.

Official Gentoo packaging is separate work. The checked-in
[development installer](../tools/joetoo-kwind-install-poc) has `--install`,
`--update`, `--check` and `--preview-legacy-backups`; these are development
integration tools, not permission to overwrite a live deployment. Install/update
changes user-owned files and OpenRC configuration but does not start the service.
Check validates its explicit inventory, not every possible host prerequisite.
Use the reviewed deployment setup for the CLI and its colocated planner/helpers;
copying just the Bash executable is insufficient. No package should populate
users' HOME profiles automatically.

The native effect must match the running KWin/kwin-x11 SDK/ABI and be explicitly
loaded through supported KWin mechanisms. Follow the
[native component instructions](../native/managed-close/README.md); do not reuse
an incompatible plugin binary or substitute an unsafe close mechanism. The new
snapshot/history code does not require a native API expansion.

Read-only service check (after installation by the operator):

```bash
rc-service -U joetoo-kwind status
joetoo-kwin -h
# End of commands

```

Daemon `conf.d` configures service execution/resident/environment. It is separate
from application defaults and is not sourced into the CLI planner.

### Implemented command reference

Put verbosity/configuration options **before `-L` or `-m`**, whose positional
operands stop option parsing. Select exactly one action. `--help` is a standalone
compatibility help form; use `-h` with ordinary short-option parsing.

| Invocation | Effect and restrictions |
| --- | --- |
| `-c [-f FILE]` | Source/validate configuration and print the dry-run plan; no broker launch or network/client execution. Trusted Bash itself can have side effects. |
| `-o [-f FILE]` | Preflight the whole configured plan, confirm, then serially launch, register, place and finalize each desktop cohort. |
| `-L DESKTOP PROGRAM MODE TARGET [over]` | One new managed window; omitted layer is `over`; explicit `over` works. `panel` and `under` are rejected. TARGET must still be supplied, including `""` for Dolphin home. There is no SLOT or geometry operand. |
| `-l` | Read-only fixed-column managed inventory, including retained missing/uncertain records and full UUIDs. No executable plan is sourced. |
| `-s` | Read-only `RegistryStatus` snapshot: counts, synchronization, Busy/uncertainty and capabilities. No remote-session health claim or plan sourcing. |
| `-i MANAGED_ID` | Read-only `GetManaged` detail for exactly one canonical managed ID. Last-known observation is not current authenticated-window proof. UNKNOWN is distinct from broker unavailability. |
| `-d MANAGED_ID` | Confirm graceful close of one positively verified window; retain its record, placement history and original reservation. Takes a managed ID, not raw UUID. |
| `-x` | Confirm a fixed registered-set progressive sweep: retire positively absent records and verified graceful closes; retain failed/unresolved entries. This closes applications and releases verified reservations. |
| `-S [-f FILE]` | Save the complete eligible managed arrangement as a new private timestamped snapshot. Current config controls history depth; FILE does not select windows. No partial selection. |
| `-r` | Validate latest last-good snapshot, preflight, confirm and launch **new instances**. No historical selector or `-f` operand is supported for `-r`. |
| `-m ...` | Move the active window using the forms below. This does not enroll it or make it eligible for managed closure. |
| `-f FILE` | Select one per-run config for `-c`, `-o`, `-L`, `-d`, `-x`, `-S` or an `l/r` layout move. Does not change selected profile. Unsupported combinations fail. |
| `-v`, `-q` | Increase/decrease verbosity; may repeat/cluster (`-vc`, `-vv`). Existing joetoo header clamps apply. |
| `-h`, standalone `--help` | Print usage without a launch. |
| `move D X Y W H` | Compatibility spelling for the five-operand move; the current implementation routes it through the same move parser. |
| `test-launch CLASS D X Y W H -- PROGRAM [ARG ...]` | Development-only launch/placement probe. Not the production recipe interface; it does not establish an ordinary managed registration. It starts a process. |
| `test-multi-launch` | Development-only four-local-Konsole managed test. It opens windows; do not treat it as an innocuous status command. No operands. |

`-s` and `-i` use the existing read-only broker APIs; neither starts a
broker, sources a launch plan, selects a window or changes managed state.
`-a`, `-D` and other unimplemented options are not supported. There is no automatic
save before closing, durable arbitrary geometry recovery, continuous layout
repair or concurrent remote launch queue.

#### Movement forms

```text
joetoo-kwin [-f FILE] -m l|r
joetoo-kwin [-f FILE] -m DESKTOP l|r
joetoo-kwin -m DESKTOP
joetoo-kwin -m DESKTOP X Y
joetoo-kwin -m X Y WIDTH HEIGHT
joetoo-kwin -m DESKTOP X Y WIDTH HEIGHT
# End of commands

```

The one-, three- and four-numeric-operand forms preserve unspecified desktop,
position or size. `l/r` uses shared two-panel policy and needs configured screen
geometry; numeric forms do not load layout configuration. Desktop is a positive
available desktop number, up to 256; coordinates are bounded signed integers
(-32768..32768), explicit sizes 1..32768. Side-layout geometry has its existing
configured display bounds. The action targets the shortcut-captured active
window, so choose it deliberately. Never use this interface as a substitute
for authenticated managed close or arbitrary UUID adoption.

### Recipes, layers and slots

Configured recipes are indexed Bash array strings:

```bash
screen_width=1920
screen_height=1080
desktop_session_list=(
    '2|konsole|local|btop|panel'
    '2|dolphin|local||over'
)
# End of commands

```

The grammar is `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`. Omitted or blank configured
LAYER means **panel**. `-L` uses four/five separate shell arguments and defaults
to **over** instead. Quoting one entire pipe-delimited string is not `-L` syntax.

| Program/mode | TARGET |
| --- | --- |
| `konsole local` | Available executable basename on PATH, such as `btop`; no command arguments. Runs in the original interactive Bash and returns to its prompt. |
| `konsole ssh` | `[USER@]HOST`, including an SSH alias. No separate port syntax; the precheck uses TCP 22. Preserve the existing SSH configuration/wrapper behavior. |
| `dolphin local` | Optional local directory; empty means HOME, relative paths resolve from HOME. Must be readable/searchable. No URL scheme. |
| `dolphin sftp` | `sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH]`; absent path requests remote login directory. Percent-encode spaces/UTF-8. No embedded password/query/fragment. KIO owns authentication and listing. |
| `vncviewer ssh` | `ssh://[USER@]HOST[:SSH_PORT]/display/N` or `/port/P`; port is SSH transport, not local forwarding. The owned worker allocates loopback forwarding and identifies the desktop viewer, excluding authentication windows. |
| `sdl-freerdp rdp` | `rdp://USER@HOST[:PORT]`, default 3389; explicit username, validated DNS/IP/bracketed IPv6, no password/path/query/fragment/client switches. |

Offline validation recognizes some historical mode spellings, but the production
launcher executes only the six pairs above. Passing a historical planner grammar
check does not make an unsupported pair launchable.

`under`, `panel`, `over` are one-shot initial classifications, not permanent
always-on-top/bottom rules. `-o` plans groups of new windows and verifies
`under → panel → over` with recipe order within a layer. Four is the absolute
physical panel limit; the ordinary `dt_win_limit=4` implicit-entry budget is
separate from explicit layers and logical slots. `-L over` uses the graphical
region and raises only its new exact window once, without reflowing, recascading
or changing existing windows. A single `over` is not a fifth panel. Launching a group does not automatically
switch the current desktop; preferred focus is considered only when the target
desktop is displayed.

Logical slots reserve identity, not screen rectangles. `-o` derives per-desktop
slots in recipe order; `-L` asks the registry for a safe unused slot, including
retained missing reservations. Neither silently renumbers existing records.
Mutable state is rechecked and the broker reserves atomically. A new `-o`/`-r`
does not append to occupied slots merely because windows are visually elsewhere.

Each actual launch announcement is timestamped. Positive registration, placement,
initial stacking/focus and remote usability are separate results. Failed plans
can leave verified successes present; they are not rolled back automatically.
Known-clean owned pending failures may allow serial continuation with an overall
incomplete/nonzero outcome. Busy, source/owner loss or uncertain cleanup stops
unsafe continuation.

### Configuration and profiles

Precedence is built-ins, optional `/etc/joetoo-kwin/defaults.conf`, optional
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf`, selected per-run plan,
then supported CLI overrides. The normal plan is the XDG user
`joetoo-kwin.conf`, with `/etc/joetoo-kwin/joetoo-kwin.conf` fallback when absent.
`-f` selects another plan without suppressing defaults. Relative XDG config
values fall back to HOME. Existing unreadable/invalid layers fail, not disappear.

Files are **trusted executable Bash**, not a sandbox. Read them before `-c`.
Use [the short template](../joetoo-kwin-per-run-template.conf) and the
[complete variable reference](configuration-reference.md). The package resource
location is `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf` when installed
by reviewed packaging; the source checkout carries that file at its root.
No geometry autodetection is implied by the example screen dimensions.

An installed optional `eselect joetoo-kwin` module uses the user's
`joetoo-kwin/profiles/` directory and default-plan symlink. Switching needs no
root and never sources a profile. Choose an unused filename and edit it first:

```bash
cfg_base=${XDG_CONFIG_HOME:-$HOME/.config}
[[ $cfg_base == /* ]] || cfg_base=$HOME/.config
cfg=$cfg_base/joetoo-kwin
mkdir -p -- "$cfg/profiles"
cp -n -- /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf "$cfg/profiles/work.conf"
chmod 600 -- "$cfg/profiles/work.conf"
# Edit work.conf for this host, then inspect without launching:
joetoo-kwin -c -f "$cfg/profiles/work.conf"
eselect joetoo-kwin list
eselect joetoo-kwin set work.conf
eselect joetoo-kwin show
# End of commands

```

The list marks the selected valid profile with `*`; numeric selection also works.
A preexisting regular default configuration is not a named selection and is not
silently overwritten by `set`. Do not bypass ownership/containment/symlink checks.
Explicit `-f` does not change profile selection. A relative XDG value is ignored
by the application; set an absolute value before using the example shell `cfg`.

### Close, recover and restore: different operations

`-d` asks an application to close normally and retains the registration/slot.
Unsaved-work dialogs and refusal are respected; there is no automatic force kill.
`-x` confirms a fixed snapshot of registrations: already-missing records require
fresh authenticated absence, present records require exact graceful close and
verified disappearance. Each verified entry retires immediately; failures remain.
Uncertain helper/source ownership can block later native dispatch. Accepted bulk
work belongs to the broker and survives the invoking terminal, with bounded
`ManagedCloseStatus` history. It is not a durable transaction across broker restart.
A warning that this terminal will close appears only after positive terminal
identity correlation, never merely because Konsole is in the target list.

Broker restart is neither close nor restore. The private runtime JSON at
`$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json` is a same-KWin-session aid.
Recovered records begin uncertain. Fresh authenticated KWin inventory plus the
native original UUID/PID/class proof can restore live presence. Resident source
IDs may change on reload; they are ordering metadata, not credentials. A new
KWin process/session or unprovable identity must not adopt old UUIDs.

The checkpoint includes bounded **last-known** observations: identity fields,
desktop-file information, caption, membership and frame. They can lag trivial
geometry activity until an authoritative state change or clean broker shutdown.
Broker memory is authoritative while running; older checkpoints may omit optional
historical fields, and queries leave unknown fields absent. This is neither exact
frame restoration nor authorization to close. `-l` and `GetManaged` do not grant
ownership by displaying an ID.

### Timestamped last-good snapshots

`-S` requires the **complete** managed arrangement: present, successfully placed,
positively verified and described by validated original launch recipes/settings.
Legacy records without export metadata, missing/uncertain windows, incompatible
effective policies, incomplete placement or empty state refuse the save and
leave previous last-good/history intact. A correctly placed unreachable SSH
placeholder can be eligible; successful remote authentication is not required.

Each successful save creates a new private file, even if the recipe data is
identical. Files use `snapshot-YYYYMMDDTHHMMSS.NNNNNNNNNZ-RANDOM.conf` (UTC,
nanosecond field and collision-resistant random suffix). Naming advances past
existing history even if the clock goes backwards. `last-session.conf` is
atomically replaced with a **relative** symlink to the latest validated file.
Private files are 0600, directory 0700; the symlink itself commonly displays 0777.
Only one contained link to a regular private generated history file is allowed.
External/traversing/dangling targets or symlink chains are refused.

`snapshot_history_depth=10` is current CLI configuration, validated 1..1000.
A successful save prunes only recognized older history files, never the active
target. It does not prune after a failed save. `-S -f FILE` can choose operational
retention configuration, but still saves the complete broker arrangement using
its original per-launch settings, not recipes from FILE. History management does
not confer window authority. A busy concurrent save is refused without waiting.

A valid older regular `last-session.conf` is preserved in timestamped history
before migration to the symlink. The configured retention limit then applies;
**depth 1 deliberately keeps only the newest save**, including during migration.
The CLI reports migration. Invalid regular files are not silently discarded.
Protocol-1 snapshots remain readable; new protocol-2 canonical data stores common
settings once at plan level, with separate window recipes and original individual
policy. Incompatible launch policies are refused, not merged.

Last-good is `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf`
(absolute XDG state root, otherwise HOME fallback). Inspect your own private data;
do not publish unredacted endpoints/captions/configuration:

```bash
state_base=${XDG_STATE_HOME:-$HOME/.local/state}
[[ $state_base == /* ]] || state_base=$HOME/.local/state
state=$state_base/joetoo-kwin
joetoo-kwin -S
ls -l -- "$state/last-session.conf"
readlink -- "$state/last-session.conf"
stat -L -c '%a %U %n' -- "$state/last-session.conf"
find "$state" -maxdepth 1 -type f -name 'snapshot-*.conf' -printf '%f\n' | sort
sed -n '2s/^# data: //p' "$state/last-session.conf" | jq .
# End of commands

```

A post-publication directory-fsync or pruning problem is reported as a warning
about a **published** save, not a false rollback. Uncertain directory durability
prevents pruning; a pruning failure can leave extra older files. Inspect and
resolve the filesystem issue; do not manually build unsafe links. There is no
historical snapshot-selection CLI. `-r` uses the latest validated selection.

Snapshots preserve recipes, order and effective layout policy, **not geometry
sampled from current windows**, old PIDs/UUIDs, credentials or connection state.
Original explicit `desktop_session_frames` policy can be retained separately;
normal recipes are recalculated by the shared planner. A manual move/resize does
not become a saved rule; reassignment away from the intended desktop makes the
conservative export ineligible. `-r` validates a generated temporary copy and
rejects arbitrary added Bash. It then performs normal preflight, confirmation,
new identities, placement and initial layout. Current reservations still block it.
`-d` and `-x` never erase or advance last-good snapshots.

## Part B — Standalone KWinBridge D-Bus reference

### Addresses, introspection and safe queries

These are session-bus services for the current graphical user:

```bash
bus=org.joetoo.KWinBridge
path=/org/joetoo/KWinBridge
kbus=org.kde.KWin
kpath=/KWin
qdbus6 "$bus" "$path"
qdbus6 "$kbus"
qdbus6 "$kbus" "$kpath"
qdbus6 "$bus" "$path" "$bus.RegistryStatus" | jq .
qdbus6 "$bus" "$path" "$bus.ListManaged" | jq .
qdbus6 "$bus" "$path" "$bus.ListObserved" | jq .
qdbus6 "$bus" "$path" "$bus.GetManaged" win-004 | jq .
# End of commands

```

The project uses `/KWin` for KWin support information, `/Scripting` for script
management and `/VirtualDesktopManager` for desktop resources. Do not assume
`/org/kde/KWin` is an equivalent object on your version: list objects with
`qdbus6 "$kbus"` and inspect the actual interface. KWin's interface is not the
joetoo bridge interface. Listing an interface is not permission to invoke its
state-changing methods.

Each method argument is a **separate** shell argument after the method name.
`GetManaged` accepts a managed ID or canonical exact KWin UUID, not a wildcard
or an expression such as `GetManaged(win-004)` in the method-name string.
An unknown valid lookup returns `state=UNKNOWN`; it does not adopt anything.

```bash
qdbus6 "$bus" "$path" "$bus.GetManaged" 11111111-1111-4111-8111-111111111111 | jq .
# Substitute your own exact retained request ID for these safe status queries:
qdbus6 "$bus" "$path" "$bus.ManagedCloseStatus" REQUEST_ID | jq .
qdbus6 "$bus" "$path" "$bus.InitialLayoutStatus" REQUEST_ID | jq .
qdbus6 "$bus" "$path" "$bus.Status" REQUEST_ID
# End of commands

```

The UUID above is illustrative, not a request to operate on that window.
`ListManaged` returns `{count,windows}` summaries with ID, UUID, original
request/run, presence, placement, connection and intended desktop/slot.
`GetManaged` returns `{state:"FOUND",window:{...}}` plus last-known observation.
Older identity-only records omit unknown optional observation fields.
`ListObserved` returns observed windows, bounded events/changes and sync metadata;
these are not additional managed windows. `RegistryStatus` reports source/revision,
counts, capabilities, Busy/cleanup/placement state and recovery status.

### Method legend and protocol rules

In the tables, `s` is string, `i` signed 32-bit integer, `b` Boolean and `h` a Unix
FD. `∅` is the empty signature (no arguments or no return). A `s` result may be
JSON or the documented text/empty string; do not assume every string is JSON.
Argument names are in wire order; sender/async callback Python keywords are not
extra wire operands.

- **Q:** observational query, meaningful from a separate `qdbus6`. Some queries
  advance expiration/verification bookkeeping but do not submit window actions.
- **F:** frontend transaction. Use the CLI/owned launcher; do not reconstruct a
  production transaction from separate `qdbus6` processes.
- **R:** resident callback/claim. Not a standalone operator action.
- **D:** development diagnostic transaction. Can consume serialization/Busy state;
  not an enrollment or destructive authorization interface.

Legacy placement/correlation APIs do not all pin a D-Bus sender. Do not confuse
source/request/UUID checks with mandatory ProcessFD authentication. The SDL,
close, recovery and snapshot paths have their additional explicit checks below.
No method table is advice to forge inventory, callbacks or UUID claims. Source
contracts remain authoritative: [broker](../libexec/joetoo-kwind),
[resident](../joetoo-kwin-resident.js),
[SDL interface](../archive/task_step1.5/step1.5c5d-sdl-interface-contract.md),
[native close protocol](../native/managed-close/README.md).

### Complete exposed `org.joetoo.KWinBridge` method reference

The following table is checked against every broker D-Bus decorator. JSON-bearing
transaction payloads are further described immediately after the table.

| Method | Input → output signature | Kind | Inputs and results | Authentication/state; standalone use |
| --- | --- | --- | --- | --- |
| `PrepareManagedClose` | `s` → `s` | F | JSON protocol 1: scope one/all, managed_id (empty for all), settings; optional terminal hints. Returns fixed preview/targets/exclusions/request ID. | Same-user ProcessFD caller, synchronized source, native KWin owner/UUID proof, no competing work. Preview only; use CLI. [source](../libexec/joetoo-kwind#L175) |
| `CommitManagedClose` | `s` → `s` | F | Preview request_id. Returns accepted/terminal redacted close JSON. | Original live prepared caller unique name only, unexpired source/claim. Separate qdbus processes are not equivalent; use CLI confirmation. [source](../libexec/joetoo-kwind#L185) |
| `ManagedCloseStatus` | `s` → `s` | Q | Retained close request_id → per-target actions/states/retired flags, retention booleans and overall state; unknown/evicted is explicit. | Safe later-console query. No close authority; broker-lifetime bounded history. [source](../libexec/joetoo-kwind#L190) |
| `BeginSdlRegistration` | `s` → `s` | F | JSON protocol 1: desktop,slot,bounds; optional profile,intent. Returns request_id, marker/profile/bounds and registration status. | Original persistent owner is authenticated with ProcessFD/UID; arm before direct child. Caller/child/source/backend evidence mandatory; use worker. [source](../libexec/joetoo-kwind#L258) |
| `BindSdlRegistration` | `sih` → `s` | F | request_id,pid,log_fd: original owned child and private evidence FD → registration JSON. | Same original authenticated owner; direct-child/start/executable/environment/log-FD checks. Cannot replace with a pathname or PID-only call. [source](../libexec/joetoo-kwind#L403) |
| `PollSdlRegistration` | `s` → `s` | F | request_id → pending/registered/failed/timeout/cancelled registration JSON, exact UUID only when proved. | Same original owner. Query can finalize registration; new standalone qdbus sender is not authorized. [source](../libexec/joetoo-kwind#L446) |
| `CancelSdlRegistration` | `s` → `s` | F | request_id → terminal registration/cancellation JSON. | Same original owner; bounded pending cleanup. Not a general viewer-close operation. [source](../libexec/joetoo-kwind#L452) |
| `SubmitSdlPlacement` | `s` → `s` | F | Confirmed JSON for managed_id/action/source/revision/intended destination/frame and timeout → request/result JSON. | Authenticated operator; original registered owner/child/exact UUID/source/reservation and exclusive placement checks. Use CLI/placement tool, not raw UUID. [source](../libexec/joetoo-kwind#L1008) |
| `TakeSdlPlacement` | `s` → `s` | R | Resident source → owned exact-UUID placement claim JSON or empty. | Pinned authenticated KWin sender, matching source and pending transaction. Not standalone. [source](../libexec/joetoo-kwind#L1201) |
| `PollSdlPlacement` | `s` → `s` | F | request_id → pending or terminal placement JSON with registration and remote_session=unverified. | Original placement operator authorization; not a general read-only cross-caller status API. [source](../libexec/joetoo-kwind#L1232) |
| `CancelSdlPlacement` | `s` → `s` | F | request_id → failed/cancelled placement result. | Authorized placement owner only. Does not close or retire the registered viewer. [source](../libexec/joetoo-kwind#L1241) |
| `Submit` | `iiiii` → `s` | F | desktop,x,y,width,height → placement request ID. | Legacy active-window move arm; exclusive state/geometry/source/recovery gates. No general caller ProcessFD pin. Use -m. [source](../libexec/joetoo-kwind#L1317) |
| `SubmitMove` | `iiiiibbb` → `s` | F | desktop,x,y,width,height,preserve_desktop,preserve_position,preserve_size → request ID. | Optional active-window move; CLI supplies preserved-field flags and invokes matching shortcut. Not managed ownership or close authority. [source](../libexec/joetoo-kwind#L1322) |
| `TakeMove` | `ss` → `s` | R | source,window_uuid → optional move claim JSON or empty. | Pending compatible request/source and shortcut-captured exact window; legacy claim validation, not a standalone UUID move API. [source](../libexec/joetoo-kwind#L1347) |
| `Take` | `∅` → `s` | R | No arguments → generic pending move claim JSON or empty. | Resident/shortcut protocol, single pending request; not an observational query and not an operator selection interface. [source](../libexec/joetoo-kwind#L1410) |
| `SubmitLaunch` | `siiiii` → `s` | F | app_class,desktop,x,y,width,height → legacy launch placement ID. | Legacy development class-correlated placement arm, Busy/geometry guards; does not itself create a managed registration. Use test-launch only deliberately. [source](../libexec/joetoo-kwind#L1415) |
| `TakeLaunch` | `ss` → `s` | R | resource_class,desktop_file → compatible launch placement JSON or empty. | Resident-selected normal candidate, class/request/ownership checks; not enrollment by calling with a class. [source](../libexec/joetoo-kwind#L1420) |
| `Complete` | `sss` → `∅` | R | request_id,result,detail; result OK/ERROR/VERIFY; VERIFY detail is exact-window JSON → no return. | Active claimed transaction; SDL requires pinned KWin sender and rejects bare OK. Legacy paths use their state/UUID/source checks. Assignment attempt is not geometry success. [source](../libexec/joetoo-kwind#L1562) |
| `Status` | `s` → `s` | Q | placement request_id → plain UNKNOWN/PENDING/RUNNING/VERIFYING/OK/ERROR plus possible detail. | Safe query; advances common verification bookkeeping. Preserve text interpretation rather than jq-parsing blindly. [source](../libexec/joetoo-kwind#L1677) |
| `SubmitManagedLaunch` | `siiiiii` → `s` | F | app_class,desktop,slot,x,y,width,height → JSON placement_request_id and registration_request_id. | Atomic pending slot/correlation/placement gates; original legacy API without sender pin. Arm only as part of the owned launch flow. [source](../libexec/joetoo-kwind#L1688) |
| `SubmitManagedLaunchIntent` | `s` → `s` | F | JSON {intent,frame:[x,y,width,height]} → same two IDs as SubmitManagedLaunch. | Validated complete restore metadata plus original managed launch checks. Metadata never enrolls or selects a UUID; no additional destructive authority. [source](../libexec/joetoo-kwind#L1719) |
| `ExportManagedSnapshot` | `∅` → `s` | Q | No arguments → generated canonical Bash snapshot text; does not publish a file. | Same-user ProcessFD operator, complete live placed metadata, authenticated/native identity and stable source. Safe own-terminal inspection when eligible; treat returned targets as private. [source](../libexec/joetoo-kwind#L1740) |
| `SetManagedLaunchPid` | `si` → `∅` | F | registration request_id,pid → no return. | Existing active owned correlation intent and positive launched PID; legacy API is not ProcessFD-pinned. Cannot enroll a preexisting arbitrary window. [source](../libexec/joetoo-kwind#L1750) |
| `PollManagedLaunch` | `s` → `s` | F | registration request_id → pending/registered/failed/timeout/ambiguous or UNKNOWN JSON. | Existing correlation state; can finalize enrollment only from retained complete positive evidence. Not interchangeable with SDL polling. [source](../libexec/joetoo-kwind#L1760) |
| `SubmitInitialLayout` | `s` → `s` | F | JSON entries [{registration_request_id,layer}], optional focus_timeout_ms/focus_poll_interval_ms/single_raise → layout ID. | Placed live registered cohort, one desktop, synchronized source, Busy/UUID/frame checks. No caller-supplied raw UUID list; use common launcher. [source](../libexec/joetoo-kwind#L1780) |
| `TakeInitialLayout` | `s` → `s` | R | source → frozen initial-layout claim JSON or empty. | Current pending cohort/source. Resident only; source is an ordering gate, not a transferable credential. [source](../libexec/joetoo-kwind#L1853) |
| `CompleteInitialLayout` | `ss` → `∅` | R | request_id,payload JSON → no return. | Matching running source/cohort/order, geometry/stack/focus verification data and deadline; legacy callback not ProcessFD-pinned. Never forge completion. [source](../libexec/joetoo-kwind#L1866) |
| `InitialLayoutStatus` | `s` → `s` | Q | layout request_id → state (PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN) and retained result JSON. | Safe status query; no new layout submission. [source](../libexec/joetoo-kwind#L1939) |
| `SubmitManagedViewerLaunch` | `s` → `s` | F | JSON desktop,slot,x,y,width,height plus validated VNC bounds; optional intent → registration/placement IDs. | Arms viewer-role observation before spawning; resident capability, slot and serialization guards. Not equivalent to generic PID-only enrollment. [source](../libexec/joetoo-kwind#L1954) |
| `TakeManagedViewer` | `s` → `s` | R | source → pending native-XID-to-KWin-UUID viewer claim JSON or empty. | Existing owned VNC role evidence, synchronized source and claim state; not standalone. [source](../libexec/joetoo-kwind#L2047) |
| `CompleteManagedViewer` | `s` → `s` | R | Matching claim/result JSON including matches of native xid and uuid → registration result JSON or empty. | Exact active claim, PID/role/window/history checks; title/class alone insufficient. Use resident resolution only. [source](../libexec/joetoo-kwind#L2058) |
| `CancelManagedViewerLaunch` | `s` → `∅` | F | registration request_id → no return. | Existing viewer transaction; fail/expire observer and pending placement. Worker must separately prove owned process/tunnel cleanup; no standalone force-close meaning. [source](../libexec/joetoo-kwind#L2109) |
| `BeginCorrelation` | `ss` → `s` | D | expected_class,title_token → diagnostic request ID. | Prelaunch synchronized baseline and serialization guard. Creates Busy state; does not grant management or close authority. [source](../libexec/joetoo-kwind#L2119) |
| `SetCorrelationPid` | `si` → `∅` | D | diagnostic request_id,pid → no return. | Matching pending probe; launched PID is evidence, not adoption permission. [source](../libexec/joetoo-kwind#L2264) |
| `PollCorrelation` | `s` → `s` | D | diagnostic request_id → PENDING/MATCHED/TIMEOUT/AMBIGUOUS/UNKNOWN evidence JSON. | Diagnostic history/settle logic only. Does not register and is not an extra SDL registration delay. [source](../libexec/joetoo-kwind#L2329) |
| `ObserveWindow` | `s` → `∅` | R | JSON event,source,revision,window → no return. | Production recovery authenticates actual KWin sender/process; sequenced lifecycle facts only. Do not send synthetic events to a live broker. [source](../libexec/joetoo-kwind#L2465) |
| `SyncInventory` | `s` → `∅` | R | JSON source,revision,windows and supported protocol capability fields → no return. | Production authenticated KWin sender/full validated inventory; source reload allowed only inside same proved compositor. Never standalone inventory injection. [source](../libexec/joetoo-kwind#L2562) |
| `ListObserved` | `∅` → `s` | Q | No arguments → windows/events/changes/eviction and sync source/revision JSON. | Safe observational query. Contains captions and diagnostic facts; not managed authority or exhaustive durable history. [source](../libexec/joetoo-kwind#L2651) |
| `ListManaged` | `∅` → `s` | Q | No arguments → {count,windows:[summaries]}. | Safe read-only managed query; invalid checkpoint is an error, not false empty success. Missing reservations remain visible. [source](../libexec/joetoo-kwind#L2681) |
| `GetManaged` | `s` → `s` | Q | Managed ID or exact UUID → {state:FOUND,window:...} or {state:UNKNOWN}. | Safe lookup, including bounded last-known observation. No wildcard, command expression or adoption; unknown fields remain omitted. [source](../libexec/joetoo-kwind#L2692) |
| `RegistryStatus` | `∅` → `s` | Q | No arguments → registry/presence/request counts, observation/recovery state, capabilities, active transaction and cleanup flags. | Safe diagnostic state. ready does not prove every individual record present or a remote session authenticated. [source](../libexec/joetoo-kwind#L2713) |

### Structured transaction payloads and outcomes

These schemas describe implementation traffic, not copyable destructive calls.
Use the original frontend/resident to create the credentials, FD and claim context.
There is no public method that simply turns an arbitrary UUID into a managed ID.

- **Close:** `PrepareManagedClose` takes protocol `1`, `scope:"one"|"all"`,
  `managed_id:"win-NNN"|""`, `settings` (validated close bounds), and optionally
  `terminal:{service,session,window}` hints. Only the same original authenticated
  unique caller may commit `request_id` before expiration. Results have `state`,
  `reason`, targets/excluded, `registration_retained`, `reservations_retained` and
  optional positively proved `self_terminal`. Target action is `close` or
  `retire_missing`; verified results distinguish `closed`/`already_missing` and
  `retired:true`. Failed, unresolved, skipped and partial results are not success.
- **SDL registration:** Begin protocol `1` has `desktop`, `slot`, `bounds`,
  optional `profile` (`sdl-x11-a1c-v1` for native X11; ordinary Wayland has no
  X11 profile) and optional validated `intent`. The generated marker and private
  log FD belong to one original owner/child transaction. Bind's `h` must be the
  actual private evidence descriptor, not a filename. Owner loss before a
  completed handoff is not authorization to adopt another child/window.
- **SDL placement:** confirmed protocol `1` JSON includes `managed_id`, fresh
  `action_id`, `source`, `revision`, `desktop`, `slot`, `x`, `y`, `width`, `height`,
  `timeout_ms`. The broker verifies the registered request/owner/child and exact
  UUID. Polling reports `registration`, `placement`, `reason`, managed ID/UUID
  and `remote_session:"unverified"`. A late observation never revives failure.
- **Intent metadata:** `intent` has integer `desktop`, `slot`, string `program`,
  `mode`, `target`, explicit/defaulted `layer`, and allowlisted Bash-value-string
  `settings`; optional `frame_override` is original policy. The native identity
  proof is separate. In new snapshot protocol `2`, these shared settings move to
  the plan level and recipes omit their redundant copies.
- **Initial layout:** entries contain registration request IDs plus layers, not
  caller-chosen UUIDs. `single_raise:true` is restricted to one `over` entry and
  an advertised compatible resident. Timing fields have existing validated bounds.
  Resident results and broker observation must verify the frozen cohort/order;
  this is one-shot stacking/focus, not a permanent rule or another geometry engine.
- **VERIFY completion:** detail JSON includes the exact `window_uuid`, `before`,
  Boolean `tiled` and `fullscreen` evidence. Subsequent broker geometry/desktop
  verification is required. `Complete(VERIFY)` accepts an assignment attempt; it
  does not by itself prove the client honored the geometry.
- **VNC viewer role:** the worker provides the original owned viewer PID and
  local desktop-role XID evidence. Resident `matches` pairs `{xid,uuid}` must
  satisfy the existing claim/history checks. Its `PollManagedLaunch` protocol
  does not apply to SDL FreeRDP, which has its own owner-authenticated methods.

**Caller continuity matters.** Running one `qdbus6 ... PrepareManagedClose ...`
and later another `qdbus6 ... CommitManagedClose ...` normally creates two unique
D-Bus senders. Same UID, terminal, shell PID or copied request ID does not supply
the original ProcessFD-backed caller connection. Do not bypass this with guessed
names or credentials. The CLI's existing frontend keeps the one original
connection through preview/confirmation; accepted `-x` then continues in the
broker after caller loss. Read-only `ManagedCloseStatus` from another console is
supported. The same distinction applies to original SDL registration/placement
owners and descriptors.

### Native service and owner diagnostics

The native service/interface is `org.joetoo.KWinCloseNative`; object path is
`/org/joetoo/KWinCloseNative`. All four methods return application-authored JSON
strings. They accept only the watched, current broker unique sender, not any
ordinary same-user `qdbus6` process. Merely seeing the interface is not authority.

| Native method | Input → output signature | Purpose and restrictions |
| --- | --- | --- |
| `Inspect` | `s` → `s` | Exact UUID → present/missing/unsupported/denied; present includes UUID, PID, class, backend, XID and closeability. Authenticated broker read only, not standalone adoption proof. |
| `Terminal` | `i` → `s` | PID hint → identified UUID only if one eligible native window; otherwise unknown/denied. Additional authenticated Konsole session/ancestry evidence is required for a self-terminal warning. |
| `Close` | `ssisis` → `s` | token, UUID, PID, class, bounded grab_ms, absolute monotonic expiry-ms string. Resolves/rechecks exact live object and supported graceful path. Broker-only owned claim, never a standalone close shortcut. |
| `Status` | `s` → `s` | Original native token → state/token/UUID/gone/helper_reaped evidence, or denied. Only matching broker/token; a user-selected managed ID is not this token. |

Native Wayland uses the ordinary supported graceful request. X11/XWayland checks
`WM_DELETE_WINDOW` and uses a bounded exact-object/XID lifetime fence; unsupported
capability fails without KWin's kill fallback. Dispatch and disappearance are
separate facts. Applications can refuse or present dialogs. See the
[native protocol and safety limits](../native/managed-close/README.md).

Safe owner/introspection diagnostics:

```bash
qdbus6 org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner org.kde.KWin
qdbus6 org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner org.joetoo.KWinCloseNative
qdbus6 org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner org.joetoo.KWinBridge
qdbus6 org.joetoo.KWinCloseNative /org/joetoo/KWinCloseNative
# End of commands

```

The native and KWin names must resolve to the same unique owner in the supported
integration. Name equality is a prerequisite, **not ProcessFD/UID/PID/start-time
identity proof**. The broker supplies that proof internally and pins its native
calls to the unique owner. Do not print raw credentials, exchange FD numbers or
substitute PID-only checks. Name replacement, source gaps, native unavailability
or incompatible plugin ABI must fail closed.

## Part C — Worked examples and troubleshooting

### Local single windows and desktop groups

The next commands launch windows and request confirmation. They do not rearrange
existing windows. Choose an intended desktop and inspect reservations first:

```bash
joetoo-kwin -l
joetoo-kwin -L 2 konsole local btop
joetoo-kwin -L 2 dolphin local "" over
# End of commands

```

For a configured group, save a trusted profile with explicit display dimensions:

```bash
screen_width=1920
screen_height=1080
desktop_session_list=(
    '3|dolphin|local||under'
    '3|konsole|local|btop|panel'
    '3|konsole|ssh|user@host.example|panel'
    '3|dolphin|local|Documents|over'
)
# End of commands

```

Then use `joetoo-kwin -c -f FILE` before `joetoo-kwin -o -f FILE`. Existing
reservations can block the plan; use a free desktop/slot arrangement, not a broker
restart as a conflict workaround. An unreachable SSH destination can still leave
a correctly managed local Bash placeholder with a manual retry instruction.
This is local window success, not a claimed SSH connection.

### SFTP and remote viewers

These are **recipe examples**, not proven reachable hosts or authorization to
contact them. Put the selected recipes in a trusted `desktop_session_list` with
appropriate screen settings. Do not launch all examples blindly into reserved
slots. Replace addresses only after checking your own trust/authentication setup.

```bash
desktop_session_list=(
    '4|dolphin|sftp|sftp://user@files.example:22/home/user/|panel'
    '4|sdl-freerdp|rdp|rdp://user@rdp.example:3389|over'
    '5|vncviewer|ssh|ssh://user@vnc.example:22/display/1|panel'
    '5|sdl-freerdp|rdp|rdp://user@rdp.example:3389|under'
    '6|vncviewer|ssh|ssh://user@vnc.example/port/5902|over'
    '6|sdl-freerdp|rdp|rdp://user@rdp.example|panel'
)
# End of commands

```

Panel uses shared panel geometry; larger `under`/`over` uses the graphical region
and configured cascade. A VNC `under` recipe uses the same supported layer syntax.
A single remote viewer uses separate arguments, for example
`joetoo-kwin -L 4 sdl-freerdp rdp rdp://user@rdp.example:3389 over`; only `over`
is supported by `-L`, regardless of recipe type.

RDP defaults remain `rdp_security_protocol=nla` → exclusive `/sec:nla`, and
`rdp_certificate_policy=strict` → `/cert:deny`. `negotiate` omits `/sec:`; it is
not `/sec:rdp`. `prompt` omits `/cert:` and is a user-chosen less restrictive trust
handling mode. NLA still uses TLS; TLS-version/cipher tuning is separate. No raw
switch/password field, automatic trust exception or credential injection exists.
`auto`/`software` X11 renderer policy does not prove authentication or usability.

SFTP uses KIO and its host-key/authentication handling; inspect the actual listing.
VNC owns its loopback-only tunnel/viewer and readiness lifecycle. SDL owns its
private log/child/backend evidence. Human authentication can occur before a
persistent desktop viewer exists; viewer-readiness defaults are finite five
minutes, distinct from mechanical placement. Local registration/placement can
succeed while a viewer is black or GDM has not rendered. Never add a GDM delay
or treat a positioned window as proof of remote TLS/NLA/login success.

### Missing records, restart and fresh restoration

Inspect without closing anything:

```bash
joetoo-kwin -l
qdbus6 "$bus" "$path" "$bus.GetManaged" win-004 | jq .
qdbus6 "$bus" "$path" "$bus.RegistryStatus" | jq .
# End of commands

```

A missing record keeps its reservation after `-d` or titlebar closure. Its
observation is historical. `GetManaged` may omit optional fields from an older
checkpoint; absent geometry/caption is unknown, not a zero rectangle/empty title.
An empty healthy registry prints `No managed windows (no retained managed
reservations).` An unavailable/malformed broker/checkpoint is not empty success.

A broker-only restart is an operator service action. With the reviewed service
installed and the same KWin session still running, this sequence tests recovery
without asking applications to close:

```bash
joetoo-kwin -l
rc-service -U joetoo-kwind restart
qdbus6 "$bus" "$path" "$bus.RegistryStatus" | jq .
joetoo-kwin -l
# End of commands

```

Wait for actual readiness/evidence, not an arbitrary delay. Compare original IDs,
UUIDs, reservations and per-record presence. `recovery=ready` means reconciliation
has finished, not that every record was proved live. KWin restart/logout/reboot is
a different boundary; the runtime file is not permission to adopt new windows.
Transient SDL worker placement authorizations and close claims are not replayed.

If `-r` refuses retained-slot conflicts, that is correct. It must not take over
old windows. For a **disposable confirmed arrangement only**, the following
closes/retire all eligible managed windows, then lets you inspect before restore:

```bash
joetoo-kwin -l
joetoo-kwin -x
joetoo-kwin -l
# Stop on any partial/unresolved result. Only when intended reservations are clear:
joetoo-kwin -r
# End of commands

```

`-x` can close this terminal if it is a proved managed target; accepted work
continues in the broker. Prefer an unmanaged console to watch results. It does
not close unrelated unmanaged windows or erase snapshot history. A successful
restore creates new windows/UUIDs/managed identities and connections, using the
latest validated recipes. Declining confirmation launches nothing. Repeated `-r`
against occupied restored slots is a new conflict, not an idempotent adoption.

### Troubleshooting guide

| Symptom | Interpretation and next check |
| --- | --- |
| Broker unavailable/introspection fails | Check session-bus environment and user service status; use the same graphical user. Do not start a separate D-Bus daemon or switch to root. |
| Recovery waiting/uncertain/invalid checkpoint | Inspect RegistryStatus, source/owner and native-effect availability. Preserve the private file for review; do not delete it to manufacture free slots. A different KWin/bus session is not same-session recovery. |
| Busy or cleanup uncertain | An active/unresolved owned transaction is not permission to submit another. Inspect retained request status; do not restart merely to bypass guards. |
| Slot reserved, window missing | Logical history persists. `-d` retains it; only eligible confirmed `-x` retires it in this version. |
| `-S` refused | Check all managed entries, placement, exact native identity, intended desktop and complete export metadata. Different effective policies are not silently merged. Old last-good/history stays intact. |
| Snapshot unsafe path/permissions or concurrent save | Resolve ownership/private-mode/link issue, or let the active writer finish. Do not chmod globally or point latest outside its private directory. |
| Snapshot published with warning | Read the specific durability/pruning warning. Publication already happened; no false rollback is promised. Extra old files may remain. |
| Placement failed/late change | Assignment is distinct from verified application. Inspect terminal outcome/actual geometry; late observations cannot turn failure into success. No automated retry/resize loop. |
| SDL NLA logon rejection | `ERRCONNECT_LOGON_FAILURE 0x00020014` reports remote logon rejection, not definitive proof of an incorrect password. Other failures remain generic; inspect only your current mission's private log safely. |
| Viewer registered/placed but black | Local identity/placement says nothing about GDM rendering, login or usability. No readiness inference from pixels or waiting heuristic. |
| SSH destination unavailable | A healthy managed placeholder terminal can still be successful; use its original Bash/manual retry. Normal Konsole/PTY closure handles the local foreground SSH lifecycle; persistent remote tmux is separate. |
| `-L panel`/`under` rejected | Intentional over-only single-launch contract. Use a configured `-o` recipe for panel/under; it still does not reflow existing windows. |
| Unexpected remote cert/host-key prompt | Stop and verify independently; do not weaken trust policy to pass a window-management test or submit credentials to an unverified endpoint. |

Private evidence may include captions, account names, endpoints and paths. Redact
before sharing; never publish credentials, ProcessFD data, private tokens or raw
client logs. For authoritative implementation details use the linked source and
configuration reference; historical acceptance records are evidence, not extra
operator commands or permissions.
