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

// Optional moves have a distinct claim path: an old resident must never
// interpret zero placeholders as real coordinates, sizes or desktop numbers.
function moveOptionalFromBroker() {
    const win = workspace.activeWindow;
    const started = Date.now();
    const identifier = windowUUID(win);
    callDBus(BRIDGE, PATH, BRIDGE, "TakeMove", observerSource, identifier, function(payload) {
        if (!payload) return;
        let request;
        try { request = JSON.parse(payload); }
        catch (err) { console.warn("joetoo: malformed optional move payload"); return; }
        if (!win || win.deleted || windowUUID(win) !== identifier) {
            finish(request, "ERROR", "Captured window disappeared"); return;
        }
        // Starting the local timer before TakeMove is conservative about bus
        // latency; never apply a callback after its remaining request lifetime.
        const elapsed = Date.now() - started;
        if (!Number.isFinite(request.remaining_ms) || elapsed < 0 || elapsed >= request.remaining_ms) {
            finish(request, "ERROR", "Optional move request expired"); return;
        }
        placeOptionalWindow(win, request);
    });
}

function placeOptionalWindow(win, request) {
    try {
        const uuid = windowUUID(win);
        if (!uuid || win.deleted) throw new Error("Captured window disappeared");
        const captured = {
            geometry: {x: win.frameGeometry.x, y: win.frameGeometry.y,
                       width: win.frameGeometry.width, height: win.frameGeometry.height},
            desktops: (win.desktops || []).map(d => Number(d.x11DesktopNumber)).sort((a, b) => a - b),
            on_all_desktops: Boolean(win.onAllDesktops)
        };
        const resolved = JSON.parse(JSON.stringify(captured));
        const desktop = request.preserve_desktop ? null : workspace.desktops[request.desktop - 1];
        if (!request.preserve_desktop && (!Number.isInteger(request.desktop) || request.desktop < 1 || !desktop)) {
            throw new Error("Virtual desktop does not exist");
        }
        for (const key of ["x", "y", "width", "height"]) {
            const preserve = key === "x" || key === "y" ? request.preserve_position : request.preserve_size;
            if (!preserve) resolved.geometry[key] = request[key];
            const value = resolved.geometry[key];
            if (!Number.isFinite(value) || value > 32768 || value < (key === "x" || key === "y" ? -32768 : 1)) {
                throw new Error("Resolved geometry out of range");
            }
        }
        if (!request.preserve_desktop) {
            resolved.desktops = [request.desktop];
            resolved.on_all_desktops = false;
        }
        const tiled = win.tile != null;
        const fullscreen = Boolean(win.fullScreen);
        const changesGeometry = !request.preserve_position || !request.preserve_size;
        // Installed KWin window.h exposes maximizeMode; MaximizeRestore is 0
        // in effect/globals.h. Unknown mode support also fails closed here.
        if (changesGeometry && (tiled || fullscreen || win.maximizeMode !== 0)) {
            throw new Error("Refusing geometry change on tiled/fullscreen/maximized or unknown-mode window");
        }
        const before = geometryText(win);
        // Resolve all omitted fields immediately before assignment, without
        // an intervening D-Bus round trip or a second active-window lookup.
        if (!request.preserve_desktop) win.desktops = [desktop];
        if (changesGeometry) win.frameGeometry = resolved.geometry;
        finish(request, "VERIFY", JSON.stringify({
            window_uuid: uuid, source: observerSource, before: before,
            tiled: tiled, fullscreen: fullscreen, captured: captured, resolved: resolved
        }));
    } catch (err) {
        finish(request, "ERROR", "Optional move failed: " + err);
    }
}

registerShortcut("joetoo_bridge_move_optional", "Joetoo optional active-window move", "", moveOptionalFromBroker);

