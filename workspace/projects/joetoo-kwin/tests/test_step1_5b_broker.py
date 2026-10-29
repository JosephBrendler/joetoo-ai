#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional move intent and exact-UUID verification with fake IPC imports."""
import copy
import json
import unittest
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

SOURCE = 'move-resident'
OTHER = 'd848c4c9-64ed-48bf-b083-40230314d5ac'


class OptionalBrokerTests(unittest.TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.now = 100
        clock = patch.object(self.module.time, 'monotonic', side_effect=lambda: self.now)
        clock.start(); self.addCleanup(clock.stop)
        self.window = json.loads(observation(desktops=[1]))['window']
        self.revision = 0
        self.sync()

    def sync(self, protocol=1, source=SOURCE):
        self.revision += 1
        self.broker.SyncInventory(json.dumps({'source': source, 'revision': self.revision,
            'windows': [self.window], 'move_protocol': protocol}))

    def arm(self, values=(2, 0, 0, 0, 0, False, True, True)):
        rid = self.broker.SubmitMove(*values)
        self.assertEqual(self.broker.Take(), '')
        request = json.loads(self.broker.TakeMove(SOURCE, WINDOW_ID))
        self.assertEqual(request['id'], rid)
        return rid

    def details(self):
        r = self.broker.request
        captured = {key: copy.deepcopy(self.window[key]) for key in ('geometry', 'desktops', 'on_all_desktops')}
        resolved = copy.deepcopy(captured)
        if not r['preserve_desktop']:
            resolved.update(desktops=[r['desktop']], on_all_desktops=False)
        for key in ('x', 'y', 'width', 'height'):
            flag = 'preserve_position' if key in ('x', 'y') else 'preserve_size'
            if not r[flag]: resolved['geometry'][key] = r[key]
        return {'window_uuid': WINDOW_ID, 'source': SOURCE, 'before': 'test frame',
                'tiled': False, 'fullscreen': False, 'captured': captured, 'resolved': resolved}

    def test_all_independent_flag_combinations(self):
        import itertools
        for pd, pp, ps in itertools.product((False, True), repeat=3):
            with self.subTest(flags=(pd, pp, ps)):
                self.broker.request = None
                self.window.update(desktops=[1, 2] if pd else [1], on_all_desktops=pd)
                self.sync()
                rid = self.arm((0 if pd else 2, 0 if pp else -40, 0 if pp else -50,
                                0 if ps else 800, 0 if ps else 900, pd, pp, ps))
                payload = self.details()
                self.broker.Complete(rid, 'VERIFY', json.dumps(payload))
                self.window.update(payload['resolved'])
                self.sync()
                self.assertTrue(self.broker.Status(rid).startswith('OK'), self.broker.Status(rid))
                self.assertEqual(len(self.broker.registry.managed_windows), 0)

    def test_wrong_uuid_and_changed_explicit_or_preserved_values_rejected(self):
        rid = self.arm()
        for change in ('uuid', 'explicit', 'preserved', 'nan', 'source', 'membership'):
            value = self.details()
            if change == 'uuid': value['window_uuid'] = OTHER
            if change == 'explicit': value['resolved']['desktops'] = [1]
            if change == 'preserved': value['resolved']['geometry']['width'] += 1
            if change == 'nan': value['captured']['geometry']['width'] = float('nan')
            if change == 'source': value['source'] = 'stale'
            if change == 'membership': value['captured']['desktops'] = [0]
            with self.subTest(change=change), self.assertRaises(self.module.dbus.DBusException):
                self.broker.Complete(rid, 'VERIFY', json.dumps(value))
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.Complete(rid, 'OK', 'unverified')

    def test_unrelated_uuid_cannot_complete_verification(self):
        rid = self.arm()
        value = self.details()
        self.broker.Complete(rid, 'VERIFY', json.dumps(value))
        self.window.update(value['resolved']); self.window['uuid'] = OTHER
        self.sync()
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')
        self.now += 16
        self.assertTrue(self.broker.Status(rid).startswith('ERROR'))

    def test_stale_and_changed_source_requests(self):
        rid = self.broker.SubmitMove(2, 0, 0, 0, 0, False, True, True)
        self.now += 16
        self.assertEqual(self.broker.TakeMove(SOURCE, WINDOW_ID), '')
        self.assertTrue(self.broker.Status(rid).startswith('ERROR'))
        self.broker.request = None
        rid = self.arm()
        value = self.details()
        self.sync(source='replacement')
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.Complete(rid, 'VERIFY', json.dumps(value))

    def test_unsupported_resident_and_legacy_compatibility(self):
        self.sync(protocol=0)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SubmitMove(2, 0, 0, 0, 0, False, True, True)
        rid = self.broker.Submit(2, -5, -6, 800, 900)
        self.assertEqual(json.loads(self.broker.Take())['id'], rid)
        self.broker.Complete(rid, 'OK', 'legacy')
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SubmitLaunch('konsole', 0, 0, 0, 0, 0)

    def test_placeholders_bounds_busy_and_duplicate_claim(self):
        for args in ((0, 0, 0, 0, 0, False, True, True),
                     (257, 0, 0, 0, 0, False, True, True),
                     (2, 1, 0, 0, 0, False, True, True),
                     (2, 0, 0, 1, 0, False, False, False)):
            with self.assertRaises(self.module.dbus.DBusException): self.broker.SubmitMove(*args)
        rid = self.arm()
        self.assertEqual(self.broker.TakeMove(SOURCE, OTHER), '')
        self.assertEqual(self.broker.request['placement_uuid'], WINDOW_ID)
        with self.assertRaises(self.module.dbus.DBusException): self.broker.Submit(1, 0, 0, 1, 1)
        with self.assertRaises(self.module.dbus.DBusException): self.broker.Complete('stale', 'ERROR', '')

    def test_delayed_success_and_fractional_preserved_frame(self):
        self.window['geometry'].update(x=-10.5, width=850.5)
        self.sync()
        rid = self.arm()
        value = self.details()
        self.broker.Complete(rid, 'VERIFY', json.dumps(value))
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')
        self.window.update(value['resolved']); self.sync()
        self.assertTrue(self.broker.Status(rid).startswith('OK'))

    def test_missing_target_and_observer_replacement_fail_closed(self):
        rid = self.broker.SubmitMove(2, 0, 0, 0, 0, False, True, True)
        self.assertEqual(self.broker.TakeMove(SOURCE, OTHER), '')
        self.assertTrue(self.broker.Status(rid).startswith('ERROR'))
        self.broker.request = None
        rid = self.arm()
        self.broker.Complete(rid, 'VERIFY', json.dumps(self.details()))
        self.sync(source='new-observer')
        self.assertTrue(self.broker.Status(rid).startswith('ERROR'))

    def test_verified_membership_report_never_uses_placeholder(self):
        for desktops, sticky, expected in [([2], False, '[2]'),
                                           ([2, 1], False, '[1,2]'),
                                           ([], True, '[all desktops]')]:
            with self.subTest(desktops=desktops, sticky=sticky):
                self.broker.request = None
                self.window.update(desktops=desktops, on_all_desktops=sticky)
                self.sync()
                rid = self.arm((0, 19, 54, 816, 918, True, False, False))
                value = self.details()
                self.broker.Complete(rid, 'VERIFY', json.dumps(value))
                self.window.update(value['resolved']); self.sync()
                status = self.broker.Status(rid)
                self.assertTrue(status.startswith('OK'), status)
                self.assertIn('after=' + expected + ' ', status)
                self.assertNotIn('after=[0]', status)

    def test_exact_geometry_rejects_roundoff_and_real_displacement(self):
        # Document current exact comparison without changing its contract.
        for actual in ({'width': 816.0000000000002},
                       {'x': 921.7951127814015, 'y': 76.30364413909359}):
            with self.subTest(actual=actual):
                self.broker.request = None
                rid = self.arm((0, 19, 54, 816, 918, True, False, False))
                value = self.details()
                self.broker.Complete(rid, 'VERIFY', json.dumps(value))
                self.window.update(value['resolved'])
                self.window['geometry'].update(actual)
                self.sync()
                self.assertEqual(self.broker.Status(rid), 'VERIFYING')
                self.now += 16
                self.assertIn('ERROR placement confirmation timed out', self.broker.Status(rid))

    def test_legacy_verified_desktop_report_unchanged(self):
        rid = self.broker.Submit(2, 19, 54, 816, 918)
        self.broker.Take()
        self.broker.Complete(rid, 'VERIFY', json.dumps({
            'window_uuid': WINDOW_ID, 'before': '[1] old frame',
            'tiled': False, 'fullscreen': False}))
        self.window.update(desktops=[2], on_all_desktops=False)
        self.window['geometry'].update(x=19, y=54, width=816, height=918)
        self.sync()
        status = self.broker.Status(rid)
        self.assertTrue(status.startswith('OK move:'), status)
        self.assertIn('after=[2] (19,54) 816x918', status)
