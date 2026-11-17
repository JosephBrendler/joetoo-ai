# Step 1.6 — Managed operations HANDOFF

**Status (2026-11-16, late evening): The focused `-x` progressive clean-sweep correction is implemented as an **uncommitted ten-file Codex candidate** at local `HEAD f26027a0`; q552u01 maintainer-native testing reports **8 verified closes + 1 missing retirement, all 9 records retired, empty `-l` without broker restart**. No code blocker demonstrated. **Step 1.6 not yet finally accepted**: remaining safety/native X11 acceptance and publication are reserved.**

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
that work. The maintainer pushed the initial Step 1.6 candidate with corrected
KWin plugin packaging and collected the first q552u01 native close evidence.
A later **locally modified, uncommitted** ten-file correction (Codex) implements
the approved progressive `-x` semantics. After deploying the corrected user
broker, the maintainer collected further native success evidence. See
[original evidence](step1.6-native-wayland-evidence-2026-11-16.md) and
[progressive-sweep review/native addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
The earlier evidence is retained unchanged; implementation and native results
in the addendum supersede its old `-x` status. Neither constitutes an automatic
publication or final milestone acceptance.

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

**The reviewed, locally uncommitted candidate now implements this distinction.**
The q552u01 positive-path test passed with nine total retirements and empty
`-l` without restart. No further `-x` implementation work is justified by
that result. See [addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md),
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

- **q552u01:** Maintainer-native KWin Wayland/XWayland tests performed 2026-11-16; remaining cases pending.
- **slim2:** Subsequent native X11 testing.
- **gmki91:** Additional X11 development and testing when available.

Host assignments do not themselves authorize native test execution, service changes or destructive operations.

## 7. Next actor and authorization

**Next actor: maintainer (native acceptance and disposition of the local diff).**
The bounded `-x` correction is implemented, headless validated and positively
exercised on q552u01. The ten changed source/test/documentation files remain
**uncommitted/unstaged** at local `HEAD f26027a0` according to Codex. Its fetch
failed because `.git/FETCH_HEAD` was read-only; the tested local patch and
source were supplied for review. **No additional Codex coding round is needed
without a demonstrated defect.**

**First next action:** finish only the remaining maintainer-native checks:
q552u01 declined `-x`/no effects, status query after CLI exit, direct-client
refusal/known-safe partial cleanup, disposable self-terminal/CLI-loss and
independent worker/SSH cleanup as feasible; then slim2 native X11 XCB
fence/unsupported-protocol/reused-XID tests (optional gmki91 coverage).
See [addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md)
for what already passed versus what is still unverified.

**After that:** record the final acceptance decision and decide whether to
publish the reviewed local candidate (commit/push/PR) at a separate maintainer
publication gate. Do not create another stage or dispatch Codex to repeat
successful tests. A [conditional defect-only Codex prompt](DRAFT_Codex-Step1.6-conditional-native-defect-fix.md)
is prepared **only if** a reproducible blocking fault is found. No native
host/service operation, repo publication, or protected-repo mutation is
authorized by this handoff.

## 8. Recent decisions

- No `-a` requirement; `-L` already launches a new managed window. Older
  archived `-a` references are historical only.
- **2026-11-16 maintainer clarification:** `-x` is a destructive *managed
  collection sweep*, not simply repeated `-d`; confirmed safe removals occur
  progressively. `-d` retains registrations; `-D` is deferred to version 2.

## 9. Latest candidate result

**Corrected `-x` native positive-path PASS on q552u01 (2026-11-16):**
Maintainer ran `./tools/restart_joetoo-kwind t`, updated the 12 user-owned
broker files, restarted the OpenRC user service, then ran the local full
regression: **1,016 Python tests OK**, **163 JavaScript PASS** and installer
check PASS. Three configured plans launched 5/5 + 2/2 + 2/2 managed windows.
A confirmed `-x` processed **nine** managed registrations: one preexisting
missing entry (`retire_missing`, `already_missing`) and **eight native verified
closes** (seven Wayland, one local XWayland); **all nine** returned
`retired=true`. Transaction `a5ac9323bd95406290e0ac5fe666b433` returned
`state=succeeded`, no exclusions, both retention flags `false` and
`./joetoo-kwin -l` immediately returned
`No managed windows (no retained managed reservations).` **No broker restart
was needed during/after that sweep.**

**Codex headless correction review:** focused 107 tests (106 PASS, 1 sandbox
SO_PASSCRED SKIP); full 1,016 (1,015 PASS, 1 SKIP); 163 JS PASS; syntax,
ShellCheck, AST and whitespace PASS. Ten modified tracked files (+374/−33
per Codex), no new native plugin/XCB/RDP/VNC code. The additional q552u01
regression was unconfined and printed `Ran 1016 tests ... OK` (no skip shown).
An intermediate help-test fixture failure was corrected before final green
runs; failed `git fetch` on read-only `FETCH_HEAD` was a source-sync limitation.

**Not yet demonstrated natively:** directly managed client refusal,
known-safe partial failure, helper/source uncertainty, self-terminal/CLI-loss,
remote worker/SSH/tmux cleanup and the separate native X11 compositor.
The unchanged earlier evidence covers selective `-d` and the old bulk
retention behavior. Details:
[2026-11-16 progressive addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md)
and [original native evidence](step1.6-native-wayland-evidence-2026-11-16.md).

## 10. Next decision

**No new coding task is indicated by the successful sweep.** Complete/record
the limited remaining native acceptance, then decide whether to accept Step 1.6
and authorize publication of the locally modified candidate. If a **specific
reproducible defect** blocks acceptance, first capture its exact failing
native/result evidence and then, if needed, authorize only the smallest
conditional Codex fix. No speculative redesign or extra implementation stage.

Historical evidence and earlier draft instructions must not override this HANDOFF or subsequent explicit maintainer decisions.
