# Step 1.5b candidate — interactive movement

Branch: `task/joetoo-kwin-step1.5b-interactive-move`.
Starting HEAD and locally recorded origin/main: `9ea76c6491e1fe2815bea514c6891dc7d5460433`.
The tree was clean before editing. This baseline contains the explicit Section 4
broker/resident write authorization. Governing instructions were unchanged from
the preceding proposal review. No fetch was attempted.

All six approved operand forms are implemented, preserving WIDTH HEIGHT order
and signed decimal coordinates. Desktop-only movement preserves both frame
position and size. Layout moves use the existing `terminal_geometry 2 1/2`
calculation and geometry-only validation; no session list is required. Select
layout config with `-f CONFIG` before `-m`. Numeric moves do not source layout
configuration and reject an explicit `-f` rather than silently ignoring it.
The five-integer path retains legacy `Submit(iiiii)` and launch methods are
unchanged. Explicit desktop existence is checked against the live KWin desktop
array at application time, including acceptance of its last element; the CLI
and broker also retain the existing 1..256 protocol bound.

## Additive protocol

- `SubmitMove(iiiiibbb) -> s`: desktop, x, y, width, height, preserveDesktop,
  preservePosition, preserveSize. Preserved groups require zero placeholders;
  explicit values retain normal bounds. The booleans are independent.
- Resident inventories advertise `move_protocol: 1`. Missing support or missing
  synchronization rejects optional requests; the client does not fall back to
  guessed geometry. A preexisting broker rejects the unknown method.
- `TakeMove(ss) -> s`: resident source and captured window UUID. This claims only
  optional-move requests and binds them to the synchronized source/exact UUID.
  Legacy `Take` cannot claim these requests. A separate registered shortcut,
  `joetoo_bridge_move_optional`, captures focus before asynchronous retrieval.
- The resident resolves omissions from that same window immediately before
  assignment. Preserved desktop membership is not assigned at all, retaining
  sticky/multiple-desktop state. Desktop-only moves do not assign frame geometry.
- `Complete(sss)` retains its signature. Optional moves require `VERIFY` with
  captured/resolved geometry and membership, source and UUID. The broker checks
  bounds, explicit intent and preservation rules before installing verification
  expectations. Normal `OK` cannot bypass optional-move UUID verification.
  Asynchronous observations must match that exact UUID, rectangle and membership.
- Requests retain bounded lifetime. Stale claims/callbacks, observer replacement,
  missing windows, malformed resolutions and nonconvergence fail safely. These
  moves neither register windows nor grant destructive ownership.

The resident rejects optional geometry changes on tiled/fullscreen/maximized
windows, or when maximize-mode support is unknown. The inspected installed
`/usr/include/kwin/window.h` exposes `maximizeMode`, and
`/usr/include/kwin/effect/globals.h` defines MaximizeRestore as zero. No code
unmaximizes, untiles, exits fullscreen or switches the displayed desktop.
The existing five-integer placement path remains unchanged.

## Validation and limits

- `python3 -m unittest discover -s tests -v`: **183 passed**, no skips. Includes
  six-form CLI tests with portable and actual installed headers; all independent
  flag combinations; sticky/multiple membership; fractional preserved frame;
  negative coordinates; placeholders/bounds; stale/source/UUID rejection; delayed
  verification; busy and duplicate claims; old-resident/old-broker rejection;
  legacy Submit and launch regressions. [Python log](step1.5b-python-tests.log).
- `node --test tests/*.js`: **3 test files passed**. New resident coverage checks
  application-time resolution, focus changes, last/nonexistent desktops, mode
  rejection, expired/deleted targets and unclaimed requests.
  [Node log](step1.5b-node-tests.log).
- Bash syntax passed for CLI, planner and portable header fixture.
  [Syntax log](step1.5b-syntax.log).
- `shellcheck -x` passed on those shell files with no diagnostics.
  [ShellCheck log](step1.5b-shellcheck.log) is intentionally empty.
- Tracked and newly added review payloads passed whitespace checks.

No native KWin operations were performed. Maintainer-native acceptance remains:
exercise all six forms on X11 and Wayland; verify desktop-only frame preservation,
sticky and multiple-desktop membership, negative coordinates, focus changes,
last-desktop acceptance, and delayed geometry readback. Check tiled/fullscreen/
maximized refusals, old/new component mismatch, and unchanged legacy launch and
service-lifecycle behavior. Configured dimensions/origin remain explicit; monitor
and work-area autodetection is deferred. A newly active window not yet in the
synchronized observations is rejected rather than guessed or adopted.

## Review boundary

Changed tracked files: `joetoo-kwin`, `libexec/joetoo-kwin-plan-functions`,
`libexec/joetoo-kwind`, `joetoo-kwin-resident.js`, `tests/test_step1_5a_plan.py`
(the obsolete three-operand rejection assertion), and only HANDOFF Section 5.
New tests: `tests/test_step1_5b_cli.py`, `tests/test_step1_5b_broker.py`,
`tests/test_step1_5b_move.js`. Other new files are this report and validation evidence.

[Complete candidate diff](step1.5b-review.patch) includes all new tests/evidence,
not merely tracked-file changes. No architecture, README, registry, service,
installed-system or protected-repository files were modified. No staging,
commit, push or deployment occurred. Next actor: maintainer review, followed
by separately authorized native validation/publication gates.
