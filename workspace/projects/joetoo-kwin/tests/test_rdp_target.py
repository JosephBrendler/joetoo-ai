# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline RDP contract and real -c planning; spies forbid live launch side effects."""
import importlib.util
import ipaddress
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
from test_step1_5a_plan import PlannerHarness, ROOT

spec = importlib.util.spec_from_file_location('rdp_target_test', ROOT / 'libexec/joetoo_kwin_rdp_target.py')
rdp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdp)


class TargetTests(unittest.TestCase):
    def test_dns_ipv4_ipv6_and_explicit_application_ports(self):
        cases = [('rdp://joe@host', 'host', 3389),
                 ('rdp://joe.test@host.example:3390', 'host.example', 3390),
                 ('rdp://joe@192.0.2.10:1', '192.0.2.10', 1),
                 ('rdp://joe@[2001:0DB8::1]:65535', '2001:db8::1', 65535),
                 ('rdp://joe@[::ffff:192.0.2.1]', '::ffff:c000:201', 3389)]
        with patch.object(socket, 'getaddrinfo', side_effect=AssertionError('No DNS')):
            for text, host, port in cases:
                with self.subTest(text=text):
                    parsed = rdp.target(text)
                    if ':' in host:
                        self.assertEqual(ipaddress.IPv6Address(parsed['host']), ipaddress.IPv6Address(host))
                    else:
                        self.assertEqual(parsed['host'], host)
                    self.assertEqual(parsed['port'], port)
                    self.assertIn(parsed['user'], ('joe', 'joe.test'))

    def test_invalid_authorities_ports_credentials_and_switches_are_redacted(self):
        cases = ['', 'rdp:rdp://joe@host:3389', 'rdp://host', 'rdp://@host', 'rdp://joe:PRIVATE@host',
                 'rdp://joe@host/', 'rdp://joe@host/path', 'rdp://joe@host?password=PRIVATE',
                 'rdp://joe@host#PRIVATE', 'rdp://joe@host:0', 'rdp://joe@host:65536',
                 'rdp://joe@host:03389', 'rdp://joe@host:', 'rdp://joe@host:-1',
                 'rdp://joe@host:3389 /cert:ignore', 'rdp://joe@bad..host', 'rdp://joe@-host',
                 'rdp://joe@host-', 'rdp://joe@host.', 'rdp://joe@bad_host',
                 'rdp://joe@999.1.2.3', 'rdp://joe@2001:db8::1', 'rdp://joe@[::1]extra',
                 'rdp://joe@[fe80::1%25eth0]', 'rdp://joe%40domain@host', 'rdp://joe@@host',
                 'RDP://joe@host', 'rdp://joe@$(PRIVATE)', 'rdp://joe@`PRIVATE`',
                 'rdp://joe@host|over', 'rdp://joe@høst', 'rdp://joe@host\\PRIVATE',
                 'rdp://joe@host\n', 'rdp://joe@host\r', 'rdp://joe@host\t', 'rdp://joe@host\x00',
                 'rdp://joe@host\x1b', 'rdp://joe@host\x7f', 'x' * 4097, None, 1]
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, '^Invalid RDP target \\(redacted\\)') as caught:
                    rdp.target(text)
                self.assertNotIn('PRIVATE', str(caught.exception))

    def test_host_label_and_account_bounds(self):
        for value in ('rdp://' + 'j' * 129 + '@host', 'rdp://joe@' + 'h' * 64,
                      'rdp://joe@' + '.'.join(['h' * 63] * 5)):
            with self.assertRaises(ValueError): rdp.target(value)
        self.assertEqual(rdp.target('rdp://_' + 'j' * 127 + '@host')['port'], 3389)

    def test_settings_defaults_and_pure_sdl_mapping_preserve_frame_separation(self):
        self.assertEqual(rdp.settings({}), rdp.DEFAULTS)
        self.assertEqual(rdp.sizing_arguments({}), ['/size:1024x768', '/smart-sizing:800x600'])
        result = rdp.sizing_arguments(dict(rdp_remote_width='1920', rdp_remote_height='1080',
            rdp_initial_client_width='900', rdp_initial_client_height='700'))
        self.assertEqual(result, ['/size:1920x1080', '/smart-sizing:900x700'])
        self.assertEqual(rdp.sizing_arguments({'RDP_SMART_SIZING': ''}),
                         ['/size:1024x768', '/smart-sizing:off'])
        self.assertEqual(rdp.settings({'RDP_SMART_SIZING': '0'})['RDP_SMART_SIZING'], True)
        self.assertEqual(rdp.settings({'RDP_SMART_SIZING': False})['RDP_SMART_SIZING'], False)

    def test_dimension_bounds_types_and_unknown_settings(self):
        names = ('rdp_remote_width', 'rdp_remote_height', 'rdp_initial_client_width', 'rdp_initial_client_height')
        for name in names:
            for value in (64, '64', 8192, '8192'):
                with self.subTest(name=name, value=value): self.assertEqual(rdp.settings({name: value})[name], int(value))
            for value in (0, 63, 8193, -1, True, 1024., '01024', '0x400', '1+1023', ' 1024', '1024 ', 'x' * 10000):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(ValueError): rdp.settings({name: value})
        for data in ({'unknown': 1}, [], None):
            with self.assertRaises(ValueError): rdp.settings(data)

    def test_backend_is_only_validated_intent_and_boolean_is_strict(self):
        for value in ('auto', 'wayland', 'x11'):
            self.assertEqual(rdp.settings({'rdp_windowing_backend': value})['rdp_windowing_backend'], value)
        for value in ('tty', 'xwayland', 'WAYLAND', '', None, True):
            with self.assertRaises(ValueError): rdp.settings({'rdp_windowing_backend': value})
        for value in ('true', 'false', '1', 0, 1, None, '$(PRIVATE)'):
            with self.assertRaises(ValueError): rdp.settings({'RDP_SMART_SIZING': value})

    def test_cli_stdin_contract_and_fixed_redacted_errors(self):
        script = str(ROOT / 'libexec/joetoo_kwin_rdp_target.py')
        for text in ('rdp://joe:PRIVATE@host', 'rdp://joe@bad..host', 'rdp://joe@host\x00', 'x' * 4097):
            run = subprocess.run([sys.executable, script, '--target'], input=text, text=True, capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, '')
            self.assertEqual(run.stderr, 'Invalid RDP target/settings (redacted)\n')
        run = subprocess.run([sys.executable, script, '--target'], input='rdp://joe@[::1]:3390', text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), dict(user='joe', host='::1', port=3390))
        for sizing in ('0', ''):
            run = subprocess.run([sys.executable, script, '--settings', '1024', '768', sizing, '800', '600', 'auto'],
                                 text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['RDP_SMART_SIZING'], sizing == '0')


class RdpPlannerTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        shutil.copyfile(ROOT / 'libexec/joetoo_kwin_rdp_target.py', self.folder / 'libexec/joetoo_kwin_rdp_target.py')
        # Every GUI/network entry point is an error/trace spy, never executed.
        for program in ('sdl-freerdp', 'dolphin', 'nc', 'getent', 'curl', 'wget'):
            path = self.folder / program
            path.write_text('#!/bin/sh\nprintf "unexpected\\n" >> "$TRACE"\nexit 99\n')
            path.chmod(0o755)

    def test_single_rdp_defaults_nonsecret_settings_and_no_backend_probe(self):
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host'])
        output = self.plan()
        self.assertIn('sdl-freerdp', output)
        for field in ('rdp_remote_width=1024', 'rdp_remote_height=768', 'RDP_SMART_SIZING=True',
                      'rdp_initial_client_width=800', 'rdp_initial_client_height=600', 'rdp_windowing_backend=auto'):
            self.assertIn(field, output)
        self.assertEqual(self.rows(output)[0][:2], ['1', '1'])

    def test_mixed_rdp_dry_run_passes_but_open_refuses_before_confirmation_or_launch(self):
        # Exercise the actual CLI/preflight, with a valid Konsole entry first:
        # validation of the whole plan must precede launching even that entry.
        self.write_config(['1|konsole|local|btop',
                           '1|sdl-freerdp|rdp|rdp://joe@host|under'])
        self.assertEqual(len(self.rows(self.plan())), 2)
        for helper in ('joetoo-kwin-launch-functions', 'joetoo-kwin-session.bashrc'):
            shutil.copyfile(ROOT / 'libexec' / helper, self.folder / 'libexec' / helper)
        runtime = self.folder / 'runtime'
        runtime.mkdir(mode=0o700)
        self.env['XDG_RUNTIME_DIR'] = str(runtime)
        # A regressed resource call must hit a poison fixture, never real D-Bus.
        (self.folder / 'libexec/joetoo_kwin_launch_resources.py').write_text(
            "import os\nwith open(os.environ['TRACE'], 'a') as f: f.write('resource\\n')\nraise SystemExit(99)\n")
        self.client.write_text(self.client.read_text().replace('#-----[ main script ]', r'''
confirm_continue_or_exit() { printf 'confirm\n' >> "$TRACE"; return 99; }
launch_managed_window() { printf 'application-launch\n' >> "$TRACE"; return 99; }
#-----[ main script ]''', 1))
        output = self.run_cli('-o', '-f', str(self.config), expected=2)
        self.assertIn('unsupported executable recipe [sdl-freerdp:rdp]', output)
        # run_cli also rejects any trace from qdbus6 (including a broker launch
        # transaction), executable spies, confirmation or the resource fixture.
        self.assertFalse(self.calls.exists())

    def test_mixed_group_slots_layers_geometry_are_identical_to_existing_allocator(self):
        mixed = ['3|sdl-freerdp|rdp|rdp://joe@host|under',
                 '3|konsole|ssh|host|panel', '3|dolphin|local||panel',
                 '3|vncviewer|ssh|ssh://joe@host/display/2|over',
                 '3|sdl-freerdp|rdp|rdp://joe@[::1]:3390|over',
                 '2|sdl-freerdp|rdp|rdp://joe@other|panel']
        self.write_config(mixed)
        rows = self.rows(self.plan())
        self.assertEqual([row[:2] for row in rows], [['3', str(n)] for n in range(1, 6)] + [['2', '1']])
        baseline = [row if '|sdl-freerdp|' not in row else
                    row.split('|', 1)[0] + '|dolphin|local||' + row.rsplit('|', 1)[1] for row in mixed]
        self.write_config(baseline)
        old = self.rows(self.plan())
        self.assertEqual([row[-5:] for row in rows], [row[-5:] for row in old])

    def test_strict_sizing_backend_and_pseudo_boolean_overrides(self):
        record = ['1|sdl-freerdp|rdp|rdp://joe@host|under']
        for value in ('auto', 'wayland', 'x11'):
            self.write_config(record, extra=f'rdp_windowing_backend={value}\nRDP_SMART_SIZING=$FALSE\nrdp_remote_width=1920\n')
            output = self.plan()
            self.assertIn('rdp_windowing_backend=' + value, output)
            self.assertIn('rdp_remote_width=1920', output)
            self.assertIn('RDP_SMART_SIZING=False', output)
        for assignment in ('rdp_remote_width=0', 'rdp_remote_height=8193', 'rdp_initial_client_width=63',
                           'rdp_initial_client_height=01024', 'RDP_SMART_SIZING=1',
                           'RDP_SMART_SIZING=true', 'rdp_windowing_backend=tty'):
            self.write_config(record, extra=assignment)
            self.plan(expected=2)

    def test_malformed_rdp_redaction_and_program_mode_pairing(self):
        records = ['1|sdl-freerdp|rdp|rdp:rdp://joe@host:3389',
                   '1|sdl-freerdp|rdp|rdp://joe:PRIVATE@host',
                   '1|sdl-freerdp|rdp|rdp://joe@host/PRIVATE',
                   '1|sdl-freerdp|rdp|rdp://joe@host?PRIVATE',
                   '1|sdl-freerdp|rdp|rdp://joe@host\tPRIVATE',
                   '1|sdl-freerdp|rdp|rdp://joe@host:65536',
                   '1|sdl-freerdp|local|PRIVATE', '1|sdl-freerdp|PRIVATE|rdp://joe@host', '1|konsole|rdp|PRIVATE', '1|dolphin|rdp|PRIVATE']
        for record in records:
            with self.subTest(record=record):
                self.write_config([record])
                output = self.plan(expected=2)
                self.assertNotIn('PRIVATE', output)

    def test_invalid_late_rdp_entry_refuses_entire_mixed_plan_without_side_effects(self):
        self.write_config(['1|konsole|ssh|host', '1|sdl-freerdp|rdp|rdp://joe@host:0'])
        self.plan(expected=2)

    def test_new_rdp_settings_do_not_change_legacy_only_recipes(self):
        self.write_config(['1|konsole|ssh|host', '1|dolphin|local|',
                           '2|vncviewer|ssh|ssh://joe@host/display/2'])
        self.assertEqual(len(self.rows(self.plan())), 3)


if __name__ == '__main__':
    unittest.main()
