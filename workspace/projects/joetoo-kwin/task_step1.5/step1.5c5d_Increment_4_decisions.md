# Step 1.5c.5d Increment 4 — Maintainer decisions (2026-11-10)

**Status:** Maintainer design decisions for a proposed configured SDL FreeRDP `-o` implementation. This file records policy; it does **not** authorize source edits, native operations, commits, or publication. Source of truth for implementation remains `../ARCHITECTURE.md`, scoped task requirements, and the active HANDOFF. Existing RDP development harnesses are evidence tools, not production launchers.

## Modularity and implementation choices

| Layer | Current implementation | Codex proposal | ChatGPT recommendation | Maintainer decision |
| --- | --- | --- | --- | --- |
| Recipe grammar | Common four/five-field format | Add `sdl-freerdp\|rdp` | Preserve existing format | **Approve**: `PROGRAM=sdl-freerdp`, `MODE=rdp` |
| Target and ports | Per-program target validation | RDP `rdp://USER@HOST[:PORT]` | Optional endpoint port in target, with client-specific default | **Approve**; see `TARGET` grammar in architecture |
| Offline validation | Common planner plus specific validators | Add RDP target/settings validator | Keep validation separate from launch | **Approve** |
| Geometry calculation | One common planner | Unchanged | Preserve shared allocator | **Approve** |
| Launch orchestration | Common `-o`; specialized VNC path | Add RDP dispatch | Minimal additional dispatch; do not call POC executables | **Approve**; cross-client normalization/consolidation is Version 2 |
| Application ownership | Generic apps launched directly; VNC frontend/worker | Add RDP frontend/worker | One production RDP executable entry point, as with VNC | **Approve**; see file layout below |
| Authentication/readiness wait | Separate bounded RDP/VNC intervals | Unbounded awaiting-viewer phase | Finite configurable five-minute default | **Approve five-minute default** for RDP and VNC; no unbounded phase in Increment 4 |
| Window identification | Generic, VNC-role, and SDL-specific positive selectors | Reuse each existing selector | Preserve their client-specific identity proofs | **Approve** |
| Placement | Shared broker/KWin exact-UUID machinery | Reuse existing | No duplicate geometry algorithm | **Approve** |
| Cohort stacking/focus | Common initial layout after group entries | Reuse existing | `under → panel → over` unchanged | **Approve** |
| Windowing backend | Explicit SDL Wayland/X11 profile | Explicit per-host selection | User-facing `rdp_windowing_backend=auto\|wayland\|x11`; keep SDL-specific internals | **Conditional approve**: verified `auto` if simple; otherwise explicit per-host setting now |
| Remote scaling | Client-specific; RDP smart sizing tested | Configurable remote/initial dimensions | Remote pixels and final outer frame remain distinct | **Approve** configurable dimensions and smart sizing; do not change planner |
| Missing-window reservations | Historical `missing` records reserve original slot | Keep existing | Permit verified termination to release slot without erasing history | **Conditional approve** if narrow; otherwise preserve current guard and defer |
| Failure/cleanup handling | Serialized broker can report unresolved transactions | Existing conservative stop | Continue after a known terminal/clean result; never override Busy/unknown owner | **Approve safe continuation only**; see below |
| Async multiple missions | Not implemented | Defer Option D | Defer | **Version 2**; retain serial plan now |

## Production RDP modules — parallelism without renaming the POCs

The VNC production path has one executable (`libexec/joetoo_kwin_vnc_launch.py`) containing *both* short-lived frontend and persistent worker, plus imported `joetoo_kwin_vnc_target.py` (parser/settings) and `joetoo_kwin_vnc_identity.py` (identity helper). These are modules, **not three chained launch executables**.

**Preferred RDP production design:** reuse the existing `libexec/joetoo_kwin_rdp_launch.py` as the single executable frontend/worker entry point (parallel naming to VNC), keeping its current import-safe broker/identity/SDL support functions intact or extracting only what is genuinely necessary; add `joetoo_kwin_rdp_target.py` for offline target/settings parsing. Codex should verify the existing broker imports and test compatibility before choosing this layout. If converting the existing module safely would require excessive churn, return a focused alternative for maintainer approval rather than silently adding another production orchestrator. A separate `joetoo_kwin_rdp_identity.py` is **optional**, not an Increment 4 prerequisite.

The three current `tools/joetoo-sdl-*.py` registration, placement and immediate-placement scripts remain **development/diagnostic harnesses**. The production launch path must not shell out to or chain these tools. Reuse tested logic through importable implementation functions or focused extraction as needed. Do not add a generic VNC/RDP framework now; normalize/consolidate those peer capabilities in Version 2 after independent native acceptance.

## Near-term behavior contracts

