#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-destructive tests of the opt-in OpenRC user configuration helper."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools' / 'joetoo-kwind-configure-openrc-user'


class UserOpenRCConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.conf = self.root / 'rc' / 'rc.conf'
        self.env = dict(os.environ, XDG_CONFIG_HOME=str(self.root), HOME=str(self.root))
        # This test suite runs without OpenRC or privilege escalation. Test id mock
        # models the non-root invocation, while ownership checks use the actual UID.
        self.bindir = self.root / 'bin'
        self.bindir.mkdir()
        (self.bindir / 'id').write_text('#!/bin/sh\nprintf "%s\\n" "$JOETOO_TEST_UID"\n')
        (self.bindir / 'id').chmod(0o755)
        self.env['JOETOO_TEST_UID'] = str(os.getuid() or 1000)
        self.env['PATH'] = f'{self.bindir}:{os.environ.get("PATH", "")}'

    def run_script(self, action):
        return subprocess.run([str(SCRIPT), action], env=self.env,
                              text=True, capture_output=True)

    def effective_allowlist(self):
        p = subprocess.run(['sh', '-c', '. "$1"; printf "%s\\n" "$rc_env_allow"',
                            'sh', str(self.conf)], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip().split()

    def test_check_is_read_only_and_apply_is_idempotent(self):
        self.assertEqual(self.run_script('--check').returncode, 1)
        self.assertFalse(self.conf.exists())
        self.assertEqual(self.run_script('--apply').returncode, 0)
        first = self.conf.read_bytes()
        self.assertEqual(self.run_script('--apply').returncode, 0)
        self.assertEqual(self.conf.read_bytes(), first)
        self.assertEqual(self.run_script('--check').returncode, 0)
        self.assertEqual(self.effective_allowlist(), ['DBUS_SESSION_BUS_ADDRESS', 'JOETOO_KWIND_EXEC'])

    def test_preserves_other_entries_and_existing_allowed_names(self):
        self.conf.parent.mkdir(parents=True)
        self.conf.write_text('rc_env_allow="FOO DBUS_SESSION_BUS_ADDRESS"\nother_setting="safe"\n')
        self.assertEqual(self.run_script('--apply').returncode, 0)
        self.assertIn('other_setting="safe"', self.conf.read_text())
        self.assertEqual(self.effective_allowlist(), ['FOO', 'DBUS_SESSION_BUS_ADDRESS', 'JOETOO_KWIND_EXEC'])

    def test_rejects_symlink_without_mutating_target(self):
        target = self.root / 'real.conf'
        target.write_text('rc_env_allow="FOO"\n')
        self.conf.parent.mkdir(parents=True)
        self.conf.symlink_to(target)
        self.assertNotEqual(self.run_script('--apply').returncode, 0)
        self.assertEqual(target.read_text(), 'rc_env_allow="FOO"\n')

    def test_rejects_partial_managed_block(self):
        self.conf.parent.mkdir(parents=True)
        self.conf.write_text('# BEGIN joetoo-kwind Step 1.2a environment\n')
        self.assertNotEqual(self.run_script('--apply').returncode, 0)
        self.assertEqual(self.conf.read_text(), '# BEGIN joetoo-kwind Step 1.2a environment\n')

    def test_refuses_root(self):
        self.env['JOETOO_TEST_UID'] = '0'
        self.assertNotEqual(self.run_script('--apply').returncode, 0)
        self.assertFalse(self.conf.exists())


if __name__ == '__main__':
    unittest.main()
