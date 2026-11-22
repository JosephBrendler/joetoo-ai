# Step 1.8 (new) — Complete the Version 1 CLI contract

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status (2026-11-22): ACTIVE; `-L under` implementation pushed at `73afa19`.**
Read-only `-s` and `-i` have native Wayland/X11 smoke evidence. The corrected
`-L under` now has **positive q552u01 Wayland native results** for displayed
desktop 1 (including the protected XWayland Video Bridge) and inactive
desktop 3 without switching away from desktop 1. A TigerVNC `under` and an
SDL RDP `over` launch also completed locally. Post-repair focused tests pass;
**slim2 native X11 `-L under`, full post-repair regression suites, and final
maintainer acceptance remain pending.** `-L panel` is excluded. The accepted
`main` reference is `7fdd2cf`; task branch merge-base was `24cd67f`, so
ancestry must be reconciled at PR review, not during native testing. The
former Step 1.8 was folded into Step 1.7; this is a separate active task.

**Accepted foundation:** All Steps **1.1–1.7 are accepted and closed**.
Step 1.5d's `-L over`/`-l` behavior is accepted
([PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30));
Step 1.6 managed `-d`/`-x` close is accepted
([PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)); and
Step 1.7 checkpoint/recovery and `-S`/`-r` is accepted
([PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33)).
This task must preserve all of those decisions and their evidence.
The [active HANDOFF](HANDOFF.md) owns task dispatch and authorization;
[ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md) owns product requirements.
The [initial planning outline](step18-branch-outline.md)
is supplemental to this task scope.

## Objective and smallest useful change

Deliver these three remaining Version 1 CLI capabilities **without
introducing a new registry, window selector, geometry engine, or general
stacking framework**:

| CLI invocation | Earlier `7fdd2cf` source | Step 1.8 target and present result |
| --- | --- | --- |
| `joetoo-kwin -s` | Parsed, then reports not yet integrated | Implemented; terminal-`OK` classification fixed; native Wayland/X11 smoke PASS |
| `joetoo-kwin -i MANAGED_ID` | Parsed, then reports not yet integrated | Implemented; present/missing records demonstrated on Wayland and present record on X11 |
| `joetoo-kwin -L DESKTOP PROGRAM MODE TARGET under` | Not accepted on earlier baseline | **Implemented on `73afa19`; q552u01 Wayland PASS:** displayed desktop 1, inactive target desktop 3, and VNC viewer. Native X11 pending. |
| `joetoo-kwin -L ... [over]` | **Accepted** default/explicit `over` | Preserve behavior and native regression evidence |
| `joetoo-kwin -L ... panel` | Unsupported | **Remain unsupported; Version 2**, with explicit refusal before side effects |

The maintainer approved **one-shot `under`** as a narrow revised Version 1
target, implemented on the Step 1.8 branch at `73afa19`. This deliberately
revises Step 1.5d's earlier Version 2 classification, but does not retroactively
change Step 1.5d acceptance or constitute Step 1.8 final acceptance.

## Read-only implementation, native evidence and known limitations (2026-11-22)

- **Implementation:** `1670bea` introduced the `-s`/`-i` CLI paths,
  `libexec/joetoo_kwin_readonly.py` and focused tests. `f3fef58` fixed a
  false **Busy/uncertain** report: the prior helper treated a retained,
  completed placement `OK` as *active*. `PENDING`/`RUNNING`/`VERIFYING` remain
  active, while `OK` and `ERROR` are terminal and unknown states fail closed.
- **Wayland evidence:** [q552u01 native read-only evidence](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md)
  contains selected `-l`, `-i` (present **and missing**) and pre-/post-fix
  `-s` output; **9/9 Step 1.8 focused tests PASS**. The long-running broker
  was not restarted for the `-s` repair.
- **X11 evidence:** [slim2 native read-only evidence](step1.8-slim2-readonly-x11-evidence-2026-11-22.md)
  records KWin **6.7.6**, successful user OpenRC broker restart, two recovered
  present records, and successful `-s`, `-l`, and `-i`. Source-tree extended
  ShellCheck passed; JavaScript **163/163 PASS**.
