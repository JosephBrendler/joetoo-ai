# Step 1.7 — Recovery and last-good layout HANDOFF

**Current status (2026-11-19): Ready for maintainer acceptance decision;
NOT yet recorded as accepted or merged.** The combined Step 1.7 (including
former Step 1.8) candidate is implemented, committed and pushed to the existing
task branch. The maintainer completed substantive native validation on both
Wayland (`q552u01`) and X11 (`slim2`). No demonstrated Step 1.7 code defect
remains in the supplied test evidence. [Detailed disposition](README.md#native-validation-and-acceptance-review--2026-11-19).

## Source, scope and authority

- Repository/project: `JosephBrendler/joetoo-ai`, `workspace/projects/joetoo-kwin/`.
- Branch: `task/joetoo-kwin-step1.7-recovery-snapshot`.
- Candidate HEAD: `33bbbee03a5effbf1c4c31b5600254ab28374510`
  (`joetoo-kwin: Step 1.7 recovery and snapshot history candidate`), signed-off
  and signed by the maintainer, pushed from `q552u01`, fetched and verified
  identical on `slim2`. Starting baseline was `f18fea2`, after accepted Step 1.6
  [PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32).
- Governing instructions: repository root, `workspace/`, project `AGENTS.md`
  and [architecture §8](../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
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

## Maintainer-run evidence and assessment

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

## Next actor and concrete next steps

**Next actor: maintainer — explicit Step 1.7 acceptance decision.**

1. Review the two native evidence records and their complete logs. Decide
   whether the small untested X11 declined-restore branch needs another check
   or can be accepted under existing confirmation coverage. No additional
   implementation milestone or large test matrix is supported by these results.
2. If satisfied, **record maintainer acceptance** in task status/evidence and
   reconcile the stale Step 1.7 “not yet implemented” wording in project
   `README.md` and `ARCHITECTURE.md` with maintainer-approved wording. Those
   project-wide edits are *proposed*, not silently authorized here.
3. With separate maintainer publication authorization, create/review the Step
   1.7 PR and merge to `main`; verify final merge SHA and archive the task
   using normal project procedures. The pushed candidate commit is **not** a
   merge or acceptance by itself.
4. Step 1.9 packaging is the subsequent distinct, maintainer-led version 1
   milestone. Deferred Version 2 work and a full RDP/VNC rerun are not Step
   1.7 acceptance criteria.

**Operational reminder:** The X11 test ended after fresh `win-003`/`win-004`
were launched; no subsequent cleanup was shown. Only the maintainer should
close disposable test windows after deciding they are no longer needed.
