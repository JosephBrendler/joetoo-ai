# joetoo-kwin CLI configuration reference

<!-- Copyright 2025-2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

This is documentation, not a sourced defaults file. It describes the current
implementation, including layered CLI defaults and the optional user-owned
profile selector. Accepted Increment 4 Stage 3 behavior is unchanged. The short
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
4. One selected per-run plan: explicit `-f FILE`, otherwise the XDG user
   `joetoo-kwin/joetoo-kwin.conf`, with `/etc/joetoo-kwin/joetoo-kwin.conf`
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

Profile selection is optional: a regular existing user plan remains valid,
and explicit `-f` works independently of the selected profile. The selector
never changes system defaults or daemon configuration.

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
| `desktop_limit` | 20 | 1..256; each recipe desktop must be 1..this limit |
| `dt_win_limit` | 4 | 1..256; caps implicit-layer entries per desktop; explicit layers may exceed it with a warning |
| `min_window_exposure_px` | 32 | 1..32768 pixels; exposure-warning threshold |
| `terminal_width_percent` | 87 | 1..100%; **total** panel region width, not per-window width |
| `terminal_gap_percent` | 2 | 0..100%; horizontal panel gutter |
| `terminal_height_percent` | 85 | 1..100%; panel height budget |
| `terminal_left_percent` | 1 | 0..100%; panel region left offset |
| `terminal_top_percent` | 5 | 0..100%; panel region top offset |
| `terminal_row_gap_percent` | 3 | 0..100%; panel row gutter |
| `graphical_left_percent` | 5 | 0..100%; under/over region left offset |
| `graphical_top_percent` | 3 | 0..100%; under/over region top offset |
| `graphical_width_percent` | 94 | 1..100%; under/over region width |
| `graphical_height_percent` | 90 | 1..100%; under/over region height |
| `verbosity` | header value; `notice` (5) if empty | 0..7; explicit CLI `-v`/`-q` adjustments apply after sourcing |

Left + width and top + height must each be <=100 for both regions. Calculated
frames must fit the supplied display. The panel allocator supports at most four
panel entries per desktop regardless of `dt_win_limit`. Exposure is a frame
prediction, not proof of compositor visibility. The shared planner owns outer
frame geometry; remote pixel and initial client sizes below do not replace it.

## Initial cohort and SFTP

| Name | Default | Bounds / purpose |
| --- | --- | --- |
| `initial_focus_timeout_ms` | 500 | 1..2000 ms; bounded observation after one focus request |
| `initial_focus_poll_interval_ms` | 25 | 1..250 ms and <= focus timeout; current Bash spelling accepts at most two digits, so use 1..99 through the CLI |
| `sftp_capability_timeout_ms` | 2000 | 1..10000 ms; local capability check |
| `sftp_advisory_enabled` | `$TRUE` | `$TRUE`/`$FALSE`; optional post-confirmation NSS/TCP advisory |
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
sftp_advisory_enabled=$FALSE
# End of example

