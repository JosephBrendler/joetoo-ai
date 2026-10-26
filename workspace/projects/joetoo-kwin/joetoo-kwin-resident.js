// joetoo-kwin-resident.js
// Resident KWin 6: move the active window OR place a newly created window.
//
// This JavaScript is loaded *inside KWin's scripting engine*. KWin supplies
// the global `workspace` object (window and desktop access), `callDBus`
// (asynchronous D-Bus client calls), and `registerShortcut` (a KWin action).
// It is NOT an independent Node.js program or a D-Bus service.
//
// The Python joetoo-kwind broker owns the methods at this D-Bus address.
// We request work from it and report placement results back to it.
// A D-Bus address combines a bus service name, an object path, an interface
// name, and finally the method being called. Here the service and interface
// happen to have the same text; that does not make them the same concept.
const BRIDGE = "org.joetoo.KWinBridge";
const PATH = "/org/joetoo/KWinBridge";

// Tell the broker whether this KWin operation succeeded.
// `request.id` identifies the *request*, not a particular window's KWin UUID.
// `String(detail)` converts error objects or other values to printable text.
// callDBus sends a message asynchronously; it does not block waiting for a
// completion reply here.
function finish(request, result, detail) {
    callDBus(BRIDGE, PATH, BRIDGE, "Complete",
             request.id, result, String(detail));
}

// Return a display-friendly virtual desktop number for a KWin window.
// The two strings handle special cases where a single desktop number cannot
// be reported. `x11DesktopNumber` is KWin's desktop-number property and is
// available through its scripting API even in the tested Wayland session.
function desktopNumber(win) {
    if (win.onAllDesktops) return "all";
    if (!win.desktops || !win.desktops.length) return "none";
    // Arrays are zero-indexed: desktops[0] is the first assigned desktop.
    return win.desktops[0].x11DesktopNumber;
}

// Format the assigned desktop and frame rectangle for CLI status messages.
// `frameGeometry` includes window decorations; x/y are the top-left corner.
function geometryText(win) {
    const g = win.frameGeometry;
    return "[" + desktopNumber(win) + "] (" + g.x + "," + g.y + ") " +
           g.width + "x" + g.height;
}

// Apply a previously accepted broker request to this specific KWin window.
// `win` is the KWin window object, `request` is the JSON object obtained from
// the broker, and `operation` is a label such as "move" or "launch".
// This changes the window's desktop *membership*; it does not explicitly
// switch the currently displayed virtual desktop.
function placeWindow(win, request, operation) {
    // `!win` rejects a missing object; `win.deleted` rejects a window already
    // removed while the asynchronous request was in flight.
    if (!win || win.deleted) {
        finish(request, "ERROR", "Window disappeared before placement");
        return;
    }
    // Broker requests use 1-based desktop numbers; JavaScript array indices
    // start at zero. A missing entry means that desktop was not configured.
    const desktop = workspace.desktops[request.desktop - 1];
    if (!desktop) {
        finish(request, "ERROR", "Virtual desktop " + request.desktop +
               " does not exist");
        return;
    }

    // The try/catch keeps a failed KWin API operation from silently leaving
    // the broker request pending until the Bash client's polling times out.
    try {
        const beforeText = geometryText(win);
        // Capture the pre-change state for the result message. These flags
        // describe the state observed, not a request to change it.
        const wasTiled = win.tile !== null;
        const wasFullscreen = win.fullScreen;

        // KWin accepts an array of virtual-desktop objects for `desktops`.
        // Assign the requested desktop, then assign the requested frame
        // rectangle (position and dimensions), both through KWin's API.
        win.desktops = [desktop];
        win.frameGeometry = {
            x: request.x, y: request.y,
            width: request.width, height: request.height
        };

        // Immediate KWin readback; Wayland clients can settle asynchronously.
        // This tests the *immediate* observed values only. It is not a promise
        // that no compositor/client adjustment will occur after this callback.
        const afterText = geometryText(win);
        const g = win.frameGeometry;
        // `===` means strict equality in JavaScript; `&&` requires every
        // desktop/coordinate/dimension comparison to agree with the request.
        const match = desktopNumber(win) === request.desktop &&
                      g.x === request.x && g.y === request.y &&
                      g.width === request.width && g.height === request.height;
        // The ternary `condition ? A : B` selects one of two strings.
        // Include before/after geometry so the CLI can show useful evidence.
        finish(request, match ? "OK" : "ERROR",
               operation + ": " + win.caption + " (pid=" + win.pid + ")\n" +
               " before=" + beforeText + "\n" +
               " after=" + afterText + "\n" +
               " tiled=" + wasTiled + " fullscreen=" + wasFullscreen +
               (match ? "" : " (desktop/geometry differs from request)"));
    } catch (err) {
        // Convert an exception into an explicit failed broker request.
        finish(request, "ERROR", "KWin operation failed: " + err);
    }
}

// The original working active-window path remains available.
// A call via KWin's registered shortcut reaches this function (not the
// Python broker's D-Bus method directly). The Bash CLI has *already* called
// Submit; "Take" retrieves that waiting move request from the broker.
function moveFromBroker() {
    // Save the currently focused window *before* starting the asynchronous
    // D-Bus call: focus could move to a different window before the callback.
    const win = workspace.activeWindow;
    // The final function argument is a callback, executed when the D-Bus
    // response arrives. An empty payload means there is nothing to move.
    callDBus(BRIDGE, PATH, BRIDGE, "Take", function(payload) {
        if (!payload) return;
        let request;
        // The broker sends JSON text, not an already constructed JS object.
        // Parsing may throw if the text is malformed; do not attempt to place
        // a window using an invalid request.
        try { request = JSON.parse(payload); }
        catch (err) { console.warn("joetoo: malformed move payload: " + err); return; }
        placeWindow(win, request, "move");
    });
}

// New-window path: KWin emits the `windowAdded` signal with the specific
// window object it just created. `.connect(function(win) { ... })` registers
// a callback; it does not call that function immediately.
//
// This proof-of-concept matches an armed launch by application class, not
// yet by an individual window UUID. It MUST NOT be used as ownership proof
// for eventual close/delete operations (Step 1.3b will strengthen matching).
workspace.windowAdded.connect(function(win) {
    if (!win || !win.normalWindow) return; // Ignore panels, tooltips, etc.
    // `|| ""` substitutes an empty string if KWin did not provide a value;
    // String(...) makes the D-Bus inputs consistently strings.
    const resourceClass = String(win.resourceClass || "");
    const desktopFile = String(win.desktopFileName || "");

    // Broker only returns a request if we armed one for this application.
    // The two class hints are passed to the Python TakeLaunch method, which
    // decides whether this new window matches the one pending launch request.
    callDBus(BRIDGE, PATH, BRIDGE, "TakeLaunch",
             resourceClass, desktopFile, function(payload) {
        if (!payload) return;
        let request;
        try { request = JSON.parse(payload); }
        catch (err) { console.warn("joetoo: malformed launch payload: " + err); return; }
        // `win` is captured from this particular windowAdded notification.
        // Another window becoming active does not change that reference.
        placeWindow(win, request, "launch");
    });
});

// Make a named KWin shortcut action available to kglobalaccel. Its first
// argument is the identifier used by the Bash CLI's invokeShortcut call;
// the second is a human-readable description. The empty shortcut string
// specifies no default key combination. KWin calls moveFromBroker when this
// action is invoked. There is no polling loop inside the resident script.
registerShortcut("joetoo_bridge_move", "Joetoo brokered move", "", moveFromBroker);
