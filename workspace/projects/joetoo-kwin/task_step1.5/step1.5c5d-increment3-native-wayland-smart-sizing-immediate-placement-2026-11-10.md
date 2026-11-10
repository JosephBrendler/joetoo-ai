# Step 1.5c.5d / Increment 3 — Native Wayland smart sizing and immediate-placement evidence (2026-11-10)

**Status:** Maintainer-run native Wayland **single-run immediate-placement success**, following separately successful manual and direct-KWin tests. This is evidence for a working *serial* SDL FreeRDP registration/placement path. It is **not** automatic configured `-o` acceptance, multi-run reliability, X11 smart-sizing regression acceptance, remote-session/security validation or Option D concurrency authorization.

## Provenance and tested environment

- Repository: `JosephBrendler/joetoo-ai`; branch `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`.
- Revisions: `df01e0c` — serial placement lifecycle consolidation; `54df85f` — maintainer's `/size:1024x768` and `/smart-sizing:800x600` development-launch arguments and tests; `599f7f38d141b2b332ca52f0daf4c7ce3c8ead43` — Codex's maintainer-only immediate-placement harness, its tests and small launcher/release-tool hooks. All were reported pushed and fast-forward synchronized by the maintainer.
- Client: `q552u01`, Gentoo, KDE Plasma/KWin **native Wayland**, SDL3 FreeRDP. Server: a GNOME Remote Desktop **system Remote Login** instance; its hostname, usernames, certificates, credentials and unfiltered client logs are deliberately omitted from this public evidence.
- Testing was performed by the **maintainer**, not the AI agent. All elapsed timing below is the experiment harness's monotonic clock unless otherwise stated. KWin and broker terminal readbacks do **not** measure physical on-screen frame commit time.
- Earlier failing placement with original 1024×796 frame: see [2026-11-09 controlled broker trace](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md). That historical failure remains valid evidence, not the current successful outcome.

## 1. Smart-sizing isolation: local viewer can scale and KWin can resize it

A **standalone**, unmanaged native-Wayland SDL FreeRDP invocation used these tested client flags:

```text
/size:1024x768
/smart-sizing:800x600
```

The maintainer observed: the entire remote GNOME desktop was visible; interactively dragging a window corner resized the local viewer and scaled content; pointer/buttons remained correctly aligned; manual window movement was immediate. A read-only KWin script then measured one SDL client as frame `(x≈563.10,y≈133.48) 914×647`, client/buffer `914×619`, `resizeable=true`, `fullscreen=false`. After a further manual resize, an independent KWin move/resize probe reported a pre-assignment **outer** frame `(563.1003609614224,133.47896159537308) 1063×814` and requested `(100,100) 800×628`.

The setter returned with **stale immediate readback**, but a subsequent independent read-only KWin script reported exactly:

```json
{"uuid":"{55f6e98a-327d-4faa-a448-a493d0664b78}","pid":2032437,"frame":{"x":100,"y":100,"width":800,"height":628},"client":{"x":100,"y":128,"width":800,"height":600},"buffer":{"x":100,"y":128,"width":800,"height":600},"resizeable":true,"fullscreen":false}
```

Thus the **existing KWin `frameGeometry` setter** achieved the requested outer frame with this scaled viewer. This direct KWin script was not a broker-managed placement test.

Before smart sizing, the maintainer's direct probe of the earlier native SDL viewer confirmed that resize-only `(300,160) 800×600` returned immediately but stayed `(300,160) 1024×796` in later reads; a combined `(1,1) 800×600` request moved the viewer to `(1,1)` while its size stayed `1024×796`. Those probes show that immediate setter readback and subsequent geometry differ; they **do not prove** that black content or GNOME GDM caused the earlier broker timeout.

## 2. Development launcher change and headless checks

At `54df85f`, the maintainer changed only `libexec/joetoo_kwin_rdp_launch.py` and `tests/test_rdp_launch.py` to pass the two fixed **development-only** FreeRDP flags above and assert their presence. The focused native-host headless tests passed:

```text
Ran 42 tests in 0.199s — OK  (test_rdp_launch.py)
Ran 37 tests in 0.864s — OK  (test_rdp_development_launcher.py)
git diff --check — clean
```

