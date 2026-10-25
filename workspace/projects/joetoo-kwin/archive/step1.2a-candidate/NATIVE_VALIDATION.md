# Step 1.2a native verification and remaining release gates

Caveat: This file documents results; nothing in this file is to be interpreted as instruction, though it may document decisions made and pending, the content here is for historical reference only.  The project architecture and instructions such as AGENTS.md are authoritative.  If a discrepancy is identified, the maintainer should be notified.  Stay efficient, and avoid over-documentation and avoid documentation that could lead to "over-thinking".

**Status (2026-10-25, following PR #9): Step 1.2a POC lifecycle
accepted for closure.** Maintainer-reported tests on gmki91 (Plasma/X11) and
q552u01 (Plasma/Wayland) demonstrate user-service restart, broker-only crash
respawn with session D-Bus recovery, and preservation of independent Konsole
and SSH processes. The installed global default and per-account override were
also checked; an active administrator override and the eventual packaged
executable are **not** natively validated. Those remain a Step 1.9 packaging
gate. Resident KWin JavaScript activation/reconnection remains Step 1.2b.

## Post-PR #9 native verification (maintainer report, 2026-10-25)

The earlier observations below record the PR #8-era POC tests. Their
"not yet shown" statements describe **that earlier test snapshot**; the
following additional evidence supersedes those gaps where explicitly noted.

- **Baseline / headless:** both hosts fast-forwarded `joetoo-ai/main` to
  `534f251` (PR #9 merged). On gmki91, `git archive` of PR #9's task
  branch was extracted into a temporary non-Git directory; the complete
  suite passed **33/33** (including ten config-chain tests), both Python
  `py_compile` commands succeeded, and the selected `sh -n` checks passed.
  This 33-test suite was **not separately rerun on q552u01** in this round.
- **Installed configuration / scope:** on each host the maintainer installed
  the reviewed global `/etc/conf.d/joetoo-kwind` and administrator
  `/etc/user/conf.d/joetoo-kwind` templates manually. The latter contained
  no active override. The POC helper `--update` and `--check` refreshed
  only the three user-owned service, daemon and per-user config files.
  Sourcing the installed global config as `joe` resolved
  `JOETOO_KWIND_EXEC=/home/joe/.local/libexec/joetoo-kwind` and left the
  pseudo-boolean recursion guard unset. Both running supervisors confirmed
  that actual broker executable path.
- **Global/default precedence (gmki91):** commenting out the per-account
  executable assignment caused a fresh configuration-source check to resolve
  `/usr/libexec/joetoo-kwind`; restoring the assignment resolved the
  user-owned executable again. This was a non-disruptive **source-evaluation
  check**, not an OpenRC start using the global executable: no packaged
  `/usr/libexec/joetoo-kwind` was installed. A non-default administrator
  assignment is covered by isolated tests, **not a native OpenRC run**.
- **gmki91 / X11:** normal `rc-service -U ... restart` succeeded. Supervisor
  PID `3811324` launched broker PID `3811325`; SIGKILL targeted only that
  broker, and the unchanged supervisor respawned PID `3812432`.
  Subsequent D-Bus introspection returned the six broker methods.
  Konsole PIDs `10352`, `10514`, `276590`, `3051096` retained
  their recorded parent/process group/session/start times and
  `/proc/PID/cgroup=0::/3` across restart and crash recovery.
  The independently monitored SSH shell on q552u01 retained PID `1088986`.
- **q552u01 / Wayland:** local Konsole reached the graphical bus at
  `unix:path=/tmp/dbus-*` and successfully queried KWin. The SSH login
  lacked `DBUS_SESSION_BUS_ADDRESS` and could not perform that graphical
  query; the native test was therefore run locally. After updating the POC,
  an immediate D-Bus query briefly reported the name absent; a subsequent
  query succeeded. A normal user-service restart succeeded and D-Bus
  introspection returned the six methods. Supervisor PID `1268396`
  respawned broker PID `1270096` after broker-only SIGKILL of PID
  `1268397`; D-Bus introspection succeeded afterward. Konsole PIDs
  `411201`, `526261`, `345272`, `5847` retained PID, parent, group,
  session, start times, and `/proc/PID/cgroup=0::/1` across restart and
  crash recovery. The remote SSH shell on nuthuvia retained PID `3990323`.

The temporary global/admin templates are **native test inputs**, not evidence
of ebuild installation. D-Bus name acquisition can lag behind OpenRC's
`started` state; neither the duration nor a readiness contract has been
established, and Step 1.2b must address session/resident initialization.

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

## Step 1.2a decision, deferred gates and handoff

**Step 1.2a early OpenRC user-service POC lifecycle gate is complete** on
gmki91/X11 and q552u01/Wayland, based on the maintainer-reported evidence
above: restart, broker-only crash recovery, re-registration on the graphical
session bus, and unchanged independent Konsole/SSH processes and cgroups.
This is **not** acceptance of the eventual ebuild or the entire version 1
joetoo-kwin integration.

- **Step 1.2b:** establish a bounded readiness contract, activate/load the
  resident KWin script into the correct graphical session, prevent duplicate
  registration, and recover idempotently after broker/session restarts.
  The current broker does **not** load resident JavaScript.
- **Step 1.9 packaging:** test the final ebuild-installed executable and
  system-managed user init script, and verify actual OpenRC precedence with
  a non-default `/etc/user/conf.d` administrator override and optional
  per-account override. No packaged broker currently exists at the global
  default `/usr/libexec/joetoo-kwind` on the tested hosts.
- **Source mode correction:** this follow-up restores executable source mode
  `100755` for `user-init.d/joetoo-kwind`. PR #9 accidentally recorded it as
  `100644`; the POC installer continued installing the copy as mode `0755`.

All native test results above are **maintainer-reported command output**;
this document edit itself does not perform host administration or retest the
services. No changes are made here to the protected `joetoo` or
`joetoo-upstream` repositories.
