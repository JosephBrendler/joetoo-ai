// Stage 0 only: existing resident observations + SYNTHETIC A2 contract traces.
// No future resolver/broker/XCB implementation is imported or exercised here.
// Fake sender identities, routing, synchronous signals and cleanup outcomes are
// assumptions supplied by this fixture, not evidence about Qt, D-Bus or the OS.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {TextDecoder} = require('node:util');
const resident = fs.readFileSync(path.join(__dirname, '../joetoo-kwin-resident.js'), 'utf8');
const BRIDGE = 'org.joetoo.KWinBridge', KWIN = ':1.20', BROKER = ':1.30';
const APP = 'com.freerdp.client.sdl3', INSTANCE = 'sdl-freerdp';
const UUID = '11111111-1111-4111-8111-111111111111';
const OTHER = '22222222-2222-4222-8222-222222222222';
// Deterministic publication identities are test data, not cryptographic randomness.
const publication = n => ({marker: 'joetoo-rdp-' + n.toString(16).padStart(64, '0'),
    nonce: (n + 4096).toString(16).padStart(64, '0')});
const BOUNDS = Object.freeze({registration: 1000, ready: 200, mapping: 200, cleanup: 100, bytes: 8192});
const clone = value => JSON.parse(JSON.stringify(value));

function signal() {
    const callbacks = new Set();
    return {connect: fn => callbacks.add(fn), disconnect: fn => callbacks.delete(fn),
        emit: (...args) => {for (const fn of [...callbacks]) fn(...args);}, count: () => callbacks.size};
}

// This is only a vector validator, NOT the proposed native XCB parser.
function properties(identity = {}) {
    const {pid = 42, xid = 101, marker, nonce} = {...publication(1), ...identity};
    const p = (type, format, value) => ({type, format, bytes_after: 0, value: Buffer.from(value)});
    return {
        proof: p('UTF8_STRING', 8, JSON.stringify({protocol: 1, role: 'desktop_viewer',
            pid, marker, epoch: 1, xid, publication_nonce: nonce})),
        pid: p('CARDINAL', 32, [pid, 0, 0, 0]), // Synthetic little-endian vector, not ABI proof.
        wmclass: p('STRING', 8, INSTANCE + '\0' + APP + '\0'),
        name: p('UTF8_STRING', 8, marker)
    };
}
function validProperties(p, identity = {}) {
    const {pid = 42, xid = 101, marker, nonce} = {...publication(1), ...identity};
    try {
        const required = {proof: ['UTF8_STRING', 8], pid: ['CARDINAL', 32],
            wmclass: ['STRING', 8], name: ['UTF8_STRING', 8]};
        let bytes = 0;
        for (const [key, [type, format]] of Object.entries(required)) {
            const v = p[key];
            if (!v || v.type !== type || v.format !== format || v.bytes_after !== 0 || !Buffer.isBuffer(v.value)) return false;
            bytes += v.value.length;
        }
        if (bytes > BOUNDS.bytes || p.pid.value.length !== 4 || p.pid.value.readUInt32LE() !== pid) return false;
        const parts = p.wmclass.value.toString('latin1').split('\0');
        if (parts.length !== 3 || parts[0] !== INSTANCE || parts[1] !== APP || parts[2] !== '') return false;
        const name = new TextDecoder('utf-8', {fatal: true}).decode(p.name.value);
        if (name !== marker || !p.name.value.equals(Buffer.from(marker))) return false;
        const raw = new TextDecoder('utf-8', {fatal: true}).decode(p.proof.value);
        if (!/^[\x20-\x7e]+$/.test(raw)) return false;
        assert.deepEqual(JSON.parse(raw), {protocol: 1, role: 'desktop_viewer', pid,
            marker, epoch: 1, xid, publication_nonce: nonce});
        return true;
    } catch {return false;}
}

