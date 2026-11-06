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
            if self.mode in ('positive', 'competing', 'stay'):
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
        self.assertTrue(kwargs['close_fds'])
        self.assertEqual(kwargs['env']['SDL_VIDEO_DRIVER'], 'wayland')
        self.assertEqual(kwargs['stderr'], subprocess.STDOUT)
        if self.mode == 'spawn_failure': raise OSError('simulated exec failure')
        code = ('import os,sys; print("[0] [%d:thread] [DEBUG][com.freerdp.client.SDL] - '
                '[main]: client is using backend \'%s\'" % (os.getpid(),sys.argv[1]),flush=sys.argv[2] == "flush"); '
                'print("ready",file=sys.stderr,flush=True); sys.stdin.read()')
        self.child = subprocess.Popen([sys.executable, '-c', code,
            'x11' if self.mode == 'x11' else 'wayland',
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

    def run_launcher(self):
        # close() models disconnect; no further external calls are possible.
        original_close = self.transport.bus.close
        def close():
            original_close()
            self.f.bus.connected = False
        self.transport.bus.close = close
        return self.client.launch(self.transport.bus, lambda obj, iface: obj,
            lambda fd: self.f.FD(os.dup(fd)), self.f.adapter, 'example.invalid', 3389,
            'testuser', 3, 1, {}, emit=self.output.append, spawn=self.spawn,
            sleep=self.wait, clock=lambda: self.f.clock, cancelled=lambda: self.cancelled)

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


if __name__ == '__main__':
    unittest.main()
