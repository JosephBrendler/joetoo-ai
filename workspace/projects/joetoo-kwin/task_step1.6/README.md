# Step 1.6 — Task index

**Current result (2026-11-18):** Core Step 1.6 is **ready for maintainer
acceptance review**: q552u01 Wayland/XWayland 9/9 clean sweep, slim2 X11 16/16
mixed retirements, retained post-CLI result, native declined confirmation,
Konsole refusal/timeouts, and clean 1,016 Python / 163 JavaScript regression.
There is **no demonstrated coding blocker**. The live X11 unsupported
`WM_DELETE_WINDOW`/stale-XID fence and some independent lifecycle tests have
headless coverage but not full live-fixture proof; acceptance/risk disposition
is reserved to the maintainer. Remote branch is `c57ab8c`; q552u01 still
reports `8849e59` and no upstream tracking. See the
[latest X11 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md) and
[active HANDOFF](HANDOFF.md). Historical uncommitted-candidate descriptions
below describe the earlier 2026-11-16 state.

## Current task and design

- [slim2 native X11 acceptance and refusal evidence (2026-11-17–18)](step1.6-slim2-native-x11-evidence-2026-11-18.md)
  — exact 16-target sweep, retained history, declined operations, live Konsole
  refusal, test-environment findings and remaining coverage limitations.
- [Corrected `-x` implementation review and native addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md)
  — ten-file diff assessment, headless/maintainer regressions, exact nine-target
  native result, limitations and shortest next acceptance actions.
- [Earlier native evidence (2026-11-16)](step1.6-native-wayland-evidence-2026-11-16.md)
  — original selective `-d`/old bulk-retention evidence, retained as history.
- [Completed `-x` Codex prompt](DRAFT_Codex-Step1.6-x-progressive-sweep.md)
  — historical implementation request, **not** a pending assignment.
- [Conditional, defect-only Codex draft](DRAFT_Codex-Step1.6-conditional-native-defect-fix.md)
  — use only if later native tests produce a concrete blocker; no automatic dispatch.
- [Native adapter contract and acceptance matrix](../native/managed-close/README.md)
  — Codex's focused source edit aligns the `-x` semantics in the local candidate;
  no native effect/XCB changes.
- [Active HANDOFF](HANDOFF.md) — current authority, transition validation,
  development/test hosts and next actor.
- [Project architecture](../ARCHITECTURE.md) — intended managed operations
  and existing ownership/safety requirements.
- [Project status](../README.md) — accepted capabilities and milestone overview.
- [Initial historical HANDOFF](step1.6_initial_historical_HANDOFF.md) — preserved
  preparation snapshot, superseded by the active HANDOFF; not current authority.

## Accepted predecessor and evidence

- [Step 1.5 archive index](../archive/task_step1.5/README.md) and
  [closure record](../archive/task_step1.5/HANDOFF.md).
- [Step 1.5d native acceptance](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md)
  and [final fixture/regression evidence](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md).
- [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29) — accepted
  managed RDP baseline; [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30)
  — accepted single-window launch, inventory and integrated regression.

## Latest maintainer-native result and corrected requirement

**Approved implementation semantics, demonstrated natively:**
`-d MANAGED_ID` closes only the positively identified managed window and
retains its registration/slot; confirmed `-x` progressively retires verified
missing entries and verified closed entries from its fixed snapshot. `-D`
remains version 2.

On **q552u01** (Wayland/XWayland), the confirmed clean sweep successfully
retired **9/9** records (8 closes, 1 missing), and `-l` became empty without
broker restart. See the [progressive addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).

On **slim2** (native KWin X11 6.7.6), the maintainer installed/loaded the
correctly owned native effect, passed **1,016/1,016 Python** and **163/163
JavaScript** tests after selecting an executable test TMPDIR, launched
**15/15** configured windows, verified two retained selective `-d` closures,
then confirmed a **16/16** progressive `-x` clean sweep (2 already missing,
14 native X11 closes) with immediate empty `-l` and independently queryable
full retained result. Later tests proved a freed slot takes a new managed ID,
negative `-d`/`-x` confirmations leave the window untouched, and real Konsole
quit dialogs produce `partial/not_closed_timeout`, not force killing.

