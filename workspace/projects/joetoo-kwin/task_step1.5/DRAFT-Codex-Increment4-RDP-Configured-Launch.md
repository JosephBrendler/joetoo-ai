# DRAFT Codex task — Step 1.5c.5d Increment 4: configured serial SDL RDP `-o` integration

**Draft for maintainer review / explicit authorization; not an instruction to begin unapproved edits, native execution, commits or publication.**

Repository: `JosephBrendler/joetoo-ai`  
Branch: `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
Verified reference baseline: `599f7f38d141b2b332ca52f0daf4c7ce3c8ead43` (fetch and verify HEAD; do not reset or overwrite later maintainer edits).

## Context and evidence

Read repository-root `AGENTS.md`, `workspace/AGENTS.md`, `workspace/README.md`, the applicable project `AGENTS.md`, `ARCHITECTURE.md`, `task_step1.5/HANDOFF.md`, `task_step1.5/README.md`, `Step1.5c5_implementation_scope.md` and `step1.5c5d-increment3-strategy-decision.md`. Prefer active source, not archive/POCs. New evidence to read:

- `task_step1.5/step1.5c5d-increment3-native-wayland-smart-sizing-immediate-placement-2026-11-10.md`
- `task_step1.5/step1.5c5d-increment3-immediate-placement-transcript-2026-11-10.log`
- Earlier failing diagnostic, **not superseded**: `task_step1.5/step1.5c5d-increment3-native-wayland-placement-trace-2026-11-09.md`

Maintainer observations on `q552u01` (KWin native Wayland): `54df85f` fixed development-only `/size:1024x768` and `/smart-sizing:800x600` enabled locally scaled full GNOME desktop, interactive resize, and exact KWin frame `(100,100) 800×628`. At harness revision `599f7f3` 789 Python + 161 JavaScript tests passed; a fresh registered exact UUID `da0a37a4-aed1-4a43-b738-b10a37c87775` was submitted for `(1,1) 800×628` **6.43 ms after registration**, then broker-verified at **116.16 ms** after registration. GDM content appeared later, while the window had already moved. **Do not add GDM-readiness waits, fixed delays, resize retries or a KWin setter rewrite based on unsupported causal speculation.** `remote_session=unverified` is intentional. One earlier 15-second placement failure remains unexplained; success is one native run, not statistical reliability.

## Proposed objective — subject to maintainer approval

Prepare a minimal, reviewable **Increment 4 candidate** to make SDL FreeRDP a peer of the established serial configured `joetoo-kwin -o` managed launch workflow. The confirmed plan's SDL recipe should reserve the appropriate logical desktop/slot, launch one owned client, positively register the persistent viewer's **exact KWin UUID**, request one-shot placement using the planner's geometry and existing KWin/broker machinery, then participate in the existing `under → panel → over` group stacking/focus policy. The single successful development harness demonstrates the mechanical path; it is not itself the production recipe.

### Required design/implementation boundaries

1. **Serial**: one pending confirmed remote viewer launch/registration/placement at a time; no Option D concurrency, prompt staging or remote session reconnection implementation. Reuse the existing registered SDL viewer selectors, launch ownership, PID/FD, source, UUID and cancellation safeguards. Do not select windows by active-window, class-only, PID-only, title-only, or by GDM content.
2. **Planner owns geometry**: consume the canonical `-o` desktop, derived slot, region dimensions and layer from existing configuration and planner output. Do not duplicate the allocator. Distinguish *outer KWin frame size*, *local SDL client area*, *remote RDP desktop resolution*, and scaling. The fixed `/size:1024x768` and `/smart-sizing:800x600` are **development probes**, not acceptable production hardcoded policy. Propose validated configurable remote-resolution/scaling semantics, defaults, explicit bounds and tests before implementation changes needing an architecture decision; preserve chosen X11/Wayland behavior and avoid assuming 28 pixels of decorations universally.
3. **Placement and stacking**: after positive exact-UUID registration, submit and verify exactly one initial placement (not a second manual release); finalize cohort stacking/focus with the current `under → panel → over` model without continuous repair. A remotely rendered GDM greeter is content inside the viewer, not a local viewer readiness signal. Do not conflate authenticating NLA, seeing GDM, window presence, geometry verification or remote-session usability.
4. **Human interactive timing**: allow the maintainer to spend minutes in NLA/GRD authentication without arbitrary automation killing a viable owned client. Mechanical correlation, D-Bus calls, assignment/verification and safe cleanup remain bounded; distinguish a user wait from actually failed client/transport. Preserve TLS/server validation and do not inject credentials or bypass trust checks.
5. **Lifecycle and usability gaps**: document the current **same-slot `presence=missing` historical reservation** (new registration currently raises slot conflict) and a broker that can report OpenRC `started` shortly before its D-Bus name is available. Do **not** silently delete historical records or weaken fail-closed ownership. Propose a separately reviewable safe release/reconciliation/API policy or maintain a clear preflight/blocked state. Ensure operator diagnostics identify a sanitized error name/reason instead of only `FAILED: RuntimeError` when practical, without leaking private RDP logs, hostnames or credentials.
6. **Peer regression**: do not change TigerVNC transport/launcher semantics, Konsole/SSH return-to-original-shell behavior, Dolphin SFTP, generic observation source, D-Bus public APIs or X11 selectors incidentally. Any needed cross-cutting change must have explicit rationale and focused regression coverage.

### Deliverables and stop conditions

**First deliver a short source-grounded design**: actual files/functions/interfaces; recipe syntax and config policy; end-to-end operation and error/timeout states; contract alignment with `ARCHITECTURE.md`; proposed minimal diff/test files; explicit decisions requiring maintainer approval. **Pause for a maintainer decision on material policy questions before coding them.** Do not use this draft as authorization for new interfaces or security changes.

Once the maintainer authorizes the bounded implementation, supply a complete reviewed diff and headless tests for the happy path, pending NLA/credential wait, failed/cancelled/ambiguous viewer, UUID mismatch, slot conflicts, sequential two-viewer plans, frame nonconvergence, absent broker D-Bus name and unaffected VNC/Konsole behavior. Make terminal placement and remote outcomes independently truthful. Run permitted headless tests only; report exactly what passed/failed and the current revision.

**Hard stops:** no installation/restart/host administration, remote RDP login, native X11/Wayland testing, commit, push, PR, merge, official `joetoo`/`joetoo-upstream` edits, Option D scheduler or speculative architecture rewrites without separate maintainer authorization. Preserve user edits and ask for the next review/publish/native-testing gate explicitly.

**Next actor:** Codex proposes a minimal design and file list; maintainer reviews/authorizes candidate code and later controls native validation and signed publication.
