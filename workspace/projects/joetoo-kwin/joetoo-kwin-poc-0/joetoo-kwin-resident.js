
//
// joetoo-kwin-resident.js
// Test persistent invocation through KDE global shortcuts.
//

function moveActiveWindow() {
    const win = workspace.activeWindow;
    const desktop = workspace.desktops[2];

    if (!win || !desktop) {
        console.warn("No active window or desktop 3");
        return;
    }

    const g = win.frameGeometry;

    win.desktops = [desktop];

    win.frameGeometry = {
        x: 100,
        y: 80,
        width: g.width,
        height: g.height
    };

    console.info("joetoo: moved " + win.caption);
}

// Register a callback without assigning a keyboard combination.
registerShortcut(
    "joetoo_test_move",
    "Joetoo test move window",
    "",
    moveActiveWindow
);
