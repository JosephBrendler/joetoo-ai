# Step 1.5c.5d — Increment 2 X11 SDL viewer-role identity: scope supplement (DRAFT)

**Revision:** 2026-11-07, after Codex's read-only X11 source/archival review.  
**Reference checkpoint:** `a66d15377f0ebd01981d771f0bcbc5cb99c99d70` on `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`; verify current HEAD before use.  
**Authority:** Planning only, subordinate to `Step1.5c5_implementation_scope.md` §5A. No implementation, native/network tests, installation, new observer, service operation, API change, or Git publication is authorized by this draft. The maintainer has **accepted Increment 1**; see `step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md`.

## Objective and operational criterion

Extend the accepted broker-owned, launch-proven, exact-KWin-UUID, **registration-without-placement** behavior to X11 on `gmki91`. In recorded successful X11 SDL runs, a temporary and a persistent *normal* window shared the launched PID, application class and exact generated title marker but had **distinct KWin UUIDs**. The selector must identify the actual persistent desktop viewer without enrolling a predecessor or guessing from window order, disappearance, dimensions, focus or an elapsed delay.

**Preferred outcome: registration without any additional human interaction after viewer creation.** This matters for the planned *sequential* `joetoo-kwin -o -f CONFIG`: a compulsory click to distinguish a viewer would introduce an additional human gate into a long launch plan. Network authentication (NLA, VNC password) may already require interaction *before* the persistent viewer exists; removing that stage is not part of this increment. Future decisions about staging, identifying, placing and reporting pending-authentication windows, and continuing a sequential plan with outstanding prompts, are explicitly deferred to `increment2-deferred-authentication-workflow-section.md` (Increments 3–5). Do **not** infer that background launchers are required or approved.

This increment does not place/move/focus/stack windows, assert transport/login/GDM readiness, implement configured `-o`, change authentication policy or broaden the supported client set. Preserve accepted Wayland, generic and TigerVNC behavior, owner/source/PID/FD safeguards, bounded failure handling and no silent registered-UUID reassignment.

## Evidence baseline and provenance

- `README_remote_desktop_research.md` §3 and Appendix B record two consecutive exact-marker X11 windows under one PID with different UUIDs; the first was temporary, the second persisted through GDM and the GNOME desktop.
- The exact X11 activity pair reviewed by Codex is `joetoo-rdp-stage-a.Fm6EBB11.tbz2` and `joetoo-rdp-diagnostic.7DZi9Tfj.tbz2`. Its supplemental ledger links: unmarked credentials XID `146800710` (changed nonzero user time), marked temporary XID `146800721` (no activity latch), and marked persistent XID `146800729` (activity latch). Thus the composite **Candidate B** was demonstrated in this run; authentication-window activity does not satisfy the marker predicate. The companion had **three discovery gaps and two unlinked windows**, so this is not yet proof of a universally correct automatic selector.
- Codex inventoried 22 locally retained private archives, reporting 12 X11 Stage A, seven Wayland Stage A, and three diagnostic archives. It examined the above pair in detail; archive inventory **is not exhaustive event-by-event review**. Other X11 outcomes (`bPd7yxLi`, `UlffFIYm`, `MiECZCsg`, `NLq2gMGj` and earlier positive runs) may inform the mechanism and its counterexamples. Do not make private raw archives public or infer a missing field.
- `tools/joetoo-rdp-window-diagnostic.js` records KWin UUID/lifecycle/activation, **not** `_NET_WM_USER_TIME`; activation is labeled `intent:unknown`. The separate X11 activity companion obtained the user-time evidence and links native client XIDs to KWin UUIDs. Its presence is diagnostic evidence, not permission to add another production observer.
- Codex's source inspection found a **credible but not proven** explanation of same-title native-X11-window replacement: FreeRDP 3.32.1 creates an SDL window before renderer construction; SDL 3.4.18's renderer configuration can cause native X11 destruction/recreation while the SDL window object persists. An OpenGL renderer log appears near the archived transition, but is **not a trace identifying the actual replaced XIDs**.

