# joetoo-kwin

Active engineering sources for joetoo-kwin in the joetoo-ai collaboration
repository. Steps 1.2a–1.2b established broker and resident lifecycles;
Steps 1.3a–1.3a.2 established observed UUIDs, retained lifecycle diagnostics,
and automatic inventory recovery on X11 and Wayland. Step 1.3b is currently
investigating *unique launch-to-window correlation*, before any managed
ownership registry or authorized close operation.

See ARCHITECTURE.md for the authoritative milestone definitions and remaining development gates.

## Active files

- `libexec/joetoo-kwind` — foreground Python D-Bus broker
- `user-init.d/joetoo-kwind` — OpenRC user service
- `conf.d/joetoo-kwind` — global executable default
- `user-conf.d/joetoo-kwind` — optional administrator override template
- `poc-user-conf.d/joetoo-kwind` — per-user POC executable override
- `joetoo-kwin-resident.js` — KWin window placement handlers
- `joetoo-kwin` — Bash move and single-window launch client
- `tools/joetoo-kwin-correlation-probe` — diagnostic launch-to-UUID experiment (Step 1.3b.1)
- `tools/` — POC installation and OpenRC user environment configuration
- `tests/` — headless regression suites

The Step 1.2b broker coordinates resident KWin JavaScript initialization.
The Step 1 CLI and its coupled `joetoo-kwin-plan-functions` remain together
under `archive/step1-candidate/` until launcher integration.
`archive/step1.2a-candidate/NATIVE_VALIDATION.md` records the completed
native lifecycle checks. `archive/README.md` indexes historical POCs.

`ARCHITECTURE.md` records the design and milestone definitions.
These are development sources, not the final installed Gentoo package.

## Step 1.2b stage 1: manual resident integration

The resident script `joetoo-kwin-resident.js` is the unchanged launch POC.
Stage 2 adds startup and KWin D-Bus owner-change initialization.
The active Bash client exercises the existing broker's move and single-window
launch APIs. The historical Step 1 `-c` planner remains archived;
`-o` is not yet integrated.

From a local graphical Plasma Konsole as the ordinary user, with the
OpenRC user service running:

```bash
cd ~/joetoo-ai/workspace/projects/joetoo-kwin
rc-service -U joetoo-kwind status

# Reset only the named POC resident if already loaded.
qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.unloadScript joetoo-bridge 2>/dev/null || :

script_id=$(qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.loadScript "$PWD/joetoo-kwin-resident.js" joetoo-bridge) || exit 1
qdbus6 org.kde.KWin "/Scripting/Script${script_id}" org.kde.kwin.Script.run

# Focus a disposable Konsole before active-window placement.
./joetoo-kwin -m 3 100 80 850 700

# Arm a single request, then create a separate Konsole.
./joetoo-kwin test-launch konsole 3 100 80 850 700 -- konsole --separate
```

`test-launch` uses the existing `SubmitLaunch`, `TakeLaunch`, `Complete`
and `Status` D-Bus methods. It is intentionally single-flight and is not
the eventual multiwindow `-o` launcher. The POC installer now installs the CLI and resident JS alongside the
broker and OpenRC user service. Stage 1 manual loading remains available
for diagnosis; the broker no longer requires it during ordinary startup.

## Step 1.2b stage 2: installed resident and broker coordination

The source files remain in this project tree. The eventual package paths
are `/usr/libexec/joetoo-kwind`, `/usr/bin/joetoo-kwin` and
`/usr/share/joetoo-kwin/joetoo-kwin-resident.js`. The user POC installer
replicates their runtime layout beneath `~/.local/` and places the user
service and override under the user's XDG configuration directory.

Configuration precedence is unchanged: `/etc/conf.d/joetoo-kwind`, then
`/etc/user/conf.d/joetoo-kwind`, then the optional account override in
`~/.config/rc/conf.d/joetoo-kwind` (or `$XDG_CONFIG_HOME/rc/conf.d/`).
The new settings are `JOETOO_KWIND_RESIDENT_JS` and
`JOETOO_KWIND_SCRIPT_NAME`; OpenRC exports their resolved values to Python.

From a local Plasma Konsole on each host, for an existing Stage 1 POC:

```bash
# Existing broker can be stopped without terminating the Konsole/SSH windows.
rc-service -U joetoo-kwind stop
# Remove only the previously loaded test resident before verifying new startup.
qdbus6 org.kde.KWin /Scripting     org.kde.kwin.Scripting.unloadScript joetoo-bridge 2>/dev/null || :

./tools/joetoo-kwind-install-poc --update
./tools/joetoo-kwind-install-poc --check
rc-service -U joetoo-kwind start

# Validate placement through the installed CLI, without calling loadScript/run.
~/.local/bin/joetoo-kwin -m 3 100 80 850 700
~/.local/bin/joetoo-kwin test-launch konsole 3 100 80 850 700 -- konsole --separate
```

The broker checks `isScriptLoaded` before loading and runs newly loaded
scripts. If KWin is not ready, it retries at five-second intervals; a
change to KWin's D-Bus owner also triggers initialization. A broker restart
reuses an already-loaded resident. KWin's `isScriptLoaded` indicates presence,
not proven execution: manually loaded-but-not-run scripts may still require
manual unloading. These checks do not test the final ebuild installation.