// A trace checker for the PROPOSED protocol. It deliberately has access to the
// entire synthetic send/delivery log to detect violated transport assumptions.
// A real broker cannot use this oracle; its ordering premise must be established
// independently as required by contract §5.4 before any implementation acceptance.
class ProtocolTrace {
    constructor() {
        this.now = 0; this.owner = BROKER; this.kwin = KWIN; this.uid = 1000;
        this.messages = []; this.jobs = []; this.current = null; this.log = [];
        this.revision = 0; this.source = null; this.synced = false;
        this.history = []; this.windows = new Map(); this.incomplete = false;
        this.sequence = 0; this.next = 0; this.workerNext = 0; this.properties = null;
        this.childLive = true;
    }
    send(method, body, {sender = KWIN, uid = 1000, destination = BROKER} = {}) {
        const m = {method, body: clone(body), sender, uid, destination,
            recipient: destination === BRIDGE ? this.owner : destination,
            sent: ++this.sequence, delivered: false, completed: false, callbackDone: false};
        this.messages.push(m); return m;
    }
    deliver(m) {
        assert.equal(m.delivered, false);
        m.delivered = true;
        // Fault injection may violate FIFO. Such a trace is not valid fence evidence.
        m.reordered = this.messages.some(a => a.sent < m.sent && !a.delivered &&
            a.sender === m.sender && a.recipient === m.recipient);
    }
    finish(m) {
        assert.ok(m.delivered && !m.completed);
        m.completed = true;
        if (m.sender !== this.kwin || m.uid !== this.uid || m.recipient !== this.owner) {
            m.reply = {error: 'AccessDenied'}; return; // Cannot cancel another caller's job.
        }
        if (m.reordered || this.messages.some(a => a.sent < m.sent && !a.completed &&
                a.sender === m.sender && a.recipient === m.recipient)) {
            this.fail('ordering_precondition'); return;
        }
        if (m.method === 'ObserveWindow' || m.method === 'SyncInventory') return this.observe(m);
        const j = this.current, b = m.body;
        // A stale/unknown job cannot consume a current challenge or its resources.
        if (!j || b.job_id !== j.id || (b.request_id && b.request_id !== j.request)) return;
        if (j.terminal) {m.reply = j.replyCache.get(JSON.stringify(b)); return;}
        if (this.expired(j)) return;
        if (b.source !== this.source || b.source !== j.source) return this.fail('source_lost');
        if (m.method === 'TakeSdlX11Identity') {
            if (b.bootstrap_nonce !== j.bootstrap || j.taken) return;
            j.taken = true;
            m.reply = {protocol: 1, action: j.phase === 'ready' ? 'ready' : 'resolve',
                job_id: j.id, challenge: j.challenge, source: j.source};
            return;
        }
        if (b.challenge !== j.challenge || !j.taken) return;
        const serialized = JSON.stringify(b);
        if (j.complete) {
            if (j.complete !== serialized) return this.fail('conflicting_reply');
            m.reply = j.replyCache.get(serialized); return;
        }
        if (j.phase === 'ready') {
            if (b.purpose !== 'ready' || b.supported !== true) return this.fail('unsupported');
            j.readyAck = true;
        } else {
            if (b.purpose !== 'map' || b.status !== 'match' || b.xid !== j.xid ||
                b.epoch !== 1 || b.publication_nonce !== j.nonce || b.window_uuid !== j.uuid ||
                b.observed_pid !== j.pid || b.resource_class !== APP ||
                b.normal_window !== true || b.marker_match !== true || !this.historyOkay(j)) return this.fail('bad_fence');
            j.fence = this.revision;
            this.worker(j, 'post');
        }
        j.complete = serialized;
        m.reply = {protocol: 1, action: 'stop', job_id: j.id, accepted: true, barrier_revision: this.revision};
        j.replyCache.set(serialized, clone(m.reply));
        this.progress(j);
    }
    callback(m) {
        assert.ok(m.completed);
        if (m.callbackDone) return false; // Duplicate transport delivery is inert.
        m.callbackDone = true;
        const j = this.current;
        if (!j || j.terminal || m.body.job_id !== j.id || !m.reply || this.expired(j)) return;
        if (m.method === 'TakeSdlX11Identity') {
            if (j.phase === 'ready') this.sendComplete({supported: true, reason: null});
            else this.mappingEvent();
        }
    }
    pump({holdMapping = false} = {}) {
        for (let i = 0; i < this.messages.length; i++) {
            const m = this.messages[i];
            if (holdMapping && m.method === 'CompleteSdlX11Identity' && m.body.purpose === 'map' && !m.completed) return;
            if (!m.delivered) this.deliver(m);
            if (!m.completed) this.finish(m);
            if (!m.callbackDone) this.callback(m);
        }
    }
    observe(m) {
        const b = m.body;
        if (this.source && b.source !== this.source) return this.fail('source_lost');
        if (b.revision !== this.revision + 1) {this.incomplete = true; this.fail('history_incomplete'); return;}
        this.source = b.source; this.revision = b.revision;
        if (m.method === 'SyncInventory') {
            this.synced = true; this.windows = new Map(b.windows.map(w => [w.uuid, w]));
        } else {
            this.history.push(b);
            if (b.event === 'removed') this.windows.delete(b.window.uuid);
            else this.windows.set(b.window.uuid, b.window);
        }
    }
    begin({pid = 42, xid = 101, uuid = UUID} = {}) {
        if ((this.current && !this.current.terminal) || this.jobs.some(j => j.resources.size)) return null;
        assert.ok(this.synced);
        const n = ++this.next;
        const j = {request: n.toString(16).padStart(32, '0'), id: (n + 100).toString(16).padStart(32, '0'),
            bootstrap: (n + 200).toString(16).padStart(64, '0'), challenge: (n + 300).toString(16).padStart(64, '0'),
            source: this.source, owner: this.owner, kwin: this.kwin, pid, xid, uuid, ...publication(n),
            phase: 'ready', started: this.now, deadline: this.now + BOUNDS.registration,
            phaseEnd: this.now + BOUNDS.ready, replyCache: new Map(),
            resources: new Map([['script', {kind: 'script', owner: this.kwin, id: null}]]), terminal: null};
        this.worker(j, 'probe'); this.properties = properties(j);
        this.jobs.push(j); this.current = j; this.log.push('automatic:ready-load'); return j;
    }
    loaded(j, id) {
        const r = j.resources.get('script');
        if (!r || r.owner !== this.kwin || r.id !== null) return false;
        r.id = id;
        if (j !== this.current || j.terminal || this.expired(j)) {this.log.push('cleanup-only:late-load'); return false;}
        this.send('TakeSdlX11Identity', {protocol: 1, purpose: j.phase, job_id: j.id,
            bootstrap_nonce: j.bootstrap, source: j.source});
        return true;
    }
    sendComplete(extra = {}) {
        const j = this.current;
        return this.send('CompleteSdlX11Identity', {protocol: 1, purpose: j.phase,
            ...(j.phase === 'map' ? {request_id: j.request} : {}), job_id: j.id,
            challenge: j.challenge, source: j.source, ...extra});
    }
    progress(j) {
        if (j !== this.current || j.terminal || this.expired(j) || j.resources.size) return;
        if (j.phase === 'ready' && j.readyAck && j.probeOkay) {
            j.phase = 'armed'; j.floor = this.revision; j.baseline = new Set(this.windows.keys());
            this.log.push('Begin-return:spawn-permitted');
        } else if (j.phase === 'map' && j.fence && j.postOkay && this.historyOkay(j) && this.childLive) {
            j.terminal = Object.freeze({state: 'registered', uuid: j.uuid, request: j.request, placement: 'not_requested'});
        }
    }
    spawn() {assert.equal(this.current.phase, 'armed'); this.log.push('direct-child:synthetic');}
    readyEvidence() {
        const j = this.current; assert.equal(j.phase, 'armed');
        j.id = (this.next + 1000).toString(16).padStart(32, '0');
        j.bootstrap = (this.next + 2000).toString(16).padStart(64, '0');
        j.phase = 'map'; j.phaseEnd = Math.min(j.deadline, this.now + BOUNDS.mapping);
        j.taken = false; j.complete = null; j.challenge = (this.next + 3000).toString(16).padStart(64, '0');
        this.worker(j, 'pre');
        this.log.push('automatic:precheck');
    }
    mappingEvent() {
        const j = this.current;
        if (!j || j.terminal || j.phase !== 'map' || !j.taken || j.mappingSent || this.expired(j)) return;
        // Resolve only the requested native XID; never the most recently added window.
        const w = this.getClient(j.xid);
        if (!w) return; // Only synthetic event callbacks can advance this lookup.
        j.mappingSent = true;
        this.sendComplete({epoch: 1, xid: j.xid, publication_nonce: j.nonce, status: 'match',
            window_uuid: w.internalId, observed_pid: w.pid, resource_class: w.resourceClass,
            normal_window: w.normalWindow, marker_match: w.caption === j.marker, reason: null});
    }
    historyOkay(j) {
        const events = this.history.filter(b => b.revision > j.floor);
        const w = this.windows.get(j.uuid);
        return this.synced && !this.incomplete && this.source === j.source && this.owner === j.owner &&
            this.kwin === j.kwin && this.childLive && !j.baseline.has(j.uuid) &&
            events.some(b => b.event === 'added' && b.window.uuid === j.uuid) &&
            !events.some(b => b.window.caption === j.marker && b.window.uuid !== j.uuid) &&
            !events.some(b => b.window.uuid === j.uuid && (b.event === 'removed' ||
                b.window.caption !== j.marker || b.window.pid !== j.pid || b.window.resource_class !== APP)) &&
            w && w.pid === j.pid && w.resource_class === APP && w.resource_name === INSTANCE && w.caption === j.marker;
    }
    worker(j, key) {
        // A broker owner can own many workers. The acknowledgement must also
        // identify this exact allocation, across phases and successive launches.
        j.resources.set(key, {kind: 'worker', owner: this.owner,
            token: j.request + ':worker:' + (++this.workerNext)});
    }
    settle(j, key, {owner, id, token, unloaded = true, reaped = true, exit = 0} = {}) {
        const r = j.resources.get(key);
        if (!r || owner !== r.owner || (r.kind === 'script' && (r.id === null || id !== r.id || !unloaded)) ||
                (r.kind === 'worker' && (token !== r.token || !reaped))) return false;
        j.resources.delete(key);
        if (j !== this.current || j.terminal) return true; // Cleanup only: never revive old work.
        if (this.expired(j)) return true;
        if (r.kind === 'worker') {
            if (exit !== 0 || (key !== 'probe' && !validProperties(this.properties, j))) {
                this.fail('native_evidence'); return true;
            }
            if (key === 'probe') j.probeOkay = true;
            if (key === 'post') j.postOkay = true;
            if (key === 'pre') {
                j.resources.set('script', {kind: 'script', owner: this.kwin, id: null});
                this.log.push('automatic:map-load');
            }
        }
        this.progress(j); return true;
    }
    fail(reason) {
        const j = this.current;
        if (j && !j.terminal) {j.terminal = Object.freeze({state: 'failed', reason}); j.cleanupEnd = this.now + 2 * BOUNDS.cleanup;}
    }
    expired(j) {
        if (this.now >= Math.min(j.deadline, j.phase === 'armed' ? j.deadline : j.phaseEnd)) this.fail('expired');
        return !!j.terminal;
    }
    tick(amount) {this.now += amount; if (this.current && !this.current.terminal) this.expired(this.current);}
    cancel() {this.fail('cancelled');}
    replace({owner = this.owner, kwin = this.kwin, source = this.source} = {}) {
        this.owner = owner; this.kwin = kwin; this.source = source; this.fail('source_lost');
    }
}

