"""Real orchestration with fake broker/processes; no GUI or bus."""
import unittest
import subprocess
import time
from test_step1_5c_corrections import CorrectionsTests as _Base


class GroupedLaunchTests(_Base):
    def setUp(self):
        super().setUp()
        self.write_config(['4|konsole|local|btop|panel', '2|konsole|local|btop',
                           '4|konsole|local|btop|over'])
        # Observe group finalization without replacing production orchestration.
        marker = '#-----[ main script ]'
        self.client.write_text(self.client.read_text().replace(marker, r'''
eval "$(declare -f qdbus6 | sed '1s/qdbus6/layer_base_bus/')"
qdbus6() {
    case $3 in
        *.SubmitInitialLayout) printf 'finalize:%s\n' "$4" >> "$TRACE"; printf 'layout-id\n' ;;
        *.InitialLayoutStatus) printf '{"state":"%s"}\n' "${INITIAL_STATE:-SUCCEEDED}" ;;
        *) layer_base_bus "$@" ;;
    esac
}
#-----[ main script ]'''))

    def test_first_appearance_group_order_and_finalize_before_next_group(self):
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.calls.read_text().splitlines()
        stages = [line for line in lines if line.startswith(('submit:', 'finalize:'))]
        self.assertEqual([line.split(':')[0] for line in stages],
                         ['submit', 'submit', 'finalize', 'submit', 'finalize'])
        self.assertEqual([line for line in stages if line.startswith('submit:')], ['submit:4', 'submit:4', 'submit:2'])
        self.assertIn('"layer":"over"', stages[2])
        self.assertIn('"focus_timeout_ms":500', stages[2])
        self.assertIn('"focus_poll_interval_ms":25', stages[2])

    def test_effective_focus_timing_reaches_transaction_payload(self):
        with self.config.open('a') as config:
            config.write('\ninitial_focus_timeout_ms=750\ninitial_focus_poll_interval_ms=30\n')
        result = self.run_client()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"focus_timeout_ms":750', self.calls.read_text())
        self.assertIn('"focus_poll_interval_ms":30', self.calls.read_text())

    def test_invalid_focus_timing_launches_nothing(self):
        original = self.config.read_text()
        for timeout, interval in [('10', '30'), ('0', '25'), ('2001', '25'),
                                  ('500', '0'), ('500', '251'), ('2+3', '1')]:
            self.config.write_text(original + f'\ninitial_focus_timeout_ms="{timeout}"\ninitial_focus_poll_interval_ms={interval}\n')
            result = self.run_client()
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('submit:', self.calls.read_text() if self.calls.exists() else '')

    def test_o_without_f_selects_xdg_user_config(self):
        selected = self.folder / 'xdg/joetoo-kwin/joetoo-kwin.conf'
        selected.parent.mkdir(parents=True)
        selected.write_text(self.config.read_text())
        result = subprocess.run(['bash', str(self.client), '-o'],
            env={**self.env, 'XDG_CONFIG_HOME': str(self.folder / 'xdg')}, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(selected), result.stdout)

    def test_nonterminal_initial_layout_stops_next_group_and_holds_lock(self):
        # Shorten only test polling, retaining actual state decisions.
        self.client.write_text(self.client.read_text().replace('_op_try<100', '_op_try<1'))
        result = self.run_client(INITIAL_STATE='RUNNING')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('submit:2', self.calls.read_text())
        self.assertIn('Initial stack/focus incomplete', result.stdout + result.stderr)

    def test_lock_is_held_while_initial_layout_is_pending(self):
        process = subprocess.Popen(['bash', str(self.client), '-o', '-f', str(self.config)],
            env={**self.env, 'INITIAL_STATE': 'RUNNING'}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            while not self.calls.exists() or 'finalize:' not in self.calls.read_text():
                self.assertIsNone(process.poll())
                self.assertLess(time.monotonic(), deadline); time.sleep(.02)
            competitor = self.run_client()
            self.assertNotEqual(competitor.returncode, 0)
            self.assertIn('Busy:', competitor.stdout + competitor.stderr)
        finally:
            if process.poll() is None: process.terminate()
            process.wait(timeout=5)


for _name in dir(_Base):
    if _name.startswith('test_') and _name not in GroupedLaunchTests.__dict__:
        setattr(GroupedLaunchTests, _name, None)
del _Base
