# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline protocol/storage tests; no session bus, KWin or network connections."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import io
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'tools/joetoo-rdp-diagnostic-receiver.py'
spec = importlib.util.spec_from_file_location('rdp_diagnostic_receiver', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.directory = m.PrivateDirectory(self.path)
        self.config = m.settings(dict(receiverUniqueName=':1.99', runId='a'*32))
        self.directory.write_new('run.json', dict(settings=self.config, kwin_owner=':1.5'))
        self.r = m.Receiver(self.directory, self.config, ':1.5')
        self.n = 0
        self.observer = 'rdp-diag-test-1'

    def tearDown(self):
        self.r.close()
        self.directory.close()
        self.temp.cleanup()

    def packet(self, kind, **values):
        self.n += 1
        return dict(protocol=1, run_id=self.config['runId'], observer=self.observer,
                    transport_seq=self.n, kind=kind, **values)

    def append(self, r, sender=':1.5'):
        return self.r.request('Append', json.dumps(r), sender)

    def ready(self):
        r = self.packet('ready', settings=self.config, capabilities=dict(
            windowAdded='connected', windowRemoved='connected', timeout='connected'),
            wall_time_ms=1000, format_version=1)
        self.append(r)
        return r

    def probe(self, action):
        return self.r.request('Probe', json.dumps(dict(protocol=1, run_id=self.config['runId'],
                             observer=self.observer, action=action)), ':1.5')

    def event(self, i):
        return self.packet('event', seq=i, capture_seq=i, event='initial_active',
                           wall_time_ms=1000+i, clock_regressed=False,
                           observed_active=dict(state='ok', value=None), intent='unknown')

    def end(self, n, reason='requested'):
        return self.packet('end', records=n, captured=n, reason=reason,
                           truncated=reason == 'record_limit', buffered_records=n,
                           overflow=(dict(event='frameGeometryChanged', rejected_records=1,
                                          limit=self.config['maxRecords']) if reason == 'record_limit' else None),
                           callback_failures=0, cleanup_failures=0, output_failures=0,
                           delivery='pending acknowledgement and independent receipt verification',
                           unresolved_window_count=0, capture_intact=reason == 'requested',
                           capabilities={})

    def complete(self, count=1, reason='requested'):
        self.ready(); self.probe('observe'); self.probe('drain')
        for i in range(1, count+1):
            self.append(self.event(i))
        ack = self.append(self.end(count, reason))
        self.probe('delivered')
        return ack

    def test_ready_requires_persistence_then_explicit_observing_handshake(self):
        with patch.object(m.os, 'fsync', wraps=os.fsync) as synced:
            self.ready()
            self.assertGreaterEqual(synced.call_count, 1)
        self.assertTrue(self.r.status()['ready_persisted'])
        self.assertFalse(self.r.status()['native_launch_ready'])
        self.assertTrue(self.probe('observe')['native_launch_ready'])
        self.assertFalse(self.probe('drain')['native_launch_ready'])

    def test_receipt_independently_verifies_without_bus_dependencies(self):
        ack = self.complete()
        self.assertTrue(ack['transport_complete'])
        receipt = m.verify(self.directory)
        self.assertEqual(receipt['lifecycle_coverage'], 'unassessed')
        self.assertEqual(receipt['records'], 3)
        self.assertTrue(receipt['internal_capture_intact'])
        for name in ('evidence.jsonl', 'receipt.json', 'run.json'):
            self.assertEqual((self.path/name).stat().st_mode & 0o777, 0o600)

    def test_full_1024_record_buffer_persisted_and_verified(self):
        started = time.monotonic()
        self.complete(1024)
        receipt = m.verify(self.directory)
        self.assertEqual(receipt['records'], 1026)
        elapsed = time.monotonic()-started
        print(f'Full diagnostic fixture export: 1024 events, {elapsed:.3f}s (disposable storage)')
        self.assertLess(elapsed*1000, self.config['exportTimeoutMs'])

    def test_full_buffer_deadline_is_derived_and_short_overrides_rejected(self):
        self.assertEqual(self.config['exportTimeoutMs'], (1024+3)*3000)
        with self.assertRaises(m.Invalid):
            m.settings(dict(self.config, exportTimeoutMs=30000))

    def test_transport_complete_is_not_internal_or_native_lifecycle_complete(self):
        self.complete(1, 'record_limit')
        receipt = m.verify(self.directory)
        self.assertTrue(receipt['transport_complete'])
        self.assertFalse(receipt['internal_capture_intact'])
        self.assertEqual(receipt['lifecycle_coverage'], 'unassessed')

    def test_wrong_sender_does_not_write_or_poison_the_run(self):
        value = self.packet('ready')
        with self.assertRaises(m.Invalid):
            self.append(value, ':1.88')
        self.assertEqual(self.r.persisted_count, 0)
        self.assertIsNone(self.r.failure)
        self.n = 0
        self.ready()

    def test_replaced_kwin_owner_invalidates_readiness(self):
        self.ready(); self.probe('observe')
        with self.assertRaises(m.Invalid):
            self.r.check_owner(':1.6')
        self.assertEqual(self.r.failure, 'kwin_owner_changed')
        self.assertFalse(self.r.ready)

    def test_liveness_expiry_stops_readiness_and_preserves_partial(self):
        self.ready(); self.probe('observe')
        self.r.clock = lambda: self.r.last_seen + 12
        self.r.alive()
        self.assertEqual(self.r.failure, 'sender_liveness_expired')
        self.assertFalse(self.r.ready)
        self.assertTrue((self.path/'evidence.partial.jsonl').exists())
        self.assertFalse((self.path/'receipt.json').exists())

    def test_no_observe_after_drain(self):
        self.ready(); self.probe('drain')
        with self.assertRaises(m.Invalid):
            self.probe('observe')
        self.assertFalse(self.r.ready)

    def test_no_event_export_before_drain(self):
        self.ready(); self.probe('observe')
        with self.assertRaises(m.Invalid):
            self.append(self.event(1))
        self.assertFalse(self.r.ready)

    def test_duplicate_or_missing_transport_sequence_fails_closed(self):
        self.ready(); self.probe('drain')
        value = self.event(1)
        value['transport_seq'] = 1
        with self.assertRaises(m.Invalid):
            self.append(value)
        self.assertIsNotNone(self.r.failure)
        self.assertFalse(self.r.complete)

    def test_reordered_event_sequence_rejected(self):
        self.ready(); self.probe('drain')
        with self.assertRaises(m.Invalid):
            self.append(self.event(2))

    def test_changed_observer_rejected(self):
        self.ready(); self.probe('drain')
        value = self.event(1); value['observer'] = 'rdp-diag-other'
        with self.assertRaises(m.Invalid):
            self.append(value)

    def test_run_protocol_and_oversized_input_rejected(self):
        for text in ('{}', '{"protocol":2}', 'x'*11000):
            with self.subTest(text=text[:20]):
                with self.assertRaises(m.Invalid):
                    self.r.request('Append', text, ':1.5')
        self.assertEqual(self.r.persisted_count, 0)

    def test_duplicate_json_keys_nonfinite_and_malformed_json_rejected(self):
        for text in ('{"a":1,"a":2}', '{"x":NaN}', '{'):
            with self.assertRaises(m.Invalid):
                m.decode(text)

    def test_payload_schema_rejects_raw_captions_and_private_fields(self):
        self.ready(); self.probe('drain')
        value = self.event(1)
        value['window'] = dict(uuid='11111111-1111-4111-8111-111111111111', caption='secret')
        with self.assertRaises(m.Invalid):
            self.append(value)
        self.assertNotIn(b'secret', (self.path/'evidence.partial.jsonl').read_bytes())

    def test_ready_disk_write_failure_never_acknowledges_persistence(self):
        with patch.object(m, 'write_all', side_effect=OSError('disk full')):
            with self.assertRaises(m.Invalid):
                self.ready()
        self.assertFalse(self.r.status()['ready_persisted'])
        self.assertFalse(self.r.ready)
        self.assertFalse(self.r.complete)

    def test_ready_fsync_failure_never_acknowledges_persistence(self):
        with patch.object(m.os, 'fsync', side_effect=OSError('sync failed')):
            with self.assertRaises(m.Invalid):
                self.ready()
        self.assertFalse(self.r.status()['ready_persisted'])
        self.assertFalse(self.r.ready)

    def test_receipt_write_failure_retains_evidence_without_completion(self):
        self.ready(); self.probe('drain')
        original = self.directory.write_new
        def fail_receipt(name, value):
            if name == 'receipt.pending.json':
                raise PermissionError('denied')
            return original(name, value)
        with patch.object(self.directory, 'write_new', side_effect=fail_receipt):
            with self.assertRaises(m.Invalid):
                self.append(self.end(0))
        self.assertFalse(self.r.complete)
        self.assertTrue((self.path/'evidence.jsonl').exists())
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_interrupted_publication_preserves_payload_and_pending_receipt(self):
        self.ready(); self.probe('drain')
        original = self.directory.publish
        def fail_publish(old, new):
            if new == 'receipt.json':
                raise OSError('interrupted')
            return original(old, new)
        with patch.object(self.directory, 'publish', side_effect=fail_publish):
            with self.assertRaises(m.Invalid):
                self.append(self.end(0))
        self.assertFalse(self.r.complete)
        self.assertTrue((self.path/'evidence.jsonl').exists())
        self.assertTrue((self.path/'receipt.pending.json').exists())

    def test_receipt_sync_failure_is_not_complete(self):
        self.ready(); self.probe('drain')
        original = self.directory.publish
        def fail_after_publish(old, new):
            original(old, new)
            if new == 'receipt.json':
                raise OSError('directory sync failed')
        with patch.object(self.directory, 'publish', side_effect=fail_after_publish):
            with self.assertRaises(m.Invalid):
                self.append(self.end(0))
        self.assertFalse(self.r.complete)
        # Existing bytes can be inspected, but failure.json prevents acceptance.
        self.assertTrue((self.path/'failure.json').exists())
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_archive_file_corruption_fails_independent_hash_verification(self):
        self.complete()
        path = self.path/'evidence.jsonl'
        path.write_bytes(path.read_bytes().replace(b'1001', b'1002'))
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_mismatched_receipt_fails_independent_verification(self):
        self.complete()
        path = self.path/'receipt.json'
        data = json.loads(path.read_text()); data['records'] = 99
        path.write_text(json.dumps(data))
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_missing_end_or_ready_is_rejected(self):
        self.complete()
        path = self.path/'evidence.jsonl'
        original = path.read_bytes().splitlines(keepends=True)
        for lines in (original[1:], original[:-1]):
            path.write_bytes(b''.join(lines))
            with self.assertRaises(m.Invalid):
                m.verify(self.directory)

    def test_symlink_destination_and_existing_payload_not_overwritten(self):
        target = self.path/'other'; target.write_text('keep')
        (self.path/'unsafe').symlink_to(target)
        with self.assertRaises(OSError):
            self.directory.create('unsafe')
        with self.assertRaises(OSError):
            self.directory.create('evidence.partial.jsonl')
        self.assertEqual(target.read_text(), 'keep')

    def test_symlink_parent_relative_and_traversal_directories_rejected(self):
        for path in (Path('relative'), self.path/'..'/'anything'):
            with self.assertRaises(m.Invalid):
                m.PrivateDirectory(path)
        (self.path/'link').symlink_to(self.path, target_is_directory=True)
        with self.assertRaises(OSError):
            m.PrivateDirectory(self.path/'link')

    def test_directory_permissions_and_owner_checked(self):
        self.path.chmod(0o755)
        with self.assertRaises(m.Invalid):
            m.PrivateDirectory(self.path)
        self.path.chmod(0o700)
        real = os.fstat
        def wrong_owner(fd):
            values = list(real(fd)); values[4] = os.geteuid()+1
            return os.stat_result(values)
        with patch.object(m.os, 'fstat', side_effect=wrong_owner):
            with self.assertRaises(m.Invalid):
                m.PrivateDirectory(self.path)

    def test_unsafe_evidence_modes_and_symlinks_rejected(self):
        self.complete()
        path = self.path/'evidence.jsonl'
        path.chmod(0o644)
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)
        path.chmod(0o600)
        path.rename(self.path/'saved')
        path.symlink_to(self.path/'saved')
        with self.assertRaises(OSError):
            m.verify(self.directory)

    def test_permission_failure_on_exclusive_creation(self):
        with patch.object(m.os, 'open', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                self.directory.create('new')

    def test_zero_length_partial_write_is_bounded_failure(self):
        with patch.object(m.os, 'write', return_value=0):
            with self.assertRaises(m.Invalid):
                self.ready()
        self.assertFalse(self.r.complete)

    def test_no_reuse_or_second_observer_after_completion(self):
        self.complete()
        with self.assertRaises(m.Invalid):
            self.append(self.event(2))
        self.assertTrue(m.verify(self.directory)['transport_complete'])

    def test_actual_javascript_observer_envelopes_replay_through_persistence(self):
        output = self.path/'node-fixture.json'
        result = subprocess.run(['node', '--test', '--test-isolation=none',
                                 '--test-name-pattern=actual observer envelopes',
                                 str(SOURCE.parents[1]/'tests/test_rdp_window_diagnostic.js')],
                                env=dict(os.environ, JOETOO_DIAGNOSTIC_FIXTURE_OUTPUT=str(output)),
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr+result.stdout)
        records = json.loads(output.read_text())
        self.config = records[0]['settings']
        self.observer = records[0]['observer']
        for i, record in enumerate(records):
            if i == 1:
                self.probe('drain')
            self.append(record)
        self.probe('delivered')
        self.assertTrue(m.verify(self.directory)['transport_complete'])

    def test_end_persisted_without_sender_confirmation_is_not_a_complete_delivery(self):
        self.ready(); self.probe('drain'); self.append(self.end(0))
        self.assertTrue(self.r.complete)
        self.assertFalse(self.r.status()['sender_confirmed_end_ack'])
        with self.assertRaises(OSError):
            m.verify(self.directory)
        self.r.clock = lambda: self.r.last_seen + 12
        self.r.alive()
        self.assertIsNotNone(self.r.failure)

    def test_delivery_confirmation_write_failure_invalidates_completion(self):
        self.ready(); self.probe('drain'); self.append(self.end(0))
        original = self.directory.write_new
        def fail_confirmation(name, value):
            if name == 'delivery-ack.json':
                raise OSError('denied')
            return original(name, value)
        with patch.object(self.directory, 'write_new', side_effect=fail_confirmation):
            with self.assertRaises(m.Invalid):
                self.probe('delivered')
        self.assertFalse(self.r.sender_confirmed)
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_confirmation_receipt_tampering_rejected(self):
        self.complete()
        path = self.path/'delivery-ack.json'
        data = json.loads(path.read_text()); data['observer'] = 'rdp-diag-other'
        path.write_text(json.dumps(data))
        with self.assertRaises(m.Invalid):
            m.verify(self.directory)

    def test_source_schema_rejects_false_integrity_and_extra_ready_fields(self):
        ready = self.ready(); self.probe('drain')
        end = self.end(0, 'record_limit'); end['capture_intact'] = True
        with self.assertRaises(m.Invalid):
            self.append(end)
        fresh = m.Sequence(self.config)
        ready['caption'] = 'private'
        with self.assertRaises(m.Invalid):
            fresh.accept(ready)

    def test_server_refuses_autolaunch_or_network_bus(self):
        for address in ('', 'autolaunch:', 'tcp:host=example.invalid', 'unix:path=/x;autolaunch:'):
            with patch.dict(os.environ, {'DBUS_SESSION_BUS_ADDRESS': address}):
                with self.assertRaises(m.Invalid):
                    m.serve(types.SimpleNamespace())

    def test_service_wrapper_pins_bus_and_uid_without_native_execution(self):
        # Replace the complete D-Bus/GLib boundary; no connection is opened.
        objects = []
        state = dict(owner=':1.5', connected=[], closed=False)
        class Object:
            def __init__(obj, bus, path):
                objects.append(obj)
                self.assertEqual(path, m.OBJECT)
            def remove_from_connection(obj):
                state['removed'] = True
        class Bus:
            def get_name_owner(obj, name):
                self.assertEqual(name, 'org.kde.KWin')
                return state['owner']
            def get_unix_user(obj, sender):
                return os.geteuid() + (1 if sender == ':1.666' else 0)
            def get_unique_name(obj):
                return ':1.99'
            def close(obj):
                state['closed'] = True
        bus = Bus()
        dbus = types.ModuleType('dbus'); dbus.__path__ = []
        service = types.ModuleType('dbus.service')
        service.Object = Object
        service.method = lambda *a, **k: lambda f: f
        dbus.service = service
        def connect(address):
            state['connected'].append(address)
            return bus
        dbus.bus = types.SimpleNamespace(BusConnection=connect)
        mainloop = types.ModuleType('dbus.mainloop'); mainloop.__path__ = []
        glib = types.ModuleType('dbus.mainloop.glib'); glib.DBusGMainLoop = lambda **kw: None
        gi = types.ModuleType('gi'); gi.__path__ = []
        repository = types.ModuleType('gi.repository')
        class Loop:
            def run(obj):
                conf = json.loads((destination/'run.json').read_text())['settings']
                receiver = objects[0]
                value = dict(protocol=1, run_id=conf['runId'], observer=self.observer,
                             kind='ready', transport_seq=1, settings=conf,
                             capabilities=dict(windowAdded='connected', windowRemoved='connected', timeout='connected'),
                             wall_time_ms=1000, format_version=1)
                # Both same-UID unrelated and wrong-UID callers are rejected.
                for sender in (':1.88', ':1.666'):
                    self.assertFalse(json.loads(receiver.Append(json.dumps(value), sender=sender))['ok'])
                ack = json.loads(receiver.Append(json.dumps(value), sender=':1.5'))
                self.assertTrue(ack['persisted'])
                self.assertFalse(json.loads(receiver.Status(sender=':1.200'))['native_launch_ready'])
                probe = dict(protocol=1, run_id=conf['runId'], observer=self.observer, action='observe')
                self.assertTrue(json.loads(receiver.Probe(json.dumps(probe), sender=':1.5'))['native_launch_ready'])
                state['owner'] = ':1.6'
                self.assertFalse(json.loads(receiver.Probe(json.dumps(probe), sender=':1.5'))['ok'])
            def quit(obj):
                pass
        repository.GLib = types.SimpleNamespace(MainLoop=Loop, timeout_add=lambda *a: 1,
            unix_signal_add=lambda *a: 1, PRIORITY_DEFAULT=0)
        modules = {'dbus': dbus, 'dbus.service': service, 'dbus.mainloop': mainloop,
                   'dbus.mainloop.glib': glib, 'gi': gi, 'gi.repository': repository}
        destination = self.path/'server'; destination.mkdir(mode=0o700)
        args = types.SimpleNamespace(directory=str(destination), duration_seconds=2400,
                                     ack_ms=3000, liveness_ms=5000, max_records=1024, max_total_bytes=16777216, export_ms=0)
        with patch.dict('sys.modules', modules), patch.dict(os.environ,
                {'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/mock-session-bus'}), redirect_stdout(io.StringIO()):
            m.serve(args)
        self.assertEqual(state['connected'], ['unix:path=/mock-session-bus'])
        self.assertTrue(state['closed'] and state['removed'])
        self.assertEqual(json.loads((destination/'failure.json').read_text())['reason'], 'kwin_owner_changed')
        self.assertIn('2400000', (destination/'observer.js').read_text())

    def test_file_path_traversal_and_symlink_publication_rejected(self):
        for name in ('../outside', '/absolute', '.', '..', ''):
            with self.assertRaises(m.Invalid):
                self.directory.create(name)
        target = self.path/'target'; target.write_text('original'); target.chmod(0o600)
        (self.path/'link').symlink_to(target)
        with self.assertRaises(m.Invalid):
            self.directory.publish('link', 'published')
        self.assertFalse((self.path/'published').exists())
        self.assertEqual(target.read_text(), 'original')

    def test_cli_verification_is_offline_and_reports_separate_outcomes(self):
        self.complete()
        result = subprocess.run([sys.executable, str(SOURCE), 'verify', str(self.path)],
                                capture_output=True, text=True, timeout=10,
                                env=dict(os.environ, DBUS_SESSION_BUS_ADDRESS='autolaunch:'))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['transport_complete'])
        self.assertTrue(report['sender_confirmed_end_ack'])
        self.assertEqual(report['lifecycle_coverage'], 'unassessed')

    def test_cumulative_byte_and_record_limits_validated(self):
        for values in (dict(maxTotalBytes=1000), dict(maxTotalBytes=67108865),
                       dict(maxRecords=65536), dict(maxRecordBytes=1048576)):
            with self.assertRaises(m.Invalid):
                m.settings(dict(self.config, **values))
        self.ready(); self.probe('drain')
        huge = self.event(1)
        huge['scope'] = 'x' * 11000
        with self.assertRaises(m.Invalid):
            self.append(huge)
        self.assertEqual(self.r.persisted_count, 1)

    def test_all_original_fixture_files_untouched_except_private_evidence(self):
        unrelated = self.path/'unrelated'; unrelated.write_bytes(b'original')
        before = unrelated.stat()
        self.complete()
        self.assertEqual(unrelated.read_bytes(), b'original')
        self.assertEqual(unrelated.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(unrelated.stat().st_mode, before.st_mode)


if __name__ == '__main__':
    unittest.main()
