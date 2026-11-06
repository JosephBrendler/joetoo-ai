# joetoo-kwin

Development workspace for replacing joetoo's X11 `xdotool_*` window workflows
with KWin-compatible tools on **X11 and Wayland**. Candidate sources remain
in `joetoo-ai`, not yet the packaged version 1 application. See
[ARCHITECTURE.md](ARCHITECTURE.md) for accepted and proposed product contracts,
including the next remote-access tranche.

## Current status — November 5, 2026

**Step 1.5c.4 is accepted and merged.** The tested implementation baseline was
`a3c50fc`, with maintainers' X11 and Wayland acceptance and subsequent
closure documentation recorded in the [Step 1.5 handoff](task_step1.5/HANDOFF.md),
[native acceptance record](task_step1.5/step1.5c4-native-acceptance.md), and
[merge-readiness audit](task_step1.5/step1.5c4-review.md).
The merged branch may have a different merge-commit SHA. Do not confuse the
tested implementation revision with a later documentation or merge commit.

**Step 1.5c.5a Dolphin SFTP is accepted and closed.** The task-branch
implementation includes safe SFTP URI handling and optional, non-enforcing
post-confirmation NSS/TCP reachability advisories. The maintainer demonstrated
managed X11 (`gmki91`) and Wayland (`q552u01`) launches, window registration,
placement and remote browsing. Positive and negative advisory observations are
recorded in the [Step 1.5 handoff](task_step1.5/HANDOFF.md) and
[SFTP acceptance record](task_step1.5/step1.5c5a-native-acceptance.md).
The advisory does not itself establish SSH authentication or SFTP usability.

**Step 1.5c.5b TigerVNC-over-SSH is accepted and merged.** On `gmki91`
(X11), the maintainer verified an authenticated
remote viewer, precise managed UUID identity and placement, a separate managed
Dolphin window, stacking, loopback-only SSH forwarding, and viewer/tunnel
teardown. On `q552u01` (Wayland/XWayland), a fresh one-window launch placed
`yorsqui:2` at desktop 10, slot 1, with verified geometry, registry presence,
1/1 layout completion, visually usable remote desktop, and both viewer and SSH
processes absent after closing the viewer. The runner reports remote
session/authentication as unverified; visual use is separate maintainer evidence.

The nine-file user OpenRC installer (including the three VNC helper modules)
reports all nine components current on both hosts. Its new content-addressed
backup behavior was checked for unchanged-update stability on `gmki91`.
Historical timestamped backups were manually relocated out of production
paths: 171 on `gmki91`, 135 on `q552u01`, retained under the user state
`legacy-backups/` directory. The unneeded standalone migration utility and
its tests are retained only in `archive/aborted_backup_migration_tool/`;
no real migration run was performed.

