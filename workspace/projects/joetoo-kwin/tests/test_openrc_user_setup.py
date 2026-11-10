#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.2a OpenRC user-config and complete local-install regression tests.

Subprocess integration runs must execute as a non-root user in a disposable HOME.
No real OpenRC service is started, stopped, configured system-wide, or reloaded.
"""

import hashlib
import json
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONFIG_TOOL = ROOT / "tools" / "joetoo-kwind-configure-openrc-user"
INSTALL_TOOL = ROOT / "tools" / "joetoo-kwind-install-poc"


def load_config():
    loader = importlib.machinery.SourceFileLoader("joetoo_user_rc_config", str(CONFIG_TOOL))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class ConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()

    def test_literal_openrc_assignment_from_empty(self):
        updated, names = self.config.parse_and_update("")
        self.assertEqual(updated, 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"\n')
        self.assertEqual(names, ["DBUS_SESSION_BUS_ADDRESS", "JOETOO_KWIND_EXEC", "DISPLAY", "XAUTHORITY"])
        self.assertEqual(self.config.parse_and_update(updated)[0], updated)
        self.assertNotIn("case ", updated)

    def test_preserve_existing_literal_allowlist_and_unrelated_settings(self):
        original = 'rc_some_setting="yes"\nrc_env_allow="FOO DBUS_SESSION_BUS_ADDRESS"\n'
        updated, names = self.config.parse_and_update(original)
        self.assertEqual(updated, 'rc_some_setting="yes"\nrc_env_allow="FOO DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"\n')
        self.assertEqual(names, ["FOO", "DBUS_SESSION_BUS_ADDRESS", "JOETOO_KWIND_EXEC", "DISPLAY", "XAUTHORITY"])
        self.assertEqual(self.config.parse_and_update(updated)[0], updated)

    def test_migrate_exact_broken_legacy_case_block(self):
        original = '''# BEGIN joetoo-kwind Step 1.2a environment
# Extend, never replace, other services' rc_env_allow entries.
case " ${rc_env_allow:-} " in
    *" DBUS_SESSION_BUS_ADDRESS "*) ;;
    *) rc_env_allow="${rc_env_allow:+${rc_env_allow} }DBUS_SESSION_BUS_ADDRESS" ;;
esac
case " ${rc_env_allow:-} " in
    *" JOETOO_KWIND_EXEC "*) ;;
    *) rc_env_allow="${rc_env_allow:+${rc_env_allow} }JOETOO_KWIND_EXEC" ;;
esac
# END joetoo-kwind Step 1.2a environment
'''
        updated, _ = self.config.parse_and_update(original)
        self.assertEqual(updated.strip(), 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"')

    def test_reject_unknown_or_partial_managed_block(self):
        with self.assertRaises(self.config.ConfigurationError):
            self.config.parse_and_update("# BEGIN joetoo-kwind Step 1.2a environment\n")
        with self.assertRaises(self.config.ConfigurationError):
            self.config.parse_and_update('rc_env_allow="${OTHER} DBUS_SESSION_BUS_ADDRESS"\n')
        with self.assertRaises(self.config.ConfigurationError):
            self.config.parse_and_update('rc_env_allow="FOO"\nrc_env_allow="BAR"\n')

    def test_literal_assignment_not_shell_case_execution(self):
        literal, _ = self.config.parse_and_update('rc_env_allow="FOO"\n')
        assignment = [s for s in literal.splitlines() if s.startswith("rc_env_allow=")]
        self.assertEqual(len(assignment), 1)
        self.assertRegex(assignment[0], r'^rc_env_allow="[A-Z_ ]+"$')



class TemplateTests(unittest.TestCase):
    def test_packaged_global_entry_point_and_user_override_contract(self):
        global_config = ROOT / "conf.d/joetoo-kwind"
        user_config = ROOT / "user-conf.d/joetoo-kwind"
        service = ROOT / "user-init.d/joetoo-kwind"
        self.assertIn('JOETOO_KWIND_EXEC="/usr/libexec/joetoo-kwind"', global_config.read_text())
        self.assertIn('[ -r /etc/user/conf.d/joetoo-kwind ]', global_config.read_text())
        self.assertIn('. /etc/user/conf.d/joetoo-kwind', global_config.read_text())
        self.assertIn('. /etc/conf.d/joetoo-kwind', service.read_text())
        self.assertNotIn('. /etc/conf.d/joetoo-kwind', user_config.read_text())
        subprocess.run(["sh", "-n", str(global_config)], check=True)
        subprocess.run(["sh", "-n", str(user_config)], check=True)

    def test_poc_override_wins_after_global_value_is_set(self):
        global_config = ROOT / "conf.d/joetoo-kwind"
        override = ROOT / "poc-user-conf.d/joetoo-kwind"
        with tempfile.TemporaryDirectory() as home:
            env = {**os.environ, "HOME": home}
            script = '. "$1"; . "$2"; printf "%s\\n" "$JOETOO_KWIND_EXEC"'
            proc = subprocess.run(
                ["sh", "-c", script, "test", str(global_config), str(override)],
                env=env, capture_output=True, text=True, check=True)
            self.assertEqual(proc.stdout.strip(), home + "/.local/libexec/joetoo-kwind")
        self.assertNotIn('JOETOO_KWIND_EXEC:-', override.read_text())

@unittest.skipIf(os.geteuid() == 0, "native file tests require ordinary user, not root")
class InstallerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = {**os.environ, "HOME": str(self.home)}
        self.env.pop("XDG_CONFIG_HOME", None)
        self.env.pop("XDG_STATE_HOME", None)
        self.archive = self.home / ".local/state/joetoo-kwin/archive"
        # Never query real OpenRC: a temporary HOME does not isolate rc-service.
        # Default to an inactive service; only the running-service test overrides it.
        self.bindir = self.home / "bin"
        self.bindir.mkdir()
        self.rc_service = self.bindir / "rc-service"
        self.rc_service.write_text('#!/bin/sh\nexit 3\n')
        self.rc_service.chmod(0o755)
        self.env["PATH"] = str(self.bindir) + os.pathsep + self.env.get("PATH", "")
        self.service = self.home / ".config/rc/init.d/joetoo-kwind"
        self.daemon = self.home / ".local/libexec/joetoo-kwind"
        self.override = self.home / ".config/rc/conf.d/joetoo-kwind"
        self.conf = self.home / ".config/rc/rc.conf"
        self.rdp_module = self.home / ".local/libexec/joetoo_kwin_rdp_launch.py"
        self.rdp_target = self.home / ".local/libexec/joetoo_kwin_rdp_target.py"
        self.vnc_modules = [self.home / '.local/libexec' / name for name in
                            ('joetoo_kwin_vnc_identity.py', 'joetoo_kwin_vnc_target.py',
                             'joetoo_kwin_vnc_launch.py')]

    def run_tool(self, tool, arg):
        return subprocess.run([str(tool), arg], env=self.env, capture_output=True, text=True)

    def test_full_install_makes_both_directories_and_literal_rc_conf(self):
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.service.read_bytes(), (ROOT / 'user-init.d/joetoo-kwind').read_bytes())
        self.assertEqual(self.daemon.read_bytes(), (ROOT / 'libexec/joetoo-kwind').read_bytes())
        self.assertEqual(self.override.read_bytes(), (ROOT / 'poc-user-conf.d/joetoo-kwind').read_bytes())
        self.assertEqual(self.conf.read_text(), 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"\n')
        self.assertIn('Installed eleven user-owned', p.stdout)
        self.assertEqual(self.rdp_module.read_bytes(), (ROOT / 'libexec' / self.rdp_module.name).read_bytes())
        self.assertEqual(self.rdp_module.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.rdp_module.stat().st_uid, os.geteuid())
        for module in self.vnc_modules:
            self.assertEqual(module.read_bytes(), (ROOT / 'libexec' / module.name).read_bytes())
            self.assertEqual(module.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        self.assertEqual(self.run_tool(CONFIG_TOOL, "--check").returncode, 0)
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--install").returncode, 1)


    def test_vnc_missing_or_outdated_modules_fail_nonmutating_check(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        config = self.conf.read_bytes()
        for module in self.vnc_modules:
            with self.subTest(module=module.name):
                original = module.read_bytes()
                module.unlink()
                check = self.run_tool(INSTALL_TOOL, '--check')
                self.assertEqual(check.returncode, 1)
                self.assertIn('Missing or outdated: ' + str(module), check.stdout)
                self.assertFalse(module.exists())
                module.write_text('# outdated module\n')
                before = module.stat().st_mtime_ns
                self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)
                self.assertEqual(module.read_text(), '# outdated module\n')
                self.assertEqual(module.stat().st_mtime_ns, before)
                self.assertEqual(self.conf.read_bytes(), config)
                module.write_bytes(original)
                module.chmod(0o644)
                self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_upgrade_six_file_install_adds_runtime_modules_and_is_content_idempotent(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        for module in [*self.vnc_modules, self.rdp_module]:
            module.unlink()
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)
        for _ in range(2):
            update = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            for module in [*self.vnc_modules, self.rdp_module]:
                self.assertEqual(module.read_bytes(), (ROOT / 'libexec' / module.name).read_bytes())
                self.assertEqual(module.stat().st_mode & 0o777, 0o644)
            self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_vnc_update_preserves_previous_modules_in_backups(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        for module in self.vnc_modules:
            module.write_text('# previous ' + module.name + '\n')
            module.chmod(0o600)
        update = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
        for module in self.vnc_modules:
            backups = list(self.archive.glob('vnc_' + module.stem.removeprefix('joetoo_kwin_vnc_') + '/*/' + module.name))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), '# previous ' + module.name + '\n')
            self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
            self.assertEqual(module.read_bytes(), (ROOT / 'libexec' / module.name).read_bytes())
            self.assertEqual(module.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def archived(self, component, name):
        return sorted(self.archive.glob(component + '/*/' + name))

    def test_unchanged_update_creates_no_archive_or_legacy_backups(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        for _ in range(2):
            result = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.archive.exists())
        self.assertFalse(list(self.home.rglob('*.before-update.*')))

    def test_mode_only_mismatches_checked_and_archived_for_all_ten_components(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        installed = {
            'service': (self.service, 0o755), 'daemon': (self.daemon, 0o755),
            'override': (self.override, 0o644),
            'rdp_launch': (self.rdp_module, 0o644),
            'rdp_target': (self.rdp_target, 0o644),
            'registry': (self.daemon.with_name('joetoo_kwin_registry.py'), 0o644),
            'resident': (self.home / '.local/share/joetoo-kwin/joetoo-kwin-resident.js', 0o644),
            'cli': (self.home / '.local/bin/joetoo-kwin', 0o755),
            **{key: (path, 0o644) for key, path in zip(
                ('vnc_identity', 'vnc_target', 'vnc_launch'), self.vnc_modules)}}
        contents = {key: path.read_bytes() for key, (path, _) in installed.items()}
        times = (1600000000000000000, 1600000001000000000)
        for path, _ in installed.values():
            path.chmod(0o600)
            os.utime(path, ns=times)
        check = self.run_tool(INSTALL_TOOL, '--check')
        self.assertEqual(check.returncode, 1, check.stdout + check.stderr)
        self.assertFalse(self.archive.exists())
        for path, _ in installed.values():
            self.assertIn('Missing or outdated: ' + str(path), check.stdout)
            self.assertEqual(path.stat().st_mode & 0o7777, 0o600)
            self.assertEqual(path.stat().st_mtime_ns, times[1])
            # --check may read bytes; restore a known access time for the update.
            os.utime(path, ns=times)
        update = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
        for component, (path, expected) in installed.items():
            saved, = self.archived(component, path.name)
            record = json.loads((saved.parent / 'provenance.json').read_text())
            self.assertEqual(saved.read_bytes(), contents[component])
            self.assertEqual(record['mode'], '0o600')
            self.assertEqual((record['atime_ns'], record['mtime_ns']), times)
            self.assertEqual(path.read_bytes(), contents[component])
            self.assertEqual(path.stat().st_mode & 0o7777, expected)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_timestamp_only_drift_does_not_archive_or_add_provenance(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        os.utime(self.daemon, ns=(1500000000000000000, 1500000001000000000))
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertFalse(self.archive.exists())
        self.daemon.chmod(0o600)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        saved, = self.archived('daemon', self.daemon.name)
        before = {p.name: p.read_bytes() for p in saved.parent.iterdir()}
        for offset in (0, 1000000000):
            os.utime(self.daemon, ns=(1500000000000000000 + offset, 1500000001000000000 + offset))
            self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)
            self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual({p.name: p.read_bytes() for p in saved.parent.iterdir()}, before)

    def test_mode_only_changes_reuse_payload_with_distinct_metadata(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        module = self.vnc_modules[0]
        content = module.read_bytes()
        for mode in (0o600, 0o640):
            module.chmod(mode)
            result = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(module.stat().st_mode & 0o7777, 0o644)
        saved, = self.archived('vnc_identity', module.name)
        self.assertEqual(saved.read_bytes(), content)
        records = [json.loads(p.read_text()) for p in saved.parent.glob('provenance*.json')]
        self.assertEqual({r['mode'] for r in records}, {'0o600', '0o640'})
        self.assertEqual(len(records), 2)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--update').returncode, 0)
        self.assertEqual(len(list(saved.parent.iterdir())), 3)

    def test_mode_only_archive_failure_does_not_correct_mode_without_backup(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.chmod(0o600)
        self.inject_archive_python('import os\n'
                                   'def fail(*args, **kwargs):\n'
                                   '    raise OSError("injected metadata archive failure")\n'
                                   'os.link = fail\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('injected metadata archive failure', result.stderr)
        self.assertEqual(self.daemon.stat().st_mode & 0o7777, 0o600)
        self.assertEqual(self.archived('daemon', self.daemon.name), [])

    def test_archive_all_ten_components_and_same_named_files_are_separate(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        installed = {
            'service': self.service, 'daemon': self.daemon, 'override': self.override,
            'rdp_launch': self.rdp_module,
            'rdp_target': self.rdp_target,
            'registry': self.daemon.with_name('joetoo_kwin_registry.py'),
            'resident': self.home / '.local/share/joetoo-kwin/joetoo-kwin-resident.js',
            'cli': self.home / '.local/bin/joetoo-kwin',
            **dict(zip(('vnc_identity', 'vnc_target', 'vnc_launch'), self.vnc_modules))}
        for path in installed.values():
            path.write_bytes(b'previous version\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for component, path in installed.items():
            saved, = self.archived(component, path.name)
            self.assertEqual(saved.read_bytes(), b'previous version\n')
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
        (self.archive / 'daemon').mkdir(mode=0o700)
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

    def archived_daemon_fixture(self):
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
        wrapper.write_text('#!' + sys.executable + '\n'
                           'import sys\nsys.argv.pop(1)\n' + preamble + '\n'
                           'exec(compile(sys.stdin.read(), "archive", "exec"))\n')
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
                preamble = ('import os\nfrom pathlib import Path\n'
                            'original_stat = Path.stat\n'
                            'def changed_stat(path, *args, **kwargs):\n'
                            '    info = original_stat(path, *args, **kwargs)\n'
                            f'    if str(path) == {str(target)!r}:\n'
                            '        fields = list(info)\n'
                            '        fields[4] = os.geteuid() + 1\n'
                            '        return os.stat_result(fields)\n'
                            '    return info\n'
                            'Path.stat = changed_stat\n')
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
        self.inject_archive_python('import os\n'
                                   'def fail(*args, **kwargs):\n'
                                   '    raise OSError("injected record publish failure")\n'
                                   'os.link = fail\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('injected record publish failure', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        self.assertEqual(saved.read_bytes(), b'previous version')
        self.assertEqual((saved.parent / 'provenance.json').read_bytes(), first)
        self.assertEqual(len(list(saved.parent.iterdir())), 2)

    def test_install_failure_keeps_recoverable_archive_and_check_detects_failure(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'previous version')
        # Fail the existing install command, without invoking a real service.
        failing = self.bindir / 'install'
        failing.write_text('#!/bin/sh\nexit 73\n')
        failing.chmod(0o755)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 73)
        self.assertEqual(self.daemon.read_bytes(), b'previous version')
        saved, = self.archived('daemon', self.daemon.name)
        self.assertEqual(saved.read_bytes(), b'previous version')
        self.assertFalse(list(self.archive.rglob('.pending-*')))
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)

    def test_archive_copy_failure_removes_staging_and_keeps_active_file(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.daemon.write_bytes(b'old daemon')
        # Inject a copy error only into the installer's embedded archive code.
        # This tests the real shell failure boundary without filling a disk.
        wrapper = self.bindir / 'python3'
        wrapper.write_text('#!' + sys.executable + '\n'
                           'import shutil, sys\n'
                           'sys.argv.pop(1)  # Match python3 - argv semantics.\n'
                           'def fail(*args, **kwargs):\n'
                           '    raise OSError("injected copy failure")\n'
                           'shutil.copy2 = fail\n'
                           'exec(compile(sys.stdin.read(), "archive", "exec"))\n')
        wrapper.chmod(0o755)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('injected copy failure', result.stderr)
        self.assertEqual(self.daemon.read_bytes(), b'old daemon')
        self.assertFalse(list(self.archive.rglob('.pending-*')))
        self.assertEqual(self.archived('daemon', self.daemon.name), [])

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
        self.rc_service.write_text('#!/bin/sh\nexit 0\n')
        result = self.run_tool(INSTALL_TOOL, '--preview-legacy-backups')
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(records), 11)
        daemon = next(r for r in records if r['component'] == 'daemon')
        self.assertEqual(sorted(v['copies'] for v in daemon['versions']), [1, 2])
        self.assertEqual({p for v in daemon['versions'] for p in v['paths']}, set(map(str, files)))
        self.assertEqual([(p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns) for p in files], before)
        self.assertFalse(self.archive.exists())
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_vnc_symlinks_rejected_before_install_update_or_check(self):
        sentinel = self.home / 'sentinel'
        sentinel.write_text('preserve\n')
        self.vnc_modules[0].parent.mkdir(parents=True)
        for module in self.vnc_modules:
            with self.subTest(module=module.name):
                module.symlink_to(sentinel)
                for action in ('--install', '--update', '--check'):
                    result = self.run_tool(INSTALL_TOOL, action)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Refusing unexpected installation destination', result.stderr)
                    self.assertTrue(module.is_symlink())
                    self.assertEqual(sentinel.read_text(), 'preserve\n')
                    self.assertFalse(self.service.exists())
                    self.assertFalse(self.conf.exists())
                module.unlink()

    def test_running_service_blocks_vnc_module_update_without_backups(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.vnc_modules[0].write_text('# old module\n')
        before = [path.read_bytes() for path in self.vnc_modules]
        daemon = self.daemon.read_bytes()
        self.rc_service.write_text('#!/bin/sh\nexit 0\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Stop the user service', result.stderr)
        self.assertEqual([path.read_bytes() for path in self.vnc_modules], before)
        self.assertEqual(self.daemon.read_bytes(), daemon)
        self.assertFalse(list(self.home.rglob('*.before-update.*')))


    def test_upgrade_detects_missing_graphical_environment_and_preserves_settings(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        original='other="yes"\nrc_env_allow="EXISTING DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"\n'
        self.conf.write_text(original)
        self.conf.chmod(0o640)
        before=self.conf.stat()
        self.assertEqual(self.run_tool(CONFIG_TOOL, '--check').returncode, 1)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)
        self.assertEqual(self.conf.read_text(), original)
        self.assertEqual(self.conf.stat().st_mtime_ns, before.st_mtime_ns)
        result=self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        expected='other="yes"\nrc_env_allow="EXISTING DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"\n'
        self.assertEqual(self.conf.read_text(),expected)
        self.assertEqual(self.conf.stat().st_mode & 0o777, 0o640)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode,0)
        updated=self.conf.stat()
        self.assertEqual(self.run_tool(CONFIG_TOOL, '--apply').returncode,0)
        self.assertEqual(self.conf.stat().st_ino,updated.st_ino)
        self.assertEqual(self.conf.stat().st_mtime_ns,updated.st_mtime_ns)
        self.assertEqual(self.conf.read_text(),expected)

    def test_unset_xauthority_is_allowed_without_recording_session_values(self):
        self.env.pop('XAUTHORITY',None)
        self.env['DISPLAY']=':97'
        result=self.run_tool(INSTALL_TOOL, '--install')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(self.run_tool(CONFIG_TOOL,'--check').returncode,0)
        self.assertEqual(self.run_tool(INSTALL_TOOL,'--check').returncode,0)
        literal=self.conf.read_text()
        self.assertIn('DISPLAY XAUTHORITY',literal)
        self.assertNotIn(':97',literal)
        self.assertNotIn(str(self.home),literal)


    def test_override_missing_causes_check_failure(self):
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.override.unlink()
        p = self.run_tool(INSTALL_TOOL, "--check")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Missing or outdated", p.stdout)

    def test_update_backs_up_existing_user_override(self):
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.override.write_text("CUSTOM=previous\\n")
        p = self.run_tool(INSTALL_TOOL, "--update")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        backups = list(self.archive.glob("override/*/joetoo-kwind"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "CUSTOM=previous\\n")
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)

    def test_rejects_symlink_user_override(self):
        self.override.parent.mkdir(parents=True)
        target = self.home / "sentinel"
        target.write_text("preserve\\n")
        self.override.symlink_to(target)
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.service.exists())
        self.assertFalse(self.daemon.exists())
        self.assertEqual(target.read_text(), "preserve\\n")

    def test_preserves_existing_rc_conf_settings_and_repair_upgrade(self):
        self.conf.parent.mkdir(parents=True)
        self.conf.write_text('other="yes"\nrc_env_allow="EXISTING"\n')
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.conf.read_text(),
                         'other="yes"\nrc_env_allow="EXISTING DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC DISPLAY XAUTHORITY"\n')
        self.service.write_text('OLD\n')
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        p = self.run_tool(INSTALL_TOOL, "--update")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        backups = list(self.archive.glob('service/*/joetoo-kwind'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'OLD\n')

    def test_refuse_symlink_configuration_without_installing(self):
        self.conf.parent.mkdir(parents=True)
        target = self.home / 'elsewhere'
        target.write_text('SAFE\n')
        self.conf.symlink_to(target)
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.service.exists())
        self.assertFalse(self.daemon.exists())
        self.assertEqual(target.read_text(), 'SAFE\n')

    def test_check_is_non_mutating(self):
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        self.assertFalse(self.conf.exists())
        self.assertFalse(self.service.exists())
        self.assertFalse(self.daemon.exists())
        self.assertFalse(self.override.exists())

    def test_refuses_replacing_running_service(self):
        # Invert the default fixture: pretend the service is running.
        self.rc_service.write_text('#!/bin/sh\nexit 0\n')
        p = self.run_tool(INSTALL_TOOL, '--install')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Stop the user service', p.stderr)
        self.assertFalse(self.conf.exists())
        self.assertFalse(self.service.exists())
        self.assertFalse(self.daemon.exists())

    def test_xdg_config_home_override(self):
        config_home = self.home / 'custom-xdg'
        self.env['XDG_CONFIG_HOME'] = str(config_home)
        p = self.run_tool(INSTALL_TOOL, '--install')
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue((config_home / 'rc/init.d/joetoo-kwind').is_file())
        self.assertTrue((config_home / 'rc/rc.conf').is_file())
        self.assertTrue(self.daemon.is_file())
        self.assertTrue((config_home / 'rc/conf.d/joetoo-kwind').is_file())


    def test_sdl_missing_outdated_or_wrong_mode_fails_nonmutating_check(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        original = self.rdp_module.read_bytes()
        for kind in ('missing', 'outdated', 'mode'):
            with self.subTest(kind=kind):
                self.rdp_module.unlink()
                if kind != 'missing':
                    self.rdp_module.write_bytes(b'# old SDL adapter\n' if kind == 'outdated' else original)
                    self.rdp_module.chmod(0o600 if kind == 'mode' else 0o644)
                before = self.rdp_module.read_bytes() if self.rdp_module.exists() else None
                check = self.run_tool(INSTALL_TOOL, '--check')
                self.assertEqual(check.returncode, 1, check.stdout + check.stderr)
                self.assertIn('Missing or outdated: ' + str(self.rdp_module), check.stdout)
                self.assertEqual(self.rdp_module.read_bytes() if self.rdp_module.exists() else None, before)
                self.assertFalse(self.archive.exists())
                if not self.rdp_module.exists(): self.rdp_module.write_bytes(original)

    def test_rdp_target_missing_outdated_mode_and_archival_lifecycle(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        source = (ROOT / 'libexec' / self.rdp_target.name).read_bytes()
        self.assertEqual(self.rdp_target.read_bytes(), source)
        self.assertEqual(self.rdp_target.stat().st_uid, os.geteuid())
        self.assertEqual(self.rdp_target.stat().st_mode & 0o7777, 0o644)
        for state in ('missing', 'outdated', 'mode'):
            with self.subTest(state=state):
                self.rdp_target.unlink()
                if state != 'missing':
                    self.rdp_target.write_bytes(b'# old parser\n' if state == 'outdated' else source)
                    self.rdp_target.chmod(0o600 if state == 'mode' else 0o644)
                check = self.run_tool(INSTALL_TOOL, '--check')
                self.assertEqual(check.returncode, 1)
                self.assertIn('Missing or outdated: ' + str(self.rdp_target), check.stdout)
                update = self.run_tool(INSTALL_TOOL, '--update')
                self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
                self.assertEqual(self.rdp_target.read_bytes(), source)
                self.assertEqual(self.rdp_target.stat().st_mode & 0o7777, 0o644)
                self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)
        saved = self.archived('rdp_target', self.rdp_target.name)
        self.assertTrue(any(path.read_bytes() == b'# old parser\n' for path in saved))

    def test_sdl_nine_file_upgrade_and_repeat_update_idempotent(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.rdp_module.unlink()  # Simulate the previously complete nine-file install.
        old = {p: p.read_bytes() for p in (self.daemon, self.service, self.override, *self.vnc_modules)}
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 1)
        for _ in range(2):
            result = self.run_tool(INSTALL_TOOL, '--update')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Installed eleven user-owned', result.stdout)
            self.assertEqual(self.rdp_module.read_bytes(), (ROOT / 'libexec' / self.rdp_module.name).read_bytes())
            self.assertEqual(self.rdp_module.stat().st_mode & 0o7777, 0o644)
            self.assertEqual(self.rdp_module.stat().st_uid, os.geteuid())
            self.assertEqual({p: p.read_bytes() for p in old}, old)
            self.assertFalse(self.archive.exists())
            self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_sdl_update_archives_old_bytes_and_metadata_before_replacement(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        old = b'# prior SDL adapter\n'
        self.rdp_module.write_bytes(old)
        self.rdp_module.chmod(0o600)
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        saved, = self.archived('rdp_launch', self.rdp_module.name)
        record = json.loads((saved.parent / 'provenance.json').read_text())
        self.assertEqual(saved.read_bytes(), old)
        self.assertEqual(record['mode'], '0o600')
        self.assertEqual(record['installed_path'], str(self.rdp_module))
        self.assertEqual(saved.stat().st_mode & 0o7777, 0o600)
        self.assertEqual(saved.stat().st_uid, os.geteuid())
        self.assertEqual(self.rdp_module.stat().st_mode & 0o7777, 0o644)
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--check').returncode, 0)

    def test_sdl_symlinks_rejected_for_all_installer_actions(self):
        self.rdp_module.parent.mkdir(parents=True)
        target = self.home / 'unrelated'
        target.write_bytes(b'untouched')
        self.rdp_module.symlink_to(target)
        for action in ('--install', '--update', '--check'):
            result = self.run_tool(INSTALL_TOOL, action)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(self.rdp_module.is_symlink())
            self.assertEqual(target.read_bytes(), b'untouched')
            self.assertFalse(self.daemon.exists())
            self.assertFalse(self.archive.exists())

    def test_sdl_archive_failure_keeps_active_adapter_and_other_files(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.rdp_module.write_bytes(b'# prior SDL adapter\n')
        before = {p: p.read_bytes() for p in (self.rdp_module, self.daemon, self.service, *self.vnc_modules)}
        self.inject_archive_python('import shutil\n'
            'def fail(*args, **kwargs):\n'
            '    raise OSError("injected SDL archive failure")\n'
            'shutil.copy2 = fail\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('injected SDL archive failure', result.stderr)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_running_service_blocks_sdl_update_without_archive(self):
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        self.rdp_module.write_bytes(b'# old SDL module\n')
        self.rc_service.write_text('#!/bin/sh\nexit 0\n')
        result = self.run_tool(INSTALL_TOOL, '--update')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.rdp_module.read_bytes(), b'# old SDL module\n')
        self.assertFalse(self.archive.exists())

    def test_sdl_foreign_ownership_is_not_current(self):
        import shutil
        self.assertEqual(self.run_tool(INSTALL_TOOL, '--install').returncode, 0)
        # Simulate stat's UID result without chown or privileged test actions.
        real_stat = shutil.which('stat')
        wrapper = self.bindir / 'stat'
        wrapper.write_text('#!' + sys.executable + '\nimport os, sys\n'
            'if sys.argv[1:3] == ["-c", "%u"] and sys.argv[-1] == ' + repr(str(self.rdp_module)) + ':\n'
            '    print(' + str(os.geteuid() + 1) + ')\n'
            'else:\n    os.execv(' + repr(real_stat) + ', [' + repr(real_stat) + '] + sys.argv[1:])\n')
        wrapper.chmod(0o755)
        before = self.rdp_module.read_bytes()
        check = self.run_tool(INSTALL_TOOL, '--check')
        self.assertEqual(check.returncode, 1)
        self.assertIn('Missing or outdated: ' + str(self.rdp_module), check.stdout)
        self.assertEqual(self.rdp_module.read_bytes(), before)
        self.assertFalse(self.archive.exists())


if __name__ == '__main__':
    unittest.main()
