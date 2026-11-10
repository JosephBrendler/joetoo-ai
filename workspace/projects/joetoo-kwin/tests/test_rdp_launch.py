#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline SDL adapter tests; no SDL, display, services or remote connection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID
from test_rdp_broker import Loop

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'libexec'))
import joetoo_kwin_rdp_launch as adapter


def backend_line(pid=42, backend='wayland'):
    return (f"[17:09:58:939] [{pid}:0024a8f1] [DEBUG][com.freerdp.client.SDL] - "
            f"[main]: client is using backend '{backend}'\n").encode()


class LaunchAdapterTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='step1.5c5d-rdp-test-')
        self.addCleanup(self.folder.cleanup)
        self.log = open(Path(self.folder.name) / 'private.log', 'w+b')
        os.fchmod(self.log.fileno(), 0o600)
        self.addCleanup(self.log.close)
        self.process = SimpleNamespace(pid=42)
        self.reader = adapter.BackendEvidence(self.process, self.log, {})
        self.addCleanup(self.reader.close)

    def write(self, data):
        self.log.write(data)
        self.log.flush()

    def test_native_backend_delayed_partial_line(self):
        self.assertIsNone(self.reader.read_backend())
        line = backend_line()
        self.write(line[:50])
        self.assertIsNone(self.reader.read_backend())
        self.write(line[50:])
        self.assertEqual(self.reader.read_backend(), 'wayland')
        self.assertEqual(self.reader.buffer, b'')

    def test_driver_must_be_native_not_session_environment(self):
        self.write(backend_line(backend='x11'))
        with self.assertRaisesRegex(ValueError, 'native-Wayland'):
            self.reader.read_backend()

    def test_wrong_child_log_pid_is_rejected(self):
        self.write(backend_line(pid=99))
        with self.assertRaises(ValueError):
            self.reader.read_backend()

    def test_backend_change_after_initial_proof_rejected(self):
        self.write(backend_line())
        self.assertEqual(self.reader.read_backend(), 'wayland')
        self.write(backend_line(backend='x11'))
        with self.assertRaises(ValueError):
            self.reader.read_backend()

    def test_arbitrary_private_log_never_exported_as_backend(self):
        self.write(b'password or certificate contents must stay private\n')
        self.assertIsNone(self.reader.read_backend())
        self.assertEqual(self.reader.buffer, b'')

    def test_log_budget_exhaustion_including_no_newline(self):
        self.write(b'x' * (self.reader.limit + 1))
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.reader.read_backend()

    def test_close_idempotent_and_does_not_close_writer(self):
        self.reader.close()
        self.reader.close()
        self.write(b'still writable; viewer is not signalled\n')
        with self.assertRaises(ValueError):
            self.reader.read_backend()

    def test_public_mode_or_pipe_log_rejected(self):
        os.fchmod(self.log.fileno(), 0o644)
        with self.assertRaises(ValueError):
            adapter.BackendEvidence(self.process, self.log, {})
        read_fd, write_fd = os.pipe()
        try:
            with os.fdopen(read_fd, 'rb') as pipe:
                with self.assertRaises(ValueError):
                    adapter.BackendEvidence(self.process, pipe, {})
        finally:
            os.close(write_fd)

    def test_reader_offsets_independent_of_child_writer(self):
        self.write(backend_line())
        offset = self.log.tell()
        self.assertEqual(self.reader.read_backend(), 'wayland')
        self.assertEqual(self.log.tell(), offset)
        self.write(b'next output\n')
        self.assertEqual(self.reader.read_backend(), 'wayland')

    def test_real_disposable_process_log_pid(self):
        # Native ABI is unnecessary here; use only a disposable Python child.
        with open(Path(self.folder.name) / 'child.log', 'w+b') as log:
            os.fchmod(log.fileno(), 0o600)
            child = subprocess.Popen([sys.executable, '-c',
                'import os; print("[0] [%d:thread] [DEBUG][com.freerdp.client.SDL] - [main]: client is using backend \'wayland\'" % os.getpid())'], stdout=log)
            self.assertEqual(child.wait(timeout=5), 0)
            reader = adapter.BackendEvidence(child, log, {})
            try:
                self.assertEqual(reader.read_backend(), 'wayland')
            finally:
                reader.close()

    def test_truncated_or_exposed_log_invalidates_cached_backend(self):
        self.write(backend_line())
        self.assertEqual(self.reader.read_backend(), 'wayland')
        self.log.truncate(0)
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.reader.read_backend()

    def test_safe_development_argv_and_no_security_policy_invention(self):
        marker = 'joetoo-rdp-' + 'a' * 64
        args = adapter.development_argv('example.invalid', 3389, 'tester', marker)
        self.assertEqual(args[:4], ['sdl-freerdp', '/v:example.invalid:3389', '/u:tester', '/t:' + marker])
        self.assertIn('/size:1024x768', args)
        self.assertIn('/smart-sizing:800x600', args)
        self.assertFalse(any(a.startswith(('/p:', '/cert:', '/sec:')) for a in args))
        self.assertIn('/v:[::1]:3390', adapter.development_argv('::1', 3390, 'tester', marker))

    def test_rejected_credentials_flags_targets_and_markers(self):
        marker = 'joetoo-rdp-' + 'a' * 64
        for host, port, user, token in [
                ('/cert:ignore', 3389, 'tester', marker), ('host;id', 3389, 'tester', marker),
                ('host', True, 'tester', marker), ('host', 65536, 'tester', marker),
                ('host', 3389, 'user:password', marker), ('host', 3389, '/p:secret', marker),
                ('host', 3389, 'tester', 'arbitrary title')]:
            with self.subTest(host=host, port=port):
                with self.assertRaises(ValueError):
                    adapter.development_argv(host, port, user, token)

    def test_child_only_backend_override(self):
        original = dict(SDL_VIDEODRIVER='x11', SDL_VIDEO_DRIVER='x11', OTHER='unchanged')
        result = adapter.development_environment(original)
        self.assertEqual(result['SDL_VIDEO_DRIVER'], 'wayland')
        self.assertNotIn('SDL_VIDEODRIVER', result)
        self.assertEqual(original['SDL_VIDEO_DRIVER'], 'x11')
        self.assertEqual(result['OTHER'], 'unchanged')

    def test_all_bounds_validate_and_allow_explicit_override(self):
        for name, (low, high) in adapter.BOUNDS.items():
            for value in (True, 0, low - 1, high + 1, 'bad', '0', '-1', 1.5):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(ValueError):
                        adapter.settings({name: value})
        data = {name: str(value) for name, value in adapter.DEFAULTS.items()}
        self.assertEqual(adapter.settings(data), adapter.DEFAULTS)
        self.assertEqual(adapter.settings({'rdp_registration_timeout_ms': 300000})['rdp_registration_timeout_ms'], 300000)
        with self.assertRaises(ValueError):
            adapter.settings(dict(rdp_registration_timeout_ms=1000, rdp_registration_poll_ms=1000))

    def test_template_defaults_match_private_adapter(self):
        import re
        text = (Path(__file__).resolve().parents[1] / 'joetoo-kwin-template.conf').read_text()
        for key, value in adapter.DEFAULTS.items():
            self.assertEqual(int(re.search(r'^' + key + r'=(\d+)$', text, re.M)[1]), value)

    def test_real_backend_reader_and_real_broker_register_without_placement(self):
        module = load_broker_without_real_dbus()
        loop = Loop()
        with patch.object(module, 'GLib', SimpleNamespace(timeout_add=loop.timeout_add,
                          source_remove=loop.source_remove, SOURCE_REMOVE=False)):
            broker = module.Broker(object())
            broker.SyncInventory(json.dumps(dict(source='source', revision=1, windows=[])))
            spec = broker._begin_rdp_registration(3, 1, adapter.settings({}))
            process = SimpleNamespace(pid=42, poll=Mock(return_value=None))
            broker._bind_rdp_process(spec['request_id'], process, self.reader)
            self.write(backend_line())
            w = json.loads(observation())['window']
            w.update(caption=spec['title_marker'], resource_class=adapter.APPLICATION)
            broker.ObserveWindow(json.dumps(dict(source='source', revision=2, event='added', window=w)))
            loop.tick()
            result = broker._poll_rdp_registration(spec['request_id'])
            self.assertEqual(result['state'], 'registered')
            self.assertEqual(result['window_uuid'], WINDOW_ID)
            self.assertEqual(broker.registry.managed_windows[WINDOW_ID].placement, 'not_requested')
            self.assertIsNone(broker.request)
            self.assertEqual(loop.callbacks, {})
            self.assertTrue(self.reader.closed)


