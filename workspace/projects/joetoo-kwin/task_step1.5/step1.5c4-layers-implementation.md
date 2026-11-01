# Graphical layers, desktop groups and XDG implementation

## Authority, baseline and status

Branch task/joetoo-kwin-step1.5c4-graphical-launch, starting HEAD
584eb2e4d024215e325e00bc6b24596e2c6f3e5c. Existing local evidence (HANDOFF row 15,
interface-review/native-plan documents and gate patch) was preserved. No fetch,
branch creation, staging or publication. Latest maintainer task explicitly approves
the bounded broker/resident extension, revised grouping/focus and XDG migration.
Earlier exclusions and proposals remain historical where superseded by that task.
No new architectural extension beyond the approved transaction was necessary.

Status: implemented and headless-tested; new native stack/focus behavior is NOT TESTED.
Prior first-increment native PASS records remain valid for that tested commit and
are not relabeled as acceptance of this feature. This document supersedes the old
gate proposal for actual implemented semantics. No SFTP/VNC/RDP/VPN gate added.

## Planner and compatibility

Four fields, or a blank fifth field as in the approved example, mean implicit panel.
A nonempty fifth field must be panel/under/over. Layer does not depend on program.
planned_explicit stores numeric explicitness separately for budget arithmetic.
Desktop-local logical slots still enumerate every entry. desktop_groups records
first appearance; planned_stack_slots and preferred_slot record complete initial
intent before confirmation. Plan table retains original entry order and now prints
execution group order explicitly. Info shows N/E counts, desired stack and focus slot.

Defaults: dt_win_limit=4, min_window_exposure_px=32. Bounded decimal validation
rejects negative/expression/overflow values. Per desktop: N>limit rejects; N<=limit
and T>limit warns; otherwise budget passes. Explicit panel counts toward E.
The existing terminal_geometry calculation now serves every panel application;
1–3 participants share the width region, four use 2x2, >4 panels reject independently
of a successful budget check. Cohorts are bounded to 256 entries by the approved
transaction implementation. -m l/r continues using its unchanged two-window geometry.

Under/over use existing graphical_* base dimensions, with deterministic shared
non-panel cascading in desktop-local file order. Offsets advance by exposure pixels
and clamp at display edges without shrinking base windows. The new stdlib-only
joetoo-kwin-exposure.py checks whether an N-by-N square in each non-panel frame can
avoid higher cohort rectangles according to the planned stack order. It sweeps
forbidden intervals, not just X/Y offsets. If valid rectangles cannot provide that
square, warn and permit confirmation; invalid rectangles reject. Decorations are
included in frame geometry; real decoration hit targets, external occlusion and
compositor visibility are not proven. The plan explicitly labels this as prediction.
Client minimum-size refusal still produces placement failure; no speculative resize
or verification tolerance was added. -c now uses Python3 for this pure offline check.

Migration is intentional: a four-field Dolphin entry now gets panel geometry,
not the old large graphical rectangle. Append under/over for a large graphical
window. Global file-order execution becomes first-appearance desktop-group execution;
within each group, original relative order and logical slots remain unchanged.

## Group orchestration and initial transaction

All entries/modes, budgets, geometries, desktop capacity and managed conflicts are
preflighted before confirmation/provisioning. After confirmation/provisioning, the
existing managed launcher registers and verifies each group's entries sequentially.
Known isolated entry failures keep prior windows and continue safely. Ambiguous or
nonterminal ownership/placement stops. Successful group entries supply registration
request IDs plus layers to finalization; failed entries never become stack targets.

The four additive D-Bus methods are:

- SubmitInitialLayout(s JSON) -> s ID, payload {entries:[{registration_request_id,layer}]}.
- TakeInitialLayout(s resident_source) -> s JSON frozen cohort, expected order,
  preferred_uuid and remaining_ms.
- CompleteInitialLayout(ss ID, JSON observation) -> void.
- InitialLayoutStatus(s ID) -> s JSON, independent geometry/stack/focus outcome,
  expected/observed order, cohort mapping, preferred/attempted/observed focus.

Existing D-Bus signatures are unchanged. Broker resolves succeeded registration IDs
through its own managed registry, requiring present, positively placed UUIDs from the
current observation source on the intended desktop. Arbitrary supplied UUIDs, duplicate
cohort entries, mixed groups and unverified registrations reject before mutation.
Registration IDs prevent stale managed-ID reuse across broker lifetimes; they are
not secrets or an independent authentication boundary. The launcher submits only its
newly succeeded cohort. No layer fields or broader schema were added to the registry.

Initial transaction state is a single bounded in-memory record with a ten-second
lease. Shared Busy checks prevent placement/correlation work overlapping initial
layout and vice versa. RegistryStatus adds initial_layout_protocol and active state;
SyncInventory advertises support only with available stack/raise/current-desktop/focus
interfaces. New -o rejects an old/incompatible running broker or resident during
preflight. Query/source refresh keeps legacy schemas compatible through additive fields.
No runtime KWin version string is assumed to establish capability.

The dedicated joetoo_bridge_initial_layout shortcut claims only frozen broker work.
Resident captures desktop/focus at claim time, validates source/lease and every cohort
UUID/frame/membership before acting, and refuses disappeared or special-mode windows.
It raises cohort windows once in under→panel→over order, preserving file order inside
each layer. It never uses an active-window-dependent lower action, sets keepAbove/
keepBelow, installs constraints, switches desktops, or subscribes to future stack repair.
Unrelated windows are never explicit mutation targets, though normal raising can cover them.

