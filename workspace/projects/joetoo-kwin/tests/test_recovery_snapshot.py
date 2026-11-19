# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Production persistence/broker/planner with disposable files and fake bus only."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_step1_4b_broker as baseline
from test_step1_3a import observation, WINDOW_ID, load_broker_without_real_dbus
from test_step1_5a_plan import PlannerHarness, ROOT
sys.path.insert(0, str(ROOT / 'libexec'))
from joetoo_kwin_persistence import (SETTING_NAMES, atomic_private, read_private, intent,
    snapshot_text, snapshot_read, save_snapshot, snapshot_path, runtime_path)
from joetoo_kwin_recovery import Recovery


def policy():
    script = 'TRUE=0; source "$1"; plan_defaults; screen_width=1920; screen_height=1080; shift; for k; do printf "%s\\0" "${!k}"; done'
    raw = subprocess.check_output(['bash', '-c', script, 'test', str(ROOT / 'libexec/joetoo-kwin-plan-functions'), *SETTING_NAMES])
    return dict(zip(SETTING_NAMES, raw.decode().split('\0')[:-1]))


def recipe(program='konsole', mode='ssh', target='user@host.example', slot=1):
    return dict(desktop=3, slot=slot, program=program, mode=mode, target=target, layer='over', settings=policy())


class FD:
    def __init__(self): self.fd = os.pidfd_open(os.getpid())
    def take(self):
        fd, self.fd = self.fd, None
        return fd


