#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Headless CLI/planner tests: disposable config/header, forbidden-operation spies.

Ordinary tests use a checked-in header double and need only Bash/Python.
Separate, availability-guarded integration tests exercise the installed header
with logging and the root gate disabled only in a temporary client copy.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HEADER = Path('/usr/sbin/script_header_joetoo')


class PlannerHarness:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        (self.folder / 'libexec').mkdir()
        shutil.copyfile(ROOT / 'libexec/joetoo-kwin-plan-functions',
                        self.folder / 'libexec/joetoo-kwin-plan-functions')
        self.client = self.folder / 'joetoo-kwin'
        self.config = self.folder / 'layout.conf'
        self.calls = self.folder / 'calls'
        self.env = {**os.environ, 'TRACE': str(self.calls), 'verbosity': '5',
                    'INTERACTIVE': '', 'QUIET': '', 'DEBUG': '', 'LOGGING': '',
                    'TERM': 'dumb', 'JOETOO_HEADER_DIR': '/usr/sbin',
                    'PATH': str(self.folder) + os.pathsep + os.environ['PATH']}
        for program in ('qdbus6', 'konsole', 'ssh', 'ssh_wrapper', 'vncviewer', 'btop'):
            spy = self.folder / program
            spy.write_text('#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$TRACE"\nexit 99\n')
            spy.chmod(0o755)
        # UI spies verify stage order and effective varlist without depending on
        # terminal width, emoji availability or an installed joetoo header.
        self.mock_header = self.folder / 'header'
        shutil.copyfile(ROOT / 'tests/fixtures/step1_5a_header.bash', self.mock_header)
        self.client.write_text((ROOT / 'joetoo-kwin').read_text().replace(
            'source /usr/sbin/script_header_joetoo',
            'source "' + str(self.mock_header) + '"', 1))
        self.write_config()

    def write_config(self, records=None, extra=''):
        if records is None:
            records = ['1|konsole|ssh|unreachable.invalid', '1|konsole|local|btop']
        # Test inputs are literal trusted Bash strings; no user input is evaluated.
        self.config.write_text('screen_width=1920\nscreen_height=1080\n' +
                               'desktop_session_list=(\n' +
                               '\n'.join("'" + record + "'" for record in records) +
                               '\n)\n' + extra + '\n')

    def run_cli(self, *args, expected=0):
        result = subprocess.run(['bash', str(self.client), *args], env=self.env,
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        # Every planner/error test asserts the absence of D-Bus, GUI and transport.
        self.assertFalse(self.calls.exists(), self.calls.read_text() if self.calls.exists() else '')
        return result.stdout

    def plan(self, *args, expected=0):
        return self.run_cli('-c', '-f', str(self.config), *args, expected=expected)

    @staticmethod
    def rows(output):
        return [line.split() for line in output.splitlines()
                if re.match(r'^\d+\s+\d+\s+', line)]

    def assert_columns_aligned(self, output, target):
        plain = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)
        lines = plain.splitlines()
        header = next(line for line in lines if 'Desktop' in line and 'Target' in line)
        data = [line for line in lines if target in line or 'underlay-proposed' in line]
        # Ignore diagnostics/config lines; these two rows carry geometry cells.
        data = [line for line in data if re.search(r'\b(?:terminal|underlay-proposed)\s+\d+', line)]
        self.assertEqual(len(data), 2)
        self.assertIn(target, data[0])
        self.assertEqual(data[0].index(target), header.index('Target'))
        for line in data:
            self.assertEqual(line.index('konsole') if 'konsole' in line else line.index('vncviewer'),
                             header.index('Program'))
            self.assertEqual(line.index('terminal') if 'underlay-proposed' not in line
                             else line.index('underlay-proposed'), header.index('Layer'))
            fields = line[header.index('Layer'):].split()
            self.assertEqual(len(fields), 5)
            self.assertEqual(line.index(fields[1], header.index('Layer')), header.index('X'))


