# Future graphical-layer native acceptance preparation

NOT executable against the current parser. Use only after interface approval,
implementation/headless review, and a maintainer-committed implementation. Run X11
first, then fast-forward Wayland to exactly the same commit; no new branch required.
No native results are claimed here. Do not repeat provisioning/destructive session
races already covered or separately deferred.

Proposed common configuration header (setting names/default still require approval):

```bash
screen_width=1920
screen_height=1080
desktop_limit=20
dt_win_limit=4
min_window_exposure_px=32
# End of configuration

```

Use a currently available desktop D; replace the example desktop 2 as needed. Fresh
slots must not conflict with earlier managed windows. Preserve the broker history:
changing test configs does not release previously occupied intended slots. Choose
fresh available desktops/slots between accepted cases; do not restart the broker to
bypass ownership and treat surviving windows as fresh managed windows.

Each row supplies desktop_session_list values, in exact file order:

| Case | Entries | Expected future result |
| --- | --- | --- |
| Implicit application-independent panels | `2\|konsole\|local\|btop`, `2\|dolphin\|local\|` | Two panel rectangles; no application-based underlay |
| Explicit layers | `2\|dolphin\|local\|\|under`, `2\|konsole\|local\|btop\|panel`, `2\|dolphin\|local\|\|over` | Under below panel below over; over focused only if desktop currently displayed |
| Final under | `2\|konsole\|local\|btop\|panel`, `2\|dolphin\|local\|\|under` | Launch order unchanged; panel above final under, focus follows approved policy |
| Cascades | Two Dolphin-under entries, one Konsole-panel, two Dolphin-over entries | Configuration-order cascades; later within each layer above earlier; inspect every exposed target |
| Implicit budget rejection | Five four-field Dolphin-local entries on desktop 2 | N=5 rejects before confirmation; zero windows |
| Explicit budget excess | Four implicit panel entries, one explicit Dolphin-under | Budget warns and accepts; panel allocator remains feasible |
| Explicit panel allocator excess | Five explicit panel entries | Budget passes with warning, geometry rejects >4 panels under recommended allocator policy |
| Insufficient exposure | Cascade case with a reviewed large min_window_exposure_px | Valid geometry warns and permits confirmation; never claims minimum exposure succeeded |
| Invalid geometry | Cascade case with invalid display/region percentage | Reject before confirmation; no windows |
| Invalid grammar | Empty fifth field, unknown layer, six fields | Reject before confirmation |

Create each trusted config manually with the common header and an indexed Bash
array, e.g. the explicit-layers case:

```bash
desktop_session_list=(
    '2|dolphin|local||under'
    '2|konsole|local|btop|panel'
    '2|dolphin|local||over'
)
# End of configuration

```

Future per-case commands (TEST_CONFIG is the exact reviewed file path):

```bash
git rev-parse HEAD
./joetoo-kwin -c -f "$TEST_CONFIG"
./joetoo-kwin -vv -o -f "$TEST_CONFIG"
# End of commands

```

For a valid plan first decline and verify no side effects, then rerun and confirm.
For every case separately record geometry, actual cohort stack order, focus UUID,
logical slots, and displayed desktop. Compare the future transaction's recorded
observations with visual KWin behavior; headless results do not establish native Z-order.

Repeat the explicit-layer cases in all six layer permutations and both application
orders, retaining launch file order. Repeat with 1–4 panels and multiple under/over
windows. Test a final under entry on current desktop and on a different desktop;
no automatic desktop switch is proposed. Verify under/over identity with unrelated
Dolphin/Konsole already open: they must not be adopted or explicitly manipulated.

For each cascade click the exposed area of every window to raise/focus it, then move,
resize and manually lower/raise windows. Wait beyond initialization: no repair or
persistent always-on-top/below constraint should restore old policy. Check decorations,
clipping, small usable areas and later overlapping windows; offsets alone do not PASS.
Verify the lock is released with living windows, and that a competing invocation is
Busy while initial stacking finishes. Collect missing/unsupported capability diagnostics
rather than falling back to active-window-dependent actions. No destructive desktop
capacity or KWin replacement tests are requested.
