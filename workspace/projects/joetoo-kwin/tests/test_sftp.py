"""Offline SFTP contract, installed-metadata discovery and real launcher mocks."""
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from test_step1_5a_plan import ROOT, INSTALLED_HEADER_AVAILABLE
from test_step1_5c4_launch import GraphicalLaunchTests as _Graphical


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'libexec' / (name + '.py'))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


uri = module('joetoo_kwin_sftp_target')
capability = module('joetoo_kwin_sftp_capability')
PLUGIN = b'\x7fELF fixture org.kde.kio.worker.sftp KDE-KIO-Protocols'


class SftpContractTests(unittest.TestCase):
    def test_valid_uri_table_and_one_pass_encoding(self):
        for target, expected in [
            ('sftp://nuthuvia', 'sftp://nuthuvia'),
            ('sftp://joe@files.example:2222/home/joe/', 'sftp://joe@files.example:2222/home/joe/'),
            ('sftp://192.0.2.10/', 'sftp://192.0.2.10/'),
            ('sftp://joe@[2001:db8::10]:2222/srv/Project%20Files', 'sftp://joe@[2001:db8::10]:2222/srv/Project%20Files'),
            ('sftp://My_Alias/srv/%e2%82%ac%23data', 'sftp://My_Alias/srv/%E2%82%AC%23data'),
            ('sftp://host/a//b/', 'sftp://host/a//b/'),
            ('sftp://host/100%25', 'sftp://host/100%25'),
            ('sftp://host/%252F', 'sftp://host/%252F'),
            ('sftp://host/$(touch%20NOFILE)', 'sftp://host/%24%28touch%20NOFILE%29')]:
            with self.subTest(target=target): self.assertEqual(uri.sftp_uri(target), expected)

    def test_invalid_uri_table(self):
        targets = ['', 'host', 'joe@host:docs', 'sftp:///x', 'ftp://host/',
                   'sftp://joe:SECRET@host/', 'sftp://joe%3ASECRET@host/', 'sftp://@host/',
                   'sftp://a@b@host/', 'sftp://[fe80::1%25eth0]/', 'sftp://2001:db8::1/',
                   'sftp://[not-v6]/', 'sftp://host:', 'sftp://host:0/', 'sftp://host:65536/',
                   'sftp://host:022/', 'sftp://host:99999999999999999/', 'sftp://host../',
                   'sftp://999.1.1.1/', 'sftp://host/a b', 'sftp://host/é', 'sftp://host/a?secret=x',
                   'sftp://host/a#x', 'sftp://host/x|panel', 'sftp://host/a\\b', 'sftp://host/%',
                   'sftp://host/%2F', 'sftp://host/%5c', 'sftp://host/%00', 'sftp://host/%7f',
                   'sftp://host/%FF', 'sftp://host/./x', 'sftp://host/%2e%2E/x', 'sftp://host/\n']
        for target in targets:
            with self.subTest(target=target), self.assertRaises(ValueError): uri.sftp_uri(target)

    def test_rejected_stdin_never_echoes_credentials(self):
        result = subprocess.run([sys.executable, str(ROOT / 'libexec/joetoo_kwin_sftp_target.py')],
                                input='sftp://joe:VERYSECRET@host/', text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('VERYSECRET', result.stdout + result.stderr)

    def test_plugin_path_and_package_records_without_qtpaths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); worker = root / 'kf6/kio/sftp.so'
            worker.parent.mkdir(parents=True); worker.write_bytes(PLUGIN)
            self.assertEqual(capability.discover_worker(100, roots=[root], records=[], tools=[])['worker'], str(worker))
            record = root / 'CONTENTS'; record.write_text('obj ' + str(worker) + ' md5 123\n')
            self.assertEqual(capability.discover_worker(100, roots=[], records=[record], tools=[])['worker'], str(worker))
            worker.unlink()
            with self.assertRaisesRegex(ValueError, 'not disproved'):
                capability.discover_worker(100, roots=[], records=[record], tools=[])

    def test_qt6_discovery_nonstandard_prefix_and_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'custom'; worker = root / 'kf6/kio/sftp.so'
            worker.parent.mkdir(parents=True); worker.write_bytes(PLUGIN)
            calls = []
            def runner(args, **kwargs):
                calls.append(args)
                return subprocess.CompletedProcess(args, 0, '6.10.0' if args[-1] == 'QT_VERSION' else str(root))
            self.assertEqual(capability.discover_worker(1000, roots=[], records=[], tools=['qtpaths'], runner=runner)['worker'], str(worker))
            self.assertEqual(len(calls), 2)
            worker.write_bytes(b'not a KIO plugin')
            with self.assertRaises(ValueError): capability.discover_worker(100, roots=[root], records=[], tools=[])

    def test_tool_failure_timeout_and_missing_detector_are_inconclusive(self):
        def runner(*args, **kwargs): raise subprocess.TimeoutExpired('qtpaths', .1)
        with self.assertRaisesRegex(ValueError, 'not disproved'):
            capability.discover_worker(100, roots=[], records=[], tools=['qtpaths'], runner=runner)
        for value in (0, True, 10001):
            with self.assertRaises(ValueError): capability.discover_worker(value, roots=[], records=[], tools=[])


