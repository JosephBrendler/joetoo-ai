# Step 1.7 — Recovery and last-good layout HANDOFF

> **Archive closure (2026-11-19): FORMALLY ACCEPTED AND MERGED into `main`**
> through [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33),
> merge commit `df118da`. The task branch was deleted locally/remotely;
> this HANDOFF is historical, **not an active task dispatcher**. The current
> task is [Step 1.9 packaging](../../task_1.9/HANDOFF.md). See the
> [merge closure evidence](step1.7-pr33-merge-closure-2026-11-19.md).

## Source, scope and authority

- Repository/project: `JosephBrendler/joetoo-ai`, `workspace/projects/joetoo-kwin/`.
- Historical branch: `task/joetoo-kwin-step1.7-recovery-snapshot` (deleted after merge).
- Integrated baseline: `main` at `df118da`, [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33).
- Accepted implementation commit: `33bbbee03a5effbf1c4c31b5600254ab28374510`
  (`joetoo-kwin: Step 1.7 recovery and snapshot history candidate`), signed-off
  and signed by the maintainer, tested on `q552u01` and `slim2`. Starting
  baseline was `f18fea2`, after accepted Step 1.6
  [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32).
- Evidence/documentation commit: `2985113`, fast-forwarded on `q552u01` from
  `33bbbee` by `git pull --ff-only`; the later PR #33 merge is separately
  evidenced in the [closure record](step1.7-pr33-merge-closure-2026-11-19.md).
- Governing instructions: repository root, `workspace/`, project `AGENTS.md`
  and [architecture §8](../../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
- This HANDOFF records work and decisions; it grants no further native,
  publication, merge, packaging or protected-repository authority.

## Delivered contract (one milestone; two distinct data/trust boundaries)

1. **Same-KWin-session checkpoint:** private atomic runtime checkpoint and
   authenticated reconciliation of existing exact managed UUIDs, desktop/slot
   reservations and diagnostic last-known observations. Broker restarts neither
   close nor relaunch applications; unproven or missing records remain
   non-destructive. Historical frames never confer fresh ownership or restore
   operator-adjusted geometry.
2. **Durable last-good snapshot:** `-S` saves complete authorized launch intent,
   not PIDs/UUIDs/credentials, as timestamped private history, with an atomic
   relative `last-session.conf` symlink, configurable pruning and legacy
   protocol-1 read/migration. Protocol 2 holds common settings once. `-r`
   validates the latest plan and, after the normal confirmation, launches
   **new** identities using the ordinary planner. `-d` and `-x` do not erase
   last-good. These responsibilities must not be conflated.

## Maintainer-run evidence and disposition

- [Formal acceptance decision and q552u01 fast-forward output](step1.7-maintainer-acceptance-2026-11-19.md):
  the maintainer explicitly accepted Step 1.7 on 2026-11-19. Evidence was
  already published at task-branch commit `2985113`; acceptance itself is
  recorded in the present documentation update, not retroactively attributed
  to that earlier commit.
- [q552u01 Wayland native evidence](step1.7-q552u01-native-evidence-2026-11-19.md):
  incomplete save refused; legacy regular-file migration byte-for-byte;
  timestamp collisions avoided; history pruning and modes; protocol 2;
  occupied-slot refusal; missing-record full observation survived broker-only
  restart with `diff` result 0; symlink/history unchanged after failed save.
- [slim2 X11 native evidence](step1.7-slim2-native-x11-evidence-2026-11-19.md):
  two-window launch; broker-only restart preserved exact IDs/UUIDs and same KWin
  owner; X11 verified close; missing record and observation survived restart;
  failed save preserved latest; `-x` retired; `-r` launched two new instances.
- [q552u01 refined headless transcript](step1.7-q552u01-refined-headless-console-2026-11-19.txt):
  79 focused Python PASS, 1080 full Python PASS, 163 JavaScript PASS. One
  combined ShellCheck invocation was `Killed`; all four files subsequently
  passed individual `validate_scripts` checks. Original console logs are
  linked from each evidence record. These are **operator-run**, not agent-run.
- X11 `-r` **decline** was not demonstrated in the refined X11 transcript;
  confirmed `-r` passed, and the previous Wayland candidate's declined flow
  was maintainer-reported. Native-effect introspection/owner equality was not
  independently completed in this X11 run, although exact verified X11 close
  passed. Neither is a demonstrated defect or necessarily a blocking retest.
- An immediate post-OpenRC-start introspection sometimes preceded D-Bus
  registration; bounded polling subsequently showed `recovery: ready` and
  synchronized inventory. It is a startup-readiness/diagnostic UX observation,
  not a proven recovery failure and not a reason to reset checkpoints.

## Closure and next task

**Step 1.7 has no remaining implementation, test, acceptance or merge gate.**
The maintainer accepted its documented X11/Wayland coverage qualifications.
PR #33 was merged, the remote/local task branch deleted and `q552u01` updated
to `main` at `df118da`; see the [merge record](step1.7-pr33-merge-closure-2026-11-19.md).

**Next actor: maintainer**, to review the documentation-only archive/kickoff
transition and authorize the separate [Step 1.9 packaging task](../../task_1.9/HANDOFF.md).
The version 1 packaging work is not an extension of Step 1.7, and neither
Version 2 features nor a full RDP/VNC retest are closure prerequisites.

**Operational reminder:** The X11 test ended after fresh `win-003`/`win-004`
were launched; no subsequent cleanup was shown. Only the maintainer should
close disposable test windows after deciding they are no longer needed.
