"""Disposable offline fixtures only. No DISPLAY, native bus or input access."""
import ctypes as C
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

TOOL = Path(__file__).resolve().parents[1] / 'tools/joetoo-rdp-x11-use.py'
spec = importlib.util.spec_from_file_location('rdp_x11_use', TOOL)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
A = '11111111-1111-4111-8111-111111111111'
B = '22222222-2222-4222-8222-222222222222'


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.rows = []; self.c = m.Capture(lambda k, b: self.rows.append((k, b.copy())), 4)

    def add(self, xid=10, timestamp=100, **kwargs):
        self.c.add(xid, 456, True, False, timestamp, **kwargs)

    def test_keep_checking_until_changed_then_latch_once(self):
        self.add()
        for value in [100, 100, 0, None, None]:
            self.assertFalse(self.c.observe(10, value))
        # Reappearance initializes the baseline; a later change confirms use.
        self.assertFalse(self.c.observe(10, 101))
        self.assertTrue(self.c.observe(10, 102))
        for value in [103, 104, None]: self.assertFalse(self.c.observe(10, value))
        self.assertEqual([k for k, b in self.rows], ['candidate', 'use_latched'])
        self.assertNotIn('last', self.c.windows[10])
        self.assertNotIn('timestamp', json.dumps(self.rows))

    def test_initial_nonzero_is_not_activity_and_absence_does_not_stop(self):
        self.add(timestamp=None)
        self.assertFalse(self.c.observe(10, None))
        self.assertFalse(self.c.observe(10, 800))
        self.assertFalse(self.c.observe(10, 800))
        self.assertTrue(self.c.observe(10, 801))

    def test_wrapping_timestamp_is_not_ordered_as_wall_clock(self):
        self.add(timestamp=0xfffffffe)
        self.assertTrue(self.c.observe(10, 2))

    def test_temporary_window_can_vanish_without_activity(self):
        self.add(); self.c.remove(10)
        self.assertFalse(self.c.observe(10, 101))
        self.assertEqual(self.c.summary()['latched'], 0)
        self.assertEqual(self.c.summary()['unlinked'], 1)

    def test_credential_use_remains_role_unproven(self):
        self.add(); self.assertTrue(self.c.observe(10, 101))
        self.assertEqual(self.rows[-1][1]['desktop_role'], 'unproven')

    def test_delegated_property_explicitly_unsupported(self):
        self.add(delegated=True)
        self.assertFalse(self.c.observe(10, 101))
        self.assertEqual(self.c.summary()['unsupported'], 1)

    def test_independent_candidates_and_no_register_or_place(self):
        self.add(10); self.add(11)
        self.assertTrue(self.c.observe(11, 200))
        self.assertFalse(self.c.windows[10]['used'])
        self.assertEqual(self.c.summary()['desktop_role'], 'unproven')

    def test_exact_uuid_link_and_no_replacement(self):
        self.add(); link = dict(xid=10, pid=456, generation=1, uuid=A)
        self.c.link([link]); self.c.link([link])
        self.assertEqual(sum(k == 'uuid_link' for k, b in self.rows), 1)
        with self.assertRaisesRegex(m.Invalid, 'uuid_replacement'):
            self.c.link([dict(link, uuid=B)])

    def test_wrong_pid_uuid_and_duplicate_uuid_rejected(self):
        self.add(10); self.add(11)
        link = dict(xid=10, pid=456, generation=1, uuid=A)
        for wrong in [dict(link, pid=999), dict(link, uuid='invalid')]:
            with self.assertRaises(m.Invalid): self.c.link([wrong])
        self.c.link([link])
        with self.assertRaisesRegex(m.Invalid, 'duplicate_uuid'):
            self.c.link([dict(link, xid=11, generation=2)])

    def test_xid_reuse_preserves_history_and_rejects_late_link(self):
        self.add(); self.c.remove(10); self.add()
        self.c.link([dict(xid=10, pid=456, generation=1, uuid=A)])
        self.assertIsNone(self.c.windows[10]['uuid'])
        self.assertEqual(self.c.summary()['candidates'], 2)

    def test_candidate_budget_includes_reused_xids(self):
        for _ in range(4): self.add(); self.c.remove(10)
        with self.assertRaisesRegex(m.Invalid, 'candidate_limit'): self.add()


