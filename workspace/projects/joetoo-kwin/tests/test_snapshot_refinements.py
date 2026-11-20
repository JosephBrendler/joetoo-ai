# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Private timestamp history and historical observations; no native/bus traffic."""
import fcntl
import json
import os
from pathlib import Path
import stat
import unittest
from unittest.mock import patch
from test_step1_5a_plan import PlannerHarness
import test_recovery_snapshot as fixtures
from joetoo_kwin_persistence import (HISTORY_PATTERN, atomic_private, read_private,
    render_snapshot, snapshot_text, snapshot_read, save_snapshot)


class SnapshotHistoryTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.path = self.folder / 'state/last-session.conf'
        self.data = dict(protocol=1, entries=[fixtures.recipe()])
        self.text = snapshot_text(self.data)
    def save(self, depth=10): return save_snapshot(self.text, self.client, self.path, depth)
    def history(self): return sorted(self.path.parent.glob('snapshot-*.conf'))
    def test_identical_saves_and_timestamp_entropy_collisions_remain_unique_sorted(self):
        with patch('joetoo_kwin_persistence.time.time_ns', return_value=1795104000000000000), \
             patch('joetoo_kwin_persistence.os.urandom', side_effect=lambda n: b'x' * n):
            for _ in range(3): self.save()
        names = self.history()
        self.assertEqual(len(names), 3)
        self.assertEqual(len({p.name for p in names}), 3)
        self.assertEqual(os.readlink(self.path), names[-1].name)
        self.assertTrue(all(HISTORY_PATTERN.fullmatch(p.name) for p in names))
        self.assertTrue(all(read_private(p) == self.text for p in names))
        self.assertTrue(all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in names))
        self.assertEqual(self.path.parent.stat().st_mode & 0o777, 0o700)
        self.assertFalse(Path(os.readlink(self.path)).is_absolute())
    def test_clock_backwards_still_selects_newest_and_depth_prunes_only_after_success(self):
        self.save()
        with patch('joetoo_kwin_persistence.time.time_ns', return_value=1):
            for _ in range(3): self.save(depth=2)
        self.assertEqual(len(self.history()), 2)
        self.assertEqual(os.readlink(self.path), self.history()[-1].name)
        self.assertEqual(snapshot_read(self.path), self.text)
    def test_invalid_save_preserves_pointer_history_and_does_not_prune(self):
        for _ in range(3): self.save()
        before = (os.readlink(self.path), [p.name for p in self.history()])
        bad = json.loads(json.dumps(self.data)); bad['entries'][0]['settings']['terminal_width_percent'] = '999'
        with self.assertRaises(ValueError): save_snapshot(snapshot_text(bad), self.client, self.path, 1)
        self.assertEqual((os.readlink(self.path), [p.name for p in self.history()]), before)
        self.assertFalse(list(self.path.parent.glob('.validate-*')))
    def test_failed_atomic_pointer_swap_preserves_previous_history_without_orphans(self):
        for _ in range(2): self.save()
        before = (os.readlink(self.path), [p.name for p in self.history()])
        with patch('joetoo_kwin_persistence.os.replace', side_effect=OSError('swap failure')):
            with self.assertRaises(OSError): self.save(depth=1)
        self.assertEqual((os.readlink(self.path), [p.name for p in self.history()]), before)
        self.assertFalse(list(self.path.parent.glob('.latest-*')))
    def test_valid_legacy_regular_snapshot_is_preserved_and_v1_restores_without_rewrite(self):
        legacy = render_snapshot(self.data, legacy=True)
        atomic_private(self.path, legacy)
        self.assertEqual(snapshot_read(self.path), self.text)
        self.assertEqual(read_private(self.path), legacy)
        result = self.save()
        self.assertTrue(result['migrated_legacy'])
        self.assertEqual(len(self.history()), 2)
        self.assertIn(legacy, [read_private(p) for p in self.history()])
        self.assertTrue(self.path.is_symlink())
        self.assertEqual(snapshot_read(self.path), self.text)
    def test_failed_legacy_migration_never_loses_regular_last_good(self):
        legacy = render_snapshot(self.data, legacy=True); atomic_private(self.path, legacy)
        with patch('joetoo_kwin_persistence.os.replace', side_effect=OSError('swap failure')):
            with self.assertRaises(OSError): self.save()
        self.assertFalse(self.path.is_symlink()); self.assertEqual(read_private(self.path), legacy)
        self.assertEqual(self.history(), [])
    def test_depth_one_and_invalid_depth_bounds(self):
        for _ in range(3): self.save(depth=1)
        self.assertEqual(len(self.history()), 1)
        self.assertEqual(self.history()[0].name, os.readlink(self.path))
        for depth in (0, -1, 1001, True, '10'):
            with self.assertRaises(ValueError): self.save(depth)
        for value in ('0', '-1', '1001', 'unsafe'):
            self.write_config(extra='snapshot_history_depth=' + value)
            self.plan(expected=2)
    def test_relative_traversal_external_and_chained_latest_links_are_rejected(self):
        self.save(); active = os.readlink(self.path)
        outside = self.folder / 'outside.conf'; outside.write_text('unrelated')
        for target in ('../outside.conf', str(outside), 'subdir/' + active, active + '/../' + active):
            self.path.unlink(); self.path.symlink_to(target)
            with self.assertRaises((ValueError, OSError)): snapshot_read(self.path)
            with self.assertRaises((ValueError, OSError)): self.save()
        self.path.unlink(); self.path.symlink_to(active)
        original = self.path.parent / active; original.unlink(); original.symlink_to(outside)
        with self.assertRaises(OSError): snapshot_read(self.path)
        with self.assertRaises(ValueError): self.save()
        self.assertEqual(outside.read_text(), 'unrelated')
    def test_dangling_link_and_unsafe_history_do_not_authorize_replacement(self):
        self.save(); active = os.readlink(self.path)
        (self.path.parent / active).unlink()
        with self.assertRaises(ValueError): self.save()
        self.assertEqual(os.readlink(self.path), active)
    def test_concurrent_writer_is_busy_without_pruning_or_pointer_change(self):
        self.save(); before = os.readlink(self.path)
        with open(self.path.parent / '.snapshot.lock', 'r+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError): self.save(1)
        self.assertEqual(os.readlink(self.path), before)
    def test_post_commit_prune_failure_reports_publication_without_deleting_active(self):
        self.save(); real = os.unlink
        def denied(name, **kw):
            if Path(name).name.startswith('snapshot-'): raise PermissionError('prune denied')
            return real(name, **kw)
        with patch('joetoo_kwin_persistence.os.unlink', side_effect=denied): result = self.save(1)
        self.assertTrue(result['pruning_warning'])
        self.assertEqual(os.readlink(self.path), result['snapshot'])
        self.assertEqual(snapshot_read(self.path), self.text)
    def test_post_commit_directory_fsync_warning_keeps_previous_history(self):
        self.save(); real = os.fsync; directories = []
        def fail_final_directory(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                directories.append(fd)
                if len(directories) == 2: raise OSError('directory fsync unavailable')
            return real(fd)
        with patch('joetoo_kwin_persistence.os.fsync', side_effect=fail_final_directory):
            result = self.save(1)
        self.assertTrue(result['publication_warning'])
        self.assertEqual(result['pruned'], 0)
        self.assertEqual(len(self.history()), 2)
        self.assertEqual(os.readlink(self.path), result['snapshot'])
    def test_invalid_regular_legacy_or_unsafe_history_is_not_overwritten(self):
        atomic_private(self.path, '# arbitrary regular file\n')
        with self.assertRaises(ValueError): self.save()
        self.assertEqual(read_private(self.path), '# arbitrary regular file\n')
        self.path.unlink(); self.save()
        active = os.readlink(self.path); (self.path.parent / active).chmod(0o644)
        with self.assertRaises(ValueError): self.save(1)
        self.assertEqual(os.readlink(self.path), active)
    def test_unrelated_files_are_never_pruned(self):
        self.save(); other = self.path.parent / 'notes.conf'; other.write_text('keep')
        self.save(1); self.assertEqual(other.read_text(), 'keep')

    def test_normalized_v2_stores_policy_once_and_rejects_mixed_policies(self):
        other = fixtures.recipe(slot=2)
        text = snapshot_text(dict(protocol=1, entries=[fixtures.recipe(), other]))
        data = json.loads(text.splitlines()[1][8:])
        self.assertEqual(data['protocol'], 2)
        self.assertEqual(data['settings'], fixtures.policy())
        self.assertTrue(all('settings' not in e for e in data['entries']))
        other['settings']['terminal_width_percent'] = '75'
        with self.assertRaises(ValueError): snapshot_text(dict(protocol=1, entries=[fixtures.recipe(), other]))


class HistoricalObservationTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RecoveryTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
    def test_missing_record_after_restart_keeps_full_bounded_last_known_observation(self):
        self.f.r.observation['caption'] = 'caption' * 100
        expected = dict(self.f.r.observation); expected['caption'] = expected['caption'][:256]
        self.f.b.registry.set_presence(self.f.r.window_uuid, 'missing')
        saved = json.loads(read_private(self.f.path))['records'][0]['observation']
        for key in ('uuid', 'pid', 'resource_class', 'resource_name', 'desktop_file', 'caption', 'desktops', 'on_all_desktops', 'geometry'):
            self.assertEqual(saved[key], expected[key])
        self.f.bus.windows.clear(); b, recovery = self.f.fresh(); self.f.sync(b, windows=[])
        record = json.loads(b.GetManaged('win-001'))['window']
        self.assertEqual(record['presence'], 'missing')
        self.assertEqual(record['observation']['geometry'], expected['geometry'])
        self.assertEqual(record['observation']['caption'], expected['caption'])
    def test_identity_only_legacy_checkpoint_getmanaged_omits_unknown_fields(self):
        data = json.loads(read_private(self.f.path))
        data['records'][0]['observation'] = {k: data['records'][0]['observation'][k] for k in ('uuid', 'pid', 'resource_class')}
        atomic_private(self.f.path, json.dumps(data))
        self.f.bus.windows.clear(); b, recovery = self.f.fresh(); self.f.sync(b, windows=[])
        observation = json.loads(b.GetManaged('win-001'))['window']['observation']
        self.assertEqual(observation, dict(pid=42, resource_class='konsole'))
    def test_geometry_only_changes_do_not_write_but_flush_and_authority_changes_do(self):
        from joetoo_kwin_recovery import atomic_private as real
        with patch('joetoo_kwin_recovery.atomic_private', wraps=real) as write:
            for i in range(30):
                observed = dict(self.f.r.observation, geometry=dict(x=i, y=80, width=850, height=700))
                self.f.b.registry.set_presence(self.f.r.window_uuid, 'present', observed)
            self.assertEqual(write.call_count, 0)
            self.f.recovery.flush(); self.assertEqual(write.call_count, 1)
            self.assertEqual(json.loads(read_private(self.f.path))['records'][0]['observation']['geometry']['x'], 29)
            self.f.b.registry.set_presence(self.f.r.window_uuid, 'missing')
            self.assertEqual(write.call_count, 2)
    def test_invalid_historical_frame_fails_closed_without_changing_identity(self):
        data = json.loads(read_private(self.f.path)); data['records'][0]['observation']['geometry']['width'] = 'unsafe'
        atomic_private(self.f.path, json.dumps(data))
        b, recovery = self.f.fresh()
        self.assertEqual(recovery.state, 'checkpoint_invalid')


class HistoryCliTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.SnapshotCliTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
    def test_current_config_retention_is_independent_of_original_launch_policy(self):
        self.f.fixture.write_config(extra='snapshot_history_depth=2')
        for _ in range(3):
            run = self.f.run_cli('-S', '-f', str(self.f.fixture.config))
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(len(list(self.f.path.parent.glob('snapshot-*.conf'))), 2)
        self.f.fixture.write_config(extra='snapshot_history_depth=1')
        run = self.f.run_cli('-S', '-f', str(self.f.fixture.config))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(len(list(self.f.path.parent.glob('snapshot-*.conf'))), 1)
        data = json.loads(snapshot_read(self.f.path).splitlines()[1][8:])
        self.assertNotIn('snapshot_history_depth', data['settings'])
    def test_bad_depth_refuses_before_broker_export(self):
        text = self.f.client.read_text().replace('*.ExportManagedSnapshot) printf', '*.ExportManagedSnapshot) printf "export\\n" >> "$TRACE"; printf')
        self.f.client.write_text(text)
        self.f.fixture.write_config(extra='snapshot_history_depth=0')
        run = self.f.run_cli('-S', '-f', str(self.f.fixture.config))
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertFalse(self.f.calls.exists())


if __name__ == '__main__': unittest.main()
