// Real resident SDL action/optional placement in a VM. No KWin, bus, GUI or input.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../joetoo-kwin-resident.js'), 'utf8');
const uuid = 'd848c4c9-64ed-48bf-b083-40230314d5ab';
function harness() {
    let mutationCount = 0, callback, now = 1000;
    const win = {internalId: '{' + uuid.toUpperCase() + '}', normalWindow: true, deleted: false,
        pid: 42, resourceClass: 'com.freerdp.client.sdl3', caption: 'marker',
        frameGeometry: {x: 0, y: 0, width: 300, height: 200}, desktops: [{x11DesktopNumber: 1}],
        onAllDesktops: false, tile: null, fullScreen: false, maximizeMode: 0};
    const other = new Proxy({...win, internalId: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'},
        {set() {mutationCount++; throw Error('Unrelated window mutation');}});
    const workspace = new Proxy({stackingOrder: [other, win], desktops: [1, 2, 3].map(n => ({x11DesktopNumber: n})),
        get activeWindow() {throw Error('Active window selection forbidden');},
        raiseWindow() {throw Error('Raise forbidden');}, lowerWindow() {throw Error('Lower forbidden');}},
        {set() {throw Error('Workspace/focus mutation forbidden');}});
    const outcomes = [], shortcuts = new Map();
    const ctx = vm.createContext({workspace, observerSource: 'source', BRIDGE: 'bridge', PATH: '/bridge',
        Date: {now: () => now}, console,
        windowUUID: w => w?.internalId || '', geometryText: () => 'before',
        finish: (r, state, detail) => outcomes.push({state, detail: state === 'VERIFY' ? JSON.parse(detail) : detail}),
        registerShortcut: (name, _label, _key, fn) => shortcuts.set(name, fn),
        callDBus: (_bus, _path, _iface, method, _source, cb) => {
            assert.equal(method, 'TakeSdlPlacement'); callback = cb;
        }}, {codeGeneration: {strings: false, wasm: false}});
    const optional = source.slice(source.indexOf('function placeOptionalWindow('), source.indexOf('registerShortcut("joetoo_bridge_move_optional"'));
    const sdl = source.slice(source.indexOf('function sdlPlacementFromBroker('), source.indexOf('// New-window path:'));
    vm.runInContext(optional + '\n' + sdl, ctx, {timeout: 1000});
    return {win, workspace, outcomes, shortcuts, start: () => ctx.sdlPlacementFromBroker(),
        reply: r => callback(JSON.stringify(r)), advance: ms => {now += ms;}, mutations: () => mutationCount};
}
const request = extra => ({id: 'placement', source: 'source', window_uuid: uuid,
    pid: 42, resource_class: 'com.freerdp.client.sdl3', title_marker: 'marker', remaining_ms: 1000,
    desktop: 3, x: 25, y: 35, width: 800, height: 600,
    preserve_desktop: false, preserve_position: false, preserve_size: false, ...extra});

if (process.argv.includes('--fixture')) {
    const r = JSON.parse(fs.readFileSync(0, 'utf8'));
    const h = harness();
    h.win.internalId = r.window_uuid; h.win.pid = r.pid; h.win.caption = r.title_marker;
    h.start(); h.reply(r);
    assert.equal(h.outcomes.length, 1);
    console.log(JSON.stringify({...h.outcomes[0], uuid: h.win.internalId,
        geometry: h.win.frameGeometry, desktops: h.win.desktops.map(d => d.x11DesktopNumber),
        unrelated_mutations: h.mutations()}));
} else {
    const {test} = require('node:test');
    test('explicit action places only broker UUID without active-window/focus/stack access', () => {
        const h = harness();
        assert.equal(h.outcomes.length, 0);
        h.start(); h.reply(request());
        assert.equal(h.outcomes[0].state, 'VERIFY');
        assert.equal(h.outcomes[0].detail.window_uuid.toLowerCase().replace(/[{}]/g, ''), uuid);
        assert.equal(h.win.frameGeometry.x, 25); assert.equal(h.win.desktops[0].x11DesktopNumber, 3);
        assert.equal(h.mutations(), 0);
    });
    for (const fault of ['uuid', 'pid', 'marker', 'class', 'removed', 'non_normal', 'source', 'expiry', 'fullscreen', 'maximized', 'tile', 'desktop']) {
        test('resident refuses ' + fault + ' before any assignment', () => {
            const h = harness(), r = request(), frame = h.win.frameGeometry, desktops = h.win.desktops;
            h.start();
            if (fault === 'uuid') r.window_uuid = 'aaaaaaaa-0000-4000-8000-000000000000';
            if (fault === 'pid') h.win.pid++;
            if (fault === 'marker') h.win.caption = 'lost';
            if (fault === 'class') h.win.resourceClass = 'other';
            if (fault === 'removed') h.win.deleted = true;
            if (fault === 'non_normal') h.win.normalWindow = false;
            if (fault === 'source') r.source = 'changed';
            if (fault === 'expiry') h.advance(1000);
            if (fault === 'fullscreen') h.win.fullScreen = true;
            if (fault === 'maximized') h.win.maximizeMode = 3;
            if (fault === 'tile') h.win.tile = {};
            if (fault === 'desktop') r.desktop = 4;
            h.reply(r);
            assert.equal(h.outcomes[0].state, 'ERROR');
            assert.equal(h.win.frameGeometry, frame); assert.equal(h.win.desktops, desktops);
            assert.equal(h.mutations(), 0);
        });
    }
}
