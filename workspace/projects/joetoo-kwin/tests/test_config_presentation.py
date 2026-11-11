# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Configuration display severity and formatting; no broker or application calls."""
import re
import subprocess
import unittest
from test_step1_5a_plan import PlannerHarness, HEADER, INSTALLED_HEADER_AVAILABLE

NOTICE = 'PN BUILD rlv.config screen_width screen_height'.split()
INFO = '''verbosity desktop_limit dt_win_limit min_window_exposure_px
terminal_width_percent terminal_gap_percent terminal_height_percent terminal_left_percent terminal_top_percent terminal_row_gap_percent
graphical_left_percent graphical_top_percent graphical_width_percent graphical_height_percent
rdp_registration_timeout_ms rdp_windowing_backend rdp_x11_renderer rdp_remote_width rdp_remote_height bool.RDP_SMART_SIZING rdp_initial_client_width rdp_initial_client_height
vnc_viewer_ready_timeout_ms bool.sftp_advisory_enabled sftp_advisory_timeout_ms sftp_advisory_ssh_port'''.split()
DEBUG = '''initial_focus_timeout_ms initial_focus_poll_interval_ms sftp_capability_timeout_ms
rdp_registration_poll_ms rdp_registration_event_limit rdp_registration_window_limit rdp_backend_log_byte_limit rdp_x11_identity_settle_ms
vnc_ssh_start_timeout_ms vnc_supervisor_poll_interval_ms vnc_cleanup_timeout_ms vnc_local_port_attempts vnc_identity_event_limit vnc_identity_settle_ms vnc_dbus_timeout_ms vnc_placement_timeout_ms vnc_identity_start_timeout_ms'''.split()


def name(entry):
    return entry.split('.')[-1]


class ConfigPresentationTests(PlannerHarness, unittest.TestCase):
    def test_each_severity_adds_exactly_its_variables_once_in_order(self):
        for flags, groups in (((), [NOTICE]), (('-v',), [NOTICE, INFO]),
                              (('-vv',), [NOTICE, INFO, DEBUG])):
            with self.subTest(flags=flags):
                output = self.plan(*flags)
                keys = re.findall(r'^([A-Za-z_][A-Za-z_0-9]*)=', output, re.M)
                expected = [name(v) for group in groups for v in group]
                self.assertEqual(keys, expected)
                self.assertEqual(len(keys), len(set(keys)))
                self.assertIn('config=' + str(self.config), output)
                self.assertIn('DRY RUN: [2]', output)

    def test_boolean_values_and_formatting_prefixes(self):
        self.write_config(extra='RDP_SMART_SIZING=$FALSE\nsftp_advisory_enabled=$TRUE')
        output = self.plan('-v')
        self.assertIn('RDP_SMART_SIZING=False', output)
        self.assertIn('sftp_advisory_enabled=True', output)
        # Capture the actual arguments supplied to show_config, not just fixture output.
        with self.mock_header.open('a') as stream:
            stream.write('\nshow_config() { printf "VARS:%s\\n" "$varlist"; }\n')
        output = self.plan('-vv')
        groups = re.findall(r'^VARS:(.*)$', output, re.M)
        self.assertEqual([group.split() for group in groups], [NOTICE, INFO, DEBUG])

    def test_disabled_groups_do_not_invoke_show_config(self):
        with self.mock_header.open('a') as stream:
            stream.write('\nshow_config() { [[ $varlist == "$notice_varlist" ]]; }\n')
        self.assertIn('DRY RUN: [2]', self.plan())

    def test_render_failure_is_fatal_at_every_enabled_severity(self):
        original = self.mock_header.read_text()
        for group in ('notice', 'info', 'debug'):
            with self.subTest(group=group):
                self.mock_header.write_text(original + '\nshow_config() { [[ $varlist != "$' + group + '_varlist" ]]; }\n')
                run = subprocess.run(['bash', str(self.client), '-c', '-vv', '-f', str(self.config)],
                                     env=self.env, capture_output=True, text=True, timeout=20)
                self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
                self.assertIn('failed to show_config for ' + group + '_varlist', run.stderr)
                self.assertNotIn('DRY RUN', run.stdout)
                self.assertFalse(self.calls.exists())


@unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed joetoo header/modules unavailable')
class InstalledConfigPresentationTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client.write_text(self.client.read_text().replace(
            'source "' + str(self.mock_header) + '"',
            'source ' + str(HEADER) + '\nchecknotroot() { :; }', 1))

    def test_actual_header_severity_path_and_boolean_rendering(self):
        for flags, enabled, absent in (((), NOTICE, INFO + DEBUG),
                                       (('-v',), NOTICE + INFO, DEBUG),
                                       (('-vv',), NOTICE + INFO + DEBUG, [])):
            with self.subTest(flags=flags):
                output = self.plan(*flags)
                plain = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', output)
                for entry in enabled:
                    self.assertRegex(plain, r'(?m)^.*\b' + name(entry) + r'\s+\.+:')
                for entry in absent:
                    self.assertNotRegex(plain, r'(?m)^.*\b' + name(entry) + r'\s+\.+:')
                # A long explicit path is wrapped by rlv; reconstruct wrapped whitespace.
                self.assertIn(str(self.config), re.sub(r'\s+', '', plain))
                if flags:
                    self.assertRegex(plain, r'RDP_SMART_SIZING.*True')
                    self.assertRegex(plain, r'sftp_advisory_enabled.*True')
                self.assertIn('DRY RUN: [2]', plain)

    def test_actual_header_false_pseudo_booleans(self):
        self.write_config(extra='RDP_SMART_SIZING=$FALSE\nsftp_advisory_enabled=$FALSE')
        plain = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', self.plan('-v'))
        self.assertRegex(plain, r'RDP_SMART_SIZING.*False')
        self.assertRegex(plain, r'sftp_advisory_enabled.*False')
