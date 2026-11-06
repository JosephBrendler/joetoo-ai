# Step 1.5 — Active task dispatch

**Active task:** Step **1.5c.5d, Increment 1** — native-Wayland SDL FreeRDP registration of the exact KWin viewer UUID, **without placement**.

**Phase:** Registration-only private core, additive D-Bus development interface and ten-component installer implemented. **Native Begin/Cancel smoke gate ACCEPTED by maintainer on 2026-11-06.** Development of the persistent SDL registration launcher is now authorized. Increment 1 is **not yet accepted**.

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`

**Published checkpoint:** `2bb9c74` — committed, pushed to `origin`, and synchronized on `gmki91` and `q552u01`. Verify actual checkout and working-tree state before acting.

## Authoritative references

| Purpose | Document |
| --- | --- |
| Governing instructions | Repository-root, workspace and project `AGENTS.md`; `workspace/README.md` |
| Product architecture | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Detailed requirements and incremental gates | [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), §5A |
| Historical outcomes and decisions | [Task README](README.md) |
| RDP feasibility and diagnostic findings | [Remote-desktop research](README_remote_desktop_research.md) |
| SDL D-Bus contract and implementation evidence | [SDL interface contract](step1.5c5d-sdl-interface-contract.md), §§1–6; next evidence in §7 |

## Current authority and boundaries

**Maintainer decision — 2026-11-06: ACCEPTED.** The q552u01 native Begin/Cancel smoke test satisfies its bounded acceptance gate. No further approval of that completed gate is pending.

**Maintainer decision — 2026-11-06: AUTHORIZED.** Codex may implement and headlessly validate the smallest development-only persistent SDL registration launcher supporting Begin → direct SDL child → Bind → Poll/Cancel, within the existing four-method contract and approved process/FD provenance requirements.

Authorized work includes focused launcher code, relevant headless tests and a concise §7 evidence update to the SDL interface contract. Codex must preserve existing generic/VNC behavior, current public D-Bus signatures and the accepted registration-only boundary. Any required expansion of source scope or security/interface design must be escalated.

**Operational authority:** Headless, non-networked implementation/testing only. Native SDL execution, actual RDP connections, installation, service restarts and native Bind/UUID registration testing remain separately reserved for maintainer approval.

**Reserved decisions:** Alternative caller provenance, changed public interfaces, production TLS/NLA/certificate policy, X11 registration, window placement, configured RDP recipes, later increments, production deployment and publication to `main`.

**Invariants:** Positively verify the exact launch-owned native-Wayland viewer UUID. Fail closed on ambiguous or incomplete evidence. Never request desktop, geometry, stacking or focus changes in Increment 1. Preserve existing generic and TigerVNC behavior.

**Stop/escalate:** Missing or contradictory identity evidence; unapproved interface/security changes; unreliable SDL backend evidence; unexpected source changes; regression failures; or actions beyond authorized source/headless scope.

## Latest result — maintainer verification, 2026-11-06

**Committed candidate:** `2bb9c74` includes the corrected ten-component installer, development-interface tests, persistent-connection Begin/Cancel smoke client and supporting documentation.

**gmki91:** 156 focused Python tests PASS. Installer update/check PASS; SDL adapter matches source, owned by `joe`, mode 0644. OpenRC service started; four SDL development methods exposed with expected signatures.

**q552u01:** Fast-forward to `2bb9c74` PASS. 156 focused Python tests PASS. Ten-component installation/check PASS; adapter matches source with correct owner/mode. `/usr/bin/sdl-freerdp` available. All four development D-Bus signatures exposed.

**Native Wayland Begin/Cancel smoke — PASS, ACCEPTED:**

- Executed locally in q552u01 Plasma/Konsole using one persistent D-Bus connection.
- Two Begin/Cancel cycles completed.
- Client returned `ok:true`, `cancelled_transactions:2`, `active_requests:0`, `managed_count:0` and `placement:"IDLE"`.
- Broker owner and observation source unchanged; inventory remained synchronized.
- Final registry: `request_count=2`, `failed=2`, `pending=0`, `running=0`, `succeeded=0`, `ambiguous=0`, `timeout=0`.
- Both failed records are intentional cancellations, not failed smoke-test outcomes.
- No SDL process spawned, remote connection initiated, viewer registered or placement requested.

**Operational qualification:** An earlier q552u01 restart-wrapper invocation encountered a D-Bus session-address error and subsequently reported the user service stopped. Later direct local Wayland-session operations succeeded; a subsequent read-only check confirmed service started and a populated Unix session-bus address. Maintainer owns the separate wrapper correction.

**Remaining Increment 1 work:** Native Bind Unix-FD marshalling, direct SDL child/process/log provenance, timely verified `wayland` backend evidence and registration of the exact live KWin viewer UUID without placement. These are not established by the completed smoke test.

Detailed implementation and test evidence resides in the SDL interface contract. Preserve §6 as historical preparation; record this accepted smoke milestone and ensuing launcher-development evidence concisely in §7.

## Next actor and authorized task

**Codex — authorized now:** Implement and headlessly validate the bounded persistent SDL development launcher. Review the complete existing interface contract and source before editing. Do not introduce a configured RDP recipe, production endpoint/security policy or alternative identity mechanism.

**Next handoff:** Codex returns the complete reviewable diff, actual headless test results, unresolved log/FD/lifecycle questions and a proposed maintainer-operated native SDL/Bind/UUID test procedure. No commit, push or native execution by Codex without separate approval.

**Next reserved acceptance gate:** Maintainer review and authorization of native SDL child launch, Bind and exact UUID registration on q552u01, still without placement. Increment 2 (X11), subsequent increments and publication remain outside this authorization.

---

**Maintenance convention:** Keep HANDOFF limited to current task, maintainer authority, latest result and next action. Detailed evidence belongs in focused documents and durable milestones in the task README. Do not recreate the historical iteration table.
