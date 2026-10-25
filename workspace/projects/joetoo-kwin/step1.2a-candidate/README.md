# joetoo-kwin Step 1.2a — OpenRC supervision candidate

**Status:** isolated candidate; gmki91/X11 native service startup and D-Bus interface verified by maintainer; lifecycle survival and q552u01/Wayland native service tests still pending. Read
`../ARCHITECTURE.md` and `../AGENTS.md` first. Existing Step 0 POCs and the
merged Step 1 CLI remain unmodified.

## Scope and baseline

This tests the early lifecycle gate for `joetoo-kwind`, **not** the later registry
or window-launch milestones. The new Python executable derives from
`joetoo-kwin-launch-poc/joetoo-kwin-broker.py` and deliberately preserves
`org.joetoo.KWinBridge`, `/org/joetoo/KWinBridge`, and the six existing methods:
`Submit`, `Take`, `SubmitLaunch`, `TakeLaunch`, `Complete`, and `Status`.
It remains single-flight and does **not** launch Konsole, spawn SSH, register
KWin UUIDs, persist JSON or load resident KWin JavaScript. These are later gates.

Files and proposed installation destinations:

- `libexec/joetoo-kwind` -> `/usr/libexec/joetoo-kwind` (foreground Python daemon)
- `user-init.d/joetoo-kwind` -> `/etc/user/init.d/joetoo-kwind` (OpenRC **user** service)
- `tests/test_step1_2a.py` -> headless mocks and non-destructive service checks
- `tools/joetoo-kwind-configure-openrc-user` -> optional **user-invoked** OpenRC allowlist setup helper
- `tests/test_openrc_user_setup.py` -> configuration helper regression checks

**No** system-level `/etc/init.d/joetoo-kwind` service and **no** root user mode.
`rc-service -U` must run in a valid graphical user session with
`XDG_RUNTIME_DIR` set; DBus can be addressed by `DBUS_SESSION_BUS_ADDRESS` or
an existing `$XDG_RUNTIME_DIR/bus` socket. Both gmki91/X11 and q552u01/Wayland have reported a valid session D-Bus address under `/tmp/dbus-*` (not a `$XDG_RUNTIME_DIR/bus` socket), so `rc_env_allow` is needed for the POC when OpenRC filters the inherited address. The service refuses root and a
runtime directory owned by another UID.

Use default OpenRC start/stop/status with `supervisor=supervise-daemon`, foreground
process, and throttled respawn (10/5/120, patterned after joetoo DDNS).
`rc_cgroup_cleanup=NO` is an intentional protective override; the daemon does
not launch applications or execute process-group termination. `pidfile` is
private runtime state for the **supervisor**, not the application.

