# joetoo-kwin CLI configuration reference

<!-- Copyright 2025-2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

This is documentation, not a sourced defaults file. It describes the current
implementation, including layered CLI defaults and the optional user-owned
config selector. Accepted Increment 4 Stage 3 behavior is unchanged. The short
`joetoo-kwin-per-run-template.conf` at the project root is the copyable starting
point. In an installed package, use the resource path in the packaging section.

## Current loading and use

`joetoo-kwin -c -f FILE` validates and calculates a plan without launching it.
`joetoo-kwin -o -f FILE` additionally performs runtime preflight, requests
confirmation, and runs the serial plan. `joetoo-kwin -f FILE -m l` (or `-m r`) consumes the shared
geometry policy; put `-f` and other options before `-m`. Numeric move forms
and read-only/help operations retain their existing policy without loading
plan/default layers. Configuration is **trusted
executable Bash**, not sandboxed key/value data; even `-c` executes the selected
file. Read it before use.

The implemented precedence, lowest to highest, is:

1. Built-in `plan_defaults()`.
2. Optional `/etc/joetoo-kwin/defaults.conf`.
3. Optional `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf`.
4. One selected per-run plan: explicit `-f FILE`, otherwise
   `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf`, with `/etc/joetoo-kwin/joetoo-kwin.conf`
   as fallback only when the user plan is absent.
5. Supported explicit CLI overrides (`-v`/`-q` verbosity adjustments).

System and user defaults are **sparse overrides**, not copies of the reference.
Every exposed setting can still be overridden in the selected per-run plan.
`-f` selects a different highest-precedence plan; it does **not** suppress the
preceding defaults. Relative `-f` paths are anchored to the invocation directory,
not searched through `PATH`. A relative `XDG_CONFIG_HOME` uses `$HOME/.config` for both
user defaults and the normal user plan, preserving existing path behavior.

Missing optional defaults are allowed. Present unreadable/non-file/dangling
layers, inaccessible configuration directories, Bash syntax errors and nonzero
source results fail rather than silently falling back. All selected files are
syntax/readability checked before any is sourced. Final **effective values**
are then validated through existing validators; an explicit later assignment
can replace an earlier value, which is an override, not fallback. Bash remains
trusted executable code, so syntax checking does not sandbox it or prevent
side effects. Use plain assignments/arrays, and do not redefine internal helpers
or configuration-selection variables.

OpenRC `joetoo-kwind` conf.d is separate service configuration. Its executable,
resident and environment settings are **not** CLI plan inputs. Exact UUID
ownership, fail-closed cleanup and other safety invariants are not configurable
toggles. Derived slots, managed IDs, UUIDs and internal transaction constants
are not plan settings.

Config selection is optional: a regular existing user plan remains valid,
and explicit `-f` works independently of the selected config. The selector
never changes system defaults or daemon configuration.

## Recovery and last-good snapshot controls

See the [user manual](joetoo-kwin_user_manual.md) for complete CLI/D-Bus use.
`-S` saves the complete authenticated managed arrangement, not recipes selected
from the current file. It loads the existing optional defaults/default-plan layers
(or `-f FILE`) for **current operational history retention**. Original per-launch
recipe/settings remain authoritative for export; different effective launch
policies are refused, not merged. `-r` validates latest last-good and calls the
ordinary confirmed new-instance launch flow; it has no historical-selection flag.

| Setting | Built-in default | Units/bounds | Meaning |
| --- | --- | --- | --- |
| `snapshot_history_depth` | `10` | integer count, 1..1000 | Current `-S` retention; info severity. Not per-window launch metadata or close authority. Failed saves never prune. |
| `snapshot_validation_timeout_ms` | `30000` | milliseconds, 100..120000 | Offline generated-snapshot `-c` validation only; debug severity. Separate from viewer/human waits. |
| `desktop_session_frames` | `()` | optional indexed array, same count as recipes | Original explicit frame policy, each `"X|Y|WIDTH|HEIGHT"` or `""`. Integers must fit the configured display, width/height positive. Normal calculations remain unchanged when empty. `-L` uses normal graphical policy. |