function fixture(existing = []) {
    const trace = new ProtocolTrace(), shortcuts = new Map(), windows = new Map(), mutationCalls = [];
    const deny = name => () => {mutationCalls.push(name); throw Error('GUI mutation forbidden: ' + name);};
    const readonly = target => new Proxy(target, {set() {deny('write')();}, defineProperty() {deny('define')();}, deleteProperty() {deny('delete')();}});
    function makeWindow(uuid = UUID, caption = trace.current?.marker ?? publication(1).marker) {
        const state = {internalId: uuid, caption, pid: trace.current?.pid ?? 42, normalWindow: true, deleted: false,
            resourceClass: APP, resourceName: INSTANCE, desktopFileName: APP, onAllDesktops: false,
            desktops: Object.freeze([{x11DesktopNumber: 1}]), frameGeometry: readonly({x: 3, y: 4, width: 500, height: 400}),
            frameGeometryChanged: signal(), desktopsChanged: signal(), captionChanged: signal(),
            desktopFileNameChanged: signal(), windowClassChanged: signal(),
            closeWindow: deny('close'), raise: deny('raise'), setMaximize: deny('maximize')};
        return {state, win: readonly(state)};
    }
    const added = signal(), removed = signal();
    const workspace = readonly({stackingOrder: Object.freeze(existing), activeWindow: null,
        desktops: Object.freeze([{x11DesktopNumber: 1}]), windowAdded: added, windowRemoved: removed,
        getClient: xid => windows.get(xid), raiseWindow: deny('raise'), lowerWindow: deny('lower'),
        activateWindow: deny('focus')});
    const lookups = [];
    trace.getClient = xid => {lookups.push(xid); return workspace.getClient(xid);};
    const timers = [];
    function QTimer() {this.timeout = signal(); this.start = () => timers.push(this); this.stop = () => {};}
    const context = vm.createContext({workspace, QTimer, console: {warn: deny('warning')},
        registerShortcut: (name, _label, _key, callback) => shortcuts.set(name, () => {deny('shortcut:' + name)(); callback();}),
        callDBus: (destination, _path, _iface, method, payload, ...args) => {
            // Existing generic windowAdded also asks TakeLaunch. Supply no work;
            // this read request must not be mistaken for a placement invocation.
            if (method === 'TakeLaunch') {args.at(-1)(''); return;}
            assert.ok(['ObserveWindow', 'SyncInventory'].includes(method), 'unexpected resident method: ' + method);
            trace.send(method, JSON.parse(payload), {destination});
        }}, {codeGeneration: {strings: false, wasm: false}});
    vm.runInContext(resident, context, {timeout: 1000});
    trace.pump();
    return {trace, shortcuts, timers, makeWindow, mutationCalls, lookups,
        add(w, xid = 101) {windows.set(xid, w.win); added.emit(w.win); trace.mappingEvent();},
        change(w, changes) {Object.assign(w.state, changes); w.state.captionChanged.emit();},
        remove(w, xid = 101) {windows.delete(xid); removed.emit(w.win);},
        quiet() {assert.deepEqual(mutationCalls, []); assert.equal(timers.length, 0);}};
}
// Only tests synthesizing a particular worker's own acknowledgement use this
// helper. Wrong/stale acknowledgements below carry independently captured tokens.
function workerAck(j, key, extra = {}) {
    return {owner: BROKER, token: j.resources.get(key)?.token, ...extra};
}
function prepared(f = fixture(), options = {}) {
    const t = f.trace, j = t.begin(options);
    assert.throws(() => t.spawn());
    t.loaded(j, 7); t.pump();
    assert.equal(j.phase, 'ready'); // Ready reply is not cleanup or spawn permission.
    t.settle(j, 'probe', workerAck(j, 'probe')); t.settle(j, 'script', {owner: KWIN, id: 7});
    assert.equal(j.phase, 'armed'); t.spawn(); f.quiet(); return f;
}
function mapping(f, {add = true, holdReply = false} = {}) {
    const t = f.trace, j = t.current;
    t.readyEvidence(); t.settle(j, 'pre', workerAck(j, 'pre'));
    if (add) {f.viewer = f.makeWindow(j.uuid); f.add(f.viewer, j.xid);}
    t.loaded(j, 8); t.pump({holdMapping: holdReply}); return j;
}
function commit(f) {
    const t = f.trace, j = t.current;
    t.settle(j, 'post', workerAck(j, 'post')); t.settle(j, 'script', {owner: KWIN, id: 8});
    f.quiet(); return j.terminal;
}

