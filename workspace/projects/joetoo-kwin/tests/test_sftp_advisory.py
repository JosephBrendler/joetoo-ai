"""Bounded NSS/TCP advisory. All resolver/probe commands are mocked."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch, MagicMock
from test_step1_5a_plan import ROOT
from test_sftp import SftpLaunchTests as _Launch

with patch.object(sys, 'path', [str(ROOT / 'libexec')] + sys.path):
    spec = importlib.util.spec_from_file_location('sftp_advisory', ROOT / 'libexec/joetoo_kwin_sftp_advisory.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class AdvisoryTests(unittest.TestCase):
    def test_resolver_status_addresses_and_timeout_are_bounded(self):
        for rc, text, expected in [(0, '192.0.2.1 STREAM host\n192.0.2.1 DGRAM host\n2001:db8::1 STREAM host', 'resolved'),
                                   (2, '', 'failed'), (3, '', 'uncertain'), (0, 'bad output', 'uncertain')]:
            runner = MagicMock(return_value=subprocess.CompletedProcess([], rc, text))
            with patch.object(module.shutil, 'which', return_value='/fake/getent'):
                state, addresses = module.resolve('host', 250, runner)
            self.assertEqual(state, expected)
            self.assertEqual(runner.call_args.kwargs['timeout'], .25)
            self.assertEqual(runner.call_args.args[0], ['/fake/getent', 'ahosts', 'host'])
            if state == 'resolved': self.assertEqual(addresses, ['192.0.2.1', '2001:db8::1'])
        with patch.object(module.shutil, 'which', return_value=None):
            self.assertEqual(module.resolve('host', 1)[0], 'unavailable')
        with patch.object(module.shutil, 'which', return_value='/fake/getent'):
            self.assertEqual(module.resolve('host', 1, MagicMock(side_effect=subprocess.TimeoutExpired('getent', .001)))[0], 'timeout')

    def test_numeric_literals_skip_resolution_and_preserve_explicit_port(self):
        resolver = MagicMock(side_effect=AssertionError('DNS forbidden'))
        connector = MagicMock(return_value='open')
        for target in ['sftp://joe@192.0.2.1:2222/x', 'sftp://joe@[2001:db8::1]:2222/x']:
            state = module.advisory(target, 100, 2200, resolver, connector)
            self.assertEqual(state['resolution'], 'numeric'); self.assertEqual(state['warning'], '')
            self.assertEqual(connector.call_args.args[1], 2222)
        resolver.assert_not_called()

    def test_single_warning_alias_caution_and_timeout_setting(self):
        for resolution in ['failed', 'timeout', 'unavailable', 'uncertain']:
            connector = MagicMock(side_effect=AssertionError('No TCP without an address'))
            result = module.advisory('sftp://Alias', 200, 22, lambda *_: (resolution, []), connector)
            self.assertIn('KIO/SSH configuration may differ', result['warning'])
            self.assertIn('anyway', result['warning'])
            self.assertNotIn('cannot connect', result['warning'])
            if resolution == 'timeout': self.assertIn('sftp_advisory_timeout_ms', result['warning'])
            connector.assert_not_called()

    def test_tcp_open_does_not_claim_sftp_and_other_results_are_qualified(self):
        for state in ['open', 'failed', 'timeout', 'uncertain']:
            result = module.advisory('sftp://host', 200, 2200, lambda *_: ('resolved', ['192.0.2.1']), lambda *_: state)
            self.assertEqual(result['port'], 2200)
            self.assertNotIn('authenticated', result['warning'])
            if state == 'open': self.assertEqual(result['warning'], '')
            if state == 'timeout':
                self.assertIn('timeout', result['warning']); self.assertNotIn('host connectivity check failed', result['warning'])

    def test_nc_probe_argv_bounds_statuses_and_unavailable_tool(self):
        for code, stderr, expected in [(0, '', 'open'), (1, '', 'failed'),
                                       (1, 'unsupported option', 'uncertain'), (2, '', 'uncertain')]:
            runner = MagicMock(return_value=subprocess.CompletedProcess([], code, '', stderr))
            with patch.object(module.shutil, 'which', return_value='/fake/nc'):
                self.assertEqual(module.probe_tcp(['2001:db8::1'], 2222, 100, runner), expected)
            args = runner.call_args.args[0]
            self.assertEqual(args, ['/fake/nc', '-n', '-z', '-w', '1', '2001:db8::1', '2222'])
            self.assertLessEqual(runner.call_args.kwargs['timeout'], .1)
        with patch.object(module.shutil, 'which', return_value=None):
            self.assertEqual(module.probe_tcp(['192.0.2.1'], 22, 100), 'unavailable')
        with patch.object(module.shutil, 'which', return_value='/fake/nc'):
            runner = MagicMock(side_effect=subprocess.TimeoutExpired('nc', .1))
            self.assertEqual(module.probe_tcp(['192.0.2.1'], 22, 100, runner), 'timeout')


class AdvisoryLaunchTests(_Launch):
    def test_warning_does_not_change_uri_counts_or_following_entries(self):
        result = self.run_client(MOCK_RESOLVE='fail')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('SFTP advisory: local name resolution failed'), 1)
        trace = self.calls.read_text()
        self.assertIn('dolphin-arg:sftp://joe@host/home/joe/', trace)
        self.assertIn('submit:2', trace); self.assertIn('Configured layout: [3/3]', result.stdout)
        self.assertNotIn('tcp:', trace)
        self.assertLess(trace.index('confirm'), trace.index('resolver:'))
        self.assertLess(trace.index('resolver:'), trace.index('submit:4'))

    def test_favorable_resolution_tcp_failure_and_timeout_still_launch(self):
        for state in ['failed', 'timeout', 'uncertain', 'open']:
            result = self.run_client(MOCK_TCP=state)
            self.assertEqual(result.returncode, 0, result.stderr)
            if state == 'failed': self.assertIn('TCP connectivity check failed', result.stdout)
            if state == 'timeout': self.assertIn('sftp_advisory_timeout_ms', result.stdout)
            self.assertNotIn('authentication succeeded', result.stdout)

    def test_numeric_uri_no_resolver_and_configured_default_probe_port(self):
        for target in ['sftp://192.0.2.1/', 'sftp://[2001:db8::1]/']:
            self.write_config(['4|dolphin|sftp|' + target], extra='sftp_advisory_ssh_port=2200')
            if self.calls.exists(): self.calls.unlink()
            self.assertEqual(self.run_client().returncode, 0)
            trace = self.calls.read_text(); self.assertNotIn('resolver:', trace); self.assertIn('tcp:2200', trace)

    def test_disabled_and_unavailable_helper_never_block_launch(self):
        self.write_config(['4|dolphin|sftp|sftp://host'], extra='sftp_advisory_enabled=$FALSE')
        self.assertEqual(self.run_client().returncode, 0)
        self.assertNotIn('resolver:', self.calls.read_text()); self.assertNotIn('tcp:', self.calls.read_text())
        self.write_config(['5|dolphin|sftp|sftp://host'])
        (self.folder / 'libexec/joetoo_kwin_sftp_advisory.py').write_text('raise RuntimeError("unavailable")')
        self.assertEqual(self.run_client().returncode, 0)

    def test_dry_run_and_cancel_have_no_resolution_or_tcp_activity(self):
        self.run_cli('-c', '-f', str(self.config)); self.assertFalse(self.calls.exists())
        self.assertNotEqual(self.run_client(CANCEL='yes').returncode, 0)
        trace = self.calls.read_text(); self.assertNotIn('resolver:', trace); self.assertNotIn('tcp:', trace)

    def test_invalid_settings_reject_before_any_advisory(self):
        for extra in ['sftp_advisory_timeout_ms=0', 'sftp_advisory_timeout_ms=10001',
                      'sftp_advisory_ssh_port=65536', 'sftp_advisory_enabled=yes']:
            self.write_config(['4|dolphin|sftp|sftp://host'], extra=extra)
            self.assertNotEqual(self.run_client().returncode, 0)
            self.assertNotIn('resolver:', self.calls.read_text() if self.calls.exists() else '')


for name in dir(_Launch):
    if name.startswith('test_') and name not in AdvisoryLaunchTests.__dict__:
        setattr(AdvisoryLaunchTests, name, None)
del _Launch
