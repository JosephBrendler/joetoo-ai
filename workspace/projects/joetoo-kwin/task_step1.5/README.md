# Step 1.5 — Task history, decisions and verification index

This is the *historical task record*, not the current execution authority.
For current branch/actor/approval, consult [HANDOFF](HANDOFF.md); for current
requirements/tests, [Step 1.5c.5 scope](Step1.5c5_implementation_scope.md);
for product design, [architecture](../ARCHITECTURE.md); and for RDP technical
findings, [remote-desktop research](README_remote_desktop_research.md).

## Accepted increment outcomes

| Increment | Accepted outcome / present limitation | Primary evidence |
| --- | --- | --- |
| 1.5a–b | Configured planning and interactive forms, preserving existing session behavior | [Project README](../README.md) and historical HANDOFF |
| 1.5c.1–c.3 | Confirmed launch planning, safe managed registration, original local Bash/SSH continuity | [Project README](../README.md) and historical HANDOFF |
| 1.5c.4 | Desktop capacity, local Dolphin, layers, grouped layout, initial stacking/focus and XDG discovery accepted on KWin X11/Wayland | [Native acceptance](step1.5c4-native-acceptance.md), [review](step1.5c4-review.md) |
| 1.5c.5a | Dolphin SFTP and non-enforcing name-resolution/TCP advisories accepted; remote use and placement independently assessed | [SFTP acceptance](step1.5c5a-native-acceptance.md), [URI/security contract](step1.5c5a-dolphin-sftp-contract.md) |
| 1.5c.5b | TigerVNC-over-authenticated-SSH accepted; positive X11/Wayland/XWayland viewer UUID placement and owned-tunnel teardown | [Project README](../README.md), historical HANDOFF |
| 1.5c.5c | Affirmative RDP feasibility accepted; SDL3 FreeRDP chosen **first by implementation order**, not as default; TigerVNC remains an independently supported peer | [PR #28](https://github.com/JosephBrendler/joetoo-ai/pull/28), [research](README_remote_desktop_research.md) |
| 1.5c.5d | **Increment 1 native-Wayland registration accepted**. Native X11 `auto` managed registration demonstrated without placement, including correct post-close UUID retention; 644 Python and 145 JavaScript regressions passed. Current candidate accepted for further development; Increment 2 closeout awaits the managed `software` native check. Controlled placement is the next code increment. | [Native X11 registration evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md), [current HANDOFF](HANDOFF.md) |

## Recent Step 1.5c.5d / Increment 2 decisions (2026-11-08)

Increment 1 native-Wayland SDL registration remains **ACCEPTED**. The native-X11 A2 patched-client path was abandoned. The renderer/identity decisions are now implemented for an explicit native-X11 profile: `auto` is the default renderer, `software` is an independently configurable alternative, and one user-adjustable 500 ms X11 UUID persistence selector operates in either mode. The Nov 8 diagnostic software/auto renderer comparisons are documented separately.

On 2026-11-08, the maintainer installed the current X11 registration candidate through the established user OpenRC workflow, ran **644 Python** and **145 JavaScript** passing tests, and demonstrated native `auto` managed-registration **without placement**. One console-captured run registered an exact KWin UUID and displayed GDM followed by a usable GNOME desktop. A second run independently showed `win-001` **present** with `placement=not_requested`, an `IDLE` placement transaction and one successful registration; after titlebar closure the *same KWin UUID* remained registered with `presence=missing`, with no adoption of a successor. See [native X11 registration evidence, including sanitized source output](step1.5c5d-increment2-native-x11-registration-2026-11-08.md).

The maintainer **accepts the current code candidate and this initial native `auto` result for forward development**, not as blanket production RDP approval. Increment 2 full closure remains pending a comparable managed-native `software` test. The next authorized Codex task is a *bounded implementation* of explicit operator-approved controlled placement of an already registered viewer, under the current [HANDOFF](HANDOFF.md) and a separate prompt. No automatic readiness inference, configured `-o -f`, upstream client patch, or native operation by Codex is authorized.

## Historical authorization chronology

Earlier SFTP, VNC and RDP-feasibility permissions were specific to their
historical stages; they confer **no current authority**. The complete original
approvals, restrictions, dated outcomes and agent observations remain in
[the committed full-length HANDOFF at the migration baseline](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md).
Its Git history retains earlier revisions. The active HANDOFF supersedes all
prior execution instructions.

- **2026-10-29–30:** Step 1.5a/b refinements and Step 1.5c planning and first
  broker/CLI integration, verified through focused and native tests.
- **2026-10-31–11-01:** Step 1.5c.4 graphical-layout enhancements, regression,
  native acceptance and review. Step 1.5c.5 SFTP planned and implemented.
- **2026-11-02–03:** TigerVNC over SSH contract, managed viewer/tunnel
  integration and native X11/Wayland validation; installer archive/backup
  housekeeping. RDP feasibility investigation approved and commenced.
- **2026-11-03–05:** GNOME Remote Login interoperability; KRDC, Remmina and
  FreeRDP comparison; SDL lifecycle evidence from X11 and native Wayland;
  subsequent negative-path and coexistence proofs.
- **2026-11-05–06:** RDP feasibility closed affirmatively and merged via PR #28;
  Step 1.5c.5d planned and a native-Wayland registration-only Increment 1
  separately authorized. See the current dispatcher for its approval boundaries.
- **2026-11-07–08:** Increment 1 native-Wayland registration-only accepted;
  X11 A2 source modification abandoned; A1/C scope adopted. Gate F feasibility
  accepted and one software-renderer native A1 comparison recorded with
  retained private archives. Default/OpenGL diagnostic comparison and
  actual managed native-X11 `auto` registration then succeeded, including
  after-close UUID retention; placement development was authorized separately.

## Historical iteration index

The former HANDOFF includes **Codex iterations 0–45** and **cloud iterations
C1–C24** on the verified published snapshot, with extensive detailed
transcripts. This is a compact navigation index, not a verbatim copy of each
row; use the [original committed HANDOFF](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md#5-agent-owned-iteration-record)
for exact row content, commands, tests, hashes and provenance. Later uncommitted
Codex iterations must be reconciled before migration is accepted.

| Iterations | Main work thread |
| --- | --- |
| 0–9, C1–C6 | 1.5a/b, forms, AAR/reporting, test review and native acceptance |
| 10–12, C7–C14 | 1.5c broker/CLI planning, public-interface, ownership and slot reviews |
| 13–19, C15–C22 | 1.5c.4 KWin layers, desktop groups, focus and acceptance |
| 20–24, C23–C24 | 1.5c.5 SFTP scope, implementation, advisory and native closure |
| 25–33 | TigerVNC-over-SSH identity, tunnel integration, installer and historical backup disposition |
| 34–36 | RDP server/client feasibility, PKI review, GNOME Remote Login native evidence |
| 37–40 | SDL diagnostic runner, X11 lifecycle, native-Wayland identity contract |
| 41–44 | Native-Wayland and X11 evidence correlation, negative/coexistence cases |
| 45 | Coordinated 1.5c.5c closeout and 1.5c.5d documentation planning |

## Detailed evidence index

- [2026-11-08 native X11 `auto` managed registration — two successful launches, 644 Python/145 JavaScript tests, full sanitized before/after registry transcript](step1.5c5d-increment2-native-x11-registration-2026-11-08.md)
- [2026-11-08 default/OpenGL renderer native feasibility and observed 22 ms marked predecessor](step1.5c5d-a1-auto-renderer-native-evidence-2026-11-08.md)
- [2026-11-08 A1 software-renderer native feasibility — complete transcript, stage timestamps, archive hashes, UUID/XID correlation](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md)
- [Active A1/C X11 draft design and stage gates](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md)
- [Remote Desktop research, comparison and SDL identity](README_remote_desktop_research.md)
- [GNOME Remote Desktop original study](README_gnome_remote_desktop.md)
- [Step 1.5c.4 native acceptance](step1.5c4-native-acceptance.md)
- [Step 1.5c.5a SFTP native acceptance](step1.5c5a-native-acceptance.md)
- [Step 1.5c.5a SFTP contract](step1.5c5a-dolphin-sftp-contract.md)
- [Step 1.5c.5 implementation scope](Step1.5c5_implementation_scope.md)
- [Historical source, all iteration rows](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md)

## Recording subsequent progress

Record only material task results, acceptance decisions, and links to precise
review evidence. A full detailed technical report belongs in an authorized
focused evidence record or the actor's response. The live HANDOFF retains only
the latest actionable status, source-availability location and next actor;
no duplicate iterative table belongs in that file. Do not present uncommitted
work as already retrievable from GitHub.
