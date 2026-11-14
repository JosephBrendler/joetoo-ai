# Focused Step 1.5c native-feedback corrections

Branch: task/joetoo-kwin-step1.5c-configured-launch.
Starting HEAD: 06bf97a7df1b68c3e9dc7fbfb0f40a328c3ea560; working tree initially clean.
Current scope and handoff inspected; latest chat authorization bounds this iteration.

## Corrections and evidence

-o acquires a nonblocking flock before preflight/configuration/confirmation, using
XDG_RUNTIME_DIR/joetoo-kwin-launch.lock. The runtime directory must be user-owned,
not a symlink, and mode 700; the lock file must be regular/user-owned, not a symlink.
Creation uses umask 077. No fallback to shared /tmp. No lock-file unlinking: locks
remain on a stable inode, with kernel release on process exit or termination.
The CLI holds descriptor 9 until its invocation exits. -c/-m do not acquire it.
The managed application spawn explicitly closes descriptor 9 before running env,
Konsole and its descendants, preserving $! and SetManagedLaunchPid. Synchronous
short-lived helper commands may inherit it, but are awaited by the launcher.
Broker per-request Busy and identity/correlation mechanisms remain independent.

The message now says “Launched Konsole operation; launch-process PID [...]”, and
states that the interactive Bash PID is reported inside the terminal. Process
creation and PID correlation are unchanged.

New tests exercise actual open_plan and launch_managed_window with mocked broker
and executable processes (no real GUI/network). Window 1 succeeds, window 2 has
controlled registration or placement failure, window 3 is submitted; final count
is 2/3 and failure is conspicuous in the desktop/slot context. Mock application
children remain alive even after a failed layout; no close/rollback is performed.
No production continuation-policy correction was needed. Pending placement or
ambiguous registration instead prevents window 3. Additional tests hold confirmation,
reject the competitor before it confirms/submits, cancel the owner, and reacquire.
They cover error/normal exits, termination, truthful PID wording and reacquisition
while live mock application children have no descriptor 9.

242 Python tests PASS, no skips, including existing real installed-header integration.
All 3 Node test files PASS (this host's runner reports files rather than 14 cases).
Bash syntax, ShellCheck and complete diff whitespace checks PASS. Initial new test
harness inheritance error and resource warning were fixed before the final full run.
See step1.5c-corrections-{python,node,syntax,shellcheck}.log.

## Inventory

Modified tracked: joetoo-kwin; libexec/joetoo-kwin-launch-functions;
tests/test_step1_5c_launch.py (isolated runtime directory for tests);
task_step1.5/HANDOFF.md (Codex Section 5 row only).
New test: tests/test_step1_5c_corrections.py.
New evidence: this report, four correction logs and step1.5c-corrections.patch.
Temporary harness output resides under /tmp and is not part of the review patch.
Broker/resident/registry, startup workflow, scope and architectural documents untouched.

## Native evidence and next gate

Maintainer reports 235 Python / 14 JS tests on both backends, successful multiwindow
SSH/local launch, duplicate protection after movement, unreachable placeholders,
original local Bash PID continuity, missing observations and window survival across
broker restart. Those are human-provided results, not agent native executions.
The controlled Wayland probe established the missing pre-confirmation serialization.

The named task_step1.5/joetoo-kwin-concurrency-probe.py and
/tmp/joetoo-kwin-concurrency-6g23ppjo were unavailable locally; no copy was replaced,
created or executed. The new headless test exercises the same hold-confirmation
condition without live GUI behavior. Exact native probe review remains unavailable.

Maintainer next: review the focused diff and install by existing human procedure;
rerun the original separate-PTY probe on Wayland (and X11 where practical). Expect A
to wait at confirmation and B to exit nonzero with Busy, no confirmation or launch.
Cancel A and verify a new invocation can confirm; also verify normal completion
with living Konsole/SSH sessions does not retain the lock. No native operations,
installation, service changes, commit, push, PR or merge were performed by the agent.
