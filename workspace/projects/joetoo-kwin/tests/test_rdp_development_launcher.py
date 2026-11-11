# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent launcher with real broker/pidfds and disposable Python children.

No live D-Bus, SDL executable, GUI or network. Only the executable seam and
transport are substituted; the actual broker/registry/FD checks run unchanged.
"""
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

class LauncherTests(unittest.TestCase):
    def setUp(self):
        from test_rdp_launch import SmokeClientTests
        self.transport = SmokeClientTests()
        self.transport.setUp()
        self.addCleanup(self.transport.doCleanups)
        self.f = self.transport.fixture
        self.bridge = self.transport.bridge
        spec = importlib.util.spec_from_file_location('sdl_launcher_test',
            Path(__file__).resolve().parents[1] / 'tools/joetoo-sdl-registration-launch.py')
        self.client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.client)
        self.transport.bus.get_is_connected = self.f.bus.get_is_connected
        self.events, self.output, self.children = [], [], []
        self.mode = 'positive'
        self.poll_count = 0
        self.cancelled = False
        self.folder = tempfile.TemporaryDirectory(prefix='sdl-launcher-test-')
        self.addCleanup(self.folder.cleanup)
        original_mkdtemp = tempfile.mkdtemp
        self.patch(self.client.tempfile, 'mkdtemp', lambda **kw: original_mkdtemp(dir=self.folder.name, **kw))
        original_begin = self.bridge.BeginSdlRegistration
        def begin(payload, **kw):
            self.events.append('begin')
            reply = original_begin(payload, **kw)
            result = json.loads(reply)
            self.f.rid, self.f.marker = result['request_id'], result['title_marker']
            return reply
        self.patch(self.bridge, 'BeginSdlRegistration', begin)
        def bind(rid, pid, fd, **kw):
            self.events.append('bind')
            self.f.assert_client_connected()
            self.assertEqual(pid, self.child.pid)
            self.assertEqual(os.stat('/proc/%d/fd/1' % pid).st_ino, os.fstat(fd.fd).st_ino)
            self.assertEqual(os.fstat(fd.fd).st_mode & 0o777, 0o600)
            self.assertEqual(self.f.adapter._proc_info(pid)['parent'], os.getpid())
            # Real bus duplicates UnixFd instead of consuming sender's wrapper.
            duplicate = self.f.FD(os.dup(fd.fd))
            if self.mode == 'substituted_fd':
                os.close(duplicate.take())
                duplicate = self.f.FD(os.dup(self.f.log.fileno()))
            result = self.f.b.BindSdlRegistration(rid, pid + 1 if self.mode == 'forged_pid' else pid,
                                                duplicate, sender=self.f.sender)
            if self.mode == 'bind_lost':
                raise RuntimeError('Bind reply lost')
            return result
        self.patch(self.bridge, 'BindSdlRegistration', bind)
        def poll(rid, **kw):
            self.events.append('poll')
            self.f.assert_client_connected()
            self.poll_count += 1
            if self.mode == 'caller_loss':
                self.f.bus.connected = False
                self.f.bus.lost()
                raise RuntimeError('Disconnected transport')
            if self.mode == 'unknown':
                return self.f.b.PollSdlRegistration('unknown', sender=self.f.sender)
            if self.mode == 'wrong_reply':
                return json.dumps(dict(protocol=1, request_id='other', state='registered'))
            if self.mode in ('positive', 'competing', 'stay') and (
                    not self.f.b._rdp_registration.get('profile') or self.poll_count == 1):
                self.f.child = self.child
                self.f.event()
                if self.mode == 'competing':
                    from test_step1_3a import observation
                    window = json.loads(observation())['window']
                    window.update(uuid='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
                                  pid=self.child.pid, resource_class=self.f.adapter.APPLICATION,
                                  caption=self.f.marker)
                    self.f.revision += 1
                    self.f.b.ObserveWindow(json.dumps(dict(source='source', revision=self.f.revision,
                                                          event='added', window=window)))
                self.f.child = None  # Launcher, not fixture, owns wait/cleanup.
            result = self.f.b.PollSdlRegistration(rid, sender=self.f.sender)
            if json.loads(result)['state'] == 'registered' and self.mode != 'stay':
                self.child.stdin.close()
                self.child.wait(timeout=3)
            return result
        self.patch(self.bridge, 'PollSdlRegistration', poll)
        original_cancel = self.bridge.CancelSdlRegistration
        def cancel(rid, **kw):
            self.events.append('cancel')
            self.f.assert_client_connected()
            return original_cancel(rid, **kw)
        self.patch(self.bridge, 'CancelSdlRegistration', cancel)
        self.addCleanup(self.assert_cleanup)

    def patch(self, obj, name, replacement):
        p = patch.object(obj, name, replacement)
        p.start()
        self.addCleanup(p.stop)

    def assert_cleanup(self):
        for child in self.children:
            self.assertIsNotNone(child.poll(), 'Launcher left a running disposable child')
            if child.stdin and not child.stdin.closed: child.stdin.close()
            if child.stderr: child.stderr.close()
        self.assertFalse(self.f.bus.get_is_connected() and not self.f.bus.lost_senders)
        self.assertIsNone(self.f.b.registry._active_request_id)
        self.assertIsNone(self.f.b.request)

    def spawn(self, argv, **kwargs):
        self.events.append('spawn')
        self.assertEqual(self.events[:2], ['begin', 'spawn'])
        self.assertEqual(argv[0], '/usr/bin/sdl-freerdp')
        self.assertIn('/t:' + self.f.marker, argv)
        self.assertEqual([a for a in argv if a.startswith('/sec:')], ['/sec:nla'])
        self.assertEqual([a for a in argv if a.startswith('/cert:')], ['/cert:deny'])
        self.assertTrue(kwargs['close_fds'])
        self.assertEqual(kwargs['env']['SDL_VIDEO_DRIVER'],
                         'x11' if self.f.b._rdp_registration.get('profile') else 'wayland')
        self.assertEqual(kwargs['stderr'], subprocess.STDOUT)
        if self.mode == 'spawn_failure': raise OSError('simulated exec failure')
        code = ('import os,sys; print("[0] [%d:thread] [DEBUG][com.freerdp.client.SDL] - '
                '[main]: client is using backend \'%s\'" % (os.getpid(),sys.argv[1]),flush=sys.argv[2] == "flush"); '
                'print("ready",file=sys.stderr,flush=True); sys.stdin.read()')
        if self.mode == 'certificate_refusal':
            code += '; print("simulated certificate refusal",flush=True); sys.exit(1)'
        self.child = subprocess.Popen([sys.executable, '-c', code,
            'x11' if self.mode == 'x11' else kwargs['env']['SDL_VIDEO_DRIVER'],
            'buffer' if self.mode == 'buffered' else 'flush'], stdin=subprocess.PIPE,
            stdout=kwargs['stdout'], stderr=subprocess.PIPE, env=kwargs['env'], close_fds=True)
        self.children.append(self.child)
        self.assertTrue(select.select([self.child.stderr], [], [], 3)[0])
        self.assertEqual(self.child.stderr.readline(), b'ready\n')
        if self.mode == 'exit':
            self.child.stdin.close()
            self.child.wait(timeout=3)
        return self.child

    def wait(self, duration):
        self.assertEqual(duration, .1)
        self.f.clock += duration
        if self.mode == 'stay':
            self.transport.owner = ':1.replacement'
            self.child.stdin.close()
            self.child.wait(timeout=3)
        if self.mode == 'cancel': self.cancelled = True
        if self.mode in ('deadline', 'buffered'): self.f.clock += 130
        if self.mode == 'owner_change': self.transport.owner = ':1.replaced'
        if self.mode == 'budget':
            path = next(Path(self.folder.name).glob('*/stdout.log'))
            with path.open('ab') as stream: stream.write(b'x' * 65537)

    def run_launcher(self, profile=None, bounds=None, **options):
        # close() models disconnect; no further external calls are possible.
        original_close = self.transport.bus.close
        def close():
            original_close()
            self.f.bus.connected = False
        self.transport.bus.close = close
        return self.client.launch(self.transport.bus, lambda obj, iface: obj,
            lambda fd: self.f.FD(os.dup(fd)), self.f.adapter, 'example.invalid', 3389,
            'testuser', 3, 1, bounds or {}, emit=self.output.append, spawn=self.spawn,
            sleep=self.wait, clock=lambda: self.f.clock, cancelled=lambda: self.cancelled, profile=profile, **options)

    def test_pending_timeout_proves_broker_terminal_and_real_child_reaped(self):
        self.mode = 'deadline'
        receipts = []
        with self.assertRaisesRegex(RuntimeError, 'deadline expired'):
            self.run_launcher(bounds={'rdp_registration_timeout_ms': 1000}, on_cleanup=receipts.append)
        receipt, = receipts
        self.assertTrue(receipt['eligible'])
        self.assertTrue(receipt['broker_terminal'])
        self.assertTrue(receipt['child_reaped'])
        self.assertTrue(receipt['resources_released'])
        self.assertEqual(receipt['terminal']['request_id'], self.f.rid)
        self.assertIsNotNone(self.child.returncode)
        self.assertFalse(self.f.b.registry.managed_windows)

    def test_verified_natural_exit_and_terminal_broker_result_can_be_clean(self):
        self.mode='deadline';receipts=[]
        def exited(duration):
            self.child.stdin.close();self.child.wait(timeout=3)
            self.f.loop.tick()  # Broker independently observes its bound child's exit.
        self.wait=exited
        with self.assertRaisesRegex(RuntimeError,'Child exited before registration'):
            self.run_launcher(on_cleanup=receipts.append)
        self.assertTrue(receipts[0]['eligible'])
        self.assertTrue(receipts[0]['natural_exit'])
        self.assertEqual(receipts[0]['terminal']['reason'],'child_identity_rejected')

    def test_simulated_strict_refusal_reaps_real_pending_child(self):
        # The child is Python, not FreeRDP: assert argv and actual cleanup only.
        self.mode = 'certificate_refusal'
        receipts = []
        def refused(duration):
            self.child.stdin.close()
            self.child.wait(timeout=3)
            self.f.loop.tick()
        self.wait = refused
        with self.assertRaisesRegex(RuntimeError, 'Child exited before registration'):
            self.run_launcher(on_cleanup=receipts.append)
        self.assertEqual(self.child.returncode, 1)
        self.assertTrue(receipts[0]['eligible'])
        self.assertTrue(receipts[0]['child_reaped'])
        self.assertEqual(json.loads(self.f.b.ListManaged())['count'], 0)

    def test_unknown_cancel_reply_retains_real_owned_child_without_clean_claim(self):
        self.mode = 'deadline'
        receipts = []
        self.patch(self.bridge, 'CancelSdlRegistration', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('lost reply')))
        def retained(value):
            receipts.append((value, self.child.poll()))
            self.child.stdin.close(); self.child.wait(timeout=3)
        with self.assertRaisesRegex(RuntimeError, 'deadline expired'):
            self.run_launcher(bounds={'rdp_registration_timeout_ms': 1000}, on_cleanup=retained)
        self.assertEqual(len(receipts), 1)
        self.assertIsNone(receipts[0][1])
        self.assertTrue(receipts[0][0]['retained'])
        self.assertFalse(receipts[0][0]['eligible'])

    def test_source_change_prevents_clean_receipt_even_after_reaping(self):
        self.mode='deadline'
        self.wait=lambda duration:(setattr(self.f,'clock',self.f.clock+2),setattr(self.f.b,'observation_source','replaced'))
        receipts=[]
        with self.assertRaisesRegex(RuntimeError,'deadline expired'):
            self.run_launcher(bounds={'rdp_registration_timeout_ms':1000},on_cleanup=receipts.append)
        self.assertFalse(receipts[0]['eligible'])
        self.assertTrue(receipts[0]['child_reaped'])

    def test_failed_reaping_cannot_be_reported_clean(self):
        self.mode='deadline';receipts=[]
        def cleanup(value):
            receipts.append(value)
            self.child.stdin.close();self.child.wait(timeout=3)
        with patch.object(self.client._runtime,'stop_child',side_effect=RuntimeError('unreaped')):
            with self.assertRaisesRegex(RuntimeError,'deadline expired'):
                self.run_launcher(bounds={'rdp_registration_timeout_ms':1000},on_cleanup=cleanup)
        self.assertFalse(receipts[0]['eligible'])
        self.assertFalse(receipts[0]['child_reaped'])

    def test_cancel_racing_broker_registration_preserves_exact_real_child(self):
        self.mode='stay';snapshots=[]
        previous=self.bridge.PollSdlRegistration
        def lost(*args,**kwargs):
            previous(*args,**kwargs)
            raise RuntimeError('simulated lost positive reply')
        self.patch(self.bridge,'PollSdlRegistration',lost)
        def retain(value):
            snapshots.append((value,self.child.poll()))
            self.child.stdin.close();self.child.wait(timeout=3)
        with self.assertRaisesRegex(RuntimeError,'lost positive reply'):
            self.run_launcher(on_cleanup=retain)
        self.assertEqual(len(snapshots),1)
        self.assertIsNone(snapshots[0][1])
        self.assertEqual(snapshots[0][0]['registration']['state'],'registered')
        self.assertFalse(snapshots[0][0]['eligible'])
        self.assertEqual(len(self.f.b.registry.managed_windows),1)

    def registered_failure(self, failure, cancel=False):
        # Actual disposable child plus the real broker/registry identity path.
        self.mode = 'stay'
        seen = []
        snapshots = []
        original_output = self.output
        outer = self
        class Reports(list):
            def append(self, line):
                value = json.loads(line)
                if failure == 'reporting' and value.get('state') == 'registered':
                    raise OSError('simulated private reporting failure')
                original_output.append(line)
                if value.get('supervision') == 'degraded' and not seen:
                    seen.append(value)
                    record = outer.f.b.registry.get_window(value['managed_id'])
                    # Assert outside the production reporting callback, whose
                    # deliberate error isolation must not swallow test failures.
                    snapshots.append((outer.child.poll(), outer.f.bus.get_is_connected(),
                        record.window_uuid, record.presence, record.placement))
                    if cancel:
                        outer.cancelled = True
                    else:
                        # Only this test's deliberate closure ends the real child.
                        outer.child.stdin.close()
                        outer.child.wait(timeout=3)
        self.output = Reports()
        def wait(duration):
            self.f.clock += duration
            path = next(Path(self.folder.name).glob('*/stdout.log'))
            if failure == 'budget':
                with path.open('ab') as stream: stream.write(b'x' * 65537)
            elif failure == 'integrity':
                path.chmod(0o640)
            elif failure == 'wait':
                raise OSError('simulated private wait failure')
        self.wait = wait
        with patch.object(self.client._runtime, 'stop_child', wraps=self.client._runtime.stop_child) as stop:
            if cancel:
                with self.assertRaisesRegex(RuntimeError, 'Operator cancellation'):
                    self.run_launcher()
                self.assertEqual(stop.call_count, 1)
            else:
                self.assertEqual(self.run_launcher(), 1)
                stop.assert_not_called()
        self.assertEqual(len(seen), 1)
        self.assertEqual(snapshots, [(None, True, seen[0]['window_uuid'], 'present', 'not_requested')])
        self.assertEqual(seen[0]['state'], 'unresolved')
        self.assertEqual(seen[0]['registration'], 'registered')
        self.assertEqual(seen[0]['remote_session'], 'unverified')
        self.assertNotIn('simulated private', json.dumps(original_output))
        self.assertNotIn('cancel', self.events)  # Enrollment is never cancelled/replaced.
        return seen[0]

    def test_registered_real_child_survives_log_budget_failure_until_own_exit(self):
        self.assertEqual(self.registered_failure('budget')['reason'], 'private_log_integrity_or_budget')

    def test_registered_real_child_survives_log_integrity_failure(self):
        self.assertEqual(self.registered_failure('integrity')['reason'], 'private_log_integrity_or_budget')

    def test_registered_real_child_survives_reporting_failure(self):
        self.assertEqual(self.registered_failure('reporting')['reason'], 'registration_notification')

    def test_registered_real_child_survives_supervision_wait_failure(self):
        self.assertEqual(self.registered_failure('wait')['reason'], 'supervision_wait')

    def test_explicit_owned_cancellation_still_stops_degraded_registered_child(self):
        self.registered_failure('budget', cancel=True)

    def test_explicit_x11_auto_full_launcher_public_broker_and_real_child(self):
        with patch.dict(os.environ, XDG_SESSION_TYPE='tty', SDL_RENDER_DRIVER='opengl',
                        SDL_FRAMEBUFFER_ACCELERATION='1'):
            parent = dict(os.environ)
            self.assertEqual(self.run_launcher(profile=self.f.adapter.X11_PROFILE), 0)
            self.assertEqual(dict(os.environ), parent)
        result = next(json.loads(s) for s in self.output if json.loads(s).get('state') == 'registered')
        self.assertEqual(result['profile'], self.f.adapter.X11_PROFILE)
        self.assertEqual(result['bounds']['rdp_x11_renderer'], 'auto')
        self.assertGreaterEqual(self.poll_count, 5)
        self.assertEqual(result['placement'], 'not_requested')

    def test_explicit_x11_software_full_launcher_public_broker_and_real_child(self):
        with patch.dict(os.environ):
            os.environ.pop('XDG_SESSION_TYPE', None)
            self.assertEqual(self.run_launcher(profile=self.f.adapter.X11_PROFILE,
                bounds={'rdp_x11_renderer': 'software', 'rdp_x11_identity_settle_ms': 250}), 0)
        result = next(json.loads(s) for s in self.output if json.loads(s).get('state') == 'registered')
        self.assertEqual(result['bounds']['rdp_x11_renderer'], 'software')
        self.assertEqual(result['bounds']['rdp_x11_identity_settle_ms'], 250)

    def test_x11_forged_pid_and_substituted_fd_remain_rejected(self):
        self.mode = 'substituted_fd'
        with patch.dict(os.environ, XDG_SESSION_TYPE='x11'):
            self.assertEqual(self.run_launcher(profile=self.f.adapter.X11_PROFILE), 1)
        self.assertFalse(self.f.b.registry.managed_windows)

    def retained_placement(self, state):
        # A real RegistryStatus snapshot, with a non-null historical ID. Do not
        # clear the history while the launcher runs or fake it into active work.
        from contextlib import ExitStack
        stack = ExitStack()
        self.addCleanup(stack.close)
        history = dict(id='previous-placement', kind='move', state=state, detail='completed')
        stack.enter_context(patch.object(self.f.b, 'request', history))
        stack.enter_context(patch.object(self.f.b, '_sync_managed_placement',
            self.f.b.__class__._sync_managed_placement.__get__(self.f.b)))
        self.statuses = []
        original = self.bridge.RegistryStatus
        def status(**kwargs):
            result = original(**kwargs)
            self.statuses.append(json.loads(result))
            return result
        stack.enter_context(patch.object(self.bridge, 'RegistryStatus', status))
        return history

    def test_retained_ok_permits_x11_auto_preflight_and_pending_monitor(self):
        history = self.retained_placement('OK')
        self.assertEqual(self.run_launcher(profile=self.f.adapter.X11_PROFILE), 0)
        self.assertIs(self.f.b.request, history)
        self.assertGreater(len(self.statuses), 2)
        self.assertTrue(all(s['placement_transaction'] == dict(id=history['id'], state='OK') for s in self.statuses))
        self.f.b.request = None  # Fixture disposal, after proving history retained.

    def test_retained_error_permits_x11_software_preflight_and_pending_monitor(self):
        history = self.retained_placement('ERROR')
        self.assertEqual(self.run_launcher(profile=self.f.adapter.X11_PROFILE,
            bounds={'rdp_x11_renderer': 'software'}), 0)
        self.assertIs(self.f.b.request, history)
        self.assertGreater(len(self.statuses), 2)
        self.assertTrue(all(s['placement_transaction'] == dict(id=history['id'], state='ERROR') for s in self.statuses))
        self.f.b.request = None

    def test_active_or_unknown_placement_refuses_before_begin_and_spawn(self):
        # Each failing preflight closes only this synthetic caller connection;
        # reconnect for the next independent negative vector, without a restart.
        for state in ('PENDING', 'RUNNING', 'VERIFYING', 'UNKNOWN'):
            with self.subTest(state=state):
                self.f.bus.connected = True
                self.f.bus.lost_senders.clear()
                self.f.b.request = dict(id='historical-id-is-not-a-busy-test', state=state)
                try:
                    with self.assertRaisesRegex(RuntimeError, 'Broker is busy'): self.run_launcher()
                    self.assertEqual(self.events, [])
                finally: self.f.b.request = None

    def test_pending_monitor_rejects_active_layout_or_uncertain_cleanup(self):
        original = self.bridge.RegistryStatus
        calls = 0
        def status(**kwargs):
            nonlocal calls
            calls += 1
            result = json.loads(original(**kwargs))
            if calls > 1: result['viewer_cleanup_uncertain'] = True
            return json.dumps(result)
        self.patch(self.bridge, 'RegistryStatus', status)
        with self.assertRaisesRegex(RuntimeError, 'Placement became active'):
            self.run_launcher(profile=self.f.adapter.X11_PROFILE)
        self.assertEqual(self.events[:4], ['begin', 'spawn', 'bind', 'poll'])
        self.assertIn('cancel', self.events)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_terminal_error_with_uncertain_sdl_cleanup_is_rejected_by_begin(self):
        self.retained_placement('ERROR')
        self.f.b._sdl_placement = dict(terminal=dict(placement='failed'), cleanup_uncertain=True)
        try:
            self.assertFalse(json.loads(self.bridge.RegistryStatus())['viewer_cleanup_uncertain'])
            with self.assertRaises(Exception): self.run_launcher()
            self.assertEqual(self.events, ['begin'])
            self.assertIsNone(self.f.b._rdp_registration)
            self.assertEqual(self.children, [])
        finally:
            self.f.b.request = None
            self.f.b._sdl_placement = None

    def test_unsynchronized_observation_and_active_initial_layout_refuse_before_spawn(self):
        original = self.bridge.RegistryStatus
        for field in ('observation', 'initial_layout_active'):
            with self.subTest(field=field):
                self.f.bus.connected = True; self.f.bus.lost_senders.clear()
                def status(**kwargs):
                    result = json.loads(original(**kwargs))
                    if field == 'observation': result[field]['synchronized'] = False
                    else: result[field] = True
                    return json.dumps(result)
                with patch.object(self.bridge, 'RegistryStatus', status):
                    with self.assertRaises(RuntimeError): self.run_launcher()
                self.assertEqual(self.events, [])

    def test_begin_dbus_error_reports_safe_name_and_operation_before_spawn(self):
        class Rejected(Exception):
            def get_dbus_name(self): return 'org.joetoo.KWinBridge.InvalidRequest'
        def reject(*args, **kwargs): raise Rejected('private environment or credential text')
        self.patch(self.bridge, 'BeginSdlRegistration', reject)
        with self.assertRaisesRegex(RuntimeError, 'BeginSdlRegistration failed: org.joetoo.KWinBridge.InvalidRequest') as caught:
            self.run_launcher()
        self.assertNotIn('private', str(caught.exception))
        self.assertEqual(self.children, [])

    def test_dbus_error_identifiers_are_allowlisted(self):
        class RemoteError(Exception):
            def __init__(self, name): self.name = name
            def get_dbus_name(self): return self.name
        for name in ('org.freedesktop.DBus.Error.AccessDenied', 'org.freedesktop.DBus.Error.NotSupported'):
            self.assertEqual(self.client.dbus_error_name(RemoteError(name)), name)
        for name in ('private.arbitrary.contents', '', None):
            self.assertIsNone(self.client.dbus_error_name(RemoteError(name)))
        self.transport.bus.close(); self.f.bus.connected = False

    def test_positive_real_broker_child_fd_uuid_and_no_placement(self):
        self.assertEqual(self.run_launcher(), 0)
        results = [json.loads(line) for line in self.output]
        registered = next(r for r in results if r.get('state') == 'registered')
        self.assertEqual(registered['placement'], 'not_requested')
        record = self.f.b.registry.managed_windows[registered['window_uuid']]
        self.assertEqual(record.observation['pid'], self.child.pid)
        self.assertEqual(record.placement, 'not_requested')
        self.assertNotIn('cancel', self.events)
        self.assertEqual(self.events[:4], ['begin', 'spawn', 'bind', 'poll'])
        self.assertTrue(Path(results[0]['evidence_directory'], 'stdout.log').is_file())

    def test_contradictory_backend_fails_bind_and_reaps(self):
        self.mode = 'x11'
        self.assertEqual(self.run_launcher(), 1)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_forged_pid_and_substituted_descriptor_fail_closed(self):
        self.mode = 'forged_pid'
        self.assertEqual(self.run_launcher(), 1)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_substituted_fd_fails_closed(self):
        self.mode = 'substituted_fd'
        self.assertEqual(self.run_launcher(), 1)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_competing_uuid_is_not_selected(self):
        self.mode = 'competing'
        self.assertEqual(self.run_launcher(), 1)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_child_environment_drops_logging_overrides_without_changing_parent(self):
        parent = dict(WLOG_APPENDER='UDP', WLOG_PREFIX='custom', WLOG_FILTER='*:OFF',
                      WLOG_LEVEL='OFF', SDL_VIDEODRIVER='x11', KEEP='yes')
        child = self.f.adapter.development_environment(parent)
        self.assertEqual(child, dict(WLOG_APPENDER='CONSOLE', SDL_VIDEO_DRIVER='wayland', KEEP='yes'))
        self.assertEqual(parent['WLOG_APPENDER'], 'UDP')
        self.transport.bus.close()
        self.f.bus.connected = False

    def test_pidfd_allocation_failure_cancels_and_reaps_without_binding(self):
        original = os.pidfd_open
        def unavailable_for_child(pid, *args):
            if pid != os.getpid(): raise OSError('simulated pidfd resource exhaustion')
            return original(pid, *args)
        with patch.object(os, 'pidfd_open', unavailable_for_child):
            with self.assertRaises(OSError): self.run_launcher()
        self.assertNotIn('bind', self.events)
        self.assertEqual(self.f.b.registry.managed_windows, {})

    def test_broker_change_after_success_does_not_close_viewer(self):
        self.mode = 'stay'
        self.assertEqual(self.run_launcher(), 0)
        self.assertEqual(self.transport.owner, ':1.replacement')
        self.assertNotIn('cancel', self.events)

    def test_busy_reservation_refuses_before_spawn(self):
        self.f.begin()
        original_id = self.f.rid
        with self.assertRaises(RuntimeError): self.run_launcher()
        self.assertNotIn('spawn', self.events)
        # Closing the same test caller cleans its existing pending intent;
        # a real competing caller would have a distinct authenticated name.
        self.assertEqual(self.f.b._sdl_response(original_id)['reason'], 'caller_lost')

    def test_invalid_endpoint_refused_before_begin_or_spawn(self):
        with self.assertRaises(ValueError):
            self.client.launch(self.transport.bus, lambda o, i: o, None, self.f.adapter,
                               '/bad', 3389, 'testuser', 3, 1, {}, emit=self.output.append)
        self.f.bus.connected = False
        self.assertEqual(self.events, [])

    def test_pending_unknown_id_cannot_cancel_other_intent(self):
        self.mode = 'unknown'
        with self.assertRaises(Exception): self.run_launcher()
        self.assertIn('cancel', self.events)
        self.assertEqual(self.f.b._sdl_response(self.f.rid)['reason'], 'cancelled')


def negative_case(mode):
    def test(self):
        self.mode = mode
        with self.assertRaises(Exception):
            self.run_launcher()
        self.assertEqual(self.f.b.registry.managed_windows, {})
    return test


for _mode in ('cancel', 'deadline', 'owner_change', 'bind_lost', 'wrong_reply',
              'unknown', 'caller_loss', 'spawn_failure', 'budget', 'exit', 'buffered'):
    setattr(LauncherTests, 'test_negative_' + _mode, negative_case(_mode))


def pending_placement_case(state):
    def test(self):
        original = self.bridge.RegistryStatus
        calls = 0
        def status(**kwargs):
            nonlocal calls
            calls += 1
            result = json.loads(original(**kwargs))
            if calls > 1:
                if state == 'layout': result['initial_layout_active'] = True
                else: result['placement_transaction'] = dict(id='active', state=state)
            return json.dumps(result)
        self.patch(self.bridge, 'RegistryStatus', status)
        with self.assertRaisesRegex(RuntimeError, 'Placement became active'):
            self.run_launcher(profile=self.f.adapter.X11_PROFILE)
        self.assertIn('cancel', self.events)
        self.assertEqual(self.f.b.registry.managed_windows, {})
    return test


for _state in ('PENDING', 'RUNNING', 'VERIFYING', 'layout'):
    setattr(LauncherTests, 'test_pending_guard_rejects_' + _state, pending_placement_case(_state))


if __name__ == '__main__':
    unittest.main()
