# joetoo-kwin

Development workspace for replacing joetoo's X11 `xdotool_*` window workflows
with KWin-compatible tools on **X11 and Wayland**. Candidate sources remain
in `joetoo-ai`, not yet the packaged version 1 application. See
[ARCHITECTURE.md](ARCHITECTURE.md) for accepted and proposed product contracts,
including managed-operation requirements.

## Current status — November 18, 2026

**Step 1.5 is accepted and archived** (RDP [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29),
`-L` and `-l` [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30),
archive transition [PR #31](https://github.com/JosephBrendler/joetoo-ai/pull/31)).

**Step 1.6 was ACCEPTED by the maintainer on 2026-11-18** on branch
`task/joetoo-kwin-step1.6-managed-close`, inspected at `65e4e6be`.
`-d MANAGED_ID` gracefully closes only the authenticated managed window and
**retains** its registration/slot; confirmed `-x` **progressively retires**
authenticated missing windows and verified graceful closes, without force
killing or restarting the broker. Native evidence: q552u01 Wayland/XWayland
9/9 retired, slim2 X11 16/16 retired and empty `-l`, real refusal/timeouts
without forced close, declined operations unchanged, 1,016 Python and 163
JavaScript tests passing on each tested host. The maintainer accepted with
explicitly documented, nonblocking live-edge coverage limits.

**Next:** review and publish the Step 1.6 PR against `main`; acceptance does
not mean the PR has been merged or an ebuild published. Future version 1 scope
is the proposed unified **Step 1.7–1.8 recovery and last-good snapshot**
workstream (two distinct artifacts); Step 1.9 packaging follows. See
[accepted HANDOFF](task_step1.6/HANDOFF.md), [Step 1.6 evidence](task_step1.6/README.md),
[architecture](ARCHITECTURE.md) and the consolidated
[Version 2 Considerations](ARCHITECTURE.md#12-version-2-considerations).

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

Step 1.1–1.4 and 1.5's accepted capabilities, detailed test counts,
intermediate corrections and native limitations are documented in the
[Step 1.4 closure](archive/step1.4/HANDOFF.md),
[Step 1.5 archive](archive/task_step1.5/README.md),
[Step 1.5d native acceptance](archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md),
and [Step 1.6 evidence](task_step1.6/README.md).
Those historical materials remain primary evidence, not active instructions.

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

## Future application evaluation

Additional clients such as KRDC, Remmina, QTerminal, alternative file managers
and terminal-hosted `mc` are **not currently supported managed launch recipes**
merely because they were installed or considered. The reported historical
candidate inventory and unresolved choices are consolidated in
[Version 2 Considerations](ARCHITECTURE.md#12-version-2-considerations).
Prior comparisons remain in the [Step 1.5 archive](archive/task_step1.5/README.md).

## Development and validation platforms

| Host | Current maintainer-designated role | Native KWin backend |
| --- | --- | --- |
| `q552u01` | Step 1.6 native acceptance completed | Wayland/XWayland |
| `slim2` | Step 1.6 native acceptance completed | X11 |
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
