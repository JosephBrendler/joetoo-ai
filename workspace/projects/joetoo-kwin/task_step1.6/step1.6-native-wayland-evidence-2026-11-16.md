# Step 1.6 — Maintainer-native Wayland/XWayland close evidence (2026-11-16)

**Source/provenance:** selected terminal transcripts, screenshots and observations supplied by the maintainer in the 2026-11-16 collaboration. Not agent-executed tests; not a complete raw console archive. The screenshots remain in the conversation, not this public repository. No credentials or private session data are copied. **Step 1.6 is not yet fully accepted.**

**Host:** `q552u01`, Gentoo hardened/OpenRC, KWin/Plasma 6.7.6, `XDG_SESSION_TYPE=wayland`, joetoo-kwin 1.0.17. **Branch inspected:** `task/joetoo-kwin-step1.6-managed-close` in `JosephBrendler/joetoo-ai`. The precise commit corresponding to the maintainer's locally installed executable was not supplied; do not assert binary/commit equivalence.

## 1. Native adapter packaging and startup

The first installed module was `libjoetoo_managed_close.so`, but the embedded KPlugin ID was `joetoo_managed_close`. KPlugin reported their mismatch. The maintainer corrected `native/managed-close/CMakeLists.txt` with `set_target_properties(joetoo_managed_close PROPERTIES PREFIX "")`, removed `KPlugin.Id` from `metadata.json`, rebuilt and installed `/usr/lib64/qt6/plugins/kwin/effects/plugins/joetoo_managed_close.so`, and removed the old unloaded filename. The pushed branch contains these corrections.

`ldd -r` showed no missing libraries/undefined symbols. The plugin contained the expected KWin factory ID `org.kde.kwin.EffectPluginFactory6.7.6`. It was discoverable but reported `isEffectSupported=false` in the *old* running compositor. After normal logout/login, the **fresh** KWin process reported:

```text
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.listOfEffects | grep joetoo
joetoo_managed_close
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.isEffectSupported joetoo_managed_close
true
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect joetoo_managed_close
true
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded joetoo_managed_close
true
```

Both `org.kde.KWin` and `org.joetoo.KWinCloseNative` returned unique D-Bus owner `:1.9`. The native interface exposed `Inspect`, `Close`, `Status`, `Terminal`. Stale plugin loading/cache in the older process is a reasonable **inference**, not a proved diagnosis. A KWin restart is required for reliable verification of a newly replaced effect in this observed setup.

After graphical relogin, the OpenRC *user* service was stopped. The maintainer ran `rc-service -U joetoo-kwind start`; status became `started`. `./tools/joetoo-kwind-install-poc --check` reported all deployed components current and OpenRC allowlist correct. The broker exposed `PrepareManagedClose`, `CommitManagedClose`, `ManagedCloseStatus` on `org.joetoo.KWinBridge`.

## 2. Mixed launch and managed-inventory observations

The maintainer launched nine initial windows via `-o` test configurations, then three via `-L`:

| IDs | Desktop/slot | Local window | Outcome and limits |
| --- | --- | --- | --- |
| `win-001`, `win-004` | 4/1, 4/4 | Dolphin | Positive registration/placement |
| `win-002`, `win-003` | 4/2, 4/3 | Konsole | Positive registration/placement |
| `win-005` | 2/1 | Konsole | Positive registration/placement |
| `win-006`, `win-007` | 11/1, 11/2 | SDL FreeRDP | Local registration/placement; remote authentication marked `unverified` |
| `win-008` | 3/1 | TigerVNC viewer | Local registration/placement; VNC authentication/usability unverified |
| `win-009` | 3/2 | Dolphin | Positive registration/placement |
| `win-010` | 3/3 | TigerVNC viewer | Positive registration/placement |
| `win-011`, `win-012` | 2/2, 2/3 | Konsole | Managed terminals; see unsaved-work caveat |

Representative reports: `Configured layout: [5/5] ... [ ✅ ]`, `[2/2] ... [ ✅ ]`, VNC `[2/2] ... [ ✅ ]`, and a later `-L` VNC `[1/1] ... [ ✅ ]`. These verify local windows, not remote connection success.