test('existing resident: ordered inventory/add/change/remove snapshots, no shortcut or GUI action', () => {
    const f = fixture(), t = f.trace, w = f.makeWindow();
    f.add(w); f.change(w, {caption: w.state.caption + '-changed'}); f.remove(w); t.pump();
    assert.deepEqual(t.messages.map(m => m.method), ['SyncInventory', 'ObserveWindow', 'ObserveWindow', 'ObserveWindow']);
    assert.deepEqual(t.history.map(b => b.event), ['added', 'changed', 'removed']);
    assert.deepEqual(t.messages.map(m => m.body.revision), [1, 2, 3, 4]);
    assert.equal(new Set(t.messages.map(m => m.body.source)).size, 1);
    assert.ok(t.messages.every(m => m.destination === BRIDGE));
    assert.equal(t.history.at(-1).window.uuid, UUID);
    assert.equal(w.state.captionChanged.count(), 0); f.quiet();
});
test('synthetic: automatic readiness, precheck/mapping, fenced reply and cleanup precede success', () => {
    const f = prepared(), j = mapping(f);
    assert.equal(j.fence, f.trace.revision); assert.equal(j.terminal, null);
    f.trace.settle(j, 'post', workerAck(j, 'post', {reaped: false}));
    assert.equal(j.terminal, null); assert.equal(f.trace.begin(), null);
    assert.deepEqual(commit(f), {state: 'registered', uuid: UUID, request: j.request, placement: 'not_requested'});
    assert.deepEqual(f.trace.log, ['automatic:ready-load', 'Begin-return:spawn-permitted',
        'direct-child:synthetic', 'automatic:precheck', 'automatic:map-load']);
    assert.equal(j.resources.size, 0);
});
test('synthetic: READY before added waits for a synthetic lifecycle event, not human input', () => {
    const f = prepared(), j = mapping(f, {add: false});
    assert.equal(j.mappingSent, undefined);
    f.add(f.makeWindow()); f.trace.pump(); assert.equal(commit(f).state, 'registered');
});

