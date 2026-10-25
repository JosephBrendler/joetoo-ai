# joetoo-kwin Step 1.2a — OpenRC supervision candidate

**Status:** isolated candidate; not installed, released or natively tested. Read
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

**No** system-level `/etc/init.d/joetoo-kwind` service and **no** root user mode.
`rc-service -U` must run in a valid graphical user session with
`XDG_RUNTIME_DIR` set; DBus can be addressed by `DBUS_SESSION_BUS_ADDRESS` or
an existing `$XDG_RUNTIME_DIR/bus` socket. The service refuses root and a
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
```

The unit tests stub dbus and GLib; they do **not** exercise actual OpenRC,
Python D-Bus bindings, PyGObject, compositor/session selection or POSIX
process/cgroup semantics. A passing suite cannot establish lifecycle safety.

## Native verification (maintainer only, **opt-in**, non-production account/session)

1. Use `rc-service -U` from an ordinary logged-in KDE/elogind graphical session.
   Confirm `id -u` is not `0`; `echo "$XDG_RUNTIME_DIR"`; `echo "$DBUS_SESSION_BUS_ADDRESS"`;
   `qdbus6 org.kde.KWin /KWin org.kde.KWin.supportInformation` where available.
   Record OpenRC/Gentoo versions and backend (`XDG_SESSION_TYPE`). Verify that
   `rc-service -U --help` works before modifying any files.
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