## Candidate A — preferred, noninteractive exact-window role/completion evidence

**Research and design priority; feasibility not yet established.** Determine the least invasive source-grounded way to prove that a *particular native X11 client XID* is the persistent desktop viewer after successful renderer/window setup, and relate it independently to the live KWin UUID. The signal must identify the actual current native window, not merely an SDL window ID, a generic renderer-ready message, a desktop-size guess, a most-recent/last-surviving KWin UUID, or an operator-supplied UUID.

Examine in this order, without prejudging the outcome:

1. **Stock-client signal:** Does the installed/unmodified FreeRDP/SDL/KWin combination already expose an unambiguous exact-XID role/completion property, structured event, or message? Record negative findings and the precise source/version inspected. The presently reviewed ordinary WM properties and generic renderer log **do not** establish the target XID.
2. **Supported restricted renderer profile:** Could an approved unmodified-client renderer selection avoid the replacement path and permit a reliable role distinction? Assess reproducible behavior, supported options, graphical correctness, performance and security; do **not** infer that merely avoiding recreation proves viewer role. Changes to invocation/profile require separate authorization, and no native trial is approved now.
3. **Minimal creation-path instrumentation (only if needed):** Propose a narrowly scoped FreeRDP/SDL signal emitted **after successful renderer setup**, containing native client XID, window-generation/replacement lineage and a role-specific assertion. Specify handling of failed setup, repeated replacement and later recreation. Show how it travels through approved evidence channels and is independently validated by KWin. This is **a proposal for approval, not permission to patch FreeRDP**, alter Gentoo ebuilds or add a new daemon.

At commit time the broker must independently verify the exact native **client XID → current KWin UUID** link, the same launched PID/class/marker, live normal-window state, synchronized source and complete added/removal history. Source evidence about renderer setup is not a substitute for those checks. A superseded or reused XID cannot be silently adopted or substituted; a later native-window replacement must not retarget an already registered UUID. Unresolved histories, multiple role-qualified viewers, inconsistent generations, stale/missing evidence, source/owner/process loss, or failed cleanup terminate or refuse enrollment safely.

No stock-client Candidate A selector is presently established. **That does not establish Candidate A infeasibility.** Its restricted-renderer and narrow-instrumentation routes remain design choices pending further source-grounded evaluation and maintainer approval.

## Candidate B — demonstrated composite interaction/lifecycle fallback

Retain and respect the November 5 positive demonstration: a launch-owned marked temporary X11 window disappeared without a changed user-time latch, whereas a distinct marked persistent window acquired user activity; the concurrently observed credential window had activity but **lacked the exact marker**. This is meaningful *combined* evidence, not a standalone `_NET_WM_USER_TIME` test and not a reason to discard prior investigation.

A possible operator-selection contract would require all shared identity/lifecycle checks, explicit resolution of the temporary predecessor, a uniquely eligible live marked UUID, and **fresh positive content-free activity attributable to that specific surviving window after a valid post-predecessor baseline**. It must distinguish initial/startup timestamp, focus/activation, queued stale updates, timestamp wrap, XID reuse and a delegated `_NET_WM_USER_TIME_WINDOW`; the archived latch does not yet prove all these stronger production conditions. Do not capture keys, coordinates, clipboard or credentials. No activity means no registration; no timeout or last-survivor guess may replace it.

Candidate B may intentionally require the user to interact **after** viewer creation and so introduces an extra blocking gate in an otherwise sequential configured plan. It is **fallback-only**, potentially suitable as an explicitly user-mediated mode, and requires separate maintainer acceptance. It does not solve pre-viewer NLA/VNC authentication, which is handled in the deferred workflow design.

## Shared contract and evidence transport

Keep `step1.5c5d-sdl-interface-contract.md` **v1** as the accepted Wayland-only reference, including the four development operations (`BeginSdlRegistration`, `BindSdlRegistration`, `PollSdlRegistration`, `CancelSdlRegistration`), authenticated unique D-Bus owner, same-UID direct child, pidfd/start/executable checks, private stdout FD, synchronized KWin source, nonce/marker, bounded retries, terminal results and no placement.

