# DRAFT Codex task — Step 1.5d single-window / listing integration and integrated regression

**Status:** Draft for maintainer review, not self-executing authority. Step 1.5c.5d was formally accepted and merged by PR #29 at `3e9c4bf311bc65b32d332a00d3b50163a9043303`. Work only from an identified clean Step 1.5d branch based on accepted `main`. This draft is a proposed single bounded milestone, **not** a new design stage.

## Goal

Finish the architected **Step 1.5d** outcome: make `joetoo-kwin -L` launch **one** managed window and `joetoo-kwin -l` list managed windows, then run a proportional integrated regression across previously accepted Step 1.5 capabilities. Keep existing `-o`, `-c`, `-m`, broker/KWin ownership, remote viewers, security defaults, OpenRC process boundaries and current configuration-layering contracts intact.

## Read and reconcile actual source first

Read root/workspace/project `AGENTS.md`, `workspace/README.md`, current `task_step1.5/HANDOFF.md`, project `ARCHITECTURE.md` (especially 1.5d milestone), project README, implementation and tests. The old Step 1.5c.5 scope and 1.5c.5d evidence are **historical**; they are not fresh authorization or proof of unfinished RDP work.

Verify the current CLI: `-L` and `-l` return `not yet integrated`; `test-launch` is a **test-only** prototype, not an automatically appropriate production API. Existing read-only broker `ListManaged` returns managed records; preserve distinction between intended desktop/slot, UUID, placement/presence and transport/session outcome. The architecture milestone table still describes 1.5c.5d as in progress; reconcile this stale *status text* with the merged evidence, not by reopening 1.5c.5d.

## Bounded implementation

1. Establish from current parser/config/launcher/prototypes the smallest maintainable **user-facing `-L` operand contract** for one configured managed window, including desktop, program/mode/target and optional layer; derive its slot safely through existing broker/config rules rather than assuming a free slot or overriding a reservation. Reuse existing validated program/mode targets, geometry, confirmation policy, backend selection, strict RDP defaults and failure/cleanup rules. Avoid arbitrary commands, a second launch engine, hidden side effects or an unreviewed new grammar. Explain the chosen CLI contract concisely before/alongside the diff.
2. Define `-l` as a **read-only, non-destructive** presentation of authoritative broker managed-window state. Include stable identifiers and useful intended desktop/slot, presence/placement fields. Do not imply a reachable/authenticated remote session or count unrelated windows as managed. Handle empty/unavailable/busy/inconsistent broker conditions truthfully; reuse existing broker interfaces without inventing privileged controls.
3. Add focused validation/tests for normal, invalid, duplicate/reserved-slot, failure and absent-broker behavior, plus integration with config/profile and existing managed X11/Wayland viewer types. Implement and headlessly test as one bounded deliverable; do not create subincrements.
4. Run full applicable Python, JavaScript, Bash syntax/ShellCheck, and any existing harness/service-check tests that fit the environment. Prepare a **small native regression matrix** for maintainer-run `gmki91` X11 and `q552u01` Wayland checking `-L`, `-l` plus representative mixed Konsole/SSH placeholder, Dolphin local/SFTP, TigerVNC SSH tunnel and SDL FreeRDP security/placement outcomes. Reuse accepted native evidence; don't repeat every prior matrix or change server certificates to manufacture tests. Maintain strict certificate refusal as an accepted invariant.
5. Update user-facing help/reference and affected task evidence/status only as needed. Report actual diff, test results, explicit native checks, new limitations and whether work is committed or only local. Never claim an unrun native test passed.

## Decision/stop boundary

If **one material UX ambiguity** remains about `-L` syntax or `-l` output after inspecting existing code, present two small alternatives and a recommended default to the maintainer before implementing the disputed behavior. Otherwise complete the approved objective without creating extra authorization gates. Do not edit `joetoo` or `joetoo-upstream`, administer hosts or perform maintainer-native tests. Request separate approval before commit/push/PR/merge if not already included in explicit task authorization.

**Out of scope:** managed close `-a/-d/-x` (1.6); broker restart/checkpoint reconciliation (1.7); durable snapshots/recovery (1.8); ebuild installation, official `eselect`, `/etc/joetoo-kwin/BUILD` from `$PVR` (1.9); redesign of RDP/VNC worker lifecycles, alternate clients or asynchronous Option D.