Each successful `-S` creates a private UTC/nanosecond/random timestamped file
under `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/` and atomically updates
`last-session.conf` as a contained relative symlink. Old regular last-good files
migrate safely into history; depth 1 explicitly retains only the newest save.
Protocol-1 snapshots remain readable; new protocol 2 stores common settings once.
Manual frame changes are never sampled into launch recipes. Only original explicit
frame overrides can be saved. Runtime checkpoint observations are historical,
private and separate from durable launch intent and current authenticated proof.

## Reading the tables

Defaults below are the values assigned before sourcing the plan. Ranges are
inclusive; coupled constraints also apply. Use canonical decimal integers, not
Bash arithmetic expressions, for numeric settings. Units are pixels, percent,
counts or milliseconds as stated. Endpoint ports belong to recipes, not global
settings. RDP/VNC settings are validated when the plan contains their recipes;
move-only operation validates geometry rather than all launch settings.

Code fences explicitly labelled **Bash** are executable snippets; they are not
automatically loaded by reading this reference. A leading `#` marks a comment;
a commented assignment in the short template has no effect. The header already
supplies pseudo-booleans: `$TRUE` is the nonempty string `0`, `$FALSE` is empty.
Use those values for the two Boolean settings, not literal `true`/`false`.

## Plan and layout

| Name | Built-in default | Validation / meaning |
| --- | --- | --- |
| `screen_width` | empty; required | 1..32768 pixels; intended display width, not autodetected |
| `screen_height` | empty; required | 1..32768 pixels; intended display height |
| `desktop_session_list` | empty array; required for `-c`/`-o` | Nonempty indexed Bash array of recipes; at most 256 entries per desktop |
| `desktop_limit` | 24 | 1..256; each recipe desktop must be 1..this limit |
| `dt_win_limit` | 4 | 1..256; caps implicit-layer entries per desktop; explicit layers may exceed it with a warning |
| `min_window_exposure_px` | 32 | 1..32768 pixels; exposure-warning threshold |
| `terminal_width_percent` | 90 | 1..100%; **total** panel region width, not per-window width |
| `terminal_gap_percent` | 1 | 0..100%; horizontal panel gutter |
| `terminal_height_percent` | 92 | 1..100%; panel height budget |
| `terminal_left_percent` | 2 | 0..100%; panel region left offset |
| `terminal_top_percent` | 2 | 0..100%; panel region top offset |
| `terminal_row_gap_percent` | 1 | 0..100%; panel row gutter |
| `graphical_left_percent` | 1 | 0..100%; shared under/over region left offset |
| `graphical_top_percent` | 1 | 0..100%; shared under/over region top offset |
| `graphical_width_percent` | 98 | 1..100%; shared under/over region width |
| `graphical_height_percent` | 94 | 1..100%; shared under/over region height |
| `verbosity` | header value; `notice` (5) if empty | 0..7; explicit CLI `-v`/`-q` adjustments apply after sourcing |

Left + width and top + height must each be <=100 for both regions. Calculated
frames must fit the supplied display. The panel allocator supports at most four
panel entries per desktop regardless of `dt_win_limit`. Exposure is a frame
prediction, not proof of compositor visibility. The shared planner owns outer
frame geometry; remote pixel and initial client sizes below do not replace it.

The percentage values above describe the current built-ins in `plan_defaults()`
(`libexec/joetoo-kwin-plan-functions`), not an immutable product requirement.
On a 1920x1080 configured display, the graphical base rectangle is
`(19,10) 1881x1015`. `under` and `over` use this same rectangle; their
one-shot stacking order is separate. The four-panel 2x2 layout uses the
`terminal_*` budget independently. Neither region automatically excludes a
KDE taskbar, compositor work area or widget area; verify visual fit on each
host and override these values in trusted configuration as appropriate.

## Initial cohort and SFTP

| Name | Default | Bounds / purpose |
| --- | --- | --- |
| `initial_focus_timeout_ms` | 500 | 1..2000 ms; bounded observation after one focus request |
| `initial_focus_poll_interval_ms` | 25 | 1..250 ms and <= focus timeout; current Bash spelling accepts at most two digits, so use 1..99 through the CLI |
| `sftp_capability_timeout_ms` | 2000 | 1..10000 ms; local capability check |
| `SFTP_ADVISORY_ENABLED` | `$TRUE` | `$TRUE`/`$FALSE`; optional post-confirmation NSS/TCP advisory |
| `sftp_advisory_timeout_ms` | 2000 | 1..10000 ms per advisory stage |
| `sftp_advisory_ssh_port` | 22 | 1..65535; advisory fallback port, explicit SFTP URI port takes precedence |