class Bus:
    def __init__(self):
        self.owner = ':1.2'
        self.bus_id = 'same-test-session'
        self.windows = {}
        self.hold = False
        self.pending = []
        self.foreign = False
        self.fd_available = True
        self.calls = []
        self.operations = []
    def get_object(self, name, path, **kw):
        self.calls.append((name, path))
        if name not in ('org.freedesktop.DBus', self.owner):
            raise ValueError('must use pinned native unique owner')
        return self
    def GetId(self, **kw): return self.bus_id
    def GetNameOwner(self, name, **kw):
        if 'reply_handler' in kw: kw['reply_handler'](self.owner)
        else: return self.owner
    def GetConnectionCredentials(self, sender, **kw):
        c = dict(ProcessID=os.getpid(), UnixUserID=os.geteuid() + int(self.foreign))
        if self.fd_available: c['ProcessFD'] = FD()
        if 'reply_handler' in kw: kw['reply_handler'](c)
        else: return c
    def add_signal_receiver(self, *args, **kwargs): return object()
    def Inspect(self, uuid, **kw):
        self.operations.append(('Inspect', uuid))
        raw = json.dumps(self.windows.get(uuid, dict(state='missing', uuid=uuid)))
        if 'reply_handler' in kw:
            if self.hold: self.pending.append((kw['reply_handler'], raw))
            else: kw['reply_handler'](raw)
        else: return raw
    def Close(self, token, uuid, pid, app_class, *args, **kw):
        self.operations.append(('Close', uuid))
        proof = self.windows.pop(uuid)
        assert proof['pid'] == pid and proof['class'] == app_class
        kw['reply_handler'](json.dumps(dict(state='closed', token=token, uuid=uuid, gone=True, helper_reaped=True)))


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name); self.folder.chmod(0o700)
        self.path = self.folder / 'managed-windows.json'
        self.base = baseline.BrokerRegistryIntegrationTests(); self.base.setUp(); self.addCleanup(self.base.doCleanups)
        self.base.sync(); rid = self.base.arm(); self.base.event('added'); self.base.finish_match(rid)
        self.b = self.base.broker
        self.r = self.b.registry.managed_windows[WINDOW_ID]
        self.r.restore_intent = recipe()
        self.b.registry.set_placement(WINDOW_ID, 'pending'); self.b.registry.set_placement(WINDOW_ID, 'succeeded')
        self.bus = Bus()
        self.bus.windows[WINDOW_ID] = dict(state='present', closeable=True, uuid=WINDOW_ID, pid=42, **{'class': 'konsole'}, backend='wayland')
        self.timers = []
        class GLib:
            timeout_add = lambda _, ms, fn: self.timers.append(fn) or len(self.timers)
        self.glib = GLib()
        self.identities = []
        self.recovery = self.attach(self.b)
        self.recovery.inventory(self.bus.owner)
    def attach(self, broker):
        rec = Recovery(broker, self.bus, lambda obj, iface: obj, self.path, self.glib)
        broker._recovery = rec
        self.identities.append(rec)
        self.addCleanup(lambda: rec.identity.close() if rec.identity else None)
        return rec
    def fresh(self):
        b = self.base.module.Broker(object())
        recovery = self.attach(b)
        return b, recovery
    def sync(self, b, source='reloaded-resident', sender=':1.2', windows=None):
        data = dict(source=source, revision=1, windows=windows if windows is not None else [self.base.window()], initial_layout_protocol=1)
        b.SyncInventory(json.dumps(data), sender=sender)
    def test_same_session_restart_preserves_exact_identity_and_new_alias_counter(self):
        for backend in ('wayland', 'x11'):
            with self.subTest(backend=backend):
                self.bus.windows[WINDOW_ID]['backend'] = backend
                b, recovery = self.fresh()
                self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
                self.sync(b)
                record = b.registry.get_window('win-001')
                self.assertEqual(record.presence, 'present')
                self.assertEqual(record.window_uuid, WINDOW_ID)
                self.assertEqual(record.restore_intent, recipe())
                self.assertEqual(b.registry._next_managed_number, 2)
                self.assertEqual(recovery.state, 'ready')
                self.assertEqual(b.registry.requests[record.request_id].state, 'succeeded')
                self.assertIsNone(b.request)
                self.assertEqual(b._sdl_registered, {})
                self.assertTrue(all(method == 'Inspect' for method, _ in self.bus.operations))
    def test_missing_processfd_never_establishes_compositor_authentication(self):
        b, recovery = self.fresh(); self.bus.fd_available = False
        self.sync(b)
        self.assertFalse(b.observation_synced)
        self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')

    def test_revision_gap_requires_fresh_authenticated_full_inventory(self):
        message = dict(source=self.b.observation_source, revision=self.b.observation_revision + 2,
                       event='changed', window=self.base.window())
        self.b.ObserveWindow(json.dumps(message), sender=self.bus.owner)
        self.assertEqual(self.recovery.state, 'awaiting_authenticated_inventory')
        self.assertEqual(self.r.presence, 'uncertain')
        with self.assertRaises(ValueError): self.recovery.guard()
        self.sync(self.b)
        self.assertEqual(self.r.presence, 'present')
        self.assertEqual(self.recovery.state, 'ready')

    def test_recovered_record_uses_existing_close_preview_and_retention_rules(self):
        b, recovery = self.fresh(); self.sync(b)
        b._sdl_bus_connection = lambda: self.bus
        self.base.module.dbus.Interface = lambda obj, iface: obj
        self.base.module.GLib.timeout_add = self.glib.timeout_add
        replies, errors = [], []
        request = dict(protocol=1, scope='one', managed_id='win-001', settings={})
        b.PrepareManagedClose(json.dumps(request), sender=':1.operator', reply=replies.append, error=errors.append)
        self.assertEqual(errors, [])
        result = json.loads(replies[0])
        self.assertEqual(result['state'], 'prepared')
        self.assertEqual(result['targets'][0]['window_uuid'], WINDOW_ID)
        self.assertTrue(result['registration_retained'])
        b._managed_close.release(b._managed_close.job)

    def test_sweep_after_recovery_updates_checkpoint_but_never_erases_last_good(self):
        saved = self.folder / 'last-session.conf'
        text = snapshot_text(dict(protocol=1, entries=[recipe()]))
        atomic_private(saved, text)
        b, recovery = self.fresh(); self.sync(b)
        b._sdl_bus_connection = lambda: self.bus
        self.base.module.dbus.Interface = lambda obj, iface: obj
        self.base.module.GLib.timeout_add = self.glib.timeout_add
        replies, errors = [], []
        b.PrepareManagedClose(json.dumps(dict(protocol=1, scope='all', managed_id='', settings={})),
                              sender=':1.operator', reply=replies.append, error=errors.append)
        request_id = json.loads(replies[-1])['request_id']
        b.CommitManagedClose(request_id, sender=':1.operator', reply=replies.append, error=errors.append)
        self.assertEqual(errors, [])
        self.assertEqual(json.loads(replies[-1])['state'], 'succeeded')
        self.assertEqual(json.loads(b.ListManaged()), dict(count=0, windows=[]))
        self.assertEqual(json.loads(read_private(self.path))['records'], [])
        self.assertEqual(read_private(saved), text)
        b2, recovery2 = self.fresh()
        self.assertEqual(b2.registry._next_managed_number, 2)

    def test_untrusted_sender_does_not_replace_inventory_or_recover(self):
        b, recovery = self.fresh(); self.sync(b, sender=':1.foreign')
        self.assertFalse(b.observation_synced)
        self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
        with self.assertRaises(ValueError): recovery.guard()
    def test_changed_compositor_or_bus_retains_only_uncertain_reservations(self):
        for change in ('owner', 'bus_id'):
            b, recovery = self.fresh()
            old = getattr(self.bus, change); setattr(self.bus, change, old + '-changed')
            self.sync(b, sender=self.bus.owner)
            self.assertEqual(recovery.state, 'different_compositor_session')
            self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
            with self.assertRaises(ValueError): recovery.guard()
            setattr(self.bus, change, old)
    def test_legitimate_resident_reload_is_not_a_new_compositor(self):
        self.sync(self.b, source='resident-after-reload')
        self.assertEqual(self.r.presence, 'present')
        self.assertEqual(self.recovery.state, 'ready')
        self.assertEqual(self.b.observation_source, 'resident-after-reload')
    def test_missing_wrong_uuid_pid_or_class_is_not_adopted(self):
        good = dict(self.bus.windows[WINDOW_ID])
        for field, value in [('uuid', '11111111-1111-4111-8111-111111111111'), ('pid', 99), ('class', 'foreign')]:
            self.bus.windows[WINDOW_ID] = dict(good, **{field: value})
            b, recovery = self.fresh(); self.sync(b)
            self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
        self.bus.windows.clear()
        b, recovery = self.fresh(); self.sync(b, windows=[])
        self.assertEqual(b.registry.get_window('win-001').presence, 'missing')
        self.assertEqual(b.registry.get_window('win-001').recipe['slot'], 1)
    def test_missing_checkpoint_record_does_not_regain_live_authority(self):
        self.r.presence = 'missing'; self.recovery.changed()
        b, recovery = self.fresh(); self.sync(b)
        self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
    def test_delayed_native_reply_after_deadline_cannot_revive_identity(self):
        self.bus.hold = True
        b, recovery = self.fresh(); self.sync(b)
        self.assertEqual(recovery.state, 'reconciling')
        self.timers[-1]()
        self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
        for cb, raw in self.bus.pending: cb(raw)
        self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
    def test_owner_loss_during_native_reply_or_expiry_cannot_be_reported_ready(self):
        for boundary in ('reply', 'expiry'):
            with self.subTest(boundary=boundary):
                self.bus.hold = True
                b, recovery = self.fresh(); self.sync(b)
                self.bus.owner = ':1.replacement'
                if boundary == 'reply':
                    cb, raw = self.bus.pending[-1]; cb(raw)
                else:
                    self.timers[-1]()
                self.assertEqual(recovery.state, 'different_compositor_session')
                self.assertEqual(b.registry.get_window('win-001').presence, 'uncertain')
                self.bus.owner = ':1.2'

    def test_corrupt_incomplete_bad_permissions_or_duplicate_checkpoint_blocks(self):
        good = self.path.read_text()
        cases = ['{}', '{bad', good.replace('"protocol": 1', '"protocol": 999')]
        data = json.loads(good); data['records'].append(data['records'][0]); cases.append(json.dumps(data))
        data = json.loads(good); data['records'][0]['managed_id'] = 'win-1'; cases.append(json.dumps(data))
        for text in cases:
            self.path.write_text(text); b, recovery = self.fresh()
            self.assertEqual(recovery.state, 'checkpoint_invalid')
            with self.assertRaises(self.base.module.dbus.DBusException): b.ListManaged()
            with self.assertRaises(ValueError): recovery.guard()
        self.path.write_text(good); self.path.chmod(0o644)
        b, recovery = self.fresh(); self.assertEqual(recovery.state, 'checkpoint_invalid')
    def test_checkpoint_write_failure_preserves_memory_and_blocks_followup(self):
        self.b.registry._next_managed_number += 1
        with patch('joetoo_kwin_recovery.atomic_private', side_effect=OSError('disk failure')):
            self.recovery.changed()
        self.assertEqual(self.recovery.state, 'checkpoint_write_failed')
        self.assertIn(WINDOW_ID, self.b.registry.managed_windows)
        with self.assertRaises(ValueError): self.recovery.guard()
    def test_new_registration_is_not_published_when_checkpoint_write_fails(self):
        second = '11111111-1111-4111-8111-111111111111'
        registry = self.b.registry
        registry.begin_launch('second-launch', source=self.b.observation_source, synchronized=True,
                              baseline=[WINDOW_ID], recipe=dict(desktop=3, slot=2, program='konsole'))
        registry.mark_running('second-launch', 99)
        correlation = dict(state='MATCHED', request_id='second-launch', evidence='pid',
                           candidate_history_complete=True, pid=99, window_uuid=second)
        observed = dict(uuid=second, pid=99, resource_class='konsole')
        with patch('joetoo_kwin_recovery.atomic_private', side_effect=OSError('disk full')):
            with self.assertRaises(self.base.module.RegistryError):
                registry.register_match('second-launch', correlation, current_windows={second: observed},
                                        source=self.b.observation_source, synchronized=True)
        self.assertEqual(set(registry.managed_windows), {WINDOW_ID})
        self.assertEqual(registry._next_managed_number, 2)
        self.assertEqual(json.loads(read_private(self.path))['next_id'], 2)
        self.assertEqual(self.recovery.state, 'checkpoint_write_failed')

    def test_export_exact_native_proof_and_no_runtime_identity_or_caption(self):
        text = self.recovery.export(':1.operator')
        self.assertIn('3|konsole|ssh|user@host.example|over', text)
        for forbidden in (WINDOW_ID, self.r.request_id, 'win-001', 'ProcessFD', 'caption', 'pid='):
            self.assertNotIn(forbidden, text)
        self.r.observation['geometry']['x'] = 777
        self.assertEqual(self.recovery.export(':1.operator'), text)
    def test_export_rejects_empty_partial_missing_uncertain_or_incomplete_metadata(self):
        for attr, value in [('presence', 'missing'), ('presence', 'uncertain'), ('placement', 'failed'), ('restore_intent', None)]:
            before = getattr(self.r, attr); setattr(self.r, attr, value)
            with self.assertRaises(ValueError): self.recovery.export(':1.operator')
            setattr(self.r, attr, before)
        self.b.registry.managed_windows.clear()
        with self.assertRaises(ValueError): self.recovery.export(':1.operator')
    def test_export_rejects_foreign_operator_and_native_mismatch(self):
        self.bus.foreign = True
        with self.assertRaises(PermissionError): self.recovery.export(':1.operator')
        self.bus.foreign = False; self.bus.windows[WINDOW_ID]['pid'] = 99
        with self.assertRaises(ValueError): self.recovery.export(':1.operator')


