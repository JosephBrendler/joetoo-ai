#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4b headless broker/registry integration and safety contracts.

Neither D-Bus nor KWin, OpenRC or application launches are required.
"""

import json
from unittest import TestCase
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

SECOND = 'd848c4c9-64ed-48bf-b083-40230314d5ac'
THIRD = 'd848c4c9-64ed-48bf-b083-40230314d5ad'
SOURCE = 'kwin-step1-4b-resident'
RECIPE = {'desktop': 3, 'slot': 1, 'program': 'konsole',
          'mode': 'ssh', 'target': 'test.example'}


class BrokerRegistryIntegrationTests(TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.clock = [100.0]
        clock_patch = patch.object(self.module.time, 'monotonic',
                                   side_effect=lambda: self.clock[0])
        clock_patch.start()
        self.addCleanup(clock_patch.stop)
        self.revision = 1

    def sync(self, windows=None, source=SOURCE):
        self.revision += 1
        self.broker.SyncInventory(json.dumps({
            'source': source, 'revision': self.revision,
            'windows': [] if windows is None else windows}))

    @staticmethod
    def window(identifier=WINDOW_ID, pid=42, x=100):
        item = json.loads(observation('added', uuid=identifier, x=x))['window']
        item['pid'] = pid
        return item

    def event(self, event, identifier=WINDOW_ID, *, pid=42, x=100,
              source=SOURCE):
        self.revision += 1
        self.broker.ObserveWindow(json.dumps({
            'event': event, 'source': source, 'revision': self.revision,
            'window': self.window(identifier, pid, x)}))

    def arm(self, pid=42, recipe=None):
        rid = self.broker._begin_managed_launch(
            expected_class='konsole', recipe=RECIPE if recipe is None else recipe,
            run_id='run-001')
        self.broker._set_managed_launch_pid(rid, pid)
        return rid

    def poll(self, request_id):
        return self.broker._poll_managed_launch(request_id)

    def finish_match(self, request_id):
        self.assertEqual(self.poll(request_id)['state'], 'pending')
        self.clock[0] += 0.6
        answer = self.poll(request_id)
        self.assertEqual(answer['state'], 'registered')
        return answer

    def test_no_implicit_ownership_from_sync_and_public_probe(self):
        self.sync([self.window()])
        self.assertEqual(self.broker.registry.managed_windows, {})
        diagnostic = self.broker.BeginCorrelation('konsole', '')
        self.broker.SetCorrelationPid(diagnostic, 99)
        self.event('added', SECOND, pid=99)
        self.broker.PollCorrelation(diagnostic)
        self.clock[0] += 0.6
        self.assertEqual(json.loads(self.broker.PollCorrelation(diagnostic))['state'], 'MATCHED')
        self.assertEqual(self.broker.registry.managed_windows, {})
        self.assertEqual(self.broker.registry.requests, {})

    def test_private_launch_registers_multiple_windows_without_replacing_history(self):
        self.sync()
        first = self.arm(pid=42)
        self.event('added')
        one = self.finish_match(first)
        second = self.arm(pid=43)
        self.event('added', SECOND, pid=43)
        two = self.finish_match(second)
        self.assertEqual((one['managed_id'], two['managed_id']),
                         ('win-001', 'win-002'))
        self.assertEqual((one['window_uuid'], two['window_uuid']), (WINDOW_ID, SECOND))
        self.assertEqual(self.broker.registry.get_window('win-001').request_id, first)
        self.assertEqual(self.broker.registry.get_window('win-002').request_id, second)
        self.assertEqual(len(self.broker.registry.managed_windows), 2)
        self.assertNotIn('managed_id', json.loads(self.broker.ListObserved())['windows'][0])
        self.assertEqual(self.poll(first)['state'], 'UNKNOWN')
        self.assertEqual(self.poll(second), two)

    def test_private_request_does_not_accept_public_pid_or_result(self):
        self.sync()
        rid = self.broker._begin_managed_launch(expected_class='konsole', recipe=RECIPE)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetCorrelationPid(rid, 42)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.BeginCorrelation('konsole', '')
        self.broker._set_managed_launch_pid(rid, 42)
        self.event('added')
        self.finish_match(rid)
        self.assertEqual(self.broker.registry.get_window('win-001').window_uuid,
                         WINDOW_ID)

    def test_diagnostic_request_blocks_private_launch_until_complete(self):
        self.sync()
        rid = self.broker.BeginCorrelation('konsole', '')
        with self.assertRaises(self.module.RegistryError):
            self.broker._begin_managed_launch(expected_class='konsole', recipe={})
        self.clock[0] += 15.1
        self.assertEqual(json.loads(self.broker.PollCorrelation(rid))['state'], 'TIMEOUT')
        self.assertIsInstance(self.broker._begin_managed_launch(
            expected_class='konsole', recipe={}), str)

    def test_expired_unpolled_private_launch_does_not_block_next_launch(self):
        self.sync()
        first = self.arm()
        # Simulate a launch caller that never polls, then exceeds the deadline.
        self.clock[0] += 15.1
        second = self.arm(pid=43)
        self.assertNotEqual(first, second)
        self.assertEqual(self.poll(first)['state'], 'UNKNOWN')
        self.assertEqual(self.broker.registry.requests[first].state, 'timeout')
        self.assertEqual(self.broker.registry.requests[second].state, 'running')
        self.event('added', SECOND, pid=43)
        self.assertEqual(self.finish_match(second)['managed_id'], 'win-001')

    def test_diagnostic_probe_can_begin_after_unpolled_managed_timeout(self):
        self.sync()
        first = self.arm()
        self.clock[0] += 15.1
        diagnostic = self.broker.BeginCorrelation('konsole', '')
        self.assertTrue(diagnostic)
        self.assertEqual(self.broker.registry.requests[first].state, 'timeout')
        self.assertIsNone(self.broker.registry._active_request_id)
        self.assertEqual(self.broker.registry.managed_windows, {})

    def test_missing_and_changed_uuid_are_reconciled_independently(self):
        self.sync()
        first = self.arm()
        self.event('added')
        self.finish_match(first)
        second = self.arm(pid=43)
        self.event('added', SECOND, pid=43)
        self.finish_match(second)
        self.event('changed', WINDOW_ID, x=207)
        self.assertEqual(self.broker.registry.get_window('win-001').observation['geometry']['x'], 207)
        self.assertEqual(self.broker.registry.get_window('win-002').observation['geometry']['x'], 100)
        self.event('removed', WINDOW_ID)
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'missing')
        self.assertEqual(self.broker.registry.get_window('win-002').presence, 'present')
        self.event('added', WINDOW_ID)
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'missing')

    def test_same_source_inventory_does_not_adopt_missing_windows(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.finish_match(rid)
        self.sync([])
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'missing')
        self.sync([self.window()])
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'missing')

    def test_different_source_invalidates_all_registered_windows(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.finish_match(rid)
        self.revision = 1
        self.sync([self.window()], source='new-resident')
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'uncertain')
        self.assertEqual(len(self.broker.registry.managed_windows), 1)

    def test_source_change_cancels_inflight_registration_without_adoption(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.revision = 1
        self.sync([self.window()], source='new-resident')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'failed')
        self.assertEqual(result['detail'], 'STALE_SOURCE')
        self.assertEqual(self.broker.registry.managed_windows, {})
        self.assertEqual(self.broker.registry.requests[rid].state, 'failed')

    def test_pid_change_turns_registration_uncertain(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.finish_match(rid)
        self.event('changed', pid=99)
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'uncertain')

    def test_class_hint_cannot_register_unrelated_existing_window(self):
        self.sync([self.window()])
        rid = self.arm(pid=99)
        self.event('added', SECOND, pid=42)
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'timeout')
        self.assertEqual(self.broker.registry.managed_windows, {})

    def test_duplicate_uuid_cannot_replace_registered_identity(self):
        self.sync()
        first = self.arm()
        self.event('added')
        self.finish_match(first)
        rid = self.arm()
        # The original UUID was in the request's prelaunch inventory.
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'timeout')
        self.assertEqual(self.broker.registry.get_window('win-001').request_id, first)
        self.assertEqual(len(self.broker.registry.managed_windows), 1)

    def test_reobserved_uuid_cannot_be_registered_a_second_time(self):
        self.sync()
        original_request = self.arm()
        self.event('added')
        self.finish_match(original_request)
        # The UUID disappears from the current inventory, but remains a
        # registered (missing) managed-window identity in the registry.
        self.sync([])
        new_request = self.arm()
        self.event('added')
        self.assertEqual(self.poll(new_request)['state'], 'pending')
        self.clock[0] += 0.6
        rejected = self.poll(new_request)
        self.assertEqual(rejected['state'], 'failed')
        self.assertIn('already registered', rejected['detail'])
        self.assertEqual(self.broker.registry.requests[new_request].state, 'failed')
        self.assertEqual(self.broker.registry.get_window('win-001').request_id,
                         original_request)
        self.assertEqual(len(self.broker.registry.managed_windows), 1)
        # Failed attempts must not consume a managed alias.
        third_request = self.arm(pid=43)
        self.event('added', THIRD, pid=43)
        self.assertEqual(self.finish_match(third_request)['managed_id'], 'win-002')

    def test_invalid_inventory_is_atomic_for_managed_presence(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.finish_match(rid)
        with self.assertRaises(self.module.dbus.DBusException):
            self.sync([self.window(), self.window()])
        self.assertEqual(self.broker.registry.get_window('win-001').presence, 'present')

    def test_new_broker_does_not_restore_registry_without_checkpoint(self):
        self.sync()
        rid = self.arm()
        self.event('added')
        self.finish_match(rid)
        restarted = self.module.Broker(object())
        self.assertEqual(restarted.registry.managed_windows, {})
        # Restart recovery from a private checkpoint is the later Step 1.7.
        self.assertEqual(len(self.broker.registry.managed_windows), 1)


class RegistryInstallerContractTests(TestCase):
    def test_poc_installer_manages_registry_module_with_daemon(self):
        """The user-owned POC must install/check/back up the new dependency."""
        from pathlib import Path
        import subprocess
        installer = (Path(__file__).resolve().parents[1] / 'tools' /
                     'joetoo-kwind-install-poc')
        script = installer.read_text()
        self.assertIn('registry_source=$root/libexec/joetoo_kwin_registry.py', script)
        self.assertIn('registry_dest=$HOME/.local/libexec/joetoo_kwin_registry.py', script)
        self.assertIn('for mapping in service daemon registry override resident cli; do', script)
        self.assertIn('registry) src=$registry_source; dest=$registry_dest ;;', script)
        self.assertIn('install -D -m 0644 -- "$registry_source" "$registry_dest"', script)
        self.assertEqual(script.count('"$daemon_dest" "$registry_dest"'), 3)
        subprocess.run(['sh', '-n', str(installer)], check=True)
