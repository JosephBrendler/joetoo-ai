# joetoo KWin resident broker: new-window placement experiment

This updates the earlier working POC with a second operation, without removing `joetoo-kwin move`.
The **modified broker must be restarted** and the **resident JavaScript unloaded/reloaded** because new D-Bus methods and a `workspace.windowAdded` callback have been introduced.

## Files

- `joetoo-kwin-broker.py`: adds `SubmitLaunch` / `TakeLaunch` to existing `Submit` / `Take` / `Complete` / `Status` methods.
- `joetoo-kwin-resident.js`: adds a `windowAdded` listener, retains the existing named shortcut for active-window moves, and reports before/after desktop+geometry.
- `joetoo-kwin_launch_test_driver.sh`: declares `program=(konsole --separate)` and `expected_class=konsole`, arms requested placement, starts Konsole, and reports completion.
- `joetoo-kwin`: existing Bash `move` client, unchanged.

## Prerequisites

`python3 -c 'import dbus; from gi.repository import GLib'` and `qdbus6`. Run everything as `joe` within the active KWin graphical session, never root.

## Setup (test session)

1. In broker's Konsole: stop the **old** `joetoo-kwin-broker.py` with Ctrl+C. Restart using `python3 ./joetoo-kwin-broker.py` in this directory.
2. Unload old resident JS: `qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript joetoo-bridge`.
3. From this directory:

   ```sh
   id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$PWD/joetoo-kwin-resident.js" joetoo-bridge)
   qdbus6 org.kde.KWin "/Scripting/Script$id" org.kde.kwin.Script.run
   ```

4. From an existing Konsole on any desktop, run `./joetoo-kwin_launch_test_driver.sh`.
5. It should create a **new** Konsole window on desktop 3 at (100,80), 850×700. The calling window should remain unchanged.
6. Verify old path still works: from a selected Konsole, run `./joetoo-kwin move 1 100 80 850 700`.

## How the window is selected

The broker accepts exactly **one** pending launch request with a target application class. The resident KWin script waits for `workspace.windowAdded`, and asks the broker to match the new window's `resourceClass` or `desktopFileName`. An app with a different class is ignored. Konsole `--separate` is important to reliably create a separate process/window.

For another program, edit the `program=(...)` Bash array and `expected_class`. Not all programs use the executable's name as their window class. For example, test with `program=(some-app)` only after identifying its KWin class.

## Limitations / interpretation

- KWin script **reacts at `windowAdded`**, not a guaranteed pre-display / before-initial-map hook. A window can briefly appear on its default desktop first. For strictly invisible initial placement, investigate KWin window rules using **Apply Initially**.
- Matching only by application class is not sufficient if multiple windows of the same application are created simultaneously. The final SSH launcher needs **per-window tokens or IDs**, plus creation order, acknowledgment, and cleanup.
- Geometry readback is immediate. Under Wayland a client may resize asynchronously and the report may temporarily differ; do not treat one mismatch as an IPC failure.
- A launch request remains pending if no window with matching class appears. The 20-second stale-request guard prevents indefinite broker blocking on subsequent requests. Test launches one at a time.
- The broker service is user-session only, not an OpenRC service. Neither JavaScript nor the D-Bus request require root privileges.
