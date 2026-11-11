# Step 1.5 — Active task dispatcher

**Task / current gate (2026-11-11):** Step **1.5c.5d CLOSED — ALL INCREMENTS INCLUDING INCREMENT 5 MAINTAINER ACCEPTED**. Managed SDL FreeRDP now has native X11/Wayland acceptance, configured `-o` placement/lifecycle acceptance, configuration layering, and tested strict security defaults. **Next:** milestone PR/review into `main`; then separately authorized Step **1.5d** integration. Official Gentoo ebuild packaging remains separate.

**Maintainer decision (2026-11-11):** “I accept Increment 5 and closing Step 1.5c.5d.” Strict built-in `rdp_security_protocol=nla` -> `/sec:nla`, `rdp_certificate_policy=strict` -> `/cert:deny`; alternatives `negotiate` and `prompt` respectively omit `/sec:` and `/cert:`. Maintainer-proven native strict positive FQDN connection and negative automatic certificate-name refusal (with verified child/broker cleanup) are recorded in [final Increment 5 acceptance](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md). Earlier [pre-policy native observations](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md) remain valid historical evidence, not the final security-policy disposition.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Baseline:** Maintainer reports publishing the approved Increment 5 implementation and prior documentation. Codex reported pre-publication HEAD `94d4bea747c1dda618da76a842ac9cfeb3c651f4`; verify latest pushed HEAD and local worktree before PR review. Preserve all maintainer edits and the accepted evidence.

## Accepted evidence and current behavior

- Increment 4 **Stages 1–2 ACCEPTED**: production configured SDL RDP frontend/worker, exact-UUID registration and placement, sequential `-o`, native X11/Wayland trials, shared cohort stacking and viewer lifecycle. [Stage 2 evidence](step1.5c5d-increment4-stage2-native-acceptance-2026-11-10-11.md).
- **Stage 3 ACCEPTED**: 300000-ms default RDP/VNC viewer-readiness deadlines; known-clean failure continuation only after positive terminal broker/worker cleanup; fail-closed uncertainty; success-only cohort order; partial plans return incomplete status. Native `gmki91` X11 and `q552u01` Wayland each demonstrated `completed [2], failed [1], skipped [0]`. [Stage 3 evidence](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md).
- **Stage 4 ACCEPTED**: CLI built-ins → optional system/user defaults → per-run plan (`-f` or existing user/system selection) → CLI overrides; fail-closed loading; optional non-root user-owned `eselect joetoo-kwin list|show|set`; short template + annotated reference and packaging-ready instructions; quiet notice/info/debug `show_config` (including `rlv.config`, pseudo-booleans and active profile asterisk). The maintainer's isolated-XDG native X11 tests verified 70%/65% profile overrides over 75% user defaults and 87% built-ins; name/number selection, unchanged selected profile with `-f`, invalid-selection rejection, and a real Dolphin + Konsole `2/2` managed launch with successful initial layout. Local initial integration reported 903 Python / 161 JS PASS and service install/check/introspection; Codex's final polish reported 911 Python / 161 JS PASS and 78 focused PASS; maintainer's final `validate_scripts joetoo-kwin -l` reported clean success. The final headless 911/161 report and post-polish native-display limits are distinguished in [Stage 4 evidence](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md).
- Existing remote authentication, TLS/NLA trust, GDM state, KWin window identity and placement remain **separate** assertions; local viewer completion does not prove the remote login/certificate/security state. VNC/RDP worker normalization and async/Option D remain deliberately deferred to version 2.

## Next actor and objective — milestone PR, then Step 1.5d

**Current actor: maintainer.** Step 1.5c.5d is fully accepted and closed; there is **no outstanding Increment 5 code task, native acceptance experiment or new stage**. Prepare one milestone PR from `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation` to `main`, after ensuring accepted closeout docs are committed/pushed and checking the actual current diff/CI. As of the 2026-11-11 connector comparison, branch was 59 commits ahead of `main`, 0 behind, 90 changed files; recompute at PR time. **No PR creation/merge is implicitly authorized by this document.** Use [milestone PR Codex draft](step1.5c5d-accepted-milestone-pr-codex-task-DRAFT.md) for an optional bounded review; maintainer controls publication and merge.

**Next implementation milestone after merge:** Step **1.5d integrated regression** under [Step 1.5 scope](Step1.5c5_implementation_scope.md) and [architecture](../ARCHITECTURE.md). Review the actual Step 1.5d requirements and remaining `-L`/`-l` integration/packaging boundaries before drafting an authorized implementation assignment; do not automatically begin Step 1.5d or re-open 1.5c.5d. Preserve documented remote-session versus local-placement distinction, original exact UUID, broker lifecycle and X11 heuristic limitations. The accepted strict negative test observed `ERRCONNECT_TLS_CONNECT_FAILED` and positive broker cleanup; it does not prove all TLS versions/ciphers.

**Packaging backlog, explicitly outside Increment 5:** future ebuild installs `/etc/joetoo-kwin/BUILD` (`BUILD="${PVR}"` at installation) and scripts source their own package version, not installed `joetoolkit` BUILD.

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
- [Increment 5 production native security evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md)
- [Increment 5 security-policy Codex task draft](step1.5c5d-increment5-rdp-security-policy-codex-task-DRAFT.md)
- [Increment 5 final strict native acceptance and milestone closure](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md)
- [Accepted-milestone PR readiness Codex task DRAFT](step1.5c5d-accepted-milestone-pr-codex-task-DRAFT.md)
- [Increment 5 Codex closure candidate (historical review)](step1.5c5d-increment5-security-native-closure-candidate.md)
