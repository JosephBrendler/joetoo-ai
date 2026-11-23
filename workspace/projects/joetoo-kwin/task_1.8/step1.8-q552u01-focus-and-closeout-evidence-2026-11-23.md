# Step 1.8 — q552u01 Wayland focus, POC repair, closeout and regression evidence (2026-11-23)

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Status:** maintainer-operated positive native/automated results; **Step 1.8 still ACTIVE** pending a preferred-focus/competing-activity policy decision, final diff/ancestry review, and maintainer acceptance. This is evidence, not an authorization to commit, deploy, or merge. Host: **q552u01**, Gentoo, KDE KWin **Wayland** (`WAYLAND_DISPLAY=wayland-0`, `kwin_wayland --xwayland`). Local task branch `task/joetoo-kwin-step1.8-cli-completion`, HEAD **`4be1b0b`** plus four uncommitted files. q552u01 results below came from maintainer-provided command output and screenshot, not independent execution by this author.

Related history: [2026-11-22 X11 focus defect](step1.8-launch-control-focus-evidence-2026-11-22.md), [gmki91 X11 native acceptance](step1.8-gmki91-x11-native-validation-2026-11-22.md), [Wayland `under` acceptance](step1.8-q552u01-under-wayland-native-validation-2026-11-22.md). 2026-11-23 console uploads (with interactive-prompt trailing spaces normalized) are preserved in [the companion transcript](step1.8-q552u01-acceptance-console-2026-11-23.txt). The [panel preferred-focus screenshot](screenshots/20261123-q552u01-wayland-panel-focus-override.png) shows the new btop Konsole on the left and the invoking control Konsole on the right, after the control Konsole accepted a typed command.

## 1. Wayland environment and broker baseline

```text
WAYLAND_DISPLAY=wayland-0
kwin_wayland_wrapper --xwayland
kwin_wayland ... --socket wayland-0 ... --xwayland
rc-service -U joetoo-kwind status -> started
RegistryStatus: recovery=ready; observation=synchronized; no Busy/uncertain flags
Before the new tests: 11 present managed windows; 11 succeeded launches
```

The installed `-s` human capability line did not show `single_lower` despite earlier protocol evidence. This is presentation-only and should not be used to infer unsupported `under` behavior.

## 2. `-L under` on inactive desktop 5 — control return PASS

From the original control Konsole on desktop 1, with an **unmanaged Konsole already on desktop 5**:

```text
$ DEBUG=$TRUE ./joetoo-kwin -L 5 konsole local btop under
Control-window focus capture: state=[captured] reason=[none] stage=[none]
Planned desktop [5] slot [1]: 96,32 1804x972
Registered [win-012] UUID [1847b72c-9db3-48c3-938b-3d2e438271c2]
Desktop [5] initial stacking/focus result: (completed)
Initial layout: state=SUCCEEDED; geometry=unchanged; stacking=verified;
  focus="inactive desktop; no activation"; current_desktop=1;
  lower_method=raise_peers; lower_peers_intact=true; lower_settled=true
Configured layout: [1/1] windows completed ... (completed)
Control-window focus restore: state=[requested]
Mission return code: 0
$ echo "wayland keyboard focus: pass"
wayland keyboard focus: pass
$ ./joetoo-kwin -l
win-012  desktop=5  slot=1  present  succeeded
```

**Established:** exact UUID registration, initial stack verification, no reported desktop switch, and usable keyboard focus in the original control Konsole after completion. The user reported no intervening click. The ordinary relative `under` peer-order result is supported by the verified `raise_peers` readback, not just the terminal `echo`.

## 3. Configured `-o` with one `under` Dolphin on desktop 6 — control return PASS

To avoid existing slots on desktops 2, 3, 4 and 5, the maintainer used a temporary one-recipe plan on desktop 6:

```text
screen_width=1920
screen_height=1080
desktop_session_list=('6|dolphin|local||under')
$ DEBUG=$TRUE ./joetoo-kwin -o -f "$test_config"
Control-window focus capture: state=[captured]
Registered [win-013] UUID [0ce3b13b-f5a6-4fd4-9d23-9aafd886a187]
Desktop [6] initial stacking/focus result: (completed)
Initial layout: state=SUCCEEDED; geometry=unchanged; stacking=verified;
  focus="no automatic target"; preferred_uuid=null; current_desktop=1
Configured layout: [1/1] windows completed ... (completed)
Control-window focus restore: state=[requested]
Configured launch return code: 0
$ echo "passed"
passed
$ ./joetoo-kwin -i win-013
MANAGED_ID: win-013
DESKTOP: 6
SLOT: 1
PRESENCE: present
PLACEMENT: succeeded
```

**Scope:** this one-window `under` run had `lower_method=null`, so it tests configured launch and controller focus, **not** an independently verified relative lower beneath a peer. The desktop-5 test above covers inactive `under` peer behavior.

## 4. Configured `-o` with preferred `panel` Konsole on displayed desktop 1 — POLICY ACCEPTED

Configuration used and validated with `./joetoo-kwin -c -f "$test_config"`:

```bash
screen_width=1920
screen_height=1080
desktop_session_list=(
    '1|konsole|local|btop|panel'
)
```

Maintainer's exact salient output from `DEBUG=$TRUE ./joetoo-kwin -o -f "$test_config"`:

```text
Control-window focus capture: state=[captured] reason=[none] stage=[none]
Planned desktop [1] slot [1]: 19,54 1670x918
preferred focus slot [1] (intent only)
Registered [win-014] UUID [d84c39fe-64cd-4d58-b58b-860565bfd693]
Desktop [1] initial stacking/focus result: (completed)
Initial layout: {
  "state":"SUCCEEDED", "geometry":"unchanged", "stacking":"verified",
  "focus":"verified", "preferred_uuid":"d84c39fe-64cd-4d58-b58b-860565bfd693",
  "observed_active_uuid":"d84c39fe-64cd-4d58-b58b-860565bfd693",
  "focus_attempted":true, "current_desktop":1, "focus_observation":"immediate"
}
Configured layout: [1/1] windows completed ... (completed)
Control-window focus restore: state=[requested] reason=[none] stage=[none]
Configured launch return code: 0
$ echo "nicely returned focus"
nicely returned focus
```

![New preferred `panel` Konsole on left, original controller on right after return of usable keyboard focus](screenshots/20261123-q552u01-wayland-panel-focus-override.png)

**Established:** the KWin initial-layout transaction successfully put focus on the new preferred window, *then* the subsequent mission-completion control restoration brought usable input focus back to the original control Konsole. The screenshot and typed `echo` support the latter. No independent after-restoration KWin UUID snapshot was supplied; do not claim one. The maintainer described the behavior positively as "nicely returned focus." This is evidence of **working controller return**, not evidence that previously accepted preferred-focus semantics are preserved.

**Maintainer decision (2026-11-23, after reviewing this evidence):**
The observed controller-return behavior is the **intended Version 1
contract**. Configured `-o` still verifies the selected `panel`/`over`
window's focus *during initial layout*, but that is not a commitment
to leave the operator in that window after a serialized mission.
The eligible original launch Konsole should regain usable keyboard
focus at completion. All launch operations are intentionally serial,
and blocking VNC/RDP authentication occurs on the launch desktop,
not the remote layout desktop. No Version 1 workflow is designed
to move the user among layout desktops. The prior proposed
preferred-focus-preservation rule is superseded. Version 2 may
reconsider navigation/focus if parallel multi-launch behavior
makes it necessary.

**Separate evidence limitation:** the code at `4be1b0b` does
not establish a veto when a human explicitly focuses a different
window while a mission is pending. The current best-effort
controller restoration may supersede that activation. This test
did not exercise such a race. No safeguard against competing
user activity is claimed; review that limitation explicitly
during PR acceptance. There was no change to source behavior
after this policy decision.

## 5. Native managed-close and POC installation regression — PASS