## Headless checks (safe on a development machine)

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
sh -n user-init.d/joetoo-kwind
python3 -m py_compile libexec/joetoo-kwind
sh -n tools/joetoo-kwind-configure-openrc-user
```

The unit tests stub dbus and GLib; they do **not** exercise actual OpenRC,
Python D-Bus bindings, PyGObject, compositor/session selection or POSIX
process/cgroup semantics. A passing suite cannot establish lifecycle safety.

## Graphical D-Bus environment setup (ordinary user only)

OpenRC user services filter inherited environment variables unless listed in
`rc_env_allow`. The running Plasma session may have
`DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-...,...` without having
`$XDG_RUNTIME_DIR/bus`. On gmki91, adding these two names to the user's
`~/.config/rc/rc.conf` allowed the service to start and register all six
existing D-Bus methods. This **does not yet establish stop/restart safety**.

For this POC, **from the project candidate directory as the graphical user**:

```sh
tools/joetoo-kwind-configure-openrc-user --check
tools/joetoo-kwind-configure-openrc-user --apply
```

The check is read-only. Apply creates or updates
`${XDG_CONFIG_HOME:-$HOME/.config}/rc/rc.conf` only on request; it preserves
existing settings and `rc_env_allow` entries, refuses a symlink or incomplete
managed block, and is idempotent. Review the resulting file before proceeding.
The helper does not install the broker or change any system file. It adds
`DBUS_SESSION_BUS_ADDRESS` and the **POC-only** `JOETOO_KWIND_EXEC` name.
The packaged daemon will not require the POC-only override.

If you prefer to configure manually, add the required names to any existing
`rc_env_allow` without discarding other entries. A simple fresh file may be:

```sh
rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"
```

Keep the original exported graphical bus address; do not hard-code the
per-login `/tmp/dbus-...` socket or autolaunch another session bus.
`XDG_SESSION_TYPE=tty` may be correct for a Plasma session launched from a
TTY; successful `qdbus6 org.kde.KWin /KWin` connectivity is stronger evidence
of the bus actually in use.

### Updating a prior test installation

If the POC service and daemon are already installed under your home directory,
**stop the user service before replacing the service definition**:

```sh
rc-service -U joetoo-kwind stop
install -m 0755 user-init.d/joetoo-kwind "${XDG_CONFIG_HOME:-$HOME/.config}/rc/init.d/joetoo-kwind"
export JOETOO_KWIND_EXEC="$HOME/.local/libexec/joetoo-kwind"
rc-service -U joetoo-kwind start
rc-service -U joetoo-kwind status
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge
```

The POC deliberately does **not** start or stop graphical windows. Continue
with the independent Konsole/Bash/SSH process survival checks below.

## Native verification (maintainer only, **opt-in**, non-production account/session)

1. Use `rc-service -U` from an ordinary logged-in KDE/elogind graphical session.
   Confirm `id -u` is not `0`; `echo "$XDG_RUNTIME_DIR"`; `echo "$DBUS_SESSION_BUS_ADDRESS"`;
   `qdbus6 org.kde.KWin /KWin org.kde.KWin.supportInformation` where available.
   Record OpenRC/Gentoo versions and backend (`XDG_SESSION_TYPE`). Verify that
   `rc-service -U --help` works before modifying any files. Run the optional
   `tools/joetoo-kwind-configure-openrc-user --apply` before starting the service,
   unless you have already configured the equivalent allowlist.
2. Do not overwrite an existing `joetoo-kwind` service or POC. In an isolated
   test account, from this candidate directory, install to *user-owned*
   paths only. No `sudo`, automatic runlevel addition or system service:

   ```sh
   joetoo_install_poc() {
       svcdir="${XDG_CONFIG_HOME:-$HOME/.config}/rc/init.d"
       test ! -e "$svcdir/joetoo-kwind" || { echo 'Service already exists'; return 1; }
       test ! -e "$HOME/.local/libexec/joetoo-kwind" || { echo 'Daemon already exists'; return 1; }
       install -D -m 0755 user-init.d/joetoo-kwind "$svcdir/joetoo-kwind" || return
       install -D -m 0755 libexec/joetoo-kwind "$HOME/.local/libexec/joetoo-kwind" || return
       export JOETOO_KWIND_EXEC="$HOME/.local/libexec/joetoo-kwind"
       rc-service -U joetoo-kwind start
   }
   joetoo_install_poc
   ```

   The `JOETOO_KWIND_EXEC` override is a **prototype-only** convenience; the
   eventual package uses `/usr/libexec/joetoo-kwind`. If installed OpenRC does
   not pass exported variables to the service, specify the absolute executable
   in the user-owned service copy and record that adaptation. Stop the user
   service before removing these POC files.

3. Record exact existing independent Konsole/Bash/SSH PIDs (if none, make a
   harmless terminal, with an SSH test connection only to a host of your choice).
   Check `ps -o pid,ppid,pgid,sid,stat,args -p PID,...`; record cgroup paths from
   `/proc/PID/cgroup`. **Do not run any broad kill command.**
4. `rc-service -U joetoo-kwind start`; check `rc-service -U joetoo-kwind status`.
   Query broker responsiveness with
   `qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge`.
   Confirm that the registered session bus is the intended desktop session.
5. `rc-service -U joetoo-kwind stop`; ensure the *same exact* Konsole/Bash/SSH
   PIDs remain present, responsive, and their SSH connection is still usable.
   Compare `/proc/PID/cgroup` and PID identities, not merely process names.
6. `rc-service -U joetoo-kwind start`; `rc-service -U joetoo-kwind restart`;
   re-verify those exact PIDs/connections. Repeated stop/start/restart must be
   idempotent. Broker may forget the POC's single in-flight transaction;
   managed-window registry recovery is explicitly **not** implemented yet.
7. Test supervised **broker-only** failure with an isolated, recorded broker PID
   and confirm that `supervise-daemon` respawns it within the configured limits.
   Never target a Konsole/SSH PID and never kill an entire process group.
   Verify correct user bus and no duplicate D-Bus-name registration after respawn.
8. Repeat these checks on both X11 and Wayland (representative joetoo hosts).
   Observe any differences in OpenRC cgroups, session bus, Python signal delivery,
   and graphical-session teardown. A service marked `started` is not proof the
   resident JavaScript is running; that integration is milestone **1.2b**.

## Release gate / remaining risks

Do not conclude that this prototype is production ready until the maintainer
confirms the actual installed OpenRC version supports user services, confirms
session-bus availability and signal/shutdown behavior, and verifies independent
Konsole/SSH process survival through ordinary stop/restart and broker crash.
OpenRC `rc_cgroup_cleanup=NO` may protect cgroup cleanup, but native behavior
and process ancestry still require testing. A separate, correctly initialized
KWin resident script is milestone 1.2b, not an automatic consequence of daemon
startup. File locations are proposed package installation targets, not actual
installed files.

Sources: upstream OpenRC user-guide.md, service-script-guide.md,
supervise-daemon-guide.md, and OpenRC rc.conf cgroup cleanup policy;
`joetoo-ai` Step 0 launch/SSH POC README and project ARCHITECTURE.md.
