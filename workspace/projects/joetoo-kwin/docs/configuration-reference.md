# joetoo-kwin CLI configuration reference

<!-- Copyright 2025-2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

This is documentation, not a sourced defaults file. It describes the current
implementation, including accepted Increment 4 Stage 3 behavior. The short
`joetoo-kwin-per-run-template.conf` at the project root is the copyable starting
point. In an installed package, use the resource path in the packaging section.

## Current loading and use

`joetoo-kwin -c -f FILE` validates and calculates a plan without launching it.
`joetoo-kwin -o -f FILE` additionally performs runtime preflight, requests
confirmation, and runs the serial plan. `joetoo-kwin -f FILE -m l` (or `-m r`) consumes the shared
geometry policy; put `-f` and other options before `-m`. Configuration is **trusted
executable Bash**, not sandboxed key/value data; even `-c` executes the selected
file. Read it before use.

The implemented order is built-in `plan_defaults()`, **one** selected plan,
then explicit CLI `-v`/`-q` adjustments. Explicit `-f FILE` selects that plan
instead of searching. Otherwise the CLI selects:

1. `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf`;
2. `/etc/joetoo-kwin/joetoo-kwin.conf` only if the user plan is absent.

A relative `XDG_CONFIG_HOME` is ignored in favor of `$HOME/.config`. A selected
unreadable, invalid or dangling-symlink plan fails; it does not trigger fallback.
User and system plans are not combined. No `defaults.conf` files are currently
loaded. `-f` does not erase built-in defaults: it selects a different plan with
the same authority to override any exposed setting, subject to validation.

OpenRC `joetoo-kwind` conf.d is separate service configuration. Its executable,
resident and environment settings are **not** CLI plan inputs. Exact UUID
ownership, fail-closed cleanup and other safety invariants are not configurable
toggles. Derived slots, managed IDs, UUIDs and internal transaction constants
are not plan settings.

The accepted direction for a later Stage 4B is optional **sparse** system/user
overrides between built-ins and the selected per-run plan. Each plan, including
one selected by `-f`, can override any exposed validated setting. Those extra
layers and optional per-user `eselect` selection are not implemented here.

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

## Packaging preparation — maintainer proposal, not an installation

| Checkout source | Candidate installed destination |
| --- | --- |
| `joetoo-kwin-per-run-template.conf` | `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf` |
| `docs/configuration-reference.md` | `/usr/share/doc/${PF}/configuration-reference.md` (possibly compressed by Gentoo documentation policy) |

Both resources are package-owned data files, normally mode 0644.
`${PF}` is the ebuild's versioned package name, not a literal directory to
create. The maintainer decides final ebuild paths, documentation compression and
post-install guidance. This reference is documentation, not an active
`/etc/joetoo-kwin/defaults.conf`. Do not install it as one or claim that sparse
defaults loading already exists. The development broker installer remains
unchanged; it is not the package documentation installer.

For human packaging integration, install the template as a read-only resource
and the reference as package documentation. Do not populate/overwrite HOME,
create user profiles, source OpenRC conf.d into the CLI, or migrate current
plans. No ebuild changes or installs were made by this preparation. The optional
user profile selector and all runtime layering changes require separate scope.
Installed readers should use the absolute resource destination from the table.

## Implementation references

Defaults and geometry validation: `libexec/joetoo-kwin-plan-functions`.
Selection/verbosity: `joetoo-kwin` (`select_config`, `check_plan`,
`apply_cli_verbosity`). Recipe validators: `libexec/joetoo_kwin_rdp_target.py`,
`libexec/joetoo_kwin_vnc_target.py`, `libexec/joetoo_kwin_sftp_target.py`.
RDP identity bounds: `libexec/joetoo_kwin_rdp_launch.py`.
These are checkout paths; the shipped reference is self-contained and does not
require production hosts to have the source tree.
