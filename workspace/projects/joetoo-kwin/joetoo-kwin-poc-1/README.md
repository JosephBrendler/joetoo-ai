# Joetoo resident KWin D-Bus proof of concept

This is an **experimental**, manually started proof of concept for a KWin 6 user session. It has not been tested in a live KWin session by the author of this response. Do not install it fleet-wide yet.

## Files

- `joetoo-kwin-broker.py`: user-session D-Bus broker (one pending request)
- `joetoo-kwin-resident.js`: resident KWin JavaScript callback
- `joetoo-kwin`: Bash command (uses `/usr/sbin/script_header_joetoo` and `isint()`)

## Dependencies

In the same Python interpreter that starts the broker, require `dbus-python` and `PyGObject`, plus `qdbus6` for the Bash side. On Gentoo, inspect `dev-python/dbus-python` and `dev-python/pygobject` before installing anything.

```sh
python3 -c 'import dbus; from gi.repository import GLib; print("ready")'
```

## Run (as joe inside Plasma, never sudo)

Terminal A:

```sh
cd ~/scratch
python3 ./joetoo-kwin-broker.py
```

Terminal B:

```sh
cd ~/scratch
js="$PWD/joetoo-kwin-resident.js"
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript joetoo-bridge >/dev/null 2>&1 || :
id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$js" joetoo-bridge)
[[ $id =~ ^[0-9]+$ ]] || { echo "bad script id: $id"; exit 1; }
qdbus6 org.kde.KWin "/Scripting/Script$id" org.kde.kwin.Script.run
qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.shortcutNames | grep -Fx joetoo_bridge_move
```

With the target Konsole active in terminal B, run:

```sh
./joetoo-kwin move 3 100 80 850 700
```

The client polls for a result and reports the window's *read-back* geometry. Use a non-maximized, non-tiled window, and ensure desktop 3 exists. This initial prototype is single-flight only and operates on whichever window is active **when the shortcut callback is triggered**. It should not yet be used by the concurrent SSH-window launcher.

## Teardown

```sh
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript joetoo-bridge
```

Stop terminal A with Ctrl+C.

## Limitations

- The broker must stay running and is scoped to the user's session bus.
- No automatic service/session startup yet.
- Only one outstanding request; concurrent calls are rejected until previous request finishes or becomes stale after ten seconds.
- The KWin async D-Bus callback does not receive a notification for a failed remote call; if broker calls fail, the caller will time out.
- `OK` means the KWin geometry properties matched immediately after the assignment. It does not prove that the application will retain the same geometry later.
- Input validation is intentionally narrow for an initial test.
