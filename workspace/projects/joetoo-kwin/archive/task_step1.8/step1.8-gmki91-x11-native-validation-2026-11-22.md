# Step 1.8 — gmki91 native X11 `-L` validation and focus observation

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22, evening EST. **Host:** `gmki91` (Gentoo, GMKtec NucBox M3 PLUS). **Source baseline:** `task/joetoo-kwin-step1.8-cli-completion` at maintainer-pushed `5ab6ea6`, clean checkout. **Native compositor:** Plasma 6.7.6 with `kwin_x11` / `kde-plasma/kwin-x11-6.7.6`. Maintainer-operated observations and transcripts; **Step 1.8 not yet finally accepted or merged**.

`XDG_SESSION_TYPE=tty` and `loginctl Type=tty` describe the launching shell's login session on this host; they do **not** establish that Plasma is on Wayland. The running `/usr/bin/kwin_x11`, native `xprop -root` properties, and screenshots support the X11 compositor identification.

## Source, install, regression, and readiness

The maintainer ran `./tools/restart_joetoo-kwind test`: POC installation and subsequent `--check` passed, D-Bus introspection succeeded, and the daemon and resident were running. The **full post-repair regression suites passed**: **1,094/1,094 Python tests** and **169/169 JavaScript tests**. The initial broker snapshot was synchronized, `recovery=ready`, `initial_layout_protocol=1`, `single_lower_protocol=1`, `single_raise_protocol=1`, with **zero managed windows**, zero active/uncertain requests, and `placement_transaction.state=IDLE`. See the earlier maintainer-provided `restart_joetoo-kwind test` console output.

The root X11 pre-test state was `_NET_CURRENT_DESKTOP=0` (Plasma desktop 1) and `_NET_ACTIVE_WINDOW=0x4400008`. `ListObserved` included an unmanaged 64x36 `xwaylandvideobridge` on desktop 1; there were also ordinary Konsole peers, including an unmanaged Konsole on desktop 2.

## Native transactions

| ID / UUID | Invoked recipe | Observation and result |
| --- | --- | --- |
| `win-001` / `586887a9-e206-4d52-a28c-88795b012659` | `-L 2 konsole local btop under` | Target desktop 2 inactive; registered slot 1; frame `(96,32) 1804x972`; initial stacking/focus and overall launch **completed**. Maintainer visually saw new btop Konsole below an existing unmanaged Konsole. |
| `win-002` / `a8bbca7e-13b5-4693-949f-deabb5a12d38` | `-L 3 konsole local btop under` | Desktop 3 inactive; slot 1; managed registration, placement, initial stacking/focus, and overall launch **completed**. |
| `win-003` / `abbebec6-31da-419d-8609-ddd4cc3258fa` | `-L 3 vncviewer ssh ssh://joe@x401/display/2 under` | Desktop 3 inactive; slot 2; TigerVNC managed launch and initial stacking/focus **completed** beneath existing Konsole. Maintainer later resized Konsole manually to expose the VNC window in screenshot; that manual change is **after** native placement verification. |
| `win-004` / `b76db766-5697-4b13-a064-24e9dc1a4948` | `-L 3 sdl-freerdp rdp rdp://joe@opi6plus01 over` | Desktop 3 inactive; slot 3; local registration/initial stacking/focus **completed**. Screenshot shows a remote Ubuntu login screen; this is not proof of successful remote authentication. |
| `win-005` / `3a8b25ce-4131-4651-a54f-cc1a7ad731a2` | `-L 2 konsole local btop under` | **Desktop 2 displayed.** Pre-/post-`xprop`: `_NET_CURRENT_DESKTOP=1`, `_NET_ACTIVE_WINDOW=0x9a00008`. Slot 2 registered, placement `(96,32) 1804x972`, initial stacking/focus and overall launch **completed**. Maintainer watched the new Konsole appear above the windows and then move underneath them. This tests the active-desktop lower operation, not just the inactive-peer fallback. |
| `win-006` / `1080ec6a-c85a-40ba-91d3-4b74dc66e5b0` | `-L 2 konsole local btop` | **Invoked from desktop 1**, target desktop 2 inactive. Omitted fifth argument selected `over`; slot 3 registered, placement and initial stacking/focus **completed**. Maintainer visually confirmed the new btop Konsole above ordinary desktop-2 windows. |