- **Obsolete fixture test:** the slim2 full Python run executed **1,089**
  tests with **one failure** from a stale Step 1.4d assertion that the now-
  accepted `-o` still contained `not yet integrated`. Test-only commit
  **`cadf992`** repaired that historical fixture. The maintainer reports
  the focused test passed on slim2; q552u01 subsequently showed **3/3 PASS**.
  A *full* Python rerun following the repair is **not yet evidenced**.
- **ShellCheck side effort:** joetoolkit **1.0.19** added
  `shellcheck_stub_filter`, which scanned **29** shell-shebang consumers and
  retained **69/1,329** generated header-variable definitions while keeping
  the full function stub. The generated consumer-scoped
  `script_header_joetoo.shellcheck_filtered_stub` was committed with
  `1670bea`; `validate_scripts ./joetoo-kwin -l` passed in **9.000s** on
  q552u01 (previously about **28s**, ~7 GB reported). Peak memory after
  filtering was **not measured**. This tool is a separate joetoolkit workflow
  improvement, not part of the Step 1.8 CLI contract.
- **Scope/remaining gaps:** the successful CLI invocations used the
  **project source tree** and the maintainer's POC broker/resident installer.
  Installed-CLI packaging/lookup for the newer read-only helper is not proven;
  Step 1.9 owns packaging. Step 1.8 is **not accepted/merged**. Current
  testing/evidence status and a baseline for the next slim2 gate are in the
  [Wayland integration record](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md).

## One-shot lower: feasibility, implementation, native evidence (2026-11-22)

The [V2/V3 Wayland probes](step1.8-q552u01-one-shot-lower-feasibility-2026-11-22.md)
established exact-UUID guarded `workspace.activeWindow` activation and
`workspace.slotWindowLower()` with settled stack verification. No
`workspace.lowerWindow(target)` is exposed in KWin 6.7.6 scripts. The V3 probe
rightly refused cross-desktop targeting; the integrated inactive-desktop path
uses a separate bounded peer-raising approach instead.

The first [integrated trials](step1.8-q552u01-under-integrated-participation-2026-11-22.md)
showed a **PASS on desktop 3** (`win-014`) and a **strict absolute-bottom
false negative on desktop 1** (`win-013`), where KWin preserved an invisible
64x36 `xwaylandvideobridge` / KeepBelow surface below the target. That remains
historical negative evidence; it is not the status of the corrected version.

**Corrected participation policy:** the target must be an ordinary visible
NormalLayer window. Other visible normal-layer peers participate; protected
BelowLayer/KeepBelow and other non-normal-layer surfaces, minimized/hidden
or opacity-zero windows remain in raw full-stack evidence but do not dictate
user-facing `under`. `skipTaskbar` alone does not exclude an otherwise
participating window. Broker and resident verify membership, participation,
relative peer order, geometry and source/lease/identity; unsupported or
ambiguous properties fail closed. On an inactive target desktop, only
participating peers are raised in their previous relative order; there is no
involuntary desktop switch or geometry reflow. It is one-shot, not persistent
KeepBelow. `single_lower_protocol` negotiates this separately from the
accepted `single_raise_protocol`; `single_lower_settle_ms` defaults to 300
ms (allowed 100..1000).

**[Corrected q552u01 Wayland native validation and logs](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md)**
records these maintainer-operated results:

- **Desktop 1 displayed, `under`:** `-L 1 konsole ssh yorsqui under`,
  `win-015`, succeeded; protected bridge no longer causes false failure.
- **Desktop 3 inactive, `under`:** `-L 3 konsole ssh yorsqui under`,
  `win-016`, succeeded; maintainer confirms **desktop 1 remained displayed
  throughout**. The existing missing desktop 3/slot 1 reservation was kept.
- **Desktop 5 inactive, VNC `under`:** `-L 5 vncviewer ssh
  ssh://joe@x401/display/2 under`, `win-018`, succeeded; `-i` verified
  a positively managed Vncviewer UUID, placement and frame.
