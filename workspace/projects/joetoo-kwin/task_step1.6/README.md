# Step 1.6 — Task index

**Status (2026-11-16, evening):** Step 1.5 and PR #31's transition are
accepted/merged. The pushed Step 1.6 candidate has substantial q552u01
Wayland/XWayland native close evidence. **Not yet accepted:** the maintainer
approved progressive `-x` record/slot retirement; the current candidate still
retains all reservations. Remaining tests and publication remain gated.

## Current task and design

- [Native evidence (2026-11-16)](step1.6-native-wayland-evidence-2026-11-16.md)
  — selected maintainer command/result excerpts and unresolved acceptance tests.
- [DRAFT Codex prompt — progressive `-x` sweep](DRAFT_Codex-Step1.6-x-progressive-sweep.md)
  — proposed focused implementation; maintainer authorization required.
- [Original native adapter contract and matrix](../native/managed-close/README.md)
  — its retained-`-x` language reflects the old candidate and needs alignment
  at implementation time.
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

## Latest maintainer-native result and refined requirement

On `q552u01`, the corrected `joetoo_managed_close.so` loaded in a fresh
KWin 6.7.6 Wayland process and matched KWin's D-Bus owner. The OpenRC user
broker was current and running. Confirmed `-d` selectively closed native
Wayland and XWayland clients without closing unrelated windows. The broker
recorded exact UUID/backend and separate retained results; retry of a missing
managed ID was safely excluded. See the [native evidence](step1.6-native-wayland-evidence-2026-11-16.md).

A confirmed `-x` reported **6/6 eligible native windows closed**, but
retained **12/12** registrations/reservations as `missing` and reported
`partial` solely because six targets were already missing. A later broker
restart emptied the in-memory registry; that is **only a workaround**, not
the `-x` contract. The maintainer clarified:

- `-d ID`: retain the closed window's managed registration/slot/history.
- **`-x`:** once confirmed, retire each positively already-missing managed
  record immediately and retire each present record/slot **as soon as its own
  graceful closure is verified**. Continue other independently safe entries
  after individual failure; retain/report only minimal unresolved residue.
  Full success means empty `-l` without broker restart. No batch rollback.
- `-D ID`: one-window close-and-retire deferred to **version 2**.

**First next implementation:** focused `-x` registry-lifecycle and truthful
bulk result/preview correction, leaving the native adapter and `-d` behavior
untouched. [Codex draft](DRAFT_Codex-Step1.6-x-progressive-sweep.md) is ready
for maintainer review, **not** an automatic dispatch. The project architecture
and native adapter README still describe the old retention contract; update
their narrow wording with implementation. Remaining native gates include
top-level application refusal, workers/SSH/tmux cleanup, self-terminal/CLI
loss, and separate native X11 compositor/XID fence tests. Step 1.6 acceptance
and publication are **not** claimed; [HANDOFF](HANDOFF.md) is the dispatcher.

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
