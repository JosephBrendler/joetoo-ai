# Step 1.6 — slim2 native X11 acceptance evidence (2026-11-17–18)

**Status:** Maintainer-executed native evidence, **accepted for Step 1.6 by the maintainer on 2026-11-18** with the explicitly listed coverage limitations. The established positive-path behavior passed; no blocking code defect was demonstrated. This record supplements, rather than rewrites, the [2026-11-16 q552u01 Wayland/XWayland progressive-sweep record](step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md) and [original Wayland record](step1.6-native-wayland-evidence-2026-11-16.md).

**Source baseline for the native tests:** `task/joetoo-kwin-step1.6-managed-close` at `c57ab8cb4a6af5c770aa281b0dcfed295b709bae` on `slim2`. Commit `c57ab8c` updated the restart helper's TMPDIR selection; the preceding `8849e59` and uncommitted `f26027a` records describe earlier development, not outstanding changes. Following these tests, the maintainer synchronized `q552u01`, pushed the evidence and originals, and accepted Step 1.6; the task branch was inspected at `65e4e6be1af7eb94a472f86c08372874e5236b43` for this documentation pass. No source was changed in order to obtain the native test observations.

## 1. Host and build boundary

- **Host:** `slim2`, Gentoo hardened, OpenRC, split-usr; `XDG_SESSION_TYPE=x11`; running `kwin_x11` / Plasma **6.7.6**; physical display **1366x768**.
- **SDK:** `/usr/lib64/cmake/KWinX11/{KWinX11Config.cmake,KWinX11ConfigVersion.cmake,KWinX11Targets.cmake}` present. Build uses `JOETOO_KWIN_X11:BOOL=ON` and `CMAKE_INSTALL_PREFIX:PATH=/usr`.
- **Compiled products:** `/tmp/joetoo-close-x11/joetoo_managed_close.so` and `/tmp/joetoo-close-x11/joetoo-kwin-close-x11`. The plugin was a valid ELF shared object with a `NEEDED` dependency on `libkwin-x11.so.6`; on an executable temporary filesystem, `ldd -r` reported no missing libraries or undefined symbols.
- **Installation (maintainer):** `/usr/lib64/qt6/plugins/kwin-x11/effects/plugins/joetoo_managed_close.so` and `/usr/libexec/joetoo-kwin-close-x11` via `sudo cmake --install /tmp/joetoo-close-x11`. `listOfEffects` found the effect, `isEffectSupported` returned `true`, `loadEffect` and `isEffectLoaded` returned `true`. Unique D-Bus owners of `org.kde.KWin` and `org.joetoo.KWinCloseNative` matched (`:1.13` in the first session, `:1.11` after reboot/reload). Native `Close`, `Inspect`, `Status`, and `Terminal` methods were introspected.
- **Broker:** `rc-service -U joetoo-kwind status` was `started`; `./tools/joetoo-kwind-install-poc --check` reported all 12 user-owned files `Current`; `RegistryStatus` reported `managed_close_protocol: 1`, `managed_close_active: false`, `observation.synchronized: true`, and initially `managed_count: 0`.

### Environment issue found and resolved

`slim2` mounts `/tmp` as `nodev,nosuid,noexec`, whereas `/var/tmp` is executable. The original Python test run with its temporary executable stubs under `/tmp` failed **80 assertions and 63 errors**, inadvertently launching real Konsole/Dolphin windows and leaving a test-spawned Konsole with `HOME=/tmp/tmpuvnq2hxy/home`. This was a test-environment failure, not evidence of managed-close regression. The `ldd` check from `/tmp` likewise could not execute the plugin. The isolated inventory and X11 RDP diagnostic tests both passed when `TMPDIR=/var/tmp`; after moving to a normal shell (`HOME=/home/joe`) and using the executable temporary location, the full test suite passed.

