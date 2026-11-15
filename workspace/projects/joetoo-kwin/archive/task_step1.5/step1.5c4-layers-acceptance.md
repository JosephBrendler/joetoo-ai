# Maintainer-operated layer/group/XDG acceptance

New layer behavior has **NOT BEEN TESTED NATIVELY by Codex**. Prior first-increment
acceptance remains in step1.5c4-native-acceptance.md and is not replaced by mocks.
Use the same reviewed implementation on gmki91 X11 and q552u01 Wayland. X11 may
first test an uncommitted diff: record HEAD plus the exact reviewed diff, then link
the accepted commit to that tested content; Wayland must fast-forward that commit.
Do not claim identical tested SHAs where X11 tested uncommitted content.

## Preparation and compatibility

Maintainer installs/reloads matching broker/resident by existing human procedure;
no agent installation/restart is authorized. A reused old resident must fail launch
preflight clearly: RegistryStatus must advertise initial_layout_protocol=1 before
new -o runs. Keep the checkout's libexec helpers colocated with its CLI. Ordinary
-c remains available without KWin. CLI no longer defaults straight to /etc.

All fixtures use local Dolphin and local btop, with no network connection. Adapt
explicit dimensions to the configured test display; no work-area discovery was added.
TEST_DESKTOP/SECOND_DESKTOP are fixture inputs, not new CLI flags. Each successful
fixture needs unused intended slots: choose unused desktops below desktop_limit.
Closing a window does not release its reservation. Never erase ownership or adopt
surviving windows just to bypass a conflict. Human installation/session preparation
must account for that existing registry policy. Unrelated windows remain isolated.

From the project root, inspect the template and the files under layers-examples first.
Example interleaved case, choosing fresh desktops 4 then 2:

```bash
git rev-parse HEAD
git diff --stat
TEST_DESKTOP=4 SECOND_DESKTOP=2 ./joetoo-kwin -c -f task_step1.5/layers-examples/interleaved.conf
TEST_DESKTOP=4 SECOND_DESKTOP=2 ./joetoo-kwin -vv -o -f task_step1.5/layers-examples/interleaved.conf
# End of commands

```

Expected execution: group 4 slots 1/2/3/4, finalize group 4, then group 2 slot 1,
finalize group 2. Plan table retains original entry order; the group notice and
per-group stack/focus intent disambiguate execution order. Logical slots are unchanged.
Final focus preference in group 4 is slot 4 (last over), group 2 slot 1 (panel).
Run once with 4 currently displayed and once with another fresh group configuration
while those desktops are inactive. No automatic desktop switch is allowed.

## Per-fixture commands and expected outcomes

Use the exact command pair below for each row, replacing FIXTURE and D with its
reviewed filename and a fresh desktop. The examples are real configuration files,
not an automated GUI test or a bypass of confirmation.

```bash
TEST_DESKTOP="$D" ./joetoo-kwin -c -f "task_step1.5/layers-examples/$FIXTURE.conf"
TEST_DESKTOP="$D" ./joetoo-kwin -vv -o -f "task_step1.5/layers-examples/$FIXTURE.conf"
# End of commands

```

| FIXTURE | Expected result on each backend |
| --- | --- |
| final-under | Panel launches first, under last; initialization puts under below panel and prefers panel |
| under-only | Two cascaded under windows; preferred_uuid null, focus_attempted false; no automatic focus selection |
| cascade | Two under, one panel, two over: relative stack under1/under2/panel/over1/over2 despite interleaved launch order; focus prefers last over |
| budget-reject | Five implicit entries reject before confirmation/side effects |
| budget-warn | N=4, E=1, T=5 warns and accepts budget; four panels in 2x2 layout, explicit under window |
| allocator-reject | Five explicit panels pass budget with warning, then reject allocator limit before confirmation |
| exposure-warn | Valid rectangles; desired 1000x1000 exposure impossible; warn but allow review/confirmation |
| invalid-region | Invalid region rejects before confirmation/side effects |

