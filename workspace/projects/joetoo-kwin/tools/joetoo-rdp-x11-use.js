// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Diagnostic XID -> UUID linkage only. This script never controls a window.
// A private copy supplies JOETOO_RDP_X11_USE; load before launching the client.
(function () {
    "use strict";
    const c = JOETOO_RDP_X11_USE;
    if (!/^:\d+\.\d+$/.test(c.receiver) || !/^[a-f0-9]{32}$/.test(c.run) ||
        !Number.isInteger(c.pollMs) || c.pollMs < 1 ||
        !Number.isInteger(c.ackMs) || c.ackMs <= c.pollMs ||
        !Number.isInteger(c.maxCandidates) || c.maxCandidates < 1 || c.maxCandidates > 64 ||
        c.expectedClass !== "com.freerdp.client.sdl3") throw Error("Invalid diagnostic settings");
    const tick = new QTimer(), watchdog = new QTimer();
    let stopped = false, pending = false;
    tick.singleShot = true; tick.interval = c.pollMs;
    watchdog.singleShot = true; watchdog.interval = c.ackMs;
    function finish() {
        if (stopped) return;
        stopped = true; pending = false;
        tick.stop(); watchdog.stop();
        tick.timeout.disconnect(sample); watchdog.timeout.disconnect(finish);
    }
    function call(method, body, done) {
        pending = true; watchdog.start();
        try {
            callDBus(c.receiver, "/org/joetoo/RDPX11Use", "org.joetoo.RDPX11Use",
                method, JSON.stringify({run: c.run, body: body}), function (text) {
                    if (stopped) return;
                    try {
                        const reply = JSON.parse(text);
                        if (reply.run !== c.run || reply.ok !== true) { finish(); return; }
                        watchdog.stop(); pending = false; done(reply.body);
                    } catch (_) { finish(); }
                });
        } catch (_) { finish(); }
    }
    function sample() {
        if (stopped || pending) return;
        call("Candidates", null, function (items) {
            if (!Array.isArray(items) || items.length > c.maxCandidates) { finish(); return; }
            const links = [];
            for (const item of items) {
                // getClient is the source-supported X11 client-XID lookup used
                // by the existing VNC diagnostic architecture. Never guess a UUID.
                const w = workspace.getClient(item.xid);
                if (!w || w.deleted || Number(w.pid) !== item.pid ||
                    String(w.resourceClass) !== c.expectedClass) continue;
                const uuid = String(w.internalId).replace(/[{}]/g, "").toLowerCase();
                if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/.test(uuid)) continue;
                links.push({generation: item.generation, xid: item.xid, pid: item.pid, uuid: uuid});
            }
            call("Links", links, function () { if (!stopped) tick.start(); });
        });
    }
    tick.timeout.connect(sample); watchdog.timeout.connect(finish);
    registerShortcut("joetoo_rdp_x11_use_finish", "Finish RDP X11 linkage diagnostic", "", finish);
    sample();
})();
