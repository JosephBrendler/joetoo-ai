# Step 1.5a candidate review

Baseline: `03b3ca493c067f18d434d078fd0c8789de80ca95`, branch
`task/joetoo-kwin-step1.5-layout-ssh-workflows`. The maintainer completed
and verified the fetch; this iteration did not fetch again.

The client implements `-c [-f CONFIG]`, grouped/repeated `-v`/`-q`, and
conflicting-option rejection. Defaults precede trusted Bash config, followed
by CLI verbosity adjustments through the installed header helper. Other
operations retain their existing paths. Effective geometry settings use the
header's `varlist`/`show_config`, followed by a colorized dry-run plan.

`libexec/joetoo-kwin-plan-functions` adapts the archived planner into a shared
terminal geometry function and ordered plan arrays. The default 87% total
width includes gutters; graphical entries do not consume terminal positions.
Four terminals use two rows within the configured height budget, separated
by a configurable row gutter. All offsets and proportions have named defaults.
Configured dimensions are mandatory and explicitly labeled, with no display
autodetection. Graphical underlay geometry remains labeled proposed; this
candidate does not establish stacking or focus behavior.

Configuration records remain `desktop|program-basename|mode|target` using the
archived `ssh`, `swr`, `via-ssh`, `local`, and `direct` vocabulary. No target is
contacted and no executable availability is required to produce a plan. The
configuration is executable trusted Bash, not a sandbox; dry-run guarantees
cover client/planner operations, not arbitrary commands placed in a config.
The default selection is `/etc/joetoo-kwin/joetoo-kwin.conf`. A review-only
example is [step1.5a-example.conf](step1.5a-example.conf).

Validation performed:

- `python3 -m unittest discover -s tests -v`: **161 passed**, including 17 new
  tests, installed-header smoke coverage, invalid inputs, precedence, geometry,
  move-argument preservation and forbidden GUI/D-Bus/SSH-operation spies.
  Output: [step1.5a-python-tests.log](step1.5a-python-tests.log).
- `node --test tests/*.js`: **2 test files passed**.
  Output: [step1.5a-node-tests.log](step1.5a-node-tests.log).
- `bash -n` on the client, helper and example: passed.
- `shellcheck -x` on client/helper: passed with no diagnostics. The initial
  lint identified intentional delayed expansion, dynamic config sourcing and
  caller-provided globals; the final source uses the skill's escaped macro
  form and documented source/global annotations.
- `git diff --check`: passed.

Only authorized CLI, new helper, tests, task artifacts and the agent-owned
handoff section changed. Iteration 1 and both preexisting maintainer artifacts
were preserved. No commits, pushes, deployment or protected-repository writes.

Next actor: maintainer review at the publication boundary. The complete review
patch is [step1.5a-review.patch](step1.5a-review.patch), including new files and
evidence except the patch itself. Native X11/Wayland geometry/underlay checks,
interactive `-m l/r` and preserve-size work, confirmation before `-o`, managed
launch and SSH-placeholder integration remain later tranches. Candidate helper
lookup is project-relative; installed helper placement belongs to later packaging.
No architecture requirements were edited or newly treated as approved.
