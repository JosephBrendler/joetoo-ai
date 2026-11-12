## Proposed addendum — isolated XCB fixture stabilization (2026-11-12)

Candidate reviewed against task branch `task/joetoo-kwin-step1.5d-integrated-regression`, HEAD `0afdcceaafde26dd153eb8ecf3b7a6ae20280c59`, plus an uncommitted change only to `tests/test_vnc_identity.py`. Starting tree was clean. Fetch was unavailable because `.git/FETCH_HEAD` is read-only; this is the inspected local baseline, not a claim of freshly fetched state.

The original fake peer sent its GetInputFocus synchronization reply before the ClientMessage. Thus the observer constructor could return before its nonblocking poll had an event available. A controlled probe withholding the event until after the original poll demonstrated that empty-poll interleaving. It does not prove this was the exact interleaving on iota01. The unmodified fixture passed 100/100 ordinary repetitions here.

The corrected peer sends the event before the synchronization reply, using the ChangeWindowAttributes request sequence for the event. NativeObserver's existing xcb_request_check must process the later reply; libxcb queues preceding events before finishing that wait. This is a receiving-side protocol barrier, not a sender acknowledgement or timing delay. The original single drain assertion, decoded event, event mask and peer-error assertions remain. Peer I/O has a two-second monotonic budget, checked writes, phase-specific error diagnostics and bounded teardown. Native ABI setup precedes socket/thread acquisition. Production observer behavior is unchanged.

Final candidate evidence:

- Focused `test_vnc_identity`: 7 PASS, 0 FAIL/ERROR/SKIP.
- Corrected exact fixture stress: 1000/1000 PASS; additional 100 repetitions showed no thread/file-descriptor growth after module import.
- Controlled missing-response probe: expected failure within 2.011 s with peer phase/timeout diagnostic and no surviving peer thread.
- Full Python discovery: 949 PASS, 0 FAIL/ERROR/SKIP, 122.203 s.
- Full JavaScript: 163 PASS, 0 FAIL/CANCEL/SKIP/TODO.
- Python AST syntax and git diff --check: PASS. No Bash files changed; Bash syntax/ShellCheck were not rerun.
- An exploratory sendall draft was rejected by the sandbox with EPERM (1000/1000 stress failures); the final candidate retains checked os.write. An initial controlled probe closed with unread event data and got a reset; the corrected probe consumed the event before teardown. An initial leak probe counted one-time libffi loading; the corrected baseline imports the test module first and shows no growth.

Commands for the focused and full suites:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_vnc_identity
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
node --test --test-isolation=none tests/test_*.js
git diff --check
# End of commands

```

This is offline socketpair/libxcb fixture evidence, not a new native desktop run. No production, locale, service or feature change was made. Preserve the historical iota01 948/949 result and eleven subsequent isolated passes above. Step 1.5d functional acceptance remains the maintainer's existing decision; publication remains separately authorized.
