#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4c read-only D-Bus registry-query contracts (headless)."""

import ast
from copy import deepcopy
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

SECOND = 'd848c4c9-64ed-48bf-b083-40230314d5ac'
SOURCE = 'step1-4c-resident'
RECIPE = {'desktop': 3, 'slot': 1, 'program': 'konsole',
          'mode': 'ssh', 'target': 'private.example',
          'password': 'MUST_NOT_LEAK'}


class ReadOnlyManagedQueryTests(TestCase):
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
    def window(identifier=WINDOW_ID, pid=42):
        result = json.loads(observation(uuid=identifier))['window']
        result['pid'] = pid
        return result

    def event(self, kind, identifier=WINDOW_ID, pid=42):
        self.revision += 1
        self.broker.ObserveWindow(json.dumps({
            'source': SOURCE, 'revision': self.revision,
            'event': kind, 'window': self.window(identifier, pid)}))

    def register(self, identifier=WINDOW_ID, pid=42):
        request_id = self.broker._begin_managed_launch(
            expected_class='konsole', recipe=RECIPE, run_id='run-001')
        self.broker._set_managed_launch_pid(request_id, pid)
        self.event('added', identifier, pid)
        self.assertEqual(self.broker._poll_managed_launch(request_id)['state'],
                         'pending')
        self.clock[0] += 0.6
        answer = self.broker._poll_managed_launch(request_id)
        self.assertEqual(answer['state'], 'registered')
        return answer

    def test_empty_and_unsynchronized_queries(self):
        self.assertEqual(json.loads(self.broker.ListManaged()),
                         {'count': 0, 'windows': []})
        self.assertEqual(json.loads(self.broker.GetManaged('win-001')),
                         {'state': 'UNKNOWN'})
        status = json.loads(self.broker.RegistryStatus())
        self.assertEqual(status['managed_count'], 0)
        self.assertEqual(status['request_count'], 0)
        self.assertEqual(status['presence_counts'],
                         {'present': 0, 'missing': 0, 'uncertain': 0})
        self.assertEqual(status['observation'], {
            'synchronized': False, 'source': None,
            'revision': -1, 'observed_count': 0})

    def test_observation_does_not_create_managed_entries(self):
        self.sync([self.window()])
        self.assertEqual(json.loads(self.broker.ListManaged())['windows'], [])
        self.assertEqual(json.loads(self.broker.RegistryStatus())['observation']['observed_count'], 1)

    def test_multiple_registrations_and_both_lookup_keys(self):
        self.sync()
        first = self.register()
        second = self.register(SECOND, pid=43)
        listing = json.loads(self.broker.ListManaged())
        self.assertEqual(listing['count'], 2)
        self.assertEqual([item['managed_id'] for item in listing['windows']],
                         ['win-001', 'win-002'])
        self.assertEqual([item['window_uuid'] for item in listing['windows']],
                         [WINDOW_ID, SECOND])
        self.assertEqual([item['request_id'] for item in listing['windows']],
                         [first['request_id'], second['request_id']])
        self.assertEqual(json.loads(self.broker.GetManaged('win-001')),
                         json.loads(self.broker.GetManaged(WINDOW_ID)))
        result = json.loads(self.broker.GetManaged('win-002'))
        self.assertEqual(result['state'], 'FOUND')
        self.assertEqual(result['window']['observation']['pid'], 43)
        self.assertEqual(result['window']['observation']['geometry']['width'], 850)
        status = json.loads(self.broker.RegistryStatus())
        self.assertEqual(status['managed_count'], 2)
        self.assertEqual(status['request_counts']['succeeded'], 2)
        self.assertEqual(status['presence_counts']['present'], 2)

    def test_no_arbitrary_recipe_or_extra_observation_fields(self):
        self.sync()
        self.register()
        self.broker.registry.managed_windows[WINDOW_ID].observation['secret'] = 'OBS_SECRET'
        for payload in (self.broker.ListManaged(),
                        self.broker.GetManaged('win-001'),
                        self.broker.RegistryStatus()):
            self.assertNotIn('MUST_NOT_LEAK', payload)
            self.assertNotIn('private.example', payload)
            self.assertNotIn('OBS_SECRET', payload)
            self.assertNotIn('recipe', payload)
        self.assertNotIn('observation',
                         json.loads(self.broker.ListManaged())['windows'][0])

    def test_missing_and_uncertain_remain_registered(self):
        self.sync()
        self.register()
        self.register(SECOND, pid=43)
        self.event('removed')
        self.event('changed', SECOND, pid=99)
        status = json.loads(self.broker.RegistryStatus())
        self.assertEqual(status['managed_count'], 2)
        self.assertEqual(status['presence_counts'],
                         {'present': 0, 'missing': 1, 'uncertain': 1})
        self.assertEqual(json.loads(self.broker.GetManaged('win-001'))['window']['presence'],
                         'missing')
        self.assertEqual(json.loads(self.broker.GetManaged('win-002'))['window']['presence'],
                         'uncertain')

    def test_running_request_is_not_a_managed_window(self):
        self.sync()
        request_id = self.broker._begin_managed_launch(
            expected_class='konsole', recipe=RECIPE)
        status = json.loads(self.broker.RegistryStatus())
        self.assertEqual(status['request_counts']['pending'], 1)
        self.assertEqual(json.loads(self.broker.ListManaged())['count'], 0)
        self.broker._set_managed_launch_pid(request_id, 42)
        status = json.loads(self.broker.RegistryStatus())
        self.assertEqual(status['request_counts']['running'], 1)
        self.assertEqual(status['managed_count'], 0)

    def test_unknown_and_invalid_identifiers(self):
        self.sync()
        self.register()
        self.assertEqual(json.loads(self.broker.GetManaged('win-999')),
                         {'state': 'UNKNOWN'})
        self.assertEqual(json.loads(self.broker.GetManaged(SECOND)),
                         {'state': 'UNKNOWN'})
        self.assertEqual(json.loads(self.broker.GetManaged('not-a-uuid')),
                         {'state': 'UNKNOWN'})
        for invalid in ('', 'x' * 129, None):
            with self.subTest(identifier=invalid):
                with self.assertRaises(self.module.dbus.DBusException):
                    self.broker.GetManaged(invalid)

    def test_queries_do_not_change_registry_or_observer_state(self):
        self.sync()
        self.register()
        before = deepcopy((self.broker.registry.__dict__,
                           self.broker.observed_windows,
                           self.broker.observation_events,
                           self.broker.observation_revision))
        for _ in range(3):
            self.broker.ListManaged()
            self.broker.GetManaged('win-001')
            self.broker.GetManaged('not-a-uuid')
            self.broker.RegistryStatus()
        self.assertEqual(before, (self.broker.registry.__dict__,
                                  self.broker.observed_windows,
                                  self.broker.observation_events,
                                  self.broker.observation_revision))

    def test_dbus_signatures_are_additive_and_read_only(self):
        source = (Path(__file__).resolve().parents[1] / 'libexec' /
                  'joetoo-kwind').read_text()
        module = ast.parse(source)
        broker = next(node for node in module.body
                      if isinstance(node, ast.ClassDef) and node.name == 'Broker')
        signatures = {}
        for node in broker.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr == 'method'):
                    settings = {key.arg: ast.literal_eval(key.value)
                                for key in decorator.keywords}
                    signatures[node.name] = (settings.get('in_signature'),
                                             settings.get('out_signature'))
        for name, expected in {
            'ListManaged': ('', 's'), 'GetManaged': ('s', 's'),
            'RegistryStatus': ('', 's'), 'Submit': ('iiiii', 's'),
            'Take': ('', 's'), 'Status': ('s', 's'),
            'ListObserved': ('', 's'), 'ObserveWindow': ('s', ''),
        }.items():
            self.assertEqual(signatures[name], expected)
        self.assertFalse(any(name.startswith(('Register', 'CloseManaged'))
                             for name in signatures))
