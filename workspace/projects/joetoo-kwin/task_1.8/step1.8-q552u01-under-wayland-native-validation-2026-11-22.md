# Step 1.8 — q552u01 Wayland `-L under` native integration and regression evidence

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22. **Host:** `q552u01`, Plasma Wayland, KWin 6.7.6.
**Operator:** maintainer. **Branch:** `task/joetoo-kwin-step1.8-cli-completion`,
maintainer-pushed implementation HEAD `73afa19`. This record supplements the
[initial integrated desktop-1 failure and desktop-3 pass](step1.8-q552u01-under-integrated-participation-2026-11-22.md)
and the [V2/V3 feasibility results](step1.8-q552u01-one-shot-lower-feasibility-2026-11-22.md).
All tests and system changes described below were performed and reported by
the maintainer; this file does not claim independently reproduced results.

## Native environment and displayed-desktop constraint

**Maintainer's explicit confirmation:** *All the following launch trials were
initiated from desktop 1 and Plasma remained on desktop 1 throughout.* This
closes the previously unverified **no desktop switch** observation for the
inactive-target-desktop Wayland test. Direct before/after active-window UUID
snapshots were not supplied, so focus-UUID preservation is supported by the
successful broker verification protocol rather than independent console evidence.

The `-L under` policy is one-shot, not permanent KeepBelow. The KWin resident
verifies a new positively registered UUID below **participating visible
NormalLayer peers** while preserving raw full-stack evidence and respecting
protected layers and minimized/hidden peers. The inactive-desktop implementation
raises participating peers in prior relative order instead of attempting to
activate a window on an undisplayed desktop. This is the maintainer-approved
narrow exception to the earlier no-peer-restacking constraint; it must not
change peer geometry or switch desktops.

## Corrected active-desktop `under`: desktop 1, protected bridge

The original `win-013` attempt on desktop 1 correctly moved below all ordinary
peers but failed strict absolute-bottom verification because an invisible,
64x36 `xwaylandvideobridge` remained underneath. The property-based
participation correction and subsequent broker verification repair were
applied before the following successful native retest.

```text
$ ./joetoo-kwin -L 1 konsole ssh yorsqui under
... Desktop  Slot  Program  Mode  Target   Layer  X   Y   Width  Height
... 1        2     konsole  ssh   yorsqui  under  96  32  1804   972
... [20261122-11:39:54] Launching desktop [1] slot [2]
... Registered [win-015] UUID [3845b99e-4bd0-487a-b75b-f56be437b3f5]
... OK launch: joetoo-kwin : bash — Konsole ... after=[1] (96,32) 1804x972
... Desktop [1] initial stacking/focus result: (completed)
... Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
... Configured layout: [1/1] windows completed ... (completed)
```

**Result: PASS as reported by the integrated transaction.** The `-l`/`-i`
read-only queries and `RegistryStatus` showed the managed window present,
placement succeeded, observer synchronized, and broker `single_lower_protocol=1`.
The raw post-stack JSON for this specific run was not included in the report;
the outcome is based on the broker's verified transaction, not an independently
reconstructed physical stack. The previously reported xwaylandvideobridge
identity/source and screenshots remain documented in the initial evidence.

## Inactive-target desktop `under`: desktop 3 without switching from desktop 1

```text
$ ./joetoo-kwin -L 3 konsole ssh yorsqui under
... Desktop  Slot  Program  Mode  Target   Layer  X   Y   Width  Height
... 3        6     konsole  ssh   yorsqui  under  96  32  1804   972
... [20261122-11:47:41] Launching desktop [3] slot [6]
... Registered [win-016] UUID [947fe577-4f75-4291-8871-7e0e8dfbb55b]
... OK launch: joetoo-kwin : bash — Konsole (pid=3702089)
... before=[1] (58,31) 1804x972 after=[3] (96,32) 1804x972
... Desktop [3] initial stacking/focus result: (completed)
... Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
... Configured layout: [1/1] windows completed ... (completed)
```

**Result: PASS.** The maintainer explicitly confirms desktop 1 stayed displayed
for the entire operation. `./joetoo-kwin -l` and `-i win-016` confirmed
`present`, `placement=succeeded`, desktop 3/slot 6, original UUID
`947fe577-4f75-4291-8871-7e0e8dfbb55b`, Konsole class and final
frame `(96,32) 1804x972`. The existing missing `win-007` reservation remained
retained at desktop 3/slot 1; this launch allocated slot 6 rather than reusing
that reservation. The resident's accepted transaction verifies stacking, but
no separate independent raw stacking-order capture was supplied.

## `over` and viewer-adapter regression trials, also initiated from desktop 1

