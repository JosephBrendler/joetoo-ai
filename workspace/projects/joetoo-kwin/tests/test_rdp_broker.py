#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real private broker/registry, simulated SDL process and KWin observations."""
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

OTHER = 'd848c4c9-64ed-48bf-b083-40230314d5ac'
AUTH = 'd848c4c9-64ed-48bf-b083-40230314d5ad'
APP = 'com.freerdp.client.sdl3'


class Loop:
    def __init__(self):
        self.callbacks = {}
        self.sequence = 0

    def timeout_add(self, interval, callback):
        self.sequence += 1
        self.callbacks[self.sequence] = callback
        return self.sequence

    def source_remove(self, timer):
        self.callbacks.pop(timer, None)

    def tick(self):
        for identifier, callback in list(self.callbacks.items()):
            if not callback():
                self.callbacks.pop(identifier, None)


class RdpBrokerTests(unittest.TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.b = self.module.Broker(object())
        self.loop = Loop()
        self.clock = 100.
        self.revision = 1
        self.patch(self.module, 'GLib', SimpleNamespace(
            timeout_add=self.loop.timeout_add, source_remove=self.loop.source_remove,
            SOURCE_REMOVE=False))
        self.patch(self.module.time, 'monotonic', lambda: self.clock)
        self.b.SyncInventory(json.dumps(dict(source='source', revision=1, windows=[])))
        # Every test, positive and negative, fails on any placement submission.
        self.submit = self.patch(self.b, '_submit', Mock(side_effect=AssertionError('placement submitted')))
        self.place = self.patch(self.b, '_sync_managed_placement', Mock(side_effect=AssertionError('placement synced')))
        self.process = SimpleNamespace(pid=42, poll=Mock(return_value=None))
        self.reader = SimpleNamespace(pid=42, read_backend=Mock(return_value='wayland'), close=Mock())
        self.arm()

    def patch(self, target, name, value):
        p = patch.object(target, name, value)
        result = p.start()
        self.addCleanup(p.stop)
        return result

    def tearDown(self):
        self.assertIsNone(self.b.request)
        self.assertIsNone(self.b.initial_layout)
        self.submit.assert_not_called()
        self.place.assert_not_called()
        for record in self.b.registry.managed_windows.values():
            self.assertEqual(record.placement, 'not_requested')
        if self.b._rdp_registration['state'] == 'PENDING':
            self.b._cancel_rdp_registration(self.rid)
        self.assertEqual(self.loop.callbacks, {})

    def arm(self, **bounds):
        self.spec = self.b._begin_rdp_registration(3, 1, bounds)
        self.rid = self.spec['request_id']
        self.marker = self.spec['title_marker']

    def bind(self):
        self.b._bind_rdp_process(self.rid, self.process, self.reader)

    def event(self, kind='added', identifier=WINDOW_ID, pid=42, caption=None, app=APP):
        w = json.loads(observation(kind, uuid=identifier))['window']
        w.update(pid=pid, resource_class=app, desktop_file=app,
                 caption=self.marker if caption is None else caption)
        self.revision += 1
        self.b.ObserveWindow(json.dumps(dict(source='source', revision=self.revision,
                                            event=kind, window=w)))
        return w

    def poll(self):
        return self.b._poll_rdp_registration(self.rid)

    def assertFailed(self, state='failed'):
        result = self.poll()
        self.assertEqual(result['state'], state, result)
        self.assertFalse(self.b.registry.managed_windows)
        return result

    def test_positive_registration_exact_uuid_without_placement(self):
        self.bind()
        self.event(identifier=AUTH, caption='Credentials required')
        self.event()
        result = self.poll()
        self.assertEqual(result['state'], 'registered')
        self.assertEqual(result['window_uuid'], WINDOW_ID)
        self.assertEqual(result['managed_id'], 'win-001')
        self.assertEqual(result['placement'], 'not_requested')
        self.assertEqual(result['remote_session'], 'unverified')
        self.assertEqual(set(self.b.registry.managed_windows), {WINDOW_ID})
        self.reader.close.assert_called_once()
        self.assertEqual(self.loop.callbacks, {})

    def test_window_creation_before_pid_handoff_is_preserved(self):
        self.event()
        self.assertEqual(self.poll()['state'], 'pending')
        self.bind()
        self.assertEqual(self.poll()['window_uuid'], WINDOW_ID)

    def test_watchdog_setup_failure_releases_registry_intent(self):
        self.b._cancel_rdp_registration(self.rid)
        self.patch(self.module.GLib, 'timeout_add', Mock(side_effect=RuntimeError('private')))
        with self.assertRaises(ValueError):
            self.arm()
        self.assertIsNone(self.b.registry._active_request_id)
        self.assertFalse(self.b.registry.managed_windows)
        self.assertEqual(self.loop.callbacks, {})

    def test_unknown_request_cannot_cancel_current_intent(self):
        self.bind()
        self.assertEqual(self.b._cancel_rdp_registration('stale'), {'state': 'unknown'})
        self.assertEqual(self.poll()['state'], 'pending')

    def test_credentials_only_cancel_never_registers(self):
        self.bind()
        self.event(identifier=AUTH, caption='Credentials required')
        self.assertEqual(self.poll()['state'], 'pending')
        self.b._cancel_rdp_registration(self.rid)
        self.assertFailed()

    def test_failed_nla_credentials_close_and_process_exits(self):
        self.bind()
        self.event(identifier=AUTH, caption='Credentials required')
        self.event('removed', AUTH, caption='Credentials required')
        self.process.poll.return_value = 134  # Fixture outcome, no authentication.
        self.assertFailed()

    def test_connection_refused_without_lifecycle(self):
        self.bind()
        self.process.poll.return_value = 141
        self.assertFailed()

    def test_late_marker_same_new_uuid(self):
        self.bind()
        self.event(caption='')
        self.assertEqual(self.poll()['state'], 'pending')
        self.event('changed')
        self.assertEqual(self.poll()['state'], 'registered')

    def test_marker_loss_then_restoration_between_polls_fails(self):
        self.bind()
        self.event()
        self.event('changed', caption='lost')
        self.event('changed')
        self.assertFailed()

    def test_decorated_marker_is_not_exact(self):
        self.bind()
        self.event(caption=self.marker + ' - duplicate')
        self.assertFailed()

    def test_two_simultaneous_eligible_windows(self):
        self.bind()
        self.event()
        self.event(identifier=OTHER)
        self.assertFailed('ambiguous')

    def test_marked_predecessor_removed_before_survivor_poll(self):
        self.bind()
        self.event(identifier=OTHER)
        self.event('removed', OTHER)
        self.event()
        self.assertFailed()

    def test_transient_late_marker_competitor_not_hidden_by_coalescing(self):
        self.bind()
        self.event(identifier=OTHER, caption='')
        self.event('changed', OTHER)
        self.event('changed', OTHER, caption='')
        self.event('removed', OTHER, caption='')
        self.event()
        self.assertFailed()

    def test_unrelated_preexisting_viewer_excluded(self):
        self.b._cancel_rdp_registration(self.rid)
        self.event(identifier=OTHER, pid=99, caption='unrelated')
        self.arm()
        self.bind()
        self.event()
        self.assertEqual(self.poll()['window_uuid'], WINDOW_ID)
        self.assertIn(OTHER, self.b.observed_windows)
        self.assertNotIn(OTHER, self.b.registry.managed_windows)

    def test_wrong_pid(self):
        self.bind()
        self.event(pid=99)
        self.assertFailed()

    def test_wrong_application(self):
        self.bind()
        self.event(app='unrelated.sdl3')
        self.assertFailed()

    def test_transient_pid_or_class_change_cannot_be_erased(self):
        self.bind()
        self.event()
        self.event('changed', pid=99)
        self.event('changed')
        self.assertFailed()

    def test_changed_only_is_not_added(self):
        self.bind()
        self.event('changed')
        self.assertFailed()

    def test_existing_only_is_not_added(self):
        self.bind()
        self.event('existing')
        self.assertFailed()

    def test_evicted_lifecycle_fails(self):
        self.bind()
        self.event()
        self.b.observation_evicted_through = self.b._rdp_registration['event_floor'] + 1
        self.assertFailed()

    def test_actual_lifecycle_eviction_fails_closed(self):
        self.b._cancel_rdp_registration(self.rid)
        self.arm(rdp_registration_window_limit=512)
        self.bind()
        for n in range(70):
            identifier = f'{n:08x}-0000-4000-8000-000000000001'
            self.event(identifier=identifier, pid=99, caption='')
            self.event('removed', identifier, pid=99, caption='')
        self.assertFailed()

    def test_missing_revision_detects_lost_transient_event(self):
        self.bind()
        self.revision += 1
        self.event()
        self.assertFailed()

    def test_source_replaced(self):
        self.bind()
        self.event()
        self.b.SyncInventory(json.dumps(dict(source='replacement', revision=1, windows=[])))
        self.assertFailed()

    def test_synchronization_lost(self):
        self.bind()
        self.event()
        self.b.observation_synced = False
        self.assertFailed()

    def test_inventory_disappearance_then_reappearance_fails(self):
        self.bind()
        window = self.event()
        self.revision += 1
        self.b.SyncInventory(json.dumps(dict(source='source', revision=self.revision, windows=[])))
        self.revision += 1
        self.b.SyncInventory(json.dumps(dict(source='source', revision=self.revision, windows=[window])))
        self.assertFailed()

    def test_same_source_inventory_refresh_preserves_birth(self):
        self.bind()
        w = self.event()
        self.revision += 1
        self.b.SyncInventory(json.dumps(dict(source='source', revision=self.revision, windows=[w])))
        self.assertEqual(self.poll()['state'], 'registered')

    def test_viewer_removal(self):
        self.bind()
        self.event()
        self.event('removed')
        self.assertFailed()

    def test_missing_retained_added_record_fails(self):
        self.bind()
        self.event()
        self.b.observation_events.clear()
        self.assertFailed()

    def test_exit_during_backend_read_cannot_register(self):
        self.bind()
        self.event()
        self.process.poll.side_effect = [None, 0]
        self.assertFailed()

    def test_process_exit_wins_over_eligible_window(self):
        self.bind()
        self.event()
        self.process.poll.return_value = 0
        self.assertFailed()

    def test_automatic_watchdog_expiry_no_poll(self):
        self.bind()
        self.clock += 121
        self.loop.tick()
        self.assertFailed('timeout')

    def test_unbound_watchdog_expires(self):
        self.clock += 121
        self.loop.tick()
        self.assertFailed('timeout')

    def test_pending_without_backend_proof_then_ready(self):
        self.bind()
        self.event()
        self.reader.read_backend.return_value = None
        self.assertEqual(self.poll()['state'], 'pending')
        self.reader.read_backend.return_value = 'wayland'
        self.loop.tick()
        self.assertEqual(self.poll()['state'], 'registered')

    def test_x11_backend_even_without_window_rejected(self):
        self.bind()
        self.reader.read_backend.return_value = 'x11'
        self.assertFailed()

    def test_backend_error_or_budget_failure(self):
        self.bind()
        self.reader.read_backend.side_effect = ValueError('sensitive untrusted log')
        result = self.assertFailed()
        self.assertNotIn('sensitive', json.dumps(result))

    def test_duplicate_transaction_is_refused_without_overwrite(self):
        original = self.b._rdp_registration
        with self.assertRaises(ValueError):
            self.b._begin_rdp_registration(3, 2, {})
        self.assertIs(self.b._rdp_registration, original)

    def test_duplicate_pid_binding_rejected(self):
        self.bind()
        with self.assertRaises(ValueError):
            self.bind()
        self.event()
        self.assertEqual(self.poll()['state'], 'registered')

    def test_slot_conflict_after_positive_registration(self):
        self.bind()
        self.event()
        self.assertEqual(self.poll()['state'], 'registered')
        with self.assertRaises(ValueError):
            self.b._begin_rdp_registration(3, 1, {})

    def test_duplicate_uuid_ownership_rejected(self):
        self.bind()
        self.event()
        # Another real registry entry occupies the UUID; registration is atomic.
        from joetoo_kwin_registry import ManagedWindow
        self.b.registry.managed_windows[WINDOW_ID] = ManagedWindow(
            'win-099', WINDOW_ID, 'prior', None, {'desktop': 9, 'slot': 1},
            deepcopy(self.b.observed_windows[WINDOW_ID]))
        self.assertEqual(self.poll()['state'], 'failed')
        self.assertEqual(self.b.registry.managed_windows[WINDOW_ID].managed_id, 'win-099')

    def test_event_budget_exhaustion(self):
        self.b._cancel_rdp_registration(self.rid)
        self.arm(rdp_registration_event_limit=16)
        self.bind()
        self.event(identifier=AUTH, caption='Credentials required')
        for n in range(16):
            self.event('changed', AUTH, caption='Credentials required')
        self.assertFailed()

    def test_window_budget_exhaustion(self):
        self.b._cancel_rdp_registration(self.rid)
        self.arm(rdp_registration_window_limit=1)
        self.bind()
        self.event(identifier=AUTH, caption='Credentials required')
        self.event()
        self.assertFailed()

    def test_terminal_reporting_and_late_callbacks_are_inert(self):
        self.bind()
        queued = next(iter(self.loop.callbacks.values()))
        self.b._cancel_rdp_registration(self.rid)
        result = self.poll()
        self.event()
        self.assertFalse(queued())
        self.assertEqual(self.poll(), result)
        result['state'] = 'tampered'
        self.assertEqual(self.poll()['state'], 'failed')
        self.reader.close.assert_called_once()

    def test_registered_uuid_not_replaced_or_reregistered(self):
        self.bind()
        self.event()
        result = self.poll()
        self.event('removed')
        self.event(identifier=OTHER)
        self.assertEqual(self.poll(), result)
        self.assertEqual(set(self.b.registry.managed_windows), {WINDOW_ID})
        self.assertEqual(self.b.registry.managed_windows[WINDOW_ID].presence, 'missing')

    def test_cleanup_failure_cannot_register(self):
        self.bind()
        self.event()
        self.reader.close.side_effect = OSError('private')
        self.assertFailed()
        self.reader.close.assert_called_once()

    def test_unsynchronized_arm_and_invalid_layout_rejected(self):
        self.b._cancel_rdp_registration(self.rid)
        self.b.observation_synced = False
        with self.assertRaises(ValueError):
            self.arm()
        self.b.observation_synced = True
        for d, slot in [(True, 1), (0, 1), (3, 257)]:
            with self.assertRaises(ValueError):
                self.b._begin_rdp_registration(d, slot, {})

    def test_reader_pid_mismatch_refused(self):
        self.reader.pid = 99
        with self.assertRaises(ValueError):
            self.bind()
        self.assertEqual(self.poll()['state'], 'pending')

    def test_generic_arm_cannot_overwrite_private_registration(self):
        self.bind()
        # Real public generic arm rolls back placement if registry is busy;
        # its _submit is stubbed here only to avoid placing in this test.
        self.submit.side_effect = None
        self.submit.return_value = 'temporary-placement'
        with self.assertRaises(Exception):
            self.b.SubmitManagedLaunch('konsole', 4, 1, 0, 0, 100, 100)
        self.submit.reset_mock()
        self.assertEqual(self.poll()['state'], 'pending')

    def test_marker_unique_and_bounds_explicit(self):
        marker = self.marker
        self.assertRegex(marker, r'^joetoo-rdp-[0-9a-f]{64}$')
        self.b._cancel_rdp_registration(self.rid)
        self.arm(rdp_registration_timeout_ms=300000)
        self.assertNotEqual(self.marker, marker)
        self.assertEqual(self.spec['bounds']['rdp_registration_timeout_ms'], 300000)
        self.assertEqual(self.b._rdp_registration['deadline'], self.clock + 300)


class SdlInterfaceTests(unittest.TestCase):
    """Public wrappers, real Linux identity/FD checks, no session-bus traffic."""
    def setUp(self):
        import os
        import tempfile
        from pathlib import Path
        self.os = os
        self.folder = tempfile.TemporaryDirectory(prefix='step1.5c5d-sdl-interface-')
        self.addCleanup(self.folder.cleanup)
        self.log = open(Path(self.folder.name) / 'child.log', 'w+b')
        os.fchmod(self.log.fileno(), 0o600)
        self.addCleanup(self.log.close)
        self.module = load_broker_without_real_dbus()
        self.b = self.module.Broker(object())
        self.loop = Loop()
        self.clock = 100.
        self.revision = 1
        self.replies, self.errors = [], []
        self.sender = ':1.501'
        self.bus = self.Bus(self)
        self.patch(self.module, 'GLib', SimpleNamespace(timeout_add=self.loop.timeout_add,
                   source_remove=self.loop.source_remove, SOURCE_REMOVE=False))
        self.patch(self.module.time, 'monotonic', lambda: self.clock)
        self.patch(self.module.dbus, 'Interface', lambda obj, iface: obj, create=True)
        self.patch(self.b, '_sdl_bus_connection', lambda: self.bus)
        self.b.SyncInventory(json.dumps(dict(source='source', revision=1, windows=[])))
        self.submit = self.patch(self.b, '_submit', Mock(side_effect=AssertionError('placement')))
        self.place = self.patch(self.b, '_sync_managed_placement', Mock(side_effect=AssertionError('placement')))
        import joetoo_kwin_rdp_launch as adapter
        self.adapter = adapter
        info = os.stat(__import__('sys').executable)
        self.exe = (info.st_dev, info.st_ino)
        self.patch(adapter, 'executable_identity', lambda: self.exe)
        self.child = None
        self.addCleanup(self.finish)

    def patch(self, obj, name, value, **kwargs):
        p = patch.object(obj, name, value, **kwargs)
        result = p.start()
        self.addCleanup(p.stop)
        return result

    class FD:
        def __init__(self, fd): self.fd = fd
        def take(self):
            if self.fd is None: raise ValueError('already taken')
            fd, self.fd = self.fd, None
            return fd

    class Match:
        def __init__(self, callback): self.callback, self.removed = callback, False
        def remove(self): self.removed = True

    class Bus:
        def __init__(self, test):
            self.test = test
            self.matches = []
            self.pending = []
            self.auto = True
            self.uid = test.os.geteuid()
            self.process_fd = True
            self.connected = True
            self.lost_senders = set()
        def get_is_connected(self): return self.connected
        def get_object(self, *args, **kwargs): return self
        def add_signal_receiver(self, callback, **kwargs):
            match = self.test.Match(callback)
            self.matches.append(match)
            return match
        def GetConnectionCredentials(self, sender, reply_handler, error_handler, timeout):
            self.pending.append((reply_handler, error_handler))
            if self.auto: self.deliver()
        def credentials(self):
            result = dict(UnixUserID=self.uid, ProcessID=self.test.os.getpid())
            if self.process_fd:
                result['ProcessFD'] = self.test.FD(self.test.os.pidfd_open(self.test.os.getpid()))
            return result
        def deliver(self):
            reply, error = self.pending.pop(0)
            reply(self.credentials())
        def lost(self):
            self.lost_senders.add(self.test.sender)
            for match in list(self.matches):
                if not match.removed: match.callback(self.test.sender, self.test.sender, '')

    def finish(self):
        c = self.b._rdp_registration
        if c is not None and c['state'] == 'PENDING':
            self.b._cancel_rdp_registration(c['id'])
        if self.b._sdl_pending_auth is not None:
            self.bus.lost()
        if self.child is not None:
            self.child.stdin.close()
            self.child.wait(timeout=5)
            self.child.stderr.close()
        self.submit.assert_not_called()
        self.place.assert_not_called()
        self.assertIsNone(self.b.request)
        self.assertEqual(self.loop.callbacks, {})
        self.assertTrue(all(m.removed for m in self.bus.matches))
        for record in self.b.registry.managed_windows.values():
            self.assertEqual(record.placement, 'not_requested')

    def assert_client_connected(self, sender=None):
        self.assertTrue(self.bus.connected, 'Disconnected transport cannot issue a call')
        self.assertNotIn(sender or self.sender, self.bus.lost_senders, 'Disconnected sender cannot issue a call')

    def begin(self, sender=None, payload=None):
        self.assert_client_connected(sender)
        self.replies.clear(); self.errors.clear()
        payload = payload if payload is not None else json.dumps(dict(protocol=1, desktop=3, slot=1, bounds={}))
        self.b.BeginSdlRegistration(payload, sender=sender or self.sender,
                                    reply=self.replies.append, error=self.errors.append)
        if self.replies:
            spec = json.loads(self.replies[-1]); self.rid = spec['request_id']; self.marker = spec['title_marker']
            return spec

    def spawn(self, backend='wayland', driver='wayland'):
        import subprocess,sys,select
        code = ('import os,sys; print("[0] [%d:thread] [DEBUG][com.freerdp.client.SDL] - '
                '[main]: client is using backend \'%s\'" % (os.getpid(),sys.argv[1]), flush=True); '
                'print("ready",file=sys.stderr,flush=True); sys.stdin.read()')
        self.child = subprocess.Popen([sys.executable, '-c', code, backend],
            stdin=subprocess.PIPE, stdout=self.log, stderr=subprocess.PIPE,
            env=dict(self.os.environ, SDL_VIDEO_DRIVER=driver))
        self.assertTrue(select.select([self.child.stderr], [], [], 5)[0])
        self.assertEqual(self.child.stderr.readline(), b'ready\n')
        return self.child.pid

    def bind(self, pid=None, file=None, sender=None):
        self.assert_client_connected(sender)
        fd = self.os.dup((file or self.log).fileno())
        wrapped = self.FD(fd)
        try:
            return json.loads(self.b.BindSdlRegistration(self.rid, pid if pid is not None else self.child.pid,
                                                        wrapped, sender=sender or self.sender))
        finally:
            with self.assertRaises(OSError): self.os.fstat(fd)

    def event(self):
        window = json.loads(observation())['window']
        window.update(pid=self.child.pid, resource_class=APP, caption=self.marker)
        self.revision += 1
        self.b.ObserveWindow(json.dumps(dict(source='source', revision=self.revision, event='added', window=window)))

    def poll(self, sender=None, request=None):
        self.assert_client_connected(sender)
        return json.loads(self.b.PollSdlRegistration(request or self.rid, sender=sender or self.sender))

    def test_public_positive_real_pidfd_log_and_registry_without_placement(self):
        self.begin(); self.spawn(); self.assertEqual(self.bind()['state'], 'pending'); self.event()
        result = self.poll()
        self.assertEqual(result['state'], 'registered')
        self.assertEqual(result['window_uuid'], WINDOW_ID)
        self.assertEqual(result['reason'], 'registered')
        self.assertEqual(self.b.registry.managed_windows[WINDOW_ID].observation['pid'], self.child.pid)
        self.assertEqual(self.poll(), result)
        self.bus.lost()  # Terminal success survives owner disconnect internally.
        self.assertEqual(self.b._sdl_response(self.rid), result)

    def test_optional_processfd_absent_fails_closed_without_intent(self):
        self.bus.process_fd = False
        self.begin()
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.NotSupported')
        self.assertIsNone(self.b._rdp_registration)
        self.assertIsNone(self.b.registry._active_request_id)

    def test_wrong_uid_and_missing_sender(self):
        self.bus.uid += 1
        self.begin()
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.AccessDenied')
        self.assertIsNone(self.b._rdp_registration)
        self.errors.clear()
        self.b.BeginSdlRegistration('{}', sender=None, reply=self.replies.append, error=self.errors.append)
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.AccessDenied')

    def test_same_uid_nonowner_cannot_poll_cancel_or_bind_known_request(self):
        self.begin(); self.spawn()
        for fn in (lambda: self.poll(sender=':1.502'),
                   lambda: self.b.CancelSdlRegistration(self.rid, sender=':1.502'),
                   lambda: self.bind(sender=':1.502')):
            with self.assertRaises(self.module.dbus.DBusException) as e: fn()
            self.assertEqual(e.exception.name, 'org.freedesktop.DBus.Error.AccessDenied')
        self.assertEqual(self.poll()['state'], 'pending')
        self.assertIsNone(self.b._rdp_registration['pid'])

    def test_forged_pid_not_a_new_direct_child(self):
        self.begin(); self.spawn()
        result = self.bind(pid=self.os.getpid())
        self.assertEqual(result['state'], 'failed')
        self.assertEqual(result['reason'], 'child_identity_rejected')
        self.assertFalse(self.b.registry.managed_windows)

    def test_substituted_log_descriptor(self):
        import tempfile
        self.begin(); self.spawn()
        with tempfile.NamedTemporaryFile(dir=self.folder.name) as other:
            self.os.fchmod(other.fileno(), 0o600)
            result = self.bind(file=other)
        self.assertEqual(result['state'], 'failed')

    def test_public_log_mode_rejected(self):
        self.begin(); self.spawn(); self.os.fchmod(self.log.fileno(), 0o644)
        self.assertEqual(self.bind()['state'], 'failed')

    def test_contradictory_backend_log_fails(self):
        self.begin(); self.spawn(backend='x11'); self.bind(); self.event()
        result = self.poll()
        self.assertEqual(result['state'], 'failed')
        self.assertEqual(result['reason'], 'backend_unverified')

    def test_wrong_initial_driver_even_if_log_claims_wayland(self):
        self.begin(); self.spawn(driver='x11')
        self.assertEqual(self.bind()['state'], 'failed')

    def test_wrong_executable_rejected(self):
        self.begin(); self.spawn()
        self.b._rdp_registration['executable'] = (0, 0)
        self.assertEqual(self.bind()['state'], 'failed')

    def test_pid_reuse_metadata_cannot_retarget_held_reference(self):
        self.begin(); self.spawn(); self.bind(); self.event()
        original = self.adapter._proc_info
        def reused(pid):
            info = original(pid)
            if pid == self.child.pid: info['start'] += 1
            return info
        with patch.object(self.adapter, '_proc_info', reused):
            self.assertEqual(self.poll()['state'], 'failed')
        self.assertFalse(self.b.registry.managed_windows)

    def test_owner_name_loss_cleanup(self):
        self.begin(); self.spawn(); self.bind()
        c = self.b._rdp_registration
        caller, child, reader = c['owner_identity'], c['process'], c['reader']
        self.bus.lost()
        self.assertEqual(self.b._sdl_response(self.rid)['reason'], 'caller_lost')
        self.assertIsNone(caller.fd); self.assertIsNone(child.fd); self.assertTrue(reader.closed)
        self.assertIsNone(self.child.poll())  # Broker never kills the viewer.

    def test_cancel_terminal_idempotent_and_late_events_inert(self):
        self.begin(); self.spawn(); self.bind()
        result = json.loads(self.b.CancelSdlRegistration(self.rid, sender=self.sender))
        self.assertEqual(result['reason'], 'cancelled')
        self.event()
        self.assertEqual(self.poll(), result)
        self.assertEqual(json.loads(self.b.CancelSdlRegistration(self.rid, sender=self.sender)), result)

    def test_duplicate_bind_refused_and_received_fd_closed(self):
        self.begin(); self.spawn(); self.bind()
        original = self.b._rdp_registration['process']
        with self.assertRaises(self.module.dbus.DBusException) as e: self.bind()
        self.assertEqual(e.exception.name, self.module.IFACE + '.InvalidRequest')
        self.assertIs(self.b._rdp_registration['process'], original)
        self.event(); self.assertEqual(self.poll()['state'], 'registered')

    def test_previous_request_cannot_cancel_new_transaction(self):
        self.begin(); old = self.rid
        self.b.CancelSdlRegistration(old, sender=self.sender)
        self.begin()
        with self.assertRaises(self.module.dbus.DBusException) as e:
            self.b.CancelSdlRegistration(old, sender=self.sender)
        self.assertEqual(e.exception.name, self.module.IFACE + '.UnknownRequest')
        self.assertEqual(self.poll()['state'], 'pending')

    def test_competing_begin_does_not_overwrite_owner(self):
        self.begin(); old = self.rid
        self.begin(sender=':1.502')
        self.assertEqual(self.errors[-1].name, self.module.IFACE + '.Busy')
        self.assertEqual(self.b._rdp_registration['id'], old)
        self.assertEqual(self.b._rdp_registration['owner_name'], self.sender)

    def test_malformed_begin_schema_and_bounds_never_arm(self):
        for data in ('{"protocol":1,"protocol":1}',
                     '{"protocol":NaN}',
                     json.dumps(dict(protocol=True, desktop=3, slot=1, bounds={})),
                     json.dumps(dict(protocol=1, desktop=3, slot=1, bounds={'unknown':1})),
                     'x' * 8193):
            self.begin(payload=data)
            self.assertEqual(self.errors[-1].name, self.module.IFACE + '.BadArguments')
            self.assertIsNone(self.b._rdp_registration)

    def test_authentication_timeout_and_late_reply_release_fd(self):
        self.bus.auto = False
        self.begin()
        self.assertIsNone(self.b._rdp_registration)
        self.clock += 121; self.loop.tick()
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.Timeout')
        credentials = self.bus.credentials()
        fd = credentials['ProcessFD'].fd
        self.bus.pending.pop(0)[0](credentials)
        with self.assertRaises(OSError): self.os.fstat(fd)
        self.assertIsNone(self.b._rdp_registration)

    def test_owner_loss_during_authentication(self):
        self.bus.auto = False
        self.begin(); self.bus.lost()
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.AccessDenied')
        self.bus.deliver()
        self.assertIsNone(self.b._rdp_registration)

    def test_pending_credentials_request_bound_and_deadline_not_renewed(self):
        self.bus.auto = False
        self.begin(); original = self.b._sdl_pending_auth
        self.begin(sender=':1.502')
        self.assertEqual(self.errors[-1].name, self.module.IFACE + '.Busy')
        self.assertIs(self.b._sdl_pending_auth, original)
        self.clock += 5
        self.bus.deliver()
        spec = json.loads(self.replies[-1]); self.rid = spec['request_id']
        self.assertEqual(self.b._rdp_registration['deadline'], 220.)
        self.poll(); self.assertEqual(self.b._rdp_registration['deadline'], 220.)

    def test_child_reparent_or_uid_change_rejected(self):
        self.begin(); self.spawn()
        original = self.adapter._proc_info
        def different_parent(pid):
            info = original(pid)
            if pid == self.child.pid: info['parent'] += 1
            return info
        with patch.object(self.adapter, '_proc_info', different_parent):
            self.assertEqual(self.bind()['state'], 'failed')

    def test_child_predating_arm_rejected(self):
        self.begin(); self.spawn()
        self.b._rdp_registration['boot_floor'] = self.adapter._proc_info(self.child.pid)['start'] + 1
        self.assertEqual(self.bind()['state'], 'failed')

    def test_forged_pid_in_real_child_backend_log_rejected(self):
        self.begin(); self.spawn()
        self.log.seek(0); self.log.truncate()
        self.log.write(b"[0] [1:thread] [DEBUG][com.freerdp.client.SDL] - [main]: client is using backend 'wayland'\n")
        self.log.flush()
        self.bind(); self.event()
        self.assertEqual(self.poll()['state'], 'failed')

    def test_unreadable_pipe_fd_rejected_and_closed(self):
        self.begin(); self.spawn()
        read_fd, write_fd = self.os.pipe()
        try:
            result = json.loads(self.b.BindSdlRegistration(self.rid, self.child.pid, self.FD(read_fd), sender=self.sender))
            self.assertEqual(result['state'], 'failed')
            with self.assertRaises(OSError): self.os.fstat(read_fd)
        finally:
            self.os.close(write_fd)

    def test_owner_start_identity_change_fails_before_bind(self):
        self.begin(); self.spawn()
        original = self.adapter._proc_info
        def reused(pid):
            info = original(pid)
            if pid == self.os.getpid(): info['start'] += 1
            return info
        with patch.object(self.adapter, '_proc_info', reused):
            self.assertEqual(self.bind()['state'], 'failed')
        self.assertEqual(self.poll()['reason'], 'caller_lost')

    def test_unauthorized_poll_does_not_advance_or_expire_owner(self):
        self.begin()
        self.clock += 121
        with self.assertRaises(self.module.dbus.DBusException): self.poll(sender=':1.502')
        self.assertEqual(self.b._rdp_registration['state'], 'PENDING')
        self.loop.tick()
        self.assertEqual(self.poll()['state'], 'timeout')

    def test_bus_credential_processfd_with_forged_numeric_pid_rejected(self):
        original = self.bus.credentials
        descriptors = []
        def forged():
            result = original()
            descriptors.append(result['ProcessFD'].fd)
            result['ProcessID'] += 1
            return result
        self.patch(self.bus, 'credentials', forged)
        self.begin()
        self.assertTrue(self.errors)
        self.assertIsNone(self.b._rdp_registration)
        with self.assertRaises(OSError): self.os.fstat(descriptors[0])

    def test_log_mode_changed_after_bind_fails_closed(self):
        self.begin(); self.spawn(); self.bind(); self.event()
        self.os.fchmod(self.log.fileno(), 0o644)
        self.assertEqual(self.poll()['state'], 'failed')

    def test_child_effective_uid_changed_rejected(self):
        self.begin(); self.spawn()
        original = self.adapter._proc_info
        def different_uid(pid):
            info = original(pid)
            if pid == self.child.pid: info['uid'] += 1
            return info
        with patch.object(self.adapter, '_proc_info', different_uid):
            self.assertEqual(self.bind()['state'], 'failed')

    def test_bus_disconnect_before_commit_fails_closed(self):
        self.begin(); self.spawn(); self.bind(); self.event()
        self.bus.connected = False
        self.loop.tick()  # No external call can arrive on the disconnected bus.
        self.assertEqual(self.b._sdl_response(self.rid)['reason'], 'caller_lost')
        self.assertFalse(self.b.registry.managed_windows)

    def test_bus_disconnect_during_authentication(self):
        self.bus.auto = False
        self.begin(); self.bus.connected = False; self.loop.tick()
        self.assertEqual(self.errors[-1].name, 'org.freedesktop.DBus.Error.AccessDenied')
        self.bus.deliver()
        self.assertIsNone(self.b._rdp_registration)

    def test_fixture_refuses_external_calls_after_owner_loss(self):
        self.begin(); self.bus.lost()
        for operation in (self.poll, self.bind, self.begin):
            with self.assertRaisesRegex(AssertionError, 'Disconnected sender'):
                operation()
        self.assertEqual(self.b._sdl_response(self.rid)['reason'], 'caller_lost')


if __name__ == "__main__":
    unittest.main()