## 3. `-d` cancellation, verified close, repeat exclusion

Declined example:

```text
./joetoo-kwin -d win-001
win-001 desktop=4 slot=1 UUID=ceec60a0-9a71-477d-9306-450700f2696e
Retained close result: 57b3bc4647b94212a16ac70491a3f290
Do you want to continue? [Y/n]: n
Negative response from user; quitting
```

A subsequent `-l` showed all nine records `present`. A confirmed repeat for `win-001` returned:

```json
{
  "state": "succeeded", "reason": "verified",
  "registration_retained": true, "reservations_retained": true,
  "request_id": "de3feb9bc2ef46bda4781adb1b133396",
  "targets": [{"managed_id":"win-001","backend":"wayland",
    "desktop":4,"slot":1,"state":"closed",
    "window_uuid":"ceec60a0-9a71-477d-9306-450700f2696e"}]
}
```

A separate `ManagedCloseStatus(de3feb9bc2ef46bda4781adb1b133396)` query returned the successful verified result. `-l` retained the same managed ID, desktop 4 / slot 1 and UUID, but with `PRESENCE=missing`, as specified for **`-d`**. An attempted *second* `-d win-001` excluded this missing target, returned no targets with `partial`/`incomplete`, and did not close another window.

Further confirmed cases:

| ID | Local application | Reported backend | Outcome |
| --- | --- | --- | --- |
| `win-005` | Konsole | `wayland` | `succeeded`, target `closed`, visually absent |
| `win-006` | SDL FreeRDP viewer | `wayland` | `succeeded`, target `closed`, visually absent |
| `win-008` | TigerVNC viewer | `x11` (XWayland) | `succeeded`, target `closed`, visually absent |
| `win-011` | Konsole running Nano | `wayland` | Konsole closed, **not** a direct Nano refusal test |
| `win-012` | Konsole launching Kate | `wayland` | Konsole closed; unmanaged Kate remained open |

TigerVNC example:

```json
{"state":"succeeded","reason":"verified","registration_retained":true,
 "reservations_retained":true,"targets":[{"managed_id":"win-008",
 "backend":"x11","desktop":3,"slot":1,"state":"closed",
 "window_uuid":"d2d12e4e-ba2d-47bc-95bb-aa43b4b9125e"}]}
```

This is positive native-close evidence for both **local Wayland and local XWayland clients** under KWin Wayland; it does not establish a native X11 compositor test, downstream worker cleanup or remote connection termination.

## 4. Bulk `-x`: six closes verified, twelve reservations retained

At the start of the confirmed `./joetoo-kwin -x` there were **12 managed records: six present and six already missing**. The preview selected six targets (`win-009`, `win-010`, `win-002`, `win-003`, `win-004`, `win-007`) and excluded six earlier missing IDs (`win-005`, `win-011`, `win-012`, `win-008`, `win-001`, `win-006`). The maintainer answered `y`.

Selected excerpt of the returned JSON (original also included UUIDs, request IDs and exclusion reasons):

```json
{
  "state": "partial", "reason": "incomplete",
  "registration_retained": true, "reservations_retained": true,
  "targets": [
    {"managed_id":"win-009","backend":"wayland","state":"closed"},
    {"managed_id":"win-010","backend":"x11","state":"closed"},
    {"managed_id":"win-002","backend":"wayland","state":"closed"},
    {"managed_id":"win-003","backend":"wayland","state":"closed"},
    {"managed_id":"win-004","backend":"wayland","state":"closed"},
    {"managed_id":"win-007","backend":"wayland","state":"closed"}
  ],
  "excluded": [
    {"managed_id":"win-005","presence":"missing"},
    {"managed_id":"win-011","presence":"missing"},
    {"managed_id":"win-012","presence":"missing"},
    {"managed_id":"win-008","presence":"missing"},
    {"managed_id":"win-001","presence":"missing"},
    {"managed_id":"win-006","presence":"missing"}
  ]
}
```