class PlannerTests(PlannerHarness, unittest.TestCase):
    def test_default_budget_and_effective_config_before_plan(self):
        output = self.plan()
        self.assertLess(output.index('CONFIG'), output.index('DRY RUN'))
        self.assertIn('terminal_width_percent=87', output)
        self.assertIn('not autodetected', output)
        self.assertEqual([row[-4:] for row in self.rows(output)],
                         [['19', '54', '816', '918'], ['873', '54', '816', '918']])

    def test_config_overrides_defaults_then_cli_overrides_config(self):
        self.write_config(extra='terminal_width_percent=80\nterminal_gap_percent=4\nverbosity=6')
        output = self.plan('-q')
        self.assertIn('verbosity=5', output)
        self.assertIn('terminal_width_percent=80', output)
        self.assertEqual([row[-4:] for row in self.rows(output)],
                         [['19', '54', '730', '918'], ['825', '54', '730', '918']])

    def test_common_option_order_and_clusters(self):
        output = self.run_cli('-vq', '-f', str(self.config), '-c')
        self.assertIn('verbosity=5', output)
        self.assertIn('verbosity=7', self.plan('-vv'))
        self.assertIn('verbosity=3', self.plan('-qq'))
        self.assertIn('verbosity=5', self.plan('-v', '-q'))
        self.plan('--')

    def test_verbosity_clamps_and_interactive_floor(self):
        self.assertIn('verbosity=7', self.plan('-vvvvvv'))
        self.assertIn('verbosity=0', self.plan('-qqqqqqqq'))
        self.env['INTERACTIVE'] = '0'
        self.assertIn('verbosity=5', self.plan('-qqqqqqqq'))

    def test_one_three_four_and_alternate_display(self):
        for count in (1, 3, 4):
            with self.subTest(count=count):
                self.write_config(['1|konsole|direct|'] * count,
                                  'screen_width=2560\nscreen_height=1440')
                rows = self.rows(self.plan())
                self.assertEqual(len(rows), count)
                rects = [list(map(int, row[-4:])) for row in rows]
                for x, y, w, h in rects:
                    self.assertGreater(w, 0); self.assertGreater(h, 0)
                    self.assertLessEqual(x + w, 2560)
                    self.assertLessEqual(y + h, 1440)
                columns = 2 if count == 4 else count
                self.assertLessEqual(columns * rects[0][2] + (columns - 1) * 51, 2227)
                if count == 4:
                    self.assertEqual(rects[0][0], rects[2][0])
                    self.assertGreater(rects[2][1], rects[0][1] + rects[0][3])

    def test_graphical_windows_do_not_consume_terminal_slots(self):
        self.write_config(['1|konsole|ssh|unreachable.invalid', '1|vncviewer|via-ssh|host',
                           '1|konsole|direct|', '2|konsole|direct|'])
        rows = self.rows(self.plan())
        self.assertEqual([row[1] for row in rows], ['1', '2', '3', '1'])
        self.assertEqual(rows[0][-4:], ['19', '54', '816', '918'])
        self.assertEqual(rows[2][-4:], ['873', '54', '816', '918'])
        self.assertEqual(rows[1][5], 'underlay-proposed')
        self.assertEqual(rows[3][-2:], ['1670', '918'])

    def test_custom_offsets_height_and_row_gutters(self):
        self.write_config(['1|konsole|direct|'] * 4,
                          'terminal_left_percent=2\nterminal_top_percent=10\n'
                          'terminal_height_percent=80\nterminal_row_gap_percent=4')
        rows = self.rows(self.plan())
        self.assertEqual(rows[0][-4:], ['38', '108', '816', '410'])
        self.assertEqual(rows[2][-4:], ['38', '561', '816', '410'])

    def test_invalid_geometry_inputs(self):
        for extra in ('screen_width=0', 'screen_height=32769', 'desktop_limit=257',
                      'terminal_width_percent=0', 'terminal_height_percent=101',
                      'terminal_gap_percent=99', 'terminal_row_gap_percent=99',
                      'terminal_top_percent=20', 'terminal_left_percent=20',
                      'graphical_width_percent=99', 'graphical_top_percent=20',
                      'screen_width=999999999999999999999999999999999',
                      'screen_width=01920', 'screen_width="1+2"', 'unset screen_width'):
            with self.subTest(extra=extra):
                self.write_config(['1|konsole|direct|'] * 4, extra)
                self.plan(expected=2)

    def test_missing_explicit_dimensions(self):
        self.config.write_text("desktop_session_list=('1|konsole|direct|')\n")
        self.plan(expected=2)

    def test_invalid_records_and_terminal_limit(self):
        for records in ([], ['1|konsole|direct|'] * 5, ['0|konsole|direct|'],
                        ['257|konsole|direct|'], ['01|konsole|direct|'],
                        ['1|konsole|ssh|'], ['1|konsole|bad|host'],
                        ['1|konsole|direct'], ['1|konsole|direct||'],
                        ['1|/usr/bin/konsole|direct|'], ['1|konsole|local|a\nb']):
            with self.subTest(records=records):
                self.write_config(records)
                self.plan(expected=2)

    def test_wrong_array_types(self):
        for definition in ('desktop_session_list=scalar', 'declare -A desktop_session_list=([a]=b)'):
            self.config.write_text('screen_width=1920\nscreen_height=1080\n'
                                   'unset desktop_session_list\n' + definition + '\n')
            self.plan(expected=2)

    def test_missing_and_failed_config(self):
        self.config.unlink()
        self.plan(expected=2)
        self.config.write_text('return 1\n')
        self.plan(expected=2)

    def test_bad_cli_and_conflicting_operations(self):
        for args in (('-c', '-f'), ('-c', '-c'), ('-c', '-o'), ('-c', 'extra'),
                     ('-c', '--unknown'), ('-v',), ('-f', str(self.config), '-m', '1', '2', '3', '4', '5')):
            with self.subTest(args=args):
                self.run_cli(*args, expected=2)
        self.run_cli('-o', '-f', str(self.config), expected=2)

    def test_reporting_fault_is_not_silent_success(self):
        self.env['REPORT_RC'] = '2'
        self.assertIn('result reporting failed', self.plan(expected=1))

    def test_selected_config_sourced_once_and_default_path_used(self):
        reads = self.folder / 'config-reads'
        self.write_config(extra=f'printf "read\\n" >> "{reads}"')
        self.client.write_text(self.client.read_text().replace(
            'config=/etc/joetoo-kwin/joetoo-kwin.conf', f'config="{self.config}"'))
        self.run_cli('-c')
        self.assertEqual(reads.read_text(), 'read\n')

    def test_move_grammar_preserves_negative_coordinates_without_loading_config(self):
        # Replace only the action in a temporary client; never move a real window.
        self.client.write_text(self.client.read_text().replace(
            '#-----[ main script ]',
            'move_active_window() { printf "MOVE:%s\\n" "$*"; }\n#-----[ main script ]'))
        self.config.unlink()
        for args in (('-m', '1', '-19', '-54', '816', '918'),
                     ('-v', '-m', '1', '-19', '-54', '816', '918'),
                     ('move', '1', '-19', '-54', '816', '918')):
            self.assertIn('MOVE:1 -19 -54 816 918', self.run_cli(*args))
        self.run_cli('-m', '1', '2', '3', expected=2)


    def test_long_targets_keep_header_and_rows_aligned(self):
        target = 'long-destination-name.for-headless-review.invalid'
        self.write_config(['1|konsole|ssh|' + target, '1|vncviewer|via-ssh|short'])
        self.assert_columns_aligned(self.plan(), target)

    def test_dry_run_explains_trusted_config_side_effects(self):
        marker = self.folder / 'config-side-effect'
        self.write_config(extra=f'printf "configured" > "{marker}"')
        output = self.plan()
        self.assertEqual(marker.read_text(), 'configured')
        self.assertIn('planner launches no applications', output)
        self.assertIn('sourced trusted Bash configuration may have side effects', output)
        self.assertNotIn('no programs launched', output)