The maintainer supplied a shell transcript (interactive prompt padding trimmed for patch whitespace hygiene):
[full RDP/VNC console log](step1.8-q552u01-rdp-vnc-console-2026-11-22.txt).
The unsuccessful URI/mode attempts were validation failures (mostly before
confirmation/launch), not evidence of `-L under` stacking malfunction.

| Invocation / observed stage | Outcome | Qualification |
| --- | --- | --- |
| `-L 3 sdl-freerdp rdp rdp://joe@opi6plus01 over` | **FAILED**, remote launch unresolved | Failure reason not established; do not claim a stacking regression |
| `-L 5 sdl-freerdp rdp rdp://joe@opi6plus01 over` | **PASS**, initial stack/focus completed | Local managed launch only; remote login/authentication not proved |
| `-L 5 vncviewer ssh ssh://joe@x401/display/2 under` | **PASS**, TigerVNC managed launch and stack/focus completed | Display `:2` from URI; local placement/management, not a fresh remote health check |
| Invalid RDP/VNC targets, programs and transport modes | **Correctly refused** | See raw transcript; no redesign implied |

The `-L 5 ... rdp ... over` trial launched at **11:51:42** and completed the
initial stack/focus transaction. The `-L 5 ... vncviewer ... under` trial
launched at **11:59:28** and reported:

```text
TigerVNC managed desktop launch result: (completed)
Desktop [5] initial stacking/focus result: (completed)
Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [1/1] windows completed ... (completed)
```

A later `-l` listed `win-017` on desktop 5 slot 2 and `win-018` on desktop 5
slot 3. `-i win-018` positively identified UUID
`300bac15-2552-4a22-9622-e277062bb0e7`, `RESOURCE_CLASS: Vncviewer`,
`present`, `placement=succeeded`, and frame `96 32 1804 972`.
The `-L 3` RDP failure remains a separate **unresolved** native test result;
subsequent `-L 5` RDP success does not explain it.

## Regression-repair and broker readiness evidence

The first participation follow-on introduced test regressions. The maintainer
reported a full run **1,094 Python tests with 3 failures** and **169 JavaScript
tests with 29 failures** *before* the repair: a JavaScript harness collision
between recipe-layer strings and numeric KWin window layers, two outdated
config-display expectations, and a broker protected-layer-order guard gap.
The follow-up repair was applied and `git diff --check` passed.

The supplied [repair/restart console transcript](step1.8-q552u01-regression-repair-console-2026-11-22.txt)
shows the **post-repair focused suites**:

| Suite | Result |
| --- | --- |
| `test_config_presentation.py` | **6/6 PASS** |
| `test_initial_layout_broker.py` | **20/20 PASS** |
| `test_initial_layout.js` | **44/44 PASS** |
| Earlier `test_single_recipe_launch.py` run before the final repair | **14/14 PASS** |

These are focused results; **a full Python/JavaScript run after the repair has
not yet been supplied**. The earlier full-suite failures must not be recorded
as either current failures or as a subsequently proved full-suite pass.

The maintainer ran `./tools/restart_joetoo-kwind notest`, which installed
and checked the user-owned files and unloaded the resident. Immediate
D-Bus introspection returned `Service ... does not exist`; later read-only
checks demonstrated the broker operating normally:

```text
rc-service -U joetoo-kwind status   # started
RegistryStatus: recovery=ready, observation.synchronized=true,
  single_lower_protocol=1, single_raise_protocol=1,
  initial_layout_active=false, presence_counts.uncertain=0
./joetoo-kwin -s: State: No reported Busy/uncertain flags
```

The immediate introspection failure is consistent with a startup/readiness
race but the logs do **not** prove its cause. The observed installed component
count (14) is the installer inventory count, not the number of changed files.
The read-only `-s` human summary still omits the new `single_lower=1` capability,
although the raw `RegistryStatus` includes it; retain this as a small
pre-acceptance presentation improvement.

## Evidence boundary and next acceptance gate

**Established on q552u01 Wayland:** both displayed-desktop and inactive-target
`-L under` succeeded; the protected bridge does not invalidate a correct
user-facing lower; no desktop switch occurred; a VNC viewer `under` and RDP
viewer `over` completed locally. The previously accepted `-s/-i` behavior
remains observed. This is not acceptance on native X11 or a finished full
regression result.

**Next:** maintainer-operated **slim2 native KWin 6.7.6 X11** compatibility and
non-regression smoke checks, followed by a full post-repair Python/JS run,
`-s` capability-display polish, final evidence reconciliation and maintainer
acceptance/PR review. The task is **ACTIVE**, not merged/closed. Earlier
screenshots are linked in the [integrated evidence](step1.8-q552u01-under-integrated-participation-2026-11-22.md).