**Decision:** no observed implementation blocker. A dedicated live compositor
fixture for absent `WM_DELETE_WINDOW` and stale/reused XID race is not yet
recorded even though the compiled helper and native broker have headless
safety tests. Mid-transaction self-terminal loss and remote worker lifecycle
are also not independently demonstrated. The maintainer must decide whether
these evidence gaps need narrowly scoped live validation or may be recorded
as accepted residual limits. See the [slim2 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md).

**Source/publication state:** Branch `task/joetoo-kwin-step1.6-managed-close`
is published through `c57ab8c`. q552u01 at `8849e59` needs a normal clean
fast-forward and optional upstream setup; no code conflict is demonstrated.
The cloud-authored documentation draft is not committed/published; normal
diff review and maintainer publication approval remain. No additional Codex
implementation round is indicated by this evidence.

## Corrected-candidate validation (Codex report and q552u01 maintainer run)

| Source | Tests/results | Interpretation |
| --- | --- | --- |
| Codex final focused Python | 107 run; 106 PASS, 1 SKIP | Sandbox `SO_PASSCRED` availability skipped |
| Codex final full Python | 1,016 run; 1,015 PASS, 1 SKIP | No final-tree failure/error |
| Codex final JavaScript | 163 PASS | No skip/failure |
| Codex syntax, ShellCheck, AST, whitespace | PASS | Candidate source-only checks |
| Maintainer `restart_joetoo-kwind t` | **1,016 Python OK, 163 JS PASS**, installer check PASS | User broker updated/restarted and tests run natively on q552u01 |
| Maintainer confirmed `-x` | 8 native closes + 1 already missing; **9 retired; empty `-l`** | Direct q552u01 positive-path evidence |
| Maintainer slim2 X11 regression/native `-x` | **1,016 Python OK; 163 JS PASS; 2 missing + 14 native X11 closes; 16/16 retired; status retained after CLI exit** | Native X11 positive path, [detailed evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md) |

The prior Codex intermediate help-test failure was corrected before the final
fresh-tree test. These original headless tests did not themselves demonstrate native refusal,
XID-reuse/lifetime fencing on `kwin_x11`, or remote-worker cleanup.
The later slim2 record now documents **actual native Konsole refusal**,
while live XID-reuse and remote-worker lifecycle remain unverified.

## Prior candidate headless validation (2026-11-16; before native results)

This section preserves the earlier Codex report at baseline/ending HEAD
`cdcdc9e8c842d0be04447c06b90a25d3cc59f107` on the task branch **before**
the maintainer pushed changes and performed native testing. It is historical
headless evidence and does **not** validate the new `-x` refinement.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_managed_close test_managed_close_cli test_managed_close_native test_config_presentation test_openrc_user_setup
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
node --test --test-isolation=none tests/test_*.js
cmake -S native/managed-close -B /tmp/joetoo-managed-close-build
cmake --build /tmp/joetoo-managed-close-build -j2
cmake -S native/managed-close -B /tmp/joetoo-managed-close-x11-build -DJOETOO_KWIN_X11=ON
cmake --build /tmp/joetoo-managed-close-x11-build -j2
bash -n joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions tools/joetoo-kwind-install-poc
shellcheck -x joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions tools/joetoo-kwind-install-poc
git diff --check
# End of commands

```

- Focused: 107 run, 106 PASS, 1 SKIP, no failures/errors.
- Full Python: 999 run, 998 PASS, 1 SKIP, no failures/errors.
- JavaScript: 163 PASS, no skips/failures.
- Bash syntax and ShellCheck: PASS. Python AST parsing: seven changed/new
  Python sources/tests PASS; native plugin metadata JSON parses.
- Both native effect variants and helper compile against the installed 6.7.6
  SDK using the commands in the adapter notes; build products stayed in `/tmp`.

SO_PASSCRED is denied by this sandbox. Its explicit availability test skips;
wire tests execute actual libxcb with an isolated platform-credential double.
Unconfined tests use real credential transport automatically. The later
maintainer-native effect loading and **some actual window disappearance**
are in the [evidence](step1.6-native-wayland-evidence-2026-11-16.md);
those native limitations applied **at the time of that earlier record**.
See the subsequent [slim2 X11 evidence](step1.6-slim2-native-x11-evidence-2026-11-18.md)
for later refusal and live X11 results; native XID-reuse and worker cleanup
are still unverified.

The first full run reported two stale configuration-presentation assertions
(981 PASS / 2 FAIL); their expected debug-variable inventory was corrected.
The final counts above supersede that run. Installer tests used disposable HOME
fixtures; no live installer, service or desktop operation was performed.
