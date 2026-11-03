#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-time migration tests: only disposable HOME, no live services or network."""

import copy
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/joetoo-kwind-migrate-legacy-backups'
INSTALLER = ROOT / 'tools/joetoo-kwind-install-poc'
loader = importlib.machinery.SourceFileLoader('legacy_migration', str(TOOL))
spec = importlib.util.spec_from_loader(loader.name, loader)
migration = importlib.util.module_from_spec(spec)
loader.exec_module(migration)


@unittest.skipIf(os.geteuid() == 0, 'ordinary-user filesystem tests')
class LegacyMigrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        env = dict(os.environ, HOME=str(self.home))
        env.pop('XDG_CONFIG_HOME', None)
        env.pop('XDG_STATE_HOME', None)
        binary = self.home / 'bin'
        binary.mkdir()
        service = binary / 'rc-service'
        service.write_text('#!/bin/sh\nexit 3\n')
        service.chmod(0o755)
        env['PATH'] = str(binary) + os.pathsep + env['PATH']
        self.env_patch = mock.patch.dict(os.environ, env, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.install('--install')
        self.roots = migration.environment()
        self.archive = Path(self.roots['archive'])
        self.components = migration.components(self.roots)
        self.paths = []

    def install(self, action):
        result = subprocess.run([str(INSTALLER), action], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def legacy(self, component='daemon', content=b'old', mode=0o600, seconds=0):
        destination = self.components[component][1]
        path = destination.with_name(destination.name + f'.before-update.20261025-010203.{len(self.paths) + 1}')
        path.write_bytes(content)
        path.chmod(mode)
        os.utime(path, ns=(1600000000000000000 + seconds, 1600000001000000000 + seconds))
        self.paths.append(path)
        return path

    def plan(self):
        result = migration.inventory()
        self.assertEqual(result['state'], 'planned', result['anomalies'])
        return json.loads(json.dumps(result))

    def snapshots(self):
        return {str(p): migration.read_file(p) for p in self.paths}

    def test_inventory_is_read_only_complete_and_separates_filename_timestamp(self):
        self.legacy(mode=0o640)
        before = self.snapshots()
        plan = self.plan()
        row, = plan['records']
        self.assertEqual(row['original_path'], str(self.paths[0]))
        self.assertEqual(row['embedded_timestamp'], '20261025-010203')
        self.assertEqual(row['mtime_ns'], 1600000001000000000)
        self.assertEqual(row['mode'], '0o640')
        self.assertEqual(row['uid'], os.geteuid())
        self.assertIn('gid', row)
        self.assertIn('ctime_ns', row)
        self.assertEqual(self.snapshots(), before)
        self.assertFalse(self.archive.exists())

    def test_unique_duplicate_metadata_and_cross_component_namespaces(self):
        self.legacy(content=b'A', mode=0o600)
        self.legacy(content=b'A', mode=0o640, seconds=100)
        self.legacy(content=b'B')
        self.legacy('service', b'A')
        before = self.snapshots()
        plan = self.plan()
        self.assertEqual(plan['summary'], dict(legacy_paths=4, distinct_versions=3,
                                             duplicate_copies=1, new_payloads=3, reused_payloads=0))
        result = migration.copy_plan(plan)
        self.assertEqual((result['legacy_paths'], result['distinct_versions']), (4, 3))
        self.assertEqual((result['new_payloads'], result['reused_payloads']), (3, 0))
        manifest = migration.read_json(Path(result['manifest']))
        self.assertEqual(len(manifest['plan']['records']), 4)
        self.assertEqual({r['mode'] for r in manifest['plan']['records']}, {'0o600', '0o640'})
        self.assertEqual(len(result['archive_after']), 6)
        self.assertEqual(self.snapshots(), before)
        migration.verify_manifest(manifest)
        self.install('--check')
        archive_before = migration.archive_inventory(self.roots)
        self.install('--update')
        self.assertEqual(migration.archive_inventory(self.roots), archive_before)
        self.assertEqual(self.snapshots(), before)

    def test_repeated_copy_and_verification_do_not_create_new_records(self):
        self.legacy()
        plan = self.plan()
        result = migration.copy_plan(plan)
        path = Path(result['manifest'])
        manifest_before = migration.read_file(path)
        before = migration.archive_inventory(self.roots)
        repeated = migration.copy_plan(plan)
        self.assertEqual((repeated['new_payloads'], repeated['reused_payloads']), (0, 1))
        self.assertEqual(migration.read_file(path), manifest_before)
        self.assertEqual(migration.archive_inventory(self.roots), before)
        # A fresh inventory of the identical originals addresses the same manifest.
        again = migration.copy_plan(self.plan())
        self.assertEqual(again['manifest'], result['manifest'])
        self.assertEqual(migration.read_file(path), manifest_before)

    def test_reuse_existing_payload_and_preserve_vnc_archives(self):
        daemon = self.components['daemon'][1]
        daemon.write_bytes(b'old')
        for key in ('vnc_identity', 'vnc_target'):
            self.components[key][1].write_bytes(key.encode())
        self.install('--update')
        existing = migration.archive_inventory(self.roots)
        self.legacy(content=b'old', mode=0o640)
        plan = self.plan()
        self.assertEqual(plan['summary']['reused_payloads'], 1)
        result = migration.copy_plan(plan)
        self.assertEqual((result['new_payloads'], result['reused_payloads']), (0, 1))
        self.assertEqual(migration.archive_inventory(self.roots), existing)
        self.install('--check')
        self.install('--update')
        self.assertEqual(migration.archive_inventory(self.roots), existing)

    def test_corrupt_archive_rejected_without_overwriting_it(self):
        self.legacy()
        plan = self.plan()
        result = migration.copy_plan(plan)
        payload = Path(plan['records'][0]['payload'])
        payload.write_bytes(b'corrupted')
        bad = migration.inventory()
        self.assertEqual(bad['state'], 'blocked')
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertEqual(payload.read_bytes(), b'corrupted')
        self.assertEqual(self.paths[0].read_bytes(), b'old')

    def test_invalid_archive_provenance_or_permissions_blocks_inventory(self):
        self.legacy()
        plan = self.plan()
        migration.copy_plan(plan)
        version = Path(plan['records'][0]['payload']).parent
        provenance = version / 'provenance.json'
        original = provenance.read_bytes()
        provenance.write_text('{}')
        self.assertEqual(migration.inventory()['state'], 'blocked')
        provenance.write_bytes(original)
        version.chmod(0o755)
        self.assertEqual(migration.inventory()['state'], 'blocked')
        version.chmod(0o700)

    def test_symlink_fifo_and_bad_filename_candidates_block_plan(self):
        path = self.legacy()
        path.unlink()
        path.symlink_to(self.components['daemon'][1])
        self.assertEqual(migration.inventory()['state'], 'blocked')
        path.unlink()
        os.mkfifo(path)
        self.assertEqual(migration.inventory()['state'], 'blocked')
        path.unlink()
        path = path.with_name(path.name.replace('20261025', '20261325'))
        path.write_bytes(b'bad date')
        self.assertEqual(migration.inventory()['state'], 'blocked')
        self.assertFalse(self.archive.exists())

    def test_path_traversal_wrong_mapping_and_duplicate_inventory_rejected(self):
        self.legacy()
        plan = self.plan()
        for change in ('traversal', 'component', 'duplicate', 'metadata', 'summary'):
            bad = copy.deepcopy(plan)
            if change == 'traversal':
                bad['records'][0]['payload'] = str(self.home / '../outside')
            elif change == 'component':
                bad['records'][0]['component'] = 'service'
            elif change == 'duplicate':
                bad['records'].append(copy.deepcopy(bad['records'][0]))
            elif change == 'metadata':
                bad['records'][0]['mode'] = '0o777'
            else:
                bad['summary']['legacy_paths'] += 1
            bad['inventory_id'] = migration.plan_id(bad)
            with self.subTest(change=change), self.assertRaises(ValueError):
                migration.copy_plan(bad)
        self.assertFalse(self.archive.exists())

    def test_changed_added_or_replaced_original_invalidates_inventory(self):
        original = self.legacy()
        plan = self.plan()
        original.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        plan = self.plan()
        self.legacy(content=b'another')
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        plan = self.plan()
        data = original.read_bytes()
        original.unlink()
        original.write_bytes(data)
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertFalse(self.archive.exists())

    def test_changed_installation_invalidates_inventory_without_touching_it(self):
        self.legacy()
        plan = self.plan()
        daemon = self.components['daemon'][1]
        daemon.chmod(0o600)
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertEqual(daemon.stat().st_mode & 0o777, 0o600)
        self.assertFalse(self.archive.exists())

    def test_archive_symlink_rejected_without_writes(self):
        self.legacy()
        plan = self.plan()
        elsewhere = self.home / 'elsewhere'
        elsewhere.mkdir()
        self.archive.parent.mkdir(parents=True)
        self.archive.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_permission_failure_reports_incomplete_without_changing_originals(self):
        self.legacy()
        plan = self.plan()
        target = self.archive / 'daemon'
        target.mkdir(parents=True, mode=0o700)
        target.chmod(0o500)
        before = self.snapshots()
        try:
            with self.assertRaises(PermissionError):
                migration.copy_plan(plan)
            manifest, = (self.archive / 'migrations').glob('legacy-*.json')
            self.assertEqual(migration.read_json(manifest)['state'], 'incomplete')
            self.assertEqual(self.snapshots(), before)
        finally:
            target.chmod(0o700)

    def test_interrupted_publication_leaves_no_partial_version_and_can_retry(self):
        self.legacy()
        plan = self.plan()
        before = self.snapshots()
        with mock.patch.object(migration, 'publish_directory', side_effect=OSError('publication interrupted')):
            with self.assertRaises(OSError):
                migration.copy_plan(plan)
        self.assertFalse(Path(plan['records'][0]['payload']).exists())
        self.assertFalse(list(self.archive.rglob('.legacy-pending-*')))
        self.assertEqual(self.snapshots(), before)
        self.assertEqual(migration.copy_plan(plan)['state'], 'verified')

    def test_concurrently_created_empty_version_is_not_overwritten(self):
        self.legacy()
        plan = self.plan()
        original = migration.publish_directory
        def collision(staging, version):
            version.mkdir(mode=0o700)
            return original(staging, version)
        with mock.patch.object(migration, 'publish_directory', side_effect=collision):
            with self.assertRaises(FileExistsError):
                migration.copy_plan(plan)
        version = Path(plan['records'][0]['payload']).parent
        self.assertTrue(version.is_dir())
        self.assertEqual(list(version.iterdir()), [])
        self.assertEqual(self.paths[0].read_bytes(), b'old')
        self.assertFalse(list(self.archive.rglob('.legacy-pending-*')))

    def test_failure_after_payload_copy_keeps_original_and_cleans_staging(self):
        self.legacy()
        plan = self.plan()
        before = self.snapshots()
        helpers = migration.archive_helpers()
        with mock.patch.object(helpers, 'write_provenance', side_effect=OSError('interrupted after copy')):
            with mock.patch.object(migration, 'archive_helpers', return_value=helpers):
                with self.assertRaises(OSError):
                    migration.copy_plan(plan)
        self.assertEqual(self.snapshots(), before)
        self.assertFalse(Path(plan['records'][0]['payload']).exists())
        self.assertFalse(list(self.archive.rglob('.legacy-pending-*')))

    def test_partial_migration_has_resumable_complete_path_manifest(self):
        self.legacy(content=b'A')
        self.legacy(content=b'B')
        plan = self.plan()
        original = migration.publish_version
        count = [0]
        def interrupt(*args):
            count[0] += 1
            if count[0] == 2:
                raise KeyboardInterrupt('test interruption')
            return original(*args)
        with mock.patch.object(migration, 'publish_version', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                migration.copy_plan(plan)
        path, = (self.archive / 'migrations').glob('legacy-*.json')
        manifest = migration.read_json(path)
        self.assertEqual(manifest['state'], 'incomplete')
        self.assertEqual(len(manifest['plan']['records']), 2)
        self.assertEqual(len(manifest['verified_payloads']), 1)
        with self.assertRaises(ValueError):
            migration.verify_manifest(manifest)
        result = migration.copy_plan(plan)
        self.assertEqual((result['new_payloads'], result['reused_payloads']), (1, 1))
        self.assertEqual(len(self.paths), 2)

    def test_manifest_publication_failure_does_not_copy_payloads(self):
        self.legacy()
        plan = self.plan()
        before = self.snapshots()
        with mock.patch.object(migration.os, 'replace', side_effect=OSError('manifest publication interrupted')):
            with self.assertRaises(OSError):
                migration.copy_plan(plan)
        self.assertFalse(Path(plan['records'][0]['payload']).exists())
        self.assertEqual(self.snapshots(), before)
        self.assertFalse(list(self.archive.rglob('.manifest-*')))

    def test_manifest_completeness_and_corruption_are_detected(self):
        self.legacy()
        result = migration.copy_plan(self.plan())
        path = Path(result['manifest'])
        manifest = migration.read_json(path)
        manifest['verified_payloads'] = []
        with self.assertRaises(ValueError):
            migration.verify_manifest(manifest)
        path.write_text('{}')
        with self.assertRaises((ValueError, KeyError)):
            migration.copy_plan(self.plan())
        self.assertEqual(path.read_text(), '{}')

    def test_existing_manifest_symlink_or_unsafe_mode_is_rejected(self):
        self.legacy()
        plan = self.plan()
        result = migration.copy_plan(plan)
        path = Path(result['manifest'])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        path.unlink()
        path.symlink_to(self.paths[0])
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertEqual(self.paths[0].read_bytes(), b'old')

    def test_inventory_and_verify_never_call_directory_creation_helpers(self):
        self.legacy()
        plan = self.plan()
        result = migration.copy_plan(plan)
        helpers = migration.archive_helpers()
        with mock.patch.object(helpers, 'private_directory', side_effect=AssertionError('read-only mkdir')):
            with mock.patch.object(migration, 'archive_helpers', return_value=helpers):
                self.assertEqual(migration.inventory()['state'], 'planned')
                migration.verify_manifest(migration.read_json(Path(result['manifest'])))

    def test_original_change_after_validation_stops_copy(self):
        original = self.legacy()
        plan = self.plan()
        publish = migration.publish_version
        def change_then_publish(*args):
            original.write_bytes(b'changed after validation')
            return publish(*args)
        with mock.patch.object(migration, 'publish_version', side_effect=change_then_publish):
            with self.assertRaises(ValueError):
                migration.copy_plan(plan)
        self.assertEqual(original.read_bytes(), b'changed after validation')
        self.assertFalse(Path(plan['records'][0]['payload']).exists())

    def test_existing_incomplete_manifest_with_unknown_payload_is_rejected(self):
        self.legacy()
        plan = self.plan()
        with mock.patch.object(migration, 'publish_version', side_effect=OSError('stop')):
            with self.assertRaises(OSError):
                migration.copy_plan(plan)
        path, = (self.archive / 'migrations').glob('legacy-*.json')
        manifest = migration.read_json(path)
        manifest['verified_payloads'] = ['/unrelated/payload']
        migration.save_manifest(path, manifest)
        before = migration.read_file(path)
        with self.assertRaises(ValueError):
            migration.copy_plan(plan)
        self.assertEqual(migration.read_file(path), before)

    def test_cli_inventory_and_verify_are_offline_and_nonmutating(self):
        self.legacy()
        result = subprocess.run([str(TOOL), '--inventory'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        plan_path = self.home / 'plan.json'
        plan_path.write_text(json.dumps(plan))
        copied = subprocess.run([str(TOOL), '--copy', str(plan_path)], capture_output=True, text=True)
        self.assertEqual(copied.returncode, 0, copied.stderr)
        manifest = Path(json.loads(copied.stdout)['manifest'])
        before, originals = migration.read_file(manifest), self.snapshots()
        verified = subprocess.run([str(TOOL), '--verify', str(manifest)], capture_output=True, text=True)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(migration.read_file(manifest), before)
        self.assertEqual(self.snapshots(), originals)


if __name__ == '__main__':
    unittest.main()