**Step 1.5c.5c — Affirmative RDP feasibility accepted by the
maintainer.** [PR #28](https://github.com/JosephBrendler/joetoo-ai/pull/28)
merged at `be8eb276`. GNOME Remote Login interoperability and client comparison
led to SDL3 FreeRDP as the first RDP implementation target. Native-Wayland
evidence distinguishes the launch-owned marked viewer from credentials and
covers cancellation, failed NLA, connection failure and an unrelated viewer.
X11 has a distinct temporary/persistent marked-window lifecycle requiring its
own role discriminator. The existing KWin observations support the Wayland
identity contract without an additional user-interaction observer. Detailed
provenance and qualifications remain in the [handoff](task_step1.5/HANDOFF.md).

**Next: Step 1.5c.5d — Managed RDP Implementation.** This is to be incrementally gated, requiring explicit maintainer authorization for each increment. The proposed first executable increment is native-Wayland SDL registrationwithout placement, after recipe, security and interface contract approval. Production RDP registration/placement is not accepted. In-process reconnect remains untested; a fresh client connection does not prove server-session continuity, and viewer identity does not prove GDM login or desktop readiness. TLS certificate trust and server identity remain separate implementation gates.

| Increment | Work | Status |
| --- | --- | --- |
| 1.5c.5a | Dolphin SFTP, safe URI handling and independent placement/remote outcomes | Accepted and closed; X11/Wayland native evidence |
| 1.5c.5b | Positively identified TigerVNC viewer over owned authenticated SSH tunnel | Accepted and merged; supported peer capability |
| 1.5c.5c | RDP interoperability, client comparison and viewer identity feasibility | Closed; affirmative maintainer decision; PR #28 |
| 1.5c.5d | Add managed SDL RDP, preserving independent client contracts | Documentation preparation only; each source increment needs approval |
| 1.5d | Broader integrated regression and `-L`/`-l` | Subsequent separate gate |

**Implementation scope:** See [Step 1.5c.5 implementation scope and outline](task_step1.5/Step1.5c5_implementation_scope.md) for detailed objectives, program/mode contracts, investigation requirements, security constraints, acceptance criteria, and increment boundaries. The scope document guides planning and review; implementation authorization and execution controls are established separately in `task_step1.5/HANDOFF.md`.

Additional installed RDP clients may now be evaluated deliberately, but are not
automatically scheduled for implementation. The original 1.5c.4 scope outline
is historical; later layer/group/focus approvals and accepted source supersede
its obsolete ordering/protrusion assumptions.

### Completed development evidence

| Gate | Delivered capability | Evidence |
| --- | --- | --- |
| 1.2a–1.3b | OpenRC user broker, resident KWin lifecycle, observation, PID/UUID correlation | [Archive](archive/README.md), [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16), [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) |
| 1.4a–1.4d | Managed registry, UUID-based reconciliation, public read-only queries and multiwindow placement | [Step 1.4 closure](task_step1.4/HANDOFF.md), PRs #19–#22 |
| 1.5a | Configurable planner/shared geometry, colorized descriptive `-c` | [Step 1.5 history](task_step1.5/HANDOFF.md), PR #23 |
| 1.5b | Interactive `-m` operands, independent preservation, native X11/Wayland acceptance | [Step 1.5 history](task_step1.5/HANDOFF.md), PR #24 |
| 1.5c.1–1.5c.3 | Confirmation before launch, safe coordinated managed slots and original Bash/SSH placeholders | [Step 1.5 history](task_step1.5/HANDOFF.md), PR #25 |
| 1.5c.4 | KWin desktop capacity, Dolphin local, application-independent layers, group finalization, bounded initial stack/focus, XDG discovery | [Native closure](task_step1.5/step1.5c4-native-acceptance.md), [audit](task_step1.5/step1.5c4-review.md) |

The maintainer ran **287 Python tests and 50 JavaScript tests** on
`q552u01` at tested baseline `a3c50fc`; syntax and lint checks also passed.
Native graphical-layer tests passed on `gmki91` (KWin X11) and `q552u01`
(KWin Wayland), including mixed panel/under/over stacks, four panels plus an
underlay, independent desktop-group finalization, inactive-desktop focus
suppression, and displayed-desktop focus verification (X11 bounded delayed
observation, Wayland immediate observation). On Wayland, 21 initial windows
were positively registered/placed; a further SSH Konsole on desktop 9 was
registered as `win-022`. Manual move/resize/raise persisted across desktop
switches, duplicate slots rejected, and SSH logout returned to the **original
local Bash** in the same managed Konsole. These were maintainer-executed
native tests, not AI-run host operations. They are not universal timing or
multi-monitor guarantees.

## Window configuration at a glance

`desktop_session_list` is an indexed Bash array of pipe-delimited recipes - see ARCHITECTURE.md

The optional `LAYER` is `under`, `panel`, or `over`; omitted means `panel`.
**`slot` is not an array field**: the planner derives the one-based entry
number per desktop, including entries of every application/layer. Desktop
groups are executed in first-appearance order and retain within-desktop
configuration order; initial stack order is `under → panel → over`. This is
a one-time layout and does not override later manual KWin operations.

The explicit `-f` configuration path takes priority; otherwise the XDG user
file at `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf`
precedes `/etc/joetoo-kwin/joetoo-kwin.conf`. Users do not need to set
`XDG_CONFIG_HOME`; packaging templates and install guidance are future 1.9 work.

## Candidate applications available for the next evaluation

The maintainer reported the following **installed on `gmki91`** (November 1,
2026); the corresponding `q552u01` installation and real launch behavior
must be verified independently. These are evaluation inputs, not verified
managed-launch implementations.

| Candidate | Reported installed version | Evaluation role |
| --- | --- | --- |
| QTerminal | 2.4.0 | Alternative terminal launch, shell and process/window identity |
| Krusader | 2.9.0 | Local/remote dual-pane graphical file management |
| FileZilla | 3.70.6 | SFTP/FTP GUI behavior and identity/delegation |
| Nautilus | 49.6-r1 | GNOME file navigation and remote URI support |
| Nemo | 6.6.4 | Cinnamon file navigation, Wayland behavior |
| KRDC | 26.04.3 (`rdp`, `ssh`, `vnc`, `wayland` USE enabled) | RDP/VNC client evaluated during feasibility; possible separately authorized managed integration |
| Midnight Commander (`mc`) | 4.8.33 (`-sftp`) | **Text-mode** file manager; assess utility through a managed terminal, not as a separate KWin GUI |

The subsequent RDP comparison included KRDC, Remmina, `xfreerdp` and SDL
FreeRDP; see the [GNOME interoperability study](task_step1.5/README_gnome_remote_desktop.md)
and [feasibility record](task_step1.5/HANDOFF.md). Installed candidates are not
automatically managed capabilities. Each future integration needs its own
launch, identity, lifecycle and security contract; TigerVNC remains fully supported.

## Development and validation platforms

| Host | Relevant system | Native KWin backend |
| --- | --- | --- |
| `gmki91` | GMKtec NucBox M3 PLUS, Intel i9-12900HK, Gentoo x86_64 | X11 |
| `q552u01` | ASUS Q552UB, Intel i7-6500U, Gentoo x86_64 | Wayland |

The completed graphical-layer acceptance used 1920×1080 configured displays;
this does **not** constitute autodetection or a universal display requirement.

## Development files and checks

- `joetoo-kwin`: Bash CLI and launch planner orchestration.
- `libexec/joetoo-kwin-plan-functions`, `libexec/joetoo-kwin-launch-functions`:
  shared plan, geometry and application dispatch.
- `libexec/joetoo-kwind`, `libexec/joetoo_kwin_registry.py`:
  user-session broker and managed registry.
- `joetoo-kwin-resident.js`: KWin observation/placement/initial-layout resident.
- `joetoo-kwin-template.conf`: documented defaults.
- `user-init.d/`, `user-conf.d/`, `conf.d/` and `poc-user-conf.d/`:
  user OpenRC and development configuration assets.
- `tests/`: headless regression suites; `archive/`: historical POCs;
  `task_step1.4/`, `task_step1.5/`: acceptance and handoffs.
- `tools/joetoo-kwind-install-poc`: user-owned installation/checking helper.

From the project directory, suitable headless checks include:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.js
bash -n joetoo-kwin
./tools/joetoo-kwind-install-poc --check
# End of commands
```

The OpenRC service can be inspected in a real local Plasma user session using
`rc-service -U joetoo-kwind status`. Installation, restart, application
launches, remote network tests, and publication remain **maintainer-operated**
or separately authorized, consistent with applicable repository policy.

## References

- [Architecture and version 1 requirements](ARCHITECTURE.md)
- [Project AI collaboration instructions](AGENTS.md)
- [Historical POCs and probes](archive/README.md)
- [Step 1.4 completion](task_step1.4/HANDOFF.md)
- [Step 1.5c.4 closure and historical authorization](task_step1.5/HANDOFF.md)
- [Step 1.5c.4 native evidence](task_step1.5/step1.5c4-native-acceptance.md)
- [Step 1.5c.4 merge-readiness audit](task_step1.5/step1.5c4-review.md)

Historical proposals and illustrative targets do not authorize new work.
The active Step 1.5c.5 HANDOFF records the accepted SFTP and native-tested VNC
outcomes; RDP evaluation and Step 1.5d remain separately gated.