- **Desktop 5 inactive, SDL RDP `over`:** local launch/stack succeeded;
  a prior desktop-3 RDP launch failed unresolved. Local viewer success
  does not establish remote authentication or session health.
- **Regression correction:** after 3 Python / 29 JS failures in a *pre-repair*
  full run, the post-repair focused suites returned **6/6** config,
  **20/20** broker and **44/44** initial-layout JS PASS; the single-recipe
  suite previously passed **14/14**. A *full post-repair rerun* is pending.

`RegistryStatus` on q552u01 reports synchronized observations,
`recovery=ready`, `single_lower_protocol=1` and no uncertain managed
registrations. Read-only `-s` currently omits `single_lower=1` from its
human capability summary; this small display defect does not negate the
working protocol. Brief restart-time D-Bus introspection failure was not
reproduced after the broker became ready; its exact cause is not established.

**Next gate:** maintainer-operated **slim2 native KWin 6.7.6 X11** `-L
under` compatibility, then full post-repair regression suites and final
Step 1.8 review. These Wayland successes do **not** establish native X11
acceptance.

## A. `-s` — read-only broker status

Reuse the existing session-bus method
`org.joetoo.KWinBridge.RegistryStatus()` in
[`libexec/joetoo-kwind`](../libexec/joetoo-kwind). That method already
returns in-memory managed counts, observation synchronization, placement
transaction state, recovery, relevant protocol/capability and cleanup fields.
It is a broker snapshot, **not** an independent remote-connection check.

- Preserve existing CLI options and joetoo `j_msg` / announce–act–report
  idioms; no new daemon API is needed for ordinary `-s`.
- Require no operands; never start the broker, load KWin effects or source a
  launch plan merely to display status.
- Parse a complete, allowlisted, bounded response. Distinguish an unavailable
  broker, malformed/inconsistent JSON, and available status. Display Busy or
  uncertain state faithfully rather than reporting unconditional readiness.
- Do not imply working SSH, RDP, VNC authentication or remote application
  health from a managed window's presence or placement.

**Focused acceptance:** valid empty and populated status, Busy/uncertain
state, disconnected broker, missing dependency, malformed/error replies,
extra operands, correct exit status, and no state-changing broker calls.

## B. `-i MANAGED_ID` — read-only managed-window information

Reuse the existing broker `GetManaged(identifier)` method, which returns a
bounded allowlist with `state:FOUND` and a managed record, or
`state:UNKNOWN`. The broker's interface accepts broader identifiers, but
the **public CLI** must accept exactly one canonical `win-NNN`-style
managed ID, not an arbitrary raw KWin UUID, title, class or PID.

- Validate the argument before querying the broker. Reject missing, extra or
  malformed IDs without launching an application or selecting a window.
- Show managed ID, original desktop/slot, presence and placement, and
  available allowlisted identity/observation information without disclosing
  private recipes, credentials or unapproved fields.
- Label recovered/historical observations **last-known** where appropriate;
  `presence:missing` and `presence:uncertain` must not be portrayed as live
  authenticated windows. `UNKNOWN` is distinct from broker unavailability.
- Remain read-only: no focus, movement, adoption, close, launch, slot
  retirement or selector/profile modification.

**Focused acceptance:** found-present, found-missing, found-uncertain,
unknown ID, broker-unavailable, malformed response, invalid identifier,
absence of optional observation keys, safe redaction and nonmutation.

## C. `-L ... under` — new one-window stacking behavior

Extend the **existing** one-recipe launch path and its broker/resident
initial-layout protocol, rather than replacing accepted `-L over` machinery.
The new `under` option is available only for a valid, confirmed single launch
and applies to **the exact original UUID** positively registered by that
launch on the requested desktop.

- Reuse existing recipe/target validation, confirmation, desktop capacity,
  free logical-slot selection (including retained missing reservations),
  application ownership, placement, timeout, cleanup and Busy guards.
- Prove the KWin **6.7.6** native X11 and Wayland APIs support a bounded
  one-shot lower without a permanent `keepBelow` rule or geometry change.
  Check focus/activation interactions: a later activation must not silently
  defeat the requested final stack position and still count as success.
