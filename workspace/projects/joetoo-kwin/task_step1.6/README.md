# Step 1.6 — Task index

**Status (2026-11-16, late evening):** Step 1.5 and PR #31's transition
are accepted/merged. The **uncommitted Step 1.6 progressive `-x` correction**
has passed Codex headless checks and a maintainer-native q552u01 Wayland/
XWayland clean sweep: 8 live windows closed, 1 missing record retired,
9/9 records retired, empty `-l` **without restart**. **Step 1.6 is not yet
finally accepted** pending only the remaining native safety/X11 checks and
maintainer publication decision. No demonstrated current coding blocker.

## Current task and design

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

**The refined `-x` clean-sweep requirement is implemented in the latest
locally uncommitted candidate.** The confirmed `-x` transaction on `q552u01`
returned `succeeded/verified`: **eight verified native closes** (seven
Wayland clients, one XWayland TigerVNC viewer), **one authenticated
already-missing retirement**, **nine `retired=true`**, zero exclusions, and
both snapshot retention flags `false`. The immediate independent
`./joetoo-kwin -l` output was:

```text
No managed windows (no retained managed reservations).
```

No broker restart occurred after the sweep. The earlier run that left 12
missing reservations is preserved in the [earlier native evidence](step1.6-native-wayland-evidence-2026-11-16.md);
the correction and new behavior are documented in the
[progressive-sweep addendum](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
The user-owned OpenRC broker was updated/restarted **before** the new launch
set; maintainer-native tests then ran **1,016 Python OK** and **163 JavaScript
PASS**. The corrected source did not modify the C++ effect/XCB helper or
RDP/VNC workers.

Lifecycle contract remains:

- `-d ID`: verified graceful close of one, **retain** record/slot/history.
- `-x`: confirm once, progressively retire authenticated absences and each
  verified graceful close; independent failures leave minimal unresolved
  records, while true native cleanup ambiguity blocks unsafe further
  dispatch. Fully resolved sweep leaves `-l` empty without broker restart.
- `-D ID`: close-and-retire one window, **version 2 only**.

The code still awaits final maintainer acceptance/publication; Codex reported
branch `task/joetoo-kwin-step1.6-managed-close`, local
`HEAD f26027a0add26442937c32b92fdc1ef9b54f1de9`, **10 modified tracked
files (uncommitted/unstaged)**. `git fetch` could not update its read-only
`.git/FETCH_HEAD`, so no refreshed remote synchronization is claimed.

**Shortest remaining work:** targeted maintainer-native tests for (1) declined
`-x`, status lookup, freed-slot/ID behavior, (2) refusal/known-safe partial
and self-terminal/CLI loss plus worker cleanup as feasible, and (3) separate
native `kwin_x11` helper/lifetime-fence cases on `slim2`. There is currently
**no demonstrated code defect requiring another Codex implementation round**.
See [HANDOFF](HANDOFF.md) for the next actor and reserved publication decision.

## Corrected-candidate validation (Codex report and q552u01 maintainer run)

| Source | Tests/results | Interpretation |
| --- | --- | --- |
| Codex final focused Python | 107 run; 106 PASS, 1 SKIP | Sandbox `SO_PASSCRED` availability skipped |
| Codex final full Python | 1,016 run; 1,015 PASS, 1 SKIP | No final-tree failure/error |
| Codex final JavaScript | 163 PASS | No skip/failure |
| Codex syntax, ShellCheck, AST, whitespace | PASS | Candidate source-only checks |
| Maintainer `restart_joetoo-kwind t` | **1,016 Python OK, 163 JS PASS**, installer check PASS | User broker updated/restarted and tests run natively on q552u01 |
| Maintainer confirmed `-x` | 8 native closes + 1 already missing; **9 retired; empty `-l`** | Direct positive-path acceptance evidence |

The prior Codex intermediate help-test failure was corrected before the final
fresh-tree test. These tests do not themselves demonstrate native refusal,
XID-reuse/lifetime fencing on `kwin_x11`, or remote-worker cleanup.

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
application refusal, native X11 ordering and worker/SSH/tmux cleanup remain
untested or unverified, not headless claims.

The first full run reported two stale configuration-presentation assertions
(981 PASS / 2 FAIL); their expected debug-variable inventory was corrected.
The final counts above supersede that run. Installer tests used disposable HOME
fixtures; no live installer, service or desktop operation was performed.
