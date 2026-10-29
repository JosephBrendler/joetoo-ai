# Step 1.5 — active task handoff

**Status:** Step 1.5a is complete. 1.5b is maintainer-approved for development.<br>
**Canonical location:** `workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md`<br>
**Original task-branch baseline:** `efb8b2059a7d069043bc0506d3386599be58c17` (historical starting commit).<br>
**Step 1.5b implementation starting HEAD:** `55f4e31aafc8ba9cadb8e73daae385f7b4ad0522` (included authorization updates).<br>
**Task branch:** `task/joetoo-kwin-step1.5-layout-ssh-workflows` (created; active).<br>
**Current HEAD:** determine dynamically with `git rev-parse HEAD`; do not store a self-referential commit ID here.<br>
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

## 3. Task workflow — authorization boundaries are in Section 4

**Cloud/design/review agent:** inspect source and archived planner/SSH references, propose a minimal decomposition and acceptance tests; report any unresolved geometry/config interface questions to maintainer.

**Maintainer:** accept or modify requirements and operating boundaries; approve a source baseline, branch, files/operations allowed, native test procedure and any cross-agent delegation. Decide when publication is authorized.

**Local implementation agent (e.g., Codex CLI):** only after authorization, inspect the actual working tree and handoff; prepare focused candidate changes on the approved task branch, run explicitly permitted headless checks and report diffs, tests, failures and untracked files. Do not independently install/restart services, modify protected repositories, or commit/push without the relevant approval.

**Native validation:** maintainer performs or separately authorizes X11 on `gmki91` and Wayland on `q552u01`, including SSH reachable/unreachable cases as relevant. No native Step 1.5 results exist yet.

## 4. Authorization and execution controls — Step 1.5a

