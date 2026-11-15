# Graphical layers: architectural approval gate (Outcome B)

Branch: task/joetoo-kwin-step1.5c4-graphical-launch.
Inspected starting HEAD: 584eb2e4d024215e325e00bc6b24596e2c6f3e5c; tree initially clean.
Current task permits investigation but requires approval before consequential
interfaces change. No executable code, tests, broker/resident or registry edited.

## Existing contract and demonstrated gap

- Planner validate_plan accepts exactly four fields. Logical slots enumerate all
  entries, but geometry counts only Konsole; terminal_geometry accepts 1–4. Changing
  those internal arrays/algorithms and presentation is ordinary feature work.
- SubmitManagedLaunch(siiiiii) carries class, desktop/slot and rectangle. TakeLaunch(ss)
  claims by new-window class; registration and _sync_managed_placement bind the actual
  positive PID/new UUID. These interfaces carry no initial stack/focus transaction.
- Complete(sss) VERIFY and _advance_placement verify exact frame/desktop for a UUID.
  They cannot establish stack order or focus. Geometry success must retain its meaning.
- captureWindow and ListObserved/GetManaged omit stack order/active-window state.
  Extending their JSON to claim stack/focus success is itself a consequential contract
  change, not a cosmetic new field.
- The resident can move the captured active window or place a newly added window.
  There is no work path to order the entire successfully registered launch cohort
  after a final under window has appeared. Changing launch order would violate policy.