```

This example requires an appropriate native Wayland host for actual launch.
Use `-c` to inspect a copied, edited plan. A successful dry run is not native
backend, endpoint, authentication or placement acceptance.

## User-owned profiles and migration

The optional `eselect joetoo-kwin` module uses the same XDG directory as the CLI.
It does not bootstrap configuration/profile directories or populate HOME with
plans. Users create their profiles explicitly. A requested `set` creates only
its private lock, temporary publication directory and selection link. As the intended **non-root** user, after package installation:

```bash
config_root=${XDG_CONFIG_HOME:-$HOME/.config}
case $config_root in /*) ;; *) config_root=$HOME/.config ;; esac
config_dir=$config_root/joetoo-kwin
install -d -m 0700 -- "$config_dir/profiles"
cp -n -- /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf "$config_dir/profiles/work.conf"
# Inspect/edit work.conf for the display, desired recipes and overrides first.
eselect joetoo-kwin list
eselect joetoo-kwin set work.conf && joetoo-kwin -c
eselect joetoo-kwin show
# End of commands

```

`list` gives names/numbers; `set` accepts a safe basename such as `work.conf`
or its current list number. Prefer names for stable scripts. `show` reports
the selected name, an unchanged regular configuration, or no user selection.
The resulting user-plan symlink is `joetoo-kwin.conf -> profiles/work.conf`.
The CLI sources that plan normally; the selector itself never executes profiles.
Validate another plan with `joetoo-kwin -c -f FILE` without changing the selection.
Use confirmed `-o` only after reviewing the effective plan and runtime preflight.

Profile names must start with an ASCII letter/digit, contain only ASCII letters,
digits, underscore, dot or hyphen, and end in `.conf`. The module accepts only
readable regular user-owned files with one link and valid Bash syntax, not
symlink/hardlink profiles, arbitrary absolute paths or directory traversal.
Configuration/profile directories must be user-owned, non-symlink directories
without group/other write permission; the XDG base must also be owned and not
writable by others. An existing symlinked XDG base can resolve to a safe owned
directory, but the `joetoo-kwin` and `profiles` subdirectories cannot be symlinks.
The CLI's pre-existing trusted-file behavior remains broader: the optional
selector does not prohibit an existing manually managed plan or explicit `-f`.

The selector refuses to replace a regular file, foreign/dangling active symlink
or unexpected object. Existing valid relative or canonical absolute profile
symlinks may be switched. A retained private lock serializes selector actions;
Busy selection fails without waiting indefinitely. First publication uses no-clobber rename. Switching uses GNU
`mv --exchange --no-copy`: the displaced object is preserved and checked before cleanup, so a
concurrently substituted regular file is restored rather than discarded. Target
rechecks roll back a switch if the target disappears. If interference prevents
restoration, the displaced object is retained in a reported private temporary
directory for manual recovery; success is never claimed.
Do not concurrently rewrite/remove profiles or the active plan outside the
selector: the advisory lock coordinates selector invocations, not arbitrary
editors. Revalidate after manually editing a selected trusted Bash file.

For an existing **regular** user plan, first preserve it deliberately. Do not
run these migration steps blindly, and choose an unused backup filename:

```bash
# config_dir is the user configuration directory resolved above.
cp -n -- "$config_dir/joetoo-kwin.conf" "$config_dir/profiles/migrated.conf"
cmp -s -- "$config_dir/joetoo-kwin.conf" "$config_dir/profiles/migrated.conf" &&
    mv -n -- "$config_dir/joetoo-kwin.conf" "$config_dir/joetoo-kwin.conf.backup"
eselect joetoo-kwin set migrated.conf && joetoo-kwin -c
# End of commands

```

If a backup already exists, inspect it and choose another name. A non-moved
regular plan makes `set` refuse safely. Invalid/dangling/foreign links require
manual inspection and preservation before removal; the module does not repair
or migrate them automatically. Deleting a selected profile later makes the CLI
fail on the dangling selection instead of using the system plan.

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

`joetoo-kwin [-v|-q ...] [-f FILE] -L DESKTOP PROGRAM MODE TARGET [over]`
accepts separate shell arguments, not a pipe-delimited string or raw application
argv. Omitted layer means **over for `-L` only**. Explicit `over` is supported;
`panel`, `under` and unknown/blank explicit layers are rejected before launch.
Configured `-o` retains its implicit/blank **panel** default and all three layers.

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

A one-entry initial-layout transaction raises only that UUID once and verifies it
above the other observed normal application windows on the requested desktop.
It also verifies unchanged existing-peer geometry and membership. No persistent
keep-above flag or existing-window move is used. Special shell/dock layers are
not ordinary application stacking; an existing normal keep-above window can
prevent successful verification, which is reported as failure rather than forced
through. An inactive desktop is not switched automatically; focus follows the
existing initial-layout policy. Placement, one-shot stack/focus and remote login
remain separate outcomes; an incomplete raise may leave a valid placed viewer
and returns failure without closing it or releasing its reservation.

`-L` requires a matching broker/resident advertising `single_raise_protocol=1`;
an older pair is rejected before confirmation. The existing `-o` protocol remains
compatible. Live-desktop reflow is withdrawn from Step 1.5d; the earlier
[source review](../task_step1.5/step1.5d-managed-inventory-and-live-layout-review.md)
is historical, not an active implementation requirement. See the
[current headless candidate and native matrix](../task_step1.5/step1.5d-single-recipe-headless-candidate.md).
