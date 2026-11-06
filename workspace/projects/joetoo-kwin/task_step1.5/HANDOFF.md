# Step 1.5 — Active task dispatch

**Active task:** Step **1.5c.5d, Increment 1** — native-Wayland SDL FreeRDP registration of the exact KWin viewer UUID, **without placement**.

**Phase:** Public development-interface candidate implemented; maintainer review and native prerequisites pending. Increment 1 is **not yet accepted**.

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`

**Reported local HEAD:** `5d322e9d254b08248ef6384f5c4815d30b4c267c`. Verify the actual checkout before acting. Candidate changes remain uncommitted and include untracked files.

**Published documentation baseline:** `main` includes documentation updates through `c26582e7f16331b61d7e2a3ca6d04113b3f89316`. These changes are not automatically present in Codex's active branch.

## Authoritative references

| Purpose | Document |
| --- | --- |
| Governing collaboration rules | Repository-root, workspace and project `AGENTS.md`; `workspace/README.md` |
| Product requirements and roadmap | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Detailed implementation requirements and gates | [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), §5A |
| Historical outcomes and decisions | [Task README](README.md) |
| RDP investigation and feasibility evidence | [Remote-desktop research](README_remote_desktop_research.md) |
| Current development interface and test evidence | `step1.5c5d-sdl-interface-contract.md` — currently available only in Codex's local working tree |

## Current authority and boundaries

**Maintainer-authorized development:** Increment 1 registration-only implementation, four additive SDL development D-Bus operations and bounded non-destructive headless testing. Narrow corrections within that previously approved implementation envelope may be undertaken when directed by the maintainer.

**Reserved decisions:** Any alternative to bus-supplied `ProcessFD`; new interface signatures or security guarantees beyond the approved development contract; production TLS/NLA and endpoint trust; native execution, installation, deployment, publication, X11 registration, placement, configured RDP integration and subsequent increments.

**Invariant:** Register only a uniquely proven, launch-owned, live native-Wayland viewer UUID. Fail closed on ambiguous or incomplete evidence. No desktop/geometry/stack/focus mutation. Existing generic and TigerVNC behavior must remain unchanged.

**Stop and escalate:** Missing or contradictory authority, insufficient caller/child/FD identity, lost KWin lifecycle evidence, new security/interface requirements, unexpected source changes, test regressions or any reserved operational/publication action.

## Latest result — Codex, 2026-11-06

Codex reports implementation of four additive development methods:

`BeginSdlRegistration`, `BindSdlRegistration`, `PollSdlRegistration` and `CancelSdlRegistration`.

**Reported validation:** 97 focused Python, 575 full Python and 99 JavaScript tests passing, plus specified syntax, declaration and whitespace checks. These results have not been independently rerun by the reviewer.

**Candidate availability:** Uncommitted local source and tests, exported to `/tmp/step1.5c5d-sdl-public-interface.patch` on `gmki91`. Full implementation and security notes reside in the local SDL interface-contract document. Neither the patch nor the uncommitted contract is assumed available on remote GitHub.

**Open prerequisite:** The existing user bus denied Codex's credential inquiry. Actual `ProcessFD` availability on `q552u01` is unverified; missing-credential behavior currently fails closed.

**Review findings:** Confirm real D-Bus/FD behavior, validate the SDL log-output assumption and correct the bus-disconnect test semantics before native acceptance.

## Next actor and decision

**Maintainer:** Run the read-only `ProcessFD` preflight on `q552u01` and report its result; review the candidate and the remaining interface/security questions.

**Codex:** Upon maintainer direction, perform only the bounded review corrections and return an updated complete source/test diff. Do not reintroduce the historical HANDOFF iteration table.

**Next approval gate:** Decide whether the current interface contract is suitable for a bounded operational development launcher and subsequent maintainer-native registration-only testing. If `ProcessFD` is unavailable, first decide the separately proposed provenance alternative.

No native test, production acceptance, commit, push, PR, merge or later increment is authorized by this status record.

---

**Maintenance convention:** Replace current status and latest-result text at material transitions. Detailed reports, engineering evidence and history belong in referenced task/evidence documents; HANDOFF is not an append-only journal.