- Verify the final order against the actual compositor's eligible normal
  windows on that desktop, using the existing UUID/source/transaction
  evidence. Do not classify a class/title match or unverified request as a
  successful lower. If safe lowering or readback is unavailable, fail
  explicitly (do not substitute `over`).
- Do **not** move, resize, reallocate, recascade or adopt existing peers.
  Ordinarily do not restack peers. The *inactive-target-desktop candidate only*
  proposes bounded raising of eligible normal peers in their existing order,
  with full readback and unchanged geometry; this exception remains subject
  to native validation and maintainer acceptance. Do not create a live panel
  insertion policy, persistent keep-below or generalized focus machinery.
- Continue supporting omitted LAYER=`over`, explicit `over`, and the
  separate configured `-o` `under/panel/over` layers unchanged. Keep
  `-L panel` a clear pre-launch validation error.

**Native acceptance (maintainer-operated):** on both KWin 6.7.6 Wayland and
native X11 sessions, demonstrate positive new-window UUID correlation,
correct one-shot lower and post-operation readback, existing peers' geometry
unchanged, a retained/missing reservation not reused, ordinary launch
failure/refusal preserving previous state, competing focus/activation handling,
and clear unsupported/timeout/fail-closed results. Test `-L over`, configured
`-o`, `-l`, managed close and Step 1.7 recovery for regressions relevant to
the modified protocol. Avoid a complete repeat of historical RDP/VNC
acceptance tests without a demonstrated need.

## Remaining validation and acceptance sequence

1. **Baseline:** keep `task/joetoo-kwin-step1.8-cli-completion` at
   maintainer-pushed `73afa19` while testing; inspect branch and dirty-state
   before any installation. Accepted Steps 1.1–1.7 stay closed.
2. **Next — slim2 native X11:** verify KWin 6.7.6 native X11, installed
   broker/resident source consistency, recovery/observation readiness and
   `single_lower_protocol=1`. Test a disposable `-L under` on an active
   desktop, then (if safe) an inactive target desktop without a desktop/focus
   switch, validating registered UUID/slot, frame and stack verification.
   Include a small `-L over` regression. Do not retest every remote adapter
   without a specific reason.
3. **Full post-repair regression:** rerun complete Python and JS suites,
   plus Bash syntax and applicable ShellCheck/`validate_scripts` checks;
   capture exact totals and any failures. Do not promote the earlier focused
   6/20/44 PASS into a full-suite PASS.
4. **Small polish and review:** include `single_lower=1` in `-s` human
   capability reporting if compatible, verify `-o` and related close/recovery
   boundaries as needed, reconcile the earlier unresolved desktop-3 RDP
   launch without inventing its cause, and update evidence/HANDOFF.
5. **Maintainer acceptance and PR:** reconcile branch ancestry against
   accepted `main`, review the complete diff/limitations, and merge only
   upon maintainer authorization. Then resume Step 1.9.

## Non-goals and stop conditions

No `-L panel`, dynamic panel occupancy/reflow, existing-peer geometry
modification, keep-below policy, general reset-layout command, new RDP/VNC
clients, different window identity authority, Step 1.6 close redesign,
Step 1.7 recovery rewrite, KWin 6.8 migration, `tarup`, Portage ebuild work or
production system integration. Those remain outside this task.

Stop and seek maintainer review if the revised `under` contract cannot verify
an exact newly managed UUID, preserved geometry/membership/peer order,
protected layer semantics or bounded focus/desktop behavior on both accepted
compositor backends. The **explicit, bounded inactive-desktop peer-raising
fallback** is part of the current reviewed candidate, not a general license
to reflow geometry or rearrange other windows arbitrarily. Fail closed if
evidence is missing; never substitute `over` silently.

## Completion and transition

Step 1.8 is complete **only** when the maintainer accepts `-s`, `-i`, and
verified `-L under` on both supported KWin 6.7.6 compositor backends,
including focused non-regression evidence. At that point update the task
HANDOFF/README with the actual result, close the task and resume
[Step 1.9](../task_1.9/HANDOFF.md), which retains the human
maintainability-comment/source audit and packaging gates.