SFTP advisory reachability is not SSH authentication or remote directory-listing
proof. Disabling the advisory does not bypass normal target validation.

## TigerVNC over SSH

| Name | Default | Bounds / purpose |
| --- | --- | --- |
| `vnc_ssh_start_timeout_ms` | 10000 | 100..120000 ms; noninteractive dedicated SSH startup |
| `vnc_viewer_ready_timeout_ms` | 300000 | 1000..3600000 ms; persistent local viewer readiness, possibly awaiting VNC interaction |
| `vnc_supervisor_poll_interval_ms` | 100 | 10..1000 ms; supervisor polling |
| `vnc_cleanup_timeout_ms` | 2000 | 100..30000 ms; owned-process cleanup |
| `vnc_local_port_attempts` | 3 | 1..20; loopback forwarding allocation attempts |
| `vnc_identity_event_limit` | 256 | 16..4096 reports |
| `vnc_identity_settle_ms` | 500 | 10..2000 ms and strictly below viewer readiness timeout |
| `vnc_dbus_timeout_ms` | 3000 | 100..30000 ms per call; also used for configured RDP mechanical calls |
| `vnc_placement_timeout_ms` | 15000 | 100..15000 ms; also used for configured RDP placement |
| `vnc_identity_start_timeout_ms` | 1000 | 100..10000 ms and strictly below D-Bus timeout; identity observer startup |

SSH key/agent and independently verified host trust are required. These bounds
do not introduce interactive SSH authentication. A readiness deadline is not
proof of the operator's authentication state. SSH transport, viewer identity,
placement and remote usability remain separate.

## SDL FreeRDP

| Name | Default | Bounds / purpose |
| --- | --- | --- |
| `rdp_registration_timeout_ms` | 300000 | 1000..3600000 ms; persistent local viewer registration, possibly including NLA interaction |
| `rdp_registration_poll_ms` | 100 | 10..1000 ms and strictly below registration timeout |
| `rdp_registration_event_limit` | 4096 | 16..65536 lifecycle reports |
| `rdp_registration_window_limit` | 64 | 1..512 tracked new UUIDs |
| `rdp_backend_log_byte_limit` | 65536 | 1024..1048576 bytes; private backend-evidence budget, not a filesystem quota |
| `rdp_x11_renderer` | `auto` | `auto` or `software`; native-X11 child-only renderer policy |
| `rdp_x11_identity_settle_ms` | 500 | 1..30000 ms and strictly below registration timeout; native-X11 UUID eligibility heuristic |
| `rdp_remote_width` | 1024 | 64..8192 remote pixels |
| `rdp_remote_height` | 768 | 64..8192 remote pixels |
| `RDP_SMART_SIZING` | `$TRUE` | `$TRUE`/`$FALSE`; SDL scaling policy |
| `rdp_initial_client_width` | 800 | 64..8192 initial client pixels |
| `rdp_initial_client_height` | 600 | 64..8192 initial client pixels |
| `rdp_windowing_backend` | `auto` | `auto`, `wayland`, `x11`; positive runtime KWin/backend evidence required |
| `rdp_security_protocol` | `nla` | `nla` -> `/sec:nla`; `negotiate` -> no `/sec:` argument |
| `rdp_certificate_policy` | `strict` | `strict` -> `/cert:deny`; `prompt` -> no `/cert:` argument |

Security policy is validated offline by `-c` and shown at info verbosity (`-vc`).
Built-ins are NLA and strict certificate refusal; the existing system/user defaults,
selected profile or explicit per-run plan may override either enum. Supported CLI
verbosity overrides still apply last; there are no new raw client-switch options.

| Config variable | Allowed value | Literal FreeRDP argv mapping |
| --- | --- | --- |
| `rdp_security_protocol` | `nla` (default) | One `/sec:nla`; exclusive NLA mode, not `/sec:nla:on` |
| `rdp_security_protocol` | `negotiate` | No `/sec:` argument; stock negotiation, not `/sec:rdp` or `-nego` |
| `rdp_certificate_policy` | `strict` (default) | One `/cert:deny`; failed validation is refused without an exception prompt |
| `rdp_certificate_policy` | `prompt` | No `/cert:` argument; stock trust/interactive handling |

