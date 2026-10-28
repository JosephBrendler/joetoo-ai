#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Headless tests for the Step 1.4d native managed-launch fixture."""

from pathlib import Path
import os
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase

CLIENT = Path(__file__).resolve().parents[1] / 'joetoo-kwin'


class TestMultiLaunchFixtureTests(TestCase):
    @staticmethod
    def run_fixture(fail=False):
        source = CLIENT.read_text()
        start = source.index('test_multi_launch() {')
        end = source.index('\n}\n', start) + 2
        implementation = source[start:end]
        with TemporaryDirectory() as tmp:
            trace = Path(tmp) / 'launches.txt'
            script = """
                PN=joetoo-kwin
                notice=5
                err=3
                j_msg() { :; }
                launch_managed_window() {
                    printf '%s\n' "$*" >> "$TRACE"
                    if [[ ${FAIL_LAUNCH:-0} == 1 && $3 == 2 && $4 == 873 ]]; then
                        return 1
                    fi
                    return 0
                }
            """ + implementation + '\ntest_multi_launch\n'
            run = subprocess.run(['bash', '-c', script], capture_output=True,
                                 text=True, check=False, env={**os.environ,
                                     'TRACE': str(trace),
                                     'FAIL_LAUNCH': '1' if fail else '0'})
            return run.returncode, trace.read_text().splitlines()

    def test_four_fixed_placements_and_separate_process_requests(self):
        code, calls = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertEqual(calls, [
            'konsole 1 1 19 54 816 918 -- konsole --separate',
            'konsole 2 1 873 54 816 918 -- konsole --separate',
            'konsole 1 2 19 54 816 918 -- konsole --separate',
            'konsole 2 2 873 54 816 918 -- konsole --separate'])

    def test_failed_launch_returns_failure_without_aborting_other_attempts(self):
        code, calls = self.run_fixture(fail=True)
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 4)

    def test_fixture_keeps_ordinary_open_flag_unimplemented(self):
        source = CLIENT.read_text()
        self.assertIn('    test-multi-launch)', source)
        self.assertIn('    -o) action="open"', source)
        self.assertIn('not yet integrated', source)
        fixture = source[source.index('test_multi_launch() {'):source.index('#-----[ main script ]')]
        self.assertIn('launch_managed_window', fixture)
        self.assertNotIn('RegisterWindow', fixture)
