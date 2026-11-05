from pathlib import Path
p=Path('tests/test_openrc_user_setup.py')
s=p.read_text().replace('import importlib.machinery','import hashlib\nimport json\nimport importlib.machinery',1).replace('self.env.pop("XDG_CONFIG_HOME", None)', 'self.env.pop("XDG_CONFIG_HOME", None)\n        self.env.pop("XDG_STATE_HOME", None)\n        self.archive = self.home / ".local/state/joetoo-kwin/archive"')
s=s.replace("backups = list(module.parent.glob(module.name + '.before-update.*'))", "backups = list(self.archive.glob('vnc_' + module.stem.removeprefix('joetoo_kwin_vnc_') + '/*/' + module.name))")
s=s.replace('backups = list(self.override.parent.glob("joetoo-kwind.before-update.*"))', 'backups = list(self.archive.glob("override/*/joetoo-kwind"))').replace("backups = list(self.service.parent.glob('joetoo-kwind.before-update.*'))", "backups = list(self.archive.glob('service/*/joetoo-kwind'))")
pos=s.index('    def test_vnc_symlinks_rejected')
s=s[:pos]+'''    def archived(self, component, name):
        return sorted(self.archive.glob(component + '/*/' + name))

    def test_unchanged_update_creates_no_archive_or_legacy_backups(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        for _ in range(2):
            result = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.archive.exists())
        self.assertFalse(list(self.home.rglob('*.before-update.*')))

    def test_archive_all_nine_components_and_same_named_files_are_separate(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        installed = {
            'service': self.service, 'daemon': self.daemon, 'override': self.override,
            'registry': self.daemon.with_name('joetoo_kwin_registry.py'),
            'resident': self.home / '.local/share/joetoo-kwin/joetoo-kwin-resident.js',
            'cli': self.home / '.local/bin/joetoo-kwin',
            **dict(zip(('vnc_identity', 'vnc_target', 'vnc_launch'), self.vnc_modules))}
        for path in installed.values():
            path.write_bytes(b'previous version\\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for component, path in installed.items():
            saved, = self.archived(component, path.name)
            self.assertEqual(saved.read_bytes(), b'previous version\\n')
            self.assertNotEqual(saved.stat().st_ino, path.stat().st_ino)
            self.assertEqual(saved.stat().st_nlink, 1)
            metadata = json.loads((saved.parent / 'provenance.json').read_text())
            self.assertEqual(metadata['installed_path'], str(path))
            self.assertEqual(metadata['original_name'], path.name)
            self.assertEqual(metadata['sha256'], hashlib.sha256(saved.read_bytes()).hexdigest())
            self.assertEqual(saved.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_archive_deduplicates_repeated_bytes_but_retains_distinct_versions(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        for old in (b'first version', b'other version', b'first version'):
            self.daemon.write_bytes(old)
            result = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(result.returncode, 0, result.stderr)
        versions = self.archived('daemon', self.daemon.name)
        self.assertEqual({p.read_bytes() for p in versions}, {b'first version', b'other version'})
        self.assertEqual(len(versions), 2)
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in versions]
        self.daemon.write_bytes(b'first version')
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual([(p.read_bytes(), p.stat().st_mtime_ns) for p in versions], before)

    def test_unsafe_archive_rejected_without_overwriting_installation(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'previous version')
        outside = self.home / 'outside'
        outside.mkdir()
        self.archive.parent.mkdir(parents=True)
        self.archive.symlink_to(outside, target_is_directory=True)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Refusing symlink', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        self.assertEqual(list(outside.iterdir()), [])
        self.archive.unlink()
        self.archive.mkdir(mode=0o777)
        self.archive.chmod(0o777)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsafe archive directory', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')

    def test_corrupt_or_symlink_archive_version_is_not_overwritten(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        old = b'previous version'
        self.daemon.write_bytes(old)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        saved, = self.archived('daemon', self.daemon.name)
        self.daemon.write_bytes(old)
        saved.write_bytes(b'corrupt')
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual(saved.read_bytes(), b'corrupt')
        self.assertEqual(self.daemon.read_bytes(), old)
        saved.unlink()
        saved.symlink_to(self.daemon)
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertTrue(saved.is_symlink())
        self.assertEqual(self.daemon.read_bytes(), old)

    def test_install_failure_keeps_recoverable_archive_and_check_detects_failure(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'previous version')
        # Fail the existing install command, without invoking a real service.
        failing = self.bindir / 'install'
        failing.write_text('#!/bin/sh\\nexit 73\\n')
        failing.chmod(0o755)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 73)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        saved, = self.archived('daemon', self.daemon.name)
        self.assertEqual(saved.read_bytes(), b'previous version')
        self.assertFalse(list(self.archive.rglob('.pending-*')))
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)

    def test_archive_failure_precedes_any_install_command(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.service.write_bytes(b'old service')
        self.daemon.write_bytes(b'old daemon')
        self.archive.mkdir(parents=True)
        (self.archive / 'daemon').write_text('not a directory')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.service.read_bytes(), b'old service')
        self.assertEqual(self.daemon.read_bytes(), b'old daemon')
        saved, = self.archived('service', self.service.name)
        self.assertEqual(saved.read_bytes(), b'old service')

    def test_xdg_state_override_and_relative_path_rejection(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'old')
        self.env['XDG_STATE_HOME'] = 'relative'
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual(self.daemon.read_bytes(), b'old')
        self.env['XDG_STATE_HOME'] = str(self.home / 'custom-state')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(list((self.home / 'custom-state/joetoo-kwin/archive').glob('daemon/*/joetoo-kwind')))
        self.assertFalse(self.archive.exists())

    def test_legacy_preview_groups_content_without_modification(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        files = []
        for suffix, content in (('before-update.one', b'A'),
                                ('before-update.two', b'A'),
                                ('before-step1.2a-update.old', b'B')):
            path = self.daemon.with_name(self.daemon.name + '.' + suffix)
            path.write_bytes(content)
            files.append(path)
        before = [(p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns) for p in files]
        self.rc_service.write_text('#!/bin/sh\\nexit 0\\n')
        result = self.run_tool(INSTALL_TOOL, '--preview-legacy-backups')
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(records), 9)
        daemon = next(r for r in records if r['component'] == 'daemon')
        self.assertEqual(sorted(v['copies'] for v in daemon['versions']), [1, 2])
        self.assertEqual({p for v in daemon['versions'] for p in v['paths']}, set(map(str, files)))
        self.assertEqual([(p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns) for p in files], before)
        self.assertFalse(self.archive.exists())
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

'''+s[pos:]
p.write_text(s)
p=Path('tests/test_step1_4b_broker.py');s=p.read_text().replace("self.assertEqual(script.count('\"$daemon_dest\" \"$registry_dest\"'), 3)","self.assertEqual(script.count('\"$daemon_dest\" \"$registry_dest\"'), 2)\n        self.assertIn('\"$registry_source\" \"$registry_dest\"', script)");p.write_text(s)
