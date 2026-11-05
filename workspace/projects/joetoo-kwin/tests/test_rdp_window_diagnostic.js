// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Existing node:test/vm approach; no KWin, GUI, D-Bus or network activity.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../tools/joetoo-rdp-window-diagnostic.js'), 'utf8');
const A = '11111111-1111-4111-8111-111111111111';
const B = '22222222-2222-4222-8222-222222222222';
const TOKEN = 'joetoo-rdp-proof-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const detailSignals = ['captionChanged', 'frameGeometryChanged', 'clientGeometryChanged',
    'bufferGeometryChanged', 'windowRoleChanged', 'hiddenChanged', 'modalChanged',
    'transientChanged', 'skipTaskbarChanged', 'skipPagerChanged', 'skipSwitcherChanged',
    'decorationChanged', 'decorationPolicyChanged', 'noBorderChanged', 'surfaceChanged',
    'readyForPaintingChanged', 'activeChanged', 'keepAboveChanged', 'keepBelowChanged',
    'fullScreenChanged', 'interactiveMoveResizeStarted', 'interactiveMoveResizeStepped',
    'interactiveMoveResizeFinished', 'windowClassChanged', 'desktopFileNameChanged'];

// Qt exposes signals as callable objects, not plain objects. Model that detail
// so property feature-detection cannot accidentally discard real Qt signals.
function signal() {
    const callbacks = new Set();
    const result = (...args) => { for (const cb of Array.from(callbacks)) cb(...args); };
    result.emit = result;
    result.connect = cb => callbacks.add(cb);
    result.disconnect = cb => {
        assert.ok(callbacks.has(cb), 'disconnect must address a live subscription');
        callbacks.delete(cb);
    };
    result.count = () => callbacks.size;
    result.pending = () => Array.from(callbacks);
    return result;
}
function window(id = A, options = {}) {
    const data = {
        internalId: '{' + id.toUpperCase() + '}', pid: 0,
        resourceClass: 'com.freerdp.client.sdl3', resourceName: 'sdl-freerdp',
        desktopFileName: 'com.freerdp.client.sdl3', caption: TOKEN, windowRole: '',
        windowType: 0, normalWindow: true, dialog: false, utility: false,
        modal: false, transient: false, transientFor: null, resizeable: true,
        noBorder: false, hidden: false, active: false, move: false, resize: false,
        frameGeometry: {x: 19, y: 54, width: 1032, height: 804},
        clientGeometry: {x: 23, y: 86, width: 1024, height: 768},
        bufferGeometry: {x: 19, y: 54, width: 1032, height: 804},
        minSize: {width: 0, height: 0}, maxSize: {width: 2147483647, height: 2147483647},
        ...options
    };
    for (const name of detailSignals) data[name] = signal();
    const mutations = [];
    const object = new Proxy(data, {set(_target, name) {
        mutations.push(String(name)); throw new Error('Diagnostic must not write window properties');
    }});
    return {object, data, mutations};
}
function harness({initial = [], settings = {}, timer = true, configure = () => {}, transport = null} = {}) {
    let now = 1000;
    const lines = [], statuses = [], calls = [], shortcuts = new Map(), timers = [], mutations = [], forbidden = [];
    const data = {stackingOrder: initial.map(w => w.object), activeWindow: null,
        windowAdded: signal(), windowRemoved: signal(), windowActivated: signal()};
    const workspace = new Proxy(data, {set(_target, name) {
        mutations.push(String(name)); throw new Error('Diagnostic must not control workspace');
    }});
    class Timer {
        constructor() { this.timeout = signal(); this.stopped = false; timers.push(this); }
        start() { this.started = true; }
        stop() { this.stopped = true; this.started = false; }
    }
    const context = {
        workspace, Date: {now: () => now}, JOETOO_RDP_DIAGNOSTIC_SETTINGS: {
            receiverUniqueName: ':1.99', runId: 'a'.repeat(32), ...settings},
        console: {info: line => statuses.push(JSON.parse(line.slice('JOETOO_RDP_DIAGNOSTIC '.length)))},
        registerShortcut: (name, _description, key, cb) => {
            assert.equal(key, ''); shortcuts.set(name, cb); return true;
        },
        callDBus: (destination, object, iface, method, text, callback) => {
            if (destination !== ':1.99' || object !== '/org/joetoo/RDPDiagnostic' ||
                iface !== 'org.joetoo.RDPDiagnostic' || !['Append', 'Probe'].includes(method)) {
                forbidden.push({destination, object, iface, method});
            }
            assert.equal(destination, ':1.99');
            assert.equal(object, '/org/joetoo/RDPDiagnostic');
            assert.equal(iface, 'org.joetoo.RDPDiagnostic');
            assert.ok(['Append', 'Probe'].includes(method));
            const value = JSON.parse(text);
            const call = {method, value, callback}; calls.push(call);
            const reply = {protocol: 1, run_id: value.run_id, observer: value.observer,
                ok: true, persisted: true, transport_seq: value.transport_seq,
                native_launch_ready: method === 'Probe' && value.action === 'observe',
                transport_complete: value.kind === 'end', sender_confirmed_end_ack: value.action === 'delivered'};
            if (transport) transport(call, reply, lines);
            else { if (method === 'Append') lines.push(value); callback(JSON.stringify(reply)); }
        }
    };
    if (timer) context.QTimer = Timer;
    configure({data, context, Timer});
    vm.runInNewContext(source, context);
    const prefix = settings.shortcutPrefix || 'joetoo_rdp_diagnostic';
    function drain() {
        let count = 0;
        while (true) {
            const t = timers.find(t => t.started && t.interval === 0);
            if (!t) return;
            assert.ok(++count < 100000, 'bounded pump');
            t.started = false; t.timeout.emit();
        }
    }
    drain();
    return {
        data, lines, statuses, calls, drain, timers, shortcuts, forbidden, mutations,
        setTime: value => { now = value; },
        add: w => data.windowAdded.emit(w.object),
        remove: w => data.windowRemoved.emit(w.object),
        activate(w) { data.activeWindow = w ? w.object : null; data.windowActivated.emit(data.activeWindow); },
        marker() { shortcuts.get(prefix + '_mark_active')(); },
        finish() { shortcuts.get(prefix + '_finish')?.(); drain(); },
        events: () => lines.filter(r => r.kind === 'event'),
        end: () => lines.find(r => r.kind === 'end')
    };
}
function disconnected(h, windows = []) {
    for (const name of ['windowAdded', 'windowRemoved', 'windowActivated']) {
        if (h.data[name]?.count) assert.equal(h.data[name].count(), 0, name);
    }
    for (const w of windows) for (const name of detailSignals) assert.equal(w.data[name].count(), 0, name);
    for (const timer of h.timers) {
        assert.equal(timer.timeout.count(), 0);
        assert.equal(timer.stopped, true);
    }
    assert.deepEqual(h.forbidden, []);
    assert.deepEqual(h.mutations, []);
    for (const w of windows) assert.deepEqual(w.mutations, []);
}

