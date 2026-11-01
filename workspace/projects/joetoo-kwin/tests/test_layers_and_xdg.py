"""Planner contracts and isolated XDG filesystem discovery, without a live bus."""
import os
import subprocess
from pathlib import Path
import unittest
from test_step1_5a_plan import PlannerHarness, ROOT


class LayerPlanTests(PlannerHarness, unittest.TestCase):
    def test_default_panels_and_explicit_layers(self):
        self.write_config(['4|dolphin|local|Documents|panel', '4|konsole|ssh|host|panel',
                           '4|konsole|ssh|host|over', '2|konsole|ssh|host|',
                           '4|konsole|ssh|host|over'], extra='verbosity=6\nmin_window_exposure_px=8')
        output = self.plan()
        rows = self.rows(output)
        self.assertEqual([r[1] for r in rows], ['1', '2', '3', '1', '4'])
        self.assertEqual([r[5] for r in rows], ['panel', 'panel', 'over', 'panel', 'over'])
        self.assertEqual(rows[0][-4:], ['19', '54', '816', '918'])
        self.assertIn('preferred focus slot [4]', output)
        self.assertIn('preferred focus slot [1]', output)

    def test_budget_thresholds_and_allocator_constraint(self):
        cases = [(['1|dolphin|local|']*5, '', 2),
                 (['1|dolphin|local||under']*5, '', 0),
                 (['1|dolphin|local|']*4+['1|dolphin|local||under'], '', 0),
                 (['1|dolphin|local||panel']*5, '', 2),
                 (['1|dolphin|local|']*5, 'dt_win_limit=5', 2)]
        for records, extra, rc in cases:
            with self.subTest(records=records, extra=extra):
                self.write_config(records, extra)
                output = self.plan(expected=rc)
                if rc == 0 and len(records) > 4:
                    self.assertIn('explicit layers exceed ordinary layout budget', output)
        for value in ('0', '-1', '999999999999999999999', '1+2'):
            self.write_config(['1|konsole|local|btop'], 'dt_win_limit='+value)
            self.plan(expected=2)

    def test_invalid_layers_and_field_counts(self):
        for value in ('1|dolphin|local||wrong', '1|dolphin|local||over|panel',
                      '1|dolphin|local', '1|dolphin|local||panel|'):
            self.write_config([value]); self.plan(expected=2)

    def test_cascades_preserve_dimensions_and_exposure_warns_not_rejects(self):
        self.write_config(['1|dolphin|local||under']*3)
        rows = self.rows(self.plan())
        self.assertEqual(rows[0][-2:], rows[1][-2:])
        self.assertLess(int(rows[0][-4]), int(rows[1][-4]))
        self.write_config(['1|dolphin|local||under', '1|dolphin|local||over'], 'min_window_exposure_px=8')
        mixed = self.rows(self.plan())
        self.assertNotEqual(mixed[0][-4:], mixed[1][-4:])
        self.write_config(['1|dolphin|local||under']*3, 'min_window_exposure_px=1000')
        output = self.plan()
        self.assertEqual(len(self.rows(output)), 3)
        self.assertIn('desired 1000x1000 logical-pixel exposure cannot be maintained', output)

    def test_exposure_geometry_checker_uses_regions_not_offsets(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('exposure', ROOT / 'libexec/joetoo-kwin-exposure.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertTrue(module.exposed((0, 0, 100, 100), [(32, 0, 100, 100)], 32))
        self.assertFalse(module.exposed((0, 0, 100, 100), [(8, 0, 100, 100)], 32))
        self.assertFalse(module.exposed((0, 0, 20, 20), [], 32))
        import random
        rng = random.Random(4)
        for _ in range(100):
            above = [(rng.randrange(10), rng.randrange(10), rng.randrange(1, 8), rng.randrange(1, 8)) for _ in range(4)]
            brute = any(all(a+3 <= c or a >= c+w or b+3 <= d or b >= d+h
                            for c, d, w, h in above) for a in range(8) for b in range(8))
            self.assertEqual(module.exposed((0, 0, 10, 10), above, 3), brute)


class XdgDiscoveryTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.env['HOME'] = str(self.folder / 'home')
        self.env.pop('XDG_CONFIG_HOME', None)
        self.user = Path(self.env['HOME']) / '.config/joetoo-kwin/joetoo-kwin.conf'
        self.user.parent.mkdir(parents=True)
        self.system = self.folder / 'system.conf'
        self.system.write_text(self.config.read_text())
        self.client.write_text(self.client.read_text().replace('/etc/joetoo-kwin/joetoo-kwin.conf', str(self.system)))

    def test_user_precedes_system_and_explicit_precedes_user(self):
        self.user.write_text(self.config.read_text())
        self.assertIn('config='+str(self.user), self.run_cli('-c'))
        self.assertIn('config='+str(self.config), self.run_cli('-c', '-f', str(self.config)))

    def test_relative_empty_unset_xdg_and_absolute_override(self):
        self.user.write_text(self.config.read_text())
        for value in ('', 'relative'):
            self.env['XDG_CONFIG_HOME'] = value
            self.assertIn('config='+str(self.user), self.run_cli('-c'))
        absolute = self.folder / 'xdg'
        selected = absolute / 'joetoo-kwin/joetoo-kwin.conf'
        selected.parent.mkdir(parents=True); selected.write_text(self.config.read_text())
        self.env['XDG_CONFIG_HOME'] = str(absolute)
        self.assertIn('config='+str(selected), self.run_cli('-c'))

    def test_system_fallback_and_missing_locations(self):
        self.assertIn('config='+str(self.system), self.run_cli('-c'))
        self.system.unlink()
        self.assertIn('No configuration:', self.run_cli('-c', expected=2))
        self.run_cli('-h')  # No configuration is needed for help.

    def test_bad_user_config_never_falls_back(self):
        self.user.write_text('return 1\n'); self.run_cli('-c', expected=2)
        self.user.write_text(self.config.read_text() + '\nscreen_width=0\n')
        self.run_cli('-c', expected=2)
        self.user.write_text(self.config.read_text()); self.user.chmod(0)
        try:
            self.assertIn('configuration unreadable', self.run_cli('-c', expected=2))
        finally: self.user.chmod(0o600)

    def test_user_discovery_for_layout_move_and_no_config_for_numeric_move(self):
        self.user.write_text(self.config.read_text())
        self.client.write_text(self.client.read_text().replace('#-----[ main script ]', r'''
qdbus6() { printf 'CALL:%s\n' "$*" >> "$TRACE"; case $3 in *.SubmitMove) printf 'rid\n';; *.Status) printf 'OK verified\n';; esac; }
#-----[ main script ]'''))
        result = subprocess.run(['bash', str(self.client), '-m', 'r'], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('SubmitMove', self.calls.read_text())
        self.user.unlink(); self.system.unlink(); self.calls.unlink()
        result = subprocess.run(['bash', str(self.client), '-m', '2'], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