Preferred focus is last successful over, else last successful panel, never under.
Only a target on the currently displayed desktop is activated. An inactive group
retains preference as intent; under-only reports no automatic target. Ordinary app
startup may already have focused a window before this initialization point. Focus
selection is not a configuration field and no simultaneous per-desktop focus is claimed.
Native remembered-focus behavior after manual desktop switching remains an observation
question, not a guarantee or background policy.

After activation the resident reads actual stack/focus and unchanged frame/membership.
Broker compares cohort ordering and eligible focus separately from geometry. A wrong
post-focus order, changed frame, disappearance, source mismatch or expiry yields
failure rather than silently repairing or choosing another target. Immediate KWin
readback may expose native asynchronous nonconvergence; the implementation reports it
and performs no persistent retries. This is a deliberate initial snapshot, not a claim
that users or later client events cannot change the result. Unknown API/special modes
fail conservatively; native API availability/result correctness still need acceptance.

The invocation lock stays held through group finalization. Groups report individual
results; final window placement count and incomplete stack/focus groups remain distinct.
A definitive failed finalization permits the next independent group; pending/unknown
state stops. The broker retains only the latest initial transaction. Save -v/-vv CLI
JSON to retain earlier group results; earlier IDs become UNKNOWN after replacement.
Manual overrides after completion are not re-enforced.

## Configuration discovery and template

-f uses exactly the selected file. Otherwise choose an existing user file at
${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf, with empty/unset or
relative XDG_CONFIG_HOME using HOME/.config. Only absence permits /etc fallback.
Unreadable, malformed or invalid user config fails; no silent fallback. Missing both
reports both expected locations and -f. -c, -o and layout-based -m share this rule;
numeric moves and help do not discover/source config. No configuration files are
created or migrated. Existing trusted Bash sourcing and CLI verbosity precedence stay.
The displayed config is the selected path. Tests isolate HOME/XDG to avoid reading a
maintainer's actual personal config.

joetoo-kwin-template.conf is project-root sample data for eventual maintainer packaging;
see [packaging recommendations](step1.5c4-layers-packaging.md). The ebuild and protected
repositories were not edited. Examples and [native instructions](step1.5c4-layers-acceptance.md)
cover migration, interleaved groups, layers, warnings and XDG discovery.

## Validation and inventory

Final counts and command output are in step1.5c4-layers-{python,node,syntax,shellcheck}.log.
Python suite: 280 tests passed without skips, including installed-header integration.
Node: four test files passed (this runner reports files; native Node may enumerate cases).
Bash syntax/template checks, Python compile, ShellCheck and whitespace checks passed.
Template-only lint excludes SC2034 because its assignments are consumed when sourced.
Initial failures were missing new helper copies/protocol doubles and old application-
dependent expected geometry; those were updated to the approved semantics. An unused
planner-output lint finding was corrected. Final regressions were rerun.
Tests cover budgets/grammar/group order, pure region occlusion versus offsets, XDG
variants and error behavior, real orchestration with mocked IPC/processes, capability
rejection, ownership/expiry/source/disappearance, post-activation stack mismatch,
no automatic under/inactive focus and live-lock duration. Existing SSH/geometry/native
acceptance evidence is preserved. No native GUI/SSH/KWin operations performed.

Modified tracked executable files: joetoo-kwin; joetoo-kwin-resident.js;
libexec/joetoo-kwind; libexec/joetoo-kwin-plan-functions;
libexec/joetoo-kwin-launch-functions. Modified tracked tests: test_step1_5a_plan.py,
test_step1_5c_launch.py. HANDOFF modification is Section 5 only; earlier local row 15
was preserved, new row 16 records this iteration.

New implementation/data: libexec/joetoo-kwin-exposure.py; joetoo-kwin-template.conf.
New tests: test_initial_layout_broker.py, test_initial_layout.js,
test_grouped_layers_launch.py, test_layers_and_xdg.py. New evidence: this report,
acceptance/packaging notes, layers-examples/*.conf, four layers logs and complete
implementation patch. Preexisting gate/interface/native-plan evidence remains intact;
its gate patch is historical and excluded from the implementation patch to avoid nested
patch duplication. Temporary intermediate logs/scripts under /tmp are excluded.

Next actor: maintainer reviews, independently tests and runs X11 acceptance; then
maintainer-committed/pushed implementation is tested identically on Wayland. No further
interface approval is requested. Stage/commit/push/PR/merge/deploy remain separately gated.

Reproduce headless checks from the project directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_*.js
bash -n joetoo-kwin
bash -n libexec/joetoo-kwin-plan-functions
bash -n libexec/joetoo-kwin-launch-functions
bash -n libexec/joetoo-kwin-session.bashrc
bash -n joetoo-kwin-template.conf
python3 -m py_compile libexec/joetoo-kwind libexec/joetoo_kwin_launch_resources.py libexec/joetoo-kwin-exposure.py
shellcheck -x -s bash joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions libexec/joetoo-kwin-session.bashrc
shellcheck -s bash -e SC2034 joetoo-kwin-template.conf
git diff --check
# End of commands

```
