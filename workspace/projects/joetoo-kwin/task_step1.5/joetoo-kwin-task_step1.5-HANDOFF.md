# Step 1.5 — initial task handoff (draft)

**Status:** PROPOSED TASK SETUP; NOT YET AUTHORIZED FOR IMPLEMENTATION.  
**Intended location:** `workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md`.  
**Source baseline observed at drafting:** `joetoo-ai/main`, `99245ca4dc12900761999ed51446201df9f2aae5` (reverify when preparing a task branch).  
**Task branch:** not yet created/selected. Use a new task branch from the maintainer-approved current baseline, not the merged/deleted Step 1.4d branch.  
**Product authority:** `../ARCHITECTURE.md` (especially §§3–9 and implementation gate 1.5).  
**Governing rules:** repository-root, workspace and project `AGENTS.md`; current draft role-specific guidance has no authority until activated by maintainer.

## 1. Maintainer-owned task definition — proposed for approval

**Objective:** Turn the verified Step 1.4 multiwindow and asynchronous placement foundation into practical, consistent layout and launch workflows, while preserving the legacy joetoo interaction requirements and both X11/Wayland backends.

**Step 1.5 deliverables, as recorded in the current architecture:**

1. One shared geometry policy for `-c`, `-o`, and interactive `-m l|r` (no duplicate calculations). Default total terminal region 87% of usable display width for 1–3 terminals, with configurable gutters, clickable spacing and right-hand visibility. Four terminals use two-by-two layout; more than four per desktop initially rejected. Respect the supported geometry policy rather than treating the Step 1.4d 1920×1080 fixture as generalized screen detection.
2. `-m l` / `-m r` (`mw` convenience) moves the **active** window to the corresponding left/right two-terminal position on its current virtual desktop. Preserve existing supported `-m DESKTOP X Y [WIDTH HEIGHT]` semantics, including omit-size behavior.
3. `-c [-f CONFIG]`: validated, colorized **dry-run** plan with no application launches.
4. `-o [-f CONFIG]`: use the plan to launch/identify/place managed windows. A configured unreachable SSH target still results in a usable, correctly placed Konsole placeholder, retaining the original local interactive Bash and allowing manual retry. Transport failures and placement/registration results must remain independent.
5. Validate `-v` / `-q` through established `script_header_joetoo` CLI conventions and preserve the requested visibility/gutter/underlay behavior as supported.

**Non-goals for Step 1.5:** Do not implement `-a`, `-d`, `-x` (1.6), checkpoint recovery (1.7), durable `-S/-r` restore (1.8) or overlay packaging (1.9). Do not turn Phase 1 into broad performance optimization. Destructive authorization and D-Bus security must be addressed before adding destructive methods.

**Proposed success criteria:** configuration dry run never launches; configured windows register and reach expected geometry; SSH placeholder is not classified as a placement failure; existing windows remain unaffected; X11/Wayland native results agree; headless regression suite remains green.

## 2. Sources to inspect before coding

- Current project root: `joetoo-kwin`, `joetoo-kwin-resident.js`, `libexec/joetoo-kwind`, `libexec/joetoo_kwin_registry.py`, config and related tests.
- Historical planning prototype: `../archive/step1-candidate/` and `../archive/joetoo-kwin-plan-poc/` (reference only; do not restore stale code wholesale).
- Historical SSH process/rcfile experiments: `../archive/joetoo-kwin-ssh-rcfile-poc/`, `../archive/joetoo-kwin-ssh-nc-poc/` and documented `ssh_wrapper` conventions.
- Skills relevant to any affected code: discover current `.agents/skills/` first; inspect actual `script_header_joetoo` interfaces rather than assuming names or signatures.

## 3. Proposed scoped workflow — not authorization

**Cloud/design/review agent:** inspect source and archived planner/SSH references, propose a minimal decomposition and acceptance tests; report any unresolved geometry/config interface questions to maintainer.

**Maintainer:** accept or modify requirements and operating boundaries; approve a source baseline, branch, files/operations allowed, native test procedure and any cross-agent delegation. Decide when publication is authorized.

**Local implementation agent (e.g., Codex CLI):** only after authorization, inspect the actual working tree and handoff; prepare focused candidate changes on the approved task branch, run explicitly permitted headless checks and report diffs, tests, failures and untracked files. Do not independently install/restart services, modify protected repositories, or commit/push without the relevant approval.

**Native validation:** maintainer performs or separately authorizes X11 on `gmki91` and Wayland on `q552u01`, including SSH reachable/unreachable cases as relevant. No native Step 1.5 results exist yet.

## 4. Authorization and execution controls — maintainer to complete

| Control | Initial value / decision pending |
| --- | --- |
| Approved branch and base SHA | **Pending maintainer approval** |
| Agent-authorized write paths | **Pending**; expected to be focused project-root source/tests and assigned handoff sections only |
| Permitted validation commands | **Pending**; likely `python3 -m unittest ...`, `node --test tests/*.js`, `bash -n`, `validate_scripts` where available |
| Native host operations | **Not authorized by this document** |
| Commit/push/PR creation | **Not authorized by this document** |
| Merge/deploy/official repository integration | **Separate explicit authorization and applicable repository policies** |
| Stop conditions | Missing/changed baseline, dirty/untracked files at risk, authority conflict, unexpected host effects, failing or inconclusive tests, request to expand scope |

This handoff is a state/communication record, not an instruction bypass. Proposed details do not confer new permissions merely by being written here.

## 5. Agent-owned iteration record — currently empty

| Iteration | Actor | Base / changed files | Verification | Outcome and next actor |
| --- | --- | --- | --- | --- |
| 0 | ChatGPT (drafting assistance) | No repository edits; this proposed handoff only | Documentation/source review, no Step 1.5 test execution | Maintainer to review scope and authorize planning/implementation |

On subsequent iterations, record only material changes, actual evidence and unresolved work. Keep detailed logs, temporary patches, input files and generators alongside this handoff under `task_step1.5/` as appropriate; keep live source/tests in the normal project-root paths.

## 6. Next decision

**Maintainer:** review this proposed scope, clarify any missing Step 1.5 decisions and authorize the next bounded planning or implementation action. The acceptance criteria and permissions must be approved before another agent treats this document as an executable task.
