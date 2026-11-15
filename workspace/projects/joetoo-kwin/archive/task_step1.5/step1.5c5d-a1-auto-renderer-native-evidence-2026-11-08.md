# Step 1.5c.5d / Increment 2 — native X11 default-renderer feasibility evidence (2026-11-08)

**Classification:** Maintainer-operated diagnostic evidence, **not** managed-registration acceptance. This run complements [`step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md`](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md). Do not commit private `.tbz2` archives or raw extracted logs. The original artifacts were supplied directly to the assistant on 2026-11-08; the keeper location after local relocation must be verified rather than presumed.

## Command and actual settings

```bash
env -u SDL_RENDER_DRIVER -u SDL_FRAMEBUFFER_ACCELERATION \
    RDP_DIAG_SECONDS=900 \
    ./tools/joetoo-rdp-diagnostic-run.sh \
    sdl-freerdp raspiubuntu401:3389 joe
```

Test host: `gmki91`, native KWin X11. Target: GNOME Remote Login on `raspiubuntu401:3389`. Diagnostic launched the *stock* SDL FreeRDP client, using the same eight plain-text phase prompts as the earlier software test. FreeRDP PID **914883**; exact launch marker `joetoo-rdp-proof-2aaf1650-70a8-4bdc-8859-403d956b8f60`. `client.log` confirms SDL video backend **`x11`** and renderer **`opengl`** three times. Neither renderer-forcing environment variable was supplied to this client invocation.

## KWin UUID / native XID lifecycle

*All lifespans below are observed KWin event timestamps, **not** native birth times or broker-local eligibility timestamps. Measurements are from added to removed events.*

| Sequence | KWin UUID | XID | Exact title marker | Observed KWin lifespan |
| --- | --- | --- | --- | ---: |
| Initial 64×64 window | `f79f8c72-ffc6-4db0-a3bd-837d1cc792e0` | `146800688` | No | **46 ms** |
| Additional initial 64×64 window | `074f0a35-c230-44f5-9337-f5b4d06f3c00` | `146800696` | No | **38 ms** |
| Credential-stage window | `df214074-67e1-437b-800e-91c7501dab91` | `146800710` | No | **27,894 ms** |
| Temporary marked 1024×768 window | `89da9a6a-f328-4497-a87a-6bb68226f690` | `146800721` | **Yes** | **22 ms** |
| Persistent marked 1024×768 viewer | `66aba172-f6e0-42aa-ba74-847c50e6654c` | `146800729` | **Yes** | **59,671 ms** |

The first marked window arrived at **13:20:32.657 EST**, was removed at **13:20:32.679**, and the replacement appeared at **13:20:32.686** (7 ms after removal). Both were normal KWin windows, with the same launch PID/class/exact marker. The persistent viewer remained until **13:21:32.357** when the maintainer closed it. The independent X11 ledger corroborates the native XID linkage, with monotonic observer discovery/removal for the temporary XID of ~32.5 ms; discovery is not a native creation timestamp.

The same phenomenon was observed in the earlier November 5 baseline (20 ms marked predecessor). Thus the original ambiguity **reproduced under ordinary OpenGL rendering**. A proposed 500 ms one-interval candidate-persistence selector would have separated these two marked windows **in this trace**; it remains an explicitly fallible heuristic, not an SDL initialization guarantee. Do not treat marker presence alone as sufficient.

## Phase results, coverage and limitations

All eight interactive prompts were answered yes. Maintainer's final statement: *“normal launch; same smooth move; minor tearing in redraw when resizing; still logged in - closed with X, not logout”*. FreeRDP returned **131** following `SDL_EVENT_WINDOW_CLOSE_REQUESTED` and log message `Window closed, terminating RDP session...`; do not represent this as a failed login or server logout. No quantitative frame-rate, CPU/GPU, 4K video or comparative performance measurements were made.

Diagnostic `receipt.json`: **331** records, `internal_capture_intact=true`, `transport_complete=true`, `sender_confirmed_end_ack=true`; `lifecycle_coverage=unassessed`. X11 `verification.json`: **6** native candidates, **5** discovery gaps, **1** unlinked, **0** unsupported, **2** use latches; `observation_completed_as_requested=true`. These limitations prevent any claim of exhaustive X11 coverage. The KWin observed five directly correlated UUIDs; the independent X11 ledger also saw a sixth short-lived candidate lacking UUID linkage. Neither the human phase report nor use-latch alone proves a specific KWin viewer-role identity.

