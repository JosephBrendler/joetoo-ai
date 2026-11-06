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


if __name__ == '__main__':
    unittest.main()


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
