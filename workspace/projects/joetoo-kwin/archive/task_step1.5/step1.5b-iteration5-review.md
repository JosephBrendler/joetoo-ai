# Step 1.5b messaging follow-up

The focused patch is relative to the existing uncommitted Iteration 4 candidate;
it includes the CLI and test changes made in this iteration. Earlier review
artifacts are preserved and describe the earlier candidate.

Submission and shortcut invocation each announce with `-n` and immediately
report the captured action status. Verification announces on a closed line;
the broker detail uses `-n` and is completed by handle_result on that line.
Header wrapping still applies to long details on narrow terminals.
The existing reporting policy is shared through report_action: preserve action
failure, separately decode auxiliary reporting bits, and stop on either failure.
No movement geometry, protocol, broker or resident code changed this iteration.

Validation: 190 Python tests passed without skips, including real installed-header
line-format coverage and portable failure tests; 3 Node test files passed.
Bash syntax, ShellCheck and whitespace checks passed. Logs use the
step1.5b-iteration5 prefix. No native KWin operations were performed.

The maintainer's demonstration ran at verbosity 7 and exited 1 at its intentional
simulated failure. Its timestamp example saves result but subsequently calls
handle_result with the status of j_msg; recommend passing "$result" instead.
Skill and demonstration files were not edited.

Maintainer review and native formatting validation are next. Publication and
deployment remain gated. The earlier native desktop diagnostic discrepancy
is outside this messaging change and remains unresolved.