test('loads before PID is known; copies creation state and exports only safe title markers', () => {
    const h = harness(), w = window();
    h.add(w);
    w.data.pid = 2345;
    w.data.frameGeometry.width = 1200;
    w.data.captionChanged.emit();
    h.finish();
    const birth = h.events().find(r => r.event === 'added');
    assert.equal(birth.window.pid.value, 0);
    assert.equal(birth.window.frameGeometry.value.width, 1032);
    assert.equal(birth.window.title_marker.value, TOKEN);
    assert.equal(h.events().find(r => r.event === 'captionChanged').window.pid.value, 2345);
    assert.equal(birth.baseline, false);
    assert.equal(h.end().capture_intact, true);
    disconnected(h, [w]);
});

test('late class recognition retains a bounded redacted birth snapshot in capture order', () => {
    const h = harness(), w = window(A, {resourceClass: '', desktopFileName: '', caption: 'private authentication text'});
    let captionReads = 0;
    Object.defineProperty(w.data, 'caption', {get() { captionReads++; return 'private authentication text'; }});
    h.add(w);
    h.activate(w);
    assert.equal(captionReads, 0);
    w.data.resourceClass = 'com.freerdp.client.sdl3';
    w.data.windowClassChanged.emit();
    h.finish();
    assert.equal(h.events()[1].event, 'added'); // initial_active precedes creation
    assert.equal(h.events()[1].window.title_marker.state, 'redacted');
    assert.equal(h.events()[1].window.in_scope, false);
    assert.ok(!JSON.stringify(h.lines).includes('private authentication text'));
    const sequences = h.events().map(r => r.capture_seq);
    assert.deepEqual(sequences, [...sequences].sort((a, b) => a - b));
    disconnected(h, [w]);
});