`54df85f` was signed and pushed; these values are **not** yet a configurable `-o` resolution/geometry policy. `599f7f3` subsequently added `tools/joetoo-sdl-immediate-placement.py` and `tests/test_rdp_immediate_placement.py`, with small edits to the registration and release tools. The maintainer's `./tools/restart_joetoo-kwind t` on `q552u01` reported installed components current, D-Bus introspection success, **789 Python tests PASS** (`Ran 789 tests in 94.058s`) and **161 JavaScript tests PASS** (`pass 161`, `fail 0`). These are the reported full suites for this revision.

## 3. Interim managed results, limitations and recovered errors

- With both FreeRDP flags confirmed in the **actual child process** (`/proc/<pid>/cmdline`), one early managed request of `(100,100) 800×628` still returned `placement=failed`, reason `Placement geometry confirmation timed out` at ~15 s. The viewer's broker observation remained `(448,119) 1024×796`. The viewer initially displayed black rather than GDM. The FreeRDP private log showed a server-redirection PDU alongside `ERRCONNECT_CONNECT_TRANSPORT_FAILED`; the cause of black content and the geometry failure in that run was **not** established.
- The maintainer rebooted the GNOME server, relaunched, manually resized to reveal GDM and then obtained `placement=succeeded, reason=verified` for `(100,100) 800×628`. Later, a separate manually issued managed placement to `(1,1) 800×628` also reported `succeeded/verified`. The observer reported that the viewer could move while **still black**, with GDM appearing afterward. These results refute an asserted need to wait for GDM appearance; they do not identify the cause of the earlier failing run.
- Diagnostic visibility: a prior OpenRC broker instance had `/proc/<broker>/fd/2 -> /dev/null`; the previous diagnostic log file was stale. The success harness **did not supply** `--broker-diagnostic-log`, so its `broker_evidence` correctly reports `status=unavailable`, `reason=diagnostic_log_not_supplied`. No internal broker assignment timestamp is asserted for this successful run.
- **Same-slot repeat blocker:** after closing a managed viewer, `ListManaged` still showed `win-001`, `presence=missing`, `placement=succeeded`, intended `(desktop=1,slot=1)`. Source inspection confirmed `_begin_rdp_registration()` rejects a second registration for the same desktop/slot **without checking `presence`**. The first immediate-harness attempt emitted only `evidence_directory` and then `FAILED: RuntimeError`, without a `child_pid`; this is consistent with the reserved-slot conflict, though the harness did not expose the underlying rejection. The maintainer restarted the user OpenRC broker; immediate D-Bus queries briefly reported `Service ... does not exist`, but a later read-only check confirmed live PID, `managed_count=0`, observation `synchronized=true`, placement transaction `IDLE`, no pending/running requests and `viewer_cleanup_uncertain=false`. Only then was the successful immediate test run. No reliable broker-ready wait was measured.

## 4. The decisive automatic immediate-placement native Wayland run

**Baseline:** `599f7f3`; tested by the maintainer on `q552u01` with a clean, synchronized broker. A fresh single viewer was launched by `tools/joetoo-sdl-immediate-placement.py`, requesting desktop 1 / slot 1 and *outer frame* `(x=1,y=1,width=800,height=628)`. No manual move/resize, arbitrary delay, or GDM-content readiness gate was used.

Command form (endpoint/user intentionally omitted):

```bash
python3 tools/joetoo-sdl-immediate-placement.py \
  --confirm-immediate-placement \
  --desktop 1 --slot 1 \
  --x 1 --y 1 --width 800 --height 628 \
  --rdp-backend-log-byte-limit 262144 \
  <RDP_HOST> <RDP_USERNAME>
# End of commands
```

**Identity:** launched child PID `2099214`; registration request `fe1973443c814d0ea77371f3d0a57490`; managed ID `win-001`; exact KWin UUID `da0a37a4-aed1-4a43-b738-b10a37c87775`; placement request `708bc4dcd635445d9af77be7fe8ca621`. Both registration and placement returned that **same UUID**. All UUIDs and request IDs here are non-secret, ephemeral test identifiers.

| Harness stage | Since launch (ms) | Since registration (ms) | Meaning |
| --- | ---: | ---: | --- |
| Local SDL child spawned | 9.906 | — | PID obtained |
| `registered` | 11,402.590 | 0 | Broker positively identified exact viewer; includes time spent connecting/authenticating before this event |
| `placement_submission` | 11,409.017 | **6.430** | Harness initiated placement without GDM readiness wait |
| `placement_accepted` | 11,416.036 | **13.446** | Broker accepted UUID-bound request |
| Local shortcut dispatch / return | ~11 / ~12 after release-tool start | — | Separate release-tool elapsed-clock basis, not compositor timing |
| `placement_terminal` | 11,518.748 | **116.159** | `placement=succeeded`, `reason=verified` |
| `experiment_result` | 11,520.756 | **118.167** | Independent broker `GetManaged` snapshot matched target |

