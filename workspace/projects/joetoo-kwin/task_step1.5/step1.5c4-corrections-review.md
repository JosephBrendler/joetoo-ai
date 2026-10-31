# Step 1.5c.4 native-review corrections

Branch task/joetoo-kwin-step1.5c4-graphical-launch; clean starting HEAD
35d1b072b763df8126c602d9840c0ad243a9a656. No fetch/branch changes.
Latest task authorizes this bounded correction; applicable instructions, scope,
HANDOFF, AAR demonstration and installed handle_result implementation inspected.

A: Relative Dolphin local paths now resolve beneath HOME, independent of config
location. Empty HOME and absolute semantics, canonicalization, directory validation
and literal argv behavior remain. Unit/integration cases use configs outside HOME.

B: plan_stage uses the existing AAR form for actions with output: closed announcement,
validator/calculation in the calling shell, captured original status, fresh result
announcement, report_action. Errors appear once on their own line; no subshell loses
planner assignments and no low-level exit/die was introduced. An installed-header
regression verifies status 2, diagnostic separation and the failed result line.

C: Capacity text explicitly reports adequate existing capacity or the exact missing
count after confirmation. Provisioning/rechecks/confirmation remain unchanged.

D: Existing lock tests already cover competition/cancellation and Konsole descendants.
Added only the missing Dolphin-specific case to the current graphical harness: completed
managed Dolphin remains alive without FD 9, and another -o reaches confirmation.
No production lock changes or concurrency framework was added.

Validation: 258 Python tests PASS, no skips (installed-header coverage retained);
3 Node test files PASS; Bash syntax, Python compile, ShellCheck, git diff --check PASS.
Commands: python3 -m unittest discover -s tests -p 'test_*.py';
node --test tests/test_*.js; bash -n on CLI/launch helper; shellcheck -x on CLI/launch
helper; Python compile of resource helper; git diff --check.
Logs: step1.5c4-corrections-{python,node,syntax,shellcheck}.log.
No native operations or publication. All new tests are headless with mocked broker
and executable interfaces; background test sleep processes are explicitly terminated.

Modified tracked files:
- joetoo-kwin
- libexec/joetoo-kwin-launch-functions
- libexec/joetoo_kwin_launch_resources.py
- tests/test_step1_5a_plan.py
- tests/test_step1_5c4_launch.py
- tests/test_step1_5c4_resources.py
- task_step1.5/step1.5c4-review.md
- task_step1.5/step1.5c4-native-acceptance.md
- task_step1.5/HANDOFF.md (Codex Section 5 only)

New files under task_step1.5: this review, step1.5c4-layer-proposal.md,
four corrections logs, and step1.5c4-corrections.patch. No new production helper.
Old patches remain historical and are not regenerated to rewrite prior evidence.
Temporary inspection files under /tmp are excluded from the review diff.

Native summary is attributed to the maintainer; screenshots/raw logs from the separate
ChatGPT conversation were not retrieved or fabricated. Revised HOME-relative paths and
reporting need narrow maintainer checks listed in the acceptance record. No further
native concurrency test is required for this increment. Layer proposal and all future
broker/resident work need a separate decision; no executable layer change occurred.
Maintainer review next; commit/push/PR/merge/deployment remain separately gated.