// Explicit operator release: obtain the broker-owned UUID, never activeWindow.
// Reuse optional-move assignment/verification with all fields explicit; no focus
// or stacking request and no observer beyond the existing lifecycle resident.
function sdlPlacementFromBroker() {
    const started = Date.now();
    callDBus(BRIDGE, PATH, BRIDGE, "TakeSdlPlacement", observerSource, function(payload) {
        if (!payload) return;
        let r;
        try { r = JSON.parse(payload); } catch (error) { return; }
        const elapsed = Date.now() - started;
        if (r.source !== observerSource || !Number.isFinite(r.remaining_ms) || elapsed < 0 || elapsed >= r.remaining_ms) {
            finish(r, "ERROR", "SDL placement callback expired/source changed"); return;
        }
        const canonical = value => String(value).replace(/[{}]/g, "").toLowerCase();
        const matches = workspace.stackingOrder.filter(win => canonical(windowUUID(win)) === r.window_uuid);
        const win = matches.length === 1 ? matches[0] : null;
        if (!win || win.deleted || !win.normalWindow || Number(win.pid) !== r.pid ||
                String(win.resourceClass || "").toLowerCase() !== r.resource_class ||
                String(win.caption || "") !== r.title_marker || r.preserve_desktop !== false ||
                r.preserve_position !== false || r.preserve_size !== false) {
            finish(r, "ERROR", "Registered SDL viewer identity unavailable"); return;
        }
        placeOptionalWindow(win, r);
    });
}
registerShortcut("joetoo_bridge_sdl_placement", "Joetoo operator SDL placement", "", sdlPlacementFromBroker);

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
        source: observerSource, revision: ++observerRevision, windows: snapshots, move_protocol: 1,
        viewer_protocol: typeof workspace.getClient === "function" ? 1 : 0,
        initial_layout_protocol: typeof workspace.raiseWindow === "function" && workspace.stackingOrder &&
            workspace.currentDesktop && Number.isInteger(Number(workspace.currentDesktop.x11DesktopNumber)) &&
            typeof workspace.activeWindow !== "undefined" ? 1 : 0
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

// TigerVNC desktop-role handshake. XID comes only from the broker's scoped
// X11 event observer. Resolve it in KWin, then require new UUID/PID/lifecycle
// validation at the broker BEFORE any geometry is changed. No title matching.
function managedViewerFromBroker() {
    if (typeof workspace.getClient !== "function") return;
    callDBus(BRIDGE, PATH, BRIDGE, "TakeManagedViewer", observerSource, function(payload) {
        if (!payload) return;
        let request;
        try { request = JSON.parse(payload); } catch (error) { return; }
        if (request.source !== observerSource || !Array.isArray(request.xids)) return;
        const matches = [];
        for (const xid of request.xids) {
            const win = workspace.getClient(xid);
            if (!win || win.deleted || !win.normalWindow || Number(win.pid) !== request.pid) continue;
            const cls = String(win.resourceClass || "").toLowerCase();
            if (cls !== "vncviewer") continue;
            const identifier = windowUUID(win);
            if (identifier) matches.push({xid: xid, uuid: identifier});
        }
        const resolutionStarted = Date.now();
        callDBus(BRIDGE, PATH, BRIDGE, "CompleteManagedViewer", JSON.stringify({
            id: request.id, claim: request.claim, source: observerSource, matches: matches
        }), function(placement) {
            if (!placement) return;
            let r;
            try { r = JSON.parse(placement); } catch (error) { return; }
            if (r.source !== observerSource || Date.now() - resolutionStarted >= r.remaining_ms) return;
            // Re-resolve the same XID and UUID after the async broker round-trip.
            const selected = matches.find(m => m.uuid.replace(/[{}]/g, "").toLowerCase() === r.window_uuid);
            const win = selected ? workspace.getClient(selected.xid) : null;
            if (!win || win.deleted || Number(win.pid) !== request.pid ||
                    windowUUID(win).replace(/[{}]/g, "").toLowerCase() !== r.window_uuid) {
                finish(r, "ERROR", "Verified viewer disappeared before placement"); return;
            }
            placeWindow(win, r, "launch");
        });
    });
}
registerShortcut("joetoo_bridge_viewer", "Joetoo verified TigerVNC desktop", "", managedViewerFromBroker);

