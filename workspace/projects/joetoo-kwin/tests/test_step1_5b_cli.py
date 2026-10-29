#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Full CLI with disposable header and bus; never operates KWin."""
import re
import unittest
from test_step1_5a_plan import PlannerHarness, ROOT, INSTALLED_HEADER_AVAILABLE


class MoveTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client.write_text(self.client.read_text().replace(
            '#-----[ main script ]', '''
qdbus6() {
    case $3 in
        *.SubmitMove|*.Submit)
            printf 'CALL:%s\\n' "$*" >> "$TRACE"
            if [[ ${REJECT_MOVE:-} == yes ]]; then
                printf '%s\\n' "${MOVE_ERROR:-Error: org.joetoo.KWinBridge.Unsupported}" >&2
                return 1
            fi
            printf 'request-1\\n' ;;
        *.Status) printf '%s\\n' "${MOVE_STATUS:-OK verified}" ;;
        *invokeShortcut)
            printf 'CALL:%s\\n' "$*" >> "$TRACE"
            return "${SHORTCUT_RC:-0}" ;;
        *) printf 'CALL:%s\\n' "$*" >> "$TRACE" ;;
    esac
}
#-----[ main script ]'''))

    def run_move(self, args, expected=0):
        import subprocess
        self.calls.unlink(missing_ok=True)
        result = subprocess.run(['bash', str(self.client), *args], env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.result = result
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return self.calls.read_text().splitlines() if self.calls.exists() else []

    def test_six_forms_and_flags(self):
        cases = [(['-f', str(self.config), '-m', 'l'], '0 19 54 816 918 true false false'),
                 (['-m', '2'], '2 0 0 0 0 false true true'),
                 (['-f', str(self.config), '-m', '2', 'r'], '2 873 54 816 918 false false false'),
                 (['-m', '2', '-19', '-54'], '2 -19 -54 0 0 false false true'),
                 (['-m', '-19', '-54', '800', '900'], '0 -19 -54 800 900 true false false'),
                 (['-m', '2', '-19', '-54', '800', '900'], '2 -19 -54 800 900')]
        for args, tail in cases:
            with self.subTest(args=args):
                calls = self.run_move(args)
                self.assertTrue(calls[0].endswith(tail), calls)
                self.assertEqual(len(calls), 2)
                method = '.Submit ' if len(args) == 6 else '.SubmitMove '
                self.assertIn(method, calls[0])

    def test_layout_needs_no_session_list_and_reuses_config(self):
        self.config.write_text('screen_width=1920\nscreen_height=1080\nterminal_gap_percent=4\n')
        calls = self.run_move(['-v', '-f', str(self.config), '-m', 'r'])
        self.assertTrue(calls[0].endswith('0 892 54 797 918 true false false'), calls)

    def test_numeric_moves_ignore_layout_config(self):
        self.config.unlink()
        self.assertEqual(len(self.run_move(['-m', '2'])), 2)
        self.assertEqual(len(self.run_move(['move', '2', '-0019', '00054', '800', '900'])), 2)

    def test_invalid_forms_never_submit(self):
        for values in ([], ['foo'], ['0'], ['257'], ['-1'], ['1', '2'], ['l', '1'],
                       ['1', 'l', 'r'], ['1', '0', '0', '0'], ['1', '-32769', '0'],
                       ['1', '0', '0', '800', '0'], ['1'] * 6, ['99999999999999999999']):
            with self.subTest(values=values):
                self.assertEqual(self.run_move(['-m', *values], 2), [])

    def test_old_broker_or_resident_rejection_never_invokes_shortcut(self):
        self.env['REJECT_MOVE'] = 'yes'
        calls = self.run_move(['-m', '2'], 1)
        self.assertEqual(len(calls), 1)
        self.assertIn('SubmitMove', calls[0])

    def test_failed_shortcut_is_reported(self):
        self.env['SHORTCUT_RC'] = '7'
        self.run_move(['-m', '2'], 1)
        self.assertNotIn('Verifying active-window', self.result.stdout)

    def test_failed_verification_keeps_error(self):
        self.env['MOVE_STATUS'] = 'ERROR exact UUID did not converge'
        self.run_move(['-m', '2'], 1)
        self.assertIn('ERROR exact UUID did not converge', self.result.stdout + self.result.stderr)

    def test_auxiliary_reporting_fault_stops_before_shortcut(self):
        # Inject only the reporting fault; other tests use the real installed helper.
        self.client.write_text(self.client.read_text().replace(
            '#-----[ main script ]', 'handle_result() { return 32; }\n#-----[ main script ]'))
        calls = self.run_move(['-m', '2'], 1)
        self.assertEqual(len(calls), 1)
        self.assertIn('result reporting failed [32]', self.result.stdout + self.result.stderr)
        self.assertNotIn('Move rejected', self.result.stdout + self.result.stderr)

    def test_submission_error_names_and_diagnostics(self):
        self.env['REJECT_MOVE'] = 'yes'
        cases = [
            ('Error: org.joetoo.KWinBridge.Busy\nPrevious request has not completed', 'Move busy:'),
            ('Error: org.joetoo.KWinBridge.Unsupported\nResident lacks protocol 1', 'compatible broker'),
            ('Error: org.freedesktop.DBus.Error.UnknownMethod\nNo method', 'compatible broker'),
            ("Cannot find 'org.joetoo.KWinBridge.SubmitMove' in object /org/joetoo/KWinBridge at org.joetoo.KWinBridge", 'compatible broker'),
            ('Error: org.joetoo.KWinBridge.BadArguments\nInvalid preservation flags', 'invalid request'),
            ('Error: org.freedesktop.DBus.Error.InvalidArgs\nWrong signature', 'invalid request'),
            ('Error: org.freedesktop.DBus.Error.NoReply\nConnection timed out', 'Move submission failed'),
            ('Transport failed with text mentioning org.joetoo.KWinBridge.Busy', 'Move submission failed')]
        for diagnostic, label in cases:
            with self.subTest(diagnostic=diagnostic):
                self.env['MOVE_ERROR'] = diagnostic
                self.assertEqual(len(self.run_move(['-m', '2'], 1)), 1)
                output = self.result.stdout + self.result.stderr
                self.assertIn(label, output)
                # The installed header may wrap long diagnostics.
                self.assertIn(diagnostic.splitlines()[-1].split()[-1], output)
                if label != 'compatible broker':
                    self.assertNotIn('compatible broker', output)

    def test_success_verbosity_and_failure_detail(self):
        self.env['MOVE_STATUS'] = 'OK window-identity before=[1] after=[1] geometry-details'
        for switches, detail, protocol in [([], False, False), (['-v'], True, False),
                                            (['-vv'], True, True)]:
            self.run_move([*switches, '-m', '2'])
            output = self.result.stdout + self.result.stderr
            self.assertEqual('window-identity' in output, detail)
            self.assertEqual('preserveDesktop=' in output, protocol)
            self.assertIn('Verifying active-window move', output)
        self.env['MOVE_STATUS'] = 'ERROR placement confirmation timed out: geometry-details'
        self.run_move(['-m', '2'], 1)
        self.assertIn('geometry-details', self.result.stdout + self.result.stderr)


@unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed joetoo header/modules unavailable')
class InstalledHeaderMoveTests(MoveTests):
    def setUp(self):
        super().setUp()
        # Keep the bus spy while restoring the actual installed header helpers.
        self.client.write_text(self.client.read_text().replace(
            'source "' + str(self.mock_header) + '"',
            'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))

    def test_result_lines_with_real_header(self):
        self.run_move(['-m', '2'])
        # Universal-newline conversion turns the status cursor's CR into LF.
        # Check descriptive completion precedes that cursor movement on each line.
        text = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', self.result.stdout)
        for label in ('Submitting active-window move ...',
                      'Invoking active-window move shortcut ...', 'Verifying active-window move ...'):
            self.assertRegex(text, re.escape(label) + r'[^\n]*\(completed\)')
        self.assertNotRegex(text, r'Verifying active-window move[^\n]*OK verified')

    def test_environment_info_detail_follows_completed_notice_block(self):
        # Real header coverage: environment verbosity and pseudo-boolean DEBUG
        # must expose full detail without reopening the notice result line.
        detail = 'OK move_optional: window-A (pid=123) before=[1] (19,54) 816x918 after=[2] (19,54) 816x918 tiled=false fullscreen=false'
        self.env['MOVE_STATUS'] = detail
        for verbosity, debug, visible in [('5', '', False), ('6', '', True), ('5', '0', True)]:
            with self.subTest(verbosity=verbosity, debug=debug):
                self.env.update(verbosity=verbosity, DEBUG=debug)
                self.run_move(['-m', '2'])
                text = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', self.result.stdout)
                self.assertEqual('before=[1]' in text, visible)
                self.assertEqual('after=[2]' in text, visible)
                if visible:
                    verification = text.index('Verifying active-window move')
                    completion = text.index('(completed)', verification)
                    details = text.index('OK move_optional:', completion)
                    self.assertIn('\n', text[completion:details])
                    self.assertIn('window-A', text[details:])
                    self.assertIn('816x918', text[details:])
                    self.assertRegex(text, r'(?m)^.*\* OK move_optional: window-A \(pid=123\)\n')
                    self.assertRegex(text, r'(?m)^.*\* before=\[1\]')
                    self.assertIn('fullscreen=false', text[details:])
