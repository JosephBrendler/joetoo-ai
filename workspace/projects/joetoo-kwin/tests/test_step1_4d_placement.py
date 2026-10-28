#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4d placement confirmation: delayed observations, bounds, UUID safety."""

import json
from unittest import TestCase
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation

SOURCE = 'step1-4d-placement-test'
A = 'd848c4c9-64ed-48bf-b083-40230314d5ab'
B = 'd848c4c9-64ed-48bf-b083-40230314d5ac'


class AsyncPlacementTests(TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.now = [100.0]
        clock = patch.object(self.module.time, 'monotonic',
                             side_effect=lambda: self.now[0])
        clock.start()
        self.addCleanup(clock.stop)
        self.revision = 0
        self.sync([])

    @staticmethod
    def window(wid=A, pid=501, desktop=1, x=535, y=76, w=700, h=700):
        value = json.loads(observation(uuid=wid, desktops=[desktop]))['window']
        value['pid'] = pid
        value['geometry'] = {'x': x, 'y': y, 'width': w, 'height': h}
        return value

    def sync(self, windows):
        self.revision += 1
        self.broker.SyncInventory(json.dumps({
            'source': SOURCE, 'revision': self.revision, 'windows': windows}))

    def event(self, state, window):
        self.revision += 1
        self.broker.ObserveWindow(json.dumps({
            'source': SOURCE, 'revision': self.revision,
            'event': state, 'window': window}))

    @staticmethod
    def details(wid=A):
        return json.dumps({'window_uuid': wid, 'before': '[1] (535,76) 700x700',
                           'immediate': '[1] (535,76) 700x700',
                           'tiled': False, 'fullscreen': False})

    def arm_move(self, desktop=1, x=19, y=54, w=816, h=918, wid=A):
        rid = self.broker.Submit(desktop, x, y, w, h)
        taken = json.loads(self.broker.Take())
        self.assertEqual(taken['id'], rid)
        self.broker.Complete(rid, 'VERIFY', self.details(wid))
        return rid

    def arm_managed(self, desktop=1, slot=1, x=19):
        ids = json.loads(self.broker.SubmitManagedLaunch(
            'konsole', desktop, slot, x, 54, 816, 918))
        placement = json.loads(self.broker.TakeLaunch('konsole', 'org.kde.konsole'))
        self.assertEqual(placement['id'], ids['placement_request_id'])
        return ids

    def register(self, ids, wid=A, pid=501, desktop=1, x=535, y=76, w=700, h=700):
        self.broker.SetManagedLaunchPid(ids['registration_request_id'], pid)
        self.event('added', self.window(wid, pid, desktop, x, y, w, h))
        self.assertEqual(json.loads(self.broker.PollManagedLaunch(
            ids['registration_request_id']))['state'], 'pending')
        self.now[0] += 0.6  # unchanged ambiguity quiet period
        result = json.loads(self.broker.PollManagedLaunch(ids['registration_request_id']))
        self.assertEqual(result['state'], 'registered')
        return result

    def test_delayed_success_not_premature_error(self):
        self.sync([self.window()])
        rid = self.arm_move()
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')
        self.event('changed', self.window(x=19, y=54, w=816, h=918))
        self.assertTrue(self.broker.Status(rid).startswith('OK move:'))

    def test_stale_size_timeout_is_real_failure(self):
        self.sync([self.window()])
        rid = self.arm_move(desktop=1, x=100, y=200, w=900, h=900)
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')
        self.event('changed', self.window(x=100, y=200, w=700, h=700))
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')
        self.now[0] += 15.1
        self.assertIn('ERROR placement confirmation timed out', self.broker.Status(rid))

    def test_unrelated_window_does_not_satisfy_uuid(self):
        self.sync([self.window()])
        rid = self.arm_move()
        self.event('added', self.window(wid=B, pid=777, x=19, y=54, w=816, h=918))
        self.assertEqual(self.broker.Status(rid), 'VERIFYING')

    def test_disappearance_is_terminal_error(self):
        self.sync([self.window()])
        rid = self.arm_move()
        self.event('removed', self.window())
        self.assertIn('ERROR target window disappeared', self.broker.Status(rid))

    def test_active_verify_blocks_overlapping_move(self):
        self.sync([self.window()])
        self.arm_move()
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.Submit(1, 10, 20, 700, 700)

    def test_managed_registered_before_delayed_placement(self):
        ids = self.arm_managed()
        self.register(ids)
        self.assertEqual(json.loads(self.broker.GetManaged('win-001'))
                         ['window']['placement'], 'pending')
        self.broker.Complete(ids['placement_request_id'], 'VERIFY', self.details())
        self.assertEqual(self.broker.Status(ids['placement_request_id']), 'VERIFYING')
        self.event('changed', self.window(x=19, y=54, w=816, h=918))
        self.assertTrue(self.broker.Status(ids['placement_request_id']).startswith('OK '))
        self.assertEqual(json.loads(self.broker.GetManaged('win-001'))
                         ['window']['placement'], 'succeeded')

    def test_managed_placement_before_registration(self):
        ids = self.arm_managed()
        self.broker.Complete(ids['placement_request_id'], 'VERIFY', self.details())
        self.register(ids, x=19, y=54, w=816, h=918)
        self.assertEqual(json.loads(self.broker.GetManaged('win-001'))
                         ['window']['placement'], 'succeeded')

    def test_mismatched_placement_uuid_fails_closed(self):
        ids = self.arm_managed()
        self.broker.Complete(ids['placement_request_id'], 'VERIFY', self.details(B))
        self.register(ids)
        self.assertIn('ERROR placement UUID differs',
                      self.broker.Status(ids['placement_request_id']))
        record = json.loads(self.broker.GetManaged('win-001'))['window']
        self.assertEqual(record['placement'], 'failed')
        self.assertEqual(record['presence'], 'present')

    def test_managed_timeout_reports_failed_not_registration_failure(self):
        ids = self.arm_managed()
        self.register(ids)
        self.broker.Complete(ids['placement_request_id'], 'VERIFY', self.details())
        self.now[0] += 15.1
        self.assertTrue(self.broker.Status(ids['placement_request_id']).startswith('ERROR '))
        record = json.loads(self.broker.GetManaged('win-001'))['window']
        self.assertEqual(record['placement'], 'failed')
        self.assertEqual(record['presence'], 'present')
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['request_counts']['succeeded'], 1)

    def test_legacy_complete_still_supported(self):
        rid = self.broker.Submit(1, 1, 2, 700, 700)
        self.broker.Take()
        self.broker.Complete(rid, 'OK', 'legacy result')
        self.assertEqual(self.broker.Status(rid), 'OK legacy result')

    def test_malformed_uuid_refused(self):
        rid = self.broker.Submit(1, 19, 54, 816, 918)
        self.broker.Take()
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.Complete(rid, 'VERIFY', self.details('not-a-uuid'))
        self.assertEqual(self.broker.Status(rid), 'RUNNING')
