# Step 1.5 — Task history, decisions and verification index

This is the **historical task record**, not execution authority. For current actor/scope/approval see [HANDOFF](HANDOFF.md), for engineering requirements see [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), and for architecture see [project ARCHITECTURE](../ARCHITECTURE.md). Source, records and tests described below remain separate from authorization to act.

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
| 1.5c.5d / Increment 3 | **NEXT IMPLEMENTATION INCREMENT**: explicit operator-controlled placement of a positively registered SDL RDP viewer; not yet implemented or natively accepted | [Active HANDOFF](HANDOFF.md), [Codex assignment](Codex-Increment3-RDP-Placement.md) |

## Increment 2 closeout: what was actually observed

The native-X11 A2 patched-FreeRDP alternative was abandoned. The current stock-client legacy X11 profile is `sdl-x11-a1c-v1`, offering child-local `rdp_x11_renderer=auto|software` (auto default) and shared configured `rdp_x11_identity_settle_ms` (tested at 500 ms). The environment-guard error caused by an OpenRC `XDG_SESSION_TYPE=tty` label was corrected without falsely claiming the desktop backend was X11; the actual SDL child/backend still must be proven.

On `gmki91` native Plasma X11, managed `auto` registered a correlated KWin UUID, showed usable remote GNOME content and, in a second launch, retained the same `win-001`/UUID after close with `presence=missing`, no successor adoption. The maintainer reported the full project command `./tools/restart_joetoo-kwind test` PASS with **644 Python** and **145 JavaScript** tests, successful update/check and introspectable SDL D-Bus interfaces.

The subsequent **managed** `software` renderer test (not merely the earlier diagnostic `software` trial) connected to `opi6plus01.brendler` on `gmki91`, registered `win-001`, child PID `2640147`, UUID `be27f183-c8a2-4772-a802-1cc5e2fb2f30` with `placement=not_requested`, live `presence=present`, `succeeded=1`, `failed=0`. After titlebar-X closure, `GetManaged` retained **the same UUID** with `presence=missing`, `RegistryStatus` synchronized, one missing managed window, idle placement transaction and no failed/ambiguous/timed-out requests. The launcher `child_exit` terminal output was not provided, so no exit-code claim is made. The maintainer accepted Increment 2 on this evidence. See the [full combined evidence record](step1.5c5d-increment2-native-x11-registration-2026-11-08.md).

**Residual risk remains accepted and explicit:** a marked temporary X11 viewer surviving 600 ms can be registered at the 500 ms eligibility threshold. A replacement UUID must never be silently enrolled. X11 selection remains best effort, not proof of renderer handover. Registration proves neither TLS/NLA authenticity nor GDM/remote usability; manually repositioned test windows do not constitute broker-managed placement.

## Accepted serial workflow design (2026-11-08)

The maintainer selected a **straightforward, sequential, human-interactive** RDP/VNC mixed launch plan for the first complete configured `-o` implementation. One owned registration/placement result resolves before the next plan entry. An operator may take several minutes or longer to respond to NLA/VNC/SSH prompts. **Human inactivity must not by itself trip a fixed automated timeout that kills the client or owned tunnel.** Technically bounded D-Bus, UUID registration and placement, safe cancellation/cleanup and fail-closed ownership remain mandatory; actual server-side timeout remains outside our control.

This choice follows the already stated architecture: **Increment 3** exact-UUID operator-controlled RDP placement; **Increment 4** configured sequential mixed `-o` integration and correct human-wait handling; **Increment 5** RDP security/native closure; **Step 1.5d** broad integrated regression and `-L`/`-l`; **Phase 2** optional throughput optimization if measurement justifies queueing, prompt staging or concurrency. This sequencing is a decided product strategy, **not proof** that Increment 3/4 code already implements it.

Current RDP and VNC supervisors have pre-registration/readiness deadlines that can expire during human authentication; those are a known Increment 4 correctness gap, not a failure of Increment 2's completed registration tests. See [strategy decision](step1.5c5d-increment3-strategy-decision.md) and [interactive-authentication decision](increment2-deferred-authentication-workflow-section.md). The superseded `step1.5c5d_DRAFT_Increment_3_strategies` and `DRAFT_Codex-Next-Operator-Controlled-RDP-Placement.md` are not current task instructions.

## Historical authorization chronology

Prior SFTP, VNC and RDP feasibility permissions were specific to those historical stages; they confer no current authority. The [committed long-form historical HANDOFF](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md) retains earlier approvals, constraints and iterations. Its historical instructions do not replace the [active HANDOFF](HANDOFF.md).

- **2026-10-29–30:** Step 1.5a/b forms and Step 1.5c broker/CLI coordination, verification and native acceptance.
- **2026-10-31–11-01:** Step 1.5c.4 layout/layers/desktop support, regression and native closeout.
- **2026-11-02–03:** SFTP and TigerVNC-over-SSH identity, owned tunnel, X11/Wayland placement/teardown and installer backup review.
- **2026-11-03–05:** GNOME Remote Login interoperability; KRDC, Remmina and FreeRDP evaluation; SDL X11/native-Wayland lifecycle feasibility.
- **2026-11-05–06:** RDP feasibility closed in PR #28; 1.5c.5d design, accepted native-Wayland registration-only Increment 1.
- **2026-11-07–08:** X11 A2 patched client abandoned; stock-client A1/C renderer/identity implementation. Native `auto` registration success, headless full suite PASS, then managed-native `software` registration and same-UUID post-close evidence. **Increment 2 accepted.** Sequential human-interactive baseline and Increment 3/4 sequencing approved.

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

- [Increment 2 X11 `auto` + `software` full registration/lifecycle evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md)
- [Increment 1 native-Wayland acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md)
- [X11 default/OpenGL feasibility](step1.5c5d-a1-auto-renderer-native-evidence-2026-11-08.md)
- [X11 software diagnostic feasibility](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md)
- [X11 A1/C draft design](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md)
- [Remote Desktop research](README_remote_desktop_research.md) and [GNOME study](README_gnome_remote_desktop.md)
- [RDP private PKI / GRD system Remote Login evidence](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md)
- [1.5c.4 native acceptance](step1.5c4-native-acceptance.md); [SFTP native acceptance](step1.5c5a-native-acceptance.md)
- [1.5c.5 implementation scope](Step1.5c5_implementation_scope.md); [project architecture](../ARCHITECTURE.md)
- [Accepted Increment 3/4 sequencing](step1.5c5d-increment3-strategy-decision.md)

## Record policy

This README reports accepted outcomes and durable engineering decisions. HANDOFF stays short and actionable. Evidence records support observations; pending Codex work is described as planned until it has actually been implemented, tested, reviewed and accepted. No future collaborator is asked to redo already settled acceptance or strategy decisions.