**Clean-shell maintainer reruns:** First, `TMPDIR=/var/tmp ./tools/restart_joetoo-kwind` returned **Ran 1016 Python tests ... OK**, **163/163 JavaScript passed**, and installer check PASS. The maintainer then ran the updated `./tools/restart_joetoo-kwind` on **2026-11-18 without a command-line TMPDIR prefix**; the supplied original log again shows **Ran 1016 tests in 217.508s / OK**, **163 JS PASS**, correct `/home/joe` installer paths and service start. The three grouped-launch failures seen in the contaminated test-spawned shell did not recur in these clean runs. Commit `c57ab8c` adjusts the restart helper's TMPDIR handling; its source diff was not separately audited in this record. No production change to the native effect or managed-close logic was made as a result of the temporary-filesystem issue.

## 2. Positive-path X11 integration and exact results

### Configured launch / layout regression

A maintainer `./joetoo-kwin -vv -o` run with `screen_width=1366`, `screen_height=768` launched **15/15 managed Konsole SSH placeholders** in five groups (desktops **5, 4, 6, 7, 8**, three windows each). All five initial stacking/focus groups completed successfully. The screenshots show expected three-window geometry. Some Konsoles were paused at SSH key-passphrase prompts; this is **not** evidence of successful remote authentication or remote process cleanup. Initial attempts with maximized Dolphin reported `maximizeMode=3` and failed the *separate* initial stacking/focus precondition; later nonmaximized launches completed. This transient was not a native-close failure.

### Selective `-d` retains registrations

The maintainer confirmed two independent native X11 selective closes:

| Command | Managed ID / original UUID | Close result | Retained operation ID |
| --- | --- | --- | --- |
| `./joetoo-kwin -d win-001` | `win-001` / `281dc4d7-5a88-4193-8f19-f805ffc7111a` | `state=succeeded`, `reason=verified`, `backend=x11`, target `state=closed`; both retention flags `true` | `3b8b0e66d0ed4cd99211a9425385daa9` |
| `./joetoo-kwin -d win-002` | `win-002` / `14f4d166-3364-491e-aec8-66424a55c61f` | same successful/retained semantics | `c9b94d19ef594b259b4302532e510efd` |

Immediately afterward, `./joetoo-kwin -l` listed both original IDs as `missing` with their original desktop/slot reservations, alongside the 14 other `present` registrations.

### Confirmed progressive `-x` sweep — 16 / 16 verified retirements

**Maintainer command:** `./joetoo-kwin -x`, confirmed `y` from an unmanaged Konsole. **Retained request ID:** `0073db0a81794860bda46995edb4ce26`.

The preview included **two `action=retire_missing`** records followed by **14 `action=close`** records. Final reply, independently verified a second time using `ManagedCloseStatus(0073db0a81794860bda46995edb4ce26)`:

```json
{
  "protocol": 1,
  "request_id": "0073db0a81794860bda46995edb4ce26",
  "state": "succeeded",
  "reason": "verified",
  "excluded": [],
  "registration_retained": false,
  "reservations_retained": false,
  "self_terminal": "excluded"
}
```

The per-target result from the supplied full JSON is preserved below. All 16 entries returned `retired=true`; the two missing entries returned `state=already_missing` and the 14 live entries returned `state=closed`, `backend=x11`, `reason=verified`.

| Managed ID | Desktop / slot | Action / state | Original UUID |
| --- | --- | --- | --- |
| win-001 | 3 / 1 | retire_missing / already_missing | `281dc4d7-5a88-4193-8f19-f805ffc7111a` |
| win-002 | 5 / 1 | retire_missing / already_missing | `14f4d166-3364-491e-aec8-66424a55c61f` |
| win-005 | 4 / 1 | close / closed | `5161fc1d-30b3-48c1-a348-ecad57abc8fd` |
| win-006 | 4 / 2 | close / closed | `f110ef69-c360-49de-a4d9-2ccc83cabded` |
| win-007 | 4 / 3 | close / closed | `aa72896e-aec8-4afd-aa99-0c8a0d4b5880` |
| win-003 | 5 / 2 | close / closed | `3615b45f-f654-4d07-baa2-30a5499c4fff` |
| win-004 | 5 / 3 | close / closed | `432c6b01-c628-4433-9465-109f59e80191` |
| win-008 | 6 / 1 | close / closed | `d628ee2e-22f6-4a27-8060-98e9f4ef2eb0` |
| win-009 | 6 / 2 | close / closed | `e4279605-08ea-4370-9c8a-09578eea6caa` |
| win-010 | 6 / 3 | close / closed | `9de2741c-5fa4-46c6-8033-2de41e826348` |
| win-011 | 7 / 1 | close / closed | `819a3c80-b69d-4343-9fc5-6f81d67cde08` |
| win-012 | 7 / 2 | close / closed | `b9d447d8-5394-4bda-b6fb-3f9175ac604b` |
| win-013 | 7 / 3 | close / closed | `b25c9598-9fcc-42c1-9c2a-3956fac662cb` |
| win-014 | 8 / 1 | close / closed | `eba26ead-4413-4afb-8ca3-b12ad57af34e` |
| win-015 | 8 / 2 | close / closed | `eec7be23-2efe-44de-bc05-d07250001aaf` |
| win-016 | 8 / 3 | close / closed | `eb94bf05-289d-422f-8372-16a649194cf9` |