class SftpLaunchTests(_Graphical):
    def setUp(self):
        super().setUp()
        self.write_config(['4|dolphin|sftp|sftp://joe@host/home/joe/|panel',
                           '2|konsole|local|btop', '4|dolphin|local||under'])
        root = self.folder / 'plugins'
        worker = root / 'kf6/kio/sftp.so'; worker.parent.mkdir(parents=True); worker.write_bytes(PLUGIN)
        self.env['QT_PLUGIN_PATH'] = str(root)

    def test_mixed_grouped_managed_launch_and_unverified_remote_reporting(self):
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        trace = self.calls.read_text()
        self.assertIn('dolphin-arg:--new-window\ndolphin-arg:--\ndolphin-arg:sftp://joe@host/home/joe/', trace)
        self.assertEqual([s for s in trace.splitlines() if s.startswith('submit:')], ['submit:4', 'submit:4', 'submit:2'])
        self.assertIn('authentication and remote listing are not verified', result.stdout)
        self.assertIn('Configured layout: [3/3]', result.stdout)

    def test_invalid_last_entry_and_malformed_record_redact_before_any_launch(self):
        for target in ('sftp://joe:VERYSECRET@host/', 'sftp://host/x|over|VERYSECRET'):
            self.write_config(['1|konsole|local|btop', '2|dolphin|sftp|' + target])
            result = self.run_client()
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('VERYSECRET', result.stdout + result.stderr)
            trace = self.calls.read_text() if self.calls.exists() else ''
            self.assertNotIn('confirm', trace); self.assertNotIn('submit:', trace)

    def test_dry_run_and_decline_do_not_launch_or_probe_remote(self):
        result = self.run_cli('-c', '-f', str(self.config))
        self.assertIn('sftp://joe@host/home/joe/', result)
        self.assertFalse(self.calls.exists())
        result = self.run_client(CANCEL='yes')
        self.assertNotEqual(result.returncode, 0)
        trace = self.calls.read_text(); self.assertNotIn('submit:', trace); self.assertNotIn('resource:provision', trace)

    def test_capability_uncertainty_rejects_before_confirmation(self):
        helper = self.folder / 'libexec/joetoo_kwin_sftp_capability.py'
        helper.write_text('import sys\nprint("Cannot confirm KIO SFTP capability offline",file=sys.stderr)\nsys.exit(2)\n')
        result = self.run_client()
        self.assertNotEqual(result.returncode, 0)
        trace = self.calls.read_text() if self.calls.exists() else ''
        self.assertNotIn('confirm', trace); self.assertNotIn('submit:', trace)
        self.assertIn('Cannot confirm', result.stderr)

    def test_ambiguous_identity_stops_and_does_not_claim_remote_success(self):
        self.write_config(['2|dolphin|sftp|sftp://host', '4|konsole|local|btop'])
        result = self.run_client(FAILURE_KIND='ambiguous')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not verified', result.stdout)
        self.assertNotIn('Configured layout: [3/3]', result.stdout)
        self.assertNotIn('submit:4', self.calls.read_text())

    def test_missing_dolphin_rejects_before_confirmation(self):
        self.client.write_text(self.client.read_text().replace('#-----[ main script ]', r'''
command() {
    if [[ $1 == -v && ${2:-} == dolphin ]]; then return 1; fi
    builtin command "$@"
}
#-----[ main script ]'''))
        result = self.run_client()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing executable [dolphin]', result.stdout + result.stderr)
        self.assertNotIn('confirm', self.calls.read_text() if self.calls.exists() else '')

    def test_validator_argv_has_no_raw_target(self):
        python = self.folder / 'python3'
        python.write_text('#!/bin/sh\nprintf "python-args:%s\\n" "$*" >> "$TRACE"\nexec ' + shlex.quote(sys.executable) + ' "$@"\n')
        python.chmod(0o755)
        self.write_config(['4|dolphin|sftp|sftp://joe:VERYSECRET@host/'])
        result = self.run_client()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('VERYSECRET', self.calls.read_text() + result.stdout + result.stderr)

    @unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed header unavailable')
    def test_sftp_with_installed_header(self):
        self.client.write_text(self.client.read_text().replace(
            'source "' + str(self.mock_header) + '"', 'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))
        self.test_mixed_grouped_managed_launch_and_unverified_remote_reporting()


for _name in dir(_Graphical):
    if _name.startswith('test_') and _name not in SftpLaunchTests.__dict__:
        setattr(SftpLaunchTests, _name, None)
del _Graphical