class PlannerPortabilityTests(unittest.TestCase):
    def test_ordinary_tests_do_not_read_installed_header(self):
        original = Path.read_text

        def without_installed_header(path, *args, **kwargs):
            if path == HEADER:
                raise FileNotFoundError('installed header unavailable in portable test')
            return original(path, *args, **kwargs)

        # Run the ordinary suite under the missing-header condition, including
        # setup. This protects against reintroducing an unconditional dependency.
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlannerTests)
        result = unittest.TestResult()
        with mock.patch.object(Path, 'read_text', without_installed_header):
            suite.run(result)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertFalse(result.skipped)


INSTALLED_HEADER_AVAILABLE = all(
    (HEADER.parent / name).is_file() for name in (
        'script_header_joetoo', 'script_header_joetoo_uiassets',
        'script_header_joetoo_unicode', 'script_header_joetoo_registries'))


@unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed joetoo header/modules unavailable')
class InstalledHeaderPlannerTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Only this integration class sources the system header.
        self.client.write_text((ROOT / 'joetoo-kwin').read_text().replace(
            'source /usr/sbin/script_header_joetoo',
            'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))

    def test_installed_header_config_and_color_smoke(self):
        # No host operations: source the real header with logging off, then
        # override only the root check in this disposable client copy.
        self.client.write_text((ROOT / 'joetoo-kwin').read_text().replace(
            'source /usr/sbin/script_header_joetoo',
            'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))
        output = self.plan()
        plain = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)
        self.assertIn('DRY RUN: [2]', plain)
        self.assertIn('terminal_width_percent', plain)
        self.assertIn('816', plain)

    def test_installed_header_long_target_columns_and_verbosity(self):
        target = 'long-destination-name.for-header-review.invalid'
        self.write_config(['1|konsole|ssh|' + target, '1|vncviewer|via-ssh|short'])
        self.assert_columns_aligned(self.plan(), target)
        for flags, expected in ((('-vv',), 7), (('-v', '-q'), 5), (('-qqqqqqqq',), 0)):
            # The real header suppresses ordinary output at low verbosity;
            # append a test-only state probe to the disposable client.
            original = self.client.read_text()
            self.client.write_text(original + '\nprintf "TEST_VERBOSITY=%s\\n" "$verbosity"\n')
            try:
                self.assertIn(f'TEST_VERBOSITY={expected}', self.plan(*flags))
            finally:
                self.client.write_text(original)
        self.env['INTERACTIVE'] = '0'
        self.client.write_text(original + '\nprintf "TEST_VERBOSITY=%s\\n" "$verbosity"\n')
        self.assertIn('TEST_VERBOSITY=5', self.plan('-qqqqqqqq'))
