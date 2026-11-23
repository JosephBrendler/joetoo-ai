# Step 1.8 — PR #36 merge closure and Step 1.9 transition

**Date:** 2026-11-23. **Operator:** maintainer on `gmki91`, with supporting
X11/Wayland evidence from `gmki91`, `q552u01`, and `slim2`.
**Repository:** `JosephBrendler/joetoo-ai`.

## Maintainer-reported Git and acceptance results

- The maintainer reviewed and accepted the implemented Version 1 CLI focus
  behavior and its explicit limitation, prepared and reviewed
  [PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36), and merged it
  using `gh pr merge 36 --merge --delete-branch`.
- The feature branch was `task/joetoo-kwin-step1.8-cli-completion`;
  its reviewed head was `9ce80d5` before Git ancestry reconciliation.
  `git merge --no-commit --no-ff origin/main` initially conflicted only in
  `ARCHITECTURE.md`. The maintainer resolved five conflict blocks, preserving
  Step 1.8's current contract and compatible automatic Step 1.9 documentation
  merges. Conflict resolution was committed and pushed as `fe60d46`.
- GitHub recomputed the pull request as clean/mergeable. The final merge
  created **`main` `67c054c`**. The PR feature branch was deleted locally
  and remotely; the maintainer subsequently fast-forwarded and pruned
  `gmki91`, `q552u01`, and `slim2` to that commit.
- The archive move was committed separately on the follow-on documentation
  branch `task/joetoo-kwin-step1.8-archive-step1.9-resume` at `48dc17a`;
  this closure record and related documentation reconcile the moved evidence
  with the active Step 1.9 dispatcher.

**Acceptance interpretation:** The maintainer approved the final focus-policy
choices and voluntarily merged the reviewed PR. No separately worded
"I formally accept Step 1.8" utterance is assumed. The accepted/merged
status here follows those documented actions, not a claimed CI gate.

## Accepted implementation and evidence

- Read-only `-s` broker status, `-i MANAGED_ID` detail, and verified
  one-shot `-L ... under`, preserving `-L over` and the configured `-o`
  layout classifications; no `-L panel` or live geometry reflow.
- [q552u01 read-only Wayland](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md),
  [slim2 read-only X11](step1.8-slim2-readonly-x11-evidence-2026-11-22.md),
  [q552u01 native under/stacking](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md),
  and [gmki91 native X11](step1.8-gmki91-x11-native-validation-2026-11-22.md)
  contain machine-specific results and negative-to-corrected testing history.
- [November 23 q552u01 focus and closeout](step1.8-q552u01-focus-and-closeout-evidence-2026-11-23.md)
  documents the configured `-o` panel launch, verified temporary preferred
  focus, and eventual usable keyboard focus in the originating Konsole;
  [console transcript](step1.8-q552u01-acceptance-console-2026-11-23.txt)
  and [screenshot](screenshots/20261123-q552u01-wayland-panel-focus-override.png)
  are retained.
- Reported headless regression results: **1,113 Python PASS** and
  **180 JavaScript PASS** on q552u01, plus **54 focused POC-installer PASS**.
  No GitHub checks were reported on PR #36; these figures are the recorded
  human-run tests, **not** passing CI or installed-package validation.

## Explicitly accepted limits and next task

- Serialized Version 1 launch operations restore keyboard focus to the
  eligible originating control Konsole, even when initial layout temporarily
  activates a different preferred window. The maintainer accepts that an
  intervening deliberate activation may be overridden at mission completion.
  Any stronger user-activity or future parallel-launch policy is deferred to
  [Version 2](../../ARCHITECTURE.md#12-version-2-considerations).
- `-L panel`, live panel reflow, and broad cross-desktop user navigation
  remain outside Version 1. A one-shot successful placement does not prove
  remote endpoint/TLS/login usability. Development POC installer tests do
  not prove production `${ED}` completeness or installed-path resolution.
- **Step 1.8 is closed.** This directory is an archival evidence resource,
  not an active task dispatcher. The active work is
  [Step 1.9 source stabilization and Gentoo packaging](../../task_1.9/HANDOFF.md),
  retaining its human maintainability-comment review, curated staging,
  `tarup`, installed-image isolation, and native packaged-path QA gates.

**Source:** the maintainer's November 23 CLI outputs and the linked
native evidence. No code, service, effect, tarball or package operation was
performed as part of this documentation-only archive transition.
