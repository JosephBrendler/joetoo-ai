#!/usr/bin/env python3
"""Run the diagnostic launcher with fake D-Bus/header, never a graphical app."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'tools/joetoo-kwin-correlation-probe'


class ProbeCLITests(unittest.TestCase):
    def test_arms_before_launch_and_passes_shell_pid_to_broker(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            script = folder / 'probe'
            source = CLI.read_text().replace(
                'source /usr/sbin/script_header_joetoo',
                'source "$JOETOO_TEST_HEADER"', 1)
            script.write_text(source)
            fake_header = folder / 'header'
            fake_header.write_text('''notice=5
err=2
checknotroot() { :; }
j_msg() { printf '%s\\n' "${*: -1}"; }
''')
            mock_bus = folder / 'qdbus6'
            mock_bus.write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$JOETOO_TEST_CALLS"
case "$3" in
  *.BeginCorrelation) printf '%s\\n' test-request-0001 ;;
  *.PollCorrelation) printf '%s\\n' '{"state":"MATCHED","window_uuid":"d848c4c9-64ed-48bf-b083-40230314d5ab"}' ;;
esac
''')
            mock_bus.chmod(0o755)
            calls = folder / 'calls'
            env = os.environ.copy()
            env.update(JOETOO_TEST_HEADER=str(fake_header),
                       JOETOO_TEST_CALLS=str(calls),
                       PATH=str(folder) + os.pathsep + env['PATH'])
            run = subprocess.run(['bash', str(script), 'konsole',
                                  '--', 'true'], env=env, capture_output=True,
                                 text=True, timeout=5)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            lines = calls.read_text().splitlines()
            self.assertIn('BeginCorrelation', lines[0])
            self.assertIn('SetCorrelationPid', lines[1])
            self.assertIn('PollCorrelation', lines[2])
            self.assertIn('window_uuid', run.stdout)


if __name__ == '__main__':
    unittest.main()
