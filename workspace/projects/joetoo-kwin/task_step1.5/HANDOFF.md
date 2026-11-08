# Step 1.5 — Active task dispatcher

**Purpose:** Identify the current task, operative authority, stop conditions and next decision. This is **not** a chronological history. Historical research and results belong in the linked documents and Git history. Older HANDOFF revisions are not authorization.

## Current dispatch — Step 1.5c.5d / Increment 2 / stock SDL X11 A1/C feasibility (2026-11-08)

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Prior verified checkpoint:** `170ab3a0e23bf71fdf333864e8781849a2b8647c` (last verified **before** the A2-to-A1/C document transition). The authoritative checkpoint is the **actual HEAD after the maintainer's transition commit**. Verify branch, current HEAD, status and applicable `AGENTS.md` at the start. Never reset or overwrite newer work.

**Maintainer decisions and current state:**

- **Increment 1 — native-Wayland SDL registration without placement:** formally **ACCEPTED / COMPLETE**. Preserve existing contract and behavior.
- **Increment 2 — native Plasma X11 SDL viewer identity:** **OPEN**, not implemented or accepted. Legacy compatibility remains useful on `gmki91`, but is not the project's longer-term Wayland path.
- **Candidate A2 Stage 1 — FreeRDP C++ proof producer:** **ABORTED / authorization withdrawn** due to unacceptable downstream FreeRDP patch maintenance for legacy X11. No FreeRDP/SDL source patch, experimental upstream build, A2 READY/nonce, or automatic A2 resolver work is authorized. The renamed [A2 contract — ABORTED](step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md) is historical.
- **A2 Stage 0 synthetic protocol research:** remains **ACCEPTED / COMPLETE**, 2026-11-08; published corrected test `../tests/test_sdl_x11_resolver_protocol.js`, 46 focused + 99 existing = 145 combined JS PASS on independent `gmki91` verification. It is **not** native X11 evidence and does not validate A1/C.
- **Active replacement direction:** **A1** = brief experiment with *supported stock* FreeRDP/SDL renderer settings; **C** = broker-only, X11-specific, configurable bounded candidate-persistence heuristic. Consider A1 + C together if evidence supports it. **B** remains a separately gated operator-interaction fallback. Do not restart an A2 design process.

## Current Codex assignment — Gate F, read-only feasibility

The maintainer's accompanying **A1/C feasibility prompt is the active authorization**. Proceed within that prompt; do not wait for another task prompt. HANDOFF alone authorizes no implementation, build, native experiment or modification.

Review existing archived X11 lifecycle evidence, beginning with the known November 5 diagnostic pair; compare actual temporary/persistent UUID lifetimes where timestamp provenance permits; evaluate provisional **250/500 ms** thresholds; identify stock renderer options from the installed binary/local source **without assuming they exist**; inspect existing broker registration and `PollCorrelation()` timing. Return a short **A1 GO/NO-GO, C GO/NO-GO**, confidence, failure cases, and smallest justified next action. Do not inventory every archive or produce another extensive design report.

**Timer rule:** For prospective C, **one** broker-local monotonic candidate eligibility interval, proposed `rdp_x11_identity_settle_ms = 500` for evaluation, centrally configurable after review. It starts at **first full qualification of a specific new UUID**, not necessarily its `added` event. It runs concurrently with normal observation; **no second 0.5-second `PollCorrelation()` wait**. Current `PollCorrelation()` is diagnostic and starts on its first matching poll; it is **not** a registration gate. Any implemented X11-only exception must remain confined to the governing scope §5A / A1-C addendum §5; accepted Wayland v1 remains strict.

## Governing references, not reproduced history

| Purpose | Document |
| --- | --- |
| Policy and architecture | Root, `workspace/`, project `AGENTS.md`; `workspace/README.md`; [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| **Governing scope + narrow fixed-delay exception** | [`Step1.5c5_implementation_scope.md`](Step1.5c5_implementation_scope.md) §5A, Increment 2 |
| **Active draft and gates** | [`step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md`](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md) §§1–6, especially §§2, 4–6 |
| Legacy X11 evidence / candidate B | [`step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md`](step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md); [`README_remote_desktop_research.md`](README_remote_desktop_research.md) |
| Aborted A2 design / accepted synthetic research | [`step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md`](step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md); [`../tests/test_sdl_x11_resolver_protocol.js`](../tests/test_sdl_x11_resolver_protocol.js) |
| Accepted native-Wayland registration | [`step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md`](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md); [`step1.5c5d-sdl-interface-contract.md`](step1.5c5d-sdl-interface-contract.md) |
| Later authentication, placement and configured `-o` | [`increment2-deferred-authentication-workflow-section.md`](increment2-deferred-authentication-workflow-section.md) |

## Stop conditions / next decision

**Read-only Gate F:** No source/docs/tests edits, no FreeRDP/SDL build or patch, no native X11/Wayland GUI or RDP connection, no real bus/KWin calls, no configuration/service/packaging/installation changes, no commit/push/merge. Previously retained archives and installed-source evidence may be inspected **read-only**. No speculative security downgrades. If timestamps, supported renderer options or exact source state are absent, report **unknown/NO-GO for that subtest**, not invented evidence or extended research.

**Stop and report** an observed temporary window surviving the proposed threshold before replacement, contradictory provenance, insufficient comparable timestamps, source/ownership/history ambiguity, or the need for an excluded action. A window surviving 500 ms is **not** positive completion proof, and a few successful trials are **not** a universal guarantee.

**Next actor:** Codex completes the already-issued narrow Gate F assessment and stops. **Next decision:** Maintainer chooses whether to authorize a small, explicitly described `gmki91` native A1 comparison, a small X11-only broker C prototype, or no further Increment 2 work. Native runs and implementation are **separate gates**; Increment 2 remains **OPEN**.