for (const fault of ['missing', 'delayed_delivery', 'delayed_handler', 'reordered', 'evicted', 'wrong_sender']) {
    test('synthetic fence rejects ' + fault + ' added evidence', () => {
        const f = prepared(), t = f.trace, j = t.current;
        t.readyEvidence(); t.settle(j, 'pre', workerAck(j, 'pre'));
        const w = f.makeWindow(); f.add(w);
        const obs = t.messages.at(-1);
        if (fault === 'missing') {t.messages.pop(); t.sequence--;}
        if (fault === 'wrong_sender') obs.sender = ':1.99';
        if (fault === 'evicted') t.incomplete = true;
        t.loaded(j, 8);
        const take = t.messages.at(-1);
        // Deliberately bypass the normal pump to control transport and handler order.
        if (fault === 'delayed_handler') t.deliver(obs);
        if (!['missing', 'delayed_delivery', 'delayed_handler', 'reordered'].includes(fault)) {
            t.deliver(obs); t.finish(obs);
        }
        t.deliver(take); t.finish(take); t.callback(take);
        if (!j.terminal) t.pump();
        assert.notEqual(j.terminal?.state, 'registered');
        if (!j.terminal) {t.tick(BOUNDS.mapping); assert.equal(j.terminal.state, 'failed');}
        f.quiet();
    });
}
for (const fault of ['owner', 'connection', 'stale_resolution', 'uid', 'source']) {
    test('synthetic rejects changed ' + fault + ' provenance', () => {
        const f = prepared(), t = f.trace, j = mapping(f, {holdReply: true});
        const m = t.messages.at(-1);
        if (fault === 'owner') t.replace({owner: ':1.31'});
        if (fault === 'source') t.replace({source: 'replacement'});
        if (fault === 'connection') m.sender = ':1.99';
        if (fault === 'uid') m.uid = 1001;
        if (fault === 'stale_resolution') {m.recipient = ':1.31'; m.destination = BRIDGE;}
        t.pump(); assert.notEqual(commit(f)?.state, 'registered');
        t.tick(BOUNDS.mapping); assert.equal(j.terminal.state, 'failed');
        assert.equal(t.current, j); f.quiet();
    });
}

test('synthetic: duplicates cache the fence; conflict before commit fails, terminal remains stable', () => {
    const f = prepared(), t = f.trace, j = mapping(f), body = JSON.parse(j.complete);
    const same = t.send('CompleteSdlX11Identity', body); t.pump();
    assert.deepEqual(same.reply, j.replyCache.get(j.complete));
    const conflict = {...body, xid: 102}; t.send('CompleteSdlX11Identity', conflict); t.pump();
    assert.equal(j.terminal.reason, 'conflicting_reply');
    const terminal = j.terminal; t.cancel(); commit(f); t.tick(1000);
    assert.equal(j.terminal, terminal); f.quiet();
});
for (const fault of ['challenge', 'job_id', 'request_id', 'expiry']) {
    test('synthetic: stale/forged/cross-request ' + fault + ' cannot complete mapping', () => {
        const f = prepared(), t = f.trace, j = t.current;
        t.readyEvidence(); t.settle(j, 'pre', workerAck(j, 'pre')); f.add(f.makeWindow());
        t.loaded(j, 8);
        // Process observations and Take, but hold the synthesized Complete.
        for (const m of [...t.messages].filter(m => !m.completed)) {t.deliver(m); t.finish(m); t.callback(m);}
        const m = t.messages.at(-1);
        if (fault === 'expiry') t.tick(BOUNDS.mapping);
        else m.body[fault] = 'f'.repeat(fault === 'challenge' ? 64 : 32);
        t.pump(); assert.notEqual(commit(f)?.state, 'registered');
        t.tick(BOUNDS.registration); assert.equal(j.terminal.state, 'failed'); f.quiet();
    });
}

