# Step 1.5c.5d / Increment 2 — A1 stock-software-renderer native feasibility evidence

**Test date:** Sunday, 2026-11-08, `gmki91`, native Plasma/KWin X11 (local time UTC−05:00).  
**Evidence status:** Maintainer **ACCEPTED as provisional A1 feasibility evidence**. **Not** Increment 2 acceptance; no managed X11 registration or placement tested.  
**Task baseline:** commit `111c04e3344ca211e1104e21f3d2508a2b42d4e9` (document-transition checkpoint; this test involved subsequent local diagnostic-script edits).  
**Related:** [A1/C design draft](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md), [governing §5A](Step1.5c5_implementation_scope.md#5a-increment-15c5d--managed-rdp-implementation), [current handoff](HANDOFF.md).

## 1. Test invocation and purpose

The maintainer ran the existing bounded `tools/joetoo-rdp-diagnostic-run.sh`, which invokes the renamed `tools/rdp_identity-security_proof` with a line-oriented, validated `tools/rdp_identity-security_proof.conf` containing eight interactive reportable phases. This is a **real interactive native run**, not a Codex-run test or a broker managed-registration acceptance test.

```bash
cd ~/joetoo-ai/workspace/projects/joetoo-kwin
SDL_RENDER_DRIVER=software \
SDL_FRAMEBUFFER_ACCELERATION=0 \
RDP_DIAG_SECONDS=900 \
./tools/joetoo-rdp-diagnostic-run.sh \
    sdl-freerdp raspiubuntu401:3389 joe
```

- The remote endpoint was GNOME Remote Login on `raspiubuntu401:3389`; the unchanged proof script requested `/sec:nla`. No TLS/NLA security relaxation was part of this test.
- The client reported SDL backend **`x11`**; `client.log` includes **three** `Created renderer: software` messages. This verifies the software renderer actually ran, but does **not** independently isolate the effect of `SDL_FRAMEBUFFER_ACCELERATION=0` or quantify a video-performance penalty.
- The proof generated exact marker `joetoo-rdp-proof-58c6412f-a60b-48e8-9a86-97a64f1f8574` for process PID **842381**; class `com.freerdp.client.sdl3`.
- `RDP_DIAG_SECONDS=900` was the diagnostic observation ceiling, not a forced run duration.

## 2. Archive provenance — private data, not committed

The user supplied the following private evidence archives for analysis. The source `.tbz2` bytes must stay **outside Git**, as logs may contain environment, window titles and connection details.

| Archive filename | SHA-256 of supplied archive | Notable contents |
| --- | --- | --- |
| `joetoo-rdp-diagnostic.M59ZAfaw.tbz2` | `75fb0499e2ff4f957f383f731b0361962089c1ab9abec448994e5a0c82ceac1e` | `evidence.jsonl`, X11 `x11-use.jsonl` and verification, `receipt.json` |
| `joetoo-rdp-stage-a.EH56gC3b.tbz2` | `cddc168ba09a7aca13c4c1f075c45a7957289b5d5528ff8b95033252317ee9d9` | `client.log`, `phases.txt`, `run.txt`, `backend.txt`, before/after inventories |

**Private storage reference:** `~/.local/share/joetoo-ai/rdp-evidence/`. The maintainer reports relocating evidence there. The specifically displayed `mv /tmp/joetoo-rdp-stage-a.EH56gC3b ~/.local/share/joetoo-ai/rdp-evidence/` command moves a **directory**, not the `.tbz2` archive; confirm both named archive files actually exist in the private directory before deleting the originals. No archive is bundled with this evidence file.

## 3. Correlated observed KWin / X11 lifecycle

The following lifetimes are **KWin observer `added`→`removed` wall-clock capture intervals**, corroborated by the independent X11 observer. They are not native creation-to-destruction guarantees and are not measurements of a hypothetical broker C eligibility timer.

| Observed role | KWin UUID | X11 XID | Added (EST) | Removed (EST) | KWin observed lifespan | Exact marker |
| --- | --- | --- | --- | --- | ---: | --- |
| Initial unmarked normal window | `8a06d393-5417-4df7-a156-5d33e8d9521a` | `146800688` | 12:18:22.663 | 12:18:22.749 | 86 ms | No |
| Unmarked non-normal credentials window | `d6b50813-20bc-40a8-a2a4-d0e8bdff448d` | `146800694` | 12:18:22.934 | 12:18:51.695 | 28,761 ms | No |
| Marked desktop viewer | `aa62a584-69d9-4e28-98c3-d7a8300687da` | `146800698` | 12:18:52.137 | 12:21:42.886 | 170,749 ms | Yes |

**Interpretation:** The initial 64×64 normal window was unmarked. The long-lived credential-stage window was **not** a KWin `normalWindow` and was unmarked. The eventual normal desktop viewer was the **only observed exact-marked normal UUID**, and was retained until close. The independent X11 ledger linked all three XIDs to the three KWin UUIDs.

The X11 verifier reported `candidates=3`, `latched=2`, `unlinked=0`, `unsupported=0`, **`discovery_gaps=1`** and `desktop_role=unproven`. Hence **the run does not establish exhaustive native-X11 coverage**, a universal no-replacement guarantee, renderer causal efficacy or broker selection correctness. It establishes a favorable *observed* outcome with the software settings.

## 4. Diagnostic transport and human-observed stages

- The main diagnostic export verified `records=975`, `internal_capture_intact=true`, `sender_confirmed_end_ack=true`, `transport_complete=true`; the diagnostic still reported `lifecycle_coverage=unassessed` pending correlation. X11 verifier reported `observation_completed_as_requested=true`, with the discovery gap above.
- All eight chosen human stages were affirmed and timestamp-recorded, from NLA credential dialog through usable GNOME desktop, rendering/resizing/redraw test and closing the viewer. These are **operator-reported stage times**, not automated proof of authentication state or exact viewer identity.
- The maintainer observed smooth window movement, some tearing during redraw/resizing (believed preexisting), and closed the viewer with its titlebar X rather than logging out of GNOME.
- `run.txt` recorded **`client_exit=131`** and **`observer_exit=0`**. The FreeRDP log includes `SDL_EVENT_WINDOW_CLOSE_REQUESTED` and `ERRCONNECT_CONNECT_CANCELLED [0x0002000B]` at close. Exit 131 is **not a clean-zero process exit**; the human-reported close explains the timing, but the proof script/parent reports proof result 0 despite that nonzero child exit. Do not mislabel this as clean exit or silently discard the discrepancy.

### Exact operator phase timestamps (`phases.txt` from the private Stage A archive)

```text
2026-11-08T12:18:35,243150612-05:00	1. NLA credential dialog visible
2026-11-08T12:18:54,675969646-05:00	2. NLA credentials submitted and accepted
2026-11-08T12:18:56,725911177-05:00	3. SDL viewer window visible
2026-11-08T12:19:04,405012291-05:00	4. GDM greeter window visible
2026-11-08T12:19:18,599838824-05:00	5. GDM login credentials submitted
2026-11-08T12:19:49,094283075-05:00	6. Authenticated GNOME desktop visible and usable
2026-11-08T12:21:25,558490152-05:00	7. Viewer rendering, resizing and redraw tested
2026-11-08T12:21:48,007448505-05:00	8. Viewer closed normally
2026-11-08T12:23:44,501384888-05:00	launch process appears to be normal. viewer window moves smoothly; some redraw tearing during resizing but I think that has always been the case (not unique to this run). Note that I closed the window with the X in the upper right. I did not log out
```

## 5. Maintainer decision and remaining risks

**Accepted now:** Gate F read-only feasibility assessment; this single software-renderer native **A1 feasibility run**, with the stated provenance and discovery-gap limitations. Increment 1 native-Wayland registration stays formally accepted. Candidate A2 Stage 1 remains aborted.

**Chosen direction:** two **independent, legacy-native-X11-only user settings** — proposed `rdp_x11_renderer = auto|software` and `rdp_x11_identity_settle_ms = 500`. In `auto`, launch the managed client with SDL's renderer overrides unset (not an empty string). In `software`, apply `SDL_RENDER_DRIVER=software` and `SDL_FRAMEBUFFER_ACCELERATION=0` **to the managed child only**. Both modes retain the same bounded broker-owned Candidate C candidate-dwell/identity checks; neither mode is infallible. Default accelerated SDL selection may offer better local performance but has not been benchmarked, and software mode may cost CPU/GPU performance. A1 **does not itself prove viewer identity**.

**Next authorized step:** limited Codex documentation/contract harmonization and a **separately maintainer-operated** default-renderer diagnostic comparison; **no Codex native test and no Gate I broker implementation yet**. After the default-renderer evidence is reviewed, seek explicit bounded Gate I approval. Even if a 500 ms interval rejects the previously observed 20 ms marked predecessor, a marked temporary window surviving 600 ms could register incorrectly at 500 ms: the known heuristic counterexample must remain a negative design/test case.

## 6. Verbatim maintainer-submitted test-run terminal output

This is the complete console transcript supplied in chat, preserved without editing. The machine-generated JSON/DBus/client raw logs remain private in the referenced archives.

```text
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ cd ~/joetoo-ai/workspace/projects/joetoo-kwin
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ SDL_RENDER_DRIVER=software \
SDL_FRAMEBUFFER_ACCELERATION=0 \
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
 ✨ Capture directory: [/tmp/joetoo-rdp-diagnostic.M59ZAfaw]
 ✨ Start temporary receiver
 ✨ Start temporary receiver result: (completed)                                                         [ ✅ ]
 ✨ Verify receiver and pinned bus owner
{"failure": null, "internal_capture_intact": null, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": false, "observer": null, "protocol": 1, "ready_persisted": false, "receiver": ":1.27574", "records": 0, "run_id": "78d0f445caa1498680725d85c8e70337", "sender_confirmed_end_ack": false, "transport_complete": false}
 ✨ Verify receiver and pinned bus owner result: (completed)                                             [ ✅ ]
 ✨ Load standalone observer
 ✨ Load standalone observer result: (completed)                                                         [ ✅ ]
 ✨ Require persisted ready and active observation
{"failure": null, "internal_capture_intact": null, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": true, "observer": "rdp-diag-mw83j1on-ymqexnb1vn4hvy85624rnyg1derce46da9eqosq0x2", "protocol": 1, "ready_persisted": true, "receiver": ":1.27574", "records": 1, "run_id": "78d0f445caa1498680725d85c8e70337", "sender_confirmed_end_ack": false, "transport_complete": false}
 ✨ Require persisted ready and active observation result: (completed)                                   [ ✅ ]
 ✨ Start X11 property observation
 ✨ Start X11 property observation result: (completed)                                                   [ ✅ ]
 ✨ Wait for private X11 linker script
 ✨ Wait for private X11 linker script result: (completed)                                               [ ✅ ]
 ✨ Load isolated X11 UUID linker
 ✨ Load isolated X11 UUID linker result: (completed)                                                    [ ✅ ]
 ✨ Require current persisted X11 readiness
{"kwin_owner": ":1.13", "ready": true, "run": "eef87f724f504b7e8a1e749deef24b11"}
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
 * rdp_proof_dir ......: [ /tmp/joetoo-rdp-stage-a.EH56gC3b ]
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
 ✨ Private evidence rdp_proof_dir: [/tmp/joetoo-rdp-stage-a.EH56gC3b]
 ✨ launching rdp client under sureillance
 * rdp_tag: [joetoo-rdp-proof-58c6412f-a60b-48e8-9a86-97a64f1f8574]
 * rdp_pid: [842381]
 ✨ Writing pid and tag to /tmp/joetoo-rdp-stage-a.EH56gC3b/run.txt (success!)                           [ ✅ ]
 * backgrounding filtered ListObserved collection
 * rdp_observer_pid: [842405]
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
Describe outcome in one line: launch process appears to be normal. viewer window moves smoothly; some redraw tearing during resizing but I think that has always been the case (not unique to this run). Note that I closed the window with the X in the upper right. I did not log out
 ✨ Waiting for SDL FreeRDP PID [842381] to exit (error!)                                                [ ❌ ]
 ✨ Client exit status: [131]
 ✨ Writing client exit status to /tmp/joetoo-rdp-stage-a.EH56gC3b/run.txt                               [ ✅ ]
 ✨ Stopping observer (success!)                                                                         [ ✅ ]
 ✨ Observer exit status: [0]
 ✨ Capturing final broker observations (success!)                                                       [ ✅ ]
 ✨ Collecting backend.txt ✨ Stage A evidence collected in [/tmp/joetoo-rdp-stage-a.EH56gC3b]
 ✨ PWD: [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]
 ✨ Moving to [/tmp]                                                                                     [ ✅ ]
 ✨ Creating evidence tarball/tmp/joetoo-rdp-stage-a.EH56gC3b/
/tmp/joetoo-rdp-stage-a.EH56gC3b/backend.txt
/tmp/joetoo-rdp-stage-a.EH56gC3b/observed-after.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/registry-after.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/RegistryStatus-before.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/ListObserved-before.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/client.log
/tmp/joetoo-rdp-stage-a.EH56gC3b/screenshots/
/tmp/joetoo-rdp-stage-a.EH56gC3b/screenshots/auth_window/
/tmp/joetoo-rdp-stage-a.EH56gC3b/screenshots/gnome_desktop/
/tmp/joetoo-rdp-stage-a.EH56gC3b/screenshots/greeter_window/
/tmp/joetoo-rdp-stage-a.EH56gC3b/observations.jsonl
/tmp/joetoo-rdp-stage-a.EH56gC3b/observer-status.txt
/tmp/joetoo-rdp-stage-a.EH56gC3b/observation-errors.log
/tmp/joetoo-rdp-stage-a.EH56gC3b/managed-after.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/phases.txt
/tmp/joetoo-rdp-stage-a.EH56gC3b/run.txt
/tmp/joetoo-rdp-stage-a.EH56gC3b/ListManaged-before.json
/tmp/joetoo-rdp-stage-a.EH56gC3b/observer.stop
 (success!)                                                                                              [ ✅ ]
 ✨ PWD: [/tmp]
 ✨ returning to [/home/joe/joetoo-ai/workspace/projects/joetoo-kwin]                                    [ ✅ ]
 ✨ Stage A evidence collected in [/tmp/joetoo-rdp-stage-a.EH56gC3b]
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
{"candidates": 3, "desktop_role": "unproven", "discovery_gaps": 1, "latched": 2, "lifecycle_coverage": "requires_comparison_with_KWin_capture", "linker_ready": true, "observation_completed_as_requested": true, "reason": "requested", "transport_complete": true, "unlinked": 0, "unsupported": 0}
X11 candidate coverage has limitations; inspect counts before drawing conclusions.
A use latch does not prove desktop role or graphical-login completion.
 ✨ Verify X11 property evidence independently result: (completed)                                       [ ✅ ]
 ✨ Wait for durable export and sender confirmation
{"failure": null, "internal_capture_intact": true, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "native_launch_ready": false, "observer": "rdp-diag-mw83j1on-ymqexnb1vn4hvy85624rnyg1derce46da9eqosq0x2", "protocol": 1, "ready_persisted": true, "receiver": ":1.27574", "records": 975, "run_id": "78d0f445caa1498680725d85c8e70337", "sender_confirmed_end_ack": true, "transport_complete": true}
 ✨ Wait for durable export and sender confirmation result: (completed)                                  [ ✅ ]
 ✨ Independently verify evidence and receipts
{"bytes": 2147309, "internal_capture_intact": true, "kwin_owner": ":1.13", "lifecycle_coverage": "unassessed", "observer": "rdp-diag-mw83j1on-ymqexnb1vn4hvy85624rnyg1derce46da9eqosq0x2", "protocol": 1, "records": 975, "run_id": "78d0f445caa1498680725d85c8e70337", "sender_confirmed_end_ack": true, "sha256": "927b5396287464e538eac7ece152ed2fc8768ffe95afac7ee929a23c37d1c923", "transport_complete": true}
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
 ✨ Evidence retained: [/tmp/joetoo-rdp-diagnostic.M59ZAfaw]
 ✨ Archive attempt: [/tmp/joetoo-rdp-diagnostic.M59ZAfaw.tbz2]; inspect its reported result
joe@gmki91 ~/joetoo-ai/workspace/projects/joetoo-kwin $ 
```
