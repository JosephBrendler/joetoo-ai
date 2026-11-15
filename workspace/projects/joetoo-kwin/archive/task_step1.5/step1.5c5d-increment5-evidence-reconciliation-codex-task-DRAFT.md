# DRAFT — Codex task: Step 1.5c.5d Increment 5 evidence reconciliation and closure recommendation

**Status: DRAFT for maintainer issuance; this document alone does not dispatch Codex.**

**Repository:** `JosephBrendler/joetoo-ai`
**Project:** `workspace/projects/joetoo-kwin/`
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`

## Goal — determine whether Increment 5 is already closable

Increment 4 Stage 4 has been **maintainer accepted**, with native X11 configuration/profile tests and full headless regression evidence. Do **not** reopen its configuration design or previous RDP/VNC implementation. Increment 5 concerns the previously identified **RDP security and native interoperability closure**, separate from local managed-window registration and placement.

**Complete an evidence-first acceptance audit, not another implementation increment.** Use the current task scope and `ARCHITECTURE.md` as acceptance criteria; identify which criteria have direct existing support, which remain unproven, and which are expressly out of scope. Distinguish proven client behavior from asserted TLS/NLA security and server authentication; never infer a trusted remote certificate or successful remote login merely from a correctly placed SDL window.

## Inputs and required investigation

1. Verify current branch HEAD/status and applicable root/workspace/project `AGENTS.md`. Preserve all maintainer changes; do not reset a checkout if fetch is blocked.
2. Read current `task_step1.5/HANDOFF.md`, task README, Step 1.5c.5 scope, Increment 4 decisions and accepted Stage 2/3/4 evidence.
3. Read *existing* GNOME Remote Desktop interoperability and PKI records, including `README_gnome_remote_desktop.md`, `step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md`, `README_remote_desktop_research.md`, native X11/Wayland RDP records and relevant archived transcripts. Avoid duplicating older failed experiments as fresh blockers after a recorded fix.
4. Inspect relevant current CLI/backend and tests only where necessary to understand security policy, credential handling, certificate validation, remote-session reporting, and behavior on user cancellation. Do not send credentials or private PKI keys to logs or evidence files.
5. Prepare an acceptance matrix: **requirement → cited prior evidence → status (proven / partial / unproven / explicitly deferred) → minimum missing verification, if any**. Use exact file/path/section references and provenance; distinguish Codex headless from maintainer native execution.

## Required deliverable and disposition

Prepare **one** concise Increment 5 evidence-and-closure recommendation in `task_step1.5/`, including the matrix, known residual limitations, and one explicit verdict:

- **ACCEPT:** established requirements already met; provide exact evidence links and closeout rationale.
- **ACCEPT WITH SPECIFIC NATIVE CHECKS:** identify only the shortest missing *maintainer-operated* verification steps and their expected observations; do not request a broad test campaign.
- **BLOCKED:** identify the precise unsafe/incorrect implementation or missing requirement that genuinely prevents acceptance and its smallest necessary correction.

Do not reinterpret remote `remote_session=unverified` as an implementation failure when the contract deliberately separates KWin registration from remote authentication. Conversely, do not treat that field or a GDM screenshot as evidence that TLS trust, identity, remote login or server policy were verified. Recommend what the existing Increment 5 acceptance actually requires.

## Limits and completion

This task authorizes read-only review and an uncommitted documentation/evidence candidate within `joetoo-ai`, not source changes. **No** RDP/VNC rewrite, generic remote scheduler, new option/stage, broker API change, config-layer changes, native GUI/network experiment, OpenRC action, protected repository edit, commit/push/merge, or packaging deployment without separately explicit maintainer authority. If evidence is incomplete, return a small executable *operator test recipe* and stop; do not invent work for Codex.

Return a concise summary, proposed evidence document/diff, and the decision the maintainer should make next. The finish line is a justified Increment 5 acceptance decision, not another intermediate design milestone.
