# Step 1.8 — q552u01 native one-shot `under` and protected-layer finding

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**2026-11-22 · q552u01 · Plasma Wayland, KWin 6.7.6 · maintainer output.**
This is native evidence, not an assertion that the follow-on candidate passed.

## Candidate installation and focused validation

Maintainer applied the first `step18_under_candidate` patch to the uncommitted
Step 1.8 branch and ran `bash -n` and `validate_scripts` on the CLI, plan and
launch functions: all passed. Focused Python suites: `test_single_recipe_launch`
**14/14 PASS**, `test_initial_layout_broker` **19/19 PASS**; JavaScript
`test_initial_layout.js` **40/40 PASS**. `git diff --check` was clean.

Initial `-L ... under` preflight rejected a stale installed broker/resident;
`rc-service -U joetoo-kwind restart` alone did not update files. Maintainer
then used `./tools/restart_joetoo-kwind notest`, updating all 14 user-owned
POC files and unloading/reloading the KWin resident. Immediately after that
restart the D-Bus introspection reported the bus missing, but a subsequent
launch reached the newly installed single-lower protocol. This is an observed
startup race or transient, **not** proof of a permanent broker outage.

## Desktop 1: actual lower, overly strict check

Invocation: `./joetoo-kwin -L 1 konsole ssh nuthuvia under`.

Selected transcript:

```text
Registered [win-013] UUID [3822d298-98bb-4376-b4c5-a6a848b7db10]
OK launch: joetoo-kwin : bash — Konsole ... after=[1] (96,32) 1804x972
Desktop [1] initial stacking/focus result: (failed)
"geometry": "unchanged", "stacking": "failed", "focus": "verified before lower"
"lower_method": "active_slot", "lower_invoked": true
"lower_peers_intact": true, "lower_settled": true
```

The raw bottom-to-top UUID orders were:

```text
before: 3b9718b9  b72172d2  7dd39b72  50ceff66  1dab289a  3f991a08  3822d298
 after: 3b9718b9  3822d298  b72172d2  7dd39b72  50ceff66  1dab289a  3f991a08
```

The new Konsole moved below **all five ordinary higher peers**, but remained
above UUID `3b9718b9-fc05-43bd-9cc7-34f943dcb8a1`.

Read-only broker query for that UUID:

```json
{
  "resource_class": "xwaylandvideobridge",
  "resource_name": "xwaylandvideobridge",
  "desktop_file": "org.kde.xwaylandvideobridge",
  "desktops": [1], "on_all_desktops": false,
  "geometry": {"x": 928, "y": 522, "width": 64, "height": 36}
}
```

No matching positively managed record appeared. Current KDE implementation
keeps its invisible bridge window mapped at **64x36** while idle and sets
`KeepBelow`, `SkipTaskbar`, `SkipPager`, `SkipSwitcher`, opacity 0, and
transparent input. Sources:
[contentswindow.cpp](https://github.com/KDE/xwaylandvideobridge/blob/master/src/contentswindow.cpp),
[xwaylandvideobridge.cpp](https://github.com/KDE/xwaylandvideobridge/blob/master/src/xwaylandvideobridge.cpp).
The live `keepBelow`/`layer` values on q552u01 were not separately reported.

`./joetoo-kwin -l/-i win-013` showed the original managed UUID still present,
placement succeeded, desktop 1 slot 1, frame 96,32 1804x972.

## Desktop 3: integrated success

Invocation: `./joetoo-kwin -L 3 konsole ssh nuthuvia under`.

```text
Registered [win-014] UUID [267c576b-1782-4a29-be76-0b518c4e06af]
OK launch: joetoo-kwin : bash — Konsole ... after=[3] (96,32) 1804x972
Desktop [3] initial stacking/focus result: (completed)
Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [1/1] windows completed ... (completed)
```

`-l` and `-i win-014` confirmed positive managed registration, `present` and
`placement=succeeded`. Maintainer subsequently raised it manually to inspect.

## Decision and unfinished work

The maintainer approved the user-facing meaning: lower the newly registered
managed window *beneath participating ordinary visible windows*, preserving
relative peer order and geometry, while respecting KWin's special/protected
layers. Do not force it below the bridge or set a persistent KeepBelow flag.

The follow-on candidate retains **raw full-stack evidence** and adds a
KWin-property-based participation subset and excluded-reason evidence. It
must pass native re-test (desktop 1 bridge, desktop 3 ordinary peers,
inactive desktop), full regression suite, and separate maintainer acceptance.

Screenshot links (new assets are supplied separately):

- [Desktop 1, newly managed Konsole](screenshots/20261122-q552u01-under-desktop1-new-konsole.png)
- [Desktop 3, completed lower result](screenshots/20261122-q552u01-under-desktop3-success.png)
- [KWin More Actions / Keep Below menu](screenshots/20261122-q552u01-kwin-keep-below-menu.jpg)
