# Step 1.5a review bundle inventory

Archive: `joetoo-kwin-step1.5a-review-bundle.zip`. Paths inside the archive are relative to the
joetoo-kwin project root, preserving the implementation directory layout.

Branch: `task/joetoo-kwin-step1.5-layout-ssh-workflows`. HEAD: `03b3ca493c067f18d434d078fd0c8789de80ca95`.
This is a working-tree review snapshot, not a commit or deployment package.

| Path | Classification / contents |
| --- | --- |
| `joetoo-kwin` | Modified tracked implementation |
| `libexec/joetoo-kwin-plan-functions` | New untracked implementation |
| `tests/test_step1_5a_plan.py` | New untracked tests |
| `task_step1.5/step1.5a-example.conf` | New untracked example configuration |
| `task_step1.5/HANDOFF.md` | Modified tracked handoff; Iterations 1 and 2 preserved |
| `task_step1.5/step1.5a-review.md` | New untracked review report |
| `task_step1.5/step1.5a-review.patch` | New untracked complete candidate patch |
| `task_step1.5/step1.5a-python-tests.log` | Validation evidence: 161 passing tests, including 17 new tests |
| `task_step1.5/step1.5a-node-tests.log` | Validation evidence: 2 passing Node test files |
| `task_step1.5/step1.5a-shellcheck.log` | Validation evidence: intentionally empty; no ShellCheck diagnostics |

Additional package metadata: this inventory and `SHA256SUMS`, which checksums
all payload files plus this inventory. The archive checksum is supplied in a
separate `.zip.sha256` sidecar.

## Completeness and verification

Both new untracked implementation/test files were explicitly included and
checked against `git ls-files --others --exclude-standard`. The existing review
patch was reconstructed in memory from tracked diffs and explicit new-file
diffs, and exactly matched the packaged working copies. Ordinary `git diff`
alone would omit the new planner, tests and support files.

Archive verification checks the exact entry list, ZIP integrity, byte-for-byte
agreement with working files, and SHA-256 hashes. No implementation changes,
staging, commits, pushes, deployments, or new test runs were performed while
packaging. Validation logs record the preceding implementation iteration;
Bash syntax and whitespace checks are recorded in the review report.

The review snapshot requires the accepted baseline and installed joetoo header
to rerun the complete tests; unchanged baseline files and system dependencies
are deliberately outside this review bundle.

## Excluded temporary, historical and unrelated artifacts

- `task_step1.5/.HANDOFF.md.kate-swp`: maintainer-owned Kate swap file.
- `task_step1.5/codex_step1.5_first_run_output`: maintainer-owned historical output.
- Python caches, Git metadata, unrelated project files, prior proposals and
  legacy reference configurations: omitted.
- No staging directories or transient build files are included. The review
  patch and validation logs are intentional review evidence, not scratch files.
- No environment dumps, credentials or private logs were collected. Selected
  contents were checked for credential signatures; existing project context
  in the requested handoff is retained verbatim.