test('utility X11 and normal Wayland credential windows are both observed without enrollment', () => {
    for (const normal of [false, true]) {
        const h = harness(), w = window(A, {normalWindow: normal, utility: !normal,
            resizeable: false, caption: 'Credentials required for private host'});
        h.add(w); h.finish();
        const birth = h.events().find(r => r.event === 'added');
        assert.equal(birth.window.normalWindow.value, normal);
        assert.equal(birth.window.resizeable.value, false);
        assert.equal(birth.window.title_marker.state, 'redacted');
        assert.ok(!JSON.stringify(h.lines).includes('private host'));
        disconnected(h, [w]);
    }
});

test('decorated captions retain only generated tokens and never suffix contents', () => {
    const h = harness(), w = window(A, {caption: TOKEN + ' secret suffix', captionNormal: TOKEN});
    h.add(w); h.finish();
    const data = h.events().find(r => r.event === 'added').window;
    assert.equal(data.title_marker.value, TOKEN);
    assert.equal(data.title_marker.exact, false);
    assert.equal(data.normal_title_marker.value, TOKEN);
    assert.equal(data.normal_title_marker.exact, true);
    assert.ok(!JSON.stringify(h.lines).includes('secret suffix'));
    disconnected(h, [w]);
});

test('unclassified removed windows make scope coverage explicitly incomplete', () => {
    const h = harness(), w = window(A, {resourceClass: '', desktopFileName: '', caption: 'not collected'});
    h.add(w); h.remove(w); h.finish();
    assert.equal(h.end().unresolved_window_count, 1);
    assert.equal(h.end().capture_intact, false);
    assert.ok(!JSON.stringify(h.lines).includes('not collected'));
    disconnected(h, [w]);
});

test('temporary marked window and persistent viewer remain distinct; neither is selected', () => {
    const h = harness(), temporary = window(A, {pid: 20}), viewer = window(B, {pid: 20});
    h.add(temporary); h.remove(temporary); h.add(viewer); h.finish();
    const births = h.events().filter(r => r.event === 'added');
    assert.deepEqual(births.map(r => r.window.uuid), [A, B]);
    assert.equal(h.events().filter(r => r.event === 'removed')[0].window.uuid, A);
    assert.ok(!h.events().some(r => 'selected_uuid' in r || 'managed_id' in r));
    disconnected(h, [temporary, viewer]);
});

test('delayed Wayland caption preserves creation UUID and records marker arrival and loss', () => {
    const h = harness(), viewer = window(A, {pid: 1763, caption: '', captionNormal: ''});
    h.add(viewer);
    viewer.data.caption = 'private progress text';
    viewer.data.captionNormal = 'private progress text';
    viewer.data.captionChanged.emit();
    viewer.data.caption = TOKEN; viewer.data.captionNormal = TOKEN;
    viewer.data.captionChanged.emit();
    viewer.data.caption = TOKEN + ' private compositor suffix';
    viewer.data.captionChanged.emit();
    viewer.data.caption = ''; viewer.data.captionNormal = '';
    viewer.data.captionChanged.emit();
    h.remove(viewer); h.finish();
    const changes = h.events().filter(r => r.event === 'captionChanged');
    assert.equal(changes.length, 4);
    assert.ok(changes.every(r => r.window.uuid === A && r.window.pid.value === 1763));
    assert.equal(changes[0].window.title_marker.state, 'redacted');
    assert.equal(changes[1].window.normal_title_marker.exact, true);
    assert.equal(changes[2].window.title_marker.exact, false);
    assert.equal(changes[2].window.normal_title_marker.exact, true);
    assert.equal(changes[3].window.normal_title_marker.state, 'redacted');
    assert.ok(!JSON.stringify(h.lines).includes('private'));
    assert.ok(changes[1].capture_seq > h.events().find(r => r.event === 'added').capture_seq);
    disconnected(h, [viewer]);
});

test('normal Wayland credentials and concurrent marked viewers remain distinct observations only', () => {
    const c = '33333333-3333-4333-8333-333333333333';
    const h = harness(), auth = window(A, {pid: 1763, caption: 'private credentials', captionNormal: ''}),
        first = window(B, {pid: 1763}), second = window(c, {pid: 1763});
    h.add(auth); h.add(first); h.add(second);
    h.remove(first); h.remove(auth); h.remove(second); h.finish();
    const births = h.events().filter(r => r.event === 'added');
    assert.equal(births[0].window.normalWindow.value, true);
    assert.equal(births[0].window.title_marker.state, 'redacted');
    assert.deepEqual(births.filter(r => r.window.title_marker.exact).map(r => r.window.uuid), [B, c]);
    assert.ok(!JSON.stringify(h.lines).includes('private credentials'));
    assert.ok(!h.events().some(r => 'selected_uuid' in r || 'managed_id' in r));
    assert.equal(h.end().capture_intact, true); // Complete evidence is not unique identity.
    disconnected(h, [auth, first, second]);
});