NLA still uses TLS internally. `/sec:tls` instead selects TLS-only RDP security
mode; `/tls:*` controls a separate TLS-version/cipher dimension. No TLS-version
force or arbitrary security switches are added here. `prompt` is an explicit,
less restrictive user choice; `negotiate` permits the client's default security
negotiation rather than enforcing NLA. Neither option means automatic certificate
bypass. The same shared argument builder gives development launchers NLA/strict
defaults; production supplies effective layered settings. Local registration and
placement still report remote authentication/session state as unverified; a local
viewer may register before certificate refusal. Previous native success evidence
predates these defaults and does not constitute their native acceptance.

Remote dimensions map to `/size:WIDTHxHEIGHT`. Smart sizing enabled maps initial
client dimensions to `/smart-sizing:WIDTHxHEIGHT`; disabled maps to
`/smart-sizing:off`, while both initial dimensions remain validated. Neither
mapping subtracts decorations or changes the planner's outer-frame contract.

`auto` backend is resolved through authenticated KWin evidence, not
`XDG_SESSION_TYPE` alone. An explicit backend must match the native compositor;
XWayland is not native X11. In X11 renderer `auto`, inherited `SDL_RENDER_DRIVER`
and `SDL_FRAMEBUFFER_ACCELERATION` are removed from the child environment. In
`software`, they are set to `software` and `0`. Neither setting proves viewer
identity, guarantees GPU use or establishes a performance result.

X11's 500-ms heuristic can select a 600-ms temporary viewer; no replacement UUID
is silently enrolled. Wayland retains its accepted distinct identity contract.
Registration and placement do not prove TLS/NLA trust, GDM readiness or remote
login. There is no GDM wait gate. The existing passive post-terminal RDP trace
horizon also follows the registration timeout; mechanical placement does not.

Known-clean pre-registration failures may allow the serial plan to continue,
with incomplete/nonzero overall status. Busy, unknown ownership, cleanup
uncertainty and unresolved registered-viewer placement stop it. Registered
viewers survive noncritical supervision failures; a missing historical managed
record still reserves its slot. No setting bypasses those safeguards.

## Recipe and override examples

`DESKTOP|PROGRAM|MODE|TARGET[|LAYER]` has four or five fields. Omitted/blank layer
means implicit `panel`; explicit `under`, `panel`, `over` control one-shot initial
ordering. Slots follow entry order for each desktop; desktops are grouped in
first-appearance order. All entries on one desktop share its derived slot
sequence, regardless of application. Endpoints below are generic examples,
not instructions or authorization to connect.

| Program / mode | Example target | Notes |
| --- | --- | --- |
| `konsole` / `local` | `btop` | Executable basename; no arguments |
| `konsole` / `ssh` | `user@host.example` | SSH alias/host; no supported explicit recipe port; existing probe uses TCP 22 |
| `dolphin` / `local` | empty or `Documents` | Empty means HOME; relative paths resolve against HOME |
| `dolphin` / `sftp` | `sftp://user@files.example/home/user/` | Optional user, port and absolute URI path; no password |
| `vncviewer` / `ssh` | `ssh://user@vnc.example/display/2` | Remote VNC port 5902; optional SSH port; `/port/5902` alternative |
| `sdl-freerdp` / `rdp` | `rdp://user@rdp.example:3389` | User required, TCP 3389 default; no password/path/query/fragment/switches |

RDP supports validated DNS/IPv4 and bracketed IPv6, for example
`rdp://user@[2001:db8::10]:3389`. VNC display `N` is nonnegative decimal and must yield a TCP port in
1..65535 (`5900+N`); explicit TCP ports are 1..65535. SFTP path/encoding and
transport rules are client-specific. See the source validators before extending
these grammars; offline planner acceptance of legacy modes such as `direct`,
`swr` or `via-ssh` does not make them supported configured `-o` recipes.

Example **Bash** assignments to copy into a selected per-run file (not commands
to run as a separate launcher):