**Observed:** 6/6 eligible exact windows reported `closed`. The *aggregate* `partial` was caused by previously missing exclusions, not a verified-close failure. Afterwards `./joetoo-kwin -l` still printed **all twelve** records with `PRESENCE=missing`; none of their reservations were retired. The maintainer then ran `rc-service -U joetoo-kwind restart`, after which `-l` printed:

```text
No managed windows (no retained managed reservations).
```

This demonstrates an **in-memory reset workaround only**. Restart would be inappropriate as a generic sweep if windows or unresolved operations were still active, and it loses retained operation results.

**Accepted refinement (2026-11-16):** `-x` is a *progressive clean sweep*, **not bulk `-d`**. After a single confirmation, iterate the fixed managed set. For each positively absent/missing record, immediately retire its registration/reservation. For each positively present target, gracefully close, then retire its record/reservation **as soon as that exact close is verified**. Flag a failed/uncertain entry and retain only the minimum safe unresolved residue, while continuing other independently safe entries; do not delay successful retirement until all outcomes are known. Never guess identity, force-kill or erase genuinely uncertain native cleanup/ownership. A fully verified sweep ends with empty `-l` **without** broker restart. Preserve a bounded independent close-result history. `-d` still retains its record; `-D` close-and-retire is **version 2**.

Current source `libexec/joetoo_kwin_managed_close.py` retains registrations by design (sets `presence=missing`; reports retention flags `true`; overall success requires no excluded records). The code needs a **narrow** registry-lifecycle/result-reporting correction. This is Step 1.6's first outstanding implementation task.

## 5. TigerVNC / FLTK / local XWayland explanation

`q552u01` runs `XDG_SESSION_TYPE=wayland`; remote `x401` reported `XDG_SESSION_TYPE=x11`. That remote type **does not** determine the `backend` field. The field identifies the **local** window's native protocol under KWin. `./joetoo-kwin -L 3 vncviewer ssh ssh://joe@x401/display/2` did not specify an X11 backend, and the VNC launch code had no listed `FLTK_BACKEND`, `GDK_BACKEND`, `QT_QPA_PLATFORM` or `WAYLAND_DISPLAY` override.

The maintainer found installed `net-misc/tigervnc-1.16.2` with `server viewer wayland` USE and installed `x11-libs/fltk-1.3.8`. `ldd /usr/bin/vncviewer` showed `libfltk_images.so.1.3`, `libfltk.so.1.3` and `libX11.so.6`; Portage conflict output explicitly said the stable installed TigerVNC requires **`<x11-libs/fltk-1.4:1`**, blocking an FLTK 1.4.5 upgrade. FLTK 1.4 offers native Wayland, but the **installed viewer is FLTK 1.3/X11**, therefore XWayland on the local Wayland compositor. TigerVNC's `USE=wayland` does not automatically convert its viewer. The FLTK migration and Portage dependency are separate from Step 1.6; no rebuild was attempted for this test.

## 6. Limits and unfinished acceptance

The screenshot showed a modified Nano buffer **inside** managed Konsole `win-011`; `-d win-011` closed the Konsole without a Nano save prompt. This does not prove forced termination and **does not test a top-level application's native close refusal**. `-L 2 konsole local kate` registered a Konsole as `win-012`, while Kate opened separately on desktop 1 as an unmanaged window; `-d win-012` closed Konsole and left Kate open. Direct `-L 2 kate local ...` was rejected by the fixed launcher program allowlist. A true top-level unsaved-document/refusal test remains pending.

Remaining tests: updated `-x` retirement/partial/uncertain paths; `-x` self-terminal and CLI-loss continuation; RDP/VNC/SSH worker and remote tmux cleanup checks; direct application refusal without force; native **X11 compositor** on `slim2` (optional `gmki91`), XID reuse/lifetime-fence and unsupported `WM_DELETE_WINDOW` rejection; relevant regression suite and final maintainer acceptance. Earlier headless Codex results (999 Python with 998 PASS/1 SKIP; 163 JS PASS) are **pre-refinement**, not tests of the new `-x` behavior.

**Conclusion:** strong positive native close evidence for Wayland/XWayland, a separately documented `-x` lifecycle discrepancy and a focused accepted refinement. No claim of full Step 1.6 acceptance, native X11 coverage, restored remote sessions or packaging publication.
