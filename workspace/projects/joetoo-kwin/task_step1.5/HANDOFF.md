# Step 1.5 — active task handoff

**Status:** Steps 1.5a and 1.5b completed and merged through PRs #23 and #24. Step 1.5c scope is under maintainer refinement; implementation begins only upon explicit authorization recorded in Section 4.
**Step 1.5c starting baseline:** `54f2ef6895f02dc198c79a821f76ef8343e5e701`
**Proposed task branch:** `task/joetoo-kwin-step1.5c-configured-launch`
**Detailed implementation scope:** [Step 1.5c implementation scope and outline] step1.5c%20%20implementation%20scope%20and%20outline.md)
**Current HEAD:** Determine dynamically; do not store a self-referential commit ID. Retain the existing historical baseline and completed task-branch records.
**Product authority:** `../ARCHITECTURE.md` (especially §§3–9 and implementation gate 1.5).<br>
**Governing rules:** repository-root, workspace and project `AGENTS.md`; supplemental role instructions remain draft where their approval caveats have not been removed.<br>

## 1. Maintainer-approved task definition

**Objective:** Turn the verified Step 1.4 multiwindow and asynchronous placement foundation into practical, consistent layout and launch workflows, while preserving the legacy joetoo interaction requirements and both X11/Wayland backends.

**Step 1.5 deliverables, as recorded in the current architecture:**

1. One shared geometry policy for `-c`, `-o`, and interactive `-m l|r` (no duplicate calculations). Default total terminal region 87% of usable display width for 1–3 terminals, with configurable gutters, clickable spacing and right-hand visibility. Four terminals use two-by-two layout; more than four per desktop initially rejected. Respect the supported geometry policy rather than treating the Step 1.4d 1920×1080 fixture as generalized screen detection. Do NOT hard-code "magic numbers" assign default global values which can be overridden by sourcing a config file, and which config may be overridden by (future) explicit cmdline override.  See launch POC and former xdotool_open_windows.conf as legacy references.
2. `-m l` / `-m r` (`mw` convenience) moves the **active** window to the corresponding left/right two-terminal position on its current virtual desktop. Preserve existing supported `-m DESKTOP X Y [WIDTH HEIGHT]` semantics, including omit-size behavior.
3. `-c [-f CONFIG]`: validated, colorized **dry-run** plan with no application launches.
4. `-o [-f CONFIG]`: use the plan to launch/identify/place managed windows. A configured unreachable SSH target still results in a usable, correctly placed Konsole placeholder, retaining the original local interactive Bash and allowing manual retry. Transport failures and placement/registration results must remain independent.
5. Validate `-v` / `-q` through established `script_header_joetoo` CLI conventions and preserve the requested visibility/gutter/underlay behavior as supported.
6. Reference associated SKILL.md and employ announce/act/report idiom at notice, info, and debug verbosity, to enable high script-state awareness for user experience.
7. Maintaner-added (not previously in ARCHITECTURE.md), in joetoo-kwin use script_header_joetoo varlist method to identify and show_config() to display global variable assingments resulting from default->config->cmdline , followed by launch plan from POC, and then confirm_continue_or_exit, and THEN launch

**Non-goals for Step 1.5:** Do not implement `-a`, `-d`, `-x` (1.6), checkpoint recovery (1.7), durable `-S/-r` restore (1.8) or overlay packaging (1.9). Do not turn Phase 1 into broad performance optimization. Destructive authorization and D-Bus security must be addressed before adding destructive methods.

**Proposed success criteria:** configuration dry run present the "plan" but never launches; configured windows register and reach expected geometry; SSH placeholder is not classified as a placement failure; existing windows remain unaffected; X11/Wayland native results agree; window/session-state race condition risks are mitigated; headless regression suite remains green.

## 2. Sources to inspect before coding

