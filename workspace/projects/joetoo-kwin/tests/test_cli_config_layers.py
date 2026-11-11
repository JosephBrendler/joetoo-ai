# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real CLI loading with disposable defaults/plans and forbidden-operation spies."""
import os
from pathlib import Path
import unittest
from test_step1_5a_plan import PlannerHarness


class ConfigLayersTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.user_defaults = Path(self.env['XDG_CONFIG_HOME']) / 'joetoo-kwin/defaults.conf'
        self.user_defaults.parent.mkdir(parents=True)
        self.user_plan = self.user_defaults.with_name('joetoo-kwin.conf')
        self.system_plan = self.folder / 'system-plan.conf'
        self.client.write_text(self.client.read_text().replace(
            '/etc/joetoo-kwin/joetoo-kwin.conf', str(self.system_plan)))

    def effective(self, extra='', args=()):
        self.write_config(['1|konsole|local|btop'], extra)
        return self.run_cli('-c', '-f', str(self.config), *(args or ('-v',)))

    def test_builtin_baseline_and_missing_optional_files(self):
        self.assertIn('terminal_width_percent=87', self.effective())
        self.assertFalse(self.system_defaults.exists())
        self.assertFalse(self.user_defaults.exists())

    def test_system_defaults(self):
        self.system_defaults.write_text('terminal_width_percent=80\n')
        self.assertIn('terminal_width_percent=80', self.effective())

    def test_user_over_system(self):
        self.system_defaults.write_text('terminal_width_percent=80\nterminal_gap_percent=3\n')
        self.user_defaults.write_text('terminal_width_percent=75\n')
        output = self.effective()
        self.assertIn('terminal_width_percent=75', output)
        self.assertIn('terminal_gap_percent=3', output)

    def test_explicit_plan_overrides_both_but_does_not_suppress_defaults(self):
        self.system_defaults.write_text('terminal_width_percent=80\n')
        self.user_defaults.write_text('terminal_gap_percent=4\n')
        self.user_plan.write_text('return 99\n')
        output = self.effective('terminal_width_percent=70\n')
        self.assertIn('terminal_width_percent=70', output)
        self.assertIn('terminal_gap_percent=4', output)

    def test_relative_f_is_anchored_to_cwd_not_path(self):
        import subprocess
        shadow=self.folder/'shadow';shadow.mkdir()
        marker=self.folder/'wrong-config-executed'
        (shadow/'layout.conf').write_text('touch "'+str(marker)+'"\nreturn 9\n')
        env={**self.env,'PATH':str(shadow)+os.pathsep+self.env['PATH']}
        run=subprocess.run(['bash',str(self.client),'-c','-f','layout.conf'],cwd=self.folder,
                           env=env,capture_output=True,text=True,timeout=20)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertFalse(marker.exists())
        self.assertFalse(self.calls.exists())

    def test_cli_verbosity_adjustment_is_last(self):
        self.system_defaults.write_text('verbosity=3\n')
        self.user_defaults.write_text('verbosity=4\n')
        self.assertIn('verbosity=6', self.effective('verbosity=5\n', ('-v',)))

    def test_default_user_and_system_plan_paths_are_compatible(self):
        self.system_defaults.write_text('terminal_width_percent=80\n')
        self.system_plan.write_text(self.config.read_text())
        self.assertIn('terminal_width_percent=80', self.run_cli('-c', '-v'))
        self.user_plan.write_text(self.config.read_text() + 'terminal_width_percent=70\n')
        self.assertIn('terminal_width_percent=70', self.run_cli('-c', '-v'))

    def test_relative_xdg_uses_home_dot_config(self):
        self.env['XDG_CONFIG_HOME'] = 'relative'
        root = Path(self.env['HOME']) / '.config/joetoo-kwin'
        root.mkdir(parents=True)
        (root / 'defaults.conf').write_text('terminal_width_percent=80\n')
        (root / 'joetoo-kwin.conf').write_text(self.config.read_text())
        self.assertIn('terminal_width_percent=80', self.run_cli('-c', '-v'))

    def test_each_present_bad_layer_fails_without_fallback_or_side_effects(self):
        for path in (self.system_defaults, self.user_defaults, self.config):
            for contents in ('screen_width=(\n', 'return 7\n', 'terminal_width_percent=999\n'):
                with self.subTest(path=path.name, contents=contents):
                    self.system_defaults.unlink(missing_ok=True)
                    self.user_defaults.unlink(missing_ok=True)
                    self.write_config(['1|konsole|local|btop'])
                    if path == self.config:
                        path.write_text(path.read_text() + contents)
                    else:
                        path.write_text(contents)
                    self.run_cli('-c', '-f', str(self.config), expected=2)
        self.system_defaults.unlink(missing_ok=True)
        self.user_defaults.unlink(missing_ok=True)

    def test_present_unreadable_nonfile_and_dangling_defaults_fail(self):
        for path in (self.system_defaults, self.user_defaults):
            for kind in ('unreadable', 'directory', 'dangling'):
                with self.subTest(layer=path, kind=kind):
                    if kind == 'unreadable':
                        path.write_text('# inaccessible\n'); path.chmod(0)
                    elif kind == 'directory': path.mkdir()
                    else: path.symlink_to(self.folder / 'missing')
                    try: self.run_cli('-c', '-f', str(self.config), expected=2)
                    finally:
                        if path.is_dir(): path.rmdir()
                        else: path.unlink()

    def test_unsearchable_optional_defaults_parent_is_not_treated_as_absent(self):
        self.user_defaults.write_text('terminal_width_percent=70\n')
        self.user_defaults.parent.chmod(0)
        try: self.run_cli('-c','-f',str(self.config),expected=2)
        finally: self.user_defaults.parent.chmod(0o700)

    def test_invalid_default_user_plan_never_falls_back(self):
        self.system_plan.write_text(self.config.read_text())
        self.user_plan.write_text('desktop_session_list=()\n')
        self.run_cli('-c', expected=2)

    def test_explicit_missing_plan_does_not_use_default_plan(self):
        self.user_plan.write_text(self.config.read_text())
        self.run_cli('-c', '-f', str(self.folder / 'absent'), expected=2)

    def test_syntax_is_checked_before_any_layer_runs(self):
        marker = self.folder / 'executed'
        self.system_defaults.write_text('touch "' + str(marker) + '"\n')
        self.user_defaults.write_text('broken=(\n')
        self.run_cli('-c', '-f', str(self.config), expected=2)
        self.assertFalse(marker.exists())

    def test_sparse_defaults_can_supply_required_values_and_plan_overrides_any(self):
        self.system_defaults.write_text('screen_width=1600\nscreen_height=900\nterminal_width_percent=75\n')
        self.config.write_text("desktop_session_list=('1|konsole|local|btop')\nterminal_width_percent=80\n")
        output = self.run_cli('-c', '-v', '-f', str(self.config))
        self.assertIn('screen_width=1600', output)
        self.assertIn('terminal_width_percent=80', output)

    def test_effective_values_validated_after_explicit_overrides(self):
        self.system_defaults.write_text('terminal_width_percent=999\n')
        self.assertIn('terminal_width_percent=80', self.effective('terminal_width_percent=80\n'))

    def test_loader_does_not_create_user_files(self):
        self.user_defaults.parent.rmdir()
        self.run_cli('-c', '-f', str(self.config))
        self.assertFalse(self.user_defaults.parent.exists())

    def test_layout_move_consumes_the_same_layers(self):
        from test_step1_5b_cli import MoveTests
        move=MoveTests()
        try:
            move.setUp()
            move.system_defaults.write_text('terminal_width_percent=80\n')
            user=Path(move.env['XDG_CONFIG_HOME'])/'joetoo-kwin/defaults.conf'
            user.parent.mkdir(parents=True);user.write_text('terminal_gap_percent=4\n')
            move.config.write_text('screen_width=1920\nscreen_height=1080\nterminal_width_percent=70\n')
            calls=move.run_move(['-f',str(move.config),'-m','l'])
            self.assertTrue(calls[0].endswith('0 19 54 634 918 true false false'),calls)
        finally: move.doCleanups()

    def test_layers_feed_real_rdp_preflight_before_confirmation(self):
        from test_rdp_configured import PlanTests
        launch=PlanTests()
        try:
            launch.setUp()
            launch.system_defaults.write_text('rdp_windowing_backend=x11\n')
            user=Path(launch.env['XDG_CONFIG_HOME'])/'joetoo-kwin/defaults.conf'
            user.parent.mkdir(parents=True);user.write_text('rdp_windowing_backend=wayland\n')
            launch.write_config(['1|sdl-freerdp|rdp|rdp://user@host.example'])
            self.assertEqual(launch.execute(2),[])  # Synthetic KWin is X11.
            launch.write_config(['1|sdl-freerdp|rdp|rdp://user@host.example'],extra='rdp_windowing_backend=x11\n')
            self.assertEqual(launch.execute(),['confirm','rdp:1:1'])
        finally: launch.doCleanups()

    def test_daemon_service_config_is_not_a_cli_layer(self):
        service = Path(self.env['XDG_CONFIG_HOME']) / 'rc/conf.d/joetoo-kwind'
        service.parent.mkdir(parents=True)
        service.write_text('return 90\n')
        self.assertIn('DRY RUN:', self.effective())
