# Step 1.5a focused review fixes — Iteration 3

Branch: `task/joetoo-kwin-step1.5-layout-ssh-workflows`.
HEAD remains `03b3ca493c067f18d434d078fd0c8789de80ca95`.
The existing review bundle is preserved as the pre-fix snapshot; its source
and handoff bytes matched the working files before this iteration.

The three findings are addressed:

- Ordinary planner tests now use `tests/fixtures/step1_5a_header.bash`, a small
  checked-in test double. They no longer extract a function from the installed
  header during setup. A portability regression reruns the ordinary suite with
  reads of the installed header blocked. Separate installed-header integration
  tests retain actual UI and verbosity coverage and skip explicitly when the
  header or required companion modules are absent. Both integration tests ran
  here; neither was skipped.
- Plan columns now measure each cell through the header's `get_msg_len` and
  grow to fit the longest value. Padding is plain spaces, then whole rows pass
  through `j_msg` with the existing severity/color policy. `pad` was inspected;
  it emits color resets, so plain space generation avoids resetting row color
  between cells. Long-target alignment is checked with the portable double and
  real installed header. Targets remain complete; very wide tables can still
  wrap in a narrow terminal.
- The message now says the planner launches no applications and explicitly says
  sourced trusted Bash configuration may have side effects. A regression uses
  a disposable config marker to verify that distinction while retaining the
  forbidden GUI/D-Bus/transport-operation spies.

Only `print_plan` changed in the planner. Its entire geometry/defaults/validation
prefix and the CLI were byte-compared against the prior bundle and remain
unchanged. No Step 1.5b–1.5d functionality was added.

Final validation:

| Check | Actual result | Evidence |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -v` | 165 passed, no skips; includes 18 ordinary planner tests, 1 portability check and 2 installed-header tests | [Python log](step1.5a-iteration3-python-tests.log) |
| `node --test tests/*.js` | Both test files passed | [Node log](step1.5a-iteration3-node-tests.log) |
| `bash -n` on CLI, planner, new shell fixture and example config | Passed | [Syntax log](step1.5a-iteration3-syntax.log) |
| `shellcheck -x` on CLI, planner and new shell fixture | Passed, no diagnostics | [ShellCheck log](step1.5a-iteration3-shellcheck.log) (empty) |
| Whitespace and scope review | Passed; new untracked implementation/test files explicitly included in complete diff | Review patches below |

The first lint pass identified two unnecessary dollar signs in new arithmetic
array indices; these were corrected and lint, syntax and Python regression were
rerun successfully. Prior validation logs and the previous bundle remain intact.
Native X11/Wayland behavior was not tested in this iteration.

Review artifacts:

- [Focused changes against the prior review bundle](step1.5a-iteration3-fixes.patch).
- [Complete candidate diff against HEAD, including new files](step1.5a-iteration3-complete.patch).

The complete patch includes the CLI, planner, Python tests, new shell fixture,
example configuration, handoff, review records and validation logs. Historical
patch/bundle artifacts are preserved separately rather than embedded again.
Both patches omit the Kate swap, maintainer historical output and unrelated
files. Only the agent-owned handoff section is updated. Nothing was staged,
committed, pushed or deployed; protected repositories were not altered.
Next actor: maintainer review at the existing publication boundary.