```bash
terminal_width_percent=80
rdp_remote_width=1920
rdp_remote_height=1080
rdp_windowing_backend=wayland
rdp_registration_timeout_ms=600000
RDP_SMART_SIZING=$FALSE
SFTP_ADVISORY_ENABLED=$FALSE
# End of example

```

This example requires an appropriate native Wayland host for actual launch.
Use `-c` to inspect a copied, edited plan. A successful dry run is not native
backend, endpoint, authentication or placement acceptance.

## User-owned configs and default selection

`eselect joetoo-kwin` selects which per-run configuration the ordinary
`joetoo-kwin -o` command loads when `-f FILE` is absent. Both the selectable
configs and the active symlink are in the **user's** XDG configuration directory;
the selector never scans, creates or changes links under `/etc`.

The selector reads only regular `.conf` files under
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/configs/` (a relative
`XDG_CONFIG_HOME` falls back to `$HOME/.config`). `set NAME` creates or changes
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf` as a symlink
to `configs/NAME`. For example:

```text
~/.config/joetoo-kwin/
├── configs/
│   ├── joetoo-kwin.conf
│   └── joetoo-kwin2.conf
└── joetoo-kwin.conf -> configs/joetoo-kwin.conf
```

Neither Portage nor `eselect list/show` creates user configs. As the intended
**non-root** user, create and review the files explicitly:

```bash
config_root=${XDG_CONFIG_HOME:-$HOME/.config}
case $config_root in /*) ;; *) config_root=$HOME/.config ;; esac
config_dir=$config_root/joetoo-kwin
install -d -m 0700 -- "$config_dir/configs"
cp -n -- /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf "$config_dir/configs/joetoo-kwin.conf"
chmod 600 -- "$config_dir/configs/joetoo-kwin.conf"
# Edit/review the copied configuration before executing trusted Bash:
joetoo-kwin -c -f "$config_dir/configs/joetoo-kwin.conf"
eselect joetoo-kwin list
eselect joetoo-kwin set joetoo-kwin.conf
eselect joetoo-kwin show
joetoo-kwin -c  # Verify what the selected default would launch.
# End of commands
```

`list` shows names/numbers from `configs/*.conf`; `set` accepts a listed
basename or number, and `show` reports the selected config. The default link
above is `joetoo-kwin.conf -> configs/joetoo-kwin.conf`. `joetoo-kwin -o`
loads that file after the normal optional defaults layers. `-f FILE` selects
another per-run plan without changing the symlink or suppressing defaults.
The CLI's `/etc/joetoo-kwin/joetoo-kwin.conf` fallback remains independent:
`eselect` does not manage it, and the fallback is used only if no user plan exists.

Config basenames must start with an ASCII letter/digit, contain only ASCII
letters, digits, underscore, dot or hyphen, and end in `.conf`. The selector
accepts only readable, user-owned regular files with one hard link and valid
Bash syntax, never symlink configs, arbitrary absolute paths or traversal.
The `joetoo-kwin` and `configs` directories must be user-owned, non-symlink
directories without group/other write permission. The XDG base must also be
owned and not group/other writable; an existing symlinked XDG base may resolve
to a safe owned directory. The CLI's `-f` policy is independent and remains
broader. All selected files are **trusted executable Bash** when loaded by
the CLI; `eselect` checks syntax but never sources them.

`set` refuses to replace a regular active config, a dangling/foreign symlink,
or an unexpected object. It can switch an existing valid `configs/NAME` link
(relative or canonical absolute). Its retained private lock serializes selector
invocations; the legacy lock filename is retained for compatibility with older
module versions. First selection uses no-clobber rename; later switches use
GNU `mv --exchange --no-copy`, preserving and verifying the displaced link.
An unsupported filesystem or an unsafe race fails without claiming success.
Do not concurrently rewrite/remove configs or the active link outside `eselect`;
its advisory lock does not coordinate arbitrary editors.

If `joetoo-kwin.conf` is an existing **regular file**, preserve it before asking
`eselect` to create its link. Inspect paths/backups first; do not run blindly:

```bash
# config_dir is the user configuration directory resolved above.
cp -n -- "$config_dir/joetoo-kwin.conf" "$config_dir/configs/migrated.conf"
cmp -s -- "$config_dir/joetoo-kwin.conf" "$config_dir/configs/migrated.conf" &&
    mv -n -- "$config_dir/joetoo-kwin.conf" "$config_dir/joetoo-kwin.conf.backup"
eselect joetoo-kwin set migrated.conf && joetoo-kwin -c
# End of commands
```

If a backup already exists, select a different name. Existing links into the
old `profiles/` directory are **not** automatically converted; migrate their
files and links deliberately. The selector leaves invalid links untouched.
Deleting a selected config makes the CLI fail on its dangling selection rather
than silently using the `/etc` fallback.

## Packaging integration — maintainer actions

| Checkout source | Installed destination |
| --- | --- |
| `joetoo-kwin-per-run-template.conf` | `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf` |
| `docs/configuration-reference.md` | `/usr/share/doc/${PF}/configuration-reference.md` (possibly compressed) |
| `eselect/joetoo-kwin.eselect` | `/usr/share/eselect/modules/joetoo-kwin.eselect` |

`${PF}` is the ebuild's versioned package name. The selector requires Gentoo's
`eselect` framework (`app-admin/eselect`) and the usual Bash/coreutils/util-linux
commands (`realpath`, `stat`, `flock`, etc.). Safe switching requires GNU `mv`
with `--exchange`/`--no-copy` and filesystem atomic-exchange support; unsupported
systems fail without an unsafe replacement fallback. The CLI does not require `eselect`;
profile selection is optional. Final dependencies/compression belong to the
maintainer's protected packaging repository.

Merge this **EAPI helper fragment into the existing `src_install()`**, adapting
source paths if the project is unpacked below `${S}`. It is not a standalone
shell installer and must not replace other package installation logic:

```bash
insinto /usr/share/joetoo-kwin
insopts -m0644
doins joetoo-kwin-per-run-template.conf
insinto /usr/share/eselect/modules
doins eselect/joetoo-kwin.eselect
dodoc docs/configuration-reference.md
# End of commands

```

Do not populate/overwrite HOME, create user profiles, run the selector, source
OpenRC conf.d into the CLI, or migrate plans during package installation or
post-installation. Give users optional setup instructions instead. No active
`defaults.conf` is required; optional administrator/user files should contain
only intentional overrides, not this exhaustive manual. Keep their ownership
and write access appropriate for trusted executable code. The broker POC
installer remains unchanged and is not the package documentation installer.
No protected ebuild, live user file or installed resource was changed here.

## Implementation references

Defaults and geometry validation: `libexec/joetoo-kwin-plan-functions`.
Selection/verbosity: `joetoo-kwin` (`select_config`, `check_plan`,
`apply_cli_verbosity`). Recipe validators: `libexec/joetoo_kwin_rdp_target.py`,
`libexec/joetoo_kwin_vnc_target.py`, `libexec/joetoo_kwin_sftp_target.py`.
RDP identity bounds: `libexec/joetoo_kwin_rdp_launch.py`.
These are checkout paths; the shipped reference is self-contained and does not
require production hosts to have the source tree.

## Managed inventory (`-l`)

`joetoo-kwin -l` queries only the broker's `ListManaged` inventory. It does not
source a plan/defaults file, launch an application, activate a window or change
geometry. One fixed-column row shows each managed ID, intended desktop/slot,
presence, placement and full UUID. Rows sort by desktop, slot, then managed ID;
column widths expand for long IDs rather than truncating them. Missing and
uncertain records remain visible because absence does not release reservations.
An empty registry is reported explicitly; an unavailable broker or inconsistent
response returns nonzero rather than an empty-success result. No remote login,
TLS/connection state, target or private log path is inferred or printed.

## Single managed launch (`-L`)

`joetoo-kwin [-v|-q ...] [-f FILE] -L DESKTOP PROGRAM MODE TARGET [over|under]`
accepts separate shell arguments, not a pipe-delimited string or raw application
argv. Omitted layer means **over for `-L` only**. Explicit `over` and
one-shot `under` are supported. `panel` and unknown/blank explicit layers are
rejected before launch. Configured `-o` retains its implicit/blank **panel**
default and all three layers.

