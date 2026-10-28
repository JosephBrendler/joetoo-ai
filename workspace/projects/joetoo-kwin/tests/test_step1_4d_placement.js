// Copyright 2025-2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Verify resident reports an applied request for asynchronous confirmation.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'joetoo-kwin-resident.js'), 'utf8');
const begin = source.indexOf('function placeWindow(win, request, operation) {');
const end = source.indexOf('// The original working active-window path remains available.', begin);
assert.ok(begin >= 0 && end > begin);
const placement = source.slice(begin, end);

function simulate({exists = true, delayed = true, desktopCount = 2} = {}) {
    let geometry = {x: 535, y: 76, width: 700, height: 700};
    let nextGeometry;
    let currentDesktop = [{x11DesktopNumber: 1}];
    let nextDesktop;
    const win = {
        deleted: !exists, tile: null, fullScreen: false, internalId: 'd848c4c9-64ed-48bf-b083-40230314d5ab',
        get frameGeometry() { return geometry; },
        set frameGeometry(value) { nextGeometry = value; if (!delayed) geometry = value; },
        get desktops() { return currentDesktop; },
        set desktops(value) { nextDesktop = value; if (!delayed) currentDesktop = value; },
    };
    const results = [];
    const workspace = {desktops: Array.from({length: desktopCount}, (_, i) => ({x11DesktopNumber: i+1}))};
    const ctx = {workspace, windowUUID: w => w.internalId,
                 geometryText: w => `${w.frameGeometry.x},${w.frameGeometry.y}`,
                 finish: (req, state, detail) => results.push({state, detail})};
    vm.runInNewContext(placement + '\nplaceWindow(win, request, "move");',
                       {...ctx, win, request: {desktop: 2, x: 19, y: 54, width: 816, height: 918}});
    return {results, commit: () => {geometry = nextGeometry; currentDesktop = nextDesktop;}};
}

test('stale immediate Wayland frame is verification pending, not failure', () => {
    const {results} = simulate({delayed: true});
    assert.equal(results.length, 1);
    assert.equal(results[0].state, 'VERIFY');
    const info = JSON.parse(results[0].detail);
    assert.equal(info.window_uuid, 'd848c4c9-64ed-48bf-b083-40230314d5ab');
    assert.match(info.before, /535,76/);
});

test('already-converged frame also requires exact UUID broker verification', () => {
    assert.equal(simulate({delayed: false}).results[0].state, 'VERIFY');
});

test('missing desktop is an immediate real error', () => {
    assert.equal(simulate({desktopCount: 1}).results[0].state, 'ERROR');
});

test('deleted window is an immediate real error', () => {
    assert.equal(simulate({exists: false}).results[0].state, 'ERROR');
});