test('removal uses cached UUID/geometry, disconnects handlers and ignores queued callbacks', () => {
    const h = harness(), w = window(); h.add(w);
    const queued = w.data.frameGeometryChanged.pending()[0];
    w.data.internalId = null; w.data.frameGeometry = null;
    h.remove(w); queued(); h.finish();
    const removed = h.events().find(r => r.event === 'removed');
    assert.equal(removed.window.uuid, A);
    assert.equal(removed.window.frameGeometry.value.width, 1032);
    assert.equal(removed.cached_on_removal, true);
    disconnected(h, [w]);
});

test('workspace activation and activeWindow readback are distinct, with no operator-intent claim', () => {
    const h = harness(), viewer = window(A), other = window(B, {resourceClass: 'other', desktopFileName: 'other'});
    let otherCaptionReads = 0;
    Object.defineProperty(other.data, 'caption', {get() { otherCaptionReads++; return 'secret'; }});
    h.add(viewer); h.add(other);
    h.activate(viewer); h.data.windowActivated.emit(viewer.object);
    h.data.activeWindow = other.object;
    h.data.windowActivated.emit(viewer.object); // explicitly model delayed readback
    h.activate(null); h.finish();
    const active = h.events().filter(r => r.event === 'workspace.windowActivated');
    assert.equal(active.length, 4);
    assert.equal(active[2].activated_uuid, A);
    assert.equal(active[2].observed_active.value, B);
    assert.ok(active.every(r => r.intent === 'unknown'));
    assert.equal(active[3].activated_uuid, null);
    assert.equal(otherCaptionReads, 0);
    assert.ok(!h.events().some(r => r.window?.uuid === B));
    disconnected(h, [viewer, other]);
});

test('interactive movement, geometry changes and explicit markers do not assert physical input', () => {
    const h = harness(), w = window(); h.add(w); h.activate(w);
    w.data.move = true; w.data.interactiveMoveResizeStarted.emit();
    w.data.frameGeometry.x = 50; w.data.interactiveMoveResizeStepped.emit();
    w.data.frameGeometryChanged.emit();
    w.data.move = false; w.data.interactiveMoveResizeFinished.emit();
    h.marker(); h.finish();
    assert.equal(h.events().find(r => r.event === 'interactiveMoveResizeStarted').window.move.value, true);
    assert.equal(h.events().find(r => r.event === 'active_window_marker_request').observed_active.value, A);
    assert.ok(!JSON.stringify(h.lines).includes('operator_initiated'));
    assert.ok(!source.includes('registerScreenEdge') && !source.includes('registerTouchScreenEdge'));
    disconnected(h, [w]);
});

test('unsupported properties and signals are explicit; function-valued getters are never invoked', () => {
    const h = harness({configure({data}) { delete data.windowActivated; }}), w = window();
    let invoked = 0;
    w.data.readyForPainting = () => { invoked++; return true; };
    delete w.data.bufferGeometryChanged;
    h.add(w); h.finish();
    const birth = h.events().find(r => r.event === 'added');
    assert.equal(birth.window.visible.state, 'unsupported');
    assert.equal(birth.window.readyForPainting.state, 'unsupported');
    assert.equal(invoked, 0);
    assert.equal(h.events().find(r => r.event === 'window_signals').supported.bufferGeometryChanged, 'unsupported');
    assert.equal(h.end().capabilities.windowActivated, 'unsupported');
    w.data.bufferGeometryChanged = signal();
    disconnected(h, [w]);
});

test('inaccessible properties do not leak exception strings or authentication/certificate contents', () => {
    const h = harness(), w = window(A, {caption: 'certificate PEM secret'});
    Object.defineProperty(w.data, 'windowRole', {get() { throw new Error('password-is-secret'); }});
    Object.defineProperty(w.data, 'clientGeometry', {get() { throw new Error('private value'); }});
    h.add(w); h.finish();
    const birth = h.events().find(r => r.event === 'added');
    assert.equal(birth.window.windowRole.state, 'inaccessible');
    assert.equal(birth.window.clientGeometry.state, 'inaccessible');
    assert.ok(!/secret|private value|certificate PEM/.test(JSON.stringify(h.lines)));
    disconnected(h, [w]);
});