// Initialization-only, positively registered cohort. Never select the active
// window as an operation target, and never subscribe to later user overrides.
function initialLayoutFromBroker() {
    // Broker UUIDs are canonical (lowercase, without Qt QUuid braces).
    // Normalize representation only; never substitute a class/title/PID match.
    function layoutUUID(win) {
        return windowUUID(win).replace(/^\{([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\}$/i, "$1").toLowerCase();
    }
    const beforeActive = workspace.activeWindow;
    const beforeDesktop = workspace.currentDesktop;
    const beforeDesktopId = String(beforeDesktop && beforeDesktop.id);
    const beforeDesktopNumber = Number(beforeDesktop && beforeDesktop.x11DesktopNumber);
    const beforeActiveId = layoutUUID(beforeActive);
    const started = Date.now();
    callDBus(BRIDGE, PATH, BRIDGE, "TakeInitialLayout", observerSource, function(payload) {
        if (!payload) return;
        let r;
        try { r = JSON.parse(payload); } catch (err) { return; }
        const result = {source: observerSource, order: [], focus_attempted: false,
                        before_active_uuid: beforeActiveId,
                        active_uuid: layoutUUID(workspace.activeWindow),
                        current_desktop: Number(workspace.currentDesktop && workspace.currentDesktop.x11DesktopNumber),
                        geometry_unchanged: false};
        let done = false, timer = null, guardPending = false;
        let focusStarted = null, focusDeadline = null;
        const connections = [];
        function connect(signal, callback) {
            if (signal && typeof signal.connect === "function" && typeof signal.disconnect === "function") {
                signal.connect(callback);
                connections.push([signal, callback]);
                return true;
            }
            return false;
        }
        function cleanup() {
            if (timer) timer.stop();
            for (const [signal, callback] of connections) {
                try { signal.disconnect(callback); } catch (err) { /* QObject may already be destroyed. */ }
            }
            connections.length = 0;
            if (timer && typeof timer.deleteLater === "function") timer.deleteLater();
            timer = null;
        }
        function contextError() {
            const elapsed = Date.now() - started;
            if (r.source !== observerSource) return "Observer source replaced during initial layout";
            if (!Number.isFinite(r.remaining_ms) || elapsed < 0 || elapsed >= r.remaining_ms)
                return "Initial layout transaction expired";
            if (String(workspace.currentDesktop && workspace.currentDesktop.id) !== beforeDesktopId ||
                Number(workspace.currentDesktop && workspace.currentDesktop.x11DesktopNumber) !== beforeDesktopNumber)
                return "Displayed desktop changed during initialization";
            return "";
        }
        function resolveCohort() {
            const available = workspace.stackingOrder;
            return r.entries.map(e => {
                const win = available.find(w => layoutUUID(w) === e.uuid);
                // Keep resolution anchored to the actual stack. windowList is
                // diagnostic evidence only, never an alternate ownership path.
                if (!win) {
                    const listed = typeof workspace.windowList === "function" ?
                        workspace.windowList().some(w => layoutUUID(w) === e.uuid) : "unavailable";
                    throw new Error("Cohort UUID [" + e.uuid + "]: stackingOrder match=false; windowList match=" + listed);
                }
                // Do not coerce an unknown Qt enum/property into a normal mode.
                // Include its JS type: undefined and numeric zero differ here.
                const checks = [
                    ["deleted", win.deleted, Boolean(win.deleted)],
                    ["fullScreen", win.fullScreen, Boolean(win.fullScreen)],
                    ["keepAbove", win.keepAbove, Boolean(win.keepAbove)],
                    ["keepBelow", win.keepBelow, Boolean(win.keepBelow)],
                    ["tile", win.tile, win.tile != null],
                    ["maximizeMode", win.maximizeMode, win.maximizeMode !== 0]
                ];
                const incompatible = checks.find(check => check[2]);
                if (incompatible) {
                    throw new Error("Cohort UUID [" + e.uuid + "]: incompatible " + incompatible[0] +
                        "=" + String(incompatible[1]) + " (type=" + typeof incompatible[1] + ")");
                }
                const g = win.frameGeometry;
                const desktops = (win.desktops || []).map(d => Number(d.x11DesktopNumber));
                if (["x", "y", "width", "height"].some(k => g[k] !== e.geometry[k]) ||
                    JSON.stringify(desktops) !== JSON.stringify(e.desktops) ||
                    Boolean(win.onAllDesktops) !== e.on_all_desktops) throw new Error("Cohort UUID [" + e.uuid + "]: frame/membership changed");
                return win;
            });
        }
        function readback() {
            // Read back after activation as activation itself may raise a window.
            result.active_uuid = layoutUUID(workspace.activeWindow);
            result.current_desktop = Number(workspace.currentDesktop && workspace.currentDesktop.x11DesktopNumber);
            result.order = workspace.stackingOrder.map(layoutUUID).filter(id => r.order.includes(id));
            // Keep geometry and stack evidence even when focus never converges.
            const windows = workspace.stackingOrder;
            result.geometry_unchanged = r.entries.every(e => {
                const w = windows.find(win => layoutUUID(win) === e.uuid);
                return w && !w.deleted && ["x", "y", "width", "height"].every(k => w.frameGeometry[k] === e.geometry[k]) &&
                    JSON.stringify((w.desktops || []).map(d => Number(d.x11DesktopNumber))) === JSON.stringify(e.desktops) &&
                    Boolean(w.onAllDesktops) === e.on_all_desktops;
            });
        }
        function finish(reason, phase) {
            if (done) return;
            done = true; // In-flight DBus replies and queued Qt signals become inert.
            cleanup();
            result.focus_observation = phase;
            result.focus_elapsed_ms = focusStarted === null ? 0 : Math.max(0, Date.now() - focusStarted);
            try { readback(); } catch (err) { reason = reason || String(err); }
            const invalid = contextError();
            if (invalid) reason = invalid;
            if (reason) result.error = reason;
            callDBus(BRIDGE, PATH, BRIDGE, "CompleteInitialLayout", r.id, JSON.stringify(result));
        }
        function observe(authorised) {
            if (done) return;
            try {
                const invalid = contextError();
                if (invalid) { finish(invalid, "interrupted or expired"); return; }
                resolveCohort(); // Never retain a vanished/incompatible QObject as a target.
                const active = layoutUUID(workspace.activeWindow);
                // An unchanged pre-request window is not evidence of intervention.
                // A different activation may be a user or client: do not reclaim it.
                if (active && active !== r.preferred_uuid && active !== beforeActiveId) {
                    finish("Competing activation observed: UUID [" + active + "]; user/client cause unknown", "interrupted");
                    return;
                }
                if (Date.now() >= focusDeadline) {
                    finish("Focus observation timed out: preferred UUID [" + r.preferred_uuid +
                           "] observed [" + active + "]", "timeout");
                    return;
                }
                // Confirm the existing broker lease/source/ownership is still live.
                // This read-only call never renews the lease or requests activation.
                if (authorised) {
                    if (active === r.preferred_uuid) finish("", "delayed");
                } else if (!guardPending) {
                    guardPending = true;
                    callDBus(BRIDGE, PATH, BRIDGE, "InitialLayoutStatus", r.id, function(payload) {
                        if (done) return;
                        guardPending = false;
                        let status;
                        try { status = JSON.parse(payload); } catch (err) {
                            finish("Initial-layout status unavailable during focus observation", "interrupted"); return;
                        }
                        if (status.id !== r.id || status.state !== "RUNNING") {
                            finish("Initial-layout lease/source/ownership no longer valid: " + String(status.state), "interrupted"); return;
                        }
                        observe(true);
                    });
                }
            } catch (err) { finish(String(err), "interrupted"); }
        }
        function tick() {
            observe(false);
            if (!done) timer.start(Math.max(1, Math.min(r.focus_poll_interval_ms, focusDeadline - Date.now(),
                                                      r.remaining_ms - (Date.now() - started))));
        }
        try {
            const invalid = contextError();
            if (invalid || layoutUUID(workspace.activeWindow) !== beforeActiveId)
                throw new Error(invalid || "Initial layout stale or user focus changed during claim");
            if (!Number.isInteger(r.focus_timeout_ms) || r.focus_timeout_ms < 1 || r.focus_timeout_ms > 2000 ||
                !Number.isInteger(r.focus_poll_interval_ms) || r.focus_poll_interval_ms < 1 ||
                r.focus_poll_interval_ms > Math.min(250, r.focus_timeout_ms))
                throw new Error("Invalid focus observation timing in initial-layout claim");
            const cohort = resolveCohort();
            if (typeof workspace.raiseWindow !== "function") throw new Error("KWin raiseWindow unavailable");
            for (const id of r.order) workspace.raiseWindow(cohort.find(w => layoutUUID(w) === id));
            if (!r.preferred_uuid || beforeDesktopNumber !== r.entries[0].desktop) {
                finish("", "not attempted"); return;
            }
            const target = cohort.find(w => layoutUUID(w) === r.preferred_uuid);
            if (!target || !(target.desktops || []).some(d => Number(d.x11DesktopNumber) === beforeDesktopNumber))
                throw new Error("Preferred target is not visible on this desktop");
            focusStarted = Date.now();
            focusDeadline = Math.min(focusStarted + r.focus_timeout_ms, started + r.remaining_ms);
            result.focus_attempted = true;
            workspace.activeWindow = target; // Exactly one activation request.
            result.initial_active_uuid = layoutUUID(workspace.activeWindow);
            if (result.initial_active_uuid === r.preferred_uuid) {
                finish("", "immediate"); return;
            }
            if (typeof QTimer !== "function") {
                finish("KWin QTimer unavailable for bounded focus observation", "unsupported"); return;
            }
            timer = new QTimer();
            timer.singleShot = true;
            if (!connect(timer.timeout, tick)) throw new Error("KWin timer timeout signal unavailable");
            // Event-driven observations are primary; the configurable timer is
            // also a watchdog for source/lease loss and missed/missing signals.
            connect(workspace.windowActivated, function(win) {
                if (done) return;
                const id = layoutUUID(win);
                // Unlike unchanged polling, an activation signal is new event
                // evidence, even if the original active window is reactivated.
                if (id && id !== r.preferred_uuid) {
                    finish("Competing activation event: UUID [" + id + "]; user/client cause unknown", "interrupted");
                    return;
                }
                observe(false);
            });
            connect(workspace.currentDesktopChanged, function() { observe(false); });
            connect(workspace.windowRemoved, function() { observe(false); });
            tick();
        } catch (err) { finish(String(err), "interrupted"); }
    });
}
registerShortcut("joetoo_bridge_initial_layout", "Joetoo initial cohort layout", "", initialLayoutFromBroker);
