# Step 1.5 — Active task dispatcher

**Task / current gate:** Step 1.5c.5d, **Increment 4 Stage 3 — finite RDP/VNC viewer waits and known-clean serial continuation**.

**Maintainer decision (2026-11-10):** Increment 4 **Stages 1 and 2 are ACCEPTED**. **Stage 3 is AUTHORIZED** for the bounded implementation described below, with execution by Codex **upon the maintainer's separate issuance of the Stage 3 task**. This HANDOFF records the decision and scope; publication of this file alone does not dispatch an agent. **Stage 4 is a separate, still-unapproved configuration-design discussion between the maintainer and ChatGPT; Codex is not its planning or implementation actor.**

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Last verified published branch HEAD before this HANDOFF revision:** `8494175a3d3c31e3f3924e52a75538fd0f74d1f6` (maintainer's configuration-proposal and improved per-run-template commit). Codex must check the actual later HEAD, local branch, status and maintainer changes before editing; never reset or overwrite returned work.

## Accepted baseline and evidence

- **Stage 1 accepted:** offline `sdl-freerdp|rdp|rdp://USER@HOST[:PORT]` recipe/settings and whole-plan validation; implementation commit `12c8f0435f3dace71ecfb4dac79469ee3669de48`.
- **Stage 2 accepted:** production RDP frontend/worker and configured serial `-o` registration, exact persistent-viewer UUID placement to planner-owned frame, and common desktop cohort ordering; accepted implementation commit [`caba9f4d3ae62b48c6d5f602af36e43fb2d4d25b`](https://github.com/JosephBrendler/joetoo-ai/commit/caba9f4d3ae62b48c6d5f602af36e43fb2d4d25b). The intervening `2d2917d5843ca0e6fbcdb6803cbc3262dd70569b` added the maintainer's Wayland example, not a production-code change.
- **Maintainer-native evidence:** on `gmki91` (KWin X11), RDP plus Konsole (`2/2`), RDP plus three Konsoles (`4/4`), and two independent RDP viewers succeeded; on `q552u01` (KWin Wayland), mixed Konsole/RDP (`2/2`), three Konsoles plus last-launched RDP (`4/4`, `under` correctly stacked beneath panels), and two RDP viewers (`2/2`) succeeded. Broker-reported `order` matched `observed_order`; occupied managed slots were refused. Closing a registered Wayland viewer naturally ended its worker/child while preserving the same exact UUID and original slot as `presence=missing`. Evidence is scoped to local identity, placement and stacking; remote login, NLA/TLS/server identity and active-desktop focus are not asserted.
- **Regression evidence supplied by Codex:** 850 Python and 161 JavaScript tests PASS, zero JS skips, with syntax/ShellCheck/diff checks PASS. Not a fresh CI run by this HANDOFF author.
- **Durable record:** [Increment 4 Stage 2 native acceptance](step1.5c5d-increment4-stage2-native-acceptance-2026-11-10-11.md). See also [task outcome index](README.md), [project architecture](../ARCHITECTURE.md), [Increment 4 maintainer decisions](step1.5c5d_Increment_4_decisions.md) and [Step 1.5c.5 implementation scope](Step1.5c5_implementation_scope.md).

## Authorized Stage 3 objective and limits

**Deliver exactly the accepted Stage 3 behavior, preserving the accepted Stage 2 implementation:**

1. Set user-overridable **300000 ms** defaults for `rdp_registration_timeout_ms` and `vnc_viewer_ready_timeout_ms` consistently across the existing CLI planning defaults, client validators and distributed current configuration template. Preserve the existing bounded validation and independent D-Bus, placement, cleanup and identity deadlines. A readiness timeout identifies failure to establish the persistent local viewer, **not** proof of the operator's authentication state. Remote GDM interaction inside the viewer never gates local `-o` completion.
2. In serial `-o`, permit continuation to the next eligible entry **only after a positively verified, terminal, known-clean pre-registration failure/timeout**: pending broker work canceled or terminal, original owned client/tunnel terminated and reaped where required, no unknown owner/source/transaction/slot state, and re-preflight of the remaining plan. Record the failed entry and report an incomplete overall layout rather than falsely claiming full success.
3. Maintain **fail-closed** behavior on Busy, ambiguous registration, broker owner/source change, lost/untrusted cleanup evidence, active placement, unverified managed-window ownership or any uncertain result. A registered viewer survives noncritical supervision/reporting/placement failure; do not reclassify it as an unregistered pending child, kill it to enable continuation, claim remote authentication, or rewrite successful placement history.
4. Provide targeted headless regression tests for RDP and VNC success, known-clean continuation, unknown-cleanup stop, all applicable timeout/default/override paths, repeated preflight, historical reservation and exact-UUID/viewer-survival invariants; run/report full Python, JavaScript and appropriate Bash/ShellCheck validation.

**Explicit exclusions:** No unapproved missing-slot release (a separately reviewed conditional proposal), no broker public D-Bus contract change, no new generic remote-client scheduler, no Option D concurrency, no credential/certificate-policy change, no geometry/stacking redesign, no daemon restart/re-adoption behavior change, and **no CLI/OpenRC configuration-file separation, precedence, path migration or template redesign**. Only narrowly update existing template *values and now-inaccurate Stage 2/3 comments* needed for Stage 3. If positive cleanup proof requires an unapproved API/schema change or a broader redesign, **stop and present the smallest specific alternative for maintainer approval**; do not invent a cleanup-success flag.

## Next actor, permitted work and review gate

**Next actor:** Maintainer publishes this HANDOFF and separately **issues the Stage 3 Codex task**. Once issued, Codex may prepare **uncommitted candidate changes and headless tests** in the approved `joetoo-ai` project scope only, following root/workspace/project `AGENTS.md`, `workspace/README.md`, the architecture and maintainer decisions. Return an exact complete working-tree diff including untracked tests, test commands/results, evidence for each continuation classification, and unresolved limitations.

**Stop conditions:** Unsafe/unknown ownership or cleanup, changed or missing required interface, unapproved scope expansion, or inability to demonstrate safe continuation. No native GUI/network experiments, host service actions, installation, edits to `joetoo`/`joetoo-upstream`, commits, signed commits, pushes, PRs or merges without separate explicit authorization. Preserve the maintainer's example configs and documentation.

**Next review gate:** Maintainer reviews the Stage 3 diff and headless results, then decides whether to authorize native X11/Wayland testing and publication. Stage 4 design remains **maintainer–ChatGPT only**, with its current [separate proposal](step1.5c5d-increment4-configuration-layering-proposal-DRAFT.md); Stage 4 neither blocks nor expands Stage 3.
