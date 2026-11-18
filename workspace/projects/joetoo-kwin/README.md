# joetoo-kwin

Development workspace for replacing joetoo's X11 `xdotool_*` window workflows
with KWin-compatible tools on **X11 and Wayland**. Candidate sources remain
in `joetoo-ai`, not yet the packaged version 1 application. See
[ARCHITECTURE.md](ARCHITECTURE.md) for accepted and proposed product contracts,
including managed-operation requirements.

## Current status — November 18, 2026

**Step 1.5 is complete and archived.** Managed configured RDP and its five
increments were accepted/merged in [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29);
single-window launch and inventory in [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30);
and archive/init in [PR #31](https://github.com/JosephBrendler/joetoo-ai/pull/31)
(`cdcdc9e`).

**Step 1.6 is implemented on the published task branch `c57ab8c` and is
ready for maintainer acceptance review, not yet formally accepted/merged.**
`-d MANAGED_ID` retains the registration/slot after verified graceful close;
confirmed fixed-set `-x` **progressively retires verified absences and verified
closes**, without force killing or restart of the broker. Core behavior passed
both q552u01 Wayland/XWayland (**9/9 records retired**) and slim2 native X11
(**16/16 records retired**) with immediate empty inventory, queryable retained
history and real Konsole refusal/timeout observations. The native X11 helper
uses a KWin 6.7.6-specific installed effect. See the
[active HANDOFF](task_step1.6/HANDOFF.md),
[task index](task_step1.6/README.md), and
[2026-11-18 slim2 evidence](task_step1.6/step1.6-slim2-native-x11-evidence-2026-11-18.md).

**Disposition:** No demonstrated code blocker. Strict live X11
unsupported-`WM_DELETE_WINDOW`/stale-XID race proof and some independent
client-worker/frontend-loss checks remain unverified; headless safety tests
exist. The maintainer decides whether to accept with those limitations or
run a narrow live fixture. Publication/merge and q552u01 fast-forward remain
separate maintainer workflow steps. No additional development stage is implied.

| Completed capability | Accepted outcome / evidence |
| --- | --- |
| Configured planning and launches | Shared geometry, confirmation, original local Bash/SSH placeholders, Dolphin local/SFTP and one-shot group layout; [Step 1.5 history](archive/task_step1.5/README.md) |
| TigerVNC over SSH | Positive viewer identity, owned forwarding lifecycle and verified placement on X11 and Wayland/XWayland; retained as a supported peer |
| SDL FreeRDP | Configured serial `-o`, native X11/Wayland registration and exact-UUID placement, finite readiness and verified clean-failure continuation; [final acceptance](archive/task_step1.5/step1.5c5d-increment5-final-native-acceptance-2026-11-11.md) |
| Configuration | Layered defaults/per-run settings, optional user-owned `eselect` profiles and severity-sensitive display; [configuration acceptance](archive/task_step1.5/step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md) |
| Single-window launch and inventory | `-L DESKTOP PROGRAM MODE TARGET [LAYER]` supports `over` only (also the omitted-layer default), retained-slot selection and verified one-shot raise without peer reflow; `-l` lists managed records read-only; [native acceptance](archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md) |

**Final recorded fixture/regression evidence:** 7 focused Python tests,
1,000/1,000 isolated XCB repetitions, an additional 100 leak-check repetitions,
949 full Python tests and 163 JavaScript tests passed after the fixture fix.
These are the [published post-fix results](archive/task_step1.5/step1.5d-xcb-evidence-addendum.md),
not tests rerun for this documentation transition. The earlier
`iota01` 948/949 result and eleven passing reruns remain preserved in the
native record. Production nonblocking libxcb behavior was unchanged.

Native Step 1.5d acceptance used `gmki91` X11 and `iota01` Wayland;
earlier RDP acceptance also used `q552u01` Wayland. Those historical results
are not Step 1.6 acceptance. Local registration/placement does not establish
remote TLS trust, authentication, GDM login or usability. RDP's accepted
built-in defaults remain `/sec:nla` and `/cert:deny`.

### Completed development evidence

| Gate | Delivered capability | Evidence |
| --- | --- | --- |
| 1.2a–1.3b | OpenRC user broker, resident KWin lifecycle, observation, PID/UUID correlation | [Archive](archive/README.md), [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16), [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) |
| 1.4a–1.4d | Managed registry, UUID-based reconciliation, public read-only queries and multiwindow placement | [Step 1.4 closure](archive/step1.4/HANDOFF.md), PRs #19–#22 |
| 1.5a | Configurable planner/shared geometry, colorized descriptive `-c` | [Step 1.5 history](archive/task_step1.5/HANDOFF.md), PR #23 |
| 1.5b | Interactive `-m` operands, independent preservation, native X11/Wayland acceptance | [Step 1.5 history](archive/task_step1.5/HANDOFF.md), PR #24 |
| 1.5c.1–1.5c.3 | Confirmation before launch, safe coordinated managed slots and original Bash/SSH placeholders | [Step 1.5 history](archive/task_step1.5/HANDOFF.md), PR #25 |
| 1.5c.4 | KWin desktop capacity, Dolphin local, application-independent layers, group finalization, bounded initial stack/focus, XDG discovery | [Native closure](archive/task_step1.5/step1.5c4-native-acceptance.md), [audit](archive/task_step1.5/step1.5c4-review.md) |
| 1.5d | `-l` list managed windows, `-L` launch one window | [step 1.5 history](archive/task_step1.5/)

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

## Accepted configuration and lifecycle baseline

RDP registration and VNC viewer-readiness defaults are 300000 ms, with validated
overrides and independently bounded mechanical operations. Serial continuation
requires positive broker/process cleanup evidence; Busy or uncertain ownership
still stops the plan. See the [Stage 3 native record](archive/task_step1.5/step1.5c5d-increment4-stage3-native-acceptance-2026-11-10-11.md).

The short [per-run template](joetoo-kwin-per-run-template.conf) and
[configuration reference](docs/configuration-reference.md) describe the accepted
layering and optional user-owned profile selector. Packaging remains Step 1.9.

## Window configuration at a glance

`desktop_session_list` is an indexed Bash array of pipe-delimited recipes - see ARCHITECTURE.md

For configured `-o`, the optional `LAYER` is `under`, `panel`, or `over`; omitted means `panel`.
**`slot` is not an array field**: the planner derives the one-based entry
number per desktop, including entries of every application/layer. Desktop
groups are executed in first-appearance order and retain within-desktop
configuration order; initial stack order is `under → panel → over`. This is
a one-time layout and does not override later manual KWin operations.

Configuration precedence is built-in defaults, optional
`/etc/joetoo-kwin/defaults.conf`, optional XDG user `joetoo-kwin/defaults.conf`,
selected per-run plan, then supported CLI overrides. Explicit `-f FILE` selects
the per-run plan without suppressing defaults. Otherwise the XDG user
`joetoo-kwin/joetoo-kwin.conf` precedes `/etc/joetoo-kwin/joetoo-kwin.conf`.
`XDG_CONFIG_HOME` defaults to `$HOME/.config`. See the configuration reference
for validation and optional profile selection. OpenRC service configuration
remains separate.

## Historical application-evaluation inventory

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
FreeRDP; see the [GNOME interoperability study](archive/task_step1.5/README_gnome_remote_desktop.md)
and [feasibility record](archive/task_step1.5/HANDOFF.md). Installed candidates are not
automatically managed capabilities. Each future integration needs its own
launch, identity, lifecycle and security contract; TigerVNC remains fully supported.

## Development and validation platforms

| Host | Current maintainer-designated role | Native KWin backend |
| --- | --- | --- |
| `q552u01` | Initial Step 1.6 development/acceptance host | Wayland |
| `slim2` | Subsequent native X11 testing | X11 |
| `gmki91` | Additional native X11 validation | X11 |

These roles do not authorize native execution. Step 1.5d's `iota01` Wayland
acceptance remains attributed to that host in the archived evidence.

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
- `tests/`: headless regression suites; `archive/`: historical POCs and
  completed tasks, including `archive/step1.4/` and `archive/task_step1.5/`.
- `task_step1.6/`: active managed-operations dispatch and task index.
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
- [Step 1.4 completion](archive/step1.4/HANDOFF.md)
- [Step 1.5 closure and historical dispatch](archive/task_step1.5/HANDOFF.md)
- [Step 1.5c.4 native evidence](archive/task_step1.5/step1.5c4-native-acceptance.md)
- [Step 1.5c.4 merge-readiness audit](archive/task_step1.5/step1.5c4-review.md)

Historical proposals and illustrative targets do not authorize new work.
The [Step 1.6 HANDOFF](task_step1.6/HANDOFF.md) identifies current authority
and the next actor. Archived task instructions confer no new authorization.