test('synthetic: lost callbacks, late load/unload/reap retain ownership and never renew deadlines', () => {
    const f = fixture(), t = f.trace, j = t.begin(), deadline = j.phaseEnd;
    t.loaded(j, 7); const take = t.messages.at(-1); t.deliver(take); t.finish(take);
    // No Take callback delivered: no Complete/spawn; watchdog alone fails.
    t.tick(BOUNDS.ready); assert.equal(j.terminal.reason, 'expired');
    const terminal = j.terminal; t.callback(take);
    assert.equal(t.messages.filter(m => m.method === 'CompleteSdlX11Identity').length, 0);
    assert.equal(t.settle(j, 'script', {owner: KWIN, id: 7, unloaded: false}), false);
    assert.equal(t.settle(j, 'probe', workerAck(j, 'probe', {reaped: false})), false);
    t.tick(2 * BOUNDS.cleanup); assert.equal(t.begin(), null); assert.equal(j.phaseEnd, deadline);
    t.settle(j, 'script', {owner: KWIN, id: 7}); t.settle(j, 'probe', workerAck(j, 'probe'));
    assert.equal(j.terminal, terminal);
    const next = t.begin(); assert.ok(next); assert.notEqual(next.id, j.id);
    assert.equal(t.settle(j, 'script', {owner: KWIN, id: 7}), false);
    assert.equal(next.resources.size, 2); f.quiet();
});
test('synthetic: unknown load outcome, cancellation, owner-specific late reconciliation', () => {
    const f = fixture(), t = f.trace, j = t.begin(); t.cancel();
    const terminal = j.terminal; assert.equal(t.begin(), null);
    assert.equal(t.loaded(j, 9), false); assert.equal(j.resources.get('script').id, 9);
    assert.equal(t.settle(j, 'script', {owner: ':1.99', id: 9}), false);
    assert.equal(t.settle(j, 'script', {owner: KWIN, id: 10}), false);
    t.settle(j, 'script', {owner: KWIN, id: 9}); t.settle(j, 'probe', workerAck(j, 'probe', {exit: 1}));
    const next = t.begin(); assert.ok(next);
    t.send('CompleteSdlX11Identity', {job_id: j.id, challenge: j.challenge, source: j.source}); t.pump();
    assert.equal(next.taken, undefined); assert.equal(next.resources.size, 2);
    assert.equal(j.terminal, terminal); f.quiet();
});
for (const fault of ['removed', 'marker', 'pid', 'app', 'instance', 'competitor', 'child_exit', 'post_property', 'worker_exit']) {
    test('synthetic: fresh checks reject ' + fault + ' after mapping snapshot', () => {
        const f = prepared(), t = f.trace, j = mapping(f);
        if (fault === 'removed') f.remove(f.viewer);
        if (fault === 'marker') f.change(f.viewer, {caption: 'lost'});
        if (fault === 'pid') f.change(f.viewer, {pid: 43});
        if (fault === 'app') f.change(f.viewer, {resourceClass: 'other'});
        if (fault === 'instance') f.change(f.viewer, {resourceName: 'other'});
        if (fault === 'competitor') {const temp = f.makeWindow(OTHER); f.add(temp, 102); f.remove(temp, 102);}
        if (fault === 'child_exit') {t.childLive = false; t.fail('child_exit');}
        if (fault === 'post_property') t.properties.name.value = Buffer.from('wrong');
        t.pump(); t.settle(j, 'post', workerAck(j, 'post', {exit: fault === 'worker_exit' ? 1 : 0}));
        t.settle(j, 'script', {owner: KWIN, id: 8});
        assert.notEqual(j.terminal?.state, 'registered');
        t.tick(BOUNDS.mapping); assert.equal(j.terminal.state, 'failed'); f.quiet();
    });
}

test('native contract vectors: exact types, instance/class order, terminators and raw title', () => {
    const {marker} = publication(1);
    assert.equal(validProperties(properties()), true);
    const faults = [
        p => {delete p.proof;}, p => {p.proof.type = 'STRING';},
        p => {p.proof.value = Buffer.from('{}');}, p => {p.proof.bytes_after = 1;},
        p => {p.proof.value = Buffer.alloc(BOUNDS.bytes + 1, 65);},
        p => {p.pid.format = 8;}, p => {p.pid.type = 'INTEGER';},
        p => {p.pid.value = Buffer.from([43, 0, 0, 0]);}, p => {p.pid.value = Buffer.alloc(8);},
        ...[APP + '\0' + INSTANCE + '\0', INSTANCE + '\0' + APP, INSTANCE + '\0' + APP + '\0\0',
            '\0' + APP + '\0', INSTANCE + '\0\0', INSTANCE.toUpperCase() + '\0' + APP + '\0']
            .map(value => p => {p.wmclass.value = Buffer.from(value);}),
        p => {p.wmclass.type = 'UTF8_STRING';},
        ...['', marker + '\0', marker + ' suffix', ' ' + marker, marker + '\n']
            .map(value => p => {p.name.value = Buffer.from(value);}),
        p => {p.name.value = Buffer.from([0xc0, 0xaf]);}, p => {p.name.format = 32;},
        p => {p.name.type = 'STRING';}, p => {delete p.name; p.WM_NAME = Buffer.from(marker);}
    ];
    for (const [index, fault] of faults.entries()) {
        const p = properties(); fault(p); assert.equal(validProperties(p), false, 'vector ' + index);
    }
});


