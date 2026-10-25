# Step 1.2a native verification and remaining release gates

**Status (2026-10-25):** the maintainer's headless and native observations
support the **user-owned Step 1.2a OpenRC POC lifecycle** on gmki91 (reported
Plasma/X11) and q552u01 (Plasma/Wayland). The packaged global/user OpenRC
configuration precedence remains **untested**. This is not a packaged release
or evidence that the later resident KWin JavaScript is running.

## Baseline and headless checks

- Tested repository baseline on each host: `joetoo-ai/main` at `3fd2e6e`
  (merge of PR #7); tests were run by the maintainer on 2026-10-25.
- `python3 -m unittest discover -s tests -p 'test_*.py' -v`:
  **23/23 passed** on gmki91 (0.716 s) and q552u01 (1.420 s).
- Both Python `py_compile` checks and the installer/service `sh -n` checks
  completed successfully on both hosts.
- With `rc-service -U joetoo-kwind` stopped, the ordinary-user
  `tools/joetoo-kwind-install-poc --update` completed successfully on each
  host; `--check` then reported the service, daemon, per-user override, and
  OpenRC environment allowlist current. Backups were reported for the two
  previously installed files. The helper did not start the service.

Headless tests mock the broker's D-Bus/GLib behavior. They do not establish
OpenRC lifecycle behavior, real D-Bus ownership, compositor integration,
packaged configuration precedence, or application process survival.

## Native POC observations: gmki91 (reported Plasma/X11)

- The shell reported `XDG_SESSION_TYPE=tty`, but had a working graphical
  session bus at a `/tmp/dbus-*` address; `qdbus6` queried KWin successfully.
- OpenRC's non-root `supervise-daemon` PID `3355545` owned Python broker PID
  `3355546`, which executed `/home/joe/.local/libexec/joetoo-kwind`.
  `/proc/3355546/environ` contained the session's `DBUS_SESSION_BUS_ADDRESS`;
  its recorded cgroup was `0::/3`. The six `org.joetoo.KWinBridge` methods
  were visible by D-Bus introspection after normal service startup.
- The maintainer performed ordinary `stop`, `start`, and `restart` operations.
  The original Konsole PIDs `10352`, `10514`, `276590`, `3051096` and SSH PID
  `3052866` survived with the same recorded start times. The old broker PID
  disappeared on stop and a different broker PID appeared after startup.
- After an ordinary restart, supervisor PID `3373510` supervised broker PID
  `3373511`. The maintainer sent **SIGKILL to this broker PID only**. The
  supervisor survived and respawned broker PID `3381588` with PPID `3373510`.
  The same four Konsole PIDs and SSH PID were present after the termination.
- **Not yet shown:** a fresh D-Bus introspection of the replacement broker
  *after that specific SIGKILL*, or before/after application cgroup comparisons.

## Native POC observations: q552u01 (Plasma/Wayland)

- `XDG_SESSION_TYPE=wayland`. The graphical session bus had a `/tmp/dbus-*`
  address. Broker PID `1165383` ran the intended user-owned executable,
  inherited the matching session bus address, and reported cgroup `0::/1`.
- The OpenRC user service stopped and started successfully. A `qdbus6` query
  issued **immediately** after startup twice reported
  `Service 'org.joetoo.KWinBridge' does not exist`, despite OpenRC reporting
  `started` and a Python broker process being visible. This indicates a
  **possible readiness race**, not a demonstrated permanent registration fault;
  startup latency and cause were not measured.
- After subsequent restart, supervisor PID `1165626` supervised broker PID
  `1165627`. The maintainer sent **SIGKILL to the broker only**; the same
  supervisor respawned broker PID `1165905` (PPID `1165626`). A later
  `qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge` successfully listed
  the six expected broker methods, **confirming D-Bus registration after
  supervised recovery**.
- An ordinary `rc-service -U joetoo-kwind restart` then succeeded. The
  original Konsole PIDs `5847`, `345272`, `411201`, `526261`, interactive
  Bash PID `526289`, and SSH PIDs `1121323`, `1163457` remained present
  afterward with unchanged recorded start times. Independently, the remote
  gmki91 shell continued to respond with the same Bash PID `3382953`
  before and after the broker-termination experiment.
- **Not yet shown:** a separate D-Bus introspection *immediately following
  the final explicit OpenRC restart*, or before/after application cgroup
  comparisons. The older gmki91 PIDs mistakenly used in an early q552u01
  `ps -p` command provided no q552u01 process-survival evidence; the later
  correctly selected q552u01 PIDs supplied that evidence.

## Configuration scope and what has actually been verified

The POC `--update` installer manages three **user-owned** files only:

1. `$XDG_CONFIG_HOME/rc/init.d/joetoo-kwind` (user service);
2. `$HOME/.local/libexec/joetoo-kwind` (Python broker);
3. `$XDG_CONFIG_HOME/rc/conf.d/joetoo-kwind` (explicit per-user override).

On both hosts, the observed running executable path was
`/home/joe/.local/libexec/joetoo-kwind`, and the actual graphical
`DBUS_SESSION_BUS_ADDRESS` reached the Python broker through the OpenRC
user-service environment. The installed override was checked for matching
content. These observations **validate the effective POC user executable
path**, but do not independently prove every possible source of that value.

The eventual **system package** is designed to install four system-managed
files: the Python broker in `/usr/libexec/`, the OpenRC **user** service in
`/etc/user/init.d/`, and these two configuration templates (neither is
installed by the POC helper):

- `/etc/conf.d/joetoo-kwind` — authoritative global executable default;
- `/etc/user/conf.d/joetoo-kwind` — in the **previous validated candidate**,
  a bridge sourcing the global file. The **proposed new config-chain draft**
  replaces this with an optional administrator override; the OpenRC service
  explicitly sources `/etc/conf.d/joetoo-kwind`, which then loads later layers.

The optional `$XDG_CONFIG_HOME/rc/conf.d/joetoo-kwind` user override is a
**separate, fifth location**, installed by the POC helper for testing but
not mandatory in a future system package. OpenRC's upstream user-service
documentation describes user `conf.d` settings overriding `/etc/user/conf.d`.
The earlier bridge-based design connected these files; the proposed new
global-first chain makes the order explicit. It also adds a joetoo canonical
pseudo-boolean reentrancy guard and validates HOME/XDG_CONFIG_HOME on startup
to prevent unintended lookups under `/.config`. The existing supervisor
PID file and respawn parameters remain unchanged. See the source loader at
<https://github.com/OpenRC/openrc/blob/master/sh/openrc-run.sh.in>.

The old bridge-based source ordering was exercised in a headless simulation,
not tested natively with both system templates installed. The subsequent
**explicit global-entry-point config chain is a new proposed change**; its
headless isolated tests do not establish the behavior of the actual installed
OpenRC service with packaged templates and per-account overrides. This is a
distinct
**packaging/configuration acceptance item** before adopting the hierarchy
system-wide (see the project's later packaging gate, Step 1.9); it need not
block acceptance of the already demonstrated **user-owned POC lifecycle**.

## Remaining checks and handoff

1. Confirm D-Bus introspection after the specific gmki91 supervised crash
   recovery and after q552u01's final explicit OpenRC restart, preferably
   with bounded readiness retries. If immediate queries fail but later ones
   work, measure time-to-ready and decide whether to add a readiness check
   when implementing Step 1.2b's resident/session initialization.
2. If strict cgroup-survival evidence is required, compare exact recorded
   Konsole/Bash/SSH `/proc/PID/cgroup` values before and after lifecycle
   operations, not just PIDs and start times. Do not use group-wide signals.
3. Keep packaged `/etc` configuration precedence testing separate from the
   current POC and verify it under the actual Gentoo/OpenRC user-service
   configuration loader before promoting the package layout.
4. After the outstanding checks, record the Step 1.2a milestone decision
   explicitly. Step 1.2b then addresses real KWin resident JavaScript
   activation/reconnection and idempotent bus/session initialization; the
   present broker **does not** load that resident JS.

All native test results above are **maintainer-reported command output**;
this document edit itself does not perform host administration or retest the
services. No changes are made here to the protected `joetoo` or
`joetoo-upstream` repositories.
