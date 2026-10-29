// Copyright 2025-2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Real optional resident functions in a headless KWin object harness.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'joetoo-kwin-resident.js'), 'utf8');
const implementation = source.slice(source.indexOf('function moveOptionalFromBroker()'), source.indexOf('// New-window path:'));
function harness() {
    const geometry = {x: 10, y: 20, width: 500, height: 400};
    const win = {internalId: 'uuid-a', deleted: false, frameGeometry: geometry,
                 desktops: [{x11DesktopNumber: 1}], onAllDesktops: false, tile: null, fullScreen: false, maximizeMode: 0};
    const other = {...win, internalId: 'uuid-b'};
    const workspace = {activeWindow: win, desktops: [{x11DesktopNumber: 1}, {x11DesktopNumber: 2}]};
    let callback, call, now = 1000;
    const results = [];
    const context = {workspace, observerSource: 'resident', Date: {now: () => now}, console,
                     registerShortcut: () => {}, windowUUID: w => w ? w.internalId : '',
                     geometryText: w => JSON.stringify(w.frameGeometry),
                     finish: (req, state, detail) => results.push({state, detail}),
                     callDBus: (...args) => {call = args; callback = args.at(-1);},
                     BRIDGE: 'bridge', PATH: '/bridge'};
    vm.runInNewContext(implementation, context);
    return {win, other, workspace, results, context,
            start: () => context.moveOptionalFromBroker(), call: () => call,
            advance: ms => {now += ms;}, reply: req => callback(JSON.stringify(req))};
}
const request = (extra = {}) => ({id: 'request', desktop: 2, x: 0, y: 0, width: 0, height: 0,
    preserve_desktop: false, preserve_position: true, preserve_size: true, remaining_ms: 14000, ...extra});
const plain = value => JSON.parse(JSON.stringify(value));

test('desktop-only preserves frame at application time and captured focus target', () => {
    const h = harness(); h.start();
    assert.equal(h.call()[3], 'TakeMove'); assert.equal(h.call()[5], 'uuid-a');
    h.workspace.activeWindow = h.other;
    h.win.frameGeometry = {x: -30, y: -40, width: 750, height: 850};
    const frame = h.win.frameGeometry;
    h.reply(request());
    assert.equal(h.win.frameGeometry, frame);
    assert.equal(h.win.desktops[0].x11DesktopNumber, 2);
    assert.equal(h.other.desktops[0].x11DesktopNumber, 1);
    const details = JSON.parse(h.results[0].detail);
    assert.equal(h.results[0].state, 'VERIFY');
    assert.equal(details.window_uuid, 'uuid-a');
    assert.deepEqual(details.resolved.geometry, frame);
});

test('all independent preservation flags preserve exactly the omitted fields', () => {
    for (const pd of [false, true]) for (const pp of [false, true]) for (const ps of [false, true]) {
        const h = harness();
        h.win.desktops = [{x11DesktopNumber: 1}, {x11DesktopNumber: 2}];
        h.win.onAllDesktops = true;
        const memberships = h.win.desktops;
        h.start();
        h.reply(request({preserve_desktop: pd, preserve_position: pp, preserve_size: ps,
                         desktop: pd ? 0 : 2, x: pp ? 0 : -100, y: pp ? 0 : -200,
                         width: ps ? 0 : 800, height: ps ? 0 : 900}));
        assert.equal(h.results[0].state, 'VERIFY');
        const resolved = JSON.parse(h.results[0].detail).resolved;
        assert.deepEqual(resolved.geometry, {x: pp ? 10 : -100, y: pp ? 20 : -200,
                                             width: ps ? 500 : 800, height: ps ? 400 : 900});
        if (pd) { assert.equal(h.win.desktops, memberships); assert.equal(resolved.on_all_desktops, true); }
        else { assert.deepEqual(resolved.desktops, [2]); assert.equal(resolved.on_all_desktops, false); }
    }
});

test('last available desktop accepted; absent desktops rejected without mutation', () => {
    for (const desktop of [0, -1, 3]) {
        const h = harness(); h.start(); h.reply(request({desktop}));
        assert.equal(h.results[0].state, 'ERROR');
        assert.equal(h.win.desktops[0].x11DesktopNumber, 1);
    }
    const h = harness(); h.start(); h.reply(request({desktop: 2}));
    assert.equal(h.results[0].state, 'VERIFY');
});

test('expired callbacks and deleted captured windows do not move another window', () => {
    for (const failure of ['expired', 'deleted']) {
        const h = harness(); h.start(); h.workspace.activeWindow = h.other;
        if (failure === 'expired') h.advance(15000); else h.win.deleted = true;
        h.reply(request());
        assert.equal(h.results[0].state, 'ERROR');
        assert.equal(h.other.desktops[0].x11DesktopNumber, 1);
    }
});

test('tiled/fullscreen/maximized geometry changes rejected without changing modes', () => {
    for (const field of ['tile', 'fullScreen', 'maximizeMode']) {
        const h = harness(); h.win[field] = field === 'tile' ? {} : field === 'maximizeMode' ? 3 : true;
        const original = plain(h.win.frameGeometry);
        h.start(); h.reply(request({preserve_size: false, width: 800, height: 900}));
        assert.equal(h.results[0].state, 'ERROR');
        assert.deepEqual(plain(h.win.frameGeometry), original);
        assert.ok(h.win[field]);
    }
});

test('unclaimed request causes no mutation or completion', () => {
    const h = harness(); h.start();
    h.call().at(-1)('');
    assert.equal(h.results.length, 0);
    assert.equal(h.win.desktops[0].x11DesktopNumber, 1);
});