**Earlier software-renderer comparison:** FreeRDP PID `842381`, SDL renderer `software`; initial unmarked window 86 ms, unmarked credential-stage window 28,761 ms, *one* exact-marked viewer 170,749 ms; X11 verifier one discovery gap. The software run was graphically usable with similar reported minor resize tearing. This comparison does **not** establish renderer causation or a measured performance differential.

## Private artifact names and SHA-256

| Artifact | SHA-256 |
| --- | --- |
| `joetoo-rdp-diagnostic.y8vCwR5i.tbz2` | `41061b61708573a23b3a1e6b05f898c5f2454049dd37b57c7d632423d9de6d6c` |
| `joetoo-rdp-stage-a.8R7xmIXt.tbz2` | `63a4e477ca4068214d5ff858744c377cbf5e5f28fffdcc49ad9e2aa5f50f9149` |
| `joetoo-rdp-diagnostic.M59ZAfaw.tbz2` | `75fb0499e2ff4f957f383f731b0361962089c1ab9abec448994e5a0c82ceac1e` |
| `joetoo-rdp-stage-a.EH56gC3b.tbz2` | `cddc168ba09a7aca13c4c1f075c45a7957289b5d5528ff8b95033252317ee9d9` |

The diagnostic captures are privacy-sensitive and should remain under the maintainer's private `~/.local/share/joetoo-ai/rdp-evidence/` store after the maintainer verifies relocation. Committing this Markdown summary is permitted; do **not** upload the actual `.tbz2` artifacts to the repository.

## Decision supported by evidence

Proceed with a **narrow native-X11 broker implementation** that supports child-local `rdp_x11_renderer=auto|software` and a **single** configurable broker-local `rdp_x11_identity_settle_ms=500` persistence selector for both choices. Prefer `auto` by default to retain the existing OpenGL path. Keep software rendering available as an explicit preference, not a guarantee against replacement. Preserve the accepted native-Wayland registration path and existing ownership/security gates. Broker implementation is **not yet native X11 acceptance**; native testing of the actual implemented registration path remains maintainer-operated and separately reviewed.

## Complete maintainer terminal transcript (verbatim submitted)

