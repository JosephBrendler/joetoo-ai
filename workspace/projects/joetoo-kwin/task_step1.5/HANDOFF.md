# Step 1.5 — Active task dispatch

**Active task:** Step **1.5c.5d, Increment 1** — native-Wayland SDL FreeRDP registration of the exact KWin viewer UUID, **without placement**.

**Phase:** Registration-only private core and additive D-Bus development-interface candidate implemented. Maintainer verification progressing; Increment 1 is **not yet accepted**.

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`

**Current integration checkpoint:** `2938ec9` — local merge of current `origin/main` into the task branch, following implementation commits through `6dee4ce`. Verify actual HEAD and working-tree state at the beginning of each subsequent iteration; this checkpoint is not a permanent branch-head assertion.

**Repository state:** The SDL candidate, associated tests, interface contract and maintainer changes to `tools/restart_joetoo-kwind` are committed on the task branch. Documentation from `main` through `9e6a061` has been integrated locally. The updated task branch still requires a push to `origin`.

## Authoritative references

| Purpose | Document |
| --- | --- |
| Governing instructions | Repository-root, workspace and project `AGENTS.md`; `workspace/README.md` |
| Product architecture | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Detailed requirements, implementation increments and gates | [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), §5A |
| Historical outcomes and decisions | [Task README](README.md) |
| RDP feasibility and diagnostic findings | [Remote-desktop research](README_remote_desktop_research.md) |
| Current SDL D-Bus contract and implementation evidence | [SDL interface contract](step1.5c5d-sdl-interface-contract.md), especially §5 and §6 |

## Current authority and boundaries

**Previously authorized:** Increment 1 native-Wayland registration-only implementation, four additive SDL development D-Bus methods, and bounded non-destructive headless tests.

**Next proposed development task:** Maintainer validation of `tools/joetoo-kwind-install-poc` and maintainer-operated Begin/Cancel D-Bus smoke test.

**Reserved decisions:** Any alternative caller-provenance mechanism, changed public signatures, production TLS/NLA or certificate policy, native SDL/RDP connection tests, X11 registration, window placement, configured RDP recipes, subsequent increments, production deployment and publication of the implementation to `main`.

**Invariants:** Register only a positively verified, launch-owned native-Wayland viewer UUID. Fail closed on ambiguous, lost or contradictory evidence. Registration must never request desktop, geometry, stacking or focus changes. Existing generic and TigerVNC behavior remains unchanged.

**Stop/escalate:** Missing authorization, incomplete process/FD provenance, ambiguous KWin lifecycle, unexpected source changes, regression failures, new interface/security requirements or expansion into a reserved operational gate.

## Latest result — maintainer validation, 2026-11-06

**Codex implementation:** Four additive development methods are implemented:

- `BeginSdlRegistration`
- `BindSdlRegistration`
- `PollSdlRegistration`
- `CancelSdlRegistration`

The implementation and focused evidence are preserved in the committed task branch. Codex originally reported 97 focused Python, 575 full Python and 99 JavaScript tests passing.

**Maintainer regression verification on `gmki91`:**

- Python: **575 PASS**, including after the documentation merge.
- JavaScript: **99 PASS**, including after the documentation merge.
- `git diff --cached --check`: clean before completing the merge.
- The merge was completed at `2938ec9`.

**Live D-Bus introspection on `gmki91`:** After the maintainer ran `tools/restart_joetoo-kwind`, all four SDL development methods appeared on `org.joetoo.KWinBridge`, with the expected signatures. This establishes method exposure, not successful live Begin/Bind/Poll/Cancel transaction execution.

**D-Bus process-identity prerequisite on `q552u01`:** A read-only preflight in the existing non-root Plasma graphical session returned `ProcessFD`, `ProcessID`, `UnixUserID` and `UnixGroupIDs`, with UID and PID matching the caller. **ProcessFD is available on the tested session bus.** No broker installation or restart was needed for this preflight.

**Installer gap:** (pending maintainer verification) `tools/joetoo-kwind-install-poc` currently installs and checks the original ten managed files but does not manage `libexec/joetoo_kwin_rdp_launch.py`. Therefore the new D-Bus method signatures are exposed, but the complete SDL implementation has not yet been verified through the installed-user-service path.

**Not yet verified:** Live Begin/Cancel transaction, Unix-FD marshalling, complete SDL child binding, actual native-Wayland viewer UUID registration, production TLS/NLA or certificate trust. No window placement or configured RDP capability has been accepted.


**Codex follow-up (2026-11-06):** installer/client candidate prepared; 156 focused,
591 full Python and 99 JavaScript tests pass. Adapter now participates in the
ten-file lifecycle; test-model/direct-discovery fixes are verified. Runtime and
restart-wrapper sources are preserved. See [focused installer/smoke evidence](step1.5c5d-sdl-interface-contract.md#6-installer-integration-and-non-networked-smoke-preparation--2026-11-06).
Maintainer review/approval of the corrected installer and non-networked
Begin/Cancel procedure is next; no operational smoke test was run by Codex.


## Next actor and decision

**Maintainer:** verification/wayland smoke test

**Next acceptance gate:** Review the corrected installer and local D-Bus smoke-test procedure before operational execution. Actual native SDL registration and remote connection testing remain separate decisions.

The successful `ProcessFD` preflight does not authorize the alternative self-pidfd design, which remains unnecessary for the tested host and unimplemented.

No further implementation, native test or publication permission is implied by this dispatcher itself.

---

**Maintenance convention:** Keep this file limited to the current task, authorized scope, latest result and next decision. Record detailed implementation evidence in focused documents and durable milestones in the task README. Do not recreate the historical iteration table.