test('backward wall-clock changes do not break sequence ordering', () => {
    const h = harness(), w = window(); h.add(w); h.setTime(900); h.activate(w); h.finish();
    assert.equal(h.events().find(r => r.event === 'workspace.windowActivated').clock_regressed, true);
    assert.deepEqual(h.events().map(r => r.seq), h.events().map((_, i) => i + 1));
    assert.ok(h.events().every((r, i, a) => i === 0 || r.capture_seq > a[i - 1].capture_seq));
    disconnected(h, [w]);
});

test('record, window and serialized-record bounds stop explicitly without active callbacks', () => {
    for (const [settings, reason] of [
        [{maxRecords: 3}, 'record_limit'], [{maxWindows: 1}, 'window_limit'],
        [{maxRecordBytes: 512}, 'record_size_limit']
    ]) {
        const h = harness({settings}), a = window(), b = window(B);
        h.add(a); h.add(b); a.data.captionChanged.emit(); h.finish(); h.drain();
        assert.equal(h.end().reason, reason);
        assert.equal(h.end().truncated, true);
        assert.equal(h.end().capture_intact, false);
        disconnected(h, [a, b]);
    }
});

test('expiry cleans signals and timer; late expiry, markers and queued events are inert', () => {
    const h = harness({settings: {durationMs: 1234}}), w = window(); h.add(w);
    const pending = w.data.captionChanged.pending()[0];
    assert.equal(h.timers[0].interval, 1234);
    h.timers[0].timeout.emit(); h.drain();
    const count = h.lines.length;
    pending(); h.marker(); h.finish(); h.timers[0].timeout.emit(); h.activate(w);
    assert.equal(h.lines.length, count);
    assert.equal(h.end().reason, 'expired');
    disconnected(h, [w]);
});

test('reaching the record bound during removal does not disconnect a subscription twice', () => {
    const h = harness({settings: {maxRecords: 3}}), w = window();
    h.add(w); h.remove(w); h.drain();
    assert.equal(h.end().reason, 'record_limit');
    assert.equal(h.end().cleanup_failures, 0);
    disconnected(h, [w]);
});

test('missing timer or lifecycle signal fails setup and never leaves observers connected', () => {
    for (const options of [{timer: false}, {configure({data}) { delete data.windowRemoved; }}]) {
        const h = harness(options);
        assert.equal(h.statuses.at(-1).phase, 'failed');
        assert.equal(h.events().length, 0);
        disconnected(h);
    }
});

test('invalid settings fail before observation, including Qt timer overflow', () => {
    for (const settings of [{durationMs: 0}, {durationMs: 2147483648}, {maxRecords: NaN},
        {maxWindows: '5'}, {unknown: true}, {expectedClass: {}}, {shortcutPrefix: 'bad/key'}]) {
        const h = harness({settings});
        assert.equal(h.statuses.at(-1).detail, 'setup_error');
        assert.equal(h.events().length, 0);
        disconnected(h);
    }
});

test('unusable SDL UUID cannot alias another unknown window', () => {
    const h = harness(), w = window(A, {internalId: null}); h.add(w); h.drain();
    assert.equal(h.end().reason, 'identity_unavailable');
    assert.equal(h.end().capture_intact, false);
    disconnected(h, [w]);
});

test('two observers have independent unique identities; baseline windows are labelled', () => {
    const w = window(), a = harness({initial: [w]}), b = harness();
    a.finish(); b.finish();
    assert.notEqual(a.lines[0].observer, b.lines[0].observer);
    assert.equal(a.events().find(r => r.event === 'existing').baseline, true);
    disconnected(a, [w]); disconnected(b);
});

test('disconnect failures are explicit and retained callbacks cannot act after finish', () => {
    const h = harness(), w = window(); h.add(w);
    w.data.captionChanged.disconnect = () => { throw new Error('disconnect failed'); };
    h.finish();
    assert.equal(h.end().cleanup_failures, 1);
    assert.equal(h.end().capture_intact, false);
    const count = h.lines.length; w.data.captionChanged.emit();
    assert.equal(h.lines.length, count);
    assert.deepEqual(w.mutations, []);
});

