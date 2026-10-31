# Step 1.5c.4 first bounded implementation review

Baseline: e722bb21502b93e687e772a319db73a857c2e75c; existing authorized branch
 task/joetoo-kwin-step1.5c4-graphical-launch. Starting tree clean; HEAD, main and
cached origin/main equal. No fetch or branch mutation performed. Section 6 and
latest explicit tasking govern; stale earlier status text did not expand scope.

## Implementation and interface contracts

The new libexec/joetoo_kwin_launch_resources.py helper separates structured resource
inspection from Bash orchestration. Its local-path action returns a JSON string;
snapshot returns owner, ordered desktop IDs and count; provision/verify take required
count plus a baseline JSON snapshot and return a newly verified snapshot.
Only provision may create desktops. Python3/dbus-python are needed for -o desktop
checks; -c remains a Bash descriptive dry run without a session or dbus-python import.

KWin /VirtualDesktopManager, org.kde.KWin.VirtualDesktopManager exposes count,
desktops and createDesktop(u,s). Installed X11/Wayland XML definitions agree.
Introspection verifies the method signature; properties are read as structured data.
Session-owner and original desktop-ID prefix checks reject replacement/removal/reorder.
[KDE implementation](https://github.com/KDE/kwin/blob/master/src/dbusinterface.cpp)
forwards creation to the [desktop manager](https://github.com/KDE/kwin/blob/master/src/virtualdesktops.cpp),
which clamps insertion position to count. UInt32 maximum is therefore used to append
rather than insert ahead of a desktop concurrently appended by another actor.
Names use KWin defaults. No configuration files, active-desktop setters or removal
methods are touched.

The required count is the maximum numbered desktop in the complete validated plan.
Before confirmation, show current/required counts. After confirmation re-read, append
only the remaining shortfall and poll for positive inventory growth; verify before
each application. Existing IDs stay in order. Unknown capacity is not guessed from
configured desktop_limit: the live API has no maximum property. Installed C++ headers
happen to return 25, but that is not assumed on another host/version. Refusal/no growth
is a bounded failure with required/observed counts and retained partial additions.
Individual D-Bus calls have three-second timeouts; no-growth polling uses a two-second
deadline. There is no atomic API spanning all desktop reads and application launches;
external changes between the final check and submission still fail under existing
resident/broker verification rather than authorizing another window.

Dolphin local dispatch constructs argv: dolphin, --new-window, --, canonical-directory.
Empty target is HOME. Relative paths resolve against the physical configuration-file
directory; existing symlinks resolve, trailing separators normalize. Whitespace and
literal shell punctuation remain data. Nonexistent paths, regular files, controls
and URL-scheme targets reject -o preflight. Targets are existing readable/searchable
directories only. No eval, shell command construction, glob or tilde expansion.
Planner permits an empty target only for dolphin:local in addition to old direct mode.
It preserves all-entry slot numbering and terminal-only geometry counts.

Existing SubmitManagedLaunch, PID handoff, unique UUID registration/placement, original
slot conflict protection, order, lock, continuation and uncertainty rules are reused.
[Dolphin source](https://github.com/KDE/dolphin/blob/master/src/main.cpp) bypasses
existing-instance attachment with --new-window; any actual delegation/ambiguity still
fails conservatively. Generic managed-launch wording was adjusted so Dolphin is not
reported as Konsole/an interactive Bash. No broker/resident/registry changes.

## Validation and limitations

254 Python tests PASS without skips, including installed-header mixed-plan integration;
3 Node test files PASS; Bash syntax, Python compile, ShellCheck and whitespace PASS.
Logs: step1.5c4-{python,node,syntax,shellcheck}.log. Initial ShellCheck array-index style
finding corrected; final lint rerun. Headless tests cover structured inventory/wire
contracts, session/reorder failure, existing/sparse capacity, confirmation-time growth,
creation/no-progress/partial/API errors, suppression after provisioning failure,
Dolphin path/argv/mixed-order/cancellation/ambiguity and preserved regressions.

No native provisioning or application acceptance performed. An installed Dolphin help
attempt initialized Qt and aborted without a display; its offscreen retry did not
complete and was interrupted. No application window was observed/operated. Primary
source was used instead; installed executable option/version confirmation remains
with maintainer. No SSH/VNC connections, service changes, installation or publication.

See [native acceptance](step1.5c4-native-acceptance.md) and
[deferred investigations](step1.5c4-investigation.md). No SFTP/VNC/VPN gate, stacking,
protrusion variable, RDP, geometry tolerance or architecture edits implemented.

## Changed-file inventory and gate

Modified tracked: joetoo-kwin; libexec/joetoo-kwin-plan-functions;
libexec/joetoo-kwin-launch-functions; tests/test_step1_5c_launch.py (resource doubles
for earlier tests); Section 5 of task_step1.5/HANDOFF.md.
New implementation: libexec/joetoo_kwin_launch_resources.py.
New tests: tests/test_step1_5c4_resources.py; tests/test_step1_5c4_launch.py.
New evidence: this report, investigation, native acceptance, four validation logs and
step1.5c4-review.patch. Temporary inspection output is under /tmp, excluded.
The complete patch explicitly includes new untracked implementation/test files.

Maintainer/cloud review next, then maintainer-native checks. No further code scope
needed for this first increment. Any future underlay/viewer identity extension requires
separate approval. Staging, commit, push and draft PR creation require express
publication authorization after review/native disposition; merge/deployment remain
separate decisions.