The immediate inventory, **without broker restart**, was:

```text
./joetoo-kwin -l
No managed windows (no retained managed reservations).
```

The later independent `ManagedCloseStatus` lookup returned the same completed, detailed 16-target history after the original CLI exited. This establishes retained in-memory status **without claiming broker-restart persistence**.

### Slot/ID reuse and declined confirmation

A subsequent new Dolphin on desktop 3 / slot 1 was registered as **`win-017`** (UUID `7a3d2a53-0be9-40ff-8c77-d76fa5b6aa29`), not recycled as `win-001`; registration/geometry/initial stacking/focus completed. The maintainer declined `-d win-017` with `n`; subsequent `-l` showed the **same UUID still `present`**. The maintainer also declined a separately previewed `-x` containing `win-017`; subsequent `-l` again showed `win-017 present`, unchanged. This is actual native decline evidence, not only a headless assertion.

## 3. Native X11 graceful-refusal and self-terminal observations

Two disposable managed local Konsoles (`-L 2 konsole local btop`) exercised actual application refusal:

1. `win-018` on desktop 2 / slot 1 (UUID `4e5b37ef-bb11-467e-ad0d-0c23f8aea34e`) launched successfully. The maintainer exited btop and invoked `./joetoo-kwin -d win-018` **inside that managed Konsole**, confirming `y`. Konsole raised its own dialog: **"There is a process running in this window. Do you still want to quit?"** The broker reported `state=partial`, `reason=incomplete`, `self_terminal=win-018`, and target `state=not_closed_timeout`, `backend=x11`; the window stayed open at timeout. The maintainer subsequently clicked **Close Window**, whereupon Konsole disappeared and the record later appeared `missing`. A late voluntary close did **not** become an earlier reported verified success. Screenshot `image(20261118-211052).png` shows the popup and result; subsequent desktop screenshot `image(20261118-211137).png` shows window gone.
2. `win-019` on desktop 2 / slot 2 (UUID `34cdd402-1abf-49c7-a182-ee52c1241a34`) was launched because `win-018` remained reserved as missing. Another confirmed `-d` from inside `win-019` raised Konsole's dialog; the maintainer chose **Cancel**. Broker result: `state=partial`, `reason=incomplete`, `self_terminal=win-019`, target `state=not_closed_timeout`; subsequent `-l` still showed `win-019 present`, `win-018 missing`, and `win-017 present`. Screenshot `image(20261118-211458).png` corroborates this.
3. The maintainer reported a similar popup/timeout when invoking `-x` from a managed Konsole. **No full `-x` request ID/result trace was supplied for that particular experiment.** The observation that a previously missing record was still listed referred to the earlier **`-d`**, which intentionally retains records; it was **not** evidence of an `-x` retirement defect. The maintainer subsequently reports `-x` from an unmanaged Konsole cleaned the remaining entries. The exact per-target statuses of that later cleanup were not supplied.

**Interpretation:** A supported application **can** refuse or defer an X11 graceful close. No forced process kill or unexpected registration retirement was observed in the shown `-d` refusal cases. The positive `-x` sweep independently proves progressive retirement for a mixed 2-missing/14-present snapshot. These experiments also prove native `self_terminal` identification, but **do not demonstrate that a broker job continues to successful completion after the invoking terminal actually exits mid-transaction**: in the shown cases, the close operation timed out before the user dismissed the Konsole dialog.

## 4. Coverage and remaining acceptance judgment

