#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.2a OpenRC user-config and complete local-install regression tests.

Subprocess integration runs must execute as a non-root user in a disposable HOME.
No real OpenRC service is started, stopped, configured system-wide, or reloaded.
"""

import importlib.machinery
import importlib.util
import os
from pathlib import Path
import re
import subprocess
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
        self.assertEqual(updated, 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"\n')
        self.assertEqual(names, ["DBUS_SESSION_BUS_ADDRESS", "JOETOO_KWIND_EXEC"])
        self.assertEqual(self.config.parse_and_update(updated)[0], updated)
        self.assertNotIn("case ", updated)

    def test_preserve_existing_literal_allowlist_and_unrelated_settings(self):
        original = 'rc_some_setting="yes"\nrc_env_allow="FOO DBUS_SESSION_BUS_ADDRESS"\n'
        updated, names = self.config.parse_and_update(original)
        self.assertEqual(updated, 'rc_some_setting="yes"\nrc_env_allow="FOO DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"\n')
        self.assertEqual(names, ["FOO", "DBUS_SESSION_BUS_ADDRESS", "JOETOO_KWIND_EXEC"])
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
        self.assertEqual(updated.strip(), 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"')

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

    def run_tool(self, tool, arg):
        return subprocess.run([str(tool), arg], env=self.env, capture_output=True, text=True)

    def test_full_install_makes_both_directories_and_literal_rc_conf(self):
        p = self.run_tool(INSTALL_TOOL, "--install")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.service.read_bytes(), (ROOT / 'user-init.d/joetoo-kwind').read_bytes())
        self.assertEqual(self.daemon.read_bytes(), (ROOT / 'libexec/joetoo-kwind').read_bytes())
        self.assertEqual(self.override.read_bytes(), (ROOT / 'poc-user-conf.d/joetoo-kwind').read_bytes())
        self.assertEqual(self.conf.read_text(), 'rc_env_allow="DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"\n')
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        self.assertEqual(self.run_tool(CONFIG_TOOL, "--check").returncode, 0)
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--install").returncode, 1)


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
        backups = list(self.override.parent.glob("joetoo-kwind.before-step1.2a-update.*"))
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
                         'other="yes"\nrc_env_allow="EXISTING DBUS_SESSION_BUS_ADDRESS JOETOO_KWIND_EXEC"\n')
        self.service.write_text('OLD\n')
        self.assertNotEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        p = self.run_tool(INSTALL_TOOL, "--update")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.run_tool(INSTALL_TOOL, "--check").returncode, 0)
        backups = list(self.service.parent.glob('joetoo-kwind.before-step1.2a-update.*'))
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


if __name__ == '__main__':
    unittest.main()
