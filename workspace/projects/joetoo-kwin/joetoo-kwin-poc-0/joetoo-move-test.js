// move a window - 3 KWin APIs do the work --
// workspace.activeWindow identifies the active window.
// win.desktops = [workspace.desktops[2]] assigns it to desktop 3 (zero-based array indexing).
// win.frameGeometry = Qt.rect(...) changes its position while preserving its size.

const x = 100;
const y = 80;

// assumes requested desktop already exists
const desktopNumber = 1;

const win = workspace.activeWindow;
const desktop = workspace.desktops[desktopNumber - 1];

if (!win) {
    print("No active window");
} else if (!desktop) {
    print("Desktop " + desktopNumber + " does not exist");
} else {
    // Move window to virtual desktop 3
    win.desktops = [desktop];

    // Preserve current size; change only position
    const g = win.frameGeometry;
    win.frameGeometry = Qt.rect(x, y, g.width, g.height);

    print("Moved " + win.caption +
          " to desktop " + desktopNumber +
          " at (" + x + "," + y + ")");
}
