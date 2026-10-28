#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4d: public launch-intent D-Bus seam, private broker registration."""

import json
from unittest import TestCase
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation

SOURCE = 'step1-4d-managed-wire'
WINDOWS = tuple(f'd848c4c9-64ed-48bf-b083-40230314d5a{digit}'
                for digit in 'bcde')


class ManagedLaunchWireTests(TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.now = [100.0]
        clock = patch.object(self.module.time, 'monotonic',
                             side_effect=lambda: self.now[0])
        clock.start()
        self.addCleanup(clock.stop)
        self.revision = 1
        self.sync()

    def sync(self, windows=()):
        self.revision += 1
        self.broker.SyncInventory(json.dumps({
            'source': SOURCE, 'revision': self.revision, 'windows': list(windows)}))

    @staticmethod
    def window(identifier, pid, desktop=1):
        data = json.loads(observation(uuid=identifier,
                                      desktops=[desktop]))['window']
        data['pid'] = pid
        return data

    def added(self, identifier, pid, desktop=1):
        self.revision += 1
        self.broker.ObserveWindow(json.dumps({
            'source': SOURCE, 'revision': self.revision,
            'event': 'added', 'window': self.window(identifier, pid, desktop)}))

    def submit(self, desktop=1, slot=1, x=19):
        return json.loads(self.broker.SubmitManagedLaunch(
            'konsole', desktop, slot, x, 54, 816, 918))

    def register(self, identifier, pid, desktop=1, slot=1, x=19):
        ids = self.submit(desktop, slot, x)
        self.assertIn('placement_request_id', ids)
        self.assertIn('registration_request_id', ids)
        self.assertNotEqual(ids['placement_request_id'],
                            ids['registration_request_id'])
        placement = json.loads(self.broker.TakeLaunch('konsole', 'org.kde.konsole'))
        self.assertEqual(placement['id'], ids['placement_request_id'])
        self.broker.Complete(ids['placement_request_id'], 'OK', 'test placement')
        self.broker.SetManagedLaunchPid(ids['registration_request_id'], pid)
        self.added(identifier, pid, desktop)
        self.assertEqual(json.loads(self.broker.PollManagedLaunch(
            ids['registration_request_id']))['state'], 'pending')
        self.now[0] += 0.6
        return json.loads(self.broker.PollManagedLaunch(
            ids['registration_request_id']))

    def test_four_real_arms_four_positive_registrations(self):
        answers = [self.register(wid, pid, desktop, slot, x)
                   for wid, pid, desktop, slot, x in zip(
                       WINDOWS, (101, 102, 103, 104),
                       (1, 1, 2, 2), (1, 2, 1, 2), (19, 873, 19, 873))]
        self.assertEqual([a['state'] for a in answers], ['registered'] * 4)
        self.assertEqual([a['managed_id'] for a in answers],
                         ['win-001', 'win-002', 'win-003', 'win-004'])
        listing = json.loads(self.broker.ListManaged())
        self.assertEqual(listing['count'], 4)
        self.assertEqual([w['window_uuid'] for w in listing['windows']],
                         list(WINDOWS))
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['request_counts']['succeeded'], 4)

    def test_placement_status_is_not_registration_evidence(self):
        ids = self.submit()
        self.broker.TakeLaunch('konsole', 'org.kde.konsole')
        self.broker.Complete(ids['placement_request_id'], 'OK', 'placed')
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)
        self.assertEqual(json.loads(self.broker.PollManagedLaunch(
            ids['registration_request_id']))['state'], 'pending')

    def test_existing_window_cannot_be_claimed(self):
        self.sync([self.window(WINDOWS[0], 101)])
        ids = self.submit()
        self.broker.SetManagedLaunchPid(ids['registration_request_id'], 101)
        self.now[0] += 15.1
        result = json.loads(self.broker.PollManagedLaunch(ids['registration_request_id']))
        self.assertEqual(result['state'], 'timeout')
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)

    def test_same_pid_two_new_windows_ambiguous(self):
        ids = self.submit()
        rid = ids['registration_request_id']
        self.broker.SetManagedLaunchPid(rid, 101)
        self.added(WINDOWS[0], 101)
        self.added(WINDOWS[1], 101)
        self.now[0] += 0.6
        self.assertEqual(json.loads(self.broker.PollManagedLaunch(rid))['state'],
                         'ambiguous')
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)

    def test_no_phantom_placement_after_unsynchronized_refusal(self):
        broker = self.module.Broker(object())
        with self.assertRaises(self.module.dbus.DBusException):
            broker.SubmitManagedLaunch('konsole', 1, 1, 19, 54, 816, 918)
        self.assertIsNone(broker.request)
        self.assertEqual(json.loads(broker.ListManaged())['count'], 0)

    def test_invalid_slot_and_wrong_pid_token_fail_closed(self):
        with self.assertRaises(self.module.dbus.DBusException):
            self.submit(slot=0)
        self.assertIsNone(self.broker.request)
        ids = self.submit()
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetManagedLaunchPid('made-up', 101)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetManagedLaunchPid(ids['registration_request_id'], -1)
        self.broker.SetManagedLaunchPid(ids['registration_request_id'], 101)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetManagedLaunchPid(ids['registration_request_id'], 101)
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)

    def test_failed_second_arm_preserves_previous_request(self):
        existing = self.broker.SubmitLaunch('konsole', 1, 19, 54, 816, 918)
        with self.assertRaises(self.module.dbus.DBusException):
            self.submit()
        self.assertEqual(self.broker.request['id'], existing)
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)
