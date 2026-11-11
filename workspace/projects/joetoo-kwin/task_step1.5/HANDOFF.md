# Step 1.5 — Active task dispatcher

**Task / current gate (2026-11-11):** Step 1.5c.5d — Increment 4 **COMPLETE AND MAINTAINER ACCEPTED**. Increment 5 **native production trusted-endpoint observations completed on X11 and Wayland; strict security-policy implementation and final negative native check PENDING**. Step 1.5d integration and official Gentoo packaging are separate.

**Maintainer decisions:** Earlier Increment 4 Stages 1–4 remain accepted and closed. Increment 5 adopts two user-configurable policy enums with built-in `rdp_security_protocol=nla` (`/sec:nla`) and `rdp_certificate_policy=strict` (`/cert:deny`); alternate `negotiate` and `prompt` each omit their respective flag. Do not require `/tls:enforce:1.3`. These are agreed specifications, **not yet implemented or acceptance-tested**. See [native evidence and four-row mapping](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md) and the [focused Codex draft](step1.5c5d-increment5-rdp-security-policy-codex-task-DRAFT.md).

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

**Next actor:** Maintainer reviews and explicitly issues the [bounded Increment 5 security-policy Codex task](step1.5c5d-increment5-rdp-security-policy-codex-task-DRAFT.md). The [earlier evidence-reconciliation draft](step1.5c5d-increment5-evidence-reconciliation-codex-task-DRAFT.md) has been superseded by the [Codex closure candidate](step1.5c5d-increment5-security-native-closure-candidate.md) and [new maintainer native evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md). **No further Increment 4 development is pending.**

**Next objective:** Implement exactly `rdp_security_protocol=nla|negotiate` (default `nla` -> `/sec:nla`; alternate omission of `/sec:`) and `rdp_certificate_policy=strict|prompt` (default `strict` -> `/cert:deny`; alternate omission of `/cert:`) through accepted configuration layering, effective `$info` display, inline template mapping and reference/manual table; add focused and full tests. Preserve exact UUID, lifecycle, SDL backend decisions, Stage 4 behavior, fail-closed assumptions and serial `-o`. After patch review, maintainer performs one strict trusted-FQDN production check and one safe strict certificate mismatch refusal. Window registration may precede certificate rejection; test remote refusal without assuming no local registered window. Close Increment 5/Step 1.5c.5d only on maintainer acceptance. No TLS 1.3 force, policy bitmask UI, per-target grammar or new implementation stage.

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
- [Increment 5 Codex closure candidate (historical review)](step1.5c5d-increment5-security-native-closure-candidate.md)
