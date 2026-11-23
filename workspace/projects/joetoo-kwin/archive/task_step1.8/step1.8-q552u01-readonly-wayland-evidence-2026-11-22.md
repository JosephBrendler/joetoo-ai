# Step 1.8 — q552u01 native Wayland evidence for read-only `-s` / `-i`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22. **Host:** `q552u01`, native Plasma Wayland (maintainer-reported session context). **Operator:** maintainer. **Task branch:** `task/joetoo-kwin-step1.8-cli-completion`. **Implementation:** `1670bea`; read-only transaction-state fix `f3fef58`; subsequent fixture-test repair `cadf992` was fast-forwarded and tested here. The current KWin version was not printed in these particular console excerpts.

**Provenance:** Selected, relevant excerpts from the maintainer's console messages in the Step 1.8 conversation. These are **not** a complete uninterrupted terminal transcript. Lines excluded for brevity are not presented as verbatim output; the results below should not be taken as evidence of unshown tests.

## Initial native read-only queries (before the `-s` fix)

The preexisting broker remained running during this testing; the maintainer reported `joetoo-kwind` uptime of **2 days 08:38:26**. No broker code change or clean restart was required for the helper correction.

```text
$ ./joetoo-kwin -l
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-010     2        1     present   succeeded  1e9aeb2f-ea2b-4685-8d1b-2fe995dc4876
win-007     3        1     missing   succeeded  db08cbb4-b3e1-48f2-adf7-ba4a17509128
win-008     3        2     present   succeeded  3bbbc9d0-ad11-4b60-96ae-364f9c35abe0
win-009     3        3     present   succeeded  612d4bba-ac04-451d-9fc3-3179faf856a5

$ ./joetoo-kwin -i win-010
Managed window information (broker record; not remote connection health)
MANAGED_ID: win-010
WINDOW_UUID: 1e9aeb2f-ea2b-4685-8d1b-2fe995dc4876
DESKTOP: 2
SLOT: 1
PRESENCE: present
PLACEMENT: succeeded
OBSERVATION: last-known (not independently verified live)
PID: 2285330
RESOURCE_CLASS: org.kde.konsole
LAST_KNOWN_FRAME: 96 32 1804 972

$ ./joetoo-kwin -i win-007
Managed window information (broker record; not remote connection health)
MANAGED_ID: win-007
WINDOW_UUID: db08cbb4-b3e1-48f2-adf7-ba4a17509128
DESKTOP: 3
SLOT: 1
PRESENCE: missing
PLACEMENT: succeeded
OBSERVATION: last-known (not independently verified live)
PID: 1039249
RESOURCE_CLASS: org.kde.konsole
LAST_KNOWN_FRAME: 19 54 1670 918

$ ./joetoo-kwin -s
Broker registry status (snapshot; not remote connection health)
State: Busy/uncertain
Managed windows: 4 (present=3, missing=1, uncertain=0)
Launch requests: 3 (pending=0, running=0, succeeded=3, failed=0, timeout=0, ambiguous=0)
Observation: synchronized; observed=9; revision=3498
Placement transaction: OK
Recovery: ready
Capabilities: managed_close=1, snapshot=1, viewer=1, initial_layout=1, single_raise=1
Attention: placement transaction active
```

The `-l` and `-i` results consistently distinguish three present managed records from the retained **missing** `win-007`; a missing reservation is not an unowned slot. `-s` initially misclassified the terminal placement state `OK` as active because `joetoo_kwin_readonly.py` used `state != 'IDLE'` for its Busy classification. This was a **CLI reporting defect**, not evidence of an active broker placement transaction.

## Correction and native retest

The maintainer applied a focused patch to `libexec/joetoo_kwin_readonly.py` and `tests/test_step1_8_readonly_cli.py`, committed and pushed it as **`f3fef58`** (commit message contains the harmless typo `tep1.8`). `PENDING`, `RUNNING`, and `VERIFYING` are active; `OK` is successful terminal; `ERROR` is terminal failure, not an active request; unknown states fail closed. The broker was **not restarted**.