test('synthetic: readiness and mapping have distinct jobs/challenges; old ready callback is inert', () => {
    const f = prepared(), t = f.trace, j = t.current;
    const oldTake = t.messages.find(m => m.method === 'TakeSdlX11Identity');
    const oldId = j.id, oldChallenge = j.challenge, deadline = j.deadline;
    t.tick(50); mapping(f);
    assert.notEqual(j.id, oldId); assert.notEqual(j.challenge, oldChallenge);
    assert.equal(j.deadline, deadline); assert.equal(j.phaseEnd, t.now + BOUNDS.mapping);
    const count = t.messages.length;
    // A duplicate transport callback is ignored by the fixture scheduler.
    assert.equal(oldTake.callbackDone, true);
    assert.equal(t.callback(oldTake), false); assert.equal(t.messages.length, count);
    assert.equal(commit(f).state, 'registered'); f.quiet();
});
test('synthetic: foreign callers cannot consume a challenge or cancel the owning job', () => {
    const f = prepared(), t = f.trace, j = mapping(f, {holdReply: true});
    const original = t.messages.at(-1);
    const forged = t.send('CompleteSdlX11Identity', original.body, {sender: ':1.99'});
    // Deliver the legitimate snapshot first to preserve same-connection order;
    // its callback remains separately controlled.
    t.deliver(original); t.finish(original);
    t.deliver(forged); t.finish(forged);
    assert.equal(forged.reply.error, 'AccessDenied'); assert.equal(j.terminal, null);
    assert.equal(commit(f).state, 'registered'); f.quiet();
});
test('synthetic: lost mapping callback expires; late proof only reports cached failure', () => {
    const f = prepared(), t = f.trace, j = mapping(f, {holdReply: true});
    const held = t.messages.at(-1), deadline = j.phaseEnd;
    t.tick(BOUNDS.mapping); const terminal = j.terminal;
    t.pump(); assert.equal(j.terminal, terminal); assert.equal(j.phaseEnd, deadline);
    assert.equal(held.reply, undefined); assert.equal(t.begin(), null);
    t.settle(j, 'script', {owner: KWIN, id: 8});
    assert.equal(j.resources.size, 0); assert.ok(t.begin()); f.quiet();
});
test('synthetic: an added event cannot reclassify a prelaunch baseline UUID as new', () => {
    const original = fixture(), old = original.makeWindow();
    const f = fixture([old.win]), t = f.trace, j = t.begin();
    t.loaded(j, 7); t.pump();
    t.settle(j, 'probe', workerAck(j, 'probe')); t.settle(j, 'script', {owner: KWIN, id: 7});
    mapping(f); assert.equal(j.terminal.reason, 'bad_fence'); f.quiet(); original.quiet();
});

for (const fault of ['expected_uuid_at_other_xid', 'reused_xid_before_snapshot', 'reused_xid_after_snapshot']) {
    test('synthetic exact-XID lookup rejects ' + fault, () => {
        const f = prepared(), t = f.trace;
        const j = mapping(f, {add: fault === 'reused_xid_after_snapshot'});
        if (fault === 'expected_uuid_at_other_xid') {
            f.add(f.makeWindow(j.uuid), j.xid + 1);
            t.pump();
            assert.equal(j.mappingSent, undefined, 'UUID at another XID is not a lookup result');
        } else {
            // Reuse the numeric XID with a distinct, unrelated native window.
            if (f.viewer) f.remove(f.viewer, j.xid);
            const unrelated = f.makeWindow(OTHER, 'unrelated viewer');
            unrelated.state.pid = 99;
            f.add(unrelated, j.xid); t.pump();
            if (fault === 'reused_xid_before_snapshot') {
                const reply = t.messages.find(m => m.method === 'CompleteSdlX11Identity' && m.body.purpose === 'map');
                assert.equal(reply.body.window_uuid, OTHER, 'snapshot must describe the actual XID lookup');
            }
        }
        commit(f); t.tick(BOUNDS.mapping);
        assert.equal(j.terminal.state, 'failed');
        assert.ok(f.lookups.length > 0);
        assert.ok(f.lookups.every(xid => xid === j.xid), 'no UUID or latest-window lookup substitute');
        f.quiet();
    });
}