Calculated from monotonic values: submission → verified terminal **109.731 ms**, and registration → verified terminal **116.159 ms**. The elapsed times include D-Bus, polling and observation; not a direct benchmark of KWin's setter execution. The ~11.4 s from process start to positive registration must **not** be described as placement latency.

**Terminal and read-only result (exact salient fields):**

```json
{"managed_id":"win-001","placement":"succeeded","protocol":1,"reason":"verified","registration":"registered","remote_session":"unverified","request_id":"708bc4dcd635445d9af77be7fe8ca621","window_uuid":"da0a37a4-aed1-4a43-b738-b10a37c87775"}
{"presence":"present","placement":"succeeded","window_uuid":"da0a37a4-aed1-4a43-b738-b10a37c87775","desktops":[1],"on_all_desktops":false,"geometry":{"x":1,"y":1,"width":800,"height":628}}
```

**Visual maintainer observation:** the window moved to `(1,1)` promptly following NLA authentication while its contents were still black; the GDM greeter appeared a couple of seconds later, **inside the already placed window**. GDM visibility is not an established prerequisite for KWin placement. This observation is visual, not a machine-timestamped GDM event.

The launcher continued foreground supervision after the placement result. It separately emitted its original `state=registered`, `placement=not_requested` record; this refers to the **registration-only launcher contract** and must not be confused with the harness's independent `placement=succeeded` transaction. The harness reported `supervision=continuing_under_original_launcher`. No final viewer-exit or later process-reap record was supplied for this particular run, so we do not assert native teardown acceptance from it.

[Normalized combined stdout/stderr trace for this run](step1.5c5d-increment3-immediate-placement-transcript-2026-11-10.log) preserves the supplied JSON values and ordering without terminal wrapping. The maintainer also supplied screenshots of the GDM viewer near the upper-left; images are **not** committed here because they display portions of a personal desktop and other applications.

## 5. Conclusions, open validation and next gates

**Demonstrated:** at `599f7f3`, one fresh native-Wayland managed SDL FreeRDP viewer was positively registered, then automatically submitted for placement **6.43 ms later**; the existing broker/KWin path verified exact desired desktop and full frame **116.16 ms after registration**, without a user-initiated geometry change or wait for remote GDM rendering. Earlier direct-KWin and manual managed experiments corroborate that smart sizing permits local frame resizing while retaining a usable full remote desktop.

Selected [earlier probe, failure, manual placement, and broker preflight excerpts](step1.5c5d-increment3-smart-sizing-probe-excerpts-2026-11-10.log) are also retained separately from the decisive immediate-run transcript.

**Not yet demonstrated:** repeated clean-launch reliability; a successful *second* same-slot immediate harness without clearing historical registry; native X11 regression after adding smart sizing to the shared launcher; automatic `-o` recipe integration, stacking of RDP `under` relative to panels/overs, config-driven window/remote-resolution policy, production TLS/server identity, reliable remote-login state, or safe long interactive-authentication waits. One earlier 15-second geometry failure remains real and its particular cause unproven. The trace's internal broker timing was unavailable for the success run. **No GDM-content readiness delay or KWin geometry rewrite is justified by these findings.**

**Proposed next actions (maintainer approval required for implementation/native operations):**

1. Consider two additional fresh native-Wayland immediate-placement runs and a focused X11 smart-sizing regression; arrange a clean slot/registry and verify the broker's D-Bus readiness before each same-slot test. Treat any failure as data; do not silently lengthen timeouts.
2. Independently scope safe missing-window slot release/explicit cleanup and actionable preflight/error reporting. Do not solve it by class/PID-only adoption or by automatically discarding uncertain ownership.
3. After native acceptance decision, design bounded **Increment 4** configured serial `-o` RDP launch using the existing registration/placement transaction and planner's graphical-region geometry/underlay stack. Replace development-only fixed sizing with validated, configurable local scaling and remote-resolution policy. Preserve TigerVNC, X11/Wayland, original operator controls, strict UUID correlation, remote-authentication separation and human-interactive wait semantics.
4. Keep Option D concurrency and remote-session/TLS security closeout deferred to their separate gates. See [active HANDOFF](HANDOFF.md), [task README](README.md) and [strategy decision](step1.5c5d-increment3-strategy-decision.md).