- Initial `./joetoo-kwin -d win-011` refused because `org.joetoo.KWinCloseNative` had no D-Bus owner (native effect unloaded). `isEffectSupported joetoo_managed_close` was `true`, `isEffectLoaded` was `false`; explicit `loadEffect joetoo_managed_close` returned `true`. Native service then exposed `Inspect`, `Terminal`, `Close`, `Status`. This diagnoses an **operational effect-loading prerequisite**, not a demonstrated Step 1.8 regression.
- The maintainer enhanced `tools/restart_joetoo-kwind`: shorthand `cbus`/`cpath`; idempotent native effect-owner/load check; bounded readiness polling of both KWinBridge and KWinCloseNative before introspection. `./tools/restart_joetoo-kwind notest` subsequently passed both introspections. Already-loaded path tested; automatic-load branch **not yet separately tested**. Successful OpenRC start alone had briefly preceded broker D-Bus name registration.
- POC installer now installs/updates/verifies/archives `joetoo_kwin_sftp_target.py` at `~/.local/libexec/` (15 installed files). Its isolated Python `-I` restore-intent regression reproduces the missing-sibling import defect. `test_openrc_user_setup.py`: **54/54 PASS**. The full 2026-11-23 Python suite includes the updated installer tests. Production `${ED}` installed-image isolation is an **explicit Step 1.9 gate**, not established by POC `--check`.
- `./joetoo-kwin -d win-011` with the native effect loaded prepared a safely excluded `missing` target; result `state=partial`, no other window adopted. The subsequent confirmed `./joetoo-kwin -x` returned `state=succeeded`, `reason=verified`, `registration_retained=false`, `reservations_retained=false`, `excluded=[]`: **3 verified missing records retired**, **10 present windows verified closed** (native Wayland and X11/XWayland targets). Final `./joetoo-kwin -l`: **No managed windows (no retained managed reservations)**.

## 6. Automated regression and current Git status — PASS / pending review

Maintainer ran the **full suites after the POC SFTP repair**, with results:

```text
Ran 1113 tests in 187.279s
OK
Python return code: 0

Node --test: tests 180; pass 180; fail 0; cancelled 0; skipped 0
JavaScript return code: 0

bash -n tools/restart_joetoo-kwind  # no output (success)
git diff --check                  # no output (success)
```

Four uncommitted files at branch HEAD `4be1b0b`: `task_1.9/step1.9-packaging-inventory-contract-REVISED-DRAFT.md`, `tests/test_openrc_user_setup.py`, `tools/joetoo-kwind-install-poc`, `tools/restart_joetoo-kwind`. An earlier stat was **4 files changed, 149 insertions, 10 deletions**; no commits were made in this conversation. Branch history diverged at merge-base `24cd67f68703b6de2522409c14a7bffab1761e85`: `main` at `7fdd2cf` has one intervening commit affecting `ARCHITECTURE.md` and three Step 1.9 docs; Step 1.8 branch at `4be1b0b` changes `ARCHITECTURE.md` too, and the working-tree Step 1.9 packaging draft overlaps main. **Reconciliation is required for PR preparation; no rebase/merge performed.**

## 7. Remaining acceptance gates and scope boundaries

1. **Policy disposition:** the maintainer approved Version 1
   controller return even after a configured preferred focus target.
   The competing-manual-activation veto remains unproved and is
   documented as a limitation, not a verified feature.
2. **Docs and Git:** review the four-file worktree diff, reconcile `ARCHITECTURE.md` and Step 1.9 draft with `main`; update CLI/manual policy wording as necessary; verify final branch tests if behavior is changed.
3. **Maintainer-controlled transition:** only after review, accept, commit/push, prepare/review the PR, merge, close Step 1.8 and resume Step 1.9. `-L panel`, ebuild installed-image tests, KWin 6.8 migration, and broad RDP/VNC reacceptance are not Step 1.8 prerequisites.

**Evidence limits:** the screenshot is supplied by the maintainer; review it and the raw logs for host-specific or private details before publication. An isolated older desktop-3 RDP attempt remained unresolved but was not attributed to the stacking change. Do not infer remote session authentication/health from a locally successful managed viewer placement.