- Current project root: `joetoo-kwin`, `joetoo-kwin-resident.js`, `libexec/joetoo-kwind`, `libexec/joetoo_kwin_registry.py`, config and related tests; legacy xdotool_open_windows; script_header_joetoo.
- Historical planning prototype: `../archive/step1-candidate/` `joetoo-kwin-launch-poc` and `../archive/joetoo-kwin-plan-poc/` (reference only; do not restore stale code wholesale).
- Historical SSH process/rcfile experiments: `../archive/joetoo-kwin-ssh-rcfile-poc/`, `../archive/joetoo-kwin-ssh-nc-poc/` and documented `ssh_wrapper` conventions.
- Skills relevant to any affected code: discover current `.agents/skills/` first; inspect actual `script_header_joetoo` interfaces rather than assuming names or signatures.
Before any Step 1.5c implementation, agents must read the complete `task_step1.5/step1.5c  implementation scope and outline.md`, this HANDOFF.md, governing AGENTS.md files, applicable SKILL.md files, current implementation sources, and relevant archived POCs.
- Inspect the actual installed `script_header_joetoo` functions, especially `ssh_wrapper`, `swr`, `pur`, `varlist`, `show_config`, `confirm_continue_or_exit`, and announce–act–report facilities. Do not infer function behavior from names or historical descriptions.
- The detailed scope document contains the maintainer-approved functional requirements. This HANDOFF.md records execution authorization, permitted paths, task state, and review gates.

- **1.5c.1 — Configuration and launch preparation:** Integrate `-o` with the existing planner. Present effective configuration using joetoo `varlist`/`show_config`, display the launch plan and applicable warnings, then invoke `confirm_continue_or_exit` before launching anything. Preflight must reject invalid or unsupported executable plans before creating windows. Keep `-c` capable of describing the complete configuration, including not-yet-executable entries. Document both indexed-array and per-entry `desktop_session_list+=(...)` assignment styles.<br>
- **1.5c.2 — Managed local launching:** Sequentially launch supported Konsole and local application sessions, using existing positive PID/UUID correlation, managed registration and asynchronous placement verification. Preserve the shared geometry policy. Reject conflicts with existing active managed windows having the same intended desktop/slot identity. Repeated SSH targets and unrelated unmanaged windows are not inherently conflicts.<br>
- **1.5c.3 — SSH launching and placeholders:** Use the proven `bash --rcfile` startup design and installed `ssh_wrapper` function. The original interactive local Bash must survive SSH logout, connection failure or an unreachable target. The established short `nc` probe may distinguish an initially reachable SSH port from an unavailable one, without using the extended `swr`/`pur` waiting workflow. A correctly registered and placed Konsole remains a successful window-management result even when SSH is unavailable.<br>
- **1.5c.4 — Graphical applications and additional transports:** Separate implementation approval required. TigerVNC-over-SSH, graphical launch modes, possible RDP support, and underlay/stacking behavior need explicit execution contracts before implementation. Do not infer these contracts from historical labels such as `direct` or `via-ssh`.<br>
- 1.5d	Native X11/Wayland validation and final integration<br>

## 3. Task workflow — authorization boundaries are in Section 4

**Cloud/design/review agent:** inspect source and archived planner/SSH references, propose a minimal decomposition and acceptance tests; report any unresolved geometry/config interface questions to maintainer.

**Maintainer:** accept or modify requirements and operating boundaries; approve a source baseline, branch, files/operations allowed, native test procedure and any cross-agent delegation. Decide when publication is authorized.

**Local implementation agent (e.g., Codex CLI):** only after authorization, inspect the actual working tree and handoff; prepare focused candidate changes on the approved task branch, run explicitly permitted headless checks and report diffs, tests, failures and untracked files. Do not independently install/restart services, modify protected repositories, or commit/push without the relevant approval.

**Native validation:** maintainer performs or separately authorizes X11 on `gmki91` and Wayland on `q552u01`, including SSH reachable/unreachable cases as relevant. No native Step 1.5 results exist yet.

## 4. Authorization and execution controls — Step 1.5a