| Area | Evidence status | Assessment |
| --- | --- | --- |
| `-d` successful selective X11 close/retention | Two native verified results | **Passed** |
| `-x` mixed native progressive retirement | Two missing + 14 native X11 closes; 16/16 retired; empty `-l`; status survives frontend | **Passed** |
| Safe declined `-d` and `-x` | Maintainer responded `n`, `win-017` stayed present | **Passed** |
| True application refusal | Konsole popup; timeout without force; `-l` retained | **Passed** |
| Invoking managed-terminal identification | `self_terminal=win-018` and `win-019` | **Passed** |
| Invoking-terminal exits during **still-running** broker sweep | Not shown by the popup/timeout tests | **Not demonstrated; optional targeted native check if required** |
| Unsupported `WM_DELETE_WINDOW` and stale/reused XID in **live** compositor | Unit tests cover no-delete/no-GO/stale and XCB wire behavior; no dedicated live X11 fixture | **Unverified live safety edge; no observed fault** |
| Known-safe failure and **independent** successful retirement in same partial live `-x` | Headless tests cover continuation; live case not conclusively captured | **Unverified natively; not a demonstrated defect** |
| Local SSH process exit vs remote tmux persistence; RDP/VNC worker lifecycle | Application windows closed in positive sweep; independent worker/remote checks not captured | **Separate lifecycle coverage limitation** |
| Test harness portability to `noexec` `/tmp` | Workaround and clean rerun passed; `c57ab8c` fixes helper TMPDIR setting | **Host-specific fixture hazard resolved for operator workflow; optional further test-harness fail-fast hardening** |

**Disposition (maintainer decision, 2026-11-18):** Step 1.6 is **accepted**. No coding blocker was demonstrated. For strict compliance with every live-case item in `native/managed-close/README.md`, the untested live X11 unsupported-WM_DELETE / stale-XID fence and mid-transaction frontend-loss cases remain **evidence gaps**, not evidence of bugs. These remain recorded evidence limitations accepted for this milestone, not tests that have passed; any later real defect warrants a narrow corrective investigation. No speculative refactor, new stage, Portage update, or additional Codex round is justified by current output.

## 5. Maintainer acceptance and provenance

The maintainer accepted Step 1.6 on **2026-11-18** and reported synchronizing
`q552u01` with the published task branch and pushing subsequent documentation
and evidence updates. The earlier pre-sync `8849e59` versus `c57ab8c`
comparison in this test record is historical, not outstanding Git work.
The task-branch revision inspected for this documentation update is
`65e4e6be1af7eb94a472f86c08372874e5236b43`. Acceptance does not
assert that the task-branch PR has been opened or merged. See
[HANDOFF.md](HANDOFF.md) for the publication next action. The unverified
live-compositor safety edges in Section 4 remain explicitly documented,
without changing the maintainer's acceptance decision.

## 6. Supporting originals (maintainer-published)

The operator preserved primary captured material in this task directory:

- [Regression and OpenRC restart log](supporting-originals/slim2-2026-11-18-restart-regression.log)
  — source for the clean 1,016 Python / 163 JavaScript rerun, installer paths
  and broker restart. The earlier contaminated `/tmp` results are contextual,
  not replacement test evidence.
- [15-window launch log](supporting-originals/slim2-2026-11-18-15-window-launch.log)
  — source for the configured native-X11 multi-desktop launch and layout result.
- [Konsole confirmation dialog and timeout](supporting-originals/image%2820261118-211052%29.png)
  — visual evidence for the self-terminal `-d` refusal/deferred-close path.
- [Desktop after operator accepted Konsole's close dialog](supporting-originals/image%2820261118-211137%29.png)
  — evidence of subsequent voluntary window disappearance, not a prior verified
  broker success.
- [Konsole after operator canceled its close dialog](supporting-originals/image%2820261118-211458%29.png)
  — native `not_closed_timeout` with retained registration.

The screenshots supplement the command results; they do not by themselves
prove KWin's native lifetime fence, remote SSH authentication, or SSH/RDP/VNC
worker cleanup. The primary typed close/sweep JSON, including request
`0073db0a81794860bda46995edb4ce26`, is preserved in Section 2 above.
