# Step 1.5 — Active task dispatcher

**Task / current gate:** Step 1.5c.5d — **Increment 4 COMPLETE AND MAINTAINER ACCEPTED (2026-11-11)**; **Increment 5 RDP security/native closure remains to be reconciled**. Step 1.5d integration and official Gentoo packaging are separate work.

**Maintainer decision:** Stage 4 (configuration layering, optional user-owned `eselect` profiles, template/reference and severity-aware `show_config`) is accepted. Earlier Increment 4 Stages 1–3 are accepted. This HANDOFF records acceptance and directs the *next review*, not a new implementation authorization.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Baseline:** The maintainer reports pushing the final Stage 4 implementation and ShellCheck refinements. Before further work, verify actual task-branch HEAD and clean/dirty status; do not assume previous documented hashes still identify the newest implementation. Preserve any maintainer changes and local drafts.

## Accepted evidence and current behavior

- Increment 4 **Stages 1–2 ACCEPTED**: production configured SDL RDP frontend/worker, exact-UUID registration and placement, sequential `-o`, native X11/Wayland trials, shared cohort stacking and viewer lifecycle. [Stage 2 evidence](step1.5c5d-increment4-stage2-native-acceptance-2026-11-10-11.md).
- **Stage 3 ACCEPTED**: 300000-ms default RDP/VNC viewer-readiness deadlines; known-clean failure continuation only after positive terminal broker/worker cleanup; fail-closed uncertainty; success-only cohort order; partial plans return incomplete status. Native `gmki91` X11 and `q552u01` Wayland each demonstrated `completed [2], failed [1], skipped [0]`. [Stage 3 evidence](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md).
- **Stage 4 ACCEPTED**: CLI built-ins → optional system/user defaults → per-run plan (`-f` or existing user/system selection) → CLI overrides; fail-closed loading; optional non-root user-owned `eselect joetoo-kwin list|show|set`; short template + annotated reference and packaging-ready instructions; quiet notice/info/debug `show_config` (including `rlv.config`, pseudo-booleans and active profile asterisk). The maintainer's isolated-XDG native X11 tests verified 70%/65% profile overrides over 75% user defaults and 87% built-ins; name/number selection, unchanged selected profile with `-f`, invalid-selection rejection, and a real Dolphin + Konsole `2/2` managed launch with successful initial layout. Local initial integration reported 903 Python / 161 JS PASS and service install/check/introspection; Codex's final polish reported 911 Python / 161 JS PASS and 78 focused PASS; maintainer's final `validate_scripts joetoo-kwin -l` reported clean success. The final headless 911/161 report and post-polish native-display limits are distinguished in [Stage 4 evidence](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md).
- Existing remote authentication, TLS/NLA trust, GDM state, KWin window identity and placement remain **separate** assertions; local viewer completion does not prove the remote login/certificate/security state. VNC/RDP worker normalization and async/Option D remain deliberately deferred to version 2.

## Current next actor and objective — Increment 5

**Next actor:** Maintainer reviews and explicitly issues the [draft Increment 5 evidence-reconciliation Codex task](step1.5c5d-increment5-evidence-reconciliation-codex-task-DRAFT.md) if desired. **No further Stage 4 development is pending.**

**Next objective:** Determine whether already collected GNOME Remote Desktop, private-PKI, TLS/NLA, authentication and native X11/Wayland observations meet the accepted Increment 5 security/native closure criteria. Start by building an evidence-to-requirement matrix, not by changing code or commissioning another broad implementation pass. Accept what is supported; specify only concrete missing native checks or genuine blockers. Use [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md), [architecture](../ARCHITECTURE.md), [task evidence index](README.md), [GNOME study](README_gnome_remote_desktop.md), [PKI record](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md) and existing RDP test records.

**Permissions / stop conditions:** The HANDOFF alone does not authorize Codex execution, native experiments, host services, edits to `joetoo`/`joetoo-upstream`, commits, pushes, PRs, merges or packaging deployment. Preserve exact UUID ownership, fail-closed behavior, managed-slot reservations, existing OpenRC separation and accepted Stage 4 configuration semantics. Report evidence gaps, source/baseline conflicts or a material security issue rather than silently expanding scope.

## References

- [Task history and evidence index](README.md)
- [Stage 4 native acceptance](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md)
- [Stage 3 X11/Wayland native acceptance](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md)
- [Stage 2 native acceptance](step1.5c5d-increment4-stage2-native-acceptance-2026-11-10-11.md)
- [Increment 5 Codex evidence-reconciliation draft](step1.5c5d-increment5-evidence-reconciliation-codex-task-DRAFT.md)
- [Step 1.5c.5 implementation scope](Step1.5c5_implementation_scope.md)
- [Project architecture](../ARCHITECTURE.md)
- [Increment 4 maintainer decisions](step1.5c5d_Increment_4_decisions.md)