class NativeAbiTests(unittest.TestCase):
    def setUp(self):
        self.x = object.__new__(m.X11); self.x.conn = 42
        self.x.lib = MagicMock(); self.x.libc = MagicMock()
        self.x.atoms = {'test': 200}; self.x.lib.xcb_connection_has_error.return_value = 0

    def reply(self, fmt, typ, raw, after=0):
        data = bytearray(32) + raw; data[1] = fmt
        struct.pack_into('=III', data, 8, typ, after, len(raw) // (fmt // 8) if fmt else 0)
        self.buffer = C.create_string_buffer(bytes(data))
        self.x.lib.xcb_get_property_reply.return_value = C.addressof(self.buffer)

    def test_only_property_and_structure_masks_no_input_selection(self):
        self.x.lib.xcb_request_check.return_value = None
        masks = []
        self.x.lib.xcb_change_window_attributes_checked.side_effect = lambda c, w, b, p: masks.append(C.cast(p, C.POINTER(C.c_uint32))[0])
        self.x.watch(10, (1 << 17) | (1 << 22)); self.x.watch(10, 1 << 17)
        self.assertEqual(masks, [(1 << 17) | (1 << 22), 1 << 17])
        self.assertTrue(all(mask & 15 == 0 for mask in masks))

    def test_native_numeric_property_layout_and_free(self):
        self.reply(32, 6, struct.pack('=I', 456))
        self.assertEqual(self.x.number(10, 'test'), 456)
        self.x.libc.free.assert_called_once()

    def test_missing_property_and_invalid_types(self):
        self.reply(0, 0, b''); self.assertIsNone(self.x.number(10, 'test'))
        self.reply(8, 31, b'abcd')
        with self.assertRaises(m.Invalid): self.x.number(10, 'test')

    def test_oversize_reply_rejected_and_freed(self):
        self.reply(32, 6, struct.pack('=I', 3), after=100)
        with self.assertRaisesRegex(m.Invalid, 'property_bound'): self.x.number(10, 'test')
        self.x.libc.free.assert_called_once()

    def test_vanished_window_and_event_flood_fail_explicitly(self):
        self.x.lib.xcb_get_property_reply.return_value = None
        with self.assertRaises(m.Invalid): self.x.prop(10, 'test')
        event = C.create_string_buffer(bytes(32))
        self.x.lib.xcb_poll_for_event.return_value = C.addressof(event)
        with self.assertRaisesRegex(m.Invalid, 'event_budget'): self.x.events(2)

    def test_connection_loss_and_idempotent_close(self):
        self.x.lib.xcb_connection_has_error.return_value = 1
        with self.assertRaisesRegex(m.Invalid, 'disconnected'): self.x.events(2)
        self.x.close(); self.x.close()
        self.x.lib.xcb_disconnect.assert_called_once_with(42)

    def test_real_libxcb_property_reply_over_isolated_socketpair(self):
        """The existing VNC prototype's isolated native-ABI technique, not Xorg."""
        import socket
        import threading
        client, server = socket.socketpair(); server.settimeout(2)
        errors = []; masks = []; atoms = {}; observer = None
        def exact(count):
            out = b''
            while len(out) < count:
                block = server.recv(count - len(out))
                if not block: raise EOFError
                out += block
            return out
        def peer():
            try:
                hello = exact(12); order = '<' if hello[0] == ord('l') else '>'
                n, d = struct.unpack_from(order + 'HH', hello, 6)
                exact((n + 3) // 4 * 4 + (d + 3) // 4 * 4)
                setup = struct.pack(order + 'BBHHHIIIIHHBBBBBBBB4x', 1, 0, 11, 0, 18,
                                    1, 0x200000, 0x1fffff, 0, 0, 65535, 1, 0, 0, 0, 32, 32, 8, 255)
                screen = struct.pack(order + 'IIIIIHHHHHHIBBBB', 1, 2, 0xffffff, 0, 0,
                                     1920, 1080, 500, 300, 1, 1, 3, 0, 0, 24, 0)
                os.write(server.fileno(), setup + screen); seq = 0
                while True:
                    h = exact(4); size = struct.unpack_from(order + 'H', h, 2)[0] * 4
                    data = h + exact(size - 4); seq += 1
                    if h[0] == 16:
                        length = struct.unpack_from(order + 'H', data, 4)[0]
                        name = data[8:8 + length]; atom = atoms.setdefault(name, 200 + len(atoms))
                        os.write(server.fileno(), struct.pack(order + 'BBHII20x', 1, 0, seq, 0, atom))
                    elif h[0] == 2:
                        masks.append(struct.unpack_from(order + 'I', data, 12)[0])
                    elif h[0] == 43:
                        os.write(server.fileno(), struct.pack(order + 'BBHII20x', 1, 0, seq, 0, 1))
                    elif h[0] == 20:
                        # A real GetProperty reply: CARDINAL/32, one uint32.
                        os.write(server.fileno(), struct.pack(order + 'BBHIIII12xI', 1, 32, seq, 1, 6, 0, 1, 98765))
                    else: raise AssertionError('Unexpected wire request')
            except EOFError: pass
            except Exception as exc: errors.append(repr(exc))
            finally: server.close()
        thread = threading.Thread(target=peer, daemon=True); thread.start()
        original = C.CDLL; native = original(C.util.find_library('xcb'))
        native.xcb_connect_to_fd.argtypes = [C.c_int, C.c_void_p]
        native.xcb_connect_to_fd.restype = C.c_void_p
        def connect(display, screen):
            C.cast(screen, C.POINTER(C.c_int))[0] = 0
            return native.xcb_connect_to_fd(client.detach(), None)
        # A callable object, so the implementation can set its ctypes signature.
        class Proxy:
            xcb_connect = staticmethod(connect)
            def __getattr__(self, name): return getattr(native, name)
        try:
            with patch.dict(os.environ, {'DISPLAY': ':99'}), \
                    patch.object(C, 'CDLL', side_effect=lambda name: original(None) if name is None else Proxy()):
                try: observer = m.X11(512)
                except m.Invalid as exc: raise AssertionError(errors) from exc
                self.assertEqual(observer.number(123, '_NET_WM_USER_TIME'), 98765)
            self.assertEqual(masks, [(1 << 19) | (1 << 22)])
        finally:
            if observer: observer.close()
            client.close(); thread.join(timeout=3)
        self.assertFalse(thread.is_alive()); self.assertEqual(errors, [])


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.p = Path(self.tmp.name); self.p.chmod(0o700)
        self.cfg = dict(run='a' * 32, maxCandidates=4)

    def tearDown(self): self.tmp.cleanup()

    def completed(self):
        ledger = m.Ledger(str(self.p), self.cfg)
        try:
            ledger.emit('ready', self.cfg)
            ledger.finish(dict(desktop_role='unproven'), 'requested')
        finally: ledger.close()

    def test_complete_receipt_does_not_claim_desktop_role(self):
        self.completed(); result = m.verify(str(self.p))
        self.assertTrue(result['transport_complete'])
        self.assertEqual(result['desktop_role'], 'unproven')
        self.assertEqual(stat_mode(self.p / 'x11-use.jsonl'), 0o600)

    def test_missing_end_or_receipt_is_not_success(self):
        ledger = m.Ledger(str(self.p), self.cfg)
        ledger.emit('ready', self.cfg); ledger.close()
        with self.assertRaises((m.Invalid, FileNotFoundError)): m.verify(str(self.p))

    def test_corruption_and_reordering_rejected(self):
        self.completed(); file = self.p / 'x11-use.jsonl'
        rows = file.read_bytes().splitlines(keepends=True); file.write_bytes(b''.join(reversed(rows)))
        with self.assertRaises(m.Invalid): m.verify(str(self.p))

    def test_no_overwrite_unsafe_modes_or_symlinks(self):
        self.completed()
        with self.assertRaises(FileExistsError): m.Ledger(str(self.p), self.cfg)
        link = self.p / 'link'; link.symlink_to(self.p, target_is_directory=True)
        with self.assertRaises((m.Invalid, OSError)): m.Ledger(str(link), self.cfg)
        self.p.chmod(0o755)
        with self.assertRaises(m.Invalid): m.verify(str(self.p))

    def test_write_or_fsync_failure_cannot_create_success_receipt(self):
        ledger = m.Ledger(str(self.p), self.cfg)
        try:
            with patch.object(m.os, 'fsync', side_effect=OSError('mock')):
                with self.assertRaises(OSError): ledger.emit('ready', self.cfg)
            self.assertFalse((self.p / 'x11-use-receipt.json').exists())
        finally: ledger.close()


class ServiceFixtureTests(unittest.TestCase):
    """Exercise the GLib/service boundary using no real bus or X connection."""
    def run_fixture(self, case):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory).chmod(0o700)
            self.service = None; self.periodic = None; self.signals = {}
            self.native = MagicMock(); self.native.atoms = dict(_NET_WM_USER_TIME=7, _NET_WM_NAME=8)
            self.native.clients.return_value = []
            self.native.events.return_value = []
            self.native.prop.side_effect = lambda xid, name, count: (8, 31, b'sdl-freerdp\0com.freerdp.client.sdl3\0') if name == 'WM_CLASS' else (8, 88, b'joetoo-rdp-proof-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')
            def number(xid, name):
                return {'_NET_WM_PID': 456, '_NET_WM_USER_TIME': self.timestamp,
                        '_NET_WM_USER_TIME_WINDOW': None}[name]
            self.timestamp = 100; self.native.number.side_effect = number
            self.bus = MagicMock(); self.bus.get_name_owner.return_value = ':1.10'
            self.bus.get_unix_user.return_value = 1000; self.bus.get_unique_name.return_value = ':1.20'
            outer = self
            class Object:
                def __init__(self, *args): outer.service = self
                def remove_from_connection(self): outer.removed = True
            class Loop:
                def run(self): outer.drive(case, directory)
                def quit(self): pass
            def timeout(ms, callback): self.periodic = callback; return 1
            service = types.ModuleType('dbus.service')
            service.Object = Object; service.method = lambda *a, **k: lambda f: f
            dbus = types.ModuleType('dbus'); dbus.service = service
            dbus.bus = types.SimpleNamespace(BusConnection=lambda address: self.bus)
            glib = types.SimpleNamespace(MainLoop=Loop, timeout_add=timeout,
                                         timeout_add_seconds=lambda *a: 2, source_remove=lambda *a: None)
            modules = {'dbus': dbus, 'dbus.service': service, 'dbus.mainloop': types.ModuleType('dbus.mainloop'),
                       'dbus.mainloop.glib': types.SimpleNamespace(DBusGMainLoop=lambda **k: None),
                       'gi': types.SimpleNamespace(repository=None),
                       'gi.repository': types.SimpleNamespace(GLib=glib)}
            args = types.SimpleNamespace(directory=directory, poll_ms=10, ack_ms=3000,
                                         seconds=30, max_candidates=4, max_clients=512, event_limit=64)
            with patch.dict('sys.modules', modules), patch.dict(os.environ, {'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/mock'}), \
                    patch.object(m.os, 'geteuid', return_value=1000), \
                    patch.object(m.os, 'fstat', side_effect=lambda fd: fake_stat(real_fstat(fd), 1000)), \
                    patch.object(m, 'X11', return_value=self.native), \
                    patch.object(m.signal, 'signal', side_effect=lambda sig, fn: self.signals.update({sig: fn})):
                rc = m.serve(args)
            # Files really belong to the fixture user; independent verification
            # runs outside the mocked UID context.
            result = m.verify(directory)
            self.assertTrue(self.removed); self.native.close.assert_called_once()
            self.bus.close.assert_called_once()
            records = [json.loads(line) for line in (Path(directory) / 'x11-use.jsonl').read_text().splitlines()]
            return rc, result, records

    def drive(self, case, directory):
        cfg = json.loads((Path(directory) / 'x11-use.jsonl').read_text().splitlines()[0])['body']
        def request(body): return json.dumps(dict(run=cfg['run'], body=body))
        if case == 'sender':
            with self.assertRaises(m.Invalid): self.service.Candidates(request(None), sender=':1.99')
            return
        if case == 'owner':
            self.bus.get_name_owner.return_value = ':1.11'
            self.assertFalse(self.periodic()); return
        self.native.clients.return_value = [123]
        self.assertTrue(self.periodic())
        self.service.Candidates(request(None), sender=':1.10')
        self.assertFalse((Path(directory) / 'linker-ready.json').exists())
        self.assertFalse(json.loads(self.service.Status(cfg['run'], sender=':1.30'))['ready'])
        self.service.Links(request([dict(xid=123, generation=1, pid=456, uuid=A)]), sender=':1.10')
        self.assertFalse((Path(directory) / 'linker-ready.json').exists())
        self.service.Candidates(request(None), sender=':1.10')
        self.assertTrue((Path(directory) / 'linker-ready.json').exists())
        self.assertTrue(json.loads(self.service.Status(cfg['run'], sender=':1.30'))['ready'])
        with self.assertRaises(m.Invalid): self.service.Status('wrong-run', sender=':1.30')
        self.bus.get_unix_user.return_value = 999
        with self.assertRaises(m.Invalid): self.service.Status(cfg['run'], sender=':1.30')
        self.bus.get_unix_user.return_value = 1000
        if case == 'lost':
            with patch.object(m.time, 'monotonic', return_value=time_monotonic() + 100):
                self.assertFalse(json.loads(self.service.Status(cfg['run'], sender=':1.30'))['ready'])
                self.assertFalse(self.periodic())
            return
        event = bytearray(32); event[0] = 28; struct.pack_into('=II', event, 4, 123, 7)
        self.timestamp = 101; self.native.events.return_value = [bytes(event)]
        self.assertTrue(self.periodic())
        self.timestamp = 102; self.assertTrue(self.periodic())
        # A latch switches the X11 connection to StructureNotify only.
        self.native.watch.assert_any_call(123, 1 << 17)
        self.signals[m.signal.SIGTERM](m.signal.SIGTERM, None)

    def test_persisted_ready_follows_round_trip_and_cleanup_preserves_latch(self):
        rc, result, records = self.run_fixture('normal')
        self.assertEqual(rc, 0); self.assertTrue(result['observation_completed_as_requested'])
        self.assertEqual([r['kind'] for r in records].count('use_latched'), 1)

    def test_wrong_sender_and_owner_replacement_fail_closed(self):
        for case in ['sender', 'owner']:
            with self.subTest(case=case):
                rc, result, records = self.run_fixture(case)
                self.assertEqual(rc, 1); self.assertFalse(result['observation_completed_as_requested'])

    def test_linker_loss_stops_observation_and_keeps_incomplete_evidence(self):
        rc, result, records = self.run_fixture('lost')
        self.assertEqual(rc, 1); self.assertEqual(result['reason'], 'observation_failed')
        self.assertTrue(result['transport_complete'])


class StatusClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name); self.p.chmod(0o700)
        self.cfg = dict(run='a'*32, maxCandidates=4, receiver=':1.20', kwin_owner=':1.10', ackMs=3000)
        ledger = m.Ledger(str(self.p), self.cfg)
        ledger.emit('ready', self.cfg); ledger.close()
        self.bus = MagicMock(); self.bus.get_name_owner.return_value = ':1.10'
        self.bus.get_unix_user.return_value = os.geteuid()
        self.reply = dict(run=self.cfg['run'], kwin_owner=':1.10', ready=True)
        self.bus.get_object.return_value.Status.side_effect = lambda *a, **k: json.dumps(self.reply)
        self.module = types.SimpleNamespace(bus=types.SimpleNamespace(BusConnection=lambda _: self.bus))

    def status(self):
        with patch.dict('sys.modules', {'dbus': self.module}), \
                patch.dict(os.environ, {'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/mock'}):
            return m.status(str(self.p))

    def test_current_unique_receiver_and_pinned_owner_are_required(self):
        self.assertTrue(self.status()['ready'])
        self.bus.get_object.assert_called_with(':1.20', '/org/joetoo/RDPX11Use', introspect=False)
        self.bus.get_name_owner.return_value = ':1.11'
        with self.assertRaises(m.Invalid): self.status()

    def test_stale_disk_readiness_cannot_override_live_status(self):
        (self.p/'linker-ready.json').write_text('{}')
        self.reply['ready'] = False
        self.assertFalse(self.status()['ready'])

    def test_wrong_receiver_uid_and_wrong_reply_run_are_rejected(self):
        self.bus.get_unix_user.return_value = os.geteuid()+1
        with self.assertRaises(m.Invalid): self.status()
        self.bus.get_unix_user.return_value = os.geteuid()
        self.reply['run'] = 'b'*32
        with self.assertRaises(m.Invalid): self.status()

    def test_status_rejects_symlink_and_insecure_evidence(self):
        (self.p/'x11-use.jsonl').chmod(0o644)
        with self.assertRaises(m.Invalid): self.status()


real_fstat = os.fstat
time_monotonic = m.time.monotonic


def fake_stat(st, uid):
    return types.SimpleNamespace(st_uid=uid, st_mode=st.st_mode)


def stat_mode(p): return p.stat().st_mode & 0o777


if __name__ == '__main__': unittest.main()
