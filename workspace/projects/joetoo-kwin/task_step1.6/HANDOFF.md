# Step 1.6 — Managed operations HANDOFF

**Current status (2026-11-18):** Implementation and core native positive-path
acceptance have passed on **q552u01 Wayland/XWayland** and **slim2 X11**.
On slim2, confirmed `-x` retired **2 already-missing + 14 native X11
verified-closed records (16/16)**; immediate `-l` was empty without a broker
restart and the entire retained result remained queryable after CLI exit.
Selective `-d`, declined `-d`/`-x`, and real Konsole refusal/timeout behavior
were also observed. **No reproducible coding blocker is established.**

**Next actor:** maintainer, for review of evidence/remaining explicit safety
coverage limitations, acceptance disposition, q552u01 fast-forward and
publication review. The current remote task branch is **`c57ab8c`**;
q552u01 is still at `8849e59` with no upstream configured (maintainer report).
This cloud-authored evidence/documentation update is a reviewable **draft**,
not committed/pushed; no new Codex implementation task is indicated.
See [slim2 native evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md),
[2026-11-16 progressive Wayland/XWayland evidence](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md),
and [task index](README.md).

## 1. Task identity and authority

**Repository:** `JosephBrendler/joetoo-ai`\
**Project:** `workspace/projects/joetoo-kwin/`\
**Implementation branch:** `task/joetoo-kwin-step1.6-managed-close`\
**Reviewed base:** `cdcdc9e8c842d0be04447c06b90a25d3cc59f107` (PR #31 merged)\
**Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)\
**Task index:** [README.md](README.md)

Step 1.6 is the active development milestone. This HANDOFF records the current assignment and authorization boundaries; it does not independently grant permission. Neither the architecture roadmap nor historical task instructions authorize implementation, native operations or publication.

## 2. Accepted predecessor

Step 1.5 is complete.

- Step 1.5c.5d accepted and merged through [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29) at `3e9c4bf311bc65b32d332a00d3b50163a9043303`.
- Step 1.5d accepted and merged through [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30) at `f72407278fa0a9c923079f3b38ce834440d2fef2`.
- Accepted behavior includes configured managed launches, exact-UUID registration and placement, remote access integration, single-window `-L` launch, read-only `-l` inventory, and verified one-shot raising of newly launched managed windows.
- Final XCB test-fixture correction and regression evidence are preserved in the [native acceptance record](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md) and [fixture addendum](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md): 7 focused Python, 1,000/1,000 stress repetitions, 100 additional leak-check repetitions, 949 full Python and 163 JavaScript passes. These recorded results were not rerun during this documentation task; the original 948/949 result and eleven passing reruns remain intact.

Historical records: [archived Step 1.5 README](../archive/task_step1.5/README.md) and [closed HANDOFF](../archive/task_step1.5/HANDOFF.md).

These completed milestones are accepted foundations, not outstanding work.

## 3. Documentation transition (completed)

PR #31 merged the archive/init transition at `cdcdc9e`; the
[initial historical HANDOFF](step1.6_initial_historical_HANDOFF.md) preserves
that transition. The corrected broker-owned progressive `-x` implementation is
now committed on the task branch; GitHub compared `8849e59..c57ab8c` and
found one subsequent commit, affecting only
`tools/restart_joetoo-kwind` (TMPDIR handling). The older statement that the
correction was an uncommitted ten-file working tree is **historical**.

The [original Wayland evidence](step1.6-native-wayland-evidence-2026-11-16.md),
[progressive-sweep addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md),
and [slim2 X11 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md)
are complementary, not competing, evidence records. None alone grants
publication or acceptance authority.

## 4. Step 1.6 objective

- `-d MANAGED_ID`: positively authenticated graceful close of **one** managed
  window; **retain** registration, desktop/slot reservation and history.
- `-x`: broker-owned **progressive clean sweep** of the fixed snapshot after
  one confirmation. Retire each *already-missing* record/reservation as
  encountered and each eligible present record/reservation **immediately after
  verified graceful closure**. Do not wait for every other target before
  retiring independently verified entries. Flag individual failures and retain
  only minimal safety-critical unresolved state; continue other work whenever
  native dispatch can be performed safely. Full success leaves `-l` empty
  without broker restart.

Preserve exact UUID/owner proof, one confirmation, truthful bounded results
surviving CLI exit, isolated unrelated windows and graceful-only behavior.
A genuinely uncertain helper/owner/source is **not** proof of closure and may
block unsafe *native dispatch*, but must not roll back earlier verified cleanup.
Never force-kill, close by title/class/PID alone, or erase uncertain ownership.
`-D` individual close-and-retire is version 2; no `-a`, `-S`, `-r`, restore,
new native subsystem or general checkpoint/recovery in Step 1.6.

**The committed task-branch candidate implements this distinction.**
The q552u01 native Wayland/XWayland sweep passed with nine total
retirements; the later slim2 native X11 sweep passed with 16 total retirements.
No further `-x` implementation work is justified by those results. See [addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md),
[unchanged original evidence](step1.6-native-wayland-evidence-2026-11-16.md)
and [updated native adapter contract](../native/managed-close/README.md).
The prior [implementation Codex prompt](DRAFT_Codex-Step1.6-x-progressive-sweep.md)
is completed history, **not a live task**.

## 5. Invariants and exclusions

