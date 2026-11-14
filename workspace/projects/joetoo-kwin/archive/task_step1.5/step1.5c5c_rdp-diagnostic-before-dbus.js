// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Standalone, observation-only KWin script. Never load as joetoo-bridge.
// Load BEFORE the client: PID is correlated afterwards with run.txt. Unknown
// classes retain one bounded birth snapshot; captions are never collected from
// them. Only SDL windows and minimal activation references are exported.
//
// A private copy may prepend `var JOETOO_RDP_DIAGNOSTIC_SETTINGS = {...};`.
// Defaults are diagnostic bounds, not production launch/readiness policy.
// Console output is JSON after "JOETOO_RDP_DIAGNOSTIC ". Collect from KWin's
// existing log sink, not from the FreeRDP log. Stop/export BEFORE unloading.
// Require ready -> contiguous transport_seq -> end in the captured log. Console
// delivery has no acknowledgement: capture_intact describes internal collection,
// never proof of delivery or full viewer-lifecycle coverage. A missing end is
// incomplete evidence, including unloading, compositor exit or logging failure.
(function () {
    "use strict";
    const prefix = "JOETOO_RDP_DIAGNOSTIC ";
    const defaults = {
        durationMs: 1800000, maxRecords: 1024, maxWindows: 64,
        maxRecordBytes: 8192, expectedClass: "com.freerdp.client.sdl3",
        shortcutPrefix: "joetoo_rdp_diagnostic"
    };
    const source = "rdp-diag-" + Date.now().toString(36) + "-" +
        Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
    let settings, running = true, captureSequence = 0, lastWallTime = null;
    let windowSequence = 0, transportSequence = 0, callbackFailures = 0;
    let overflow = null;
    let timer = null, cleanupFailures = 0, outputFailures = 0;
    const entries = new Map(), connections = new Set(), records = [];
    const targetIds = new Set(), capabilities = {};
    const unresolvedWindows = new Set();

    function output(value) {
        // Includes ready and end, so external validation detects lost boundary
        // lines as well as dropped, duplicated or reordered event records.
        const envelope = Object.assign({transport_seq: ++transportSequence}, value);
        try { console.info(prefix + JSON.stringify(envelope)); return true; }
        catch (_) { outputFailures++; return false; }
    }
    function guarded(callback) {
        return function () {
            if (!running) return;
            try { callback.apply(null, arguments); }
            catch (_) {
                // Qt objects may become inaccessible inside a queued callback.
                // Do not let exceptions escape into KWin or serialize their text.
                callbackFailures++;
                finish("callback_error");
            }
        };
    }
    function raw(object, name) {
        try {
            const value = object[name];
            return value === undefined
                ? {state: "unsupported"} : {state: "ok", value: value};
        } catch (_) { return {state: "inaccessible"}; }
    }
    function uuid(win) {
        if (!win) return null;
        const result = raw(win, "internalId");
        if (result.state !== "ok") return null;
        let value;
        try { value = String(result.value).replace(/^\{(.*)\}$/, "$1").toLowerCase(); }
        catch (_) { return null; }
        return /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(value) ? value : null;
    }
    function field(win, name, type) {
        const result = raw(win, name);
        if (result.state !== "ok") return result;
        const value = result.value;
        if (typeof value === "function") return {state: "unsupported"};
        if (type === "boolean" && typeof value === "boolean") return result;
        if (type === "number" && typeof value === "number" && Number.isFinite(value)) return result;
        if (type === "string" && typeof value === "string" && value.length <= 128) return result;
        if (type === "uuid") {
            const identifier = uuid(value);
            return value === null || identifier !== null
                ? {state: "ok", value: identifier} : {state: "inaccessible"};
        }
        if ((type === "rect" || type === "size") && value) {
            const copy = {};
            for (const key of (type === "rect" ? ["x", "y", "width", "height"] : ["width", "height"])) {
                const item = raw(value, key);
                if (item.state !== "ok") return item;
                if (typeof item.value !== "number" || !Number.isFinite(item.value)) return {state: "invalid"};
                copy[key] = item.value;
            }
            return {state: "ok", value: copy};
        }
        return {state: "invalid"};
    }
    function inScope(win) {
        return ["resourceClass", "desktopFileName"].some(function (key) {
            const value = raw(win, key);
            return value.state === "ok" && value.value === settings.expectedClass;
        });
    }
    function classKnown(win) {
        return ["resourceClass", "desktopFileName"].some(function (key) {
            const value = raw(win, key);
            return value.state === "ok" && typeof value.value === "string" && value.value.length > 0;
        });
    }
    function snapshot(win, id) {
        const scope = inScope(win);
        const data = {uuid: id, in_scope: scope, pid: field(win, "pid", "number")};
        for (const key of ["normalWindow", "dialog", "utility", "modal", "transient",
            "resizeable", "noBorder", "hidden", "visible", "readyForPainting",
            "decorationHasAlpha", "skipTaskbar", "skipSwitcher", "skipPager", "fullScreen",
            "minimized", "keepAbove", "keepBelow", "active", "deleted", "wantsInput", "move", "resize"]) {
            data[key] = field(win, key, "boolean");
        }
        data.windowType = field(win, "windowType", "number");
        data.transientFor = field(win, "transientFor", "uuid");
        for (const key of ["frameGeometry", "clientGeometry", "bufferGeometry"]) data[key] = field(win, key, "rect");
        for (const key of ["minSize", "maxSize"]) data[key] = field(win, key, "size");
        // Only safe structural role values, never arbitrary captions or widget text.
        for (const key of ["windowRole", "resourceClass", "resourceName", "desktopFileName"]) {
            const value = scope ? field(win, key, "string") : {state: "redacted"};
            data[key] = value.state === "ok" && !/^[A-Za-z0-9_.:-]*$/.test(value.value)
                ? {state: "redacted"} : value;
        }
        for (const key of ["caption", "captionNormal"]) {
            const outputKey = key === "caption" ? "title_marker" : "normal_title_marker";
            data[outputKey] = {state: "redacted"};
            if (scope) {
                const title = raw(win, key);
                if (title.state !== "ok") data[outputKey] = title;
                else if (typeof title.value === "function") data[outputKey] = {state: "unsupported"};
                else if (typeof title.value === "string") {
                    // KWin may decorate a duplicate caption. Export the generated
                    // marker alone, never any suffix or other client-provided text.
                    const match = /^(joetoo-rdp-proof-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:$|\s)/i.exec(title.value);
                    if (match) data[outputKey] = {state: "ok", value: match[1], exact: match[1] === title.value};
                }
            }
        }
        return data;
    }
    function disconnect(handles) {
        for (const handle of Array.from(handles)) {
            try { handle.signal.disconnect(handle.callback); }
            catch (_) { cleanupFailures++; }
            connections.delete(handle);
            if (handle.owner) handle.owner.delete(handle);
            handles.delete(handle);
        }
    }
    function connect(object, name, callback, handles) {
        if (!running) return "inactive";
        const result = raw(object, name);
        if (result.state !== "ok") return result.state;
        try {
            if (!result.value || typeof result.value.connect !== "function" ||
                typeof result.value.disconnect !== "function") return "unsupported";
            const safeCallback = guarded(callback);
            result.value.connect(safeCallback);
            const handle = {signal: result.value, callback: safeCallback, owner: handles || null};
            connections.add(handle);
            if (handles) handles.add(handle);
            return "connected";
        } catch (_) { return "inaccessible"; }
    }
    function finish(reason) {
        if (!running) return;
        running = false; // Queued callbacks become inert before disconnecting.
        if (timer) {
            try { timer.stop(); } catch (_) { cleanupFailures++; }
        }
        disconnect(connections);
        const exported = records.filter(function (record) {
            return !record.window || targetIds.has(record.window.uuid);
        }).sort(function (a, b) { return a.capture_seq - b.capture_seq; });
        // Stream sequence is contiguous; capture_seq may skip deliberately
        // filtered non-SDL births. Wall time is NOT a monotonic clock.
        exported.forEach(function (record, index) {
            output(Object.assign({kind: "event", observer: source, seq: index + 1}, record));
        });
        output({kind: "end", observer: source, records: exported.length,
            captured: captureSequence, reason: reason,
            truncated: ["record_limit", "window_limit", "record_size_limit"].includes(reason),
            buffered_records: records.length, overflow: overflow,
            callback_failures: callbackFailures,
            cleanup_failures: cleanupFailures, output_failures: outputFailures,
            delivery: "unacknowledged; validate complete transport sequence externally",
            unresolved_window_count: unresolvedWindows.size,
            capture_intact: ["requested", "expired"].includes(reason) && !cleanupFailures &&
                !outputFailures && !callbackFailures && unresolvedWindows.size === 0,
            capabilities: capabilities});
        records.length = 0;
        entries.clear(); targetIds.clear(); unresolvedWindows.clear();
    }
    function record(event, fields) {
        if (!running) return;
        if (records.length >= settings.maxRecords) {
            overflow = {event: event, rejected_records: 1, limit: settings.maxRecords};
            finish("record_limit"); return;
        }
        const now = Date.now();
        const value = Object.assign({event: event, capture_seq: ++captureSequence,
            wall_time_ms: now, clock_regressed: lastWallTime !== null && now < lastWallTime}, fields);
        lastWallTime = now;
        if (JSON.stringify(value).length > settings.maxRecordBytes) {
            overflow = {event: event, rejected_records: 1, limit: settings.maxRecordBytes};
            finish("record_size_limit"); return;
        }
        records.push(value);
    }
    function activeReference() {
        const active = raw(workspace, "activeWindow");
        if (active.state !== "ok") return active;
        return {state: "ok", value: uuid(active.value)};
    }
    function sample(entry, event) {
        if (!running || entry.removed) return;
        const data = snapshot(entry.win, entry.id);
        entry.last = data;
        if (!entry.baseline) {
            if (classKnown(entry.win)) unresolvedWindows.delete(entry.serial);
            else unresolvedWindows.add(entry.serial);
        }
        if (data.in_scope) {
            if (entry.id === null) { finish("identity_unavailable"); return; }
            targetIds.add(entry.id);
        }
        record(event, {window: data, baseline: entry.baseline,
            observed_active: activeReference()});
        if (running && data.in_scope && !entry.detailed) attachDetail(entry);
    }
    function attachDetail(entry) {
        entry.detailed = true;
        const supported = Object.assign({}, entry.identitySignals);
        // These names are declared in the inspected KWin 6.7.5 Window APIs.
        // Feature-check even known signals; X11 decoration naming differs.
        for (const name of ["captionChanged", "frameGeometryChanged", "clientGeometryChanged",
            "bufferGeometryChanged", "windowRoleChanged", "hiddenChanged", "modalChanged",
            "transientChanged", "skipTaskbarChanged", "skipPagerChanged", "skipSwitcherChanged",
            "decorationChanged", "decorationPolicyChanged", "noBorderChanged", "surfaceChanged",
            "readyForPaintingChanged", "activeChanged", "keepAboveChanged", "keepBelowChanged",
            "fullScreenChanged", "interactiveMoveResizeStarted", "interactiveMoveResizeStepped",
            "interactiveMoveResizeFinished"]) {
            supported[name] = connect(entry.win, name, function () {
                sample(entry, name);
            }, entry.handles);
        }
        record("window_signals", {window: {uuid: entry.id}, supported: supported});
    }
    function track(win, baseline) {
        if (!running || !win || entries.has(win)) return;
        if (entries.size >= settings.maxWindows) {
            overflow = {event: "track", rejected_windows: 1, limit: settings.maxWindows};
            finish("window_limit"); return;
        }
        const entry = {win: win, id: uuid(win), handles: new Set(), baseline: baseline,
            detailed: false, removed: false, last: null, identitySignals: {}, serial: ++windowSequence};
        entries.set(win, entry);
        // Birth snapshots are retained even before class/PID is available.
        // Nonmatching windows get only identity notifications, not busy frame
        // subscriptions. Later class recognition exports the earlier snapshot.
        for (const name of ["windowClassChanged", "desktopFileNameChanged"]) {
            entry.identitySignals[name] = connect(win, name, function () { sample(entry, name); }, entry.handles);
        }
        sample(entry, baseline ? "existing" : "added");
    }
    function activation(win) {
        if (!running) return;
        record("workspace.windowActivated", {
            activated_uuid: uuid(win === undefined ? raw(workspace, "activeWindow").value : win),
            observed_active: activeReference(), intent: "unknown"});
    }
    function marker() {
        if (!running) return;
        // Invoking from Konsole observes Konsole, not the previously active
        // viewer. No inference about earlier focus or physical input is made.
        record("active_window_marker_request", {observed_active: activeReference(),
            intent: "explicit invocation; operator provenance unverified",
            scope: "active at invocation only; no previous-viewer confirmation"});
    }

    try {
        const supplied = typeof JOETOO_RDP_DIAGNOSTIC_SETTINGS === "undefined"
            ? {} : JOETOO_RDP_DIAGNOSTIC_SETTINGS;
        if (!supplied || typeof supplied !== "object" || Array.isArray(supplied) ||
            Object.keys(supplied).some(key => !Object.prototype.hasOwnProperty.call(defaults, key))) throw new Error();
        settings = Object.assign({}, defaults, supplied);
        for (const key of ["durationMs", "maxRecords", "maxWindows", "maxRecordBytes"]) {
            if (!Number.isSafeInteger(settings[key]) || settings[key] < 1) throw new Error();
        }
        if (settings.durationMs > 2147483647 || typeof settings.expectedClass !== "string" ||
            typeof settings.shortcutPrefix !== "string" ||
            !/^[A-Za-z0-9_.-]{1,128}$/.test(settings.expectedClass) ||
            !/^[A-Za-z0-9_]{1,64}$/.test(settings.shortcutPrefix)) throw new Error();
        if (typeof QTimer !== "function") throw new Error();
        timer = new QTimer();
        timer.singleShot = true; timer.interval = settings.durationMs;
        capabilities.timeout = connect(timer, "timeout", function () { finish("expired"); });
        if (capabilities.timeout !== "connected") throw new Error();
        capabilities.windowAdded = connect(workspace, "windowAdded", win => track(win, false));
        capabilities.windowRemoved = connect(workspace, "windowRemoved", function (win) {
            const entry = entries.get(win);
            if (!running || !entry) return;
            entry.removed = true;
            record("removed", {window: entry.last || {uuid: entry.id},
                baseline: entry.baseline, cached_on_removal: true});
            disconnect(entry.handles); entries.delete(win);
        });
        capabilities.windowActivated = connect(workspace, "windowActivated", activation);
        if (capabilities.windowAdded !== "connected" || capabilities.windowRemoved !== "connected") throw new Error();
        // No default keys. These actions only export evidence or mark the
        // observed active UUID; neither requests activation or selection.
        if (typeof registerShortcut === "function") {
            capabilities.finishShortcut = registerShortcut(settings.shortcutPrefix + "_finish",
                "Finish observational RDP diagnostic", "", guarded(function () { finish("requested"); })) !== false;
            capabilities.markerShortcut = registerShortcut(settings.shortcutPrefix + "_mark_active",
                "Record active UUID in observational RDP diagnostic", "", guarded(marker)) !== false;
        } else capabilities.finishShortcut = capabilities.markerShortcut = false;
        timer.start();
        if (!output({kind: "ready", observer: source, settings: settings, capabilities: capabilities,
            wall_time_ms: Date.now(), format_version: 1})) {
            finish("output_error"); return;
        }
        const initial = raw(workspace, "stackingOrder");
        if (initial.state !== "ok" || !initial.value || !Number.isSafeInteger(initial.value.length)) throw new Error();
        for (let i = 0; running && i < initial.value.length; i++) track(initial.value[i], true);
        record("initial_active", {observed_active: activeReference(), intent: "unknown"});
    } catch (_) {
        // Do not serialize exception messages, which can include client text.
        finish("setup_error");
    }
})();
