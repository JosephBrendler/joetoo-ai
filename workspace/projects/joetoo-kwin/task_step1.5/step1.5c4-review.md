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
Empty target is HOME. Relative paths resolve against HOME independently of the
configuration-file directory; existing symlinks resolve, trailing separators normalize. Whitespace and
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


## Native acceptance review and focused corrections

Accepted candidate 35d1b072b763df8126c602d9840c0ad243a9a656 substantially passed
maintainer-reported X11/Wayland native acceptance; see the updated native report.
This corrective iteration starts from that clean commit on the same task branch.
Relative paths now use HOME (helper config argument retained for compatibility).
Validator stages close their announcement before running output-producing actions,
then open a result line for handle_result. The original action status and reporting
status remain separate; diagnostics are not captured in a state-losing subshell.
Desktop text distinguishes adequate existing capacity from an exact append shortfall.
An added mock Dolphin lifetime test proves completed-launch lock reacquisition while
the original process remains alive; no lock implementation change was necessary.

258 Python tests passed without skips, including installed-header validation-format
coverage; three JS test files passed; syntax/Python compile, ShellCheck and whitespace
checks passed. New logs use the step1.5c4-corrections prefix. Current focused diff is
step1.5c4-corrections.patch; the earlier review patch remains historical evidence.
No new native tests or executable broker/resident/registry/layer changes were made.
The separate step1.5c4-layer-proposal.md is a proposal only, requiring maintainer decisions.

## Merge-readiness audit — a3c50fc

**Recommendation: ready for maintainer merge decision for the implemented bounded
candidate. No blocker identified by this focused read-only audit.** This does not
merge the branch or close deferred transports/the separate Step 1.5d milestone.

