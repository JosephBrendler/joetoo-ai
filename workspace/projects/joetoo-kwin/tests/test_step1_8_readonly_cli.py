# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.8 -s/-i: disposable-bus read-only CLI and response-validation tests."""
import copy
import json
import os
import shutil
from pathlib import Path
import subprocess
import unittest

from test_step1_5a_plan import PlannerHarness
from test_step1_3a import WINDOW_ID


class ReadOnlyCliTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        shutil.copyfile(Path(__file__).resolve().parents[1] / 'libexec/joetoo_kwin_readonly.py',
                        self.folder / 'libexec/joetoo_kwin_readonly.py')
        self.payload = self.folder / 'readonly.json'
        self.env.update(READONLY_FILE=str(self.payload), READONLY_EXIT='0')
        spy = self.folder / 'qdbus6'
        spy.write_text('''#!/usr/bin/env python3
import json, os, sys
with open(os.environ['TRACE'], 'a') as out:
    out.write(json.dumps(sys.argv[1:]) + '\\n')
sys.stdout.buffer.write(open(os.environ['READONLY_FILE'], 'rb').read())
sys.exit(int(os.environ['READONLY_EXIT']))
''')
        spy.chmod(0o755)
        self.status = dict(
            placement_transaction=dict(id=None, state='IDLE'),
            managed_close_active=False, managed_close_protocol=1,
            recovery_snapshot_protocol=1, recovery='inactive',
            viewer_protocol=1, viewer_cleanup_uncertain=False,
            initial_layout_protocol=1, single_raise_protocol=1,
            initial_layout_active=False, managed_count=0,
            presence_counts=dict(present=0, missing=0, uncertain=0),
            request_count=0,
            request_counts=dict(pending=0, running=0, succeeded=0,
                                failed=0, timeout=0, ambiguous=0),
            observation=dict(synchronized=True, source='observer-1',
                             revision=3, observed_count=0))
        self.window = dict(state='FOUND', window=dict(
            managed_id='win-001', window_uuid=WINDOW_ID,
            request_id='PRIVATE_REQUEST_TOKEN', run_id=None,
            intended=dict(desktop=3, slot=1), presence='present',
            placement='succeeded', connection='not_attempted',
            observation=dict(pid=1234, resource_class='konsole',
                             caption='PRIVATE_CAPTION', target='PRIVATE_TARGET')))

    def query(self, args, payload, expected=0, method=None):
        self.payload.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        self.calls.unlink(missing_ok=True)
        run = subprocess.run(['bash', str(self.client), *args], env=self.env,
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
        calls = [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []
        if method is not None:
            args_expected = ['org.joetoo.KWinBridge', '/org/joetoo/KWinBridge',
                             f'org.joetoo.KWinBridge.{method}']
            if method == 'GetManaged':
                args_expected.append('win-001')
            self.assertEqual(calls, [args_expected])
        else:
            self.assertEqual(calls, [])
        return run.stdout + run.stderr

    def test_status_empty_and_read_only_without_sourcing_configuration(self):
        user = Path(self.env['XDG_CONFIG_HOME']) / 'joetoo-kwin'
        user.mkdir(parents=True)
        (user / 'defaults.conf').write_text('exit 99\n')
        (user / 'joetoo-kwin.conf').write_text('exit 99\n')
        output = self.query(['-s'], self.status, method='RegistryStatus')
        self.assertIn('Managed windows: 0', output)
        self.assertIn('No reported Busy/uncertain flags', output)
        self.assertIn('not remote connection health', output)

    def test_status_placement_transaction_terminal_and_active_states(self):
        # The broker retains its last completed placement: OK is not in-flight.
        for state in ('IDLE', 'OK'):
            with self.subTest(state=state):
                status = copy.deepcopy(self.status)
                status['placement_transaction'] = dict(
                    state=state, id=None if state == 'IDLE' else 'attempt-123')
                output = self.query(['-s'], status, method='RegistryStatus')
                self.assertIn('No reported Busy/uncertain flags', output)
                self.assertNotIn('placement transaction active', output)

        for state in ('PENDING', 'RUNNING', 'VERIFYING'):
            with self.subTest(state=state):
                status = copy.deepcopy(self.status)
                status['placement_transaction'] = dict(state=state, id='attempt-123')
                output = self.query(['-s'], status, method='RegistryStatus')
                self.assertIn('Busy/uncertain', output)
                self.assertIn('placement transaction active', output)

        status = copy.deepcopy(self.status)
        status['placement_transaction'] = dict(state='ERROR', id='attempt-123')
        output = self.query(['-s'], status, method='RegistryStatus')
        self.assertIn('last placement transaction failed', output)
        self.assertNotIn('placement transaction active', output)

        for state, identifier in (('UNKNOWN', 'attempt-123'),
                                  ('OK', None), ('IDLE', 'attempt-123')):
            with self.subTest(state=state, identifier=identifier):
                status = copy.deepcopy(self.status)
                status['placement_transaction'] = dict(state=state, id=identifier)
                output = self.query(['-s'], status, expected=2, method='RegistryStatus')
                self.assertIn('Malformed or inconsistent', output)
                self.assertNotIn('Managed windows:', output)

    def test_status_busy_and_uncertainty_is_not_misreported_ready(self):
        status = copy.deepcopy(self.status)
        status['placement_transaction'] = dict(id='attempt-123', state='RUNNING')
        status['managed_count'] = 2
        status['presence_counts'] = dict(present=1, missing=0, uncertain=1)
        status['recovery'] = 'reconciling'
        status['viewer_cleanup_uncertain'] = True
        status['observation']['synchronized'] = False
        output = self.query(['-vs'], status, method='RegistryStatus')
        self.assertIn('Busy/uncertain', output)
        self.assertIn('viewer cleanup uncertain', output)
        self.assertIn('recovery not ready', output)
        self.assertIn('uncertain=1', output)

    def test_status_inconsistent_or_malformed_fails_without_partial_details(self):
        cases = [dict(self.status, managed_count=1),
                 dict(self.status, managed_count=True),
                 '{"managed_count":0,"managed_count":0}',
                 dict(self.status, observation=dict(synchronized='true',
                     source='PRIVATE', revision=0, observed_count=0)),
                 'not JSON']
        for payload in cases:
            with self.subTest(payload=repr(payload)[:70]):
                output = self.query(['-s'], payload, expected=2, method='RegistryStatus')
                self.assertIn('Malformed or inconsistent', output)
                self.assertNotIn('Managed windows:', output)
                self.assertNotIn('PRIVATE', output)

    def test_info_found_and_historical_without_private_fields(self):
        for presence in ('present', 'missing', 'uncertain'):
            with self.subTest(presence=presence):
                value = copy.deepcopy(self.window)
                value['window']['presence'] = presence
                output = self.query(['-i', 'win-001'], value, method='GetManaged')
                self.assertIn('MANAGED_ID: win-001', output)
                self.assertIn('WINDOW_UUID: ' + WINDOW_ID, output)
                self.assertIn('last-known', output)
                self.assertIn('PRESENCE: ' + presence, output)
                for secret in ('PRIVATE_CAPTION', 'PRIVATE_TARGET', 'PRIVATE_REQUEST_TOKEN'):
                    self.assertNotIn(secret, output)

    def test_info_unknown_and_malformed_are_distinct(self):
        out = self.query(['-i', 'win-001'], {'state':'UNKNOWN'}, expected=1, method='GetManaged')
        self.assertIn('UNKNOWN', out)
        for payload in ({'state':'FOUND', 'window':dict(self.window['window'], managed_id='win-002')},
                        {'state':'FOUND', 'window':dict(self.window['window'], placement='PRIVATE')},
                        '{"state":"FOUND","state":"UNKNOWN"}'):
            out = self.query(['-i','win-001'], payload, expected=2, method='GetManaged')
            self.assertIn('Malformed or inconsistent', out)
            self.assertNotIn('PRIVATE', out)

    def test_invalid_arguments_have_no_dbus_call(self):
        for args in (['-s','extra'], ['-i'], ['-i','raw-uuid'], ['-i','win-000'],
                     ['-i','win-001','extra'], ['-i','win-1'], ['-f','unused','-s']):
            with self.subTest(args=args):
                self.query(args, self.status, expected=2)

    def test_missing_helper_fails_without_contacting_broker(self):
        (self.folder / 'libexec/joetoo_kwin_readonly.py').unlink()
        output = self.query(['-s'], self.status, expected=2)
        self.assertIn('helper unavailable', output)

    def test_broker_unavailable_distinct_from_unknown_or_empty(self):
        self.env['READONLY_EXIT'] = '7'
        for args,method in ((['-s'],'RegistryStatus'), (['-i','win-001'],'GetManaged')):
            with self.subTest(args=args):
                out = self.query(args, self.status, expected=2, method=method)
                self.assertIn('unavailable', out)
                self.assertNotIn('UNKNOWN', out)
