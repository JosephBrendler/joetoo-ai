# joetoo-kwin

Development workspace for replacing joetoo's X11 `xdotool_*` window workflows
with KWin-compatible tools on **X11 and Wayland**. Candidate sources remain
in `joetoo-ai`, not yet the packaged version 1 application. See
[ARCHITECTURE.md](ARCHITECTURE.md) for accepted and proposed product contracts,
including the next remote-access tranche.

## Current status — November 1, 2026

**Step 1.5c.4 is accepted and merged.** The tested implementation baseline was
`a3c50fc`, with maintainers' X11 and Wayland acceptance and subsequent
closure documentation recorded in the [Step 1.5 handoff](task_step1.5/HANDOFF.md),
[native acceptance record](task_step1.5/step1.5c4-native-acceptance.md), and
[merge-readiness audit](task_step1.5/step1.5c4-review.md).
The merged branch may have a different merge-commit SHA. Do not confuse the
tested implementation revision with a later documentation or merge commit.

**Next proposed tranche: 1.5c.5 (remote resources and remote desktop).**
This architecture/README update is planning, **not** an authorization to
implement, perform remote operations, or change protected repositories.
The sequence proposed for a new, separately authorized task handoff is:

| Increment | Proposed work | Status |
| --- | --- | --- |
| 1.5c.5a | Dolphin SFTP, safe target grammar and independent placement/connection semantics | Proposed |
| 1.5c.5b | Translate the maintainer's existing KDE-launcher-integrated TigerVNC-over-SSH workflow into positively managed launch after POC/security review | Proposed |
| 1.5c.5c | Compare RDP graphical candidates and decide whether secure, reliable RDP should replace legacy VNC as preferred graphical remote access | Feasibility first; implementation separately gated |
| 1.5d | Integrated X11/Wayland regression of accepted 1.5 features, including selected new transports | Future separate gate |

Additional installed clients may now be evaluated deliberately, but are not
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

`desktop_session_list` is an indexed Bash array of pipe-delimited recipes:

`DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`

Example:

```bash
desktop_session_list=(
    "2|konsole|ssh|nuthuvia"
    "2|dolphin|local||under"
    "4|dolphin|local|Documents|panel"
)
# End of configuration
```

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
| KRDC | 26.04.3 (`rdp`, `ssh`, `vnc`, `wayland` USE enabled) | RDP/VNC graphical client, potential principal RDP candidate |
| Midnight Commander (`mc`) | 4.8.33 (`-sftp`) | **Text-mode** file manager; assess utility through a managed terminal, not as a separate KWin GUI |

Also investigate appropriate Remmina and FreeRDP graphical executables
when available. Do **not** infer they are installed merely from candidate
status. A secure, reliably integrated RDP client would likely be preferred
over the maintainer's functioning but legacy TigerVNC-over-SSH workflow;
that preference is conditional on actual comparative evidence.

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

Do not treat historical proposals, illustrative targets or documentation as
authorization for executable program/mode support. A new Step 1.5c.5 HANDOFF
must separately establish baseline, permissions, testing and publication gates.
