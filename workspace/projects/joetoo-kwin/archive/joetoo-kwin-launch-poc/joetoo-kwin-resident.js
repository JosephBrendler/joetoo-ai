// joetoo-kwin-resident.js
// Resident KWin 6: move the active window OR place a newly created window.
const BRIDGE = "org.joetoo.KWinBridge";
const PATH = "/org/joetoo/KWinBridge";

function finish(request, result, detail) {
    callDBus(BRIDGE, PATH, BRIDGE, "Complete",
             request.id, result, String(detail));
}

function desktopNumber(win) {
    if (win.onAllDesktops) return "all";
    if (!win.desktops || !win.desktops.length) return "none";
    return win.desktops[0].x11DesktopNumber;
}

function geometryText(win) {
    const g = win.frameGeometry;
    return "[" + desktopNumber(win) + "] (" + g.x + "," + g.y + ") " +
           g.width + "x" + g.height;
}

function placeWindow(win, request, operation) {
    if (!win || win.deleted) {
        finish(request, "ERROR", "Window disappeared before placement");
        return;
    }
    const desktop = workspace.desktops[request.desktop - 1];
    if (!desktop) {
        finish(request, "ERROR", "Virtual desktop " + request.desktop +
               " does not exist");
        return;
    }

    try {
        const beforeText = geometryText(win);
        const wasTiled = win.tile !== null;
        const wasFullscreen = win.fullScreen;

        win.desktops = [desktop];
        win.frameGeometry = {
            x: request.x, y: request.y,
            width: request.width, height: request.height
        };

        // Immediate KWin readback; Wayland clients can settle asynchronously.
        const afterText = geometryText(win);
        const g = win.frameGeometry;
        const match = desktopNumber(win) === request.desktop &&
                      g.x === request.x && g.y === request.y &&
                      g.width === request.width && g.height === request.height;
        finish(request, match ? "OK" : "ERROR",
               operation + ": " + win.caption + " (pid=" + win.pid + ")\n" +
               " before=" + beforeText + "\n" +
               " after=" + afterText + "\n" +
               " tiled=" + wasTiled + " fullscreen=" + wasFullscreen +
               (match ? "" : " (desktop/geometry differs from request)"));
    } catch (err) {
        finish(request, "ERROR", "KWin operation failed: " + err);
    }
}

// The original working active-window path remains available.
function moveFromBroker() {
    const win = workspace.activeWindow; // Capture before asynchronous D-Bus call.
    callDBus(BRIDGE, PATH, BRIDGE, "Take", function(payload) {
        if (!payload) return;
        let request;
        try { request = JSON.parse(payload); }
        catch (err) { console.warn("joetoo: malformed move payload: " + err); return; }
        placeWindow(win, request, "move");
    });
}

// New path: KWin tells us WHICH window has just been added.
workspace.windowAdded.connect(function(win) {
    if (!win || !win.normalWindow) return; // Ignore panels, tooltips, etc.
    const resourceClass = String(win.resourceClass || "");
    const desktopFile = String(win.desktopFileName || "");

    // Broker only returns a request if we armed one for this application.
    callDBus(BRIDGE, PATH, BRIDGE, "TakeLaunch",
             resourceClass, desktopFile, function(payload) {
        if (!payload) return;
        let request;
        try { request = JSON.parse(payload); }
        catch (err) { console.warn("joetoo: malformed launch payload: " + err); return; }
        placeWindow(win, request, "launch");
    });
});

registerShortcut("joetoo_bridge_move", "Joetoo brokered move", "", moveFromBroker);
