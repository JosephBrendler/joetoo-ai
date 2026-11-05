// Offline KWin VM tests. No compositor, GUI, native bus or input access.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require('node:path').join(__dirname, '../tools/joetoo-rdp-x11-use.js'), 'utf8');
const UUID = '11111111-1111-4111-8111-111111111111';
function fixture(window, candidates = [{xid: 123, pid: 456, generation: 1}]) {
    const calls = [], timers = [], shortcuts = {};
    function QTimer() {
        this.timeout = {connect: f => {this.callback = f;}, disconnect: f => {assert.equal(f, this.callback); this.callback = null;}};
        this.start = () => {this.running = true;}; this.stop = () => {this.running = false;};
        timers.push(this);
    }
    const settings = {receiver: ':1.99', run: 'a'.repeat(32), pollMs: 10, ackMs: 3000,
        maxCandidates: 64, expectedClass: 'com.freerdp.client.sdl3'};
    const context = {JOETOO_RDP_X11_USE: settings, QTimer,
        workspace: new Proxy({getClient: xid => {assert.equal(xid, 123); return window;}},
            {set() {throw Error('Window control forbidden');}}),
        registerShortcut: (name, text, key, fn) => {assert.equal(key, ''); shortcuts[name] = fn;},
        callDBus: (name, path, iface, method, body, callback) => {calls.push({method, body: JSON.parse(body), callback});}}
    vm.runInNewContext(source, context);
    const reply = (index, body, extra = {}) => calls[index].callback(JSON.stringify({run: settings.run, ok: true, body, ...extra}));
    return {calls, timers, shortcuts, reply, candidates};
}
function window(extra = {}) {
    return new Proxy({internalId: '{' + UUID.toUpperCase() + '}', pid: 456,
        resourceClass: 'com.freerdp.client.sdl3', deleted: false, ...extra},
    {set() {throw Error('Window control forbidden');}});
}
test('exact getClient XID maps live PID/class to canonical UUID only', () => {
    const f = fixture(window()); f.reply(0, f.candidates);
    assert.deepEqual(f.calls[1].body.body, [{generation: 1, xid: 123, pid: 456, uuid: UUID}]);
    f.reply(1, null); assert.equal(f.timers[0].running, true);
});
test('missing, deleted, wrong PID and wrong class are never linked', () => {
    for (const w of [null, window({deleted: true}), window({pid: 999}), window({resourceClass: 'other'})]) {
        const f = fixture(w); f.reply(0, f.candidates); assert.deepEqual(f.calls[1].body.body, []);
    }
});
test('one outstanding call; a missing D-Bus callback cleans up', () => {
    const f = fixture(window()); f.timers[0].callback(); assert.equal(f.calls.length, 1);
    f.timers[1].callback(); assert.ok(f.timers.every(t => !t.running && t.callback === null));
    f.reply(0, f.candidates); assert.equal(f.calls.length, 1);
});
test('wrong receiver run and malformed reply stop without linkage', () => {
    for (const text of ['bad', JSON.stringify({ok: true, run: 'wrong', body: []})]) {
        const f = fixture(window()); f.calls[0].callback(text);
        assert.equal(f.calls.length, 1); assert.ok(f.timers.every(t => t.callback === null));
    }
});
test('explicit finish is idempotent and late replies cannot restart observation', () => {
    const f = fixture(window()); const finish = f.shortcuts.joetoo_rdp_x11_use_finish;
    finish(); finish(); f.reply(0, f.candidates);
    assert.equal(f.calls.length, 1); assert.ok(f.timers.every(t => !t.running));
});
test('candidate overflow and inaccessible KWin object fail safely', () => {
    const f = fixture(window()); f.reply(0, Array(65).fill({}));
    assert.ok(f.timers.every(t => !t.running));
    const bad = fixture({get pid() {throw Error('gone');}});
    bad.reply(0, bad.candidates); assert.ok(bad.timers.every(t => !t.running));
});