| Control | Approved scope / retained restrictions |
| --- | --- |
| Agent-authorized write paths | joetoo-kwin, libexec/joetoo-kwin-plan-functions, libexec/joetoo-kwind, joetoo-kwin-resident.js, relevant tests, and the agent-owned task evidence and iteration record. If necessary; relevant `tests/`; new task-support artifacts under `task_step1.5/`; and the agent-owned iteration section of `task_step1.5/HANDOFF.md`. |
| Read-only reference paths | `archive/`, including historical planner and SSH POCs; existing configuration examples; installed `/usr/sbin/script_header_joetoo`; relevant `joetoo` and `joetoo-upstream` sources, subject to their policies. |
| Explicit exclusions | No edits to `archive/`, `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, installed system files, or protected repositories. |
| Preexisting local artifacts | `.HANDOFF.md.kate-swp` and `codex_step1.5_first_run_output` are maintainer-owned, untracked files. Preserve them; do not modify, delete, stage, or treat their known presence alone as a blocking dirty-tree condition. |
| Scope expansion | If implementation requires changing a file outside the approved paths, stop and request maintainer authorization. |
| Permitted validation commands | `python3 -m unittest ...`, `node --test tests/*.js`, `bash -n`, `shellcheck -x`, `validate_scripts` where available |
| Native host operations | **Not authorized by this document** |
| Commit/push/PR creation | **Not authorized by this document** |
| Merge/deploy/official repository integration | **Separate explicit authorization and applicable repository policies** |
| Stop conditions | Missing/changed baseline, dirty/untracked files at risk, authority conflict, unexpected host effects, failing or inconclusive tests, agent request to expand scope |

Permitted initial write paths: joetoo-kwin, libexec/joetoo-kwin-plan-functions, new narrowly scoped launch/SSH startup helpers under libexec/, relevant tests, task evidence and the agent-owned HANDOFF iteration record.

Read-only/excluded: Archived POCs, the detailed maintainer-owned implementation outline, AGENTS.md, ARCHITECTURE.md, README.md, installed files, broker/resident/registry sources unless separately authorized, and protected joetoo and joetoo-upstream repositories.

Permitted validation: Headless Python and JavaScript regressions, actual installed-header integration tests, Bash syntax, ShellCheck and approved mock launch/SSH tests.

Separate approval required: Native KWin/SSH operations, installation, service changes, commit, push, PR, merge, deployment or protected-repository integration.

**Separate approval required:** Native KWin/SSH operations, installation, service changes, commit, push, PR, merge, deployment or protected-repository integration.
Maintainer authorized [20261028-23:49:38] codex to proceed with its proposed first tranche of step 1.5 (step1.5a below)<br>
Maintainer authorized [20261029-02:10:04] codex to proceed with second tranche of step 1.5 (step1.5b below)<br>
Maintainer authorized [20261029-21:46:16] codex to proceed with third tranche of step 1.5 (step1.5c below)<br>
**Initial authorized scope:** Steps 1.5c.1 through 1.5c.3, subject to the detailed scope document and approved execution boundaries. Step 1.5c.4 requires separate authorization.

Proposed 4-trance implementation plan for step 1.5 follows and will be updated in project ARCHITECTURE.md, as gets approved.<br>
Increment	Scope<br>
- 1.5a	Configuration, shared geometry planner, CLI options, -c dry run and headless tests<br>
- 1.5a.1 Implemented configuration and CLI parsing foundation, including -f, -v, -q, and defaults → config → future CLI overrides.<br>
- 1.5a.2 Adapted archived planner's geometry logic into one shared implementation, preserving the 87% terminal-width policy and configurable gutters.<br>
- 1.5a.3 Implemented -c with effective configuration display, colorized launch plan, and no application launches.<br>
- 1.5a.4 Added focused headless tests for configuration precedence, geometry, invalid inputs, and absence of launch operations.<br>
- 1.5b	Interactive -m l/r, preserve-size semantics and shared geometry integration<br>
- 1.5b.1	Implement joetoo-kwin -m [DESKTOP] l and -m [DESKTOP] r, moving the active window into the left or right of two-terminal position layout, on its current virtual desktop if DESKTOP is omitted
- 1.5b.2	Reuse Step 1.5a's terminal_geometry 2 1 and terminal_geometry 2 2 calculations; no duplicated geometry formulas
- 1.5b.3	Support -m DESKTOP [X Y] [WIDTH HEIGHT], preserving the window's dimensions when width and height are omitted and/or position when X, Y are omitted
- 1.5b.4	Add regression tests covering both movement modes, preservation of dimensions, current-desktop selection, negative coordinates, validation, and existing launch behavior
- **1.5c** — Configuration-driven `-o`, managed local and SSH launching
- **1.5c.1** — Effective configuration, complete plan display, warnings, confirmation and safe preflight
- **1.5c.2** — Sequential managed Konsole/local launching, unique registration and placement, concurrency safety, independent failure handling
- **1.5c.3** — Interactive SSH through `ssh_wrapper`, short connectivity probe, original-Bash preservation and unreachable-host placeholders
- **1.5c.4** — Graphical applications and additional transports, subject to separate approval
- **1.5d** — Integrated X11/Wayland native validation, including remaining Step 1.5b edge cases

**Approved operating policies:**

1. Preflight failure or declined confirmation must launch no windows.
2. Only one launch transaction may be active until its registration/placement outcome is definitively known. Preserve existing broker concurrency protections.
3. A known, isolated failure of one window should be reported conspicuously, but should not automatically prevent launching subsequent independent windows. Retain already-created windows and report the final layout as incomplete when appropriate.
4. If broker state, window ownership, or previous-request completion cannot be established reliably, stop launching rather than bypassing safety checks.
5. Conflicts with already managed desktop/slot identities must be rejected. Unmanaged windows must never be silently adopted or replaced. Where reliable observations indicate possible visual overlap, present a warning before confirmation.
6. Repeated connections to the same SSH target are valid and must be independently registered.
7. Unsupported execution modes must be rejected during preflight. The planner may continue to describe them for `-c`.
8. `ssh_wrapper` is the initial multi-window SSH mechanism. `swr` remains distinct and is not automatically substituted. Single-window launch syntax and retry behavior remain open for later design.
9. Preserve existing broker/resident interfaces unless a demonstrated limitation requires separately authorized changes.
10. Continue using established `script_header_joetoo` facilities and announce–act–report conventions, including established norms for categorization of severity level in messaging.

This handoff is a state/communication record, not an instruction bypass. Proposed details do not confer new permissions merely by being written here.

## 5. Agent-owned iteration record — currently empty

| Iteration | Actor | Base / changed files | Verification | Outcome and next actor |
| --- | --- | --- | --- | --- |
| 0 | ChatGPT (drafting assistance) | No repository edits; this proposed handoff only | Documentation/source review, no Step 1.5 test execution | Maintainer to review scope and authorize planning/implementation |
| 1 | Codex (2026-10-29) | Branch `task/joetoo-kwin-step1.5-layout-ssh-workflows`, HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; only this agent-owned record changed | Reread handoff and governing root/workspace/project instructions. Confirmed tracked working tree initially clean, with only the two exempted maintainer-owned untracked artifacts. Required `git fetch origin` failed: `cannot open '.git/FETCH_HEAD': Read-only file system`. No implementation or tests performed. | Step 1.5a authorization confirmed, but baseline-fetch prerequisite could not be completed within client permissions. Stopped before implementation; maintainer to fetch the accepted baseline and provide confirmation or make fetching available. No commit, push, deployment, or protected-repository changes. |

| 2 | Codex (2026-10-29) | Same branch/HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; `joetoo-kwin`, new `libexec/joetoo-kwin-plan-functions`, `tests/test_step1_5a_plan.py`, task review/example/test evidence and this record; Iteration 1 preserved | Maintainer verified fetch satisfied, HEAD equals origin/main, no incoming commits; no repeat fetch. 161 Python tests passed (17 new); 2 Node test files passed; Bash syntax, ShellCheck and diff whitespace checks passed. See [review and evidence](step1.5a-review.md). | Step 1.5a candidate ready for maintainer review: defaults/config/CLI precedence, shared geometry and colorized `-c` dry run. No launch/transport calls in headless spies. Explicit configured screen dimensions required; no native validation. Stopped at review/publication boundary; later tranches require maintainer tasking. Both exempted untracked artifacts preserved; no commit, push, deploy or protected-repository changes. |

| 3 | Codex (2026-10-29), focused review fixes | Same branch/HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; planner `print_plan`, Python planner tests, new portable test-header fixture, task review/diffs/evidence and this agent-owned record | 165 Python tests passed with no skips (including installed-header integration and ordinary tests with header reads blocked); 2 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed. Initial lint style findings corrected; final checks rerun. CLI and planner geometry/defaults/validation byte-compared unchanged against prior bundle. | Addressed all three review findings: portable ordinary tests with separately guarded installed-header coverage; display-width-aware colorized columns tested with long targets; dry-run wording explicitly permits trusted-config side effects. See [Iteration 3 review and complete diff](step1.5a-iteration3-review.md). Earlier bundle/records and maintainer artifacts preserved. No native tests or scope expansion. Maintainer review next; no staging, commit, push, deploy or protected-repository changes. |

| 4 | Codex (2026-10-29), Step 1.5b implementation | Branch `task/joetoo-kwin-step1.5b-interactive-move`; starting HEAD/origin/main `9ea76c6491e1fe2815bea514c6891dc7d5460433`. Verified clean tree and explicit broker/resident authorization in Section 4 before editing. CLI, shared planner validation, bounded broker/resident move changes, relevant tests and task evidence | 183 Python tests passed with real installed-header coverage and no skips; 3 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed. See [Step 1.5b review and complete diff](step1.5b-review.md). | Implemented all six approved forms, independent desktop/position/size preservation, shared l/r geometry, resident-support rejection, captured UUID/source binding and asynchronous resolved-value verification. Legacy Submit and launches retained. No native operations performed. Stopped at maintainer review/native-validation/publication gates; no staging, commit, push, deploy or protected writes. |

| 5 | Codex (2026-10-29), announce–act–report follow-up | Same Step 1.5b branch and HEAD `9ea76c6491e1fe2815bea514c6891dc7d5460433`; preserved existing candidate and maintainer skill edits. Changed CLI messaging, relevant CLI tests and agent-owned evidence only | Reviewed updated skill/demonstration and installed header. Demonstration at verbosity 7 reached its intentional simulated failure (exit 1). 190 Python tests passed, including installed-header integration; 3 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed. See [focused patch](step1.5b-iteration5.patch) and iteration5 validation logs. | Submission and shortcut dispatch now finish their announced lines immediately; verification detail and completion share a result line. Original action failures and auxiliary reporting faults remain distinct. Demo review finding: timestamp example captures `result` but passes the later `j_msg` status to `handle_result`; maintainer skill left untouched. Native formatting review remains with maintainer; no native operations, staging, commit, push, deployment or protected writes. |

| 6 | Codex (2026-10-29), focused native-feedback corrections | Clean existing task branch at `22e93f21e27c38f28e60fd3c2fa4f99523f13d68`; CLI, bounded broker success reporting, two Step 1.5b Python test files, agent evidence and this record | 197 Python tests passed without skips, including real installed-header integration; 3 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed. See [Iteration 6 review](step1.5b-iteration6-review.md) and [complete patch](step1.5b-iteration6.patch). | Verified desktop membership replaces optional-move placeholder zero; submission errors classified by exact known D-Bus names with original diagnostics retained; notice/info/debug reporting refined. Exact geometry comparison unchanged: regression demonstrates roundoff sensitivity, but native timeout also had displaced position, so its cause remains unproven. Maintainer reviews and validates corrections natively next; publication remains gated. No fetch, native operations, staging, commit, push, deploy, skill or protected-repository edits. |

| 7 | Codex (2026-10-29), info-detail clarification | Existing task branch and Iteration 6 candidate preserved; installed-header CLI regression and agent evidence only | 22 focused CLI tests passed, including actual installed-header checks for notice suppression, environment verbosity=6, DEBUG=0, and before/after details following the completed notice block; Bash syntax and diff whitespace checks passed | Confirmed Iteration 6 already implements the requested separate info-level j_msg after handle_result; no redundant production edit or grammar change. Full before/after detail is retained. Existing -v/-q precede -m; trailing -v remains an operand. See [Iteration 7 review](step1.5b-iteration7-review.md). Maintainer native/review gates remain; no commit, push, deploy or live operations. |

| 8 | Codex (2026-10-29), info-detail formatting | Existing candidate preserved; optional-move success detail in CLI, installed-header formatting assertions and agent evidence | 22 focused CLI tests passed, including actual header asterisk prefixes and split after PID with environment info/debug controls; Bash syntax, ShellCheck and whitespace checks passed | Success detail now uses two info-level j_msg -m calls: identity through PID, then before/after frame and tiled/fullscreen data. Other notice/debug/error messages unchanged. Unknown status formats retain all text. Maintainer native review next; no live operations, staging, commit, push or deploy. |

| 9 | Codex (2026-10-29), native acceptance evidence | Clean existing task branch at `de79be3ef14665c0510162f0e72a8352827641b8`; agent-owned validation/evidence documents and this record only | Reviewed maintainer transcripts/screenshots: latest X11 198 Python / 14 JS tests passing; native basic forms, reporting, sticky preservation and expected rejections demonstrated on X11/Wayland. No tests or native operations rerun by agent for this documentation-only iteration; whitespace checked | [Native acceptance record](step1.5b-native-validation.md) distinguishes PASS, FAIL and NOT TESTED, with sanitized evidence links. Recommend proceeding to final review/PR preparation with explicit coverage gaps and no precision-contract change. Maintainer owns acceptance/publication; no staging, commit, push, deploy or protected writes. |

### Retrospective cloud-agent collaboration records (compiled 2026-10-29)

These entries supplement existing Iterations 0–9. The `C` identifiers record substantive cloud-agent reviews in approximate chronological order without falsely renumbering Codex iterations. All source edits, native operations, testing and Git publication described as maintainer- or Codex-executed remain attributed to those actors; ChatGPT performed none of those operations unless explicitly stated.

| Iteration | Actor | Base / changed files | Verification | Outcome and next actor |
| --- | --- | --- | --- | --- |
| C1 | ChatGPT (2026-10-29), Step 1.5a closeout | Read PR #23 merge status and reviewed the accepted Step 1.5a scope; no repository edits. | GitHub confirmed PR #23 merge; Codex-reported 165 Python tests and installed-header coverage were not rerun by ChatGPT. | Maintainer/Codex proceeded to Step 1.5b; no independent cloud testing or publication. |
| C2 | ChatGPT (2026-10-29), Step 1.5b native and source review | Reviewed X11/Wayland move transcripts and broker/CLI optional-move reporting, including separate Konsole PIDs and shortcut-time target selection. | Maintainer native results showed distinct X11 windows and successful right placement. Source review located the optional-move `after=[0]` placeholder and generic Busy explanation; Wayland drag/roundoff cause remained unproven. | Recommended focused corrections and controlled focus/geometry tests; no edits or native actions. |
| C3 | ChatGPT (2026-10-29), Codex correction tasking | Drafted the Step 1.5b focused-correction prompt: verified desktop membership, Busy/unsupported classification, announce-act-report levels, regression tests and bounded geometry-precision investigation. | Prompt was based on published candidate source, Codex reports and maintainer transcripts; no tools were run to modify files or execute tests. | Maintainer supplied tasking to Codex; implementation and test evidence belong to Codex Iteration 6. |
| C4 | ChatGPT (2026-10-29), Iteration 6 review and native plan | Reviewed Codex Iteration 6 report; proposed gmki91 X11 and q552u01 Wayland acceptance sequences, installation synchronization, sticky/maximized/invalid-desktop checks, and a separate Wayland precision experiment. | Codex reported 197 Python tests, three Node files and static checks; ChatGPT did not rerun them. Geometry tolerance was not approved. | Maintainer executed native checks and synchronized the corrected task branch. |
| C5 | ChatGPT (2026-10-29), corrected native output assessment | Interpreted maintainer DEBUG runs on both backends: `-m l/r`, desktop 1/2 preservation, request flags and single-poll successful verification; corrected earlier mistaken advice about `-v`. | Native transcripts showed verified `after=[1]` and `after=[2]`, with preserved frame geometry on desktop-only moves. No ChatGPT code or host operations. | Requested remaining safety checks without reopening the six-form grammar. |
| C6 | ChatGPT (2026-10-29), safety and publication review | Reviewed maintainer screenshots/transcripts for two-window placement, sticky membership, maximized rejection, invalid desktop and `-v/-q` behavior; recommended consolidating native evidence and final PR review. | Expected rejections were reported correctly on X11/Wayland. Corrected Busy and post-capture focus cases remained headless-only or untested natively. | Recommended Step 1.5b acceptance with explicit coverage gaps; maintainer later merged PR #24. |
| C7 | ChatGPT (2026-10-29), Step 1.5c planning gate | Verified PR #24 merge at `54f2ef6`, read merged HANDOFF and architecture, inspected current launcher/planner and archived launch/SSH POCs; proposed decomposing `-o` into configuration, local launch, SSH and later graphical increments. | GitHub source and archive inspection only; no 1.5c implementation or tests. Outstanding Step 1.5b edge cases allocated to 1.5d where appropriate. | Maintainer asked Codex for an independent refined 1.5c proposal. |
| C8 | ChatGPT (2026-10-29), Codex plan synthesis | Compared Codex source-grounded 1.5c proposal with existing architecture; drafted detailed Step 1.5c scope and HANDOFF text, including preliminary slot conflicts and execution gates. | Based on Codex read-only report and repository inspection. Documents were proposed in chat, not installed or committed by ChatGPT. | Maintainer reviewed drafts and corrected premature assumptions about graphical modes and fail-fast policy. |
| C9 | ChatGPT (2026-10-29), maintainer-policy revision | Revised the proposed authorization and scope around 43-window best-effort continuation, definitive single-flight Busy completion, managed-slot identity, unmanaged-overlap warnings, repeated SSH hosts and delayed graphical/RDP/generalization decisions. | Used maintainer decisions; no code tests. Historical mode labels were not yet a verified executable dispatch contract. | Maintainer continued editing the separate scope; cloud agent to verify actual header behavior. |
| C10 | ChatGPT (2026-10-29), SSH source correction | Inspected actual `script_header_joetoo` `pur`, `swr`, `ssh_wrapper` implementations and archived nc/rcfile POCs; corrected earlier inference that `swr` was an SSH synonym and revised HANDOFF recommendations. | Source established `pur` uses ICMP ping, `swr` waits via `pur` plus `nc`, `ssh_wrapper` invokes `command ssh` and restores tty; both SSH POCs use a short `nc` precheck. No native actions. | Recommended `ssh_wrapper` for multi-window `-o`; one-off/retry semantics deferred. |
| C11 | ChatGPT (2026-10-29), published 06ab98c documentation review | Reviewed maintainer-published HANDOFF and `Step1.5c_implementation_scope.md`; identified duplicated/contradictory write permissions, broken scope link, obsolete next-gate label and fail-fast policy conflict. Prepared proposed full-file replacements/diffs as separate review artifacts. | Compared actual GitHub documents at `06ab98c`; no repository edits, builds or runtime tests performed by ChatGPT. | Maintainer to review and selectively incorporate corrections; approval boundaries remain maintainer-owned. |
| C12 | ChatGPT (2026-10-29), cloud collaboration record recovery | Audited Section 5 and recognized that previous handoff drafts had preserved Codex rows 1–9 but left only one ChatGPT drafting row. Reconstructed retrospective cloud-agent entries without renumbering Codex records. | Compared earlier candidate and published Section 5; sources were conversation transcripts, maintainer logs and GitHub records. No code tests or repository modifications. | Maintainer to review provenance and insert rows; future material ChatGPT reviews should be recorded at handoff time. |

On subsequent iterations, record only material changes, actual evidence and unresolved work. Keep detailed logs, temporary patches, input files and generators alongside this handoff under `task_step1.5/` as appropriate; keep live source/tests in the normal project-root paths.

## 6. Next gate — Step 1.5a candidate review

**Agents:** Preserve the maintainer-owned authorization and task-definition sections. Record subsequent implementation or review iterations in the assigned handoff section. Work under Steps 1.5b–1.5d requires subsequent maintainer tasking and scope decisions.

Local agent (Codex): After authorization, verify the accepted baseline, create or use the authorized isolated task branch, read the complete detailed outline and applicable instructions, then implement the approved increments. Preserve maintainer-owned sections and record material implementation/test outcomes in the agent-owned iteration record.

Cloud agent (ChatGPT): Review implementation proposals, source-grounded findings, diffs, validation results and unresolved design issues; recommend focused corrections or subsequent authorization decisions.

Outstanding validation: Carry post-capture focus races, multiple-specific-desktop membership, tiled/fullscreen refusal and controlled concurrency checks into Step 1.5d, except where Step 1.5c correctness requires earlier testing. Preserve exact geometry verification unless separately authorized to change it.

Future design: Single-window launch and retry policy, graphical/VNC/RDP integration, and possible non-KWin desktop-environment support require separate design decisions. Do not treat these possibilities as authorization for current implementation.

Publication: Maintainer retains acceptance, native testing, commit/push/PR, merge and official integration decisions. Completion of a coding iteration does not itself authorize publication.