All six IDs appeared `present`, `placement=succeeded` in the managed listing after the last launch. For the first four operations, the recorded X11 desktop and EWMH active window remained `0` / `0x4400008` at observed checkpoints. This supports no final desktop/focus-window switch; it does not continuously prove the absence of transient focus events. The broker verifies the operation's specific stack/geometry and UUID evidence, which is distinct from independent window-manager instrumentation.

## Rejected requests and final broker state

`-L 1 konsole local btop panel` was rejected as unsupported; `-L 1 konsole local __joetoo_test_absent__ under` was rejected because the local executable was unavailable. Before and after these attempts, `-l` showed the same four managed records and no extra managed launch. The preceding four-run status was 4/4 succeeded and no pending, failed, timeout, or ambiguous requests. After the displayed-desktop and omitted-layer tests, six records were shown; the final status snapshot for these last two launches was not supplied.

## Open X11 keyboard-focus observation — investigate before final acceptance

**Maintainer's repeatable visual/input report:** After each `joetoo-kwin -L` launch, including launches to an inactive desktop, the launching Konsole remains displayed on its original desktop, but its terminal cursor becomes **hollow** and it will **not accept another typed command until clicked**. The small desktop-pager previews visibly update as target windows are placed. The screenshots do not independently identify the X11 input-focus owner; the hollow-cursor and required-click observations come from the maintainer's direct report.

**Distinction:** `_NET_CURRENT_DESKTOP` describes the displayed virtual desktop; `_NET_ACTIVE_WINDOW` is KWin's EWMH active-window report; `XGetInputFocus`/actual Konsole terminal keyboard focus is an independent observation. In the displayed-desktop `win-005` test, `_NET_ACTIVE_WINDOW` matched before and after, **but** the maintainer's required-click observation contradicts claiming preserved usable terminal input focus. The X11 keyboard-focus owner was **not captured** before and after the launch. Do not assert a cause or mark the focus-preservation aspect accepted yet.

**Follow-up probe completed:** A subsequent inactive-target `-L 2 ... under` test recorded desktop 1 displayed (`_NET_CURRENT_DESKTOP=0`) but `_NET_ACTIVE_WINDOW` changing `0x4400008` → `0x0`, and actual X11 input focus changing `0x4400008` → `0x1800007`. A separate test successfully restored original control-window focus using guarded experimental `xdotool windowactivate`, verified immediately and one second later. `-o` also visibly reproduced the hollow terminal cursor; a similar Wayland symptom is maintainer-reported, not instrumented. These new findings are recorded with exact transcripts and limitations in [the launch-control focus evidence](step1.8-launch-control-focus-evidence-2026-11-22.md). No focus-restoration product code has been authorized or changed; the verified stacking evidence remains positive.

**Acceptance classification:** Native X11 window registration, placement, active/inactive `under` ordering, explicit/omitted `over`, VNC/RDP local adapters, and pre-launch refusal are **positive**. Keyboard-focus fidelity remains **open**. The output does not independently map the entire EWMH stack to each UUID/property; compositor/broker post-operation checks and maintainer visual inspection are separate evidence. Do not imply that `-L` provides persistent KeepBelow or that a remote login was proven.

## Evidence retained

- Maintainer raw `script` file (ANSI/control sequences preserved): `step1.8-gmki91-x11-native-console-2026-11-22.txt`; review for sensitive terminal output before publication. This was recorded for the initial four transactions and refusal cases.
- The displayed-desktop `win-005`, omitted-`over` `win-006` output, and focus report were provided in the subsequent conversation and are captured above; they were **not** in the original raw `script` session.
- [X11 desktop 2 under first native view](screenshots/20261122-gmki91-x11-under-inactive-konsole.png)
- [X11 desktop 3 VNC under Konsole](screenshots/20261122-gmki91-x11-vnc-under.png)
- [X11 desktop 3 SDL FreeRDP over at Ubuntu login](screenshots/20261122-gmki91-x11-rdp-over.png)
- [X11 desktop 2 omitted-layer `over` btop on top](screenshots/20261122-gmki91-x11-omitted-over-btop.png)

Do not infer a later tested state from any screenshot taken after manual window manipulation. The maintainer controls acceptance and cleanup of the six test windows.