Inspected clean local HEAD `a3c50fc54f95e25fd766b58037e773977f854f33` on
`task/joetoo-kwin-step1.5c4-graphical-launch`, source/tests and current architecture.
The branch remains ahead of the cached local main; no remote synchronization claim
or publication action is made. The initial sections of this review describe earlier
increments; this subsection is the current assessment. [Native closure evidence](step1.5c4-native-acceptance.md#graphical-layers-and-bounded-focus--acceptance-closure-at-a3c50fc)
is maintainer-reported, not Codex-operated. Automated suites were inspected, not rerun
for these documentation edits. Maintainer reports 287 Python and 50 JS tests passing
on Wayland; prior agent evidence and its runner's file-level counts are retained.

### Contract traceability

Architecture references below are to [ARCHITECTURE.md](../ARCHITECTURE.md).
The [scope outline](Step1.5c4_implementation_scope.md) remains the wider roadmap;
later explicit layer/group/focus/XDG authorizations (recorded in HANDOFF iterations
16–18 and the focused implementation records) refine its earlier geometry/order text.
“Satisfied” means source and available tests/native evidence support the bounded
contract, not that all environments or races have been exercised.

| Contract / requirement | Inspected implementation | Available evidence | Assessment |
| --- | --- | --- | --- |
| 1. Application-independent layers; stable order inside each layer — approved layer task, architecture §§4/6 ownership/geometry | [planner](../libexec/joetoo-kwin-plan-functions) `validate_plan`, `calculate_plan`; [broker](../libexec/joetoo-kwind) `SubmitInitialLayout` computes under/panel/over order | `LayerPlanTests.test_default_panels_and_explicit_layers`; JS layer-order test; native mixed layers on both hosts | Satisfied; older terminal-only prose is superseded as noted below |
| 2. Four panels, implicit/explicit budget — approved dt_win_limit policy; §6 shared geometry | planner `validate_plan`, unchanged 1–4 `terminal_geometry`; exposure helper warns independently of geometry validity | `test_budget_thresholds_and_allocator_constraint`, `test_exposure_geometry_checker_uses_regions_not_offsets`; native budget-warn and four-panel layout | Satisfied; explicit budget exception does not waive allocator limits or promise actual clickable exposure |
| 3. Interleaved desktop groups, bounded finalization — approved grouped task; scope §3 provisioning | planner `desktop_groups`; [launcher](../libexec/joetoo-kwin-launch-functions) `open_plan` launches relative entry order then finalizes each group before the next | `GroupedLaunchTests.test_first_appearance_group_order_and_finalize_before_next_group`, nonterminal-stop test; native interleaved groups on both hosts | Satisfied; first-appearance desktop order deliberately replaces global file order |
| 4. Positive UUID ownership, unrelated-window isolation — §§4/5/10; scope §§2/3 | broker resolves registration request IDs to placed/present current-source records; resident `layoutUUID`, `resolveCohort` resolve exact stack identities; windowList is diagnostic only | broker `test_no_arbitrary_or_duplicate_identity`, disappearance tests; JS canonical UUID/missing-stack tests; native independent Dolphin isolation from first increment | Satisfied; no class/title fallback or adoption |
| 5. Coordination, Busy, deadline, stale callbacks — §§4/5/10; scope §6 | launcher FD9 `flock` spans confirmation through finalization, child closure; broker `_initial_layout_active`/shared Busy guards, ten-second lease; resident `done`, `contextError`, read-only broker guard | broker `test_shared_busy_and_expiration`; grouped pending-lock test; correction tests for cancellation/live children; native first-increment Wayland Busy/cancellation/reacquisition | Satisfied; destructive native races remain untested |
| 6. Initialization only, manual overrides — §§4/6/10; scope §3c | resident raises cohort once; activation may itself raise; `cleanup` stops timer/disconnects temporary handlers; no keepAbove/Below assignment or background repair | JS manual-control/cleanup/late-callback cases; native move/resize/raise/desktop-return on both hosts; Wayland win-007 conflict after manual changes | Satisfied |
| 7. Last successful over, else panel; inactive/under-only suppression; one activation — approved focus rule | broker selects preferred from successfully registered cohort; resident visibility check and single `workspace.activeWindow = target` assignment | broker preference/inactive tests; JS last-panel/final-under and exactly-one-request cases; native under-only and displayed-desktop panel | Satisfied; inactive preference is intent, not simultaneous per-desktop focus |
| 8. Bounded nonblocking verification/interruption — approved focus correction; §§4/10 | resident temporary signals plus QTimer watchdog, source/desktop/UUID/mode/geometry checks, terminal cleanup; broker `CompleteInitialLayout` readback validation | 36 focused JS cases cover delayed/immediate, timeout, competing events, source/desktop loss, expiry and post-focus stack mismatch; broker focus-timeout preserves stack/placement; native X11 delayed 5 ms and Wayland immediate 0 ms | Satisfied; competing client vs human cause remains explicitly uncertain |
| 9. Configurable new operational timing — §4 Configuration and operational bounds | planner defaults/validation; CLI varlist; template assignments; launcher JSON; broker validates/freezes/returns bounds; resident validates and clips observation to remaining lease | grouped effective-payload/invalid-timing tests; broker bounds test; JS custom-timeout/remaining-lease case; native 500/25 ms | Satisfied for new focus parameters; migration of preexisting constants is a permitted later focused task |
| 10. XDG user-first, explicit -f, system fallback — §3 configuration discovery | [CLI](../joetoo-kwin) `select_config`, `check_plan`, layout-based move path; bad existing user file does not fall through | `XdgDiscoveryTests` precedence/error/environment/move cases; grouped no-f launch; native X11 system fallback | Satisfied; extra native user-file-precedence transcript not supplied for closure |
| 11. Original interactive Bash after SSH — §7, scope preservation | launcher argv uses separate Konsole and `bash --rcfile`; [session file](../libexec/joetoo-kwin-session.bashrc) runs `ssh_wrapper` without exec/exit/replacement Bash | `test_original_shell_survives_unreachable_and_ended_ssh`; earlier placeholder acceptance; native Wayland win-022 returns to original local Bash PID 3957428 | Satisfied; window presence remains separate from transport telemetry |
| 12. Existing protocol/CLI compatibility — §3 D-Bus contract, §9 CLI, scope §6 | existing method signatures retained; four additive initial-layout methods, capability reporting and optional timing JSON; numeric moves remain config-free | read-only AST comparison against local main found no changed established D-Bus signature; current move/placement tests retained; XDG config-free numeric move test | Satisfied with intentional layer/default/group migration; updated layered -o needs matching broker/resident |

### Findings and disposition

**Blockers:** none identified. The original premature immediate-focus failure is
historical and resolved by the maintainer's successful corrected transaction; it is
not erased or converted into an original PASS. Native PASS does not establish every
failure path, but the inspected safeguards and focused headless cases cover the
unperformed rare interruption/expiry scenarios without requiring destructive tests.

**Nonblocking follow-ups:**

- Unmanaged overlap warnings repeat because preflight rechecks remaining entries.
  They predict possible intersection, not stacking order; they do not adopt/conflict
  with those windows. Deduplication would be presentation refinement, not correctness.
- The trusted-Bash side-effect statement is accurate: sourcing already occurs before
  validation. It describes the trust boundary, not a promise that -c sandboxes arbitrary
  configuration code. Its wording/placement and validation-versus-geometry warning
  ordering may be refined later; the inspected AAR paths preserve action/report status.
- 500/25 ms defaults are bounded and configurable. Event-driven completion at 5 ms
  is compatible with a 25 ms watchdog interval. Do not tune from two observations or
  infer an X11/Wayland timing guarantee; retain truthful timeout on nonconvergence.
- Documentation consolidation: architecture §6 and scope §§2/3c/6 still describe
  terminal-only geometry, global file order and percentage protrusion, while later
  approved tasks explicitly require application-independent panel, desktop grouping
  and pixel exposure. The architecture component table also retains an /etc label
  beside its newer explicit XDG contract. HANDOFF §6 is first-iteration tasking.
  These are stale descriptions, not evidence of a source deviation from the later
  approved decisions. Maintainer may consolidate authoritative prose separately;
  no architecture or maintainer-owned section is edited here. Earlier reviews' future
  tense and first-increment NOT IMPLEMENTED results remain clearly historical.
- Native evidence is a supplied summary, not independently retrieved raw artifacts.
  Additional HOME-relative/spaces, config-error formatting and user-file-precedence
  native transcripts are not claimed. Headless coverage makes these evidence limits
  nonblocking; exact multi-monitor/decorated hit-target exposure remains unguaranteed.

**Future scope / remaining obligations:**

- Packaging gate 1.9 must install/distribute the existing template and required helpers,
  document optional per-user configuration and provide the required ebuild post-install
  guidance without writing HOME files. The [packaging notes](step1.5c4-layers-packaging.md)
  recommend paths; the final template path, dependencies and pkg_postinst implementation
  remain maintainer integration work, not fulfilled by merely adding a project template.
- SFTP/TigerVNC-over-SSH/RDP/other application dispatch requires separate scope/identity/
  transport decisions. No direct VNC or VPN gate was introduced. These wider-outline
  items are not implicitly accepted or abandoned by merging this bounded candidate.
- Step 1.5d integrated regression, managed closure (1.6), checkpoint/reconciliation
  (1.7), durable restore (1.8), slot release and transport telemetry remain separate.
  Existing timing constants may be inventoried/migrated in focused increments under
  architecture §4; this does not retroactively require a wholesale timer rewrite here.

### Closure checks and next decision

Only this review, the native acceptance record and HANDOFF Section 5 were edited.
Whitespace and local relative-link/anchor checks passed; implementation, templates,
tests and architecture were unchanged. Branch/HEAD remain the unmerged task candidate.
No automated implementation tests or native operations were executed in this closure.
Next actor: maintainer reviews the documentation and decides PR/publication/merge
readiness; this recommendation supplies no publication or merge authorization.
