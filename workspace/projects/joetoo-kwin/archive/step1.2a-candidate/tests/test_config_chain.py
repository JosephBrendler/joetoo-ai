#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated source-order tests for the explicit joetoo-kwind config chain.

The test uses disposable copies of the configs; it never reads/writes /etc.
OpenRC's native RC_PATH processing must still be verified by the maintainer.
"""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / 'conf.d/joetoo-kwind'
SERVICE = ROOT / 'user-init.d/joetoo-kwind'


class ConfigChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.system_user = self.root / 'etc-user-conf'
        self.global_config = self.root / 'global-conf'
        self.service = self.root / 'service'
        self.xdg = self.root / 'xdg'
        self.env = {**os.environ, 'HOME': str(self.root),
                    'XDG_CONFIG_HOME': str(self.xdg),
                    'XDG_RUNTIME_DIR': str(self.root)}
        self.global_config.write_text(GLOBAL.read_text().replace(
            '/etc/user/conf.d/joetoo-kwind', str(self.system_user)))
        self.service.write_text(SERVICE.read_text().replace(
            '/etc/conf.d/joetoo-kwind', str(self.global_config)))
        self.system_user.write_text('# No user-service override\n')

    def resolve(self, preloaded=''):
        script = preloaded + '. "$1"; printf "%s\\n" "$command"'
        return subprocess.run(['sh', '-c', script, 'sh', str(self.service)],
                              env=self.env, capture_output=True, text=True,
                              check=True, timeout=5).stdout.strip()

    def test_global_default(self):
        self.assertEqual(self.resolve(), '/usr/libexec/joetoo-kwind')

    def test_system_user_service_overrides_global(self):
        self.system_user.write_text('JOETOO_KWIND_EXEC="/tmp/override-by-admin"\n')
        self.assertEqual(self.resolve(), '/tmp/override-by-admin')

    def test_individual_user_overrides_both(self):
        self.system_user.write_text('JOETOO_KWIND_EXEC="/tmp/override-by-admin"\n')
        config = self.xdg / 'rc/conf.d/joetoo-kwind'
        config.parent.mkdir(parents=True)
        config.write_text('JOETOO_KWIND_EXEC="${HOME}/.local/libexec/joetoo-kwind"\n')
        # Simulate OpenRC having already sourced user conf.d before the service.
        preloaded = '. "' + str(self.system_user) + '"; . "' + str(config) + '"; '
        self.assertEqual(self.resolve(preloaded), str(self.root / '.local/libexec/joetoo-kwind'))

    def test_obsolete_bridge_cannot_recurse_forever(self):
        self.system_user.write_text('. "' + str(self.global_config) + '"\n')
        self.assertEqual(self.resolve(), '/usr/libexec/joetoo-kwind')

    def test_xdg_unset_falls_back_to_home_dot_config(self):
        self.env.pop('XDG_CONFIG_HOME', None)
        config = self.root / '.config/rc/conf.d/joetoo-kwind'
        config.parent.mkdir(parents=True)
        config.write_text('JOETOO_KWIND_EXEC="/tmp/home-override"\n')
        self.assertEqual(self.resolve(), '/tmp/home-override')

    def test_missing_home_refuses_start_without_root_dot_config(self):
        self.env.pop('HOME', None)
        self.env.pop('XDG_CONFIG_HOME', None)
        # eerror is an OpenRC function; stub it in this isolated test.
        script = '. "$1"; id() { printf "1234\n"; }; '
        script += 'eerror() { printf "%s\n" "$*" >&2; }; start_pre'
        result = subprocess.run(['sh', '-c', script, 'sh', str(self.service)],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('HOME must be set', result.stderr)

    def test_relative_home_refuses_start(self):
        self.env['HOME'] = 'relative-home'
        self.env.pop('XDG_CONFIG_HOME', None)
        script = '. "$1"; id() { printf "1234\n"; }; '
        script += 'eerror() { printf "%s\n" "$*" >&2; }; start_pre'
        result = subprocess.run(['sh', '-c', script, 'sh', str(self.service)],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('HOME must be set', result.stderr)

    def test_relative_xdg_config_home_refuses_start(self):
        self.env['XDG_CONFIG_HOME'] = 'relative-config'
        script = '. "$1"; id() { printf "1234\n"; }; '
        script += 'eerror() { printf "%s\n" "$*" >&2; }; start_pre'
        result = subprocess.run(['sh', '-c', script, 'sh', str(self.service)],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('XDG_CONFIG_HOME must be absolute', result.stderr)

    def test_pseudo_boolean_guard_is_canonical_and_reentrant(self):
        text = GLOBAL.read_text()
        self.assertIn('TRUE=0', text)
        self.assertIn('FALSE=""', text)
        self.assertIn('_JOETOO_KWIND_CONFIG_LOADING=$TRUE', text)
        self.assertIn('[ ! "${_JOETOO_KWIND_CONFIG_LOADING:-${FALSE}}" ]', text)
        # A legacy bridge re-sourcing global while loading is already tested
        # above; verify that the sentinel does not persist after completion.
        script = '. "$1"; printf "<%s>\n" "${_JOETOO_KWIND_CONFIG_LOADING-unset}"'
        run = subprocess.run(['sh', '-c', script, 'sh', str(self.global_config)],
                             env=self.env, capture_output=True, text=True, check=True)
        self.assertEqual(run.stdout.strip(), '<unset>')

    def test_uninstalled_global_uses_openrc_loaded_user_override(self):
        self.global_config.unlink()
        config = self.xdg / 'rc/conf.d/joetoo-kwind'
        config.parent.mkdir(parents=True)
        config.write_text('JOETOO_KWIND_EXEC="/tmp/poc-only-broker"\n')
        self.assertEqual(self.resolve('. "' + str(config) + '"; '), '/tmp/poc-only-broker')


if __name__ == '__main__':
    unittest.main()