For an explicit 1–4 panel progression, use four-field local Dolphin/Konsole entries
on a fresh desktop; mix applications in both orders. Panels share exactly the same
allocator independent of application. Use cascade as a basis for all six under/panel/
over order permutations, preserving entries' relative order inside a layer. Confirm
later over entries appear above earlier over entries. Inspect exposure at screen edges,
small gutters and decorations; click a safe exposed content/title region of every
window rather than assuming an offset gives a hit target. If no such region exists,
record actual exposure failure separately from geometry and stack order.

For every successful cohort record these independent outcomes:

1. Geometry and membership: GetManaged's observed frame/desktop/UUID and placement state.
2. Stacking: InitialLayoutStatus.order must equal observed_order for success; entries
   map UUIDs to layers and intended desktop. Compare with actual visual overlap.
3. Focus: preferred_uuid vs focus_attempted vs observed_active_uuid. On an inactive
   desktop focus is reported as retained intent, not successful activation. Under-only
   does not choose a target, although ordinary application startup may naturally focus
   a window before initialization. Observe before_active_uuid at the initialization point.

The info result includes the transaction ID and complete per-group outcome. Save
-vv output to retain each group's record. The bounded broker keeps only the latest
initial-layout transaction; an earlier group's ID becomes UNKNOWN after the next
group is submitted. Query the latest group ID (use saved CLI JSON for earlier groups):

```bash
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge org.joetoo.KWinBridge.InitialLayoutStatus "$LAYOUT_REQUEST" | jq .
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge org.joetoo.KWinBridge.GetManaged "$MANAGED_ID" | jq .
qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.current
# End of commands

```

Test manual click-to-raise/focus, move/resize, and manual lower after completion. Wait:
no subscriptions or flags should restore old order. No keepAbove/keepBelow or persistent
constraints are set. Check unrelated windows' identities/geometry; they may naturally
be obscured but are not explicit operation targets. A focus-induced stack mismatch must
report failure; it must not silently focus another window to force a success.

Manually switch to an inactive desktop after its group finishes and record which
window KWin naturally remembers as active. This is investigation, not an asserted
per-desktop focus guarantee. No subscription is installed to make it happen.

Cancellation and competing -o retain the prior native lock contract. New headless
coverage verifies the lock stays held through pending group initialization. Do not
repeat destructive KWin/session/capacity races. Partial missing/ambiguous target scenarios
are headless-covered; collect naturally occurring native failures without touching
unrelated windows or weakening ownership checks.

## XDG selection (read-only planning)

Demonstrate a personal config with a temporary absolute XDG root, then /etc fallback
with an absent user config. These commands create only temporary test configuration
files as the maintainer; the CLI does not create or migrate them.

```bash
NATIVE_CONFIG_TEST=$(mktemp -d)
mkdir -p "$NATIVE_CONFIG_TEST/user/joetoo-kwin"
cp joetoo-kwin-template.conf "$NATIVE_CONFIG_TEST/user/joetoo-kwin/joetoo-kwin.conf"
XDG_CONFIG_HOME="$NATIVE_CONFIG_TEST/user" ./joetoo-kwin -c
XDG_CONFIG_HOME="$NATIVE_CONFIG_TEST/absent" ./joetoo-kwin -c
# End of commands

```

First displayed config must be the temporary user file. Second must select
/etc/joetoo-kwin/joetoo-kwin.conf if available and valid; if absent or invalid, report
the actual failure instead of a PASS. An explicit -f still wins over discovery.
User-unreadable/invalid config must fail rather than fall back. Relative XDG values
are ignored in favor of HOME/.config. Configuration-free numeric -m/help stay independent.

Record PASS/FAIL/NOT TESTED by backend and SHA/diff for each case, with geometry,
stack and focus as separate columns. Do not merge or claim native acceptance from
these instructions or the headless suite.