class X11AdapterTests(unittest.TestCase):
    setUp = LaunchAdapterTests.setUp
    write = LaunchAdapterTests.write
    def test_x11_renderer_policy_is_child_only(self):
        parent = dict(SDL_VIDEO_DRIVER='wayland', SDL_VIDEODRIVER='wayland',
                      SDL_RENDER_DRIVER='opengl', SDL_FRAMEBUFFER_ACCELERATION='1')
        before = parent.copy()
        for renderer in ('auto', 'software'):
            child = adapter.development_environment(parent, adapter.X11_PROFILE, {'rdp_x11_renderer': renderer})
            self.assertEqual(parent, before)
            self.assertEqual(child['SDL_VIDEO_DRIVER'], 'x11')
            self.assertNotIn('SDL_VIDEODRIVER', child)
            if renderer == 'auto':
                self.assertNotIn('SDL_RENDER_DRIVER', child)
                self.assertNotIn('SDL_FRAMEBUFFER_ACCELERATION', child)
            else:
                self.assertEqual(child['SDL_RENDER_DRIVER'], 'software')
                self.assertEqual(child['SDL_FRAMEBUFFER_ACCELERATION'], '0')

    def test_x11_settings_profile_and_timeout_validation(self):
        result = adapter.settings({}, adapter.X11_PROFILE)
        self.assertEqual(result['rdp_x11_renderer'], 'auto')
        self.assertEqual(result['rdp_x11_identity_settle_ms'], 500)
        for name, values in dict(rdp_x11_renderer=['gpu', '', True],
                                  rdp_x11_identity_settle_ms=[0, -1, True, 1.5, '0', 30001]).items():
            for value in values:
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    adapter.settings({name: value}, adapter.X11_PROFILE)
        with self.assertRaises(ValueError):
            adapter.settings({'rdp_x11_renderer': 'auto'})
        with self.assertRaises(ValueError):
            adapter.settings({}, 'unknown')
        with self.assertRaises(ValueError):
            adapter.settings({'rdp_registration_timeout_ms': 1000, 'rdp_x11_identity_settle_ms': 1000}, adapter.X11_PROFILE)

    def test_x11_pid_backend_and_contradictory_log(self):
        for pid, backend in ((99, 'x11'), (42, 'wayland')):
            self.log.seek(0); self.log.truncate(); self.write(backend_line(pid, backend))
            reader = adapter.BackendEvidence(self.process, self.log, {}, adapter.X11_PROFILE)
            try:
                with self.assertRaises(ValueError): reader.read_backend()
            finally: reader.close()
        self.log.seek(0); self.log.truncate(); self.write(backend_line(backend='x11'))
        reader = adapter.BackendEvidence(self.process, self.log, {}, adapter.X11_PROFILE)
        try:
            self.assertEqual(reader.read_backend(), 'x11')
            self.write(backend_line())
            with self.assertRaises(ValueError): reader.read_backend()
        finally: reader.close()

    def test_x11_child_identity_checks_actual_driver_and_renderer(self):
        import select
        caller = SimpleNamespace(pid=os.getpid(), alive=lambda: True)
        st = os.stat(sys.executable)
        for renderer in ('auto', 'software'):
            env = adapter.development_environment(os.environ, adapter.X11_PROFILE, {'rdp_x11_renderer': renderer})
            child = subprocess.Popen([sys.executable, '-c',
                'import sys; print("ready",file=sys.stderr,flush=True); sys.stdin.read()'],
                stdin=subprocess.PIPE, stdout=self.log, stderr=subprocess.PIPE, env=env)
            identity = None
            try:
                self.assertTrue(select.select([child.stderr], [], [], 3)[0])
                self.assertEqual(child.stderr.readline(), b'ready\n')
                with open(self.log.name, 'rb') as log:
                    identity = adapter.ChildIdentity(caller, child.pid, log.fileno(), 0,
                        (st.st_dev, st.st_ino), 65536, adapter.X11_PROFILE, {'rdp_x11_renderer': renderer})
                self.assertIsNone(identity.poll())
                identity.bounds['rdp_x11_renderer'] = 'software' if renderer == 'auto' else 'auto'
                self.assertEqual(identity.poll(), 1)
                identity.bounds['rdp_x11_renderer'] = renderer
                identity.backend = 'wayland'
                self.assertEqual(identity.poll(), 1)
            finally:
                if identity: identity.close()
                child.stdin.close(); child.wait(timeout=3); child.stderr.close()


