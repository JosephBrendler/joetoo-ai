# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-networked harness tests. Real tools; synthetic placement bus/log/time.

Integration cases retain actual broker registration and Linux child/pidfd/FD
checks, substituting a disposable Python child, never SDL or a native session.
"""
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from contextlib import redirect_stderr
from test_step1_3a import WINDOW_ID


def module():
    spec = importlib.util.spec_from_file_location('immediate_harness_test',
        Path(__file__).resolve().parents[1] / 'tools/joetoo-sdl-immediate-placement.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.m = module()
        self.now = 100.
        self.output, self.calls, self.actions = [], [], []
        self.cancelled = False
        self.mode = 'success'
        self.registration = dict(protocol=1, state='registered', managed_id='win-001',
            request_id='b' * 32, window_uuid=WINDOW_ID, placement='not_requested', remote_session='unverified')
        self.result = dict(protocol=1, request_id='a' * 32, managed_id='win-001', window_uuid=WINDOW_ID,
            registration='registered', remote_session='unverified', placement='pending')
        outer = self
        class Bus:
            closed = False
            def close(self): self.closed = True
            def get_object(self, name, path, **kw):
                def invoke(key, **kw): outer.actions.append(key)
                return SimpleNamespace(invokeShortcut=invoke)
        self.bus = Bus()
        class API:
            def __init__(self, bus, interface, timeout):
                self.daemon = SimpleNamespace(GetNameOwner=lambda *a, **kw: ':1.accel')
            def call(self, name, *args):
                outer.calls.append(name)
                if name == 'RegistryStatus': return dict(observation=dict(source='source', revision=7))
                if name == 'SubmitSdlPlacement':
                    payload = json.loads(args[0])
                    outer.assertEqual((payload['desktop'], payload['slot']), (1, 1))
                    outer.assertEqual({k: payload[k] for k in outer.m.DEFAULT_GEOMETRY}, outer.m.DEFAULT_GEOMETRY)
                    outer.assertNotIn('window_uuid', payload)
                    if outer.mode == 'submit_failure': raise RuntimeError('PRIVATE exception')
                    return dict(outer.result, window_uuid=('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
                        if outer.mode == 'wrong_uuid' else WINDOW_ID))
                if name == 'PollSdlPlacement':
                    if outer.mode == 'cancel': outer.cancelled = True
                    if outer.mode == 'transport': raise RuntimeError('PRIVATE bus error')
                    if outer.mode in ('timeout', 'cancel'): return dict(outer.result)
                    return dict(outer.result, placement='failed' if outer.mode == 'failed' else 'succeeded',
                        reason='Placement geometry confirmation timed out' if outer.mode == 'failed' else 'verified')
                if name == 'CancelSdlPlacement': return dict(outer.result, placement='failed')
                if name == 'GetManaged':
                    if outer.mode == 'snapshot_failure': raise RuntimeError('PRIVATE snapshot')
                    return dict(state='FOUND', window=dict(window_uuid=WINDOW_ID, placement='succeeded', presence='present',
                        observation=dict(geometry=dict(outer.m.DEFAULT_GEOMETRY), desktops=[1], on_all_desktops=False,
                                         caption='PRIVATE caption')))
                raise AssertionError(name)
        self.patch = patch.object(self.m.placement.connection, 'Connection', API)
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.capture = redirect_stderr(io.StringIO())
        self.capture.__enter__(); self.addCleanup(self.capture.__exit__, None, None, None)
        self.trace = self.m.BrokerTrace(None, 1024)
        self.experiment = self.m.Experiment(lambda: self.bus, lambda obj, iface: obj, self.trace,
            desktop=1, slot=1, geometry=self.m.DEFAULT_GEOMETRY, timeout_ms=1000, poll_ms=100,
            call_timeout_ms=1000, emit=self.output.append, clock=lambda: self.now)
        self.real_release = self.m.placement.release
        def release(*args, **kwargs):
            def sleep(seconds): self.now += seconds
            return self.real_release(*args, **kwargs, sleep=sleep)
        self.experiment.release = release

    def run_experiment(self): self.experiment.registered(self.registration, lambda: self.cancelled)
    def rows(self): return [json.loads(line) for line in self.output]

    def test_immediate_owned_uuid_and_geometry_no_readiness_or_sleep_before_submit(self):
        self.run_experiment()
        rows = self.rows()
        self.assertEqual([row['stage'] for row in rows],
            ['registered', 'placement_submission', 'placement_accepted', 'placement_terminal', 'experiment_result'])
        self.assertEqual(rows[1]['since_registration_ms'], 0)
        self.assertEqual(self.actions, ['joetoo_bridge_sdl_placement'])
        self.assertEqual(self.calls, ['RegistryStatus', 'SubmitSdlPlacement', 'PollSdlPlacement', 'GetManaged'])
        final = rows[-1]
        self.assertEqual(final['observed']['geometry'], self.m.DEFAULT_GEOMETRY)
        self.assertEqual(final['observed']['window_uuid'], WINDOW_ID)
        self.assertEqual(final['broker_evidence']['reason'], 'diagnostic_log_not_supplied')
        self.assertIsNone(final['broker_evidence']['assignment'])
        self.assertTrue(self.experiment.placement_ok)
        self.assertTrue(self.bus.closed)
        self.assertNotIn('PRIVATE', ''.join(self.output))

    def test_failures_are_single_attempt_and_do_not_raise_into_viewer_supervisor(self):
        for mode in ('submit_failure', 'failed', 'transport', 'timeout', 'wrong_uuid', 'cancel'):
            with self.subTest(mode=mode):
                self.mode = mode
                self.calls.clear(); self.actions.clear(); self.output.clear(); self.cancelled = False
                self.experiment.attempted = False
                self.run_experiment()
                self.assertEqual(self.calls.count('SubmitSdlPlacement'), 1)
                if mode not in ('submit_failure', 'failed'): self.assertIn('CancelSdlPlacement', self.calls)
                if mode in ('wrong_uuid', 'submit_failure'): self.assertEqual(self.actions, [])
                self.assertFalse(self.experiment.placement_ok)
                self.assertTrue(self.bus.closed)
                self.assertEqual(self.rows()[-1]['supervision'], 'continuing_under_original_launcher')
                self.assertNotIn('PRIVATE', ''.join(self.output))

    def test_cancellation_before_submission_creates_no_placement_request(self):
        self.cancelled = True
        self.run_experiment()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.actions, [])
        self.assertTrue(self.bus.closed)

    def test_missing_snapshot_is_explicit_and_does_not_change_broker_result(self):
        self.mode = 'snapshot_failure'
        self.run_experiment()
        final = self.rows()[-1]
        self.assertEqual(final['placement']['placement'], 'succeeded')
        self.assertEqual(final['observed']['status'], 'unavailable')
        self.assertTrue(self.experiment.placement_ok)

    def test_duplicate_registration_never_retries_placement(self):
        self.run_experiment()
        with self.assertRaises(RuntimeError): self.run_experiment()
        self.assertEqual(self.calls.count('SubmitSdlPlacement'), 1)

    def test_cli_delegates_to_original_launcher_with_same_destination_and_call_bound(self):
        from contextlib import redirect_stdout
        fake_dbus = SimpleNamespace(bus=SimpleNamespace(BusConnection=lambda address: self.bus),
                                    Interface=lambda obj, iface: obj)
        delegated = []
        def launch(argv, *, emit, on_registered):
            delegated.extend(argv)
            on_registered(self.registration, lambda: False)
            emit(json.dumps(dict(child_exit=2, placement='not_requested')))
            return 0
        with patch.dict('sys.modules', dbus=fake_dbus), \
             patch.object(self.m, 'Experiment', return_value=self.experiment), \
             patch.object(self.m.launcher, 'main', launch), redirect_stdout(io.StringIO()):
            self.assertEqual(self.m.main(['--confirm-immediate-placement', 'example.invalid', 'testuser',
                                         '--rdp-registration-timeout-ms', '120000']), 0)
        self.assertEqual(delegated, ['example.invalid', 'testuser', '--rdp-registration-timeout-ms', '120000',
                                    '--desktop', '1', '--slot', '1', '--call-timeout-ms', '3000'])
        self.assertEqual(self.rows()[-1]['launcher']['placement'], 'not_requested')
        self.assertEqual(self.rows()[-2]['placement']['placement'], 'succeeded')

    def test_cli_requires_prelaunch_confirmation(self):
        with self.assertRaises(SystemExit) as caught:
            self.m.main(['example.invalid', 'testuser'])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(self.calls, [])

    def test_observer_failure_does_not_bypass_tool_cleanup_or_authorization(self):
        def observer(*args): raise ValueError('PRIVATE callback')
        code = self.real_release(self.bus, lambda obj, iface: obj, 'win-001', 1, 1, self.m.DEFAULT_GEOMETRY,
            confirmed=True, timeout_ms=1000, poll_ms=100, call_timeout_ms=1000,
            sleep=lambda seconds: None, clock=lambda: self.now, emit=lambda line: None, observe=observer)
        self.assertEqual(code, 0)
        self.assertTrue(self.bus.closed)

    def test_real_foreground_launcher_keeps_child_alive_through_placement_then_reaps(self):
        self.integrate_launcher('success')

    def test_placement_failure_preserves_foreground_child_until_its_normal_exit(self):
        self.integrate_launcher('failed')

    def test_cancel_during_placement_uses_original_launcher_owned_child_cleanup(self):
        self.integrate_launcher('cancel')

    def test_registration_failure_never_invokes_placement_and_owned_child_is_reaped(self):
        from test_rdp_development_launcher import LauncherTests
        fixture = LauncherTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.mode = 'competing'
        status = fixture.client.launch(fixture.transport.bus, lambda obj, iface: obj,
                lambda fd: fixture.f.FD(os.dup(fd)), fixture.f.adapter, 'example.invalid', 3389,
                'testuser', 1, 1, {}, emit=fixture.output.append, spawn=fixture.spawn,
                sleep=fixture.wait, clock=lambda: fixture.f.clock,
                on_registered=self.experiment.registered)
        self.assertEqual(status, 1)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.experiment.attempted)
        self.assertIsNotNone(fixture.child.poll())

    def integrate_launcher(self, mode):
        from test_rdp_development_launcher import LauncherTests
        fixture = LauncherTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.mode = 'stay'  # Original fixture keeps child alive until first supervision wait.
        self.mode = mode
        self.experiment.clock = lambda: fixture.f.clock
        def release(*args, **kwargs):
            self.assertIsNone(fixture.child.poll())
            self.assertFalse(any(json.loads(line).get('state') == 'registered' for line in fixture.output))
            self.assertTrue(fixture.transport.bus.get_is_connected())
            code = self.real_release(*args, **kwargs, sleep=lambda seconds: None)
            self.assertIsNone(fixture.child.poll())
            return code
        self.experiment.release = release
        def cancelled(): return self.cancelled
        arguments = dict(emit=fixture.output.append, spawn=fixture.spawn, sleep=fixture.wait,
                         clock=lambda: fixture.f.clock, cancelled=cancelled,
                         on_registered=self.experiment.registered)
        if mode == 'cancel':
            # Do not let the normal-exit fixture close the child: exercise
            # the foreground launcher's actual pidfd TERM/reap cleanup.
            arguments['sleep'] = lambda seconds: setattr(fixture.f, 'clock', fixture.f.clock + seconds)
            with self.assertRaisesRegex(RuntimeError, 'Operator cancellation'):
                fixture.client.launch(fixture.transport.bus, lambda obj, iface: obj,
                    lambda fd: fixture.f.FD(os.dup(fd)), fixture.f.adapter, 'example.invalid', 3389,
                    'testuser', 1, 1, {}, **arguments)
        else:
            self.assertEqual(fixture.client.launch(fixture.transport.bus, lambda obj, iface: obj,
                lambda fd: fixture.f.FD(os.dup(fd)), fixture.f.adapter, 'example.invalid', 3389,
                'testuser', 1, 1, {}, **arguments), 0)
        self.assertIsNotNone(fixture.child.poll())
        self.assertEqual(fixture.events[:2], ['begin', 'spawn'])
        self.assertEqual(self.calls.count('SubmitSdlPlacement'), 1)
        registered = next(json.loads(line) for line in fixture.output if json.loads(line).get('state') == 'registered')
        self.assertEqual(self.rows()[0]['window_uuid'], registered['window_uuid'])


class TraceTests(unittest.TestCase):
    def setUp(self):
        self.m = module()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'private.log'
        self.path.touch(mode=0o600)
        self.trace = self.m.BrokerTrace(str(self.path), 4096)
        self.addCleanup(self.trace.close)

    def append(self, **fields):
        row = dict(request_id='a' * 32, window_uuid=WINDOW_ID, receipt_elapsed_ms=5)
        row.update(fields)
        with self.path.open('ab') as stream:
            stream.write(b'joetoo-kwind: SDL placement diagnostic ' + json.dumps(row).encode() + b'\n')

    def test_request_specific_receipt_evidence_is_not_physical_execution_time(self):
        self.append(stage='resident_assignment_attempt', caption='PRIVATE')
        self.append(stage='terminal_begin', requested_outcome='succeeded', geometry_match=True, desktop_match=True)
        self.append(stage='terminal', outcome='succeeded')
        self.append(stage='terminal', outcome='failed', request_id='b' * 32)
        result = self.trace.read('a' * 32, WINDOW_ID)
        self.assertEqual(result['assignment']['broker_elapsed_ms'], 5)
        self.assertEqual(result['geometry_verification']['broker_elapsed_ms'], 5)
        self.assertEqual(result['terminal']['outcome'], 'succeeded')
        self.assertEqual(result['missing'], [])
        self.assertIn('not physical execution', result['time_basis'])
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_failed_geometry_missing_rows_and_partial_line_are_not_success_evidence(self):
        self.append(stage='terminal_begin', requested_outcome='failed', geometry_match=False, desktop_match=True)
        with self.path.open('ab') as stream: stream.write(b'joetoo-kwind: SDL placement diagnostic {')
        result = self.trace.read('a' * 32, WINDOW_ID)
        self.assertEqual(result['missing'], ['assignment', 'geometry_verification', 'terminal'])

    def test_bounds_rotation_truncation_and_unsafe_permissions(self):
        with self.path.open('ab') as stream: stream.write(b'x' * 4097)
        self.assertEqual(self.trace.read('a' * 32, WINDOW_ID)['status'], 'partial')
        self.path.chmod(0o644)
        self.assertEqual(self.trace.read('a' * 32, WINDOW_ID)['status'], 'unavailable')
        with self.assertRaises(RuntimeError): self.m.BrokerTrace(str(self.path), 4096)
        self.path.chmod(0o600)
        self.path.rename(self.path.with_suffix('.old'))
        self.path.touch(mode=0o600)
        self.assertEqual(self.trace.read('a' * 32, WINDOW_ID)['status'], 'unavailable')

    def test_no_trace_for_unknown_request_and_no_reuse_of_preexperiment_rows(self):
        self.append(stage='terminal', outcome='succeeded')
        later = self.m.BrokerTrace(str(self.path), 4096)
        try:
            self.assertEqual(later.read('a' * 32, WINDOW_ID)['missing'], ['assignment', 'geometry_verification', 'terminal'])
            self.assertEqual(later.read(None, WINDOW_ID)['reason'], 'placement_request_id_unavailable')
        finally: later.close()


if __name__ == '__main__':
    unittest.main()
