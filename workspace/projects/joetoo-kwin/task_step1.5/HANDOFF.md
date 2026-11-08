# Step 1.5 — Active task dispatcher

**Purpose:** This file identifies the *current* task, its authority, stop conditions and next decision. It is **not** a development history or evidence report. For earlier work, follow the references below and Git history; do not treat an old HANDOFF revision as current authorization.

## Current dispatch — Step 1.5c.5d, Increment 2 / A2 Stage 0 (2026-11-07)

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Published pre-dispatch checkpoint:** `b8d9d943e87d56912081284e3a73e6f8c9239d25` (published A2 contract addendum). Verify the actual branch, HEAD, working-tree status, and governing instructions before acting; this SHA is a reference checkpoint, **not** a requirement to reset or overwrite newer work.

**Milestone state:** Increment **1 — native-Wayland SDL registration without placement — is formally ACCEPTED and COMPLETE**. Increment **2 — X11 SDL viewer-role identity — is NOT implemented or accepted**. The maintainer has selected **A2**, noninteractive hidden desktop-viewer initialization with positive native-client-XID/nonce evidence and independent KWin UUID correlation, as the **provisional implementation contract**. The addendum specifies proposed mechanisms and future gates; approval is **not** a general implementation grant.

**Current actor and authority:** Codex is authorized for **Stage 0 only: one isolated, headless JavaScript resolver-protocol test** as bounded in [A2 addendum §7.1](step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md#71-proposed-stage-0--test-only-authorization-envelope-not-granted). This dated maintainer dispatch is the explicit Stage 0 grant; the addendum's older “not granted” wording describes its status before this dispatch. **No Stage 0 result is yet claimed.**

## Required reading — references, not reproduced history

| Purpose | Authoritative reference |
| --- | --- |
| Repository policies and project workflow | Repository-root, `workspace/`, and project `AGENTS.md`; `workspace/README.md` |
| Product architecture and milestones before this stage | [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`README.md`](README.md), [`Step1.5c5_implementation_scope.md`](Step1.5c5_implementation_scope.md) §5A |
| **Current Increment 2 A2 contract and Stage 0 bounds** | [`step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md`](step1.5c5d-sdl-x11-a2-contract-addendum-DRAFT.md) §§1–8, especially §§5.4–5.6 and **§7.1** |
| Increment 2 problem, historical X11 evidence, A2 priority and B fallback | [`step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md`](step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md), [`README_remote_desktop_research.md`](README_remote_desktop_research.md) |
| Prior **accepted** increment and original Wayland interface | [`step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md`](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md), [`step1.5c5d-sdl-interface-contract.md`](step1.5c5d-sdl-interface-contract.md) |
| Pending NLA/VNC staging, placement, sequential `-o -f CONFIG` and timeouts — **not this stage** | [`increment2-deferred-authentication-workflow-section.md`](increment2-deferred-authentication-workflow-section.md) |

The linked acceptance/evidence reports, task READMEs and Git history contain past commands, outcomes, native gates, PKI details, and prior authorizations. Consult the appropriate source when relevant; do not reconstruct that narrative in HANDOFF. The current authorization here controls the actor's write/test scope; documents labeled DRAFT do not independently grant implementation authority.

## Stage 0 — exact authorization

**Only new repository file authorized:** `tests/test_sdl_x11_resolver_protocol.js`. Keep synthetic vectors/fixtures inside this file. Follow existing `node:test`, `vm` and fake-KWin patterns in `tests/test_step1_3a.js` and `tests/test_rdp_x11_use.js` **without modifying either file**.

- Execute **existing** `joetoo-kwin-resident.js` observation code inside a restricted Node VM with fake workspace, windows, Qt-style signals, timers and `callDBus`. Reject any placement, focus, stack, credential or other GUI mutation.
- Model **future** A2 helper/broker handshake as **explicitly test-only protocol fixtures**, not working production code. Distinguish observations of the existing resident from assumptions injected by the fixture.
- Cover automatic pre-spawn readiness and post-READY mapping without a shortcut or human input; positive ordered traces; actual-versus-modeled sender connection, well-known-to-unique destination resolution and owner changes; missing/delayed/reordered lifecycle evidence and receipt-fence rejection; replay, stale/wrong-source/expired challenges, cross-job isolation and duplicates; lost callbacks, late load/unload/reap acknowledgements and cleanup-uncertain blocking; no unauthorized window operations.
- Include bounded native-property **schema vectors** (including `WM_CLASS` instance/class ordering and `_NET_WM_NAME` exact marker) if feasible in the one file. Do **not** claim a native XCB parser was tested.
- Run the focused new test and applicable **existing headless JavaScript** regression suite only. Report exact commands, test counts, failures and `git diff --check`. No claim of a prior suite count as the new result.

**What Stage 0 cannot prove:** Real Qt signal ordering, D-Bus transport sender/destination/receipt ordering, future broker/helper behavior, XCB ABI/authorization, FreeRDP hidden initialization, native XID→UUID identity, OS reaping or actual Increment 2 registration. These require later, separately authorized stages/gates.

## Hard exclusions and stop conditions

**No changes** to production code, resident, broker, FreeRDP/SDL, ebuilds, launcher, registry, existing tests, scope, contract, HANDOFF, scripts, configuration, installation, or other repository files. No native GUI/KWin/RDP sessions, real bus or X server test, network operation, service restart/reload, `mw`, deployment, commit, push, PR or merge. Stage 0 does **not** authorize Increment 2 implementation, placement, authentication staging, configured `-o` or production security changes.

**Stop and report** if the checkout differs unexpectedly from the authorized baseline; a relevant governing document is unavailable; the one-file test cannot exercise the existing resident safely; the proposed model permits success with incomplete observation, stale sender/source/challenge or unresolved cleanup; source evidence contradicts mandatory ordering; regression testing finds a product defect; or completing the test would require any excluded action. Do not weaken the positive identity/receipt predicate or modify production code to obtain a passing test.

## Required Codex return / next maintainer decision

Report branch, actual HEAD and working-tree baseline; the single-file diff; focused and applicable headless-JS test commands/counts/results; tested positive and negative traces; **what existing code was actually executed versus what was modeled**; outstanding Qt/D-Bus/native proof gates and any exact contract contradiction. Leave changes **uncommitted/unpushed**, then stop. The maintainer will review Stage 0 before separately authorizing any subsequent source, build, or native-testing envelope.
