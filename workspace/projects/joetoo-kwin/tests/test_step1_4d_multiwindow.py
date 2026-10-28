#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4d: four-window broker registration and failure isolation (headless).

Simulated KWin events use real broker/registry implementations; no graphical
session, root privileges, OpenRC service or applications are started.
"""

import json
from unittest import TestCase
from unittest.mock import patch

from test_step1_3a import load_broker_without_real_dbus, observation

WINDOWS = tuple(f'd848c4c9-64ed-48bf-b083-40230314d5a{suffix}'
                for suffix in 'bcde')
SOURCE = 'step1-4d-resident'


class FourWindowRegistryTests(TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.clock = [100.0]
        fake_time = patch.object(self.module.time, 'monotonic',
                                 side_effect=lambda: self.clock[0])
        fake_time.start()
        self.addCleanup(fake_time.stop)
        self.revision = 1
        self.sync()

    @staticmethod
    def window(identifier, pid=42, desktop=1):
        item = json.loads(observation(uuid=identifier, desktops=[desktop]))['window']
        item['pid'] = pid
        return item

    def sync(self, windows=(), source=SOURCE):
        self.revision += 1
        self.broker.SyncInventory(json.dumps({
            'source': source, 'revision': self.revision,
            'windows': list(windows)}))

    def event(self, event, identifier, pid, desktop=1):
        self.revision += 1
        self.broker.ObserveWindow(json.dumps({
            'event': event, 'source': SOURCE, 'revision': self.revision,
            'window': self.window(identifier, pid, desktop)}))

    def arm(self, pid, desktop, slot):
        request_id = self.broker._begin_managed_launch(
            expected_class='konsole', run_id='run-four',
            recipe={'desktop': desktop, 'slot': slot,
                    'program': 'konsole', 'mode': 'local', 'target': ''})
        self.broker._set_managed_launch_pid(request_id, pid)
        return request_id

    def register(self, identifier, pid, desktop, slot):
        request_id = self.arm(pid, desktop, slot)
        self.event('added', identifier, pid, desktop)
        self.assertEqual(self.broker._poll_managed_launch(request_id)['state'],
                         'pending')
        self.clock[0] += 0.6
        result = self.broker._poll_managed_launch(request_id)
        self.assertEqual(result['state'], 'registered')
        return result

    def four_windows(self):
        return [self.register(identifier, pid, desktop, slot)
                for identifier, pid, desktop, slot in zip(
                    WINDOWS, (101, 102, 103, 104), (1, 1, 2, 2), (1, 2, 1, 2))]

    def test_two_desktops_four_independent_registrations(self):
        results = self.four_windows()
        self.assertEqual([r['managed_id'] for r in results],
                         ['win-001', 'win-002', 'win-003', 'win-004'])
        listing = json.loads(self.broker.ListManaged())
        self.assertEqual(listing['count'], 4)
        self.assertEqual([w['window_uuid'] for w in listing['windows']],
                         list(WINDOWS))
        for index, result in enumerate(results):
            by_alias = json.loads(self.broker.GetManaged(result['managed_id']))
            by_uuid = json.loads(self.broker.GetManaged(WINDOWS[index]))
            self.assertEqual(by_alias, by_uuid)
            self.assertEqual(by_alias['window']['observation']['desktops'],
                             [1, 1, 2, 2][index:index + 1])
            self.assertEqual(by_alias['window']['presence'], 'present')
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['request_counts']['succeeded'], 4)

    def test_disappearance_is_isolated_from_other_registrations(self):
        self.four_windows()
        self.event('removed', WINDOWS[1], 102)
        self.event('changed', WINDOWS[2], 999, desktop=2)
        states = [w['presence'] for w in
                  json.loads(self.broker.ListManaged())['windows']]
        self.assertEqual(states, ['present', 'missing', 'uncertain', 'present'])
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['presence_counts'],
                         {'present': 2, 'missing': 1, 'uncertain': 1})
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 4)

    def test_new_resident_invalidates_all_without_re_adoption(self):
        self.four_windows()
        self.sync([self.window(WINDOWS[0], 101)], source='new-resident')
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['presence_counts']['uncertain'], 4)
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 4)

    def test_ambiguous_same_pid_cannot_register_a_window(self):
        request_id = self.arm(101, 1, 1)
        self.event('added', WINDOWS[0], 101)
        self.event('added', WINDOWS[1], 101)
        self.clock[0] += 0.6
        result = self.broker._poll_managed_launch(request_id)
        self.assertEqual(result['state'], 'ambiguous')
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)
        self.assertEqual(json.loads(self.broker.RegistryStatus())
                         ['request_counts']['ambiguous'], 1)

    def test_failed_correlation_does_not_prevent_subsequent_windows(self):
        self.register(WINDOWS[0], 101, 1, 1)
        bad_id = self.arm(202, 1, 2)
        self.event('added', WINDOWS[1], 999)
        self.clock[0] += 15.1
        self.assertEqual(self.broker._poll_managed_launch(bad_id)['state'],
                         'timeout')
        self.register(WINDOWS[2], 103, 2, 1)
        listing = json.loads(self.broker.ListManaged())
        self.assertEqual([item['managed_id'] for item in listing['windows']],
                         ['win-001', 'win-002'])
        self.assertEqual([item['window_uuid'] for item in listing['windows']],
                         [WINDOWS[0], WINDOWS[2]])

    def test_preexisting_window_does_not_become_managed(self):
        self.sync([self.window(WINDOWS[0], 101)])
        request_id = self.arm(101, 1, 1)
        self.event('changed', WINDOWS[0], 101)
        self.clock[0] += 15.1
        self.assertEqual(self.broker._poll_managed_launch(request_id)['state'],
                         'timeout')
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)
