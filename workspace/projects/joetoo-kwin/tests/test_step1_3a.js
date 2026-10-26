// Headless KWin scripting mock; run `node --test tests/test_step1_3a.js`.
// Only the KWin and D-Bus interfaces needed by Step 1.3a are simulated.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

// Each fake Qt signal stores callbacks registered with `.connect`.
function signal() {
    const callbacks = new Set();
    return {
        connect: callback => callbacks.add(callback),
        disconnect: callback => callbacks.delete(callback),
        emit: (...args) => { for (const callback of callbacks) callback(...args); },
        count: () => callbacks.size
    };
}

function windowObject(id, title) {
    return {
        internalId: id, normalWindow: true, deleted: false,
        resourceClass: 'konsole', resourceName: 'konsole',
        desktopFileName: 'org.kde.konsole', caption: title, pid: 441,
        onAllDesktops: false, desktops: [{x11DesktopNumber: 2}],
        frameGeometry: {x: 10, y: 20, width: 500, height: 400},
        frameGeometryChanged: signal(), desktopsChanged: signal(),
        captionChanged: signal(), desktopFileNameChanged: signal(),
        windowClassChanged: signal()
    };
}

function residentWith(existing) {
    const calls = [], shortcuts = new Map();
    const workspace = {stackingOrder: existing, activeWindow: null,
                       desktops: [{x11DesktopNumber: 1}, {x11DesktopNumber: 2}],
                       windowAdded: signal(), windowRemoved: signal()};
    const context = {
        workspace, console,
        callDBus: (...args) => calls.push(args),
        registerShortcut: (name, _description, _key, cb) => shortcuts.set(name, cb)
    };
    const source = fs.readFileSync(path.join(__dirname, '..', 'joetoo-kwin-resident.js'), 'utf8');
    vm.runInNewContext(source, context);
    const events = () => calls.filter(args => args[3] === 'ObserveWindow')
        .map(args => JSON.parse(args[4]));
    return {workspace, shortcuts, calls, events};
}

const A = 'd848c4c9-64ed-48bf-b083-40230314d5ab';
const B = 'd848c4c9-64ed-48bf-b083-40230314d5ac';

test('initial inventory is observational only, including application hints', () => {
    const existing = windowObject(A, 'Konsole A');
    const context = residentWith([existing]);
    assert.equal(context.events().length, 1);
    assert.equal(context.events()[0].event, 'existing');
    assert.equal(context.events()[0].window.uuid, A);
    assert.equal(context.events()[0].window.resource_class, 'konsole');
    assert.equal(context.events()[0].window.geometry.width, 500);
    assert.equal(context.events()[0].window.managed_id, undefined);
});

test('distinct windows, updates and removal retain correct UUID', () => {
    const a = windowObject(A, 'A');
    const b = windowObject(B, 'B');
    const c = residentWith([a]);
    c.workspace.windowAdded.emit(b);
    b.frameGeometry.x = 150;
    b.frameGeometryChanged.emit();
    assert.equal(c.events().at(-1).event, 'changed');
    assert.equal(c.events().at(-1).window.geometry.x, 150);
    b.deleted = true;
    b.frameGeometry = null; // simulate invalidated metadata after removal
    b.internalId = null;     // even its UUID may be inaccessible by this point
    c.workspace.windowRemoved.emit(b);
    assert.equal(c.events().at(-1).event, 'removed');
    assert.equal(c.events().at(-1).window.uuid, B);
    assert.equal(c.events().at(-1).window.geometry.x, 150);
    assert.equal(b.frameGeometryChanged.count(), 0);
    assert.equal(a.frameGeometryChanged.count(), 1);
});

test('explicit refresh republishes existing windows without duplicate subscriptions', () => {
    const w = windowObject(A, 'A');
    const c = residentWith([w]);
    c.shortcuts.get('joetoo_bridge_observe')();
    assert.equal(c.events().length, 2);
    assert.equal(w.frameGeometryChanged.count(), 1);
    assert.ok(c.shortcuts.has('joetoo_bridge_move'));
});
