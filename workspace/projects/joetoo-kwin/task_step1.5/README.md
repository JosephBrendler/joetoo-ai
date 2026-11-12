# Step 1.5 — Task history, decisions and verification index

This is the **historical task record**, not execution authority. For current actor/scope/approval see [HANDOFF](HANDOFF.md), for engineering requirements see [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), and for architecture see [project ARCHITECTURE](../ARCHITECTURE.md). Source, records and tests described below remain separate from authorization to act.

## Merged Step 1.5c.5d milestone and Step 1.5d transition (2026-11-11)

**MERGED — PR [#29](https://github.com/JosephBrendler/joetoo-ai/pull/29)** completed Step **1.5c.5d** on `main` at merge commit **`3e9c4bf311bc65b32d332a00d3b50163a9043303`**. All five Increment acceptance decisions, including Increment 5's native strict-security refusal, remain final. The maintainer reported `gmki91` clean on synchronized `main`, and `git log -1 --show-signature` showed a good GitHub GPG signature for the merge. This is source publication evidence, **not** proof that every other workstation/installed runtime was updated.

**Next Step 1.5d:** implement the existing `-L` single-window launch and `-l` managed listing CLI stubs and run a bounded integrated native X11/Wayland regression of accepted Step 1.5 features; see [current HANDOFF](HANDOFF.md) and [architecture milestone table](../ARCHITECTURE.md). Design details of `-L` operands, supported modes and `-l` display/filter behavior must be source-grounded before implementation; preserve current `-o` and D-Bus ownership contracts. The new preparatory branch `task/joetoo-kwin-step1.5d-integrated-regression` is based on the accepted merge. Separate future steps include destructive managed close (1.6), runtime reconciliation (1.7), restore (1.8) and packaging (1.9). `/etc/joetoo-kwin/BUILD` from ebuild `$PVR` remains on the packaging backlog.

**Accepted evidence pointers:** [Increment 5 final native acceptance](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md), [pre-strict native X11/Wayland](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md), [Increment 4 Stage 4](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md). The historical discussion and draft tasks below remain chronology, not new work authorization. Any older `1.5c.5d OPEN` or `1.5d FUTURE` text in historical sources is superseded by this current accepted status and HANDOFF.

## Increment 5 native evidence and security-policy decision (2026-11-11)

**Production trusted endpoint accepted on both backends:** `gmki91` native X11 and `q552u01` native Wayland each launched `joetoo-kwin -v -o` against `raspiubuntu401.brendler:3389`; desktop 18 slot 1 exact UUID, verified placement and stacking, `1/1` success and GDM greeter screenshots. Prior registered windows were preserved; no certificate warning observed. X11 explicitly included a completed NLA prompt. System GRD certificate fingerprint and SAN/CA chain were checked; exact negotiated TLS protocol/cipher remains unrecorded. Existing default FreeRDP production policy was *not* strict. Details/excerpts and limitations: [2026-11-11 production native/security evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md), supplemented by the [earlier Codex closure candidate](step1.5c5d-increment5-security-native-closure-candidate.md).

**Final maintainer acceptance (2026-11-11):** `rdp_security_protocol=nla` defaults to exclusive `/sec:nla` (not `/sec:nla:on`), with `negotiate` omitting `/sec:`; `rdp_certificate_policy=strict` defaults to `/cert:deny`, with `prompt` omitting `/cert:`. Both are validated, user-overridable under accepted configuration precedence and shown in `-vc`, documented in templates/reference. Codex reported **185 focused Python / 919 full Python / 161 JS PASS**, syntax and ShellCheck PASS (reported outcomes, not independently rerun here). The maintainer verified native strict production arguments on `gmki91` X11, successful GDM greeter and exact UUID placement on desktop 19, then an IP-name mismatch (192.168.62.171) automatically rejected by FreeRDP with `CERTIFICATE NAME MISMATCH`, strict auto-deny and `ERRCONNECT_TLS_CONNECT_FAILED`; the registered trusted viewer survived and the failed child was reaped with verified eligible cleanup. **Increment 5 ACCEPTED, Step 1.5c.5d CLOSED.** See [final strict native acceptance with selected transcripts](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md), supplemented by the [earlier pre-policy production X11/Wayland observations](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md). The [Codex implementation task](step1.5c5d-increment5-rdp-security-policy-codex-task-DRAFT.md) is historical/completed, not a current assignment. No `/tls:enforce:1.3` default.

**Later ebuild to-do (not Increment 5):** install `/etc/joetoo-kwin/BUILD` from package `$PVR`; have CLI source its own BUILD rather than `joetoolkit` BUILD, with an appropriate development fallback.

## Accepted increment outcomes

| Increment | Accepted outcome / limitation | Primary evidence |
| --- | --- | --- |
| 1.5a–b | Configured planning and interactive forms, preserving existing session behavior | [Project README](../README.md) and historical HANDOFF |
| 1.5c.1–c.3 | Confirmed launch planning, safe managed registration, original local Bash/SSH continuity | [Project README](../README.md), historical HANDOFF |
| 1.5c.4 | Desktop capacity, local Dolphin, layers, grouping and bounded initial stack/focus accepted on native X11/Wayland | [Native acceptance](step1.5c4-native-acceptance.md), [review](step1.5c4-review.md) |
| 1.5c.5a | Dolphin SFTP, independent connectivity advisories and safe managed placement accepted | [SFTP acceptance](step1.5c5a-native-acceptance.md) |
| 1.5c.5b | TigerVNC over owned authenticated SSH tunnel, exact viewer UUID placement and tunnel teardown accepted | [Project README](../README.md), historical HANDOFF |
| 1.5c.5c | Affirmative RDP feasibility; SDL3 FreeRDP chosen **first by implementation order**, not as default over TigerVNC | [PR #28](https://github.com/JosephBrendler/joetoo-ai/pull/28), [research](README_remote_desktop_research.md) |
| 1.5c.5d / Increment 1 | **ACCEPTED**: native-Wayland SDL registration-only, no placement | [Native-Wayland evidence](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md) |
| 1.5c.5d / Increment 2 | **ACCEPTED (2026-11-08)**: native-KWin-X11 stock SDL registration-only with `auto` and `software`; same exact UUID retained when closed; 644 Python and 145 JavaScript regressions passed on the implementation baseline. The 500 ms X11 persistence heuristic has a known counterexample; no automatic placement or general production-RDP security acceptance. | [Native X11 registration evidence, including `software` closeout](step1.5c5d-increment2-native-x11-registration-2026-11-08.md) |
| 1.5c.5d / Increment 4 Stage 3 | **ACCEPTED (2026-11-10–11)**: five-minute readiness defaults, known-clean failure continuation, fail-closed uncertainty, success-only cohort ordering; headless and native X11/Wayland pass | [Stage 3 native acceptance](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md) |
| 1.5c.5d / Increment 4 Stage 4 | **ACCEPTED (2026-11-11)**: optional sparse system/user defaults, `-f`/selected plan precedence, non-root `eselect joetoo-kwin` profile selection, reference/template, notice/info/debug configuration display; isolated native X11 selected-profile and real `2/2` Dolphin/Konsole launch accepted; 903 local full Python / 161 JS, 911 final Codex Python / 161 JS, final maintainer ShellCheck clean | [Stage 4 native acceptance and transcripts](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md) |
| 1.5c.5d / Increment 3 | **Option C candidate implemented; new single-run native-Wayland automated placement succeeded (2026-11-10).** `599f7f3`: 789 Python / 161 JS tests pass; exact UUID registered, placement submitted +6.43 ms, full `(1,1) 800×628` frame broker-verified +116.16 ms after registration, while GDM still black. Earlier 15 s failure remains historical/unexplained; repeat/X11 regression and configured `-o` are open. | [New smart-sizing/immediate-placement evidence](step1.5c5d-increment3-native-wayland-smart-sizing-immediate-placement-2026-11-10.md), [normalized trace](step1.5c5d-increment3-immediate-placement-transcript-2026-11-10.log), [earlier failing Wayland trace](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md), [X11 sequential closeout](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md) |

## Increment 4 Stage 3 acceptance and Stage 4 authorization (2026-11-10–11)

The maintainer **accepted Stage 3** after Codex's 447 focused / 869 full Python and 161 JavaScript PASS report, locally observed `gmki91` 869 Python and 161 JavaScript PASS with service update/check, and native serial tests on **X11 (`gmki91`) and Wayland (`q552u01`)**. In both native tests: Konsole slot 1 succeeded, RDP slot 2 failed with positively verified terminal broker and child/worker cleanup, Konsole slot 3 succeeded, success-only initial stack/focus was verified, and final accounting correctly reported `completed [2], failed [1], skipped [0]` with incomplete/nonzero overall status. Valid `rdp_registration_timeout_ms=5000` test overrides worked; production RDP/VNC defaults are 300000 ms. The earlier unresolved failure correctly blocked continuation. Full field excerpts, screenshot provenance, limitations and test-plan pointer: [Stage 3 acceptance record](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md).

**Stage 4 authorized to proceed in bounded phases**: next Stage 4A documentation/template preparation, using [configuration layering design](step1.5c5d-increment4-configuration-layering-proposal-DRAFT.md), [per-run draft](../joetoo-kwin-per-run-template-IMPROVED-DRAFT.conf) and [draft Codex task](step1.5c5d-increment4-stage4A-codex-task-DRAFT.md). Stage 4B runtime layering and optional per-user `eselect` selection require separate implementation authorization. Do not reopen the working VNC/RDP implementations for redesign or normalization in version 1. HANDOFF controls the next actor and publication gates.

## Increment 2 closeout: what was actually observed

The native-X11 A2 patched-FreeRDP alternative was abandoned. The current stock-client legacy X11 profile is `sdl-x11-a1c-v1`, offering child-local `rdp_x11_renderer=auto|software` (auto default) and shared configured `rdp_x11_identity_settle_ms` (tested at 500 ms). The environment-guard error caused by an OpenRC `XDG_SESSION_TYPE=tty` label was corrected without falsely claiming the desktop backend was X11; the actual SDL child/backend still must be proven.

On `gmki91` native Plasma X11, managed `auto` registered a correlated KWin UUID, showed usable remote GNOME content and, in a second launch, retained the same `win-001`/UUID after close with `presence=missing`, no successor adoption. The maintainer reported the full project command `./tools/restart_joetoo-kwind test` PASS with **644 Python** and **145 JavaScript** tests, successful update/check and introspectable SDL D-Bus interfaces.

The subsequent **managed** `software` renderer test (not merely the earlier diagnostic `software` trial) connected to `opi6plus01.brendler` on `gmki91`, registered `win-001`, child PID `2640147`, UUID `be27f183-c8a2-4772-a802-1cc5e2fb2f30` with `placement=not_requested`, live `presence=present`, `succeeded=1`, `failed=0`. After titlebar-X closure, `GetManaged` retained **the same UUID** with `presence=missing`, `RegistryStatus` synchronized, one missing managed window, idle placement transaction and no failed/ambiguous/timed-out requests. The launcher `child_exit` terminal output was not provided, so no exit-code claim is made. The maintainer accepted Increment 2 on this evidence. See the [full combined evidence record](step1.5c5d-increment2-native-x11-registration-2026-11-08.md).

**Residual risk remains accepted and explicit:** a marked temporary X11 viewer surviving 600 ms can be registered at the 500 ms eligibility threshold. A replacement UUID must never be silently enrolled. X11 selection remains best effort, not proof of renderer handover. Registration proves neither TLS/NLA authenticity nor GDM/remote usability; manually repositioned test windows do not constitute broker-managed placement.

## Increment 3 implementation and native X11 status (2026-11-09)

The maintainer pushed the five-file Codex placement candidate as [`e7f63ce`](https://github.com/JosephBrendler/joetoo-ai/commit/e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1). The separate `joetoo-sdl-release-placement.py` operator action targets a previously registered exact UUID without relying on the active window or changing remote authentication status. Maintainer-run headless verification passed **191 focused Python, 676 full Python and 158 JavaScript tests** with a clean `git diff --check`; the initial missing-`node` test prerequisite was resolved.

Native X11 `software` placement to `(0,0)` and `auto` placement to `(120,90)` succeeded against `opi6plus01.brendler`, each with stable exact UUID across placement, `presence=missing` after titlebar closure, and no successor adoption; placing a closed viewer was rejected with `InvalidRequest`. The original viewer remained separate from remote-GDM login status (`remote_session=unverified`). Both tests requested 800×600 but later observed **1032×804** frames, so stable specified size is **not established**. An attempted next registration was refused as `Broker is busy` solely because the standalone launcher insists on placement transaction `IDLE` after an earlier terminal `OK`; a temporary broker restart allowed the `auto` test. This is a **confirmed sequential-reuse defect**, not a different-slot conflict.

**Subsequent resolution, 2026-11-09:** The maintainer reviewed, signed and pushed the focused three-file terminal-`OK` launcher fix as [`5a2e152`](https://github.com/JosephBrendler/joetoo-ai/commit/5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c). Reinstallation/restart and independent 691 Python / 158 JavaScript full regression passed. Native A (`software`, `win-001`, placed and closed) was followed by B (`auto`, `win-002`, registered and closed) **without restarting the same broker**, while A's previous terminal `OK` placement and original UUID were preserved. Final state: two distinct managed records, both `missing`, two successful registrations and no failures. **Sequential-registration defect CLOSED / ACCEPTED**; details and exact broker output in [native sequential closeout](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md). The previous `Broker is busy` transcript is pre-fix history, not an open issue.

### Increment 3 native-Wayland diagnostic — completed, not placement acceptance (2026-11-09)

The maintainer published diagnostic-only revision `6516a31`, fast-forwarded `q552u01`, installed it, restored the user-private broker stderr sink, and ran **763 Python / 161 JavaScript tests PASS**. The newly registered viewer `win-001` started at `(448,119) 1024×796` on desktop 1. One request for `(300,160) 800×600` was accepted: KWin claimed the exact UUID and attempted assignment; `Complete(VERIFY)` was accepted and `VERIFYING` entered within ~5 ms. The **outer `guard_deadline` expired at 15.001 s** with identity/source continuity true. A passive event at 54.343 s observed the **same UUID at `(300,160)`**, while size remained **1024×796**. Terminal placement remained `failed`. The physical-movement time and delayed client/compositor behavior are not established; no verified frame-size success is claimed. Full normalized operator/broker output and limitations: [native-Wayland placement trace](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md).

**Historical disposition (2026-11-09):** The failed native diagnostic was accepted as sufficient to implement Option C; that consolidation has since landed at `df01e0c`. **Current (2026-11-10):** A separate native Wayland immediate placement succeeded at `599f7f3`; see the next section. Increment 3 still awaits a maintainer acceptance decision and any chosen repeat/X11 checks. Configured `-o` and Option D are separate gates; see [HANDOFF](HANDOFF.md).

## Increment 3 native-Wayland smart-sizing / automatic placement (2026-11-10)

The maintainer committed `54df85f` after two focused test modules passed (42 + 37 tests); the restricted development SDL FreeRDP launcher now supplies `/size:1024x768` and `/smart-sizing:800x600`. A standalone Wayland viewer scaled the full GNOME desktop correctly, with aligned pointer and interactive resizing. A separate KWin direct assignment achieved exact frame `(100,100) 800×628` and client `800×600`. After rebooting the GNOME server, manual broker-controlled placements to `(100,100)` and `(1,1)` also returned `succeeded/verified`. One earlier managed attempt nevertheless timed out at 15 seconds; that failing outcome is preserved, not revised retrospectively.

At Codex harness revision `599f7f3`, the maintainer's `q552u01` installation/check completed and **789 Python + 161 JavaScript tests passed**. In the first clean-broker immediate-placement native run, the SDL child positively registered as `win-001` / UUID `da0a37a4-aed1-4a43-b738-b10a37c87775`. The harness submitted `(1,1) 800×628` **6.43 ms** after registration; the shared broker reported `placement=succeeded`, `reason=verified` **116.16 ms** after registration, and read-only `GetManaged` showed the exact full frame on desktop 1. The maintainer observed the local black window move promptly, followed a couple of seconds later by the GDM greeter inside it. **A GDM-readiness delay is not supported by this experiment.** Registration-to-placement timing is distinct from the **~11.4 s** spent before registration, including human/remote authentication.

The successful harness lacked an attached broker-stderr trace (`diagnostic_log_not_supplied`). A prior closed viewer's `presence=missing` record continued reserving its intended desktop/slot, so the first same-slot harness attempt failed before child spawn with a generic `RuntimeError`; a broker restart cleared the in-memory record, but OpenRC initially reported started before the D-Bus service was queried successfully. These are open testing/lifecycle ergonomics issues, not proof of placement failure. The development harness continues foreground supervision but does not claim remote-session authentication (`remote_session=unverified`). Single-run native success is **not** multi-run acceptance, X11 regression or configured RDP `-o` integration. Full timings, constraints and transcript: [new native evidence](step1.5c5d-increment3-native-wayland-smart-sizing-immediate-placement-2026-11-10.md) and [normalized output](step1.5c5d-increment3-immediate-placement-transcript-2026-11-10.log).

## Accepted serial workflow design (updated 2026-11-10)

The maintainer selected a **straightforward, sequential, human-interactive** RDP/VNC mixed launch plan for the first complete configured `-o` implementation. One owned registration/placement result resolves before the next plan entry. The **2026-11-10 Increment 4 decision supersedes the previous unlimited human-wait intent**: RDP registration and TigerVNC viewer readiness have user-configurable **five-minute (300000 ms) defaults**. These bounds measure positive viewer identification, not a proven password-entry state. A known-clean timeout/failure cancels and terminates only owned pending work, reports the failed recipe and permits serial continuation; Busy, unknown ownership or unresolved cleanup remain stop conditions. D-Bus, post-registration verification, placement and cleanup retain separate bounded checks; server-side inactivity limits are outside our control.

This choice follows the already stated architecture: **Increment 3** exact-UUID operator-controlled RDP placement; **Increment 4** configured sequential mixed `-o` integration and correct human-wait handling; **Increment 5** RDP security/native closure; **Step 1.5d** broad integrated regression and `-L`/`-l`; **Phase 2** optional throughput optimization if measurement justifies queueing, prompt staging or concurrency. This sequencing is a decided product strategy, **not proof** that Increment 3/4 code already implements it.

**Historical note:** Before Increment 4 Stage 3, the RDP/VNC readiness defaults were 120 seconds and known-clean continuation remained pending. **Current accepted Stage 3 defaults are 300 seconds**, with positive cleanup and serial continuation verified on X11 and Wayland; see the acceptance record above. See [authoritative Increment 4 decisions](step1.5c5d_Increment_4_decisions.md). The [earlier strategy](step1.5c5d-increment3-strategy-decision.md) and [authentication-workflow discussion](increment2-deferred-authentication-workflow-section.md) remain historical; their prior open-ended-wait language is superseded. Old exploratory drafts are not current task instructions.

## Historical authorization chronology

Prior SFTP, VNC and RDP feasibility permissions were specific to those historical stages; they confer no current authority. The [committed long-form historical HANDOFF](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md) retains earlier approvals, constraints and iterations. Its historical instructions do not replace the [active HANDOFF](HANDOFF.md).

- **2026-10-29–30:** Step 1.5a/b forms and Step 1.5c broker/CLI coordination, verification and native acceptance.
- **2026-10-31–11-01:** Step 1.5c.4 layout/layers/desktop support, regression and native closeout.
- **2026-11-02–03:** SFTP and TigerVNC-over-SSH identity, owned tunnel, X11/Wayland placement/teardown and installer backup review.
- **2026-11-03–05:** GNOME Remote Login interoperability; KRDC, Remmina and FreeRDP evaluation; SDL X11/native-Wayland lifecycle feasibility.
- **2026-11-05–06:** RDP feasibility closed in PR #28; 1.5c.5d design, accepted native-Wayland registration-only Increment 1.
- **2026-11-07–08:** X11 A2 patched client abandoned; stock-client A1/C renderer/identity implementation. Native `auto` registration success, headless full suite PASS, then managed-native `software` registration and same-UUID post-close evidence. **Increment 2 accepted.** Sequential human-interactive baseline and Increment 3/4 sequencing approved.
- **2026-11-09:** Increment 3 placement candidate, 191 focused / 676 full Python / 158 JS tests, native X11 `software` and `auto` placement/closeout PASS. Terminal-`OK` launcher bug fixed in `5a2e152`; subsequent 691 Python / 158 JS PASS and native two-viewer same-broker A/B X11 acceptance CLOSED the sequential defect.
- **2026-11-09 (later):** `51ceda4` recorded Option C → D direction; `6516a31` diagnostic-only implementation passed 763 Python / 161 JavaScript tests on `q552u01`. Native trace isolated 15-second `guard_deadline` during `VERIFYING`, with later position-only observation. Maintainer approved proceeding to Option C implementation, leaving Option D deferred.

## Historical iteration index

The original historical HANDOFF records **Codex iterations 0–45** and **cloud iterations C1–C24**. This index is for navigation, not independent implementation authority.

| Iterations | Primary work |
| --- | --- |
| 0–9, C1–C6 | 1.5a/b forms, reports, reviews and native acceptance |
| 10–12, C7–C14 | 1.5c broker/CLI orchestration and ownership/slot contracts |
| 13–19, C15–C22 | 1.5c.4 layers, grouping, initial stacking/focus and acceptance |
| 20–24, C23–C24 | SFTP contract, implementation and native closeout |
| 25–33 | TigerVNC over SSH identity, tunnel and installer/backup disposition |
| 34–36 | RDP/GRD feasibility, PKI and native evidence |
| 37–40 | SDL diagnostics, X11 lifecycle and Wayland identity |
| 41–44 | Native Wayland/X11 correlations, failures and coexistence |
| 45 | 1.5c.5c closeout and 1.5c.5d planning |

## Focused evidence and navigation

- [Increment 4 Stage 3 native acceptance: X11/Wayland operator excerpts and test results](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md)
- [Increment 4 Stage 4A draft Codex assignment (not dispatched)](step1.5c5d-increment4-stage4A-codex-task-DRAFT.md)

- [Increment 3 native-Wayland smart sizing and automatic immediate-placement success, with limitations (2026-11-10)](step1.5c5d-increment3-native-wayland-smart-sizing-immediate-placement-2026-11-10.md)
- [Normalized native immediate-placement JSON/stderr output (2026-11-10)](step1.5c5d-increment3-immediate-placement-transcript-2026-11-10.log)
- [Increment 3 native-Wayland diagnostic trace: exact UUID, deadline, and post-terminal movement (2026-11-09)](step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md)
- [Increment 3 native X11 sequential A/B registration correction and acceptance evidence](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md)
- [Increment 3 native X11 `software` + `auto` controlled placement and historical pre-fix findings](step1.5c5d-increment3-native-x11-placement-2026-11-09.md)
- [Increment 2 X11 `auto` + `software` full registration/lifecycle evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md)
- [Increment 1 native-Wayland acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md)
- [X11 default/OpenGL feasibility](step1.5c5d-a1-auto-renderer-native-evidence-2026-11-08.md)
- [X11 software diagnostic feasibility](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md)
- [X11 A1/C draft design](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md)
- [Remote Desktop research](README_remote_desktop_research.md) and [GNOME study](README_gnome_remote_desktop.md)
- [RDP private PKI / GRD system Remote Login evidence](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md)
- [1.5c.4 native acceptance](step1.5c4-native-acceptance.md); [SFTP native acceptance](step1.5c5a-native-acceptance.md)
- [1.5c.5 implementation scope](Step1.5c5_implementation_scope.md); [project architecture](../ARCHITECTURE.md)
- [Authoritative Increment 4 maintainer decisions](step1.5c5d_Increment_4_decisions.md); [superseded historical strategy](step1.5c5d-increment3-strategy-decision.md)

## Record policy

This README reports accepted outcomes and durable engineering decisions. HANDOFF stays short and actionable. Evidence records support observations; pending Codex work is described as planned until it has actually been implemented, tested, reviewed and accepted. No future collaborator is asked to redo already settled acceptance or strategy decisions.
