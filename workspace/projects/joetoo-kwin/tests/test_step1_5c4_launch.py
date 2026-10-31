"""Actual mixed orchestration with mocked resource API and application processes."""
from pathlib import Path
import unittest
import os
import time
from test_step1_5a_plan import INSTALLED_HEADER_AVAILABLE
from test_step1_5c_corrections import CorrectionsTests as _CorrectionsHarness


class GraphicalLaunchTests(_CorrectionsHarness):
    def setUp(self):
        super().setUp()
        self.env['HOME'] = str(self.folder)
        (self.folder / 'folder with spaces').mkdir()
        self.write_config(['1|konsole|local|btop', '2|dolphin|local|folder with spaces',
                           '3|konsole|local|btop'])
        dolphin = self.folder / 'dolphin'
        dolphin.write_text('''#!/bin/sh
exec >/dev/null 2>&1
printf 'dolphin-arg:%s\\n' "$@" >> "$TRACE"
printf 'dolphin-pid:%s\\n' "$$" >> "$TRACE"
if [ "${KEEP_DOLPHIN:-}" = yes ]; then exec sleep 20; fi
''')
        dolphin.chmod(0o755)
        helper = self.folder / 'libexec/joetoo-kwin-launch-functions'
        helper.write_text(helper.read_text() + r'''
launch_resource() {
    printf 'resource:%s\n' "$1" >> "$TRACE"
    case $1 in
        local-path) command python3 "$(dirname -- "${BASH_SOURCE[0]}")/joetoo_kwin_launch_resources.py" "$@" ;;
        snapshot) printf '{"owner":":owner","ids":["one"],"count":%s}\n' "${SNAPSHOT_COUNT:-1}" ;;
        provision) [[ ${PROVISION_FAIL:-} != yes ]] || return 1; printf '%s\n' "$3" ;;
        verify) [[ ${VERIFY_FAIL:-} != yes ]] || return 1; printf '%s\n' "$3" ;;
    esac
}
''')

    def test_mixed_order_and_literal_dolphin_argv(self):
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        trace = self.calls.read_text()
        self.assertLess(trace.index('submit:1'), trace.index('submit:2'))
        self.assertLess(trace.index('submit:2'), trace.index('submit:3'))
        self.assertIn('dolphin-arg:--new-window\ndolphin-arg:--\ndolphin-arg:' + str(self.folder / 'folder with spaces'), trace)
        self.assertLess(trace.index('resource:snapshot'), trace.index('confirm'))
        self.assertLess(trace.index('confirm'), trace.index('resource:provision'))
        self.assertLess(trace.index('resource:provision'), trace.index('submit:1'))
        self.assertIn('required [3]', result.stdout)

    def test_dry_run_is_offline_and_mixed_slots_remain_in_file_order(self):
        self.write_config(['7|dolphin|local|', '7|konsole|local|btop', '7|dolphin|local|.'])
        output = self.run_cli('-c', '-f', str(self.config))
        self.assertIn('DRY RUN', output)
        self.assertLess(output.index('dolphin'), output.index('btop'))
        self.assertFalse(self.calls.exists())

    @unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed header unavailable')
    def test_mixed_plan_with_installed_header(self):
        self.client.write_text(self.client.read_text().replace(
            'source "' + str(self.mock_header) + '"',
            'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))
        self.test_mixed_order_and_literal_dolphin_argv()

    def test_relative_target_uses_home_with_config_elsewhere(self):
        elsewhere = self.folder / 'elsewhere'
        elsewhere.mkdir()
        self.config = elsewhere / 'plan.conf'
        self.write_config(['2|dolphin|local|folder with spaces'])
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('dolphin-arg:' + str(self.folder / 'folder with spaces'), self.calls.read_text())

    def test_capacity_notice_matches_existing_or_missing_count(self):
        for count in ('1', '3', '8'):
            with self.subTest(count=count):
                result = self.run_client(SNAPSHOT_COUNT=count, CANCEL='yes')
                self.assertNotEqual(result.returncode, 0)
                if count == '1':
                    self.assertIn('append [2] missing desktops after confirmation', result.stdout)
                else:
                    self.assertIn('existing desktop capacity is adequate', result.stdout)
                    self.assertNotIn('missing desktops', result.stdout)

    def test_completed_dolphin_does_not_retain_launcher_lock(self):
        self.write_config(['2|dolphin|local|'])
        pid = None
        try:
            result = self.run_client(KEEP_DOLPHIN='yes')
            self.assertEqual(result.returncode, 0, result.stderr)
            deadline = time.monotonic() + 5
            while pid is None:
                for line in self.calls.read_text().splitlines():
                    if line.startswith('dolphin-pid:'): pid = int(line.split(':')[1])
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.02)
            os.kill(pid, 0)
            self.assertFalse(Path(f'/proc/{pid}/fd/9').exists())
            second = self.run_client(CANCEL='yes')
            self.assertEqual(self.calls.read_text().count('confirm'), 2)
            self.assertNotIn('Busy:', second.stdout + second.stderr)
            os.kill(pid, 0)  # The first Dolphin is still alive after reacquisition.
        finally:
            if pid is not None:
                try: os.kill(pid, 15)
                except ProcessLookupError: pass

    def test_capacity_failure_suppresses_every_application(self):
        for mode in ('PROVISION_FAIL', 'VERIFY_FAIL'):
            with self.subTest(mode=mode):
                self.calls.unlink(missing_ok=True)
                result = self.run_client(**{mode: 'yes'})
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('submit:', self.calls.read_text())

    def test_decline_cannot_provision_or_launch(self):
        result = self.run_client(CANCEL='yes')
        self.assertNotEqual(result.returncode, 0)
        trace = self.calls.read_text()
        self.assertIn('resource:snapshot', trace)
        self.assertNotIn('resource:provision', trace)
        self.assertNotIn('submit:', trace)

    def test_invalid_path_rejects_whole_plan(self):
        self.write_config(['1|konsole|local|btop', '2|dolphin|local|does not exist'])
        result = self.run_client()
        self.assertEqual(result.returncode, 2)
        trace = self.calls.read_text()
        self.assertNotIn('confirm', trace)
        self.assertNotIn('submit:', trace)

    def test_empty_dolphin_target_and_ambiguous_identity_stop(self):
        self.write_config(['1|konsole|local|btop', '2|dolphin|local|', '3|konsole|local|btop'])
        result = self.run_client(FAILURE_KIND='ambiguous')
        self.assertNotEqual(result.returncode, 0)
        trace = self.calls.read_text()
        self.assertIn('submit:2', trace)
        self.assertNotIn('submit:3', trace)
        self.assertIn('managed registration [ambiguous]', result.stdout + result.stderr)


# The base harness's cases are executed in its own module.
for _name in dir(_CorrectionsHarness):
    if _name.startswith('test_') and _name not in GraphicalLaunchTests.__dict__:
        setattr(GraphicalLaunchTests, _name, None)
del _CorrectionsHarness
