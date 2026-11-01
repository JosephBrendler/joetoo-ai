# Bounded initial-layout focus observation

## Baseline and evidence

Branch `task/joetoo-kwin-step1.5c4-graphical-launch`, HEAD
`584eb2e4d024215e325e00bc6b24596e2c6f3e5c`. Existing dirty feature and compatibility
work were preserved. The maintainer's changed root AGENTS, ARCHITECTURE, relocated
architecture patch and new task/native fixtures were inspected/preserved, not edited.
No repository metadata, native session or installed files were changed.

Maintainer-reported X11 evidence: panel/under, five-window layering, interleaved
groups, UUID placement and manual overrides worked. Two displayed-desktop Dolphin
runs verified relative stack and geometry but immediately observed the underlay
still active. Ctrl+L later reached the panel without a click. This supports delayed
convergence, but does not establish which request caused the later keyboard focus.
The immediate active UUID was the underlay, not the unmanaged control Konsole.

Source establishes that our previous observation was too early to decide definitive
failure: the resident sampled activeWindow in the same synchronous callback as the
activation request. KDE's [X11 6.7.4 workspace wrapper](https://sources.debian.org/src/kwin-x11/4:6.7.4-1/src/scripting/workspace_wrapper.cpp/)
forwards the setter to activateWindow; [activation code](https://raw.githubusercontent.com/KDE/kwin/master/src/activation.cpp)
raises the window and requests focus subject to focus policy. The
[X11 implementation](https://raw.githubusercontent.com/KDE/kwin/Plasma/6.3/src/x11window.cpp)
uses X input-focus requests and/or WM_TAKE_FOCUS, recording an expected focus target.
These sources explain an asynchronous path and possible rejection/policy contention;
they do not prove the exact native run's cause. The source snapshots are identified
versions, not a claim to have inspected gmki91's exact built binary source.
KWin active-window observation is the approved verification criterion; it is not
an independent raw-X-server keyboard-focus measurement or causal attribution.

The [X11 scripting implementation](https://sources.debian.org/src/kwin-x11/4:6.7.4-1/src/scripting/scripting.cpp/)
exports ScriptTimer as QTimer to QJSEngine. Installed X11 and Wayland headers and
wrapper source expose windowActivated, currentDesktopChanged and windowRemoved.
Temporary activation-event verification is preferred; a QTimer watchdog also handles
missing signals, ownership/source loss and a bounded timeout. No new persistent
component, public D-Bus signature or registry semantics were necessary.

## Implemented transaction behavior

1. Claim the existing broker-owned frozen cohort and validate context/UUIDs/modes.
2. Raise each member once, in the approved order. On the displayed group, request
   the approved preferred focus target **once**. Under-only/inactive groups do not
   activate or wait, and no desktop switch is introduced.
3. Read activeWindow immediately. Matching preferred UUID completes as `immediate`.
4. Otherwise attach temporary activation/desktop/removal handlers and a nonblocking
   single-shot QTimer, rearmed only to observe. No activation or raise is retried.
5. Each observation re-resolves the cohort, validates geometry/membership/modes and
   checks local source, desktop and remaining lease. Read-only InitialLayoutStatus
   checks broker RUNNING state, so a different resident's source replacement,
   missing ownership or superseded/expired request also terminates the wait.
6. A target observation plus valid broker state completes as `delayed`. Geometry,
   relative stack and active UUID are read again after activation; a focus-induced
   stack mismatch remains a failure, with no repair or alternate focus target.

Polling of the unchanged pre-request active UUID is allowed. A different active
UUID, or a new non-target windowActivated event (even for the original window),
reports a competing activation and stops. It cannot reliably distinguish a human
from another client; the diagnostic states that uncertainty. A transient null
active state is not by itself classified as an intentional intervention.

All terminal paths stop the timer and disconnect its handler and temporary workspace
handlers. A completed flag makes queued/in-flight callbacks inert. Timer destruction
is requested when exposed by Qt. Script unload destroys its JS context; no subscription
is installed outside the bounded operation. A stalled broker reply cannot keep the
watchdog from timing out. Lease expiry does not renew the transaction, and the broker
rejects an expired completion. Nothing in a late callback can reactivate or reposition.

## Configuration and wire compatibility

New global defaults, also explicitly assigned in `joetoo-kwin-template.conf`:

| Bash configuration | Default | Supported range |
| --- | --- | --- |
| initial_focus_timeout_ms | 500 ms | 1..2000 ms |
| initial_focus_poll_interval_ms | 25 ms | 1..250 ms, no greater than timeout |

500 ms permits event-loop/X11/client acknowledgement without a long focus wait;
25 ms bounds watchdog checks when signals do not arrive. These are defaults for
native review, not a measured guarantee for every client or focus policy. The
upper observation bound remains well inside the existing ten-second transaction
lease and launcher polling window. Effective deadline is the earlier of the user's
observation timeout and the remaining claim lease; there is no lease extension.
Timing validation occurs before confirmation/provisioning/launch. Values are shown
in effective configuration output and passed explicitly in SubmitInitialLayout's
existing JSON as focus_timeout_ms and focus_poll_interval_ms. Broker validates them
independently, freezes them and returns them in TakeInitialLayout. Resident validates
the claim again; it never assumes access to Bash variables. Existing callers that
omit these optional JSON fields retain the defaults; D-Bus signatures are unchanged.
A matching updated resident is needed for delayed verification; an old resident
would still make its old immediate observation. Other preexisting timers/constants
were deliberately not migrated.

InitialLayoutStatus retains geometry, stacking and focus independently. Additive
focus_observation, focus_elapsed_ms and initial_active_uuid distinguish immediate,
delayed, timeout, unsupported observation and interrupted/expired results. Explicit
errors carry details; a focus mismatch without a resident error now also names the
preferred and observed UUID. Focus timeout does not erase verified stack or successful
window placement. Busy protection and the launcher's invocation lock remain held
until terminal finalization; the existing pending-finalization lock test remains.

## Changed files and headless verification

Production: joetoo-kwin; joetoo-kwin-resident.js; joetoo-kwin-template.conf;
libexec/joetoo-kwin-plan-functions; libexec/joetoo-kwin-launch-functions;
libexec/joetoo-kwind. Tests: tests/test_initial_layout.js,
tests/test_initial_layout_broker.py, tests/test_grouped_layers_launch.py.
Evidence: this review, focused incremental patch, HANDOFF Section 5 row 18 only.
Earlier patches and logs remain historical and unchanged.

Executed: **287 Python tests PASS**, no skips (including installed-header integration);
**36 focused JavaScript cases PASS**; **4 Node discovery files PASS**. Focused broker
suite has 13 cases. Bash syntax, JS syntax, Python compilation, ShellCheck and
`git diff --check` PASS. Template-only lint excludes SC2034 because assignments
are consumed by sourcing. Final output is retained in /tmp/joetoo-focus-*.log.
Tests exercise delayed and immediate convergence, custom observation bounds and
remaining lease, nonconvergence, competing activation, desktop/source/ownership loss,
deletion/mode/geometry changes, stale callbacks, cleanup, fallback observation,
post-focus stack mismatch, config rejection and explicit timing propagation.
No native X11/Wayland focus acceptance is claimed from these tests.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_initial_layout.js
node --test tests/test_*.js
node --check joetoo-kwin-resident.js
python3 -m py_compile libexec/joetoo-kwind tests/test_initial_layout_broker.py tests/test_grouped_layers_launch.py
bash -n joetoo-kwin
bash -n libexec/joetoo-kwin-plan-functions
bash -n libexec/joetoo-kwin-launch-functions
bash -n joetoo-kwin-template.conf
shellcheck -x -s bash joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions
shellcheck -s bash -e SC2034 joetoo-kwin-template.conf
git diff --check
# End of commands

```

## Precise maintainer X11 retest

After review, install/reload the matching CLI/helpers, broker and resident using the
already-established maintainer procedure. Codex has not installed or restarted anything.
Use the existing two-Dolphin `cascade_joe2.conf`, unchanged. Choose a desktop with fresh
intended slots, manually display it first, and use an unmanaged Konsole there to start
these commands (4 below is illustrative only; use a fresh desktop consistently):

```bash
TEST_DESKTOP=4 ./joetoo-kwin -c -f task_step1.5/layers-examples/cascade_joe2.conf
TEST_DESKTOP=4 ./joetoo-kwin -vv -o -f task_step1.5/layers-examples/cascade_joe2.conf
# End of commands

```

Confirm the displayed effective timing is 500/25 unless intentionally overridden.
Answer y, then avoid clicking windows or changing desktops while initialization runs.
Expected: both placements succeed, relative order is under -> panel, preferred UUID
is the panel. Final focus must be verified with observed_active_uuid equal to that
preferred UUID and focus_observation immediate or delayed. For delayed success,
initial_active_uuid records the stale immediate UUID and elapsed time records the
observation interval. Either immediate or delayed success is valid; do not force delay.

After completion, press Ctrl+L without clicking first and record which Dolphin receives
it. This supplements, rather than replaces, the saved KWin observation. Then manual
focus/raise/move remains unrestricted. Save the full CLI outcome, including any timeout,
interruption or stack mismatch; do not alter policy or repeatedly activate to force PASS.
After the keyboard check, the stored transaction snapshot can be queried using the ID
from the output (this is historical completion evidence, not a new live-focus sample):

```bash
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge org.joetoo.KWinBridge.InitialLayoutStatus "$LAYOUT_REQUEST" | jq .
# End of commands

```

No need to repeat the accepted full geometry/layout battery for this correction.
Maintainer reviews this [incremental diff](step1.5c4-delayed-focus.patch) and performs
the displayed-desktop test before continuing X11 acceptance; Wayland remains separately
maintainer-operated against the same reviewed implementation. No commit/publication,
deployment, native GUI/service operation or protected-repository write was performed.