[KWin scripting wrapper source](https://github.com/KDE/kwin/blob/master/src/scripting/workspace_wrapper.h)
exposes stackingOrder, writable activeWindow and UUID-resolvable window lists; it
exposes raiseWindow and constrain/unconstrain (latter since 6.5). No window-argument
lowerWindow is declared there; slotWindowLower acts on active state. Installed Window
headers expose keepBelow/keepAbove. Persistent constraints/flags conflict with free
manual overrides. Upstream availability does not establish deployed capabilities.

## Recommended bounded extension, for approval

Keep all existing D-Bus signatures and placement/registration semantics intact.
Add a separate, single-flight initial-layout transaction after sequential launches:

| Proposed method | Input / output | Purpose |
| --- | --- | --- |
| SubmitInitialLayout | s JSON -> s request ID | Validate and freeze the positively registered cohort and its requested layer order |
| TakeInitialLayout | s resident source -> s JSON | Resident claims exact cohort UUIDs, deadline and focus intent |
| CompleteInitialLayout | ss request ID, JSON -> void | Return source-bound actual stack/focus observation or explicit failure |
| InitialLayoutStatus | s request ID -> s JSON | Bounded pending/running/succeeded/failed status, geometry/stack/focus reported separately |

These names/signatures are proposals, not existing APIs. Dedicated status avoids
changing Status's placement-only semantics. A small bounded in-memory transaction
record is needed in the broker; no durable record, new managed registry or broad
registry schema is proposed.

Submit JSON protocol 1: ordered entries {registration_request_id, layer}, plus the
explicit no-desktop-switch focus policy below. The launcher supplies no arbitrary
window UUIDs. Broker resolves registration IDs to its own succeeded requests and
present managed records with successful placement; freezes exact UUIDs, intended
slots, current observer source and deadline. Reject duplicates, unknown/stale IDs,
unknown layers, mismatched current presence/source or conflicting active transactions.
Do not use managed_id alone: IDs may be reused after broker restart. Registration
UUIDs also scope the cohort to this actual launch rather than earlier managed windows.

Resident advertises initial_layout_protocol=1 and required KWin capabilities in
SyncInventory. Broker validates/forwards an allowlisted readiness summary in
RegistryStatus. Launcher checks compatibility before confirmation or side effects;
old broker/resident must reject the layered executable plan clearly, not silently
place geometry while claiming layer success. Offline -c remains available.

After verified launches, submit successful cohort only. Definitively failed entries
remain failures in final layout; never include an unregistered/ambiguous target.
Keep the invocation lock until layer completion. Extend the broker's shared Busy
gate in both directions: layer submission rejects active placement/correlation,
and placement/move submissions reject a pending/running initial-layout transaction.
Observation/query traffic continues. Claim the request via a distinct
named shortcut whose callback uses the frozen UUID cohort, never active-window
selection. This is an additional resident request schema and trigger, requiring approval.

Resolve/check every cohort UUID before mutation, recheck source/deadline/presence,
and validate that desktops/frames have not changed since the accepted snapshot.
Raise cohort windows once, bottom-to-top: under in file order, panel in file order,
over in file order. Later entries within a group are above earlier entries. This
changes initial Z-order, not configuration application-launch order. Only cohort
windows are targets; unrelated windows may naturally become covered but must not
be explicitly activated, lowered, moved or adopted.

Read stackingOrder and activeWindow after the synchronous operation. Compare the
cohort's relative ordering per desktop and the selected focus UUID; geometry result
remains distinct. A successful API return is not proof of either result. If the
snapshot does not establish convergence, report a bounded nonconvergence/failure;
do not loop indefinitely or re-enforce ordering later. Native tests must establish
whether a supported bounded follow-up observation is needed for asynchronous focus;
any such callback schema belongs to this approved transaction, not a background policy.
Report partial application truthfully if a window disappears during application;
never undo user actions or touch unrelated windows as rollback.

No persistent keepAbove/keepBelow, constraints or stack-repair subscriptions. Preexisting
special modes/flags that prevent requested order should be reported as incompatible
rather than silently cleared. No new KWin API/privileged host service is proposed:
resident capability detection must fail closed on unsupported deployed versions.
Existing observer labels are instance/staleness checks, not authentication secrets;
this does not make the session-bus service a new security boundary.

### Proposed initial focus policy (decision required)

Never switch displayed virtual desktop merely to focus a hidden window. On the
currently displayed desktop, choose the last over entry, else last panel, else last
under entry; if no cohort member is visible there, leave focus unchanged. Thus a final
under entry does not steal focus from a panel/over window. Freeze/check displayed
desktop and active focus state when claiming; if user/session changes invalidate the
operation, stop rather than force stale focus intent. Do not activate windows on all
planned desktops successively. No cohort member on current desktop is a valid
unchanged-focus outcome, not a failure. Clarify activity/multiple-output behavior
before promising semantics beyond the current configured-display scope.

## Alternatives

1. Extend each launch request with layer intent: smaller-looking wire change, but
   cannot finalize arbitrary order when under is launched last without cohort state
   and extra completion reporting. Not recommended.
2. Add optional fields to placement VERIFY: conflates geometry with stack/focus and
   still lacks a final ordering request. Not recommended.
3. Load an ad-hoc KWin script or bypass the broker with another control path: bypasses
   established ownership/lifecycle checks. Not recommended.
4. Geometry-only labels/cascades: can be useful planning, but do not implement the
   required feature. Do not ship them as successful layered launching.

## Internal implementation plan once the interface is approved

Four fields imply panel; optional fifth must be a nonempty panel/under/over. Preserve
file order, logical slots and current application/mode validation. Track explicitness
separately from effective layer. dt_win_limit defaults to 4; N implicit > limit rejects;
T > limit with N <= limit warns; otherwise budget passes. Explicit panel belongs to E.
Validate bounded decimal limit before arithmetic. Budget acceptance is separate from
geometry feasibility: reuse the 1–4 panel allocator for all panel applications and
reject >4 panels with a clear allocator-limit error until another allocator is approved.
Explicit under/over entries can exceed the budget with warnings and feasible rectangles.

Recommend min_window_exposure_px=32 logical pixels initially (approval requested).
Define desired exposure as a 32x32 square within a window's frame, clipped to usable
display bounds and uncovered by higher cohort rectangles; decorations can count only
where native hit testing confirms useful interaction. Deterministic right/down cascading
uses file order within each layer, base graphical region and edge-constrained offsets.
Keep valid base sizes; if available offset room is inadequate, warn that minimum exposure
cannot be achieved and allow confirmation. Do not shrink arbitrarily or label offsets
as verified exposure. Invalid dimensions/out-of-display rectangles reject. Track planned
cohort exposure separately from actual compositor visibility; unmanaged obstruction and
native decorations can prevent actual exposure and must not produce false success.
Several over windows use the same ordered cascade and later-over-on-top policy.

This intentionally migrates every four-field graphical entry from the old graphical
rectangle to shared panel geometry. Users wanting a large window must append under/over.
Keep -m l/r geometry unchanged; panel allocation should reuse its common calculation.
Update plan columns/effective-config display and warnings with consistent terminology.
No new syntax or geometry was partially implemented before this gate.

## Required approval and verification

Authorize the four additive broker methods, the resident claim/completion schema and
named trigger, additive capability reporting, plus bounded broker transaction state.
Authorize broker/resident edits specifically for this purpose. Approve the proposed
focus and relative-order scope, and select the exposure default/criterion (32x32 suggested).
No registry data-model or persistent stacking changes are requested.

Compatibility: existing move/launch clients keep their signatures and behavior. New
layer-aware launcher requires matching capability for -o. X11/Wayland use the same
resident path but each deployed API set and compositor result must pass native tests.
Manual moves/focus after initialization are never repaired. Test source replacement,
expired claims, deleted UUIDs, registration-ID reuse prevention, unsupported capabilities,
user-focus interference, partial failures and live-child lock release headlessly.

Outcome B: await maintainer decision; no executable edits. The native matrix/configs
below are future acceptance preparation only and are not valid in the current parser.


## Baseline validation and changed-file inventory

Unchanged code: 258 Python tests PASS without skips (installed-header coverage retained),
3 JavaScript test files PASS, Bash syntax/Python compile PASS, ShellCheck PASS.
Commands: python3 -m unittest discover -s tests -p 'test_*.py'; node --test tests/test_*.js;
bash -n on CLI/planner/launcher/startup; shellcheck -x on CLI/planner/launcher; compile
resource helper; git diff --check. Raw baseline logs remain under /tmp/joetoo-layers-baseline-*;
no duplicate historical logs were added to the repository. No feature tests or native
runs occurred. Prior maintainer native evidence remains in the existing acceptance record.

Only modified tracked file: HANDOFF.md Section 5. New files: this interface review,
step1.5c4-layers-native-plan.md and step1.5c4-layers-gate.patch. The patch includes
new evidence explicitly. No executable, scope, architecture or historical record edit.
[Future native plan](step1.5c4-layers-native-plan.md) gives proposed configurations/actions;
these are review artifacts, not current parser support. Stage/commit/push/PR/merge/deploy
remain separately gated after the architecture decision and subsequent implementation.
