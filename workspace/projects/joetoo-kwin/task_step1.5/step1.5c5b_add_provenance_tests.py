from pathlib import Path
p=Path('tests/test_openrc_user_setup.py');s=p.read_text();pos=s.index('    def test_install_failure_keeps_recoverable_archive')
s=s[:pos]+'''    def archived_daemon_fixture(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'previous version')
        self.daemon.chmod(0o600)
        os.utime(self.daemon, ns=(1600000000000000000, 1600000001000000000))
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stderr)
        saved, = self.archived('daemon', self.daemon.name)
        self.daemon.write_bytes(b'previous version')
        return saved

    def inject_archive_python(self, preamble):
        wrapper = self.bindir / 'python3'
        wrapper.write_text('#!' + sys.executable + '\\n'
                           'import sys\\nsys.argv.pop(1)\\n' + preamble + '\\n'
                           'exec(compile(sys.stdin.read(), "archive", "exec"))\\n')
        wrapper.chmod(0o755)
        return wrapper

    def test_existing_version_directory_permissions_are_revalidated(self):
        saved = self.archived_daemon_fixture()
        for mode in (0o755, 0o770, 0o777):
            with self.subTest(mode=oct(mode)):
                saved.parent.chmod(mode)
                result = self.run_tool(INSTALL_TOOL, '--update')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(str(saved.parent), result.stderr)
                self.assertEqual(self.daemon.read_bytes(), b'previous version')
                self.assertEqual(saved.read_bytes(), b'previous version')
        saved.parent.chmod(0o700)

    def test_existing_version_and_provenance_ownership_are_revalidated(self):
        saved = self.archived_daemon_fixture()
        for target in (saved.parent, saved.parent / 'provenance.json'):
            with self.subTest(target=target.name):
                # Ordinary-user tests cannot chown files to another UID. Inject
                # only that stat field, exercising the real installer boundary.
                preamble = ('import os\\nfrom pathlib import Path\\n'
                            'original_stat = Path.stat\\n'
                            'def changed_stat(path, *args, **kwargs):\\n'
                            '    info = original_stat(path, *args, **kwargs)\\n'
                            f'    if str(path) == {str(target)!r}:\\n'
                            '        fields = list(info)\\n'
                            '        fields[4] = os.geteuid() + 1\\n'
                            '        return os.stat_result(fields)\\n'
                            '    return info\\n'
                            'Path.stat = changed_stat\\n')
                wrapper = self.inject_archive_python(preamble)
                result = self.run_tool(INSTALL_TOOL, '--update')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(str(target), result.stderr)
                self.assertEqual(self.daemon.read_bytes(), b'previous version')
                wrapper.unlink()

    def test_existing_provenance_rejects_invalid_json_schema_and_identity(self):
        saved = self.archived_daemon_fixture()
        provenance = saved.parent / 'provenance.json'
        valid = json.loads(provenance.read_text())
        variants = {'malformed': '{', 'array': '[]',
                    'missing field': json.dumps({k: v for k, v in valid.items() if k != 'mode'})}
        for key, value in (('schema_version', 2), ('sha256', '0' * 64),
                           ('original_name', 'unrelated'), ('installed_path', 'relative'),
                           ('source_path', '/tmp/unrelated'), ('mode', '0o888'),
                           ('mtime_ns', True), ('atime_ns', 'yesterday'),
                           ('archived_at', '2026-11-02T12:00:00')):
            variants[key] = json.dumps({**valid, key: value})
        for label, text in variants.items():
            with self.subTest(label=label):
                provenance.write_text(text)
                result = self.run_tool(INSTALL_TOOL, '--update')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(provenance.read_text(), text)
                self.assertEqual(self.daemon.read_bytes(), b'previous version')
                self.assertEqual(saved.read_bytes(), b'previous version')
        provenance.write_text(json.dumps(valid))
        provenance.chmod(0o644)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unsafe provenance file', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')

    def test_identical_payload_retains_distinct_metadata_records(self):
        saved = self.archived_daemon_fixture()
        first = json.loads((saved.parent / 'provenance.json').read_text())
        original = saved.stat()
        self.daemon.chmod(0o640)
        second_times = (1700000000000000000, 1700000001000000000)
        os.utime(self.daemon, ns=second_times)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stderr)
        second_path, = saved.parent.glob('provenance.*.json')
        second = json.loads(second_path.read_text())
        self.assertEqual(first['mode'], '0o600')
        self.assertEqual(second['mode'], '0o640')
        self.assertEqual((second['atime_ns'], second['mtime_ns']), second_times)
        self.assertEqual(first['mtime_ns'], 1600000001000000000)
        self.assertEqual(saved.stat().st_ino, original.st_ino)
        self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
        self.assertEqual(saved.stat().st_mtime_ns, first['mtime_ns'])
        self.assertEqual(saved.read_bytes(), b'previous version')
        self.assertEqual(len(list(saved.parent.iterdir())), 3)  # One payload, two records.
        self.assertEqual(json.loads((saved.parent / 'provenance.json').read_text()), first)
        # Retrying the exact same installation metadata adds no duplicate record.
        self.daemon.write_bytes(b'previous version')
        self.daemon.chmod(0o640)
        os.utime(self.daemon, ns=second_times)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual(len(list(saved.parent.iterdir())), 3)
        self.assertEqual(second_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(second_path.stat().st_nlink, 1)

    def test_additional_provenance_and_payload_metadata_must_remain_valid(self):
        saved = self.archived_daemon_fixture()
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        extra, = saved.parent.glob('provenance.*.json')
        self.daemon.write_bytes(b'previous version')
        original = extra.read_bytes()
        extra.write_text('{}')
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        extra.write_bytes(original)
        wrong_name = extra.with_name('provenance.wrong.json')
        extra.rename(wrong_name)
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        wrong_name.rename(extra)
        saved.chmod(0o640)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Payload/provenance metadata mismatch', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')

    def test_new_provenance_failure_preserves_payload_old_record_and_install(self):
        saved = self.archived_daemon_fixture()
        first = (saved.parent / 'provenance.json').read_bytes()
        self.inject_archive_python('import os\\n'
                                   'def fail(*args, **kwargs):\\n'
                                   '    raise OSError("injected record publish failure")\\n'
                                   'os.link = fail\\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('injected record publish failure', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        self.assertEqual(saved.read_bytes(), b'previous version')
        self.assertEqual((saved.parent / 'provenance.json').read_bytes(), first)
        self.assertEqual(len(list(saved.parent.iterdir())), 2)

'''+s[pos:];p.write_text(s)