class LaunchIntentTests(unittest.TestCase):
    def setUp(self):
        self.base = baseline.BrokerRegistryIntegrationTests(); self.base.setUp()
        self.addCleanup(self.base.doCleanups); self.base.sync()
        self.b = self.base.broker
    def test_additive_launch_captures_complete_original_recipe_without_granting_ownership(self):
        payload = dict(intent=recipe(), frame=[10, 20, 800, 600])
        ids = json.loads(self.b.SubmitManagedLaunchIntent(json.dumps(payload)))
        rid = ids['registration_request_id']
        self.assertFalse(self.b.registry.managed_windows)
        self.b.SetManagedLaunchPid(rid, 42); self.base.event('added'); self.base.finish_match(rid)
        record = self.b.registry.get_window('win-001')
        self.assertEqual(record.restore_intent, recipe())
        for key in ('desktop', 'slot', 'program', 'mode', 'target', 'layer'):
            self.assertEqual(record.recipe[key], recipe()[key])
    def test_invalid_metadata_rejected_before_transaction_or_registration(self):
        bad = recipe('sdl-freerdp', 'rdp', 'rdp://joe:password@host')
        with self.assertRaises(self.base.module.dbus.DBusException):
            self.b.SubmitManagedLaunchIntent(json.dumps(dict(intent=bad, frame=[10, 20, 800, 600])))
        self.assertIsNone(self.b.request); self.assertFalse(self.b.registry.requests)
    def test_sdl_authenticated_begin_keeps_complete_recipe_through_real_pidfd_registration(self):
        from test_rdp_broker import SdlInterfaceTests
        f = SdlInterfaceTests(); f.setUp(); self.addCleanup(f.doCleanups)
        metadata = recipe('sdl-freerdp', 'rdp', 'rdp://user@host.example:3389')
        f.begin(payload=json.dumps(dict(protocol=1, desktop=3, slot=1, bounds={}, intent=metadata)))
        self.assertFalse(f.errors)
        f.spawn(); f.bind(); f.event()
        self.assertEqual(f.poll()['state'], 'registered')
        self.assertEqual(f.b.registry.get_window('win-001').restore_intent, metadata)

    def test_vnc_positive_viewer_selection_keeps_original_remote_recipe(self):
        from test_vnc_broker import ViewerBrokerTests, FakeObserver
        f = ViewerBrokerTests(); f.setUp(); self.addCleanup(f.doCleanups)
        f.b.CancelManagedViewerLaunch(f.rid)
        f.observer = FakeObserver(); f.module.DesktopObserver = lambda bounds: f.observer
        metadata = recipe('vncviewer', 'ssh', 'ssh://user@host.example/display/2')
        ids = json.loads(f.b.SubmitManagedViewerLaunch(json.dumps(dict(f.spec, intent=metadata))))
        f.rid = ids['registration_request_id']; f.b.SetManagedLaunchPid(f.rid, 42)
        f.add(); f.observer.events = [('desktop', 123)]
        f.resolve(); f.now += .6; f.resolve()
        self.assertEqual(f.b.registry.get_window('win-001').restore_intent, metadata)

    def test_configured_rdp_job_validates_intent_target_and_destination_binding(self):
        from test_rdp_configured import job, rdp
        data = job(); metadata = recipe('sdl-freerdp', 'rdp', data['target'])
        metadata['desktop'] = data['desktop']
        self.assertEqual(rdp.configured_job(dict(data, intent=metadata))['intent'], metadata)
        metadata['target'] = 'rdp://other@host.example'
        with self.assertRaises(rdp.ConfiguredError): rdp.configured_job(dict(data, intent=metadata))

    def test_legacy_launch_still_valid_without_fabricated_restore_metadata(self):
        ids = json.loads(self.b.SubmitManagedLaunch('konsole', 3, 1, 10, 20, 800, 600))
        rid = ids['registration_request_id']; self.b.SetManagedLaunchPid(rid, 42)
        self.base.event('added'); self.base.finish_match(rid)
        self.assertIsNone(self.b.registry.get_window('win-001').restore_intent)


class SnapshotTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.path = self.folder / 'state' / 'last-session.conf'
        self.data = dict(protocol=1, entries=[recipe()])
    def test_atomic_valid_snapshot_and_actual_offline_planner(self):
        text = snapshot_text(self.data)
        save_snapshot(text, self.client, self.path)
        self.assertEqual(snapshot_read(self.path), text)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertFalse(self.calls.exists())
        self.assertFalse(list(self.path.parent.glob('.validate-*')))
    def test_bad_plan_does_not_overwrite_last_good(self):
        good = snapshot_text(self.data); save_snapshot(good, self.client, self.path)
        invalid = json.loads(json.dumps(self.data)); invalid['entries'][0]['settings']['terminal_width_percent'] = '999'
        with self.assertRaises(ValueError): save_snapshot(snapshot_text(invalid), self.client, self.path)
        self.assertEqual(snapshot_read(self.path), good)
        with self.assertRaises(ValueError): snapshot_text(dict(protocol=1, entries=[]))
    def test_failed_atomic_replace_preserves_prior_bytes_and_cleans_temporary(self):
        good = snapshot_text(self.data); atomic_private(self.path, good)
        with patch('joetoo_kwin_persistence.os.replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError): atomic_private(self.path, good + '# newer\n')
        self.assertEqual(read_private(self.path), good)
        self.assertFalse(list(self.path.parent.glob('.pending-*')))

    def test_original_explicit_frame_override_validates_but_manual_geometry_is_not_captured(self):
        data = json.loads(json.dumps(self.data))
        data['entries'][0]['frame_override'] = '10|20|800|600'
        text = snapshot_text(data); save_snapshot(text, self.client, self.path)
        self.assertIn("desktop_session_frames=(", text)
        self.assertIn('10|20|800|600', text)
        data['entries'][0]['frame_override'] = '1900|20|800|600'
        with self.assertRaises(ValueError): save_snapshot(snapshot_text(data), self.client, self.path)
        self.assertEqual(snapshot_read(self.path), text)

    def test_tampering_and_arbitrary_bash_are_never_sourced(self):
        text = snapshot_text(self.data); atomic_private(self.path, text + 'touch /tmp/unsafe\n')
        with self.assertRaises(ValueError): snapshot_read(self.path)
        with self.assertRaises(ValueError): save_snapshot(text + 'echo unsafe\n', self.client, self.path)
    def test_secret_targets_unknown_variables_and_recipe_fields_rejected(self):
        for bad in [recipe('sdl-freerdp', 'rdp', 'rdp://joe:password@host'),
                    recipe('vncviewer', 'ssh', 'ssh://joe:password@host/display/1')]:
            with self.assertRaises(ValueError): intent(bad)
        bad = recipe(); bad['settings']['password'] = 'secret'
        with self.assertRaises(ValueError): intent(bad)
        bad = recipe(); bad['settings']['screen_width'] = '$(secret)'
        with self.assertRaises(ValueError): intent(bad)
    def test_original_slot_order_preserved_without_runtime_ids(self):
        first = recipe(slot=5); second = recipe(slot=2)
        second['target'] = 'other.example'
        text = snapshot_text(dict(protocol=1, entries=[first, second]))
        self.assertLess(text.index('3|konsole|ssh|other.example|over'), text.index('3|konsole|ssh|user@host.example|over'))
        self.assertIn('desktop_session_frames=()', text)
    def test_mixed_effective_policy_refused_instead_of_silently_changed(self):
        first = recipe(); second = recipe(slot=2); second['settings']['terminal_width_percent'] = '75'
        with self.assertRaises(ValueError): snapshot_text(dict(protocol=1, entries=[first, second]))
    def test_private_file_symlink_and_permissions_rejected(self):
        atomic_private(self.path, snapshot_text(self.data)); self.path.chmod(0o644)
        with self.assertRaises(ValueError): read_private(self.path)
        self.path.unlink(); target = self.folder / 'target'; target.write_text('unrelated')
        self.path.symlink_to(target)
        with self.assertRaises(OSError): read_private(self.path)
        with self.assertRaises(ValueError): atomic_private(self.path, 'no')
        self.assertEqual(target.read_text(), 'unrelated')



class SnapshotCliTests(unittest.TestCase):
    def setUp(self):
        import test_step1_5c_launch as configured
        self.fixture = configured.ConfiguredLaunchTests()
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.client, self.env, self.calls = self.fixture.client, self.fixture.env, self.fixture.calls
        self.env['XDG_STATE_HOME'] = str(self.fixture.folder / 'state')
        self.env['SNAPSHOT_TEXT'] = snapshot_text(dict(protocol=1, entries=[recipe()]))
        text = self.client.read_text().replace('    *.RegistryStatus)', '    *.ExportManagedSnapshot) printf "%s" "$SNAPSHOT_TEXT" ;;\n    *.RegistryStatus)')
        self.client.write_text(text)
        self.path = Path(self.env['XDG_STATE_HOME']) / 'joetoo-kwin/last-session.conf'
    def run_cli(self, *args):
        return subprocess.run(['bash', str(self.client), *args], env=self.env, capture_output=True, text=True, timeout=15)
    def test_save_validates_and_advances_explicitly_without_confirmation_or_launch(self):
        run = self.run_cli('-S'); self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(snapshot_read(self.path), self.env['SNAPSHOT_TEXT'])
        self.assertFalse(self.calls.exists())
    def test_restore_uses_real_open_plan_confirmation_and_new_launch(self):
        atomic_private(self.path, self.env['SNAPSHOT_TEXT'])
        run = self.run_cli('-r'); self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        trace = self.calls.read_text()
        self.assertEqual(trace.count('confirm'), 1)
        self.assertIn('launch:1:3', trace)
        self.assertEqual(snapshot_read(self.path), self.env['SNAPSHOT_TEXT'])
        runtime = Path(self.env['XDG_RUNTIME_DIR'])
        self.assertFalse(list(runtime.glob('joetoo-restore.*.conf')))
    def test_restore_decline_or_reserved_slot_creates_no_window(self):
        atomic_private(self.path, self.env['SNAPSHOT_TEXT'])
        self.env['CANCEL'] = 'yes'
        run = self.run_cli('-r'); self.assertNotEqual(run.returncode, 0)
        self.assertNotIn('launch:', self.calls.read_text())
        del self.env['CANCEL']; self.calls.unlink()
        self.env['MANAGED'] = json.dumps(dict(windows=[dict(managed_id='win-050', presence='missing', intended=dict(desktop=3, slot=1))]))
        run = self.run_cli('-r'); self.assertNotEqual(run.returncode, 0)
        self.assertFalse(self.calls.exists())
    def test_unused_legacy_policy_does_not_prevent_local_launch_without_export_claim(self):
        self.fixture.write_config(['3|konsole|local|btop|over'], extra='rdp_security_protocol=unused_legacy_value')
        run = self.run_cli('-o', '-f', str(self.fixture.config))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn('cannot be faithfully exported', run.stdout + run.stderr)
        self.assertIn('launch:1:3', self.calls.read_text())

    def test_restore_bad_file_is_not_executed(self):
        atomic_private(self.path, 'touch "$TRACE"\n')
        run = self.run_cli('-r'); self.assertNotEqual(run.returncode, 0)
        self.assertFalse(self.calls.exists())


if __name__ == "__main__": unittest.main()
