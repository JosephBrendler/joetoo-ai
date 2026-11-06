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
| 1.5c.5d | Managed RDP implementation active. Private native-Wayland registration-only core and tests *reported by Codex*, not yet independently reviewed/accepted; public interface under review | [Current HANDOFF](HANDOFF.md) and active Codex diff/test report |

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