```text
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ cd ~/joetoo-ai/workspace/projects/joetoo-kwin
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ env -u SDL_RENDER_DRIVER -u SDL_FRAMEBUFFER_ACCELERATION \
    RDP_DIAG_SECONDS=900 \
    ./tools/joetoo-rdp-diagnostic-run.sh \
    sdl-freerdp raspiubuntu401:3389 joe
---[ gmki91 joetoo-rdp-diagnostic-run.sh-20261108 ]-------------------------------------------------------------
---[ joetoo-rdp-diagnostic-run.sh-20261108 (configuration) ]----------------------------------------------------
 * PN ..............................: [ joetoo-rdp-diagnostic-run.sh ]
 * BUILD ...........................: [ 20261108 ]
 * project_dir .....................: [ /home/joe/joetoo-ai/workspace/projects/joetoo-kwin ]
 * RDP_DIAG_SECONDS ................: [ 900 ]
 * RDP_DIAG_ACK_MS .................: [ 3000 ]
 * RDP_DIAG_LIVENESS_MS ............: [ 5000 ]
 * RDP_DIAG_MAX_RECORDS ............: [ 1024 ]
 * RDP_DIAG_MAX_TOTAL_BYTES ........: [ 16777216 ]
 * RDP_DIAG_EXPORT_MS ..............: [ 0 ]
 * RDP_DIAG_START_TIMEOUT_SECONDS ..: [ 15 ]
 * RDP_DIAG_READY_WAIT_MS ..........: [ 15000 ]
 * RDP_DIAG_DBUS_SECONDS ...........: [ 5 ]
 * RDP_DIAG_CLEANUP_MS .............: [ 5000 ]
 * RDP_DIAG_POLL_MS ................: [ 100 ]
 * RDP_DIAG_X11_USE ................: [ 0 ]
 * RDP_DIAG_X11_POLL_MS ............: [ 10 ]
 * RDP_DIAG_X11_ACK_MS .............: [ 3000 ]
 * RDP_DIAG_X11_MAX_CANDIDATES .....: [ 64 ]
 * RDP_DIAG_X11_MAX_CLIENTS ........: [ 512 ]
 * RDP_DIAG_X11_EVENT_LIMIT ........: [ 4096 ]
 ⚠ This maintainer-run procedure starts a real RDP client and opens KWin Debug Console.
 ✨ No managed enrollment or production-resident restart; viewer cleanup remains yours.

 ✨ Do you want to continue? [Y/n]: y                                                                           
 ✨ Affirmative response from user; continuing
 ✨ Check whether diagnostic is already loaded ✨ Check diagnostic load state result:                    [ ✅ ]
 ✨ Create private evidence directory
 ✨ Create private evidence directory result: (completed)                                                [ ✅ ]
 ✨ Capture directory: [/tmp/joetoo-rdp-diagnostic.y8vCwR5i]
 ✨ Start temporary receiver
 ✨ Start temporary receiver result: (completed)                                                         [ ✅ ]
 ✨ Verify receiver and pinned bus owner
{"failure": null, "internal_capture_intact": null, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": false, "observer": null, "protocol": 1, "ready_persisted": false, "receiver": ":1.28781", "records": 0, "run_id": "02b7a74ba65645a790f39757a21fddaa", "sender_confirmed_end_ack": false, "transport_complete": false}
 ✨ Verify receiver and pinned bus owner result: (completed)                                             [ ✅ ]
 ✨ Load standalone observer
 ✨ Load standalone observer result: (completed)                                                         [ ✅ ]
 ✨ Require persisted ready and active observation
{"failure": null, "internal_capture_intact": null, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": true, "observer": "rdp-diag-mw85qdoh-glpcssid27s5j6lg1dpknsph1907v0azbw64qrv841", "protocol": 1, "ready_persisted": true, "receiver": ":1.28781", "records": 1, "run_id": "02b7a74ba65645a790f39757a21fddaa", "sender_confirmed_end_ack": false, "transport_complete": false}
 ✨ Require persisted ready and active observation result: (completed)                                   [ ✅ ]
 ✨ Start X11 property observation
 ✨ Start X11 property observation result: (completed)                                                   [ ✅ ]
 ✨ Wait for private X11 linker script
 ✨ Wait for private X11 linker script result: (completed)                                               [ ✅ ]
 ✨ Load isolated X11 UUID linker
 ✨ Load isolated X11 UUID linker result: (completed)                                                    [ ✅ ]
 ✨ Require current persisted X11 readiness
{"kwin_owner": ":1.13", "ready": true, "run": "83c1e201d0fe4d8db4220c436e87500d"}
 ✨ Require current persisted X11 readiness result: (completed)                                          [ ✅ ]
 ✨ Screenshot-free run: ignore Debug Console; answer skip to prompts claiming debug-console evidence.
 ✨ Answer other phases truthfully. GNOME logout and viewer disconnect/closure are distinct outcomes.
 ✨ If logout ends the viewer, skip the normal viewer-close claim and report that logout ended the session.
 ✨ Run unchanged maintainer identity proof
---[ gmki91 rdp_identity-security_proof-20261108 ]--------------------------------------------------------------
 ✨ PWD: [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]
 ✨ Moving to [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]                                       [ ✅ ]
 ✨ creating rdp_proof_dir                                                                               [ ✅ ]
 ✨ creating screenshot subdirectories                                                                   [ ✅ ]
---[ rdp_identity-security_proof-20261108 (configuration) ]-----------------------------------------------------
 * PN .................: [ rdp_identity-security_proof ]
 * BUILD ..............: [ 20261108 ]
 * rdp_user ...........: [ joe ]
 * project_dir ........: [ /home/joe/joetoo-ai/workspace/projects/joetoo-kwin ]
 * rdp_proof_dir ......: [ /tmp/joetoo-rdp-stage-a.8R7xmIXt ]
 * rdp_bus ............: [ org.joetoo.KWinBridge ]
 * rdp_path ...........: [ /org/joetoo/KWinBridge ]
 * rdp_iface ..........: [ org.joetoo.KWinBridge ]
 * rdp_proof_seconds ..: [ 1800 ]
 * rdp_poll_seconds ...: [ 0.25 ]
 * rdp_dbus_seconds ...: [ 3 ]
 * rdp_tag ............: [  ]

 ✨ Writing RegistryStatus-before json file
                                                                                                         [ ✅ ]
 ✨ Writing ListManaged-before json file
                                                                                                         [ ✅ ]
 ✨ Writing ListObserved-before json file
                                                                                                         [ ✅ ]
 ✨ Launching debug console                                                                              [ ✅ ]
 ✨ Private evidence rdp_proof_dir: [/tmp/joetoo-rdp-stage-a.8R7xmIXt]
 ✨ launching rdp client under sureillance
 * rdp_tag: [joetoo-rdp-proof-2aaf1650-70a8-4bdc-8859-403d956b8f60]
 * rdp_pid: [914883]
 ✨ Writing pid and tag to /tmp/joetoo-rdp-stage-a.8R7xmIXt/run.txt (success!)                           [ ✅ ]
 * backgrounding filtered ListObserved collection
 * rdp_observer_pid: [914907]
 ✨ Note: Tests may require debug console evidence collection
 ✨ If not, you may dismiss the launched debug console; otherwise do this for each --
 ✨  - find target section in the debug console and take screenshot(s)
 ✨  - move the new screenshots to the associated subdir in rdp_proof_dir
 ✨ Are you ready to record, "1. NLA credential dialog visible"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [1. NLA credential dialog visible]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "2. NLA credentials submitted and accepted"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [2. NLA credentials submitted and accepted]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "3. SDL viewer window visible"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [3. SDL viewer window visible]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "4. GDM greeter window visible"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [4. GDM greeter window visible]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "5. GDM login credentials submitted"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [5. GDM login credentials submitted]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "6. Authenticated GNOME desktop visible and usable"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [6. Authenticated GNOME desktop visible and usable]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "7. Viewer rendering, resizing and redraw tested"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [7. Viewer rendering, resizing and redraw tested]
                                                                                                         [ ✅ ]
 ✨ Are you ready to record, "8. Viewer closed normally"?
 ✨ y: yes; n: no - abort; s: skip [Yes/no/skip|Yns]: y                                                         
 ✨ recording phase [8. Viewer closed normally]
                                                                                                         [ ✅ ]
Describe outcome in one line: normal launch; same smooth move; minor tearing in redraw when resizing; still logged in - closed with X, not logout
 ✨ Waiting for SDL FreeRDP PID [914883] to exit (error!)                                                [ ❌ ]
 ✨ Client exit status: [131]
 ✨ Writing client exit status to /tmp/joetoo-rdp-stage-a.8R7xmIXt/run.txt                               [ ✅ ]
 ✨ Stopping observer (success!)                                                                         [ ✅ ]
 ✨ Observer exit status: [0]
 ✨ Capturing final broker observations (success!)                                                       [ ✅ ]
 ✨ Collecting backend.txt ✨ Stage A evidence collected in [/tmp/joetoo-rdp-stage-a.8R7xmIXt]
 ✨ PWD: [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]
 ✨ Moving to [/tmp]                                                                                     [ ✅ ]
 ✨ Creating evidence tarball/tmp/joetoo-rdp-stage-a.8R7xmIXt/
/tmp/joetoo-rdp-stage-a.8R7xmIXt/backend.txt
/tmp/joetoo-rdp-stage-a.8R7xmIXt/observed-after.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/registry-after.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/RegistryStatus-before.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/ListObserved-before.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/client.log
/tmp/joetoo-rdp-stage-a.8R7xmIXt/screenshots/
/tmp/joetoo-rdp-stage-a.8R7xmIXt/screenshots/auth_window/
/tmp/joetoo-rdp-stage-a.8R7xmIXt/screenshots/gnome_desktop/
/tmp/joetoo-rdp-stage-a.8R7xmIXt/screenshots/greeter_window/
/tmp/joetoo-rdp-stage-a.8R7xmIXt/observations.jsonl
/tmp/joetoo-rdp-stage-a.8R7xmIXt/observer-status.txt
/tmp/joetoo-rdp-stage-a.8R7xmIXt/observation-errors.log
/tmp/joetoo-rdp-stage-a.8R7xmIXt/managed-after.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/phases.txt
/tmp/joetoo-rdp-stage-a.8R7xmIXt/run.txt
/tmp/joetoo-rdp-stage-a.8R7xmIXt/ListManaged-before.json
/tmp/joetoo-rdp-stage-a.8R7xmIXt/observer.stop
 (success!)                                                                                              [ ✅ ]
 ✨ PWD: [/tmp]
 ✨ returning to [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]                                    [ ✅ ]
 ✨ Stage A evidence collected in [/tmp/joetoo-rdp-stage-a.8R7xmIXt]
 ✨ Run unchanged maintainer identity proof result: (completed)                                          [ ✅ ]
 ✨ Proof command result [0]; this is separate from remote-session outcome
 ✨ Finish observation and start export
 ✨ Finish observation and start export result: (completed)                                              [ ✅ ]
 ✨ Finish X11 UUID linkage
 ✨ Finish X11 UUID linkage result: (completed)                                                          [ ✅ ]
 ✨ Stop X11 property observation
 ✨ Stop X11 property observation result: (completed)                                                    [ ✅ ]
 ✨ Unload isolated X11 linker
 ✨ Unload isolated X11 linker result: (completed)                                                       [ ✅ ]
 ✨ Verify X11 property evidence independently
{"candidates": 6, "desktop_role": "unproven", "discovery_gaps": 5, "latched": 2, "lifecycle_coverage": "requires_comparison_with_KWin_capture", "linker_ready": true, "observation_completed_as_requested": true, "reason": "requested", "transport_complete": true, "unlinked": 1, "unsupported": 0}
X11 candidate coverage has limitations; inspect counts before drawing conclusions.
A use latch does not prove desktop role or graphical-login completion.
 ✨ Verify X11 property evidence independently result: (completed)                                       [ ✅ ]
 ✨ Wait for durable export and sender confirmation
{"failure": null, "internal_capture_intact": true, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": false, "observer": "rdp-diag-mw85qdoh-glpcssid27s5j6lg1dpknsph1907v0azbw64qrv841", "protocol": 1, "ready_persisted": true, "receiver": ":1.28781", "records": 331, "run_id": "02b7a74ba65645a790f39757a21fddaa", "sender_confirmed_end_ack": true, "transport_complete": true}
 ✨ Wait for durable export and sender confirmation result: (completed)                                  [ ✅ ]
 ✨ Independently verify evidence and receipts
{"bytes": 662825, "internal_capture_intact": true, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "observer": "rdp-diag-mw85qdoh-glpcssid27s5j6lg1dpknsph1907v0azbw64qrv841", "protocol": 1, "records": 331, "run_id": "02b7a74ba65645a790f39757a21fddaa", "sender_confirmed_end_ack": true, "sha256": "4daa896269e61e7b65408949d25a4b1f68917c01f0fe5ecb623e0a90298c72eb", "transport_complete": true}
 ✨ Independently verify evidence and receipts result: (completed)                                       [ ✅ ]
 ✨ Check internal capture integrity separately from delivery
 ✨ Check internal capture integrity separately from delivery result: (completed)                        [ ✅ ]
 ⚠ Lifecycle coverage remains UNASSESSED: correlate proof PID/title/actual phase markers with exact diagnostic UUIDs.
 ✨ Closing a client is not proof of remote logout. No native identity conclusion is automatic.
 ✨ Unload only our diagnostic
 ✨ Unload only our diagnostic result: (completed)                                                       [ ✅ ]
 ✨ Stop only our receiver
 ✨ Stop only our receiver result: (completed)                                                           [ ✅ ]
 ✨ Archive private diagnostic evidence
 ✨ Archive private diagnostic evidence result: (completed)                                              [ ✅ ]
 ✨ Evidence retained: [/tmp/joetoo-rdp-diagnostic.y8vCwR5i]
 ✨ Archive attempt: [/tmp/joetoo-rdp-diagnostic.y8vCwR5i.tbz2]; inspect its reported result
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $
```
