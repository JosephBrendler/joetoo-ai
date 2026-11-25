# Step 1.9 - Geometry defaults: gmki91 native X11 evidence (2026-11-25)

**Status:** Maintainer-operated source-tree geometry trial, not a packaged-path
release acceptance. This records the intended values while the Step 1.9 source
stabilization branch is still in progress; it does not add a second source of
default-value authority. The values are assigned in
`libexec/joetoo-kwin-plan-functions` by `plan_defaults()`.

## Selected layout policy

Host: `gmki91`; KWin X11 6.7.6; configured display 1920x1080. Earlier manual
`-m` experiments established useful bounds, followed by a larger graphical
`under`/`over` region and a smaller 2x2 terminal/panel allocation. The final
candidate for this trial was:

| Parameter | Value |
| --- | ---: |
| `graphical_left_percent` | 1 |
| `graphical_top_percent` | 1 |
| `graphical_width_percent` | 98 |
| `graphical_height_percent` | 94 |
| `terminal_width_percent` | 90 |
| `terminal_height_percent` | 92 |
| `terminal_gap_percent` | 1 |
| `terminal_row_gap_percent` | 1 |
| `terminal_left_percent` | 2 |
| `terminal_top_percent` | 2 |

The first graphical `under` or `over` window has predicted outer frame
`(19,10) 1881x1015`. The four panel frames in the tested 2x2 arrangement are:

| Panel slot | X | Y | Width | Height |
| --- | ---: | ---: | ---: | ---: |
| 1 | 38 | 21 | 854 | 491 |
| 2 | 911 | 21 | 854 | 491 |
| 3 | 38 | 522 | 854 | 491 |
| 4 | 911 | 522 | 854 | 491 |

These percentages refer to the full configured display rather than the KWin
work area. The terminal region leaves space to the right, while the larger
shared graphical region can remain visible behind panel windows. `under` and
`over` classify initial stacking, not different geometric regions or
permanent always-below/above states.

## Native exercise and observations

The maintainer copied `/etc/joetoo-kwin/joetoo-kwin.conf` to a temporary
per-run `/tmp/joetoo-kwin.conf` and tested this five-entry arrangement:

- Four `konsole|ssh` recipes (`nuthuvia`, `tahawus`, `slim2`, `katahdin`),
  each in `panel` on desktop 15.
- One `vncviewer|ssh` recipe (`ssh://joe@x402/display/2`) in `under` on
  desktop 15.

`./joetoo-kwin -c -f /tmp/joetoo-kwin.conf` completed validation and
predicted all five frame rectangles above. It emitted the *nonfatal* warning
`Desktop [15]: explicit layers exceed ordinary layout budget [5/4]`:
there were five recipes but only four physical panel participants.

`./joetoo-kwin -o -vv -f /tmp/joetoo-kwin.conf` subsequently registered
`win-016` through `win-020` and placed all five windows. Initial
stack/focus reported `SUCCEEDED`, with the `under` VNC viewer ordered below
the four `panel` Konsoles. The CLI reported `5/5` completed and zero failed.
The supplied screenshot showed the intended four-panel overlay with the
larger graphical viewer behind it.

The TigerVNC launcher separately reported `desktop_readiness=verified` but
`vnc_authentication=unverified` and `remote_session_usability=unverified`.
Local managed placement and stacking are **not** proof of remote login.
The target desktop was inactive during launch, so focus activation was not
attempted; focus policy should not be inferred from that screenshot alone.

In a separate `-L ... over` single-window test using the same large graphical
rectangle, placement succeeded but initial stack/focus verification returned
`incompatible maximizeMode=1`. Later `-L ... under` and `-L ... over` tests
reported completed. The earlier failure is a distinct KWin stacking edge
case; it does not invalidate the verified five-window `-o` geometry trial.

### Three-panel layout on desktop 14 (additional native validation)

The maintainer then exercised a second `-o -vv -f /tmp/joetoo-kwin.conf`
configuration on `gmki91`, this time with three `konsole|ssh` panel recipes
(`nuthuvia`, `tahawus`, `slim2`) and one `vncviewer|ssh` graphical `under`
recipe (`ssh://joe@x402/display/2`) on desktop 14. The planner and native
placement produced these verified outer frames:

| Participant | X | Y | Width | Height |
| --- | ---: | ---: | ---: | ---: |
| Panel slot 1 (`nuthuvia`) | 38 | 21 | 563 | 993 |
| Panel slot 2 (`tahawus`) | 620 | 21 | 563 | 993 |
| Panel slot 3 (`slim2`) | 1202 | 21 | 563 | 993 |
| Graphical `under` (`x402:2`) | 19 | 10 | 1881 | 1015 |

All four were positively registered (`win-021` through `win-024`), placed and
included in a `SUCCEEDED` initial stacking transaction, with the viewer
below the three panel windows. The command reported `4/4` completed, zero
failed, zero skipped and zero incomplete desktop cohorts. The supplied
screenshot confirms the three tall side-by-side panels. The `slim2` Konsole
showed an SSH connection failure but remained a successfully placed managed
terminal, consistent with the separate placeholder-versus-transport contract.
VNC authentication and remote-session usability were not proven. The
requested desktop was inactive during the launch, so no focus request was
attempted. The `-vv` display showed `desktop_limit=20` from this run's
selected `/tmp` configuration, not the `desktop_limit=24` now assigned by
`plan_defaults()` in commit `9b72161`.

## Scope and follow-up

- `-o` supports the mixed `panel`/`under` group. Single-window `-L` supports
  `over` and one-shot `under`, but `-L panel`/live reflow is deferred.
- The graphical and panel percentages are a maintainer-selected *built-in*
  candidate, not a universal work-area calculation for every screen/host.
  Configuration layering may override them.
- Earlier focused and full Python regression results preceded this final
  geometry edit; this record does **not** claim they were rerun afterward.
- Source documentation must describe constraints and point to `plan_defaults()`
  as the built-in authority. The configuration reference and annotated template
  mirror its present values; they must be checked when the defaults change.
- No modifications to packaged builds, OpenRC, checkpoint/snapshot policy,
  native KWin interfaces, or managed-window semantics are implied.