```text
$ python3 -m unittest discover -s tests -p 'test_step1_8_readonly_cli.py' -v
... nine named tests reported ok, including
... test_status_placement_transaction_terminal_and_active_states ... ok
----------------------------------------------------------------------
Ran 9 tests in 1.759s

OK

$ ./joetoo-kwin -s
Broker registry status (snapshot; not remote connection health)
State: No reported Busy/uncertain flags
Managed windows: 4 (present=3, missing=1, uncertain=0)
Launch requests: 3 (pending=0, running=0, succeeded=3, failed=0, timeout=0, ambiguous=0)
Observation: synchronized; observed=9; revision=3538
Placement transaction: OK
Recovery: ready
Capabilities: managed_close=1, snapshot=1, viewer=1, initial_layout=1, single_raise=1

$ git diff --check
$ git status --short
 M libexec/joetoo_kwin_readonly.py
 M tests/test_step1_8_readonly_cli.py
```

The ellipsis above explicitly summarizes the other eight passing test lines; the run count, duration and concluding result are copied from the operator output. `git diff --check` emitted no diagnostics. This was the expected two-file working-tree diff **before** commit `f3fef58`.

## ShellCheck side effort and fixture-test follow-up

- Before the read-only change could be fully linted, `validate_scripts ./joetoo-kwin -l` using ShellCheck's source-following mode was reported to take about **28 seconds** and roughly **7 GB** of RAM. The maintainer developed/installed `shellcheck_stub_filter` in `dev-util/joetoolkit/devtools` (joetoolkit **1.0.19**) as a separate workflow improvement, not a new joetoo-kwin feature.
- `shellcheck_stub_filter ./` scanned **29 shell-shebang files** and retained **69 of 1,329** generated header-variable assignments, preserving the complete function stub; the generated `script_header_joetoo.shellcheck_filtered_stub` was added to the project and committed in `1670bea`. Generated stubs are excluded from subsequent input scans. The maintainer reported the `-l` validation subsequently passed in **9.000 seconds**, with no ShellCheck diagnostics. **Post-filter peak memory usage was not measured**, so no memory reduction is claimed.
- On slim2, the full Python suite later exposed an **obsolete Step 1.4d test expectation** that the now-implemented `-o` command should contain `not yet integrated`. The maintainer applied and committed a test-only repair on slim2 as **`cadf992`**, then fast-forwarded q552u01 from `f3fef58` to `cadf992` and verified a clean working tree with remote tracking.

The q552u01 post-sync fixture test output was:

```text
$ python3 -m unittest discover -s tests -p 'test_step1_4d_cli.py' -v
test_failed_launch_returns_failure_without_aborting_other_attempts (test_step1_4d_cli.TestMultiLaunchFixtureTests.test_failed_launch_returns_failure_without_aborting_other_attempts) ... ok
test_fixture_remains_separate_from_configured_open (test_step1_4d_cli.TestMultiLaunchFixtureTests.test_fixture_remains_separate_from_configured_open) ... ok
test_four_fixed_placements_and_separate_process_requests (test_step1_4d_cli.TestMultiLaunchFixtureTests.test_four_fixed_placements_and_separate_process_requests) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.006s

OK
```

## Assessment and unverified items

**Observed:** source-tree `-s` and `-i` on Wayland for present/missing records; corrected terminal-`OK` status; nine focused tests passing; later three repaired fixture tests passing; ShellCheck extended validation successful after stub filtering. **Not demonstrated here:** fresh whole-project Python rerun after `cadf992`, native Wayland one-shot `-L under`, installed (non-source-tree) CLI helper resolution, or final Step 1.8 acceptance. See the companion [slim2 X11 evidence](step1.8-slim2-readonly-x11-evidence-2026-11-22.md).