Codex should propose a **separate Increment 2 X11 addendum**, not edit v1. It must explicitly address X11 profile selection (the current adapter, environment, backend reader and broker reject X11), whether wire signatures and `protocol:1` remain compatible, role evidence provenance and transport, exact client XID↔KWin UUID binding, role generation/expiry, terminal outcomes, event/FD budgets and cleanup. An unchanged method signature does **not** by itself authorize changed schema/semantics. Do not accept a caller-selected UUID or trust a raw log line without the existing process/FD/lifecycle corroboration. Preserve accepted Wayland semantics unchanged.

## Acceptance gates to propose, not execute

**Headless:** faithful broker/registry path for positive A completion, temporary-only/renderer failure, multiple recreations and role-qualified windows, lost/contradictory/stale role generation or XID reuse, source/owner/process loss, unrelated/preexisting viewers, duplicate ownership, cancellation/expiry and inert late callbacks, cross-request retention, and no placement. Preserve all existing 179/614/99 accepted-suite coverage (counts are the previous checkpoint, not a promised future count). For optional B, also test unmarked credential activity, temporary-window activity, initial/stale user-time, post-predecessor baseline, missing activity and wrap/delegation.

**Maintainer-native on `gmki91`, later and separately authorized:** prove real `x11` backend and real child/XID/KWin UUID evidence; verify absence of premature temporary-window registration, correct persistent registration without a new click for A, unrelated-viewer isolation, bounded failures and no placement. Any native procedure must begin with explicit no-restart/no-`mw` conditions and protect private logs. No native acceptance follows from archive/source review alone.

## Current read-only Codex design-review deliverable

Produce a concise, source-grounded **decision memo** addressing A-stock vs A-restricted-renderer vs A-minimal-instrumentation vs B-operator-selection; note what is observed, inferred, unavailable or untested. Compare exact-XID proof, false positives, complexity, performance/packaging impact and ability to avoid an *additional* human interaction gate. Give the narrowest viable X11 contract-addendum proposal and its minimum headless/native acceptance matrix. Focus detailed additional archive review on runs that can corroborate or contradict the renderer-recreation hypothesis; inventory alone is not proof. Stop at the maintainer's decision boundary: no repository edits, live tests, client changes, contract edits or publication.

## Deferred downstream workflow — do not expand this increment

The authoritative open decision is [`increment2-deferred-authentication-workflow-section.md`](increment2-deferred-authentication-workflow-section.md): staging/labeling or separately identifying and placing temporary NLA/VNC prompts, managing pre-viewer authentication, pending-status console alerts, sequential `-o -f CONFIG` progression, bounded per-entry state and later GDM/NLA/VNC idle behavior. This is primarily Increments **3–4**, with transport/timeout verification in **5**. The planned workflow must be designed to move beyond a *pending-human-action stage* under an approved contract, rather than claiming every launched RDP connection is already registered; this is not background-launcher authorization. No approach to pending-prompt placement, continued scheduling or timeout semantics is selected yet.

## References

- `Step1.5c5_implementation_scope.md` §5A; current `HANDOFF.md` dispatcher.
- `step1.5c5d-sdl-interface-contract.md` v1 (accepted Wayland implementation).
- `step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md` (maintainer acceptance).
- `README_remote_desktop_research.md` §3/Appendix B and original historical HANDOFF.
- `increment2-deferred-authentication-workflow-section.md` (future authentication/placement/workflow choice).
- `tools/joetoo-rdp-window-diagnostic.js`, `tools/joetoo-rdp-x11-use.py`, `tools/joetoo-rdp-x11-use.js` (confirm exact current paths/availability); private X11 archives remain local.
- Relevant installed FreeRDP 3.32.1 / SDL 3.4.18 / KWin 6.7.5 source and official SDL/EWMH specs; verify exact versions and line references in Codex's review.