| Control | Approved scope / retained restrictions |
| --- | --- |
| Agent-authorized write paths | `joetoo-kwin` CLI; new Step 1.5a planning helpers under `libexec/` if necessary; relevant `tests/`; new task-support artifacts under `task_step1.5/`; and the agent-owned iteration section of `task_step1.5/HANDOFF.md`. |
| Read-only reference paths | `archive/`, including historical planner and SSH POCs; existing configuration examples; installed `/usr/sbin/script_header_joetoo`; relevant `joetoo` and `joetoo-upstream` sources, subject to their policies. |
| Explicit exclusions | No edits to `archive/`, `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, KWin resident JavaScript, existing broker/registry implementation, installed system files, or protected repositories. |
| Preexisting local artifacts | `.HANDOFF.md.kate-swp` and `codex_step1.5_first_run_output` are maintainer-owned, untracked files. Preserve them; do not modify, delete, stage, or treat their known presence alone as a blocking dirty-tree condition. |
| Scope expansion | If implementation requires changing a file outside the approved paths, stop and request maintainer authorization. |
| Permitted validation commands | `python3 -m unittest ...`, `node --test tests/*.js`, `bash -n`, `shellcheck -x`, `validate_scripts` where available |
| Native host operations | **Not authorized by this document** |
| Commit/push/PR creation | **Not authorized by this document** |
| Merge/deploy/official repository integration | **Separate explicit authorization and applicable repository policies** |
| Stop conditions | Missing/changed baseline, dirty/untracked files at risk, authority conflict, unexpected host effects, failing or inconclusive tests, agent request to expand scope |

Maintainer authorized [20261028-23:49:38] codex to proceed with its proposed first tranche of step 1.5 (step1.5a below)<br>
Maintainer authorized [20261029-02:10:04] codex to proceed with second tranche of step 1.5 (step1.5b below)<br>

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
- 1.5c	Configuration-driven -o managed launch and SSH placeholder integration<br>
- 1.5d	Native X11/Wayland validation and final integration<br>

This handoff is a state/communication record, not an instruction bypass. Proposed details do not confer new permissions merely by being written here.

## 5. Agent-owned iteration record — currently empty

| Iteration | Actor | Base / changed files | Verification | Outcome and next actor |
| --- | --- | --- | --- | --- |
| 0 | ChatGPT (drafting assistance) | No repository edits; this proposed handoff only | Documentation/source review, no Step 1.5 test execution | Maintainer to review scope and authorize planning/implementation |
| 1 | Codex (2026-10-29) | Branch `task/joetoo-kwin-step1.5-layout-ssh-workflows`, HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; only this agent-owned record changed | Reread handoff and governing root/workspace/project instructions. Confirmed tracked working tree initially clean, with only the two exempted maintainer-owned untracked artifacts. Required `git fetch origin` failed: `cannot open '.git/FETCH_HEAD': Read-only file system`. No implementation or tests performed. | Step 1.5a authorization confirmed, but baseline-fetch prerequisite could not be completed within client permissions. Stopped before implementation; maintainer to fetch the accepted baseline and provide confirmation or make fetching available. No commit, push, deployment, or protected-repository changes. |

| 2 | Codex (2026-10-29) | Same branch/HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; `joetoo-kwin`, new `libexec/joetoo-kwin-plan-functions`, `tests/test_step1_5a_plan.py`, task review/example/test evidence and this record; Iteration 1 preserved | Maintainer verified fetch satisfied, HEAD equals origin/main, no incoming commits; no repeat fetch. 161 Python tests passed (17 new); 2 Node test files passed; Bash syntax, ShellCheck and diff whitespace checks passed. See [review and evidence](step1.5a-review.md). | Step 1.5a candidate ready for maintainer review: defaults/config/CLI precedence, shared geometry and colorized `-c` dry run. No launch/transport calls in headless spies. Explicit configured screen dimensions required; no native validation. Stopped at review/publication boundary; later tranches require maintainer tasking. Both exempted untracked artifacts preserved; no commit, push, deploy or protected-repository changes. |

| 3 | Codex (2026-10-29), focused review fixes | Same branch/HEAD `03b3ca493c067f18d434d078fd0c8789de80ca95`; planner `print_plan`, Python planner tests, new portable test-header fixture, task review/diffs/evidence and this agent-owned record | 165 Python tests passed with no skips (including installed-header integration and ordinary tests with header reads blocked); 2 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed. Initial lint style findings corrected; final checks rerun. CLI and planner geometry/defaults/validation byte-compared unchanged against prior bundle. | Addressed all three review findings: portable ordinary tests with separately guarded installed-header coverage; display-width-aware colorized columns tested with long targets; dry-run wording explicitly permits trusted-config side effects. See [Iteration 3 review and complete diff](step1.5a-iteration3-review.md). Earlier bundle/records and maintainer artifacts preserved. No native tests or scope expansion. Maintainer review next; no staging, commit, push, deploy or protected-repository changes. |

On subsequent iterations, record only material changes, actual evidence and unresolved work. Keep detailed logs, temporary patches, input files and generators alongside this handoff under `task_step1.5/` as appropriate; keep live source/tests in the normal project-root paths.

## 6. Next gate — Step 1.5a candidate review

**Maintainer:** ReviewStep 1.5a candidate implementation, [review report](step1.5a-review.md), [review patch](step1.5a-review.patch), and validation evidence. The Step 1.5a authorization was granted and acted upon; it is **not** awaiting initial task approval. Decide whether to request focused corrections or authorize publication of a reviewed candidate. No commit, push, merge, deployment, or changes to protected repositories are authorized by this handoff alone.
maintainer decision: [20261029-01:37:01] review complete. Generating commit/push. Will open PR and merge.  Agents are requested to recommend implementation detail for 1.5a.2 for maintainer approval

**Agents:** Preserve the maintainer-owned authorization and task-definition sections. Record subsequent implementation or review iterations in the assigned handoff section. Work under Steps 1.5b–1.5d requires subsequent maintainer tasking and scope decisions.
