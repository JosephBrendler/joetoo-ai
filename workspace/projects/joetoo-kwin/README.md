# joetoo-kwin

Active engineering sources for joetoo-kwin in the joetoo-ai collaboration
repository. Current milestone: Step 1.2b (KWin resident-script
initialization and reconnection). The Step 1.2a OpenRC user-service
lifecycle was validated on gmki91/X11 and q552u01/Wayland.

## Active files

- `libexec/joetoo-kwind` — foreground Python D-Bus broker
- `user-init.d/joetoo-kwind` — OpenRC user service
- `conf.d/joetoo-kwind` — global executable default
- `user-conf.d/joetoo-kwind` — optional administrator override template
- `poc-user-conf.d/joetoo-kwind` — per-user POC executable override
- `tools/` — POC installation and OpenRC user environment configuration
- `tests/` — Step 1.2a regression tests

The promoted broker does not yet activate resident KWin JavaScript.
The Step 1 CLI and its coupled `joetoo-kwin-plan-functions` remain together
under `archive/step1-candidate/` until launcher integration.
`archive/step1.2a-candidate/NATIVE_VALIDATION.md` records the completed
native lifecycle checks. `archive/README.md` indexes historical POCs.

`ARCHITECTURE.md` records the design and milestone definitions.
These are development sources, not the final installed Gentoo package.

## Step 1.2b stage 1: manual resident integration

The resident script `joetoo-kwin-resident.js` is the unchanged launch POC.
Automatic loading and recovery are not implemented at this stage.
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
the eventual multiwindow `-o` launcher. The POC installer does not install
this CLI or JS script; run them from the checkout. Test on gmki91/X11 and
q552u01/Wayland. Broker/OpenRC behavior remains unchanged.
