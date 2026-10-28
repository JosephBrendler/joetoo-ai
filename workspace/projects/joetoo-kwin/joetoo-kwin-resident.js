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
    // UUID is the identity of the exact window acted on, never an ownership
    // claim. The broker must cross-check it with positive managed correlation.
    const uuid = windowUUID(win);
    if (!uuid) {
        finish(request, "ERROR", "Target window has no KWin UUID");
        return;
    }
    try {
        const before = geometryText(win);
        const tiled = win.tile !== null;
        const fullscreen = win.fullScreen;
        // Wayland geometry can require a client configure/commit round-trip.
        // Assigning these properties is not proof they have already settled.
        win.desktops = [desktop];
        win.frameGeometry = {
            x: request.x, y: request.y,
            width: request.width, height: request.height
        };
        // The broker's existing window-observation event stream confirms the
        // final frame asynchronously, or times out if the client rejects it.
        // Do not return ERROR simply because an immediate readback is stale.
        finish(request, "VERIFY", JSON.stringify({
            window_uuid: uuid, operation: operation,
            before: before, immediate: geometryText(win),
            tiled: tiled, fullscreen: fullscreen
        }));
    } catch (err) {
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

// ------------------- Step 1.3a: observation, NOT ownership ------------------
// KWin knows which window exists, its application hints, desktop and geometry.
// It does NOT know whether a Konsole runs ssh_wrapper, distccmon-tui, etc.
// Those application-level launch recipes belong to a later milestone.
//
// Source/revision labels separate this KWin script instance from an older
// one and order its asynchronous D-Bus messages. They are NOT ownership proof
// or secure authentication tokens; they are diagnostic ordering metadata.
const observerSource = String(Date.now()) + "-" + Math.random().toString(36).slice(2);
let observerRevision = 0;

// Store plain snapshots keyed by KWin UUID. Unlike request IDs from the
// Python broker, internalId belongs to the WINDOW and lasts only as long as
// that KWin window does. No managed_id or permission to close is created.
const observedWindows = new Map();
const observationSignals = new Map();

// A Qt QUuid is exposed to the scripting engine as a UUID-like value. Its
// JavaScript string representation is normalized by the Python broker.
// If a particular KWin backend does not convert it to a usable string,
// ignore the observation rather than invent an identity from title or PID.
function windowUUID(win) {
    if (!win || win.internalId === undefined || win.internalId === null) return "";
    const identifier = String(win.internalId);
    if (!identifier || identifier === "[object Object]") return "";
    return identifier;
}

// Copy currently available information out of the KWin object into plain
// JavaScript values. Never send the window object itself over D-Bus.
// Caption/class/PID are *hints* about the application, NOT proof of what
// shell command, SSH host, VNC connection or browser page it represents.
function captureWindow(win) {
    const id = windowUUID(win);
    if (!id || !win.normalWindow) return null;

    const g = win.frameGeometry;
    // `onAllDesktops` is explicit because an empty desktops array alone is
    // not an ordinary desktop number. KWin desktop numbers start at 1.
    const desktops = [];
    const assigned = win.desktops || [];
    for (let i = 0; i < assigned.length; i++) {
        desktops.push(Number(assigned[i].x11DesktopNumber));
    }
    return {
        uuid: id,
        pid: Number(win.pid) || 0,
        resource_class: String(win.resourceClass || ""),
        resource_name: String(win.resourceName || ""),
        desktop_file: String(win.desktopFileName || ""),
        caption: String(win.caption || "").slice(0, 200),
        on_all_desktops: Boolean(win.onAllDesktops),
        desktops: desktops,
        geometry: {x: Number(g.x), y: Number(g.y),
                   width: Number(g.width), height: Number(g.height)}
    };
}

// This method calls a diagnostic-only Python D-Bus method. It never calls
// SubmitLaunch, registers a managed window, or invokes a close operation.
function sendObservation(event, snapshot) {
    if (!snapshot) return;
    callDBus(BRIDGE, PATH, BRIDGE, "ObserveWindow",
             JSON.stringify({source: observerSource, revision: ++observerRevision,
                             event: event, window: snapshot}));
}

// Refresh an already known snapshot; suppress an unchanged 'changed' event.
// A freshly observed window is always reported as added/existing.
function observeWindow(event, win) {
    const snapshot = captureWindow(win);
    if (!snapshot) return;
    const before = observedWindows.get(snapshot.uuid);
    observedWindows.set(snapshot.uuid, snapshot);
    if (event !== "changed" || !before ||
            JSON.stringify(before) !== JSON.stringify(snapshot)) {
        sendObservation(event, snapshot);
    }
    return snapshot.uuid;
}

// Remember the specific signal callbacks we registered for each window.
// Removing them during windowRemoved avoids retaining references to closed
// KWin window objects. Callback captures its own `win` reference, NOT whichever
// window happens to be active later.
function followWindow(win) {
    const id = windowUUID(win);
    if (!id || !win.normalWindow || observationSignals.has(id)) return;
    const changed = function() { observeWindow("changed", win); };
    // These signals notify us about user-driven movement, resizing, desktop
    // changes, app identity hints and captions even without joetoo actions.
    win.frameGeometryChanged.connect(changed);
    win.desktopsChanged.connect(changed);
    win.captionChanged.connect(changed);
    win.desktopFileNameChanged.connect(changed);
    win.windowClassChanged.connect(changed);
    observationSignals.set(id, {win: win, changed: changed});
}

// A removed KWin object may already be invalid: send the *last captured*
// metadata instead of reading its disappearing geometry or caption again.
function forgetWindow(win) {
    // KWin normally keeps internalId readable here, but find the stored
    // identity by the same window-object reference if deletion hid its ID.
    let id = windowUUID(win);
    if (!id || !observedWindows.has(id)) {
        for (const [candidate, hooks] of observationSignals) {
            if (hooks.win === win) { id = candidate; break; }
        }
    }
    const prior = id ? observedWindows.get(id) : null;
    if (!prior) return;
    sendObservation("removed", prior);
    observedWindows.delete(id);
    const hooks = observationSignals.get(id);
    if (hooks) {
        // The Qt object may already be in deletion; disconnect when possible
        // but always release our JavaScript references in the local map.
        try {
            hooks.win.frameGeometryChanged.disconnect(hooks.changed);
            hooks.win.desktopsChanged.disconnect(hooks.changed);
            hooks.win.captionChanged.disconnect(hooks.changed);
            hooks.win.desktopFileNameChanged.disconnect(hooks.changed);
            hooks.win.windowClassChanged.disconnect(hooks.changed);
        } catch (err) {
            console.warn("joetoo: window signal cleanup: " + err);
        }
        observationSignals.delete(id);
    }
}

// On script startup (or explicit refresh), enumerate windows that already
// existed before `windowAdded` handlers were installed. A refresh also
// repopulates the Python cache after an OpenRC broker restart that reuses
// the running KWin resident script.
function reportExistingWindows() {
    const windows = workspace.stackingOrder;
    const snapshots = [];
    for (const win of windows) {
        const id = observeWindow("existing", win);
        followWindow(win);
        if (id) snapshots.push(observedWindows.get(id));
    }
    // The separate existing events retain backward-compatible diagnostics.
    // This ONE complete inventory message marks a synchronization boundary:
    // the broker validates it first, then atomically replaces its current map.
    // KWin runs this enumeration synchronously on its scripting thread.
    callDBus(BRIDGE, PATH, BRIDGE, "SyncInventory", JSON.stringify({
        source: observerSource, revision: ++observerRevision, windows: snapshots
    }));
}

// Install event handlers BEFORE enumerating, so windows created during script
// initialization are not silently omitted. Added/removed are KWin events;
// they are not requests to launch or terminate applications.
workspace.windowAdded.connect(function(win) {
    observeWindow("added", win);
    followWindow(win);
});
workspace.windowRemoved.connect(forgetWindow);

// The existing Bash CLI can invoke this named KWin action using kglobalaccel
// to refresh diagnostics (e.g. after the broker restarts). No default hotkey.
registerShortcut("joetoo_bridge_observe", "Joetoo refresh window observations",
                 "", reportExistingWindows);
reportExistingWindows();
// ---------------- End Step 1.3a observational extension ---------------------