for (const phase of ['pre', 'post']) {
    for (const reuseXid of [false, true]) {
        test('synthetic rejects previous publication at ' + phase + 'check; numeric XID reuse=' + reuseXid, () => {
            for (const replay of ['nonce_only', 'whole_property']) {
                const f = prepared(), t = f.trace, first = mapping(f);
                const oldProperty = properties(first), firstResult = commit(f);
                assert.equal(firstResult.state, 'registered');
                f.remove(f.viewer, first.xid); t.pump();
                prepared(f, {uuid: OTHER, pid: 43, xid: reuseXid ? first.xid : first.xid + 1});
                const next = t.current;
                assert.notEqual(next.request, first.request);
                assert.notEqual(next.marker, first.marker); assert.notEqual(next.nonce, first.nonce);
                assert.equal(next.xid === first.xid, reuseXid);
                // nonce_only retains every current field, isolating the nonce check.
                // whole_property simulates a stale native proof on the target XID.
                const stale = replay === 'whole_property' ? oldProperty.proof : properties(next).proof;
                if (replay === 'nonce_only') {
                    const value = JSON.parse(stale.value.toString('utf8'));
                    value.publication_nonce = first.nonce;
                    stale.value = Buffer.from(JSON.stringify(value));
                }
                if (phase === 'pre') {
                    t.readyEvidence(); t.properties.proof = stale;
                    t.settle(next, 'pre', workerAck(next, 'pre'));
                } else {
                    mapping(f); t.properties.proof = stale; commit(f);
                }
                assert.equal(next.terminal.state, 'failed', replay);
                assert.equal(next.terminal.reason, 'native_evidence', replay);
                assert.equal(first.terminal, firstResult, 'prior terminal result must remain stable');
                f.quiet();
            }
        });
    }
}

test('synthetic: successive launches accept their own distinct markers, nonces and exact XIDs', () => {
    const f = prepared(), t = f.trace, first = mapping(f), firstResult = commit(f);
    f.remove(f.viewer, first.xid); t.pump();
    prepared(f, {uuid: OTHER, pid: 43, xid: 102});
    const second = mapping(f), secondResult = commit(f);
    assert.equal(firstResult.state, 'registered'); assert.equal(secondResult.state, 'registered');
    for (const key of ['request', 'marker', 'nonce', 'uuid', 'xid']) assert.notEqual(first[key], second[key], key);
    assert.equal(secondResult.uuid, OTHER); assert.equal(first.terminal, firstResult);
    assert.equal(first.resources.size, 0); assert.equal(second.resources.size, 0); f.quiet();
});

test('synthetic worker identity: a probe acknowledgement cannot discharge the precheck worker', () => {
    const f = fixture(), t = f.trace, j = t.begin();
    const probeToken = j.resources.get('probe').token;
    t.loaded(j, 7); t.pump();
    t.settle(j, 'probe', workerAck(j, 'probe')); t.settle(j, 'script', {owner: KWIN, id: 7});
    t.readyEvidence();
    const pre = j.resources.get('pre'); assert.notEqual(pre.token, probeToken);
    assert.equal(t.settle(j, 'pre', {owner: BROKER, token: probeToken}), false);
    assert.equal(j.resources.get('pre'), pre); assert.equal(t.begin(), null);
    assert.equal(j.terminal, null); t.cancel();
    const terminal = j.terminal;
    t.settle(j, 'pre', {owner: BROKER, token: pre.token});
    assert.equal(j.terminal, terminal); assert.equal(j.resources.size, 0); f.quiet();
});

test('synthetic worker identity: stale/missing tokens keep postcheck owned and registration blocked', () => {
    const f = prepared(), t = f.trace, j = t.current;
    t.readyEvidence(); const preToken = j.resources.get('pre').token;
    t.settle(j, 'pre', workerAck(j, 'pre'));
    f.add(f.makeWindow()); t.loaded(j, 8); t.pump();
    const post = j.resources.get('post'); assert.notEqual(post.token, preToken);
    t.settle(j, 'script', {owner: KWIN, id: 8});
    for (const token of [undefined, 'forged-worker', preToken]) {
        assert.equal(t.settle(j, 'post', {owner: BROKER, token}), false);
        assert.equal(j.resources.get('post'), post);
        assert.equal(j.terminal, null); assert.equal(t.begin(), null);
    }
    t.settle(j, 'post', {owner: BROKER, token: post.token});
    const result = j.terminal; assert.equal(result.state, 'registered');
    assert.equal(t.settle(j, 'post', {owner: BROKER, token: post.token}), false);
    assert.equal(j.terminal, result); f.quiet();
});

test('synthetic worker identity: late reaping for an old request cannot clean up a newer same-owner worker', () => {
    const f = fixture(), t = f.trace, old = t.begin();
    const oldToken = old.resources.get('probe').token;
    t.loaded(old, 7); t.pump(); t.cancel(); const oldResult = old.terminal;
    t.settle(old, 'script', {owner: KWIN, id: 7});
    t.settle(old, 'probe', {owner: BROKER, token: oldToken});
    const next = t.begin(), currentWorker = next.resources.get('probe');
    assert.equal(currentWorker.owner, BROKER); assert.notEqual(currentWorker.token, oldToken);
    assert.equal(t.settle(next, 'probe', {owner: BROKER, token: oldToken}), false);
    assert.equal(t.settle(old, 'probe', {owner: BROKER, token: oldToken}), false);
    assert.equal(next.resources.get('probe'), currentWorker); assert.equal(next.resources.size, 2);
    assert.equal(next.terminal, null); assert.equal(old.terminal, oldResult); f.quiet();
});