// Consumer-side validation: console.info returning does not acknowledge delivery.
// Capture completeness requires BOTH boundary records and every transport line.
function validateCapture(lines) {
    assert.ok(lines.length >= 2, 'missing lifecycle boundaries');
    assert.equal(lines[0].kind, 'ready');
    assert.equal(lines.at(-1).kind, 'end');
    const observer = lines[0].observer;
    lines.forEach((line, i) => {
        assert.equal(line.observer, observer);
        assert.equal(line.transport_seq, i + 1);
    });
    const events = lines.slice(1, -1), end = lines.at(-1);
    assert.equal(events.length, end.records);
    events.forEach((line, i) => {
        assert.equal(line.kind, 'event');
        assert.equal(line.seq, i + 1);
        if (i) assert.ok(line.capture_seq > events[i - 1].capture_seq);
    });
    assert.equal(end.capture_intact, true);
    assert.equal(end.truncated, false);
    assert.equal(end.cleanup_failures, 0);
    assert.equal(end.callback_failures, 0);
    assert.equal(end.output_failures, 0);
}

test('default duration matches the 1800-second proof and remains configurable with early cleanup', () => {
    for (const [settings, expected] of [[{}, 1800000], [{durationMs: 3210}, 3210]]) {
        const h = harness({settings});
        assert.equal(h.lines[0].settings.durationMs, expected);
        assert.equal(h.timers[0].interval, expected);
        assert.equal(h.lines[0].format_version, 1);
        h.finish();
        assert.equal(h.end().reason, 'requested');
        validateCapture(h.lines);
        disconnected(h);
    }
});

test('geometry storm exhausts default bound explicitly; no dropped event can look successful', () => {
    const h = harness(), w = window(); h.add(w);
    const queued = w.data.frameGeometryChanged.pending()[0];
    for (let i = 0; i < 2000; i++) {
        w.data.frameGeometry.x = i;
        w.data.frameGeometryChanged.emit();
    }
    h.drain();
    const end = h.end();
    assert.equal(end.reason, 'record_limit');
    assert.equal(end.buffered_records, 1024);
    assert.equal(end.records, 1024);
    assert.equal(end.overflow.event, 'frameGeometryChanged');
    assert.equal(end.overflow.rejected_records, 1);
    assert.equal(end.truncated, true);
    assert.equal(end.capture_intact, false);
    assert.throws(() => validateCapture(h.lines));
    const count = h.lines.length;
    queued(); h.finish();
    assert.equal(h.lines.length, count);
    disconnected(h, [w]);
});

test('transport boundaries and sequence detect loss, duplication, reordering and interrupted export', () => {
    const h = harness(), w = window(); h.add(w); h.activate(w); h.finish();
    validateCapture(h.lines);
    assert.match(h.end().delivery, /pending acknowledgement/);
    for (const broken of [
        h.lines.slice(1), h.lines.slice(0, -1),
        h.lines.filter((_, i) => i !== 2),
        [h.lines[0], h.lines[1], h.lines[1], ...h.lines.slice(2)],
        [h.lines[0], h.lines[2], h.lines[1], ...h.lines.slice(3)]
    ]) assert.throws(() => validateCapture(broken));
    disconnected(h, [w]);
});

test('callback exception ends capture without escaping into KWin and queued callbacks are inert', () => {
    let clock;
    const h = harness({configure({context}) { clock = context.Date; }}), w = window();
    h.add(w);
    const queued = w.data.captionChanged.pending()[0];
    clock.now = () => { throw new Error('sensitive native exception'); };
    assert.doesNotThrow(() => w.data.frameGeometryChanged.emit()); h.drain();
    assert.equal(h.end().reason, 'callback_error');
    assert.equal(h.end().callback_failures, 1);
    assert.equal(h.end().capture_intact, false);
    const count = h.lines.length;
    queued(); h.marker(); h.finish();
    assert.equal(h.lines.length, count);
    assert.ok(!JSON.stringify(h.lines).includes('sensitive native exception'));
    disconnected(h, [w]);
});

test('timer and shortcut setup exceptions fail closed and disconnect existing observations', () => {
    for (const fault of ['timer', 'shortcut']) {
        const h = harness({configure({context, Timer}) {
            if (fault === 'timer') Timer.prototype.start = () => { throw new Error('native timer error'); };
            else context.registerShortcut = () => { throw new Error('native shortcut error'); };
        }});
        assert.equal(h.statuses.at(-1).phase, 'failed');
        assert.equal(h.events().length, 0);
        disconnected(h);
    }
});