| Question | Decision / boundary |
| --- | --- |
| Recipe | `DESKTOP\|sdl-freerdp\|rdp\|rdp://USER@HOST[:PORT][\|LAYER]`; username explicit, RDP port default 3389 |
| Endpoint ports | Optional `[:PORT]` in URL targets; application-specific parser translates port to invocation. Konsole SSH currently has **no explicit recipe-port syntax**; its TCP reachability check uses 22 (separate limitation). |
| Windowing backend | User-facing `rdp_windowing_backend` (not RDP client selection); verified `auto` if straightforward, else `wayland`/`x11` explicit. Retain SDL's actual `SDL_VIDEO_DRIVER` contract internally, without global variable refactor. |
| Initial sizing | User-configurable `rdp_remote_width=1024`, `rdp_remote_height=768`, `rdp_smart_sizing=$TRUE`, `rdp_initial_client_width=800`, `rdp_initial_client_height=600` as proven initial defaults; validate offline. |
| Final local geometry | Existing planner exclusively owns desired KWin **outer frame**; no hard-coded window-decoration subtraction. |
| Authentication/viewer wait | `rdp_registration_timeout_ms=300000` and `vnc_viewer_ready_timeout_ms=300000` proposed defaults; these bound viewer identification, **not** demonstrated credential state. Preserve finite identity/history budgets and bounded mechanical operations. |
| Known-clean timeout/failure | Cancel pending broker request, terminate only owned pre-registration client/tunnel, confirm terminal result/cleanup, report failed recipe, advance through the existing serial plan. |
| Unresolved transaction | Prefer continuation of unrelated entries **only where the broker can positively certify next-operation eligibility**. Do not bypass Busy, source/owner uncertainty, active placement, or potential slot conflict; stop safely if independence cannot be established. |
| Registered viewer placement failure | Report placement separately; do not silently destroy enrolled viewer or misreport remote session. Decide continuation from known broker terminal/ownership state. |
| Remote GDM | Local NLA leads to positively identified viewer, then placement. GNOME greeter login takes place inside the viewer **after** placement and never blocks configured `-o`. |
| Broker restart | Existing windows/workers can survive, but new broker in-memory `ListManaged` is empty; no automatic ownership re-adoption in Increment 4. |
| Missing vs. terminated | Release the **slot**, not the history, only with trustworthy closure/termination proof. Conservative `missing` continues reserving until such proof exists. Scoped improvement conditional on small reviewable change; otherwise defer. |
| Version 2 | Mission-scoped ownership across authentication windows/viewers; async and out-of-order completion; cancel versus bad-password retry policy research; VNC/RDP lifecycle normalization. |

**Staged Increment 4 review:** (1) offline target/settings/backend validation; (2) one production RDP frontend/worker integrated into `-o`, with first-class registration/placement/cohort result; (3) finite five-minute RDP/VNC wait defaults, known-clean failure continuation, and optionally narrow verified slot release. Preserve prior working X11/Wayland, Konsole, Dolphin and VNC behavior. No source implementation or publication approval is granted by this document.

## Carried-forward strategy from the superseded Increment 3/4 record

This section incorporates earlier **still-applicable** decisions from the
[2026-11-08 strategy record](step1.5c5d-increment3-strategy-decision.md).
Where the earlier record permitted open-ended human waits, the finite
five-minute viewer-readiness policy above **supersedes** it.

| Strategy | Rationale / limitation | Current decision |
| --- | --- | --- |
| Sequential interactive launches | Reuse established serialized ownership and placement; a pending credential dialog delays later entries | **SELECTED for Increment 4**, with the configurable finite readiness deadline and known-clean failure continuation above |
| Launch all remote clients and stage prompts on a control desktop | Would permit concurrent human authentication, but needs independently proven prompt ownership, source/slot association and safe cancellation | **DEFER to Version 2 / Option D** |
| Queue remote authentication while continuing local launches | Could improve throughput, but adds scheduling, reservation, transaction and invocation-lock complexity | **DEFER to Version 2 / Option D**, after latency/usability evidence |

- **Identity timing is not human waiting.** The accepted 500 ms native-X11
  persistent-viewer identity-settling interval starts when a UUID begins
  qualifying as a viewer. It is **not** a connection/authentication timeout
  and must never substitute for the separately configured viewer-readiness
  deadline. Preserve the known temporary-X11-viewer counterexample.
- **Different windows and outcomes remain separate.** SDL NLA dialogs and
  VNC/SSH prompts may precede a persistent managed viewer; none may be
  enrolled merely by shared PID, class or caption. A remote GNOME GDM greeter
  is content *inside* the RDP viewer, not a separate local KWin window.
  Authentication, registration, placement and remote usability are
  independent outcomes and may be reported only to the extent verified.
- **Security and external constraints remain intact.** Do not inject or save
  credentials, weaken certificate/SSH host-key verification, or assume a
  remote server will maintain an idle authentication session indefinitely.
- **Milestone sequencing remains:** Increment 4 configured serial `-o`;
  Increment 5 and Step 1.5d security/native integration and broader
  acceptance; Version 2 / Option D optional prompt staging, readable target
  labels, cascading prompt geometry, queuing and out-of-order completion
  after measured need and separately approved design. Earlier Increment 2/3
  evidence is historical, not permission to reimplement it.

This record states product decisions only; implementation, native testing,
commits, publication and merge require separate authorization.
