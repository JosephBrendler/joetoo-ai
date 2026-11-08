# Step 1.5 — Active task dispatcher

**Purpose:** State the current task, maintainer authorization, stop conditions,
and next decision. Detailed history and evidence live in the linked documents,
not here. Prior HANDOFF revisions are not current authorization.

## Current dispatch — Step 1.5c.5d / Increment 2 / A2 Stage 1 (2026-11-08)

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Verified published checkpoint:** `d0a7e4d7514660132fc74135714951712a04bdf9`
(corrected Stage 0 test, maintainer-pushed). Verify actual HEAD, checkout status,
and governing `AGENTS.md` before acting; do not reset newer work to this SHA.

**Milestone status and maintainer decisions:**

- **Increment 1 — native-Wayland SDL registration without placement:**
  formally **ACCEPTED and COMPLETE**.
- **Increment 2 — X11 SDL viewer-role identity:** **OPEN**, not implemented
  or accepted. Candidate **A2** is the approved *provisional design baseline*.
- **A2 Stage 0 — isolated resolver-protocol tests:** formally **ACCEPTED and
  COMPLETE** (2026-11-08). The corrected test is published. Independent
  `gmki91` runs: **46 focused / 99 existing JS / 145 combined PASS**;
  whitespace checks PASS. Results validate existing resident behavior under
  mocks and synthetic contract traces, **not** native KWin/D-Bus/XCB/FreeRDP.
- **A2 Stage 1 — FreeRDP proof producer:** **approved as the next stage**,
  contingent on a **separate maintainer Codex prompt specifying exact
  source-write, build and test permissions**. No Stage 1 work is yet accepted.

## Stage 1 objective and authority

Stage 1 concerns **only** the opt-in FreeRDP 3.32.1 / SDL 3.4.18 native-X11
proof producer described in [the A2 addendum](step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md)
§§1–4 and §7 Stage 1: checked *hidden* desktop-viewer initialization;
initial/completed native client XIDs; fresh nonce published on the completed
XID as `_JOETOO_SDL_X11_A2`; checked one-time show and post-show XID;
one bounded, explicitly flushed `JOETOO_SDL_X11_A2` READY record;
conservative boundary lineage and fail-closed errors. Preserve stock/Wayland
behavior. Producer evidence does **not** independently authorize registration
or establish remote login/session readiness.

**Authorization boundary:** The maintainer has approved *proceeding to Stage 1*,
**not** an unrestricted FreeRDP patch/build or installation. The next Codex
prompt will specify the actual development source tree, file-level edit
permissions, compilation/test limits, artifacts and stop gates. **Until that
prompt is issued, HANDOFF authorizes read-only orientation only.** Neither
the addendum nor this dispatcher authorizes writes to FreeRDP, SDL, Gentoo
ebuilds, broker/resident/registry/launcher, or installed clients.

## Required references — details are maintained elsewhere

| Purpose | Reference |
| --- | --- |
| Policies and architecture | Repository-root, `workspace/`, project `AGENTS.md`; `workspace/README.md`; [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| Governing incremental scope | [`Step1.5c5_implementation_scope.md`](Step1.5c5_implementation_scope.md) §5A |
| **A2 contract and Stage 1 source envelope** | [`step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md`](step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md) §§1–4, 7 |
| **Accepted Stage 0 code** | [`../tests/test_sdl_x11_resolver_protocol.js`](../tests/test_sdl_x11_resolver_protocol.js), checkpoint `d0a7e4d` |
| Earlier X11 problem/evidence | [`step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md`](step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md); [`README_remote_desktop_research.md`](README_remote_desktop_research.md) |
| Accepted Increment 1 and Wayland v1 | [`step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md`](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md); [`step1.5c5d-sdl-interface-contract.md`](step1.5c5d-sdl-interface-contract.md) |
| Deferred auth, placement and `-o -f CONFIG` | [`increment2-deferred-authentication-workflow-section.md`](increment2-deferred-authentication-workflow-section.md) |
| Earlier decisions/results | [`README.md`](README.md), focused evidence reports, Git history |

The addendum retains `DRAFT` and some earlier pre-authorization wording;
its design has been provisionally approved and Stage 0 accepted, but later
implementation, native gates and final Increment 2 acceptance remain separate.

## Exclusions, stop conditions and next actor

**No implied authorization** for production/other-source edits, new SDL
lineage hooks, A1/B fallback, placement/focus/stack changes, authentication
or TLS/NLA policy, configured `-o`, protected packaging repositories, native
RDP/X11/KWin runs, service operations, installation/deployment, commit/push
or merge. Keep accepted Wayland v1, generic/TigerVNC and no-placement
invariants. Later native testing requires its own no-restart/no-`mw` gate.

**Stop/escalate** for unexpected source/build differences, inability to prove
checked initialization/property/show/XID semantics, unexpected mapped
predecessors or native recreation, uncertain cleanup, a contract conflict,
or any need to exceed the expressly authorized Stage 1 envelope. Never
weaken the positive identity predicate or silently broaden the task.

**Next actor:** Codex works only within the grant of permissions expressed in maintainer's prompt and
returns exact baseline/diff, validation and limitations for review.
**Next decision:** Maintainer reviews the Stage 1 proof-producer candidate
before authorizing packaging, broker integration, KWin resolver work or
native acceptance. **Increment 2 remains OPEN.**
