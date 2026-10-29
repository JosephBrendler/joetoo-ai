#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Propose a source-verified, non-mutating Step 1.4d placement patch.

Run from the joetoo-ai clone: python3 make_step14d_async_patch.py > candidate.patch
This generator NEVER changes a checkout or performs Git operations other than
read-only git hash-object. Commit/push are maintainer-only review decisions.
"""

import difflib
import pathlib
import subprocess
import sys

PREFIX = 'workspace/projects/joetoo-kwin/'
SHA = {
    'joetoo-kwin-resident.js': '676e14d15572ab963cfb17a94f4adb25ea548866',
    'libexec/joetoo-kwind': 'd1df99c1e401bc3eeb53ecb050628fd6eedb33bb',
    'libexec/joetoo_kwin_registry.py': '406ecd2822b8f18e62d5660112feaf34450e2054',
}


def replace_once(src, old, new, where):
    if src.count(old) != 1:
        raise ValueError(f'{where}: expected 1 occurrence; got {src.count(old)}: {old[:100]!r}')
    return src.replace(old, new, 1)


def replace_section(src, begin, end, new, where):
    i = src.index(begin)
    j = src.index(end, i)
    return src[:i] + new + src[j:]


def transform_js(s):
    original = '''function placeWindow(win, request, operation) {'''
    # The original function ends just before the legacy move path comment.
    new = '''function placeWindow(win, request, operation) {
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

'''
    return replace_section(s, original,
        '// The original working active-window path remains available.',
        new, 'js placement callback')


def transform_registry(s):
    old = '''        if record.presence != "present" or state not in allowed[record.placement]:
            raise RegistryError("invalid placement transition")
        record.placement = state
'''
    new = '''        # A disappeared window may finish an already pending placement as
        # failed. Never declare placement succeeded unless presence is present.
        if (state not in allowed[record.placement]
                or (state != "failed" and record.presence != "present")):
            raise RegistryError("invalid placement transition")
        record.placement = state
'''
    return replace_once(s, old, new, 'registry placement transitions')


def transform_broker(s):
    s = replace_once(s, '''        self._managed_correlation = None

    def _submit(''', '''        self._managed_correlation = None

    def _submit(''', 'broker constructor')
    s = replace_once(s, '''        # Single-flight only, matching the already tested proof of concept.
        if (self.request is not None
                and self.request["state"] in ("PENDING", "RUNNING")
''', '''        # In-flight verification is still a placement request: never allow a
        # second request to overwrite the UUID before it settles or times out.
        self._advance_placement()
        if (self.request is not None
                and self.request["state"] in ("PENDING", "RUNNING", "VERIFYING")
''', 'broker serialized placement')
    s = replace_once(s, '''        return json.dumps({"placement_request_id": placement_id,
                           "registration_request_id": registration_id}, sort_keys=True)
''', '''        self.request["registration_request_id"] = registration_id
        return json.dumps({"placement_request_id": placement_id,
                           "registration_request_id": registration_id}, sort_keys=True)
''', 'managed link')
    old = '''    @dbus.service.method(IFACE, in_signature="sss", out_signature="")
    def Complete(self, request_id, result, detail):'''
    start = s.index(old)
    end = s.index('    # Step 1.4d: a launch-intent interface', start)
    new = '''    def _sync_managed_placement(self):
        """Cross-check target UUID and record placement without granting ownership.

        Registration and placement can complete in either order. A successful
        placement on a different UUID must NEVER be attributed to the managed
        window, even when both have the same application class or PID.
        """
        r = self.request
        if r is None or not r.get("registration_request_id"):
            return
        launch = self.registry.requests.get(r["registration_request_id"])
        if launch is None or launch.state != "succeeded":
            return
        managed = self.registry.get_window(launch.result)
        if managed is None:
            return
        if managed.placement == "not_requested":
            if managed.presence != "present":
                return
            self.registry.set_placement(managed.window_uuid, "pending")
            managed = self.registry.get_window(managed.window_uuid)
        target = r.get("placement_uuid")
        if target is not None and target != managed.window_uuid:
            r["state"] = "ERROR"
            r["detail"] = "placement UUID differs from positively registered UUID"
        if managed.placement != "pending":
            return
        if (r["state"] == "OK" and target == managed.window_uuid
                and managed.presence == "present"):
            self.registry.set_placement(managed.window_uuid, "succeeded")
        elif r["state"] == "ERROR":
            self.registry.set_placement(managed.window_uuid, "failed")

    def _advance_placement(self, removed_uuid=None):
        """Resolve VERIFYING from exact-UUID KWin observations or deadline.

        KWin's resident already emits changed/removed events on geometry and
        desktop changes. No arbitrary sleeps or JS timer API are needed.
        """
        r = self.request
        if r is None or r["state"] != "VERIFYING":
            return
        identifier = r["placement_uuid"]
        if r["observation_source"] != self.observation_source:
            r["state"] = "ERROR"
            r["detail"] = "resident observation source changed during placement"
        elif removed_uuid == identifier:
            r["state"] = "ERROR"
            r["detail"] = "target window disappeared during placement"
        else:
            observed = self.observed_windows.get(identifier)
            if observed is not None:
                geo = observed["geometry"]
                desired = all(geo[key] == r[key]
                              for key in ("x", "y", "width", "height"))
                desktop_ok = (observed["desktops"] == [r["desktop"]]
                              and not observed["on_all_desktops"])
                if desired and desktop_ok:
                    r["state"] = "OK"
                    r["detail"] = (f'{r["kind"]}: {observed["caption"]} '
                                   f'(pid={observed["pid"]}) '
                                   f'before={r["placement_before"]} '
                                   f'after=[{r["desktop"]}] '
                                   f'({geo["x"]},{geo["y"]}) '
                                   f'{geo["width"]}x{geo["height"]} '
                                   f'tiled={str(r["placement_tiled"]).lower()} '
                                   f'fullscreen={str(r["placement_fullscreen"]).lower()}')
            if (r["state"] == "VERIFYING" and
                    time.monotonic() >= r["created"] + 15.0):
                observed = self.observed_windows.get(identifier)
                actual = "window not observed"
                if observed is not None:
                    actual = (f'desktops={observed["desktops"]} '
                              f'geometry={observed["geometry"]}')
                r["state"] = "ERROR"
                r["detail"] = "placement confirmation timed out: " + actual
        if r["state"] in ("OK", "ERROR"):
            self._sync_managed_placement()

    @dbus.service.method(IFACE, in_signature="sss", out_signature="")
    def Complete(self, request_id, result, detail):
        """KWin reports accepted assignment; broker confirms observed state.

        Preserve existing OK/ERROR messages for legacy callers and tests.
        VERIFY is an additive result, with an exact KWin UUID and diagnostics.
        """
        r = self.request
        if r is None or r["id"] != request_id or r["state"] != "RUNNING":
            raise dbus.DBusException("Unknown or inactive request",
                                     name=IFACE + ".InvalidRequest")
        if result not in ("OK", "ERROR", "VERIFY"):
            raise dbus.DBusException("Invalid completion result",
                                     name=IFACE + ".BadArguments")
        if result == "VERIFY":
            try:
                payload = json.loads(detail)
                identifier = str(uuid.UUID(payload["window_uuid"]))
                before = payload["before"]
                if (not isinstance(before, str) or len(before) > 256
                        or not isinstance(payload["tiled"], bool)
                        or not isinstance(payload["fullscreen"], bool)):
                    raise ValueError("invalid placement detail")
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise dbus.DBusException("Invalid placement verification",
                                         name=IFACE + ".BadArguments") from exc
            if not self.observation_synced:
                r["state"] = "ERROR"
                r["detail"] = "KWin observation is not synchronized"
            else:
                r["state"] = "VERIFYING"
                r["placement_uuid"] = identifier
                r["placement_before"] = before
                r["placement_tiled"] = payload["tiled"]
                r["placement_fullscreen"] = payload["fullscreen"]
                r["observation_source"] = self.observation_source
                self._advance_placement()
        else:
            r["state"] = result
            r["detail"] = str(detail)[:1024]
        self._sync_managed_placement()

    @dbus.service.method(IFACE, in_signature="s", out_signature="s")
    def Status(self, request_id):
        self._advance_placement()
        r = self.request
        if r is None or r["id"] != request_id:
            return "UNKNOWN"
        return r["state"] + (" " + r["detail"] if r["detail"] else "")

'''
    s = s[:start] + new + s[end:]
    # Registration must link with whichever placement state already arrived.
    s = replace_once(s, '''                answer = {"state": "registered", "request_id": request_id,
                          "managed_id": managed.managed_id,
                          "window_uuid": managed.window_uuid}
''', '''                self._sync_managed_placement()
                answer = {"state": "registered", "request_id": request_id,
                          "managed_id": managed.managed_id,
                          "window_uuid": managed.window_uuid}
''', 'registration hooks placement')
    # Both fast-path and change-path observations must advance requests.
    # The same branch tail occurs for "existing" and "changed" observations.
    old = '''            self.observed_windows[identifier] = details
            self._refresh_registered_window(identifier, details)
            return
'''
    new = '''            self.observed_windows[identifier] = details
            self._refresh_registered_window(identifier, details)
            self._advance_placement()
            return
'''
    if s.count(old) != 2:
        raise ValueError('Expected two observation refresh tails')
    s = s.replace(old, new)
    s = replace_once(s, '''        self._refresh_registered_window(
            identifier, None if event == "removed" else details)

        # 'existing', 'added' and 'removed' cannot be evicted by dragging.
''', '''        self._refresh_registered_window(
            identifier, None if event == "removed" else details)
        self._advance_placement(removed_uuid=identifier if event == "removed" else None)

        # 'existing', 'added' and 'removed' cannot be evicted by dragging.
''', 'added/removed observation refresh')
    s = replace_once(s, '''                self._refresh_registered_window(
                    identifier, self.observed_windows.get(identifier))

    # Read-only diagnostic query.''', '''                self._refresh_registered_window(
                    identifier, self.observed_windows.get(identifier))
        self._advance_placement()

    # Read-only diagnostic query.''', 'inventory refresh')
    return s

# Test fixture added in a separate string below.

NEW_TEST_NAME = 'tests/test_step1_4d_placement.py'
NEW_JS_NAME = 'tests/test_step1_4d_placement.js'
NEW_JS_CONTENT = '// Copyright 2025-2026 Joseph Brendler\n// SPDX-License-Identifier: GPL-3.0-or-later\n// Verify resident reports an applied request for asynchronous confirmation.\n\'use strict\';\nconst test = require(\'node:test\');\nconst assert = require(\'node:assert/strict\');\nconst fs = require(\'node:fs\');\nconst path = require(\'node:path\');\nconst vm = require(\'node:vm\');\n\nconst source = fs.readFileSync(path.join(__dirname, \'..\', \'joetoo-kwin-resident.js\'), \'utf8\');\nconst begin = source.indexOf(\'function placeWindow(win, request, operation) {\');\nconst end = source.indexOf(\'// The original working active-window path remains available.\', begin);\nassert.ok(begin >= 0 && end > begin);\nconst placement = source.slice(begin, end);\n\nfunction simulate({exists = true, delayed = true, desktopCount = 2} = {}) {\n    let geometry = {x: 535, y: 76, width: 700, height: 700};\n    let nextGeometry;\n    let currentDesktop = [{x11DesktopNumber: 1}];\n    let nextDesktop;\n    const win = {\n        deleted: !exists, tile: null, fullScreen: false, internalId: \'d848c4c9-64ed-48bf-b083-40230314d5ab\',\n        get frameGeometry() { return geometry; },\n        set frameGeometry(value) { nextGeometry = value; if (!delayed) geometry = value; },\n        get desktops() { return currentDesktop; },\n        set desktops(value) { nextDesktop = value; if (!delayed) currentDesktop = value; },\n    };\n    const results = [];\n    const workspace = {desktops: Array.from({length: desktopCount}, (_, i) => ({x11DesktopNumber: i+1}))};\n    const ctx = {workspace, windowUUID: w => w.internalId,\n                 geometryText: w => `${w.frameGeometry.x},${w.frameGeometry.y}`,\n                 finish: (req, state, detail) => results.push({state, detail})};\n    vm.runInNewContext(placement + \'\\nplaceWindow(win, request, "move");\',\n                       {...ctx, win, request: {desktop: 2, x: 19, y: 54, width: 816, height: 918}});\n    return {results, commit: () => {geometry = nextGeometry; currentDesktop = nextDesktop;}};\n}\n\ntest(\'stale immediate Wayland frame is verification pending, not failure\', () => {\n    const {results} = simulate({delayed: true});\n    assert.equal(results.length, 1);\n    assert.equal(results[0].state, \'VERIFY\');\n    const info = JSON.parse(results[0].detail);\n    assert.equal(info.window_uuid, \'d848c4c9-64ed-48bf-b083-40230314d5ab\');\n    assert.match(info.before, /535,76/);\n});\n\ntest(\'already-converged frame also requires exact UUID broker verification\', () => {\n    assert.equal(simulate({delayed: false}).results[0].state, \'VERIFY\');\n});\n\ntest(\'missing desktop is an immediate real error\', () => {\n    assert.equal(simulate({desktopCount: 1}).results[0].state, \'ERROR\');\n});\n\ntest(\'deleted window is an immediate real error\', () => {\n    assert.equal(simulate({exists: false}).results[0].state, \'ERROR\');\n});\n'
NEW_TEST_CONTENT = '#!/usr/bin/env python3\n# Copyright 2025-2026 Joseph Brendler\n# SPDX-License-Identifier: GPL-3.0-or-later\n"""Step 1.4d placement confirmation: delayed observations, bounds, UUID safety."""\n\nimport json\nfrom unittest import TestCase\nfrom unittest.mock import patch\nfrom test_step1_3a import load_broker_without_real_dbus, observation\n\nSOURCE = \'step1-4d-placement-test\'\nA = \'d848c4c9-64ed-48bf-b083-40230314d5ab\'\nB = \'d848c4c9-64ed-48bf-b083-40230314d5ac\'\n\n\nclass AsyncPlacementTests(TestCase):\n    def setUp(self):\n        self.module = load_broker_without_real_dbus()\n        self.broker = self.module.Broker(object())\n        self.now = [100.0]\n        clock = patch.object(self.module.time, \'monotonic\',\n                             side_effect=lambda: self.now[0])\n        clock.start()\n        self.addCleanup(clock.stop)\n        self.revision = 0\n        self.sync([])\n\n    @staticmethod\n    def window(wid=A, pid=501, desktop=1, x=535, y=76, w=700, h=700):\n        value = json.loads(observation(uuid=wid, desktops=[desktop]))[\'window\']\n        value[\'pid\'] = pid\n        value[\'geometry\'] = {\'x\': x, \'y\': y, \'width\': w, \'height\': h}\n        return value\n\n    def sync(self, windows):\n        self.revision += 1\n        self.broker.SyncInventory(json.dumps({\n            \'source\': SOURCE, \'revision\': self.revision, \'windows\': windows}))\n\n    def event(self, state, window):\n        self.revision += 1\n        self.broker.ObserveWindow(json.dumps({\n            \'source\': SOURCE, \'revision\': self.revision,\n            \'event\': state, \'window\': window}))\n\n    @staticmethod\n    def details(wid=A):\n        return json.dumps({\'window_uuid\': wid, \'before\': \'[1] (535,76) 700x700\',\n                           \'immediate\': \'[1] (535,76) 700x700\',\n                           \'tiled\': False, \'fullscreen\': False})\n\n    def arm_move(self, desktop=1, x=19, y=54, w=816, h=918, wid=A):\n        rid = self.broker.Submit(desktop, x, y, w, h)\n        taken = json.loads(self.broker.Take())\n        self.assertEqual(taken[\'id\'], rid)\n        self.broker.Complete(rid, \'VERIFY\', self.details(wid))\n        return rid\n\n    def arm_managed(self, desktop=1, slot=1, x=19):\n        ids = json.loads(self.broker.SubmitManagedLaunch(\n            \'konsole\', desktop, slot, x, 54, 816, 918))\n        placement = json.loads(self.broker.TakeLaunch(\'konsole\', \'org.kde.konsole\'))\n        self.assertEqual(placement[\'id\'], ids[\'placement_request_id\'])\n        return ids\n\n    def register(self, ids, wid=A, pid=501, desktop=1, x=535, y=76, w=700, h=700):\n        self.broker.SetManagedLaunchPid(ids[\'registration_request_id\'], pid)\n        self.event(\'added\', self.window(wid, pid, desktop, x, y, w, h))\n        self.assertEqual(json.loads(self.broker.PollManagedLaunch(\n            ids[\'registration_request_id\']))[\'state\'], \'pending\')\n        self.now[0] += 0.6  # unchanged ambiguity quiet period\n        result = json.loads(self.broker.PollManagedLaunch(ids[\'registration_request_id\']))\n        self.assertEqual(result[\'state\'], \'registered\')\n        return result\n\n    def test_delayed_success_not_premature_error(self):\n        self.sync([self.window()])\n        rid = self.arm_move()\n        self.assertEqual(self.broker.Status(rid), \'VERIFYING\')\n        self.event(\'changed\', self.window(x=19, y=54, w=816, h=918))\n        self.assertTrue(self.broker.Status(rid).startswith(\'OK move:\'))\n\n    def test_stale_size_timeout_is_real_failure(self):\n        self.sync([self.window()])\n        rid = self.arm_move(desktop=1, x=100, y=200, w=900, h=900)\n        self.assertEqual(self.broker.Status(rid), \'VERIFYING\')\n        self.event(\'changed\', self.window(x=100, y=200, w=700, h=700))\n        self.assertEqual(self.broker.Status(rid), \'VERIFYING\')\n        self.now[0] += 15.1\n        self.assertIn(\'ERROR placement confirmation timed out\', self.broker.Status(rid))\n\n    def test_unrelated_window_does_not_satisfy_uuid(self):\n        self.sync([self.window()])\n        rid = self.arm_move()\n        self.event(\'added\', self.window(wid=B, pid=777, x=19, y=54, w=816, h=918))\n        self.assertEqual(self.broker.Status(rid), \'VERIFYING\')\n\n    def test_disappearance_is_terminal_error(self):\n        self.sync([self.window()])\n        rid = self.arm_move()\n        self.event(\'removed\', self.window())\n        self.assertIn(\'ERROR target window disappeared\', self.broker.Status(rid))\n\n    def test_active_verify_blocks_overlapping_move(self):\n        self.sync([self.window()])\n        self.arm_move()\n        with self.assertRaises(self.module.dbus.DBusException):\n            self.broker.Submit(1, 10, 20, 700, 700)\n\n    def test_managed_registered_before_delayed_placement(self):\n        ids = self.arm_managed()\n        self.register(ids)\n        self.assertEqual(json.loads(self.broker.GetManaged(\'win-001\'))\n                         [\'window\'][\'placement\'], \'pending\')\n        self.broker.Complete(ids[\'placement_request_id\'], \'VERIFY\', self.details())\n        self.assertEqual(self.broker.Status(ids[\'placement_request_id\']), \'VERIFYING\')\n        self.event(\'changed\', self.window(x=19, y=54, w=816, h=918))\n        self.assertTrue(self.broker.Status(ids[\'placement_request_id\']).startswith(\'OK \'))\n        self.assertEqual(json.loads(self.broker.GetManaged(\'win-001\'))\n                         [\'window\'][\'placement\'], \'succeeded\')\n\n    def test_managed_placement_before_registration(self):\n        ids = self.arm_managed()\n        self.broker.Complete(ids[\'placement_request_id\'], \'VERIFY\', self.details())\n        self.register(ids, x=19, y=54, w=816, h=918)\n        self.assertEqual(json.loads(self.broker.GetManaged(\'win-001\'))\n                         [\'window\'][\'placement\'], \'succeeded\')\n\n    def test_mismatched_placement_uuid_fails_closed(self):\n        ids = self.arm_managed()\n        self.broker.Complete(ids[\'placement_request_id\'], \'VERIFY\', self.details(B))\n        self.register(ids)\n        self.assertIn(\'ERROR placement UUID differs\',\n                      self.broker.Status(ids[\'placement_request_id\']))\n        record = json.loads(self.broker.GetManaged(\'win-001\'))[\'window\']\n        self.assertEqual(record[\'placement\'], \'failed\')\n        self.assertEqual(record[\'presence\'], \'present\')\n\n    def test_managed_timeout_reports_failed_not_registration_failure(self):\n        ids = self.arm_managed()\n        self.register(ids)\n        self.broker.Complete(ids[\'placement_request_id\'], \'VERIFY\', self.details())\n        self.now[0] += 15.1\n        self.assertTrue(self.broker.Status(ids[\'placement_request_id\']).startswith(\'ERROR \'))\n        record = json.loads(self.broker.GetManaged(\'win-001\'))[\'window\']\n        self.assertEqual(record[\'placement\'], \'failed\')\n        self.assertEqual(record[\'presence\'], \'present\')\n        self.assertEqual(json.loads(self.broker.RegistryStatus())\n                         [\'request_counts\'][\'succeeded\'], 1)\n\n    def test_legacy_complete_still_supported(self):\n        rid = self.broker.Submit(1, 1, 2, 700, 700)\n        self.broker.Take()\n        self.broker.Complete(rid, \'OK\', \'legacy result\')\n        self.assertEqual(self.broker.Status(rid), \'OK legacy result\')\n\n    def test_malformed_uuid_refused(self):\n        rid = self.broker.Submit(1, 19, 54, 816, 918)\n        self.broker.Take()\n        with self.assertRaises(self.module.dbus.DBusException):\n            self.broker.Complete(rid, \'VERIFY\', self.details(\'not-a-uuid\'))\n        self.assertEqual(self.broker.Status(rid), \'RUNNING\')\n'


def main():
    checkout = pathlib.Path.cwd()
    rels = sorted(SHA)
    originals = {}
    replacements = {}
    actions = {'joetoo-kwin-resident.js': transform_js,
               'libexec/joetoo-kwind': transform_broker,
               'libexec/joetoo_kwin_registry.py': transform_registry}
    for name in rels:
        path = checkout / PREFIX / name
        if not path.is_file():
            raise ValueError(f'Expected file missing: {path}')
        digest = subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()
        if digest != SHA[name]:
            raise ValueError(f'{name}: baseline blob {digest}, expected {SHA[name]}; '
                             'do not overwrite maintainer edits')
        originals[name] = path.read_text()
        replacements[name] = actions[name](originals[name])
    for name in (NEW_TEST_NAME, NEW_JS_NAME):
        if (checkout / PREFIX / name).exists():
            raise ValueError(f'Already exists: {name}')
    for name in [*rels, NEW_TEST_NAME, NEW_JS_NAME]:
        full = PREFIX + name
        old = originals.get(name, '')
        new = (NEW_TEST_CONTENT if name == NEW_TEST_NAME else
               NEW_JS_CONTENT if name == NEW_JS_NAME else replacements[name])
        first = 'a/' + full if old else '/dev/null'
        second = 'b/' + full
        d = ''.join(difflib.unified_diff(old.splitlines(keepends=True),
                                         new.splitlines(keepends=True),
                                         fromfile=first, tofile=second, n=3))
        if not d:
            raise ValueError(f'No diff generated: {name}')
        sys.stdout.write(f'diff --git a/{full} b/{full}\n')
        if not old:
            sys.stdout.write('new file mode 100644\n')
        sys.stdout.write(d)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'REFUSED: {exc}', file=sys.stderr)
        raise SystemExit(2)
