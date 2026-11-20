# Step 1.7 — formal maintainer acceptance and evidence synchronization

> **Post-acceptance publication (2026-11-19):** The previously accepted Step
> 1.7 was subsequently merged into `main` by
> [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33) at `df118da`.
> The local and remote task branches were deleted. See the
> [separate merge record](step1.7-pr33-merge-closure-2026-11-19.md).
> The chronological pre-merge statements below describe the time of acceptance.

**Decision date:** 2026-11-19. **Decision maker:** project maintainer.
**Decision:** **Step 1.7 formally accepted.** The former Step 1.8 durable
layout work is included in the accepted combined Step 1.7 milestone. This is
an acceptance decision, **not** a statement that the branch has merged.

## Accepted implementation and supporting evidence

- Repository/project: `JosephBrendler/joetoo-ai`,
  `workspace/projects/joetoo-kwin/`.
- Task branch: `task/joetoo-kwin-step1.7-recovery-snapshot`.
- Implementation under test: `33bbbee03a5effbf1c4c31b5600254ab28374510`.
- Evidence/documentation synchronization shown by the maintainer:
  `33bbbee..2985113` fast-forward on `q552u01` on 2026-11-19. This earlier
  evidence commit did **not** itself record the acceptance decision; the
  present document records the subsequent explicit decision.
- [Native Wayland evidence on q552u01](step1.7-q552u01-native-evidence-2026-11-19.md),
  with complete native/headless transcripts linked therein.
- [Native X11 evidence on slim2](step1.7-slim2-native-x11-evidence-2026-11-19.md),
  with the complete launch/recovery/restore transcripts linked therein.

The accepted evidence demonstrates authenticated same-KWin-session broker
reconciliation (including original managed IDs, exact UUIDs and retained
missing observations), `-S` complete-snapshot selection and fail-closed
last-good preservation, timestamped protocol-2 history/retention and legacy
migration, and confirmed `-r` fresh-instance launches on both backends.
`-d`/`-x` close/retire behavior and duplicate-slot safety were exercised.
Headless validation on `q552u01` reported 79 focused Python, 1080 full Python
and 163 JavaScript passing checks; four scripts passed individually. The
combined ShellCheck invocation was interrupted with `Killed`, so no combined
pass is claimed.

## Maintainer-supplied q552u01 Git output

The following is the terminal output supplied by the maintainer immediately
before the explicit acceptance decision. The `...` prefixes in the file list
were printed by Git's abbreviated diffstat; they are not elisions made in this
record.

```text
* task/joetoo-kwin-step1.7-recovery-snapshot 33bbbee [origin/task/joetoo-kwin-step1.7-recovery-snapshot] joetoo-kwin: Step 1.7 recovery and snapshot history candidate
joe@q552u01 ~/joetoo-ai/workspace/projects/joetoo-kwin $ git pull --ff-only
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 15 (delta 6), reused 15 (delta 6), pack-reused 0 (from 0)
Unpacking objects: 100% (15/15), 33.03 KiB | 751.00 KiB/s, done.
From github.com:JosephBrendler/joetoo-ai
   33bbbee..2985113  task/joetoo-kwin-step1.7-recovery-snapshot -> origin/task/joetoo-kwin-step1.7-recovery-snapshot
Updating 33bbbee..2985113
Fast-forward
 workspace/projects/joetoo-kwin/task_1.7/HANDOFF.md             | 160 +++---
 workspace/projects/joetoo-kwin/task_1.7/README.md              |  86 ++-
 ...ep1.7-q552u01-initial-native-focused-console-2026-11-19.txt | 123 +++++
 .../task_1.7/step1.7-q552u01-native-evidence-2026-11-19.md     | 152 ++++++
 .../step1.7-q552u01-refined-headless-console-2026-11-19.txt    | 195 +++++++
 .../step1.7-q552u01-refined-native-console-2026-11-19.txt      | 766 +++++++++++++++++++++++++++
 .../step1.7-slim2-initial-native-console-2026-11-19.txt        | 246 +++++++++
 .../task_1.7/step1.7-slim2-native-x11-evidence-2026-11-19.md   | 140 +++++
 .../step1.7-slim2-recovery-native-console-2026-11-19.txt       | 301 +++++++++++
 9 files changed, 2076 insertions(+), 93 deletions(-)
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-q552u01-initial-native-focused-console-2026-11-19.txt
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-q552u01-native-evidence-2026-11-19.md
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-q552u01-refined-headless-console-2026-11-19.txt
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-q552u01-refined-native-console-2026-11-19.txt
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-slim2-initial-native-console-2026-11-19.txt
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-slim2-native-x11-evidence-2026-11-19.md
 create mode 100644 workspace/projects/joetoo-kwin/task_1.7/step1.7-slim2-recovery-native-console-2026-11-19.txt
joe@q552u01 ~/joetoo-ai/workspace/projects/joetoo-kwin $
```

The output confirms an ordinary fast-forward of the **task branch** and the
presence of the nine evidence/documentation files on `q552u01`; it is not
proof of merge into `main`. No code or native-test outputs changed in this
pull, and no new native test is claimed from the pull itself.

## Acceptance qualifications and remaining work

The refined X11 console did not include a declined `-r` or a completed
native-effect D-Bus owner/method-introspection comparison, although confirmed
restore and verified native X11 close passed. The immediate OpenRC startup
probe occasionally preceded D-Bus registration, while a bounded readiness
check succeeded. These qualifications were disclosed before the maintainer's
formal acceptance. There is **no demonstrated unresolved Step 1.7 defect** in
the supplied evidence; acceptance does not convert untested paths into tests.
A reboot/new-KWin-session adoption check is outside the same-session recovery
contract and is not claimed.

**Next actions:** incorporate this acceptance record and the task
[README](README.md)/[HANDOFF](HANDOFF.md) update; review and reconcile stale
project-level README/ARCHITECTURE status language under explicit authorization;
review/create a Step 1.7 PR as appropriate; separately authorize and verify
merge to `main`; archive the completed task and proceed to maintainer-led
Step 1.9 packaging. No further native testing is required for this already
accepted Step 1.7 milestone unless the maintainer identifies a new defect.