test('marker invoked after activating Konsole refers only to Konsole, never the previous viewer', () => {
    const h = harness(), viewer = window(A), terminal = window(B, {
        resourceClass: 'org.kde.konsole', desktopFileName: 'org.kde.konsole'
    });
    h.add(viewer); h.add(terminal);
    h.activate(viewer); h.activate(terminal); h.marker(); h.finish();
    const marker = h.events().find(r => r.event === 'active_window_marker_request');
    assert.equal(marker.observed_active.value, B);
    assert.match(marker.scope, /no previous-viewer confirmation/);
    assert.equal(marker.intent, 'explicit invocation; operator provenance unverified');
    assert.ok(!Object.hasOwn(marker, 'previous_viewer_uuid'));
    validateCapture(h.lines);
    disconnected(h, [viewer, terminal]);
});

test('persisted ready plus observe acknowledgement precede launch gate; transition events are retained', () => {
    const waiting = [];
    const h = harness({transport(call, reply, lines) { waiting.push({call, reply, lines}); }});
    const w = window(); h.add(w); h.activate(w);
    assert.equal(h.statuses.length, 0);
    assert.equal(waiting.length, 1);
    assert.equal(waiting[0].call.value.kind, 'ready');
    function ack() {
        const {call, reply, lines} = waiting.shift();
        if (call.method === 'Append') lines.push(call.value);
        call.callback(JSON.stringify(reply));
        h.drain();
    }
    ack();
    assert.equal(h.statuses.length, 0);
    assert.equal(waiting[0].call.method, 'Probe');
    ack();
    assert.match(h.statuses.at(-1).detail, /proof may begin/);
    h.finish();
    while (waiting.length) ack();
    validateCapture(h.lines);
    assert.ok(h.events().some(r => r.event === 'added' && r.window.uuid === A));
    assert.ok(h.events().some(r => r.event === 'workspace.windowActivated'));
    disconnected(h, [w]);
});

test('lost ready callback (including native D-Bus error) times out without a launch gate', () => {
    const h = harness({transport() { /* KWin suppresses callbacks on native D-Bus errors. */ }});
    const w = window(); h.add(w);
    const pending = w.data.captionChanged.pending()[0];
    h.timers[1].timeout.emit();
    assert.equal(h.statuses.at(-1).detail, 'acknowledgement_timeout');
    assert.ok(!h.statuses.some(r => /proof may begin/.test(r.detail)));
    const calls = h.calls.length;
    pending(); h.finish();
    assert.equal(h.calls.length, calls);
    disconnected(h, [w]);
});

test('late ready acknowledgement after expiry cannot revive observation or launch permission', () => {
    let saved;
    const h = harness({transport(call, reply) { saved = () => call.callback(JSON.stringify(reply)); }});
    h.timers[1].timeout.emit(); saved(); h.drain();
    assert.equal(h.calls.length, 1);
    assert.equal(h.statuses.at(-1).phase, 'failed');
    disconnected(h);
});

test('missing or malformed persistence acknowledgement fails without trusting another run', () => {
    for (const change of [r => { r.persisted = false; }, r => { r.transport_seq = 99; },
        r => { r.run_id = 'b'.repeat(32); }, r => { r.observer = 'rdp-diag-other'; },
        r => { r.ok = false; }, r => { r.protocol = 2; }]) {
        const h = harness({transport(call, reply) { change(reply); call.callback(JSON.stringify(reply)); }});
        assert.equal(h.statuses.at(-1).detail, 'invalid_acknowledgement');
        assert.equal(h.calls[0].value.kind, 'ready');
        disconnected(h);
    }
    const h = harness({transport(call) { call.callback('{'); }});
    assert.equal(h.statuses.at(-1).phase, 'failed'); disconnected(h);
});

test('receiver disappearance during observation stops subscriptions and never retargets a new owner', () => {
    let vanished = false;
    const h = harness({transport(call, reply, lines) {
        if (vanished) return;
        if (call.method === 'Append') lines.push(call.value);
        call.callback(JSON.stringify(reply));
    }});
    const w = window(); h.add(w); vanished = true;
    h.timers[2].timeout.emit();
    h.timers[1].timeout.emit();
    assert.equal(h.statuses.at(-1).detail, 'acknowledgement_timeout');
    assert.equal(h.calls.at(-1).method, 'Probe');
    disconnected(h, [w]);
});

test('receiver refusal of observe handshake prevents readiness even after ready was persisted', () => {
    const h = harness({transport(call, reply, lines) {
        if (call.method === 'Append') lines.push(call.value);
        else reply.native_launch_ready = false;
        call.callback(JSON.stringify(reply));
    }});
    assert.equal(h.lines[0].kind, 'ready');
    assert.equal(h.statuses.at(-1).detail, 'receiver_not_observing');
    disconnected(h);
});

