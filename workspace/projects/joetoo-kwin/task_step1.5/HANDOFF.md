# Step 1.5 — Active task dispatcher

**Task / current gate:** Step 1.5c.5d, Increment 4 — **Stage 3 ACCEPTED; Stage 4A documentation/template preparation AUTHORIZED for separate task issuance**. Stage 4B configuration-loader layering and optional user `eselect` remain gated, not dispatched.

**Maintainer decision (2026-11-10–11):** Stage 3 is accepted on operator-supplied headless and native X11/Wayland evidence. The maintainer authorized moving to Stage 4; the next narrow agent candidate is Stage 4A as outlined below. This HANDOFF records the decision, **not an automatic Codex invocation or publication permission**.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Baseline:** Stage 3 implementation was committed/pushed by the maintainer to make it available on `q552u01`; **current HEAD must be re-read**, not inferred from the prior Stage 2/3 HANDOFF or a stale hash. Retain any uncommitted Stage 4 drafts.

## Accepted baseline and supporting evidence

- Increment 4 **Stages 1 and 2 accepted**. Stage 2 serial RDP production behavior and native X11/Wayland results: [Stage 2 acceptance](step1.5c5d-increment4-stage2-native-acceptance-2026-11-10-11.md).
- **Stage 3 ACCEPTED:** 300000-ms RDP/VNC viewer-readiness defaults with valid override; known-clean pre-registration failure permits serial continuation only after verified terminal cleanup; uncertain failure stops; partial cohorts use only successful registration IDs; incomplete overall status remains nonzero.
- **Headless and native record:** Codex reported 447 focused Python, 869 full Python and 161 JavaScript PASS; maintainer's `gmki91` restart/test operation independently showed 869 Python and 161 JavaScript PASS plus update/check and D-Bus introspection. `gmki91` native X11 and `q552u01` native Wayland each showed Konsole success → RDP known-clean failure → Konsole success, verified broker/worker cleanup and final `completed [2], failed [1], skipped [0]`. See [Stage 3 acceptance and selected operator transcripts](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md).
- Earlier unresolved RDP failure properly stopped and did not prove continuation. Remote login/TLS/NLA and universal failure-path coverage are not claimed. No VNC/RDP architectural unification is required for version 1; possible normalization belongs to a later version-2 scope.

## Current next step: Stage 4A (bounded task)

**Next actor:** Maintainer reviews/edits and separately issues [draft Stage 4A Codex assignment](step1.5c5d-increment4-stage4A-codex-task-DRAFT.md). Codex has **not** been dispatched by this HANDOFF update.

**Authorized candidate scope upon issuance:** Produce a small per-run template and separately installed annotated reference for existing exposed CLI settings; prepare compatible packaging/documentation guidance within `joetoo-ai`, maintaining current `-f` and XDG/system lookup behavior. Reference the [Stage 4 layering design proposal](step1.5c5d-increment4-configuration-layering-proposal-DRAFT.md) and [improved per-run draft](../joetoo-kwin-per-run-template-IMPROVED-DRAFT.conf). Built-in defaults remain authoritative until a later loader change. Avoid HOME mutations by ebuild. User-configurable values may ultimately be overridden by any per-run plan selected through the default path or `-f FILE`, within validated bounds.

**Stage 4B separately gated:** Do not implement multi-file loader precedence, new default-source files, system path migration or symlink/`eselect` profile switching without review and explicit new authorization. CLI launch-plan configuration and OpenRC daemon conf.d remain distinct.

**Stop conditions and permissions:** Preserve accepted behavior, exact UUID ownership, fail-closed cleanup, current API/registry, and existing VNC/RDP implementations. No official `joetoo` or `joetoo-upstream` edits; no native tests, service actions, commits, pushes, PRs, merges or package deployment absent separate maintainer permission. Report any baseline conflict, public-information/privacy concern or proposed scope expansion before editing. Codex returns a small complete diff and headless checks for maintainer review.

## References

- [Task history and evidence index](README.md)
- [Project architecture](../ARCHITECTURE.md)
- [Stage 3 native acceptance](step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md)
- [Stage 4 configuration proposal (design, loader not yet implemented)](step1.5c5d-increment4-configuration-layering-proposal-DRAFT.md)
- [Stage 4A draft Codex task](step1.5c5d-increment4-stage4A-codex-task-DRAFT.md)
- [Maintainer Increment 4 decisions](step1.5c5d_Increment_4_decisions.md)
- [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md)
