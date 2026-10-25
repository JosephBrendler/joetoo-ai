# joetoo-kwin Step 1.2a — OpenRC supervision candidate

**Status:** isolated POC candidate; gmki91/X11 and q552u01/Wayland user-service startup have been reported by maintainer. Stop/restart safety remains unverified. Read
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
- `tools/joetoo-kwind-configure-openrc-user` -> opt-in literal OpenRC allowlist editor
- `tools/joetoo-kwind-install-poc` -> installs **both** service and daemon, creates parent directories
- `tests/test_openrc_user_setup.py` -> configuration and complete-install regression checks

**No** system-level `/etc/init.d/joetoo-kwind` service and **no** root user mode.
`rc-service -U` must run in a valid graphical user session with
`XDG_RUNTIME_DIR` set; DBus can be addressed by `DBUS_SESSION_BUS_ADDRESS` or
an existing `$XDG_RUNTIME_DIR/bus` socket. On both tested hosts, the session
D-Bus address instead uses `/tmp/dbus-*`, so OpenRC must pass the existing
`DBUS_SESSION_BUS_ADDRESS` via `rc_env_allow`. The service refuses root or a
runtime directory owned by another UID.

Use default OpenRC start/stop/status with `supervisor=supervise-daemon`, foreground
process, and throttled respawn (10/5/120, patterned after joetoo DDNS).
`rc_cgroup_cleanup=NO` is an intentional protective override; the daemon does
not launch applications or execute process-group termination. `pidfile` is
private runtime state for the **supervisor**, not the application.

## Headless checks (safe on a development machine)

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile libexec/joetoo-kwind
python3 -m py_compile tools/joetoo-kwind-configure-openrc-user
sh -n tools/joetoo-kwind-install-poc
sh -n user-init.d/joetoo-kwind
```

The unit tests stub dbus and GLib; they do **not** exercise actual OpenRC,
Python D-Bus bindings, PyGObject, compositor/session selection or POSIX
process/cgroup semantics. A passing suite cannot establish lifecycle safety.

## What native testing found (gmki91 X11 and q552u01 Wayland)

The maintainer confirmed that both Plasma desktops expose working session D-Bus
addresses under `/tmp/dbus-*`, not `$XDG_RUNTIME_DIR/bus`. `qdbus6` reached KWin
on both. On gmki91 and q552u01, a **literal** OpenRC user `rc.conf` assignment:

```sh
rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"
```

allowed `rc-service -U joetoo-kwind start` to proceed on each machine. The
original follow-up helper generated `case` statements inside `rc.conf`; these
did **not** work with OpenRC's configuration loading. Do not reinstall those
statements. This repair replaces them with one literal assignment and tests
that exact behavior. `JOETOO_KWIND_EXEC` is temporary for the POC; packaged
installation with the default executable path should need only
`DBUS_SESSION_BUS_ADDRESS`.

The helper retains other existing literal allowlist entries, refuses arbitrary
shell expressions or duplicate assignments rather than guessing, and can
migrate **exactly** the broken managed block produced by the earlier candidate.
It refuses modified or incomplete blocks and symlinked configuration paths.
Its `--check` operation does not modify any file; `--apply` is opt-in. Check the
real resolved path in the helper's output. The helper handles XDG_CONFIG_HOME
or falls back to HOME/.config, avoiding manual path construction.

Running these helpers over SSH under the target user can configure files, but
the **service must be started from a shell attached to that host's Plasma
session** with its own `DBUS_SESSION_BUS_ADDRESS` exported. The XDG_SESSION_TYPE
value `tty` can be correct for a Plasma session started from a TTY.

## Complete POC installation (ordinary user, no sudo)

From this `step1.2a-candidate` directory on the target host, first run the
headless checks above. The installer uses `install -D` and creates the missing
`~/.config/rc/init.d` and `~/.local/libexec` directories **without** any `mkdir`
commands from the user. It also checks/applies the OpenRC allowlist with the
fixed helper. Nothing starts automatically.

### Fresh test installation

```sh
tools/joetoo-kwind-install-poc --check
tools/joetoo-kwind-install-poc --install
```

The first command reports what is missing (and exits nonzero if setup is
incomplete). The second installs both files and updates the user rc.conf.
`--install` refuses to overwrite an existing destination.

### Updating the POC already installed on gmki91 or q552u01

From a **local Konsole on the target Plasma desktop**:

```sh
rc-service -U joetoo-kwind stop
tools/joetoo-kwind-install-poc --update
tools/joetoo-kwind-install-poc --check
```

`--update` refuses to proceed if OpenRC reports the service as running. It
preserves installed service/daemon copies with dated, PID-suffixed backups
before replacing them. It updates the user rc.conf only through the literal
allowlist editor. It never terminates Konsole, Bash or SSH sessions.

### Start and verify on that host's own graphical session

```sh
export JOETOO_KWIND_EXEC="$HOME/.local/libexec/joetoo-kwind"
printf 'Graphical bus: %s\n' "$DBUS_SESSION_BUS_ADDRESS"
qdbus6 org.kde.KWin /KWin org.kde.KWin.currentDesktop
rc-service -U joetoo-kwind start
rc-service -U joetoo-kwind status
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge
```

Expect the bridge's six existing methods. If the bus environment is missing,
do **not** start a new bus via `dbus-launch`; use Konsole under Plasma on that
machine. The installer never changes system `/etc/rc.conf`, never uses root,
and never invokes a service start/stop/restart automatically.

## Native lifecycle verification (maintainer only, separate from installation)

1. Record exact existing independent Konsole/Bash/SSH PIDs (if none, make a
   harmless terminal, with an SSH test connection only to a host of your choice).
   Check `ps -o pid,ppid,pgid,sid,stat,args -p PID,...`; record cgroup paths from
   `/proc/PID/cgroup`. **Do not run any broad kill command.**
2. `rc-service -U joetoo-kwind start`; check `rc-service -U joetoo-kwind status`.
   Query broker responsiveness with
   `qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge`.
   Confirm that the registered session bus is the intended desktop session.
3. `rc-service -U joetoo-kwind stop`; ensure the *same exact* Konsole/Bash/SSH
   PIDs remain present, responsive, and their SSH connection is still usable.
   Compare `/proc/PID/cgroup` and PID identities, not merely process names.
4. `rc-service -U joetoo-kwind start`; `rc-service -U joetoo-kwind restart`;
   re-verify those exact PIDs/connections. Repeated stop/start/restart must be
   idempotent. Broker may forget the POC's single in-flight transaction;
   managed-window registry recovery is explicitly **not** implemented yet.
5. Test supervised **broker-only** failure with an isolated, recorded broker PID
   and confirm that `supervise-daemon` respawns it within the configured limits.
   Never target a Konsole/SSH PID and never kill an entire process group.
   Verify correct user bus and no duplicate D-Bus-name registration after respawn.
6. Repeat these checks on both X11 and Wayland (representative joetoo hosts).
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