The ordinary configuration layers still supply screen dimensions, security,
backend, geometry and mechanical limits. The selected per-run file's recipe
array is replaced only for this invocation by the command-line recipe; its other
settings remain effective. `-f` selects that settings/plan file normally and never
changes a selected profile. Options precede `-L`; quote an empty TARGET for
Dolphin's local home directory. Supported executable pairs are Konsole local/ssh,
Dolphin local/sftp, TigerVNC ssh and SDL FreeRDP rdp, with their existing validators.

The launch chooses an unused logical slot in 1..256 from authoritative retained
reservations, including missing windows. Uncertain/malformed inventory or Busy
state fails closed. The displayed one-entry plan uses the configured graphical
region, without panel allocation, peer cascade or reflow. Confirmation precedes
application/network launch and desktop provisioning. The same serial adapters
positively register and place only the new UUID; state/slot checks repeat before
submission and the broker independently guards reservation. A newly conflicting
slot is rejected, not silently changed after confirmation.

A one-entry initial-layout transaction verifies the requested one-shot
stacking: `over` raises only the new exact UUID, while `under` lowers it
beneath participating normal-layer peers. Existing peer geometry and
membership are preserved. There is no permanent keep-above/below flag,
existing-window move or live reflow. Special shell/dock layers are not
ordinary application stacking, and unsupported peer state can prevent
successful verification rather than triggering a forced change. An inactive
desktop is not switched automatically; focus follows the initial-layout
policy. Placement, one-shot stacking/focus and remote login remain separate
outcomes; a stacking failure can leave a valid placed window and return
failure without closing it or releasing its reservation.

`-L over` requires the broker/resident `single_raise_protocol=1`, and
`-L under` requires `single_lower_protocol=1`; an older or mismatched pair is
rejected before confirmation. The existing `-o` protocol remains compatible.
Live-desktop reflow is deferred; the earlier
[source review](../archive/task_step1.5/step1.5d-managed-inventory-and-live-layout-review.md)
is historical, not an active implementation requirement. See the
[historical headless candidate and native matrix](../archive/task_step1.5/step1.5d-single-recipe-headless-candidate.md),
[accepted native X11/Wayland record](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md)
and [post-fix regression evidence](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md).
Step 1.5d is accepted and merged through PR #30. Step 1.6 managed operations
are the next milestone; detailed scope and implementation are not yet approved.

## Managed graceful close (Step 1.6 candidate)

`joetoo-kwin [-f FILE] -d win-001` previews and confirms one managed target;
`joetoo-kwin [-f FILE] -x` previews a fixed eligible set and confirms it once.
The ordinary layered configuration is used for the budgets below; an absent
default per-run plan is optional for close (explicit `-f` must still be valid). Close does
not consume launch recipes or require valid launch geometry. `-l` stays read-only
and does not load executable configuration. The exact-version native adapter
must be installed/loaded separately by the maintainer; absence fails closed.

| Name | Built-in default | Validation / meaning |
| --- | --- | --- |
| `managed_close_timeout_ms` | 15000 | 100..120000 ms per target; refusal/no disappearance is not success |
| `managed_close_total_timeout_ms` | 300000 | 100..600000 ms for accepted fixed set; >= per-target budget |
| `managed_close_prepare_timeout_ms` | 300000 | 1000..600000 ms for authentication/preview/confirmation |
| `managed_close_x11_grab_ms` | 100 | 10..500 ms maximum atomic X11 fence/WM_DELETE operation |
| `managed_close_poll_ms` | 100 | 10..1000 ms status polling |
| `managed_close_dbus_timeout_ms` | 3000 | 100..10000 ms individual native/frontend IPC |

Closing retains registration, intended desktop/slot reservation and placement
history. It neither retires a record nor saves/restores a snapshot. Only native
KWin-authenticated disappearance proves closure. Dispatch, refusal/timeout,
source loss and unresolved helper cleanup are reported independently. A lost
frontend does not cancel accepted bulk work; retained results can be queried
using broker `ManagedCloseStatus(REQUEST_ID)` from another console. Results
are in-memory and bounded; broker restart recovery is not implemented.

The terminal-membership warning is conditional on authenticated Konsole/session
and native UUID correlation; uncertain/multi-window identity is not guessed.
Already-issued graceful requests cannot be recalled. Late disappearance cannot
revive a terminal timeout. No application force-kill escalation is supplied.
