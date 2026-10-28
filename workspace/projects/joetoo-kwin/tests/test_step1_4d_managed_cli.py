#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4d Bash launch transaction mock; no real applications or D-Bus."""

import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase

CLIENT = Path(__file__).resolve().parents[1] / 'joetoo-kwin'


class ManagedLaunchCLITests(TestCase):
    @staticmethod
    def run_transaction(state='registered', slot='1'):
        source = CLIENT.read_text()
        start = source.index('launch_managed_window() {')
        end = source.index('\n}\n', start) + 2
        impl = source[start:end]
        with TemporaryDirectory() as tmp:
            trace = Path(tmp) / 'transactions.txt'
            script = r"""
                PN=joetoo-kwin
                notice=5
                err=3
                bus=org.joetoo.KWinBridge
                path=/org/joetoo/KWinBridge
                iface=org.joetoo.KWinBridge
                j_msg() { :; }
                isint() { [[ $1 =~ ^-?[0-9]+$ ]]; }
                validate_geometry() { :; }
                bad_args() { return 2; }
                konsole() { :; }
                wait_for_request() { [[ $1 == place-1 && $2 == launch ]]; }
                qdbus6() {
                    case $3 in
                        *.SubmitManagedLaunch)
                            printf '%s\n' 'submit' >> "$TRACE"
                            printf '{"placement_request_id":"place-1","registration_request_id":"reg-1"}\n' ;;
                        *.SetManagedLaunchPid)
                            printf 'set-pid %s %s\n' "$4" "$5" >> "$TRACE" ;;
                        *.PollManagedLaunch)
                            printf '%s\n' 'poll' >> "$TRACE"
                            printf '{"state":"%s","managed_id":"win-001","window_uuid":"d848c4c9-64ed-48bf-b083-40230314d5ab"}\n' "$TEST_STATE" ;;
                        *) return 1 ;;
                    esac
                }
            """ + impl + r"""
                launch_managed_window konsole "$TEST_SLOT" 1 19 54 816 918 -- konsole --separate
            """
            run = subprocess.run(['bash', '-c', script], capture_output=True,
                                 text=True, check=False, env={**os.environ,
                                      'TRACE': str(trace),
                                      'TEST_STATE': state,
                                      'TEST_SLOT': slot})
            return run.returncode, (trace.read_text().splitlines()
                                     if trace.exists() else []), run.stderr

    def test_successful_transaction_arms_before_launch_and_hands_off_pid(self):
        rc, trace, err = self.run_transaction()
        self.assertEqual((rc, err), (0, ''))
        self.assertEqual(trace[0], 'submit')
        self.assertTrue(trace[1].startswith('set-pid reg-1 '))
        self.assertEqual(trace[2], 'poll')

    def test_failed_registration_is_failure(self):
        rc, trace, _ = self.run_transaction(state='failed')
        self.assertNotEqual(rc, 0)
        self.assertEqual(trace[0], 'submit')

    def test_invalid_slot_does_not_arm_request(self):
        rc, trace, _ = self.run_transaction(slot='0')
        self.assertNotEqual(rc, 0)
        self.assertEqual(trace, [])