class ProcessIdentityTests(unittest.TestCase):
    """Actual pidfds and validators, with isolated /proc access fault seams."""
    class FD:
        def __init__(self, fd): self.fd = fd
        def take(self):
            fd, self.fd = self.fd, None
            return fd

    def credentials(self, pid=None, uid=None, descriptor=None):
        pid = os.getpid() if pid is None else pid
        value = self.FD(os.pidfd_open(pid) if descriptor is None else descriptor)
        self.addCleanup(lambda: os.close(value.fd) if value.fd is not None else None)
        return dict(ProcessFD=value, ProcessID=pid, UnixUserID=os.geteuid() if uid is None else uid)

    def caller(self):
        identity = adapter.CallerIdentity(self.credentials())
        self.addCleanup(identity.close)
        return identity

    def deny_executable(self, path):
        if path.endswith('/exe'): raise PermissionError('synthetic restricted executable link')
        return self.original_inode(path)

    def setUp(self):
        self.original_inode = adapter._inode

    def child(self):
        folder = tempfile.TemporaryDirectory(prefix='sdl-process-identity-')
        self.addCleanup(folder.cleanup)
        log = open(Path(folder.name) / 'stdout.log', 'w+b')
        os.fchmod(log.fileno(), 0o600); self.addCleanup(log.close)
        child = subprocess.Popen([sys.executable, '-c',
            'import sys; print("ready",file=sys.stderr,flush=True); sys.stdin.read()'],
            stdin=subprocess.PIPE, stdout=log, stderr=subprocess.PIPE,
            env=adapter.development_environment(os.environ))
        def cleanup():
            if not child.stdin.closed: child.stdin.close()
            child.wait(timeout=5); child.stderr.close()
        self.addCleanup(cleanup)
        import select
        self.assertTrue(select.select([child.stderr], [], [], 5)[0])
        self.assertEqual(child.stderr.readline(), b'ready\n')
        return child, log

    def test_caller_creation_and_alive_never_access_unused_executable(self):
        with patch.object(adapter, '_inode', side_effect=self.deny_executable) as inode:
            caller = self.caller()
            self.assertTrue(caller.alive())
            self.assertEqual(caller.pid, os.getpid())
            inode.assert_not_called()

    def test_proc_info_default_stays_strict_and_opt_out_omits_executable(self):
        with patch.object(adapter, '_inode', side_effect=self.deny_executable):
            with self.assertRaises(PermissionError): adapter._proc_info(os.getpid())
            info = adapter._proc_info(os.getpid(), include_executable=False)
        self.assertNotIn('exe', info)
        self.assertEqual(info['uid'], os.geteuid())
        self.assertEqual(info['start'], adapter._proc_info(os.getpid())['start'])
        self.assertIn('exe', adapter._proc_info(os.getpid()))

    def test_caller_requires_processfd_and_processid(self):
        for key in ('ProcessFD', 'ProcessID'):
            credentials = self.credentials(); credentials.pop(key)
            with self.subTest(key=key), self.assertRaises(NotImplementedError):
                adapter.CallerIdentity(credentials)

    def test_caller_rejects_regular_fd_and_closes_it(self):
        fd = os.open('/dev/null', os.O_RDONLY)
        with self.assertRaises(ValueError): adapter.CallerIdentity(self.credentials(descriptor=fd))
        with self.assertRaises(OSError): os.fstat(fd)

    def test_caller_rejects_descriptor_pid_mismatch(self):
        credentials = self.credentials(); credentials['ProcessID'] += 1
        with self.assertRaises(ValueError): adapter.CallerIdentity(credentials)

    def test_caller_rejects_credential_uid_mismatch(self):
        with self.assertRaises(PermissionError):
            adapter.CallerIdentity(self.credentials(uid=os.geteuid() + 1))

    def test_caller_rejects_proc_uid_mismatch(self):
        original = adapter._proc_info
        def changed(pid, **kwargs):
            info = original(pid, **kwargs); info['uid'] += 1
            return info
        with patch.object(adapter, '_proc_info', changed), self.assertRaises(ValueError):
            self.caller()

    def test_caller_rejects_exited_process_descriptor(self):
        child, _ = self.child()
        credentials = self.credentials(pid=child.pid)
        child.stdin.close(); child.wait(timeout=5)
        with self.assertRaises(ValueError): adapter.CallerIdentity(credentials)

    def test_caller_alive_rejects_changed_start_and_uid(self):
        caller = self.caller()
        original = adapter._proc_info
        for field in ('start', 'uid'):
            def changed(pid, **kwargs):
                info = original(pid, **kwargs); info[field] += 1
                return info
            with self.subTest(field=field), patch.object(adapter, '_proc_info', changed):
                self.assertFalse(caller.alive())
        self.assertTrue(caller.alive())

    def test_caller_start_change_during_constructor_is_rejected(self):
        original = adapter._proc_info
        calls = 0
        def changed(pid, **kwargs):
            nonlocal calls
            calls += 1
            info = original(pid, **kwargs)
            if calls > 1: info['start'] += 1
            return info
        with patch.object(adapter, '_proc_info', changed), self.assertRaises(ValueError): self.caller()

    def test_required_proc_reads_still_fail_closed(self):
        caller = self.caller()
        with patch.object(adapter, '_proc_info', side_effect=PermissionError('stat inaccessible')):
            self.assertFalse(caller.alive())
            with self.assertRaises(PermissionError): self.caller()
        import builtins, io
        original_open = builtins.open
        def malformed(path, *args, **kwargs):
            if path == '/proc/' + str(os.getpid()) + '/stat':
                return io.BytesIO(b'malformed proc stat')
            return original_open(path, *args, **kwargs)
        with patch('builtins.open', side_effect=malformed):
            with self.assertRaises((ValueError, IndexError)): self.caller()

    def test_child_executable_evidence_remains_required_at_creation_and_poll(self):
        caller = self.caller(); child, log = self.child()
        executable = adapter._inode('/proc/' + str(child.pid) + '/exe')
        def identity():
            return adapter.ChildIdentity(caller, child.pid, log.fileno(), 0, executable, 65536)
        with patch.object(adapter, '_inode', side_effect=self.deny_executable):
            with self.assertRaises(PermissionError): identity()
        owned = identity(); self.addCleanup(owned.close)
        self.assertIsNone(owned.poll())
        with patch.object(adapter, '_inode', side_effect=self.deny_executable):
            with self.assertRaises(PermissionError): owned.poll()
        original = adapter._inode
        def substituted(path): return (0, 0) if path.endswith('/exe') else original(path)
        with patch.object(adapter, '_inode', side_effect=substituted):
            self.assertEqual(owned.poll(), 1)
            with self.assertRaises(ValueError): identity()