test('ready may be pending when early finish occurs; no later launch gate is opened', () => {
    const waiting = [];
    const h = harness({transport(call, reply, lines) { waiting.push({call, reply, lines}); }});
    h.finish();
    while (waiting.length) {
        const {call, reply, lines} = waiting.shift();
        if (call.method === 'Append') lines.push(call.value);
        call.callback(JSON.stringify(reply)); h.drain();
    }
    assert.ok(!h.statuses.some(r => /proof may begin/.test(r.detail)));
    assert.equal(h.calls.filter(c => c.method === 'Probe' && c.value.action === 'observe').length, 0);
    validateCapture(h.lines);
    disconnected(h);
});

test('all observation subscriptions are disconnected before export; end needs final receipt acknowledgement', () => {
    let holdEnd = false;
    const h = harness({transport(call, reply, lines) {
        if (call.value.kind === 'end') { holdEnd = true; return; }
        if (call.method === 'Append') lines.push(call.value);
        call.callback(JSON.stringify(reply));
    }});
    const w = window(); h.add(w); h.finish();
    assert.equal(holdEnd, true);
    assert.equal(w.data.frameGeometryChanged.count(), 0);
    assert.equal(h.data.windowAdded.count(), 0);
    assert.ok(!h.statuses.some(r => r.phase === 'complete'));
    h.timers[1].timeout.emit();
    assert.equal(h.statuses.at(-1).phase, 'failed');
    disconnected(h, [w]);
});

test('total export timeout independently stops a progressing drain and ignores its late callback', () => {
    let delayed;
    const h = harness({transport(call, reply, lines) {
        if (call.value.kind === 'event') { delayed = () => call.callback(JSON.stringify(reply)); return; }
        if (call.method === 'Append') lines.push(call.value);
        call.callback(JSON.stringify(reply));
    }});
    h.finish(); h.timers[3].timeout.emit(); delayed(); h.drain();
    assert.equal(h.statuses.at(-1).detail, 'export_timeout');
    disconnected(h);
});

test('full 1024-event export fits default deadline even at almost the per-call acknowledgement limit', () => {
    const waiting = [];
    let inFlight = 0, maxInFlight = 0, elapsed = 0, exporting = false;
    const h = harness({transport(call, reply, lines) {
        maxInFlight = Math.max(maxInFlight, ++inFlight);
        waiting.push(() => {
            inFlight--;
            if (exporting) elapsed += 2999;
            if (call.method === 'Append') lines.push(call.value);
            call.callback(JSON.stringify(reply));
        });
    }});
    while (waiting.length) { waiting.shift()(); h.drain(); }
    const w = window(); h.add(w);
    for (let i = 0; i < 1021; i++) w.data.frameGeometryChanged.emit();
    exporting = true; h.finish();
    while (waiting.length) { waiting.shift()(); h.drain(); }
    assert.equal(maxInFlight, 1);
    assert.equal(h.end().records, 1024);
    assert.equal(h.end().truncated, false);
    assert.ok(elapsed < h.lines[0].settings.exportTimeoutMs);
    assert.equal(elapsed, 1027*2999);
    validateCapture(h.lines);
    disconnected(h, [w]);
});

test('deadline and receiver settings are validated before making any call', () => {
    for (const settings of [{exportTimeoutMs: 30000}, {receiverUniqueName: 'org.joetoo.Other'},
        {runId: 'not-a-run'}, {maxTotalBytes: 1000}, {ackTimeoutMs: 0}, {livenessIntervalMs: Infinity}]) {
        const h = harness({settings});
        assert.equal(h.calls.length, 0);
        assert.equal(h.statuses.at(-1).phase, 'failed');
        disconnected(h);
    }
});

test('actual observer envelopes are available for independent Python replay', () => {
    const h = harness(), w = window(); h.add(w); h.activate(w); h.marker(); h.remove(w); h.finish();
    validateCapture(h.lines);
    if (process.env.JOETOO_DIAGNOSTIC_FIXTURE_OUTPUT) {
        fs.writeFileSync(process.env.JOETOO_DIAGNOSTIC_FIXTURE_OUTPUT,
            JSON.stringify(h.lines), {flag: 'wx', mode: 0o600});
    }
    disconnected(h, [w]);
});
