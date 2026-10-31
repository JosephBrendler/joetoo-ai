"""Configured launch orchestration: no live bus, GUI or network."""
import json
import shutil
import subprocess
import unittest
from test_step1_5a_plan import PlannerHarness, ROOT, INSTALLED_HEADER_AVAILABLE
from test_step1_4c_queries import ReadOnlyManagedQueryTests


class SlotGuardTests(ReadOnlyManagedQueryTests):
    def test_original_association_survives_manual_move_and_conflict_is_atomic(self):
        self.sync(); self.register()
        record = self.broker.registry.managed_windows[next(iter(self.broker.registry.managed_windows))]
        record.observation['desktops'] = [9]
        record.observation['geometry']['x'] = 999
        summary = json.loads(self.broker.ListManaged())['windows'][0]
        self.assertEqual(summary['intended'], {'desktop': 3, 'slot': 1})
        for presence in ('present', 'missing', 'uncertain'):
            record.presence = presence
            previous = self.broker.request
            count = len(self.broker.registry.requests)
            with self.assertRaises(self.module.dbus.DBusException):
                self.broker.SubmitManagedLaunch('konsole', 3, 1, 0, 0, 800, 900)
            self.assertIs(self.broker.request, previous)
            self.assertEqual(len(self.broker.registry.requests), count)
        # Same mission/host is immaterial: another logical entry is allowed.
        self.assertTrue(self.broker.SubmitManagedLaunch('konsole', 3, 2, 0, 0, 800, 900))

    def test_placement_snapshot_includes_legacy_transactions(self):
        rid = self.broker.Submit(1, 0, 0, 800, 900)
        self.assertEqual(json.loads(self.broker.RegistryStatus())['placement_transaction'],
                         {'id': rid, 'state': 'PENDING'})


class ConfiguredLaunchTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('joetoo-kwin-launch-functions', 'joetoo-kwin-session.bashrc'):
            shutil.copyfile(ROOT / 'libexec' / name, self.folder / 'libexec' / name)
        self.env['BROKER_STATE'] = json.dumps({'observation': {'synchronized': True},
            'presence_counts': {'uncertain': 0}, 'request_counts': {'pending': 0, 'running': 0},
            'placement_transaction': {'state': 'IDLE'}})
        self.env['MANAGED'] = '{"windows":[]}'
        self.write_config(['1|konsole|local|btop', '2|konsole|local|btop'])
        self.client.write_text(self.client.read_text().replace('#-----[ main script ]', r'''
warn=4
confirm_continue_or_exit() { printf 'confirm\n' >> "$TRACE"; [[ ${CANCEL:-} != yes ]]; }
qdbus6() {
    case $3 in
    *.RegistryStatus) printf '%s\n' "$BROKER_STATE" ;;
    *.ListManaged) printf '%s\n' "$MANAGED" ;;
    *.ListObserved) printf '%s\n' '{"windows":[]}' ;;
    *.PollManagedLaunch) printf '%s\n' "{\"state\":\"${REG_STATE:-registered}\"}" ;;
    *.Status) printf '%s\n' "${PLACEMENT_STATE:-OK}" ;;
    esac
}
launch_managed_window() {
    printf 'launch:%s:%s\n' "$2" "$3" >> "$TRACE"
    launch_registration_id=reg; launch_placement_id=place
    [[ ${FAIL_FIRST:-} != yes || $3 != 1 ]]
}
#-----[ main script ]'''))

    def execute(self, expected=0):
        result = subprocess.run(['bash', str(self.client), '-o', '-f', str(self.config)],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return self.calls.read_text().splitlines() if self.calls.exists() else []

    def test_confirm_before_sequential_launches(self):
        self.assertEqual(self.execute(), ['confirm', 'launch:1:1', 'launch:1:2'])

    def test_cancel_launches_nothing(self):
        self.env['CANCEL'] = 'yes'
        self.assertEqual(self.execute(1), ['confirm'])

    def test_unsupported_entire_plan_launches_nothing(self):
        self.write_config(['1|konsole|local|btop', '2|vncviewer|via-ssh|example.invalid'])
        self.assertEqual(self.execute(2), [])

    def test_partial_failure_continues_independent_entries(self):
        self.env['FAIL_FIRST'] = 'yes'
        self.assertEqual(self.execute(1), ['confirm', 'launch:1:1', 'launch:1:2'])

    def test_uncertain_previous_completion_stops(self):
        self.env['PLACEMENT_STATE'] = 'VERIFYING'
        self.assertEqual(self.execute(1), ['confirm', 'launch:1:1'])

    def test_managed_conflict_prevents_confirmation(self):
        self.env['MANAGED'] = json.dumps({'windows': [{'managed_id': 'win-1', 'intended': {'desktop': 1, 'slot': 1}}]})
        self.assertEqual(self.execute(2), [])

    def test_same_host_in_distinct_slots_is_valid(self):
        # Dependency discovery is mocked; no actual probe or SSH runs here.
        for name in ('nc', 'ssh'):
            spy = self.folder / name
            spy.write_text('#!/bin/sh\nexit 99\n')
            spy.chmod(0o755)
        self.write_config(['1|konsole|ssh|example.invalid', '1|konsole|ssh|example.invalid'])
        self.assertEqual(self.execute(), ['confirm', 'launch:1:1', 'launch:2:1'])

    def test_busy_preflight_prevents_confirmation(self):
        self.env['BROKER_STATE'] = json.dumps({'observation': {'synchronized': True},
            'presence_counts': {'uncertain': 0}, 'request_counts': {'pending': 0, 'running': 0},
            'placement_transaction': {'state': 'VERIFYING'}})
        self.assertEqual(self.execute(1), [])


@unittest.skipUnless(INSTALLED_HEADER_AVAILABLE, 'installed header unavailable')
class InstalledConfiguredLaunchTests(ConfiguredLaunchTests):
    def setUp(self):
        super().setUp()
        self.client.write_text(self.client.read_text().replace(
            'source "' + str(self.mock_header) + '"',
            'source /usr/sbin/script_header_joetoo\nchecknotroot() { :; }', 1))


class SessionStartupTests(unittest.TestCase):
    def test_original_shell_survives_unreachable_and_ended_ssh(self):
        import os
        import tempfile
        for reachable in (0, 1):
            with self.subTest(reachable=reachable), tempfile.TemporaryDirectory() as directory:
                from pathlib import Path
                home = Path(directory)
                (home / '.bashrc').write_text('''
notice=5; warn=4; err=3
j_msg() { printf '%s\\n' "${*: -1}"; }
handle_result() { return "$1"; }
nc() { printf 'probe:%s\\n' "$*" >> "$TRACE"; return "$PROBE_RC"; }
ssh_wrapper() { printf 'ssh:%s pid:%s\\n' "$*" "$$" >> "$TRACE"; return 255; }
''')
                trace = home / 'trace'
                run = subprocess.run(['bash', '-c',
                    'printf "before:%s\\n" "$$"; source "$1"; printf "after:%s\\n" "$$"',
                    'test', str(ROOT / 'libexec/joetoo-kwin-session.bashrc')],
                    env={**os.environ, 'HOME': directory, 'TRACE': str(trace),
                         'JOETOO_SESSION_MODE': 'ssh', 'JOETOO_SESSION_TARGET': 'example.invalid',
                         'PROBE_RC': str(reachable)}, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                lines = run.stdout.splitlines()
                self.assertEqual(lines[0].replace('before:', ''), lines[-1].replace('after:', ''))
                self.assertIn('Manual retry: ssh_wrapper example.invalid', run.stdout)
                self.assertIn('probe:-z -w 2 example.invalid 22', trace.read_text())
                self.assertEqual('ssh:example.invalid' in trace.read_text(), reachable == 0)
