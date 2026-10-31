"""Actual -o orchestration with process/broker doubles; no GUI/network calls."""
import os
from pathlib import Path
import subprocess
import time
import unittest
import test_step1_5c_launch as configured


class CorrectionsTests(configured.ConfiguredLaunchTests):
    def setUp(self):
        super().setUp()
        self.write_config(['1|konsole|local|btop', '2|konsole|local|btop', '3|konsole|local|btop'])
        text = self.client.read_text().replace("launch_managed_window() {\n    printf 'launch:",
                                               "unused_launch_double() {\n    printf 'launch:")
        text = text.replace('#-----[ main script ]', r'''
confirm_continue_or_exit() {
    printf 'confirm\n' >> "$TRACE"
    if [[ ${WAIT_CONFIRM:-} == yes ]]; then read -r reply; [[ $reply == y ]];
    else [[ ${CANCEL:-} != yes ]]; fi
}
# Retain the baseline preflight query double; override only transaction methods.
eval "$(declare -f qdbus6 | sed '1s/qdbus6/preflight_bus/')"
qdbus6() {
    case $3 in
    *.SubmitManagedLaunch)
        printf 'submit:%s\n' "$5" >> "$TRACE"
        printf '{"placement_request_id":"place-%s","registration_request_id":"reg-%s"}\n' "$5" "$5" ;;
    *.SetManagedLaunchPid) printf 'pid:%s\n' "$4" >> "$TRACE" ;;
    *.PollManagedLaunch)
        if [[ $4 == reg-2 && ${FAILURE_KIND:-} == registration ]]; then
            printf '{"state":"failed"}\n'
        elif [[ $4 == reg-2 && ${FAILURE_KIND:-} == ambiguous ]]; then
            printf '{"state":"ambiguous"}\n'
        else printf '{"state":"registered","managed_id":"win-test","window_uuid":"uuid-test"}\n'; fi ;;
    *.Status)
        if [[ $4 == place-2 ]]; then
            case ${FAILURE_KIND:-} in
            placement|registration) printf 'ERROR controlled middle failure\n' ;;
            busy) printf 'PENDING\n' ;;
            *) printf 'OK verified\n' ;; esac
        else printf 'OK verified\n'; fi ;;
    *) preflight_bus "$@" ;;
    esac
}
#-----[ main script ]''')
        # Do not wait 15s on the intentionally unresolved request in this test.
        text = text.replace('_wr_limit=150', '_wr_limit=1')
        self.client.write_text(text)
        (self.folder / 'konsole').write_text('''#!/bin/sh
exec >/dev/null 2>&1
if [ -e /proc/self/fd/9 ]; then echo inherited-lock >> "$TRACE"; fi
echo child:$$ >> "$TRACE"
if [ "${KEEP_CHILD:-}" = yes ]; then exec sleep 10; fi
''')
        (self.folder / 'konsole').chmod(0o755)

    def run_client(self, **values):
        return subprocess.run(['bash', str(self.client), '-o', '-f', str(self.config)],
                              env={**self.env, **values}, text=True, capture_output=True, timeout=20)

    def test_middle_failure_continues_and_identifies_incomplete_layout(self):
        for kind in ('placement', 'registration'):
            with self.subTest(kind=kind):
                self.calls.unlink(missing_ok=True)
                result = self.run_client(FAILURE_KIND=kind)
                trace = self.calls.read_text()
                self.assertNotEqual(result.returncode, 0)
                self.assertLess(trace.index('submit:1'), trace.index('submit:2'))
                self.assertLess(trace.index('submit:2'), trace.index('submit:3'))
                self.assertIn('Configured layout: [2/3]', result.stdout)
                self.assertIn('layout is incomplete', result.stdout + result.stderr)
                self.assertIn('Launching desktop [2] slot [1]', result.stdout)
                self.assertNotIn('inherited-lock', trace)
                # No rollback/close methods exist in the broker double; all three
                # processes are attempted and none is terminated by orchestration.

    def test_indeterminate_or_ambiguous_transaction_stops(self):
        for kind in ('busy', 'ambiguous'):
            with self.subTest(kind=kind):
                self.calls.unlink(missing_ok=True)
                result = self.run_client(FAILURE_KIND=kind)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('submit:2', self.calls.read_text())
                self.assertNotIn('submit:3', self.calls.read_text())

    def test_lock_refuses_competitor_before_confirmation_and_releases_on_cancel(self):
        first = subprocess.Popen(['bash', str(self.client), '-o', '-f', str(self.config)],
            env={**self.env, 'WAIT_CONFIRM': 'yes'}, stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        try:
            deadline = time.monotonic() + 5
            while not self.calls.exists() or 'confirm' not in self.calls.read_text():
                self.assertIsNone(first.poll())
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.02)
            competing = self.run_client()
            self.assertNotEqual(competing.returncode, 0)
            self.assertIn('Busy:', competing.stderr + competing.stdout)
            self.assertEqual(self.calls.read_text().count('confirm'), 1)
            self.assertNotIn('submit:', self.calls.read_text())
            first.communicate('n\n', timeout=5)
            self.assertNotEqual(first.returncode, 0)
            self.assertEqual(self.run_client().returncode, 0)
        finally:
            if first.poll() is None: first.kill(); first.wait()
            if first.stdin is not None and not first.stdin.closed: first.stdin.close()

    def test_reacquire_after_error_and_normal_exit(self):
        self.assertNotEqual(self.run_client(FAILURE_KIND='placement').returncode, 0)
        self.assertEqual(self.run_client().returncode, 0)
        self.assertEqual(self.run_client().returncode, 0)
        self.assertNotIn('inherited-lock', self.calls.read_text())

    def test_reacquire_after_termination(self):
        first = subprocess.Popen(['bash', str(self.client), '-o', '-f', str(self.config)],
            env={**self.env, 'WAIT_CONFIRM': 'yes'}, stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            while not self.calls.exists() or 'confirm' not in self.calls.read_text():
                self.assertLess(time.monotonic(), deadline); time.sleep(.02)
            first.terminate(); first.wait(timeout=5)
            self.assertEqual(self.run_client().returncode, 0)
        finally:
            if first.poll() is None: first.kill(); first.wait()
            if first.stdin is not None and not first.stdin.closed: first.stdin.close()

    def test_live_application_children_do_not_retain_lock(self):
        children = []
        try:
            result = self.run_client(KEEP_CHILD='yes', FAILURE_KIND='placement')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Configured layout: [2/3]', result.stdout)
            deadline = time.monotonic() + 5
            while len(children) < 3:
                children = [int(line.split(':')[1]) for line in self.calls.read_text().splitlines()
                            if line.startswith('child:')]
                self.assertLess(time.monotonic(), deadline); time.sleep(.02)
            for pid in children:
                os.kill(pid, 0)
                self.assertFalse(Path(f'/proc/{pid}/fd/9').exists())
            self.assertEqual(self.run_client().returncode, 0)
            self.assertNotIn('inherited-lock', self.calls.read_text())
        finally:
            for pid in children:
                try: os.kill(pid, 15)
                except ProcessLookupError: pass

    def test_truthful_launch_pid_message(self):
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Launched Konsole operation; launch-process PID [', result.stdout)
        self.assertIn('interactive Bash PID is reported inside the terminal', result.stdout)
        self.assertNotIn('Launched [env], shell PID', result.stdout)

# This harness uses the real transaction function, unlike the baseline test
# class. Run its focused cases only; the baseline cases run in their own module.
for _name in dir(configured.ConfiguredLaunchTests):
    if _name.startswith('test_') and _name not in CorrectionsTests.__dict__:
        setattr(CorrectionsTests, _name, None)
