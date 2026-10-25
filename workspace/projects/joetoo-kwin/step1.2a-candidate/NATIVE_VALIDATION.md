# Step 1.2a native verification and remaining release gates

**Status:** documentation of previous maintainer observations; the new
executable-path configuration hierarchy has **not yet been verified natively**.

## Previously reported observations

- gmki91 (Plasma/X11) and q552u01 (Plasma/Wayland) have session D-Bus
  addresses of the `/tmp/dbus-*` form, rather than a session bus socket at
  `$XDG_RUNTIME_DIR/bus`.
- The maintainer reported `qdbus6` KWin connectivity on each host.
- On each host, literal `rc_env_allow` entries allowed the user OpenRC
  service to begin startup; OpenRC did not consume the earlier shell `case`
  expressions as expected.
- These observations are **not** evidence that restarting the broker safely
  preserves independently launched Konsole, Bash and SSH processes.

The isolated headless tests exercise the broker mock and installer contracts.
They cannot prove how a specific Gentoo OpenRC installation searches and
sources its configuration files or handles cgroups, stop/restart and respawn.

## Newly introduced configuration hierarchy — pending native tests

1. Confirm the packaged template path `/etc/conf.d/joetoo-kwind` is sourced
   through `/etc/user/conf.d/joetoo-kwind` in the installed OpenRC release.
2. Confirm a present `$XDG_CONFIG_HOME/rc/conf.d/joetoo-kwind` is loaded
   **after** the system bridge and its `JOETOO_KWIND_EXEC` assignment wins.
   Do not assume the configuration precedence solely from the headless
   simulated source-order test.
3. Confirm the user POC installer creates and checks three user-owned files
   and does not touch system configuration. Verify that `--update` preserves
   previous copies of all three, and the selected executable is the user path.
4. From a **local graphical Konsole**, confirm `DBUS_SESSION_BUS_ADDRESS`
   survives the OpenRC user environment allowlist into the daemon.
5. On both gmki91/X11 and q552u01/Wayland, record the exact unrelated
   Konsole/Bash/SSH PIDs and cgroups, then verify they survive service
   start/stop/restart and supervised broker respawn. Verify bus registration.
6. Confirm no application kill, process-group kill or unwanted cgroup cleanup.
   Do not perform broad kill commands. Use only a recorded broker PID for
   controlled supervised-failure tests.

No live host change, installation, stop/start/restart, or native validation is
performed by preparing this development candidate in `joetoo-ai`.