Preserve source/owner/exact-UUID validation, the fixed authenticated snapshot,
existing broker serialization, and protection of unrelated windows. `-d`
retains missing reservations; **confirmed `-x` retires them progressively**.
No registration/slot mutation before explicit confirmation; no implied
rollback or forced process termination. Keep application, placement, RDP/VNC
connection and broker lifetime outcomes separate.

Step 1.7 checkpoint/reconciliation, Step 1.8 snapshots/restore and Step 1.9
packaging remain out of scope. `-x` must not erase a future last-good snapshot.

## 6. Development and native testing hosts

- **q552u01:** Maintainer-native Wayland/XWayland full positive-path and
  regression checks passed 2026-11-16; local branch at `8849e59`, not yet
  tracking origin and one commit behind the remote task branch as of 2026-11-18.
- **slim2:** Maintainer-native `kwin_x11` 6.7.6 effect build/install/owner
  checks, 1,016 Python + 163 JavaScript pass, 15 configured launches, two
  retained selective closes, confirmed 16-record clean sweep, declined closes,
  and real Konsole refusal/timeout checks on 2026-11-17–18.
- **gmki91:** Additional X11 host if a specific defect or justified coverage
  need arises; not a standing prerequisite.

Host assignments do not independently authorize native operations or
publication. See [slim2 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md).

## 7. Next actor and authorization

**Next actor: maintainer — acceptance and publication review.** No new
implementation task is dispatched. The implementation is committed/pushed on
`origin/task/joetoo-kwin-step1.6-managed-close` at `c57ab8c`; the present
cloud documentation/evidence draft is **not** yet applied, committed or pushed.

**Shortest path:**
1. On `q552u01`, check the worktree; if clean, `git fetch origin`,
   fast-forward the task branch from `8849e59` to `c57ab8c` and set its
   upstream. Do not rebase or overwrite maintainer changes.
2. Review/apply the documentation-only evidence/HANDOFF/README diff; inspect
   `git diff --check` and the diff. Keep screenshots/logs optional as separate
   attachments rather than adding unrelated assets to the source tree.
3. Decide whether the recorded headless XCB safety proofs plus native X11
   positive/refusal tests meet acceptance, **or** whether a narrow live
   unsupported-`WM_DELETE_WINDOW`/stale-XID fixture is non-waivable under the
   accepted native adapter checklist. Record the decision explicitly; unrun
   cases are not passed cases. Mid-transaction self-terminal loss and remote
   SSH/RDP/VNC worker cleanup are likewise evidence limitations, not observed
   code defects.
4. If accepted, approve publication/PR and integration separately under the
   standing workflow. No further Codex round without a reproducible defect.

Step 1.7–1.9 and version-2 `-D` remain out of scope. No native host/service
operation or protected-repository mutation is authorized by this handoff.

## 8. Recent decisions

- No `-a` requirement; `-L` already launches a new managed window. Older
  archived `-a` references are historical only.
- **2026-11-16 maintainer clarification:** `-x` is a destructive *managed
  collection sweep*, not simply repeated `-d`; confirmed safe removals occur
  progressively. `-d` retains registrations; `-D` is deferred to version 2.

## 9. Latest candidate result

**Published task branch:** `c57ab8c` (one commit ahead of `8849e59`, only
restart helper TMPDIR change in that last commit); previous uncommitted Codex
candidate status is superseded. The later documentation draft remains
unpublished until reviewed/applied.

**q552u01 2026-11-16:** 1,016 Python OK, 163 JavaScript PASS; confirmed
Wayland/XWayland `-x` closed eight native windows and retired one missing
registration (9/9), empty inventory without broker restart. Details in the
[progressive addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).

**slim2 2026-11-17–18:** 1,016 Python OK and 163 JavaScript PASS after using
an executable test temporary filesystem (`/tmp` is `noexec`); native KWin X11
6.7.6 effect loaded with matching authenticated owner; 15/15 configured
Konsole launches; two successful `-d` closures retained missing records;
confirmed mixed `-x` retired **16/16** (2 already missing, 14 native X11
verified closed), empty `-l` **without restart**; independent
`ManagedCloseStatus(0073db0a81794860bda46995edb4ce26)` returned the
full successful history. New ID `win-017` reoccupied an available slot;
declined `-d` and `-x` left it present. Managed Konsoles `win-018` and
`win-019` displayed real close-confirmation dialogs and timed out rather
than being killed; each `-d` retained its reservation and accurately reported
`partial/not_closed_timeout`. Their `self_terminal` fields identified the
invoking managed Konsole. Details, exact IDs and qualifications:
[slim2 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md).

**No demonstrated blocker:** All principal implemented semantics passed.
Live unsupported-X11-protocol/XID-reuse race, frontend disappearance *during*
a still-running sweep and independently verified remote-worker cleanup remain
unproven natively; the helper and broker refusal/partial/identity rules have
focused headless coverage. These are evidence/acceptance disposition items,
not observed regressions. A missing registration seen after `-d` is correct
retention behavior, **not** a failed `-x` sweep.

## 10. Next decision

**Recommendation:** ready for maintainer acceptance review now, with no new
implementation stage or coding task. Make one explicit call on whether the
remaining live X11 fence edge tests in the native adapter checklist are
required before formal acceptance; if not, record the bounded evidence gaps
and accept. Synchronize q552u01 and review/publish the focused documentation
update. A reproducible safety failure, not mere absence of optional coverage,
is the condition for a further defect-only Codex assignment.
