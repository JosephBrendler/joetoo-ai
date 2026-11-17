# Step 1.6 — Task index

**Status (2026-11-16):** Step 1.5 and PR #31's archive/init transition are
accepted and merged. Step 1.6 is an uncommitted implementation candidate for
confirmed graceful `-d` and broker-owned fixed-set `-x`. Native acceptance and
publication remain reserved for the maintainer.

## Current task and design

- [Native adapter, safety contract and acceptance matrix](../native/managed-close/README.md).
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

## Next work and results

The source/contract review and final design are complete. The authorized
candidate implements confirmed `-d` and broker-owned fixed-set `-x`, using
three additive broker methods and the exact-version native close adapter.
Managed records, slots and placement history remain intact; application refusal
never triggers automatic force killing. `-a` is removed; `-D` retirement and
snapshot/restart restoration are not part of this milestone.

The [adapter notes](../native/managed-close/README.md) contain API details,
headless/native evidence boundaries and the maintainer acceptance matrix.
Current validation and next-actor permissions belong in [HANDOFF.md](HANDOFF.md).
No Step 1.6 native acceptance, installation or publication is claimed.

## Candidate headless validation (2026-11-16)

Baseline/ending HEAD: `cdcdc9e8c842d0be04447c06b90a25d3cc59f107`, branch
`task/joetoo-kwin-step1.6-managed-close`; candidate remains uncommitted.
The four starting documentation edits were preserved and extended.

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
Unconfined tests use real credential transport automatically. Real KWin loading,
Qt event ordering, native disappearance/refusal and application/SSH/tmux cleanup
remain maintainer-native acceptance, not headless claims.

The first full run reported two stale configuration-presentation assertions
(981 PASS / 2 FAIL); their expected debug-variable inventory was corrected.
The final counts above supersede that run. Installer tests used disposable HOME
fixtures; no live installer, service or desktop operation was performed.