class PublicDeclarationTests(unittest.TestCase):
    def test_real_dbus_python_declarations_without_connecting_to_a_bus(self):
        # Validate the actual decorators/signature marshalling metadata, rather
        # than relying solely on the fake decorator in broker-state fixtures.
        import importlib.util
        from importlib.machinery import SourceFileLoader
        broker_file = Path(__file__).resolve().parents[1] / 'libexec/joetoo-kwind'
        spec = importlib.util.spec_from_loader('sdl_real_declarations_test',
            SourceFileLoader('sdl_real_declarations_test', str(broker_file)))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Does not instantiate a service/bus.
        signatures = {'BeginSdlRegistration': 's', 'BindSdlRegistration': 'sih',
                      'PollSdlRegistration': 's', 'CancelSdlRegistration': 's'}
        for name, signature in signatures.items():
            fn = getattr(module.Broker, name)
            self.assertEqual(fn._dbus_in_signature, signature)
            self.assertEqual(fn._dbus_out_signature, 's')
            self.assertEqual(fn._dbus_sender_keyword, 'sender')
        self.assertEqual(module.Broker.BeginSdlRegistration._dbus_async_callbacks, ('reply', 'error'))


class SmokeClientTests(unittest.TestCase):
    def setUp(self):
        import importlib.util
        from importlib.machinery import SourceFileLoader
        from test_rdp_broker import SdlInterfaceTests
        self.fixture = SdlInterfaceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        spec = importlib.util.spec_from_loader('sdl_smoke_test', SourceFileLoader('sdl_smoke_test',
            str(Path(__file__).resolve().parents[1] / 'tools/joetoo-sdl-registration-smoke.py')))
        self.client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.client)  # Never invoke its live main().
        test = self
        self.begin_count = 0
        self.owner = ':1.broker'
        class Bridge:
            def Introspect(self, **kwargs):
                return '<node><interface name="org.joetoo.KWinBridge">' + ''.join(
                    '<method name="' + name + '">' + ''.join('<arg type="' + c + '" direction="in"/>' for c in signature)
                    + '<arg type="s" direction="out"/></method>' for name, signature in
                    dict(BeginSdlRegistration='s', BindSdlRegistration='sih',
                         PollSdlRegistration='s', CancelSdlRegistration='s').items()) + '</interface></node>'
            def RegistryStatus(self, **kwargs): return test.fixture.b.RegistryStatus()
            def ListManaged(self, **kwargs): return test.fixture.b.ListManaged()
            def BeginSdlRegistration(self, payload, **kwargs):
                test.begin_count += 1
                replies, errors = [], []
                test.fixture.b.BeginSdlRegistration(payload, sender=test.fixture.sender,
                                                   reply=replies.append, error=errors.append)
                if errors: raise errors[0]
                return replies[0]
            def CancelSdlRegistration(self, rid, **kwargs):
                return test.fixture.b.CancelSdlRegistration(rid, sender=test.fixture.sender)
            def PollSdlRegistration(self, rid, **kwargs):
                return test.fixture.b.PollSdlRegistration(rid, sender=test.fixture.sender)
            def BindSdlRegistration(self, *args, **kwargs): raise AssertionError('Smoke must not bind/spawn')
        self.bridge = Bridge()
        class Daemon:
            def GetNameOwner(self, *args, **kwargs): return test.owner
        self.daemon = Daemon()
        class Bus:
            def get_object(self, name, path, **kwargs):
                return test.daemon if name == 'org.freedesktop.DBus' else test.bridge
            def close(self): test.fixture.bus.lost()
        self.bus = Bus()

    def run_smoke(self):
        return self.client.smoke(self.bus, lambda obj, iface: obj, self.fixture.adapter.settings({}), 3)

    def test_real_core_two_cycles_no_child_no_registration_or_placement(self):
        result = self.run_smoke()
        self.assertTrue(result['ok'])
        self.assertEqual(self.begin_count, 2)
        self.assertIsNone(self.fixture.child)
        self.assertIsNone(self.fixture.b.registry._active_request_id)
        self.assertEqual(self.fixture.b.registry.managed_windows, {})
        self.assertEqual(self.fixture.b.registry.requests[self.fixture.b._rdp_registration['id']].state, 'failed')

    def test_unsynchronized_inventory_refuses_before_begin(self):
        self.fixture.b.observation_synced = False
        with self.assertRaisesRegex(RuntimeError, 'synchronized'): self.run_smoke()
        self.assertEqual(self.begin_count, 0)

    def test_active_placement_refuses_before_begin(self):
        self.fixture.b.request = dict(id='unrelated', state='PENDING')
        with self.assertRaisesRegex(RuntimeError, 'idle'): self.run_smoke()
        self.assertEqual(self.begin_count, 0)
        self.fixture.b.request = None

    def test_missing_method_refuses_before_begin(self):
        with patch.object(self.bridge, 'Introspect', return_value='<node/>'):
            with self.assertRaisesRegex(RuntimeError, 'missing'): self.run_smoke()
        self.assertEqual(self.begin_count, 0)

    def test_wrong_signature_refuses_before_begin(self):
        xml = self.bridge.Introspect().replace('type="i"', 'type="s"')
        with patch.object(self.bridge, 'Introspect', return_value=xml):
            with self.assertRaisesRegex(RuntimeError, 'signature'): self.run_smoke()
        self.assertEqual(self.begin_count, 0)

    def test_missing_processfd_is_failure_without_armed_intent(self):
        self.fixture.bus.process_fd = False
        with self.assertRaises(Exception): self.run_smoke()
        self.assertIsNone(self.fixture.b._rdp_registration)

    def test_cancel_reply_loss_stays_failure_and_best_effort_cleans(self):
        original = self.bridge.CancelSdlRegistration
        calls = []
        def lost_reply(rid, **kwargs):
            result = original(rid, **kwargs)
            calls.append(rid)
            if len(calls) == 1: raise RuntimeError('simulated lost cancel reply')
            return result
        with patch.object(self.bridge, 'CancelSdlRegistration', lost_reply):
            with self.assertRaisesRegex(RuntimeError, 'lost cancel reply'): self.run_smoke()
        self.assertIsNone(self.fixture.b.registry._active_request_id)
        self.assertEqual(len(calls), 2)

    def test_owner_replacement_aborts_and_connection_close_cleans_old_owner(self):
        def owner_after_begin(*args, **kwargs):
            return ':1.replacement' if self.begin_count else self.owner
        with patch.object(self.daemon, 'GetNameOwner', owner_after_begin):
            with self.assertRaisesRegex(RuntimeError, 'owner changed'): self.run_smoke()
        self.bus.close()  # main() closes the persistent connection on every exit.
        self.assertEqual(self.fixture.b._rdp_registration['result']['state'], 'failed')
        self.assertIsNone(self.fixture.b.registry._active_request_id)


if __name__ == "__main__":
    unittest.main()
