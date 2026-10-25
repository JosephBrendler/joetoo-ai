# joetoo-kwin — Step 1 candidate (review, not integrated)

Baseline: JosephBrendler/joetoo-ai `main` commit `09611c4`. Proposed task
branch: `task/joetoo-kwin-step1-cli-plan`. Keep all six historical POC directories intact under `../archive/` (unchanged contents).

## Scope

The new `joetoo-kwin` combines two **previously separate** interfaces:

- `-m DESKTOP X Y WIDTH HEIGHT` — run the proven active-window D-Bus move.
- `move DESKTOP X Y WIDTH HEIGHT` — maintain compatibility with the tested POC.
- `-c` — source trusted selected configuration, validate, and show a dry-run plan.
- `-f CONFIG -c` — test an alternate configuration without changing the eselect symlink.
- `-o` — reserved and explicitly fails. It does not start a program or an SSH connection.

Production configuration path: `/etc/joetoo-kwin/joetoo-kwin.conf` (a symlink
selected by eselect in a later milestone). This directory's
`desktop_sessions.conf` is only a sample and can be exercised with `-f`.

The planning functions are **sourced into** `joetoo-kwin` and populate one
set of `planned_*` arrays. The eventual `-o` action must reuse that plan.

## Preliminary layout assumptions — Step 2 is still required

`terminal_width_percent=87` is the default total horizontal allocation for
Konsole terminals, relative to configured `screen_width`.
`terminal_gap_percent=2` leaves clickable space *between* adjacent terminals;
there is also a margin on the right. One to three Konsole windows divide the
horizontal region equally. Four Konsole windows use two rows by two columns.
More than four Konsole windows per desktop is rejected. The count is of
configured windows, regardless of whether a remote host is reachable.

Graphical applications **do not reduce the allocated number/width of Konsole
slots**. They currently receive **provisional underlay geometry** intended to
stick out from beneath the terminals; no stacking or focus policy is yet
implemented. The `underlay-proposed` label is not a claim KWin will stack it.
Geometry calculations use explicit screen dimensions; multi-monitor support
and usable-work-area discovery remain separate validation work.

## Release gates

Version 1 **must include OpenRC user-session lifecycle management** for the
Python D-Bus broker and load/unload supervision of the resident KWin script.
This is not deferred from version 1; only the order of intermediate 0.x
milestones is flexible. `-o` must support terminal, SSH (`--rcfile`), VNC, and
local programs, including connection failures without empty slots. Future
close-window support must account for the exact managed processes, not broad
process-name searches. No Konsole sensitive D-Bus API and no persistent tmux.

No changes in this candidate to the existing broker, resident JS, SSH POC,
OpenRC runtime, eselect module, or official source/package repositories.

## Validation

Run `bash -n` on the candidate Bash files, and `tests/test_step1.sh` for
headless parser/plan/move-protocol checks. The test copies the CLI to a
private temporary directory and substitutes mock header and qdbus6 commands;
there are **no real KWin or SSH operations**. Native move behavior and
configuration integration require tests by the human maintainer on both X11
and Wayland.
