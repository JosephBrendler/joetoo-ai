# Step 1.5c.5 — remote resources and graphical remote desktops: active task handoff

**Current maintainer status (2026-11-03):** Step 1.5c.5a (Dolphin SFTP)
is accepted and closed. The maintainer reports that Step 1.5c.5b
(TigerVNC-over-SSH) has been merged following native X11 and Wayland/XWayland
acceptance. **Step 1.5c.5c (RDP feasibility and decision) is now authorized
for read-only, server-first research and a comparative recommendation only.**
RDP client/server implementation, package or service changes, native network
connections and Step 1.5d integrated regression are not authorized here.
Earlier VNC investigation directions below are historical.

**Canonical location:** `workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md`.

**Active 1.5c.5c branch (maintainer-approved):**
`task/joetoo-kwin-step1.5c5c-rdp-feasibility`. Begin from the maintainer's
merged, current `main` after verifying `git status`, remote tracking and the
actual base SHA. This document does not assert that the new branch exists
or that its changes have been committed/pushed. The historical 1.5c.5b
branch was `task/joetoo-kwin-step1.5c5-remote-access` (local review merge
`949268e`; published archive commit `c5d7f28`). SFTP/advisory baseline:
`b8120f7c9aad608e26b5c147561a5eee5756a8e9`.

**Authoritative design:** [ARCHITECTURE.md](../ARCHITECTURE.md) and [Step 1.5c.5 approved scope](Step1.5c5_implementation_scope.md). This HANDOFF grants operational permissions only within that design. Governing root/workspace/project `AGENTS.md` and applicable `.agents/skills/` take precedence. `joetoo` and `joetoo-upstream` retain their read-only/advisory restrictions for AI.

**Accepted 1.5c.5a evidence:** [Native acceptance record](step1.5c5a-native-acceptance.md), [implementation review](step1.5c5a-review.md) and [URI/security contract](step1.5c5a-dolphin-sftp-contract.md). See Section 4 for corrected interpretation of the previously omitted X11 positive advisory. Earlier Step 1.5c.4 acceptance remains in [its native closure](step1.5c4-native-acceptance.md).

**Step 1.5c.5b native closeout evidence (maintainer, 2026-11-03;
formal milestone merge pending):** `gmki91` X11 registered and placed the
actual TigerVNC desktop viewer, verified coexistence with an independently
managed Dolphin window and stacking, observed loopback-only SSH forwarding,
and confirmed viewer/SSH teardown. `q552u01` Wayland/XWayland used the final
nine-file installer and launched `yorsqui:2` on desktop 10, slot 1;
`win-001` and exact KWin UUID `afbdbaa1-3c45-49a4-a18f-ac2793fbbb1d`
were verified by the broker, geometry was 1670×918, initial layout was
`SUCCEEDED`, the remote desktop was visually usable, and viewer/SSH PIDs
`1183613`/`1183610` were absent after closure. CLI remote-session and VNC
authentication fields remained `unverified`, correctly independent of the
human observation. Both machines reported all nine installed files `Current`.
The maintainer reported 382 Python/53 JavaScript passes on `gmki91`, and
405 Python/53 JavaScript passes on `q552u01` before moving the 23 legacy
migration-only tests outside normal test discovery. Repeat regressions after
the archive move were not claimed.

**Legacy-backup housekeeping (maintainer, 2026-11-03):** 171 historical backup
files on `gmki91` and 135 on `q552u01` were manually moved into their
respective `~/.local/state/joetoo-kwin/legacy-backups/` trees; no legacy
contents were deleted. The proposed migration utility and tests were archived
at `archive/aborted_backup_migration_tool/` in `c5d7f28`; no real migration
Gate B/C was executed. Historical Iteration 33 records the abandoned proposal,
not a pending migration requirement. The active installer preserves replaced
versions in its separate content-addressed archive and avoids new timestamped
backups in production directories.

## Active authorization — Step 1.5c.5c RDP feasibility (2026-11-03)

**Maintainer decision and motivation.** Investigate RDP starting with the
*server/session model*, then clients. The maintainer has working
TigerVNC-over-SSH but little prior RDP experience and wishes to start a
remote graphical login/session, not merely observe an already-logged-in
screen. Several Ubuntu machines currently offer RDP-oriented GNOME access.
Keep existing TigerVNC working and do not assume RDP is categorically more
secure than verified SSH-protected VNC.

**Scope: research and comparison only.** Reuse Section 5 of
`Step1.5c5_implementation_scope.md` and the project's architecture. First
separate (a) sharing an existing session, (b) logging in remotely to a new
session, and (c) reconnecting to a persistent session; do not assume one
server supports all three. Compare the following server-side options and
verify version-specific behavior: Ubuntu/GNOME Remote Desktop's RDP
*Desktop Sharing* versus *Remote Login* (GNOME/GDM, Wayland), `xrdp` with
`xorgxrdp` and a compatible Xorg desktop, and KDE KRDP's logged-in Plasma
session service. Determine whether an independent KDE/Wayland remote login
is actually supported; do not conflate KRDP with KRDC. Consider OpenRC
compatibility and the existing remote-login behavior of Ubuntu systems.

**Client evaluation follows the server requirements.** Compare KRDC,
Remmina, `xfreerdp`, `sdl-freerdp`, and supported Wayland-native FreeRDP
frontends if available, on `gmki91` (X11) and `q552u01` (Wayland/XWayland).
Evaluate exact installed versions/USE flags/executables, credential and
certificate trust policies, command-line/profile security, unique desktop
window identity versus preliminary login dialogs, window reuse, process
lifetime, and fit with the existing broker's UUID-based placement.

**New maintainer-supplied inventory (not a native RDP test).** On `gmki91`
Gentoo Portage showed `net-misc/freerdp-3.32.1` installed; executables
`xfreerdp`, `sdl-freerdp`, `freerdp-shadow-cli`, `freerdp-proxy`, and
`krdpserver` were present. `kde-plasma/krdp-6.7.5-r1` was subsequently
confirmed installed. A proposed Remmina 1.4.43 installation had `rdp`,
`ssh`, `vnc`, and `wayland` USE flags but its completion was not shown.
The FreeRDP emerge output showed `(-wayland)`; identify the *effective*
Portage masking source before attributing it to the joetoo profile.
`q552u01` installed-client inventory and all server configurations remain
unverified.

**Security gates.** Assess TLS certificate identity, trusted CA or pinned
fingerprints, login authentication/NLA where supported, downgrade behavior,
network binding, VPN/SSH gateway choices, credential handling and least
exposure. No direct public TCP/3389, automatic trust override, `/cert:ignore`,
password in argv/history/logs, security weakening, firewall change or
server start is authorized. Separately report encrypted transport, verified
server identity, authenticated login and graphical usability; success of a
window launch is not proof of any of these.

**Permitted actor and edits.** Codex may read joetoo-ai code/docs, upstream
technical documentation and nonsecret local installed-package metadata. It
may propose a small read-only command checklist for the maintainer and edit
**only this HANDOFF.md** with concise findings within the approved joetoo-ai
research branch after verifying a clean working tree and applicable
`AGENTS.md`/skills. No new framework, source implementation, test harness,
configuration or separate planning files. Do not alter `joetoo` or
`joetoo-upstream`, install packages, configure RDP servers, open real
connections, handle credentials, commit, push, open a PR or merge. If read
access to a host or file is unavailable, ask the maintainer for exact
nonsecret output rather than inventing the result.

**Deliverable and stop gate.** Present a compact *server-first* capability
matrix, a client matrix limited to credible candidates, an explicit security
assessment, a recommended Ubuntu-first native pilot the maintainer may
separately authorize, and a ranked decision: pursue an RDP client/endpoint
contract or retain TigerVNC as primary. Label every finding inspected,
maintainer-reported, proposed or untested. Stop for approval before native
RDP tests or any implementation. The maintainer remains responsible for
selecting server, client, login semantics, trust policy, packaging and
publication. Step 1.5d remains a separate gate.

## 1. Maintainer-approved task definition — historical scope and accepted outcome

**Objective:** Turn the verified Step 1.4 multiwindow and asynchronous placement foundation into practical, consistent layout and launch workflows, while preserving the legacy joetoo interaction requirements and both X11/Wayland backends.

**Original Step 1.5 deliverables (historical requirements snapshot):** Later approved graphical-layer policy extends and, where noted, supersedes the original terminal-only geometry and global-order assumptions. The accepted Step 1.5c.4 implementation is traced in the closure audit.

1. One shared geometry policy for `-c`, `-o`, and interactive `-m l|r` (no duplicate calculations). Default total terminal region 87% of usable display width for 1–3 terminals, with configurable gutters, clickable spacing and right-hand visibility. Four terminals use two-by-two layout; more than four per desktop initially rejected. Respect the supported geometry policy rather than treating the Step 1.4d 1920×1080 fixture as generalized screen detection. Do NOT hard-code "magic numbers" assign default global values which can be overridden by sourcing a config file, and which config may be overridden by (future) explicit cmdline override.  See launch POC and former xdotool_open_windows.conf as legacy references.
2. `-m l` / `-m r` (`mw` convenience) moves the **active** window to the corresponding left/right two-terminal position on its current virtual desktop. Preserve existing supported `-m DESKTOP X Y [WIDTH HEIGHT]` semantics, including omit-size behavior.
3. `-c [-f CONFIG]`: validated, colorized **dry-run** plan with no application launches.
4. `-o [-f CONFIG]`: use the plan to launch/identify/place managed windows. A configured unreachable SSH target still results in a usable, correctly placed Konsole placeholder, retaining the original local interactive Bash and allowing manual retry. Transport failures and placement/registration results must remain independent.
5. Validate `-v` / `-q` through established `script_header_joetoo` CLI conventions and preserve the requested visibility/gutter/underlay behavior as supported.
6. Reference associated SKILL.md and employ announce/act/report idiom at notice, info, and debug verbosity, to enable high script-state awareness for user experience.
7. Maintaner-added (not previously in ARCHITECTURE.md), in joetoo-kwin use script_header_joetoo varlist method to identify and show_config() to display global variable assingments resulting from default->config->cmdline , followed by launch plan from POC, and then confirm_continue_or_exit, and THEN launch

**Non-goals for Step 1.5:** Do not implement `-a`, `-d`, `-x` (1.6), checkpoint recovery (1.7), durable `-S/-r` restore (1.8) or overlay packaging (1.9). Do not turn Phase 1 into broad performance optimization. Destructive authorization and D-Bus security must be addressed before adding destructive methods.

**Original proposed success criteria (now assessed for the bounded Step 1.5c.4 candidate):** configuration dry run present the "plan" but never launches; configured windows register and reach expected geometry; SSH placeholder is not classified as a placement failure; existing windows remain unaffected; X11/Wayland native results agree; window/session-state race condition risks are mitigated; headless regression suite remains green.

**Current phase:** Steps 1.5c.5a and 1.5c.5b are accepted; the maintainer
reports the 1.5c.5b branch merged. Step 1.5c.5c is authorized for read-only,
server-first RDP feasibility and comparative decision support as defined in
the active authorization above. Earlier VNC investigation and execution
directions below document historical approvals, not present instructions.
No RDP implementation, native RDP connection, or Step 1.5d work is authorized.

## 2. Required inspection for Step 1.5c.5b

The next actor (Codex) shall establish the **actual branch, HEAD, worktree differences and governing policies** before editing anything. Inspect current CLI/planner/launch-functions, broker/resident contracts, relevant regression harnesses, template, architecture and scope. Read the relevant joetoo SSH/header, announce–act–report and pseudo-boolean skills and verify any invoked utility against source rather than relying on remembered behavior.

Inspect the [archived VNC proof of concept](../archive/tigervnc-poc/vnc-via-ssh-launch) and, crucially, the maintainer's **actual currently working KDE application-launcher `.desktop` entry or invoked command**. The archived POC uses `vncviewer ... -via ... localhost:2`; it is a reference, not a verified description of the maintained launcher or an approved final transport. If the current KDE launcher is not available in the checked-out files, ask the maintainer to supply that **one concrete command/file** before making claims or implementing it. Also inspect installed TigerVNC, OpenSSH and relevant server configurations/options using non-network, non-destructive methods. Do not read or publish secret keys, passwords or tokens.

The first deliverable is a **concise POC-to-managed-launch contract presented in the conversation or a focused update to this existing HANDOFF**, not a new planning document. It must establish: accepted `DESKTOP|vncviewer|ssh|TARGET[|LAYER]` grammar; validated viewer and SSH argument arrays; whether TigerVNC `-via` or explicitly managed `ssh -L` is actually appropriate; SSH host identity/authentication; loopback-only VNC forwarding; destination/display/port handling; port collisions and readiness; viewer process/window identity versus transient dialogs; child/tunnel lifetime, cancellation and teardown; timeout and truthful independent connection/placement reporting. Identify unknowns explicitly.

## 3. Roles, sequencing and review

**Maintainer:** approves the concrete VNC endpoint and tunnel/security contract, controls native X11/Wayland and network/credential testing, and alone stages/commits/pushes/merges/deploys changes or modifies protected joetoo repositories. Approval to investigate 1.5c.5b is granted here; approval of **specific executable implementation details** remains a separate decision after inspecting the working launcher.

**Codex:** is authorized now to inspect source/POC/installed metadata, compare security/lifecycle choices and return a short source-grounded recommendation. **Stop for maintainer approval before implementing the VNC executor or opening a connection.** Once the maintainer approves a concrete design and file envelope, implement only that bounded candidate with mocked/headless tests; do not expand into RDP or repair unrelated components. Do not invent a new tool or force `ssh_wrapper`/`swr` into a background tunnel without inspecting their actual contracts.

**Cloud reviewer:** may assess the source-grounded proposal, evidence and test outcomes and draft bounded follow-up tasking. No authority is implied to deploy, edit protected sources or perform native operations.

**Reporting discipline:** Keep historical Section 5 rows intact. Append one concise iteration row only for material new work. Reuse this HANDOFF, existing acceptance/review documents and source tests; **do not create another standalone planning, review or acceptance document without a maintainer request**.

## 4. Acceptance closure and active execution controls

### Step 1.5c.5a — accepted and closed

The maintainer's native X11 (`gmki91`) and Wayland (`q552u01`) results establish successful managed SFTP and local-underlay Dolphin launches, distinct registered KWin UUIDs, correct desktop/geometry and panel-over-under stacking, and independently observed remote `nuthuvia.brendler` browsing. The published implementation includes offline URI/worker-capability checks and optional **post-confirmation**, non-enforcing `getent ahosts` plus `nc` TCP advisories. Unresolvable targets retain their original SFTP URL in Dolphin, which presents its own error while local window management can still succeed. A successful TCP check is **not** SSH authentication or SFTP listing proof.

**Evidence correction:** The supplied `gmki91` **post-advisory positive** transcript explicitly reports `resolution=resolved`, `tcp=open`, `port=22`, with two Dolphin windows registered/placed, verified stacking and `2/2` layout completion. It must **not** remain described as pending. The maintainer also supplied positive Wayland `resolved/open/22` and negative `failed/skipped` results, plus negative X11 resolution evidence. These observations support acceptance without repeating that X11 test. Existing older acceptance/review documents may still contain the now-obsolete X11-pending phrase; this HANDOFF records the corrected maintainer evidence without requiring a new documentation task.

Native SFTP-specific active-desktop focus, new/changed host-key prompts, uncommon URI/profile precedence and some IPv6/nonstandard endpoints remain explicitly **NOT TESTED**, not presumed PASS. These optional edges do not block this bounded acceptance; preserve safe host-key verification and report any later incompatibility. The final `SFTP NSS/TCP advisory observation` debug-label refinement is a non-behavioral change reported by Codex; verify its commit/diff independently before treating it as published. Step 1.5c.5a is closed regardless of its historical task-record wording; no additional SFTP implementation is authorized here.

### Step 1.5c.5b — currently authorized

| Control | Active rule |
| --- | --- |
| Branch and dirty worktree | Stay on `task/joetoo-kwin-step1.5c5-remote-access`. Verify HEAD, published cleanup and any maintainer-owned local edits; do not reset, switch, overwrite or silently absorb them. |
| Initial permitted actions | Read current source, archive and the actual working KDE launcher; inspect nonsecret installed client/server metadata; propose exact security, argv, target, viewer identity and tunnel-lifetime contract. No real SSH/VNC/network probe. |
| Implementation gate | **Stop for explicit maintainer approval** of selected `-via` versus tunnel approach, endpoint grammar, security/lifecycle invariants, and exact editable file envelope. This HANDOFF alone does not authorize executable VNC changes. |
| Potential files after approval | Prefer existing `joetoo-kwin`, planner and launch functions, narrowly necessary helpers, configuration template and directly relevant tests. Broker, registry, resident and public D-Bus APIs are read-only unless separately approved. |
| Safety invariants | No exposed/direct raw VNC; forwarding only through verified authenticated SSH with loopback-only local endpoint; no auto-accepted host keys, credentials in argv/logs, adopted class/title-only windows, orphaned tunnel, secret copying or broadened permissions. |
| Plan/launch behavior | Keep `-c` offline. Reject unsupported/invalid whole plans before confirmation/provisioning. After approved launch, report viewer/window placement separately from SSH/VNC connection/authentication outcome; do not falsely claim session success. |
| Testing after implementation approval | Use mocked command, lifecycle, failure and cleanup cases; retain installed-header tests, Python/Node regressions, shell checks and focused diff review. Real X11/Wayland connection, authentication, listener-binding and teardown checks remain maintainer-operated. |
| Documentation/publication | Existing HANDOFF and task evidence only; no additional `.md` files by default. Do not stage/commit/push/PR/merge, deploy, administer hosts or modify `joetoo`/`joetoo-upstream`. |
| Stop/escalate | Missing actual working launcher, uncertain SSH identity or tunnel binding, unverified host-key policy, inability to identify the real viewer UUID, risky process/FD lifetime, ambiguous cleanup, unexpected API edits or changed baseline. |

**Next decision gate:** Codex reports the source-grounded TigerVNC POC/launcher comparison and a minimal proposed managed-launch contract. The maintainer either approves a specifically bounded implementation, requests a correction or explicitly defers VNC. **Do not begin 1.5c.5c RDP feasibility or 1.5d from this authorization.**

## 5. Agent-owned iteration record

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
| 10 | Codex (2026-10-30), Step 1.5c prerequisite inspection | Clean existing task branch at `31400fe0d2be05064b898cf520d06d6445e13839`, equal to main/cached origin/main and descended from supplied bf835c7; agent evidence and this Section 5 row only | Read current governing instructions, complete scope/handoff, planner and managed/public query interfaces, relevant SSH POCs and installed header helpers. No production edits or tests; whitespace check only | Explicit confirmation resolves draft language. Required intended-slot and active-placement preflight data are not exposed by existing public APIs; existing broker edits remain excluded. [Concrete bounded interface recommendation](step1.5c-interface-review.md). Maintainer must authorize necessary broker extension/slot-race policy; no fetch, native operations, staging or publication. |
| 11 | Codex (2026-10-30), Step 1.5c.1–1.5c.3 implementation | Existing approved task branch/baseline 31400fe; CLI/shared planner/bounded broker, new launch/session helpers, relevant tests and agent evidence; preexisting maintainer records preserved | 235 Python tests PASS without skips including installed-header integration; 3 Node test files PASS; syntax/ShellCheck logs and production/test whitespace checks. Full diff retains preexisting maintainer approval-line whitespace | Confirmed plan/preflight, atomic original-slot guard/query metadata, sequential managed launch with safe partial-failure continuation and conservative unresolved-state stopping, single-Bash nc/ssh_wrapper placeholders. See [candidate review](step1.5c-review.md). Maintainer/cloud review and native gates next; no fetch, live operations, staging, commit, push or deploy. |
| 12 | Codex (2026-10-31), focused native-feedback corrections | Clean approved task branch at 06bf97a7df1b68c3e9dc7fbfb0f40a328c3ea560; CLI/launch helper, focused tests and agent evidence only | 242 Python tests PASS without skips including installed-header integration; 3 JS files PASS; syntax, ShellCheck and whitespace PASS. See [correction review and inventory](step1.5c-corrections-review.md) | Added invocation-wide nonblocking runtime flock, child FD closure and truthful launch PID wording. Actual three-window orchestration regression passes existing safe partial-failure continuation; unresolved/ambiguous state stops. Native probe file/transcripts unavailable locally; maintainer reruns controlled PTY probe next. No broker changes, native operations or publication. |
| 13 | Codex (2026-10-31), Step 1.5c.4 first bounded iteration | Clean authorized branch/main/cached origin at e722bb21502b93e687e772a319db73a857c2e75c; CLI/planner/launcher, new resource helper, relevant tests and agent evidence | 254 Python tests PASS without skips including installed-header mixed-plan coverage; 3 JS files PASS; syntax/compile, ShellCheck, whitespace PASS. [Complete review/inventory](step1.5c4-review.md) | Added confirmed append-only KWin desktop capacity provisioning and Dolphin local argv dispatch with existing PID/UUID/slot safeguards. Deferred SFTP/VNC/underlay findings and native instructions provided. Dolphin executable help unavailable due Qt startup; no native acceptance claimed. Maintainer/cloud review next; no broker/resident/registry edits, live desktop operations, network connections or publication. |
| 14 | Codex (2026-10-31), native acceptance review and focused corrections | Clean approved task branch at 35d1b072b763df8126c602d9840c0ad243a9a656; narrow CLI/resource/launcher changes, directly affected tests and agent evidence | 258 Python tests PASS without skips including installed-header coverage; 3 JS files PASS; syntax/compile, ShellCheck and whitespace PASS. [Focused review/inventory](step1.5c4-corrections-review.md) | HOME-relative Dolphin paths; readable validator AAR; accurate adequate/missing capacity notice; added live mock Dolphin lock-lifetime regression. Maintainer-reported X11/Wayland acceptance recorded, including completed Wayland concurrency/cancellation PASS; no further native concurrency required. Layer proposal is separate and unimplemented. Maintainer reviews and checks revised paths/messages next; no native operations or publication. |
| 15 | Codex (2026-10-31), graphical-layer architectural gate (Outcome B) | Clean existing task branch at 584eb2e4d024215e325e00bc6b24596e2c6f3e5c; agent interface/native-plan evidence and this Section 5 row only | Unchanged baseline: 258 Python tests PASS, 3 Node files PASS; Bash syntax/Python compile, ShellCheck and whitespace PASS. Inspected planner, orchestration, ownership/query/placement contracts, resident observations and KWin scripting APIs | Genuine cohort stack/focus operation and observation are absent from existing contracts. [Bounded interface proposal](step1.5c4-layers-interface-review.md) and future native plan prepared. No executable or feature-test edits. Maintainer must approve broker/resident transaction/capability extensions and proposed focus/exposure details before implementation; no native operations or publication. |
| 16 | Codex (2026-10-31), approved graphical layers / desktop groups / XDG implementation | Existing task branch, HEAD `584eb2e4d024215e325e00bc6b24596e2c6f3e5c`; CLI, planner/launcher, bounded broker/resident extension, exposure helper, template, focused tests and agent evidence; earlier row 15 and gate evidence preserved | 280 Python tests PASS including installed-header integration; 4 Node test files PASS; Bash syntax, Python compilation, ShellCheck and whitespace checks PASS. No native operations | Application-independent layers/budgets, planned cascade/exposure warnings, first-appearance desktop groups, owned-UUID one-shot stack/focus with independent verification, and XDG discovery implemented. See [implementation and inventory](step1.5c4-layers-implementation.md), [complete diff](step1.5c4-layers-implementation.patch), and [native acceptance](step1.5c4-layers-acceptance.md). Maintainer reviews and runs X11 acceptance, then publishes the reviewed task increment for identical Wayland testing. Native stack/focus/exposure and remembered focus remain unverified; no staging/publication/deployment. |
| 17 | Codex (2026-11-01), initial-layout native-failure compatibility follow-up | Same task branch/HEAD `584eb2e4d024215e325e00bc6b24596e2c6f3e5c`; preserved dirty feature; resident/broker, two focused tests and agent evidence only | 282 Python PASS; focused broker 10 PASS; focused JS 19 PASS / all 4 Node files PASS; JS syntax, Python compilation and whitespace PASS. No native operations | Corrected raw Qt vs canonical broker UUID representation mismatch; retained mode checks with UUID/property/value/type diagnostics. Guarded disappearing completion observations. [Findings and focused diff](step1.5c4-initial-layout-compatibility.md). Native triggering predicate remains unproven from old aggregated error; maintainer reviews and repeats smallest native case with fresh slots. No publication. |
| 18 | Codex (2026-11-01), bounded delayed-focus correction | Same task branch/HEAD `584eb2e4d024215e325e00bc6b24596e2c6f3e5c`; preserved dirty implementation and maintainer instruction/architecture edits; CLI/planner/launcher, broker/resident, template and three focused tests | 287 Python PASS (no skips, installed-header integration retained); 36 focused JS cases / all 4 Node discovery files PASS; Bash/JS syntax, Python compilation, ShellCheck and whitespace PASS; no native operations | Replaced immediate-only focus decision with one activation and bounded event/timer observation; configurable 500/25 ms defaults explicitly conveyed through existing JSON, no new D-Bus signatures or lease extension. Stack/geometry/focus outcomes remain separate; handlers/timer cleaned and late callbacks inert. [Review, findings, incremental diff and exact native retest](step1.5c4-delayed-focus-review.md). Native causal timing remains unproven; maintainer reviews then repeats displayed-desktop two-Dolphin test on fresh slots. No publication/deployment. |
| 19 | Codex, Step 1.5c.4 acceptance closure and read-only merge audit | Clean task branch HEAD `a3c50fc54f95e25fd766b58037e773977f854f33`; only native acceptance record, existing c4 review and this Section 5 row edited | Inspected architecture/scope/source/tests and legacy D-Bus signatures; maintainer reports X11 delayed focus verified at 5 ms, Wayland immediate at 0 ms, 287 Python / 50 JS PASS. Documentation whitespace/link/scope checks only; no suites rerun or native operations | Implemented bounded candidate recommended ready for maintainer merge decision; no blocker identified. [Native closure and qualifications](step1.5c4-native-acceptance.md#graphical-layers-and-bounded-focus--acceptance-closure-at-a3c50fc); [12-contract audit and follow-ups](step1.5c4-review.md#merge-readiness-audit--a3c50fc). Wider transports, packaging and 1.5d remain separate. Maintainer reviews/decides publication and merge; no commit, publication or deployment authorized/performed. |
| 20 | Maintainer and ChatGPT (2026-11-01), Step 1.5c.5 scope and task activation | Planning baseline `099096e33fe568579b219ffced4131f211af2a3f`; proposed branch `task/joetoo-kwin-step1.5c5-remote-access`; this new handoff draft only | Maintainer reports signed commit/push of architecture, README and detailed Step 1.5c.5 scope; ChatGPT inspected those files at the supplied SHA. No 1.5c.5 source or native tests performed. | Maintainer authorization recorded [20261101-16:37:41]; after maintainer branch creation, local agent starts 1.5c.5a source/grammar investigation; executable SFTP dispatch awaits explicit grammar/security decision. 1.5c.5b/c and 1.5d are separately gated. |
| 21 | Codex (2026-11-01), 1.5c.5a SFTP contract investigation | Clean branch `task/joetoo-kwin-step1.5c5-remote-access`; HEAD/local main `5dd60d397d00539ddfc973455e178dfefda80267`, containing planning baseline `099096e`; new contract report and this Section 5 row only | Inspected accepted launcher/planner/broker/resident/tests, installed Dolphin/KIO/libssh package/plugin metadata, Qt plugin-path query and primary Dolphin/KIO/libssh sources. No implementation suites, GUI or transport tests. Documentation link/whitespace/scope checks PASS | [URL-only SFTP recommendation and decision gate](step1.5c5a-dolphin-sftp-contract.md): approve grammar/encoding, native KIO trust and config precedence, redaction/stdin validation, unverified remote outcomes and capability discovery before executable work. KIO changed-key override differs from strict OpenSSH; no automatic trust/config changes proposed. Maintainer/cloud review next; no source edits, connections, publication or advancement to b/c/d. |
| 22 | Codex (2026-11-01), approved 1.5c.5a Dolphin SFTP candidate | Same branch/HEAD `5dd60d397d00539ddfc973455e178dfefda80267`; prior proposal/row 21 preserved. CLI/planner/launcher/template, two new offline helpers, focused tests/native fixture and task evidence | 301 Python PASS without skips including installed-header integration; 14 focused SFTP cases rerun after final diagnostic refinement; 4 Node files PASS; Bash syntax, Python compile, ShellCheck, whitespace/link/scope checks PASS. Exact 26.04.3 worker archive inspected; local offline worker discovery confirmed. No native/transport testing | [Candidate review, complete diff and native commands](step1.5c5a-review.md): approved URL validation/stdin redaction, no unconditional qtpaths dependency, existing managed PID/UUID machinery, independent unverified remote outcomes. Maintainer manual gmki91 browsing feasibility recorded separately; managed SFTP X11/Wayland acceptance remains next. No broker/registry/resident edits, SSH config changes, commit/publication or advancement to b/c/d. |
| 23 | Codex (2026-11-01), bounded SFTP NSS/nc advisory and documentation reconciliation | Existing task branch HEAD `98e366899a611e000f246b74abb4906f7238db8b`; CLI/planner/launcher/template, new advisory helper, focused tests, five authorized Markdown documents and complete correction patch. Maintainer architecture/scope changes and untracked native_joe fixture preserved/excluded | 312 Python PASS without skips including installed-header coverage; 4 Node discovery files PASS; Bash syntax, Python compilation, ShellCheck and scoped diff checks PASS; full-tree EOF whitespace findings in concurrent maintainer architecture/scope edits left untouched. Resolver/nc calls mocked; no native/network operations | Post-confirmation optional two-stage advisory with configurable enable/timeout/port, numeric NSS bypass and qualified uncertainty; original Dolphin URI always launched. Published base native acceptance and negative X11 destination recorded separately from pending correction-native results. Maintainer reviews [correction and native checklist](step1.5c5a-review.md); no publication or b/c/d advancement. |
| 24 | Codex, Step 1.5c.5a final label/evidence cleanup | Clean starting task branch HEAD `b8120f7c9aad608e26b5c147561a5eee5756a8e9`; only launch-functions debug label and the five requested Markdown files changed | 25 focused SFTP tests PASS; 312 full Python PASS without skips including installed-header coverage; 4 Node discovery files PASS; Bash syntax, Python compilation, ShellCheck, scoped diff checks PASS. Historical rows preserved; no native/network tests | Published advisory status reconciled; maintainer Wayland positive resolved/open/22, desktop-4 win-003/win-004 placement/stack and 2/2 browsing evidence recorded, alongside negative failed/skipped and retained X11 evidence. Post-advisory X11 TCP-open remains pending. Maintainer reviews cleanup and decides acceptance/closure. No commit, publication, merge or subsequent increment. |
| 25 | Codex, Step 1.5c.5b source-grounded contract investigation | Initially clean existing task branch HEAD `9dbaabd6a55e321ba9df73569f4f23aa0d6cc2e1`; only this iteration row added | Read actual local KDE VNC entries, archived POC, installed TigerVNC 1.16.2/FLTK 1.3.8 exact distfile source, nonsecret SSH options, launch/broker/resident/tests/template and governing skills. No implementation suites or native/network operations; scoped whitespace check PASS | Local entries confirm -via SSH + localhost:2; source default uses shell/system, ssh -f and sleep 20 without explicit loopback binding or owned teardown. Recommend approving an explicitly owned SSH tunnel contract rather than copying defaults. Same-process/class authentication window precedes real desktop and is not proven excluded by normalWindow; native identity evidence or separately approved minimal remediation required before safe executor work. Full proposal delivered in conversation. Maintainer selects transport/grammar/authentication and identity-validation next step; no executable changes or b/c/d advancement. |

| 26 | Codex, maintainer-approved native identity investigation preparation | Same task branch HEAD `9dbaabd6a55e321ba9df73569f4f23aa0d6cc2e1`; preserve uncommitted row 25, append this row only | Inspected existing correlation probe, Begin/SetPid/PollCorrelation, ListObserved, resident normalWindow filtering and installed X11/Wayland KWin D-Bus XML for debug console/window queries. Scoped whitespace PASS; no GUI/network or implementation tests | Maintainer provisionally approves ssh:// user/host/port with display/N or port/P, dedicated supervised foreground SSH and compatible noninteractive authentication; executable implementation remains gated. Native-only instructions delivered for both hosts: capture auth/viewer UUID/PID/class/type/normalWindow, observation lifecycle and 15-second diagnostic correlation; no SubmitManagedLaunch or adoption. Cached/no-dialog case is a limitation. Maintainer runs working launcher observation and returns evidence; Codex then proposes final viewer-registration strategy, supervisor contract and exact file envelope for approval. |

| 27 | Codex (2026-11-02), native identity findings and final contract recommendation | Same HEAD `9dbaabd6a55e321ba9df73569f4f23aa0d6cc2e1`; prior dirty rows 25–26 preserved; this record only | Maintainer reports X11/x402 and Wayland/x402,yorsqui auth-to-desktop distinct UUIDs with same PID/class, both observed; X11 auth normalWindow=true and not dialog/modal/transient. Inspected exact TigerVNC DesktopWindow::show/ServerInit and broker correlation/placement source; checked KDE Plasma/6.7 getClient(XID) source. No native observations repeated or executable changes | Current unique-PID/0.5-second correlation and class-driven TakeLaunch can select/move auth; extending 15 seconds alone is unsafe. Propose narrow gated viewer transaction with broker-owned stock-TigerVNC desktop ClientMessage observation, KWin XID-to-UUID resolution plus existing PID/source/new-window checks, deferred placement, bounded configurable readiness and owned tunnel cleanup. Stock signal is application-role evidence, not a credential; runtime capability/transport must fail closed. No reliable cancellation-versus-connection-failure classification from generic pre-ready exit alone. Exact file/interface envelope and alternatives delivered in conversation; maintainer must approve before implementation. |

| 28 | Codex (2026-11-02), authorized 1.5c.5b implementation candidate | Existing branch HEAD `9dbaabd6a55e321ba9df73569f4f23aa0d6cc2e1`; dirty rows 25–27 preserved. CLI/planner/launcher/template, broker/resident, three new VNC helpers, four new test files and planner test fixture; this iteration row only in documentation | 350 Python PASS without skips including installed-header regressions; 38 focused VNC cases PASS; 5 Node discovery files PASS. Bash syntax, Python compilation, ShellCheck, tracked/new-file whitespace PASS. Real libxcb exercised against isolated local-IPC X11 protocol peer; KWin XID lookup tested in resident VM with source-confirmed getClient. No live X server/KWin, DNS/TCP/SSH/VNC or GUI tests | Deferred desktop-role registration keeps auth windows unregistered/unplaced; exact PID/new UUID/source/lifecycle guards, bounded observer child and expiry, UUID-only placement, dedicated foreground SSH/private master/loopback forwarding, owned viewer lifetime, cancellation and cleanup-uncertainty stopping. Cleanup failure regression exposed and corrected skipped second-child teardown. Maintainer reviews full diff then stages identical candidate for X11/Wayland event-to-UUID, long auth/cancel/timeout, listener exposure, BatchMode compatibility and teardown acceptance. Existing installer is unchanged: new VNC Python helpers must be staged alongside broker manually for native testing. No architecture/scope/registry/SSH-config changes, commit, deployment, publication or RDP. |

| 29 | Codex (2026-11-02), first native viewer-submit failure investigation | Same branch/HEAD; prior candidate and rows 25–28 preserved. Narrow diagnostics in VNC launch/identity helpers, two regression test files and this row only | Maintainer gmki91: 350 Python / 53 JS PASS; dry run and viewer_protocol=1 synchronized inventory PASS; actual -o failed at SubmitManagedViewerLaunch with no reported viewer/SSH PID or registration IDs. ShellCheck could not load libHSaeson shared library (tool/environment failure, not script diagnostics). Correction: 352 Python PASS, 40 focused VNC PASS, 5 Node files PASS; Bash syntax, Python compilation, whitespace PASS; ShellCheck remains blocked | Generic helper error discarded the D-Bus reason. Now retain only recognized local rejection detail/error namespace, redact arbitrary stderr, and reject absent broker DISPLAY explicitly before spawning observer. Installed OpenRC allowlist inspected: DBUS_SESSION_BUS_ADDRESS/JOETOO_KWIND_EXEC only; missing broker X11 context is a hypothesis, not established root cause (running process environment unavailable in agent view). Maintainer checks broker DISPLAY/XAUTHORITY and returns that result or newly qualified error. No live GUI/network tests, installed-file/config changes, service operations or publication by Codex. |

| 30 | Codex (2026-11-02), X11 evidence and final integration corrections | Same task branch HEAD `9dbaabd6a55e321ba9df73569f4f23aa0d6cc2e1`; all candidate work, rows 25–29 and preexisting user-init.d edit preserved. Only existing OpenRC helper, existing OpenRC/VNC tests, explanatory VNC argv comment and this row changed | 357 Python PASS without skips (18 OpenRC setup, 43 VNC focused); 5 Node files PASS; syntax/compilation/whitespace PASS. Shell helpers/installer ShellCheck PASS; strict CLI emits 6 cross-file-global SC2034/SC2154 warnings, excluded run PASS. Maintainer X11: win-001 UUID eacf57ad-d571-4155-bc73-d52cc9fcd1cf and Dolphin win-002 on desktop 10, 2/2 placement/stack PASS and visual remote use; SSH 3836204 bound 127.0.0.1:48329, viewer 3836207/SSH/listener disappeared on viewer close | Existing configuration helper now preserves DISPLAY/XAUTHORITY names alongside other entries, never hardcodes values or requires XAUTHORITY set; fresh/update/check/idempotence verified through disposable installer path. Empty -via intentionally disables TigerVNC's own tunnel; exact empty argv and one owned tunnel/viewer startup tested. Added readiness-timeout cleanup and both control-path/private-directory handoff-cleanup orders; startup/cancel cleanup attempts both children, unrelated processes/live enrolled viewers protected. X11 delayed-auth/cancel/timeout/unreachable and Wayland positive/event delivery still maintainer-native gates; remote listener exposure remains separate. No production SSH/VNC config, service, protected-repository edits, commits/publication or acceptance declaration. |

| 31 | Codex (2026-11-02), final installer integration correction | Clean starting task branch HEAD `ee534cd7744d71fd7623428c76f6ac1f26d0215f`; only existing installer, existing OpenRC/registry installer tests and this iteration row changed | 23 focused installer tests PASS; 362 full Python PASS without skips; 5 Node discovery files PASS; installer sh syntax/ShellCheck, Python test compilation and diff whitespace PASS. First regression run found an old test pinning exactly six mappings; updated it to retain registry coverage while permitting the added dependencies. All installer execution used temporary HOME and mocked OpenRC | Existing install/update/check/backup and destination-safety paths now include all three VNC Python helpers under user .local/libexec at 0644; missing/outdated detection, six-file upgrade, backup content/modes, symlink refusal, running-service update refusal and content-idempotence covered. Maintainer reports X11 cases 1–4 completed and Wayland/XWayland actual desktop registration after delayed authentication, auth-window exclusion, independent Dolphin placement, verified stacking and 2/2 success after manual module staging. New installer removes that manual step; maintainer reviews and verifies ordinary update/check reports nine current files. No launch behavior changes, new configuration utility/document, production install/service/network operations or publication by Codex; milestone acceptance remains maintainer-controlled. |
| 32 | Codex (2026-11-02), integrated installer archive and content deduplication | Same task branch HEAD `ee534cd7744d71fd7623428c76f6ac1f26d0215f`; preserved the pending nine-file correction and row 31; only existing installer, its two existing test files and this row changed | 33 focused installer tests and 372 full Python tests PASS without skips; 5 Node discovery files PASS; installer sh syntax/ShellCheck, embedded Python/test compilation and diff whitespace PASS. Mutating installer tests used temporary HOME and mocked OpenRC; actual installed legacy files were inspected read-only | Changed components are copied before installation into `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/archive/COMPONENT/SHA256/ORIGINAL_NAME`, with first-archive provenance JSON and preserved modes/timestamps. Unchanged bytes create no backup; existing versions require byte equality; symlinks, unsafe archive paths, corrupt versions and copy failures abort without replacing active components. All nine components covered, including independent same-basename namespaces and VNC modules at 0644. New existing-installer `--preview-legacy-backups` reports content groups, hashes and original paths without modifying history: current preview found 171 legacy files / 50 component-local versions (registry 21 / 2). Legacy migration is NOT performed: maintainer reviews preview, then separately authorizes copying/verifying unique versions with a full original-path manifest before any consolidation/deletion. Installation failure retains archived previous contents; no automatic rollback or retention policy added. Next actor: maintainer reviews combined uncommitted diff and verifies installer update/check; native launch behavior unchanged; no production install/service/network operations, publication or milestone acceptance by Codex. |
| 33 | Codex (2026-11-02), standalone legacy migration Gates A/B candidate | Same task branch HEAD `ee534cd7744d71fd7623428c76f6ac1f26d0215f`; all pending installer/tests and rows 25–32 preserved. Added only separate migration utility/test file and this row; no installer/runtime changes | 23 migration tests and 405 full Python tests PASS without skips; 5 Node discovery files PASS; Python compilation, existing installer sh syntax/ShellCheck and diff whitespace PASS. Real read-only Gate A re-inventoried 171 legacy paths / 50 component-local versions / 121 duplicate copies, exactly matching supplied six-component counts: 50 payloads new, 0 reused, 4 preexisting VNC archive files. Repeated no-atime inventory confirmed all original/installed/archive file snapshots unchanged | Gate B implemented/tested ONLY in disposable HOME: representative 4-path/3-version fixture created 2 payloads, reused 1; component archive files 6→10, all originals/installed files unchanged, full manifest verified and retry created 0 payloads. Legacy metadata/filenames/embedded timestamps live in durable resumable `archive/migrations/legacy-INVENTORY_ID.json`, separate from strict installer provenance; copy uses atomic no-replace publication, stale/source checks and failure-safe staging. Utility reuses trusted installer archive helper definitions without running installer entry points; requires Linux no-atime/no-replace facilities. Real Gate B NOT executed; actual archive still 4 files. Maintainer reports deployed nine-file installer Current/restart/D-Bus PASS and 382 Python / 53 JS PASS; not Codex native testing. Next: maintainer reviews candidate and Gate A JSON, then performs separately reviewed copy/verify on gmki91; no other hosts, deletion/Gate C, deployment or publication by Codex. |
| 34 | Codex (2026-11-03), 1.5c.5c server-first RDP feasibility | Clean approved branch `task/joetoo-kwin-step1.5c5c-rdp-feasibility`, HEAD `76dba5b968f38d2c80ff178c932046c6023ae664`; merge base/local main/origin-main `d8aad51e9ea894c49c78bdb7a8a5bea8b83df550` (merged PR 27). Only Section 5 of this HANDOFF edited | Read current architecture/scope, installed package metadata/manpages, exact cached KRDC/KRDP/FreeRDP/Remmina release sources, selected profile ancestry and primary upstream docs. Remmina 1.4.43 installation confirmed. No clients/services launched, credentials read, remote sessions opened or regressions rerun; documentation whitespace/scope/link checks only | Findings below are inspected/documented capabilities, not native RDP acceptance. Recommend Ubuntu GNOME Remote Login pilot, then KRDC versus SDL3 FreeRDP comparison; retain accepted TigerVNC-over-SSH. Maintainer chooses pilot host/session/trust policy and separately authorizes native tests before any executable RDP contract. No installation, configuration, protected-repository edits or publication. |
| 35 | Codex (2026-11-03), focused RDP PKI/Windows/Shadow follow-up | Preserved pending iteration 34 and findings on unchanged `76dba5b`; only agent-owned Section 5 updated | Inspected exact FreeRDP 3.32.1 Shadow/crypto source, installed build flags and PAM/X11 linkage, plus primary GNOME/xrdp/Microsoft documentation. No keys, credentials, clients or services accessed; no native RDP result inferred | Existing private CA workflow is maintainer-reported. Added certificate integration, Windows login versus attended sharing, SAM-NLA versus TLS/PAM and Shadow X11 limits. `raspiubuntu401` test remains in progress elsewhere; maintainer reviews findings and supplies pilot outcomes before an implementation contract. |
| 36 | Codex (2026-11-04), Ubuntu GNOME native evidence review | Clean approved RDP feasibility branch, HEAD `3eb587bda2a4d50ab6985df728a7db012b8e509f`; reviewed maintainer report and all 17 supporting screenshots read-only; updated only Section 5 | Recorded six working mode/client combinations, Remmina reconnect persistence, separate service credentials/certificates, session-state limitations and qualified TLS observations. Screenshot 01 duplicates KRDC screenshot 04 despite its FreeRDP label. Evidence files preserved byte-for-byte; documentation checks only, no native operations or tests | Recommend GNOME Remote Login as demonstrated Ubuntu baseline and KRDC as provisional managed-client candidate; retain xfreerdp diagnostic and Remmina working alternatives. PKI, fresh-boot login, Windows, Wayland client and positive KWin identity evidence remain outstanding; implementation still requires maintainer decision. |
| 37 | Codex (2026-11-04), SDL lifecycle diagnostic, temporary evidence transport and maintainer runner | Approved RDP feasibility branch at `6922be6d9f17621e5be41b92284932ab01b623b7`. Preserved four untracked diagnostic/receiver candidates; added `tools/joetoo-rdp-diagnostic-run.sh`, extended existing receiver tests, and updated only this agent-owned record | Prior transport iteration: 424 Python / 91 JavaScript PASS. Current: 58 focused Python (42 receiver + 16 wrapper), 440 full Python and 91 JavaScript PASS; no failures/skips. Bash syntax, ShellCheck, Python compilation and whitespace checks PASS. Wrapper execution used disposable fake header/KWin/receiver/proof tools only | Observation-only candidate, not RDP enrollment. Persisted readiness precedes proof; bounded export, receipts and sender confirmation remain separate from lifecycle coverage. Partial evidence retained; no production changes or native sessions. Maintainer reviews candidate and decides when to run the focused X11 diagnostic; native execution/publication remain gated. |
| 38 | Codex (2026-11-05), native capture analysis and authorized X11 activity-property experiment | Same approved branch/HEAD; preserved all existing edits. Added only `tools/joetoo-rdp-x11-use.py`, its isolated KWin linkage companion `.js`, and `tests/test_rdp_x11_use.py`/`.js`, plus this row | Maintainer's accessible X11 capture independently verified: 175 transport records, intact capture, both temporary and persistent marked windows activated and shared recorded birth attributes. New tests: 26 Python / 6 JS focused PASS, including real libxcb against an isolated socketpair peer; full repeat 466 Python under umask 077 / 97 JS PASS without skips. An earlier full run had one existing wrapper-fixture assertion failure; isolated and full reruns passed, cause unestablished. Python/JS syntax and whitespace PASS | Source-inspected SDL 3.4.18 updates per-window `_NET_WM_USER_TIME` after input presses; companion observes property changes only, never key/button events or text. Establish baseline, continue waiting through absent/unchanged values, latch once per candidate, then remove its property watch. Private bounded evidence, pinned KWin sender, exact live getClient XID/UUID links, generation/late-event guards and explicit unlinked/discovery-gap counts; no automatic role conclusion. Candidate native run is maintainer-operated and pending. Registration and placement remain separate proposed decisions; no production enrollment/control or protected-tool changes. Native Wayland requires separate follow-up because its internal lastUsageSerial is not exposed by the inspected scripting API. |
| 39 | Codex (2026-11-05), authorized single-command X11 diagnostic integration | Same approved branch/HEAD; changed the existing candidate runner, X11 observer, their two Python test files, and this row only; prior candidate and maintainer edits preserved | 66 receiver/runner and 30 X11 focused Python PASS; 478 full Python under umask 077 and 97 JavaScript PASS, no failures/skips. Bash syntax, ShellCheck, Python compilation and tracked/new-file whitespace PASS. Combined execution used disposable fake header/KWin/proof/X11 services only | Runner gates proof on main persisted readiness plus live, pinned-owner X11 status after a confirmed linker round trip. Both evidence sets share one private diagnostic archive. Finish/owned-child cleanup/UUID-linker unload and independent verification are integrated; X11 failure still drains primary export and cannot yield combined success. Native Wayland defaults to X11 companion disabled, explicitly qualified. Unchanged proof still raises Debug Console: no screenshots required; skip screenshot-evidence claims and distinguish logout from manual viewer close. New private Status inspection does not renew linker liveness. Mock startup allowance is three seconds for combined fixtures; production startup default remains fifteen seconds. Maintainer runs/reviews the combined X11 capture next. No native execution, production changes, publication or automatic enrollment by Codex. |
| 40 | Codex (2026-11-05), authorized native-Wayland identity contract investigation | Same approved branch/HEAD; preserved maintainer organization and revised twelve proof phases. Only two focused cases added to the existing diagnostic JS tests, plus this agent-owned record and findings below; no diagnostic runtime or production changes | 92 existing Python ownership/observation/viewer regressions PASS; 44 focused JS and 99 full JS PASS, no skips/failures. Two isolated in-memory broker reproductions: an unmarked credential alone can register under the generic evaluator; credential plus marked viewer is ambiguous. Persistent Wayland archive inspected in place, no native sessions or raw evidence copies | Native marker/PID/new-UUID contract is feasible for a verified native backend and bounded single-desktop profile; generic PID selector and fifteen-second lease cannot be reused unchanged. No interaction observer, new service or resident instrumentation required for this investigation. Proposed SDL-specific predicate must reject role ambiguity and retain complete lifecycle/source guards; registration remains separate from post-login placement. Negative/retry/reconnect native behavior and security/production contracts remain gated. See findings and artifact accounting below; maintainer reviews and operates the bounded native check. |
| 41 | Codex (2026-11-05), partial native-Wayland follow-up evidence review | Verified new maintainer-staged baseline `272a81ded4527c6badc4775afdab451ad9c99b18`, initially clean tree. Read archives in memory; only this agent-owned row changed | Maintainer reports 478 Python / 99 JS PASS. Offline schema, sequence, framing, payload hash, receipt and sender-confirmation checks PASS for `joetoo-rdp-diagnostic.NCakxMYv.tbz2`: 33 records, intact delivery but capture_intact=false solely because unresolved_window_count=2; no overflow/callback/cleanup errors. Credential and viewer are both normal windows, PID 2027485; viewer UUID `419e5b24-7601-41a4-a1f4-7c9512a1884c` has exact marker at birth while credential UUID `46d324bf-57d4-40a1-abb7-416f703a9e8d` does not | Positive exported lifecycle evidence, not complete uniqueness proof: two unclassified windows were filtered from export, so their PID/UUID/scope cannot be attributed from this archive. Matching new proof `joetoo-rdp-stage-a.mceCcUHo.tbz2` has not been made accessible here; supplied `/tmp/joetoo-rdp-stage-a.uXBwj934.tbz2` is byte-identical to the old November 4 archive (PID 1763685), not this run. Obtain matching proof before deciding on diagnostic changes or another native run. Retain new diagnostic: currently verified only at `/tmp/joetoo-rdp-diagnostic.NCakxMYv.tbz2`, SHA-256 `ad5d87507b06d3620b16e60ea14487f55f7ea2b3b8d562a883a68945cf8b6439`; private persistent copy not yet found. No extraction, relocation, new temporary artifact, runtime changes, native execution or publication. |
| 42 | Codex (2026-11-05), corrected Wayland proof correlation | Same `272a81d` baseline; only this agent-owned row added. Corrected proof read in memory at `/tmp/joetoo-rdp-stage-a.mceCcUHo.tbz2`, SHA-256 `2154bc110be0a3e2c5e37cf2b926ae391a036d9b22e4849fde544e9840aac9ad` | Proof matches diagnostic PID 2027485/token; native wayland, 609 synchronized samples from one source, marked viewer added at broker event 175 and removed 176 with unchanged UUID/marker. Credential events 66/174 have no marker. Maintainer recorded usable GNOME desktop and logout, skipping manual viewer close; client exit 2 remains independent. Full retained broker lifecycle has five baseline windows and four additions/removals: the two SDL windows and two unclassified normal windows with PID -1, empty class/desktop identity and no marker | Two unclassified UUIDs account for the broad diagnostic coverage concern: one has Debug Console caption evidence; the unnamed small window is not further attributed. Neither supplied the PID/class/marker evidence required by the proposed contract. Preserve capture_intact=false; do not retroactively relabel the global diagnostic PASS. This corroborates the positive native-Wayland viewer distinction without another positive run or a new input observer; cancellation/failure/retry/ambiguity acceptance remains pending. Both corrected proof and diagnostic tarballs currently exist only in verified `/tmp` locations, not in the known persistent `rdp-evidence` directory: retain privately. No new temporary artifact, extraction, relocation, runtime changes or native execution by Codex. |
| 43 | Codex (2026-11-05), eight additional maintainer proof archives reviewed read-only | Preserved maintainer eighteen-phase/outcome edits in `tools/rdp_identity-security_proof.sh`; only this agent-owned row added. Archives read in memory, no extraction or native execution | All eight backend.txt files explicitly report x11; all filtered proof samples synchronized to one source per run, observer exit 0 and empty observation error logs. `l0TjJ6r5` cancellation, `fvriEFLc` bad NLA password and `o5Ejba3p` connection failure each retain two new unmarked UUIDs and no marked target lifecycle. Client logs respectively report CONNECT_CANCELLED, LOGON_FAILURE and CONNECT_FAILED. `jNG7fbvJ` is the aborted/mistargeted failure run. `bPd7yxLi` and `UlffFIYm` retain distinct old/new PID/UUID histories; old viewer survives the first and is removed during the second. Successful runs again contain two successive same-PID exact-marker UUIDs. `MiECZCsg` / `NLq2gMGj` are separate launches (PIDs 590564 / 596213), each with new UUIDs | Useful X11 failure/concurrency/fresh-launch evidence, not native-Wayland negative acceptance, in-process reconnect, remote session-ID continuity or production registration tests. No retry was offered after bad NLA credentials; quicker second login alone does not establish remote session continuity. No additional input observer is justified by these results; the existing native-Wayland negative checks remain bounded as below, with no need to repeat its successful positive case. Retain all eight `/tmp/joetoo-rdp-stage-a.{l0TjJ6r5,fvriEFLc,o5Ejba3p,jNG7fbvJ,bPd7yxLi,UlffFIYm,MiECZCsg,NLq2gMGj}.tbz2` archives privately; matching names absent from known persistent rdp-evidence directory. Mistargeted archive needs maintainer disposition, not automatic deletion. No new scratch artifacts, runtime changes, headless tests, relocation or publication this iteration. |
| 44 | Codex (2026-11-05), five q552u01 native-Wayland follow-up proofs | Clean maintainer baseline `cb84248d1b523717389595d84f426f42f578107b` on existing task branch. Only this agent-owned row added; archives inspected in memory | All five backend.txt files explicitly report wayland. All 2,714 samples synchronized to one source; observer exits 0, error logs empty, managed inventories unchanged. `GxoO58Q5`: cancel, one unmarked credential UUID, CONNECT_CANCELLED. `BRKiefxH`: failed NLA, one unmarked credential UUID, LOGON_FAILURE, no retry offered. `txX5XzJf`: CONNECT_FAILED, no target-PID window in retained observations/lifecycle. `kaZuBRs6`: PID 2402545, unmarked credential events 521/588 and exact-marker viewer `eaf88abb-9f0a-4b4c-9f5d-c0b712957b20` events 767/769; all 523 current viewer samples retain marker. Unrelated PID 2401889 / UUID d2e6b937-29d9-4b6a-9106-5c3e0eccb651 remains present before/after. `4DytUoCv`: fresh PID 2411692, unmarked credential 805/856; exact-marker viewer `5c6fbcd4-7ac6-4677-9516-f2a8cf6f620a` 857/858, all 236 viewer samples retain marker. Maintainer reports 478 Python / 99 JS PASS | Requested cancellation, failed-NLA, connection-failure and unrelated-viewer native checks now support the bounded single-desktop marker/PID/new-UUID contract without a separate interaction observer. No marked temporary predecessor appeared in these Wayland histories. Test E is a fresh client launch; remote-session resumption remains inferred, in-process reconnect untested and UUID replacement unsupported. Direct proof runs do not establish standalone diagnostic transport completeness or production enrollment acceptance. Next actor: maintainer reviews feasibility and separately authorizes a focused SDL registration-only implementation; generic PID-only launch selection remains unsuitable. Retain private `/tmp/joetoo-rdp-stage-a.{GxoO58Q5,BRKiefxH,txX5XzJf,kaZuBRs6,4DytUoCv}.tbz2`; matching names absent from known persistent archive directory. No scratch artifacts, runtime edits, headless reruns, native execution, relocation or publication by Codex. |




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
| C13 | ChatGPT (2026-10-30), Step 1.5c broker interface review | Inspected `joetoo-kwind`, managed-window summaries, registry records, `SubmitManagedLaunch` and broker transaction reporting. No source edits. | Verified that original desktop/slot existed in launch recipes but was not exposed in public managed summaries; transaction state reporting was insufficient for planned preflight. Read-only source inspection; no tests. | Recommended a narrowly bounded broker interface extension, subject to maintainer approval. |
| C14 | ChatGPT (2026-10-30), desktop/slot architecture reconciliation | Iterated the distinction among KWin virtual desktop, joetoo logical launch slot, mission, initial geometry and observed geometry; drafted revised Codex guidance. | Used actual planner/broker source and maintainer decisions. Established that slot is the sequence number of a configured entry, not its screen position; manually moving a window does not change its original logical association. | Maintainer approved the persistent logical association and broker-side duplicate-launch guard; policy published in `Step1.5c_clarification_of_desktop_slot_duplicate_launch_policy`. |
| C15 | ChatGPT (2026-10-31), architecture consolidation | Reviewed §§4–7, 9, 11 and 12 of `ARCHITECTURE.md`; prepared and published `ARCHITECTURE-step1.5-clarifications.patch` on `main` in commit `f414f93`. | Verified patch hunks reconstruct the proposed architecture changes; the patch was not applied to `ARCHITECTURE.md`. No native tests. | Maintainer to review and apply separately after Step 1.5c integration. |
| C16 | ChatGPT (2026-10-30), X11 validation review and Wayland test planning | Reviewed maintainer's `gmki91` X11 native launch logs, registry behavior and screenshots; prepared a staged `q552u01` Wayland test battery. | Maintainer demonstrated layouts from two through four windows, an 11/11 run, repeated SSH hosts, unreachable placeholders, duplicate protection and original Bash PID continuity (`2117716`). ChatGPT did not execute tests. | Classified X11 functionality as substantially passing; recommended controlled Wayland testing with the same candidate revision. |
| C17 | ChatGPT (2026-10-31), Wayland native acceptance assessment | Reviewed `q552u01` Wayland transcripts for two-, three-, four- and six-window launches, desktop/slot protection, SSH lifecycle, unavailable targets and registry observations. | Maintainer reported 235 Python / 14 JS tests passing, 17/17 initial placements, later additional launches, original Bash PID continuity (`3231813`), and duplicate rejection after movement of `win-018`. No ChatGPT native tests. | Recommended focusing remaining validation on concurrency and lifecycle; deferred transport telemetry, slot release and durable broker recovery. |
| C18 | ChatGPT (2026-10-31), concurrency diagnosis and focused correction tasking | Inspected `open_plan()` and launcher helpers; proposed a pseudo-terminal concurrency test and reviewed maintainer's initial probe transcripts. Drafted the three-objective correction task for Codex. | Initial maintainer Wayland probe showed A and B both reached confirmation, demonstrating missing pre-confirmation whole-run serialization. Both were cancelled without launch. | Recommended invocation-wide locking, corrected launch-PID messaging and deterministic partial-failure regression; Codex implemented these in Iteration 12. |
| C19 | ChatGPT (2026-10-31), corrected implementation and native evidence review | Inspected revised launcher, FD9 closure, `flock` acquisition, orchestration tests and Codex correction review; evaluated maintainer's corrected X11/Wayland results. | Maintainer Wayland: 242 Python / 14 JS PASS, pseudo-terminal concurrency PASS, lock release after cancellation PASS and lock release with live Konsole PASS. Maintainer X11: corrected concurrency probe PASS at `9b5fe097`; real Konsole successfully registered/placed. No ChatGPT native executions. | Recommended final X11 live-Konsole lock-release check, then complete branch/PR review and maintainer merge decision. |
| C20 | ChatGPT (2026-10-31), final Step 1.5c PR-readiness review | Compared task branch `9b5fe097` against published `main` `f414f93`; reviewed 26 changed paths, authorization history, existing handoff rows and remaining native evidence. | GitHub comparison: branch 3 commits ahead, 1 behind; `main` contains an unapplied architecture patch not present on the task branch. No active PR found. No tests or host operations executed by ChatGPT. | Candidate recommended for PR review after final X11 lock check and documentation reconciliation. Maintainer retains PR creation, acceptance and merge authority. |
| C21 | ChatGPT (2026-10-31), Step 1.5c.4 scope review | Reviewed architecture, planner, launcher, broker and resident; refined Dolphin/SFTP, TigerVNC/SSH, underlay and security requirements. No edits. | Confirmed missing virtual-desktop provisioning and unsupported graphical dispatch; no native tests. | Proposed bounded increments, desktop provisioning after confirmation, and separate 1.5d regression. Maintainer to approve implementation scope and permissions. |
| C22 | ChatGPT (2026-11-01), graphical-layer acceptance synthesis and 1.5c.4 closure assistance | Reviewed maintainer-supplied X11/Wayland native launch, UUID/stack/focus, manual override, duplicate-slot and SSH-lifecycle transcripts and screenshots; drafted the bounded delayed-focus Codex task, remaining acceptance commands, and the documentation/12-contract merge-readiness audit instruction; reviewed Codex closure output and drafted this maintainer-facing closure reconciliation. No repository edits or native operations performed by ChatGPT. | Maintainer native X11 delayed focus verified at 5 ms; Wayland displayed-desktop focus verified immediately; Wayland `win-022` confirmed present after SSH lifecycle test, reported 287 Python / 50 JS tests passing; Codex found no blocker in source audit and edited only acceptance/review/HANDOFF Section 5. Timing examples do not establish backend guarantees; rare disruption paths remain headless-covered. | Maintainer **accepts** the delivered bounded Step 1.5c.4 implementation and **closes the task**. Maintainer will merge the reviewed branch; afterward maintainer and cloud AI will separately draft a **new Step 1.5d HANDOFF update**. No 1.5d work or merge is performed or authorized by this retrospective entry. |
| C23 | ChatGPT (2026-11-01), Step 1.5c.5 scope reconciliation and handoff draft | Reviewed committed `099096e` architecture, README, 1.5c.5 scope, and existing Step 1.5c.4 closure handoff; proposed branch and complete active-task HANDOFF replacement. No repository edits, commits, native operations or transport tests. | Verified that the published scope establishes Dolphin SFTP → working TigerVNC-over-SSH POC adaptation → RDP feasibility/decision, with endpoint grammar and RDP implementation still separately gated. The maintainer reports signed `099096e` on `main` and `origin/main`. | Maintainer approves/installs revised HANDOFF and creates task branch after planning merge. Codex then undertakes 1.5c.5a endpoint-contract investigation; stop for maintainer decision before executable SFTP dispatch. |
| C24 | ChatGPT (2026-11-01), 1.5c.5a closure and 1.5c.5b activation | Reviewed maintainer-supplied X11/Wayland SFTP positive/negative transcripts, the final Codex cleanup and current handoff; verified published `b8120f7` and the archived VNC POC on GitHub. Proposed this replacement HANDOFF and unified diff, with no repository edits or native tests. | The X11 positive NSS/TCP transcript (`resolved/open/22`) was supplied but incorrectly marked pending in the prior acceptance summaries. Base managed SFTP and advisory behavior are demonstrated on both backends; remaining security/endpoint/focus variants stay qualified. | Maintainer directs 1.5c.5a closure and authorizes beginning 1.5c.5b POC/security/identity inspection; separate contract approval precedes executable VNC implementation. No new standalone planning document, native operations or publication by cloud agent. |
On subsequent iterations, record only material changes, actual evidence and unresolved work. Keep detailed logs, temporary patches, input files and generators alongside this handoff under `task_step1.5/` as appropriate; keep live source/tests in the normal project-root paths.


### 1.5c.5c findings — research 2026-11-03; native evidence reviewed 2026-11-04

**Server/session decision first.** Sharing exposes an existing graphical session;
remote login starts one without a physical user login; headless means no physical
display, not necessarily no session; persistence means reconnecting after network
loss, not recovering a session after logout/reboot. Client X11/Wayland and server
Xorg/Wayland are independent choices across RDP.

| Server | Session model and prerequisites | Assessment |
| --- | --- | --- |
| GNOME Desktop Sharing | Existing logged-in GNOME session; user service/Mutter/PipeWire; sharing credentials | Does not meet logged-out login goal. |
| GNOME Remote Login | GNOME 46+/GDM; system GRD service; entry credentials then OS-user login. Upstream 47 adds persistent remote-login sessions | Now demonstrated on Ubuntu 26.04.1 Raspberry Pi 4, including reconnect persistence; fresh-boot login remains untested. Ubuntu 24.04 persistence/backports remain separate. Documented service setup uses systemd; Gentoo/OpenRC server portability is unestablished. |
| xrdp + xorgxrdp | xrdp/sesman/PAM creates separate virtual Xorg desktop; no physical login or GDM required; reconnect policy configurable | Alternative for persistent independent sessions. Needs an Xorg-capable desktop (e.g. Xfce), not a Wayland-only GNOME session. Upstream permits non-systemd builds; local Gentoo/OpenRC packaging/PAM integration not established. |
| KRDP 6.7.5-r1 | Shares current Plasma Wayland session; screencast/portal, user authentication; virtual monitor does not create a new login | Defer as solution to logged-out remote login. Installed without systemd USE; upstream KCM service-control instructions cannot be assumed to work on OpenRC. |

Sources: [Ubuntu sharing/login](https://documentation.ubuntu.com/desktop/en/24.04/how-to/share-your-desktop-remotely/),
[GNOME configuration](https://github.com/GNOME/gnome-remote-desktop/blob/main/docs/configuration.md),
[46 login](https://release.gnome.org/46/), [47 persistence](https://release.gnome.org/47/),
[Ubuntu 26.04 GNOME 50](https://documentation.ubuntu.com/release-notes/26.04/changes-since-previous-interim/),
[xrdp 0.10.5](https://github.com/neutrinolabs/xrdp/tree/v0.10.5),
[session policy](https://github.com/neutrinolabs/xrdp/blob/v0.10.5/sesman/sesman.ini.in).
KRDP assertions checked against cached `krdp-6.7.5.tar.xz` server/main.cpp,
SessionController.cpp, RdpConnection.cpp and Gentoo patchset (no NLA changes).

**gmki91 installed clients, ranked provisionally.** Exact cached release source
and installed manpages inspected; none has demonstrated native KWin identity yet.
There is no executable RDP recipe in `-o`; subsequent maintainer manual-client evidence is assessed below.

| Candidate | Invocation/security | Identity/backend tradeoff |
| --- | --- | --- |
| 1. KRDC 26.04.3, rdp/ssh/vnc/wayland | `krdc rdp://HOST:PORT`; prompts/KWallet; certificate and changed-certificate dialogs | Fresh QApplication/MainWindow per invocation in main.cpp; Qt X11/Wayland capable. Best first managed-client candidate; separate auth dialogs and pre-login main-window placement need native acceptance. |
| 2. SDL3 FreeRDP 3.32.1 | `sdl-freerdp /v:HOST:PORT`; shared FreeRDP cert/security controls; no password argv | SDL3 has X/Wayland support locally; dialogs/viewport/window lifecycle require observation. Installed SDL3 supports both backends. |
| 3. Remmina 1.4.43, rdp/ssh/vnc/wayland/kwallet | `remmina -c PROFILE.remmina` or password-free RDP URI; cert_ignore defaults off in plugin source | GTK3 X/Wayland capable; GApplication command delegation/tab reuse complicates exact launched-PID ownership. `--new` creates a profile, not an isolated process. |
| Reference: xfreerdp 3.32.1 | `/v:HOST:PORT`, `/u:USER`, `/d:DOMAIN`, `/size:WxH`; stdin/interactive credentials | X11/XWayland, not native Wayland. Simpler per-process reference; native client/dialog identity still untested. |

`wlfreerdp` is absent. The inherited **Gentoo base**
`profiles/base/package.use.mask:334` masks `>=net-misc/freerdp-3 wayland` because
the old frontend is broken/deprecated ([bug 930197](https://bugs.gentoo.org/930197));
profile ancestry was inspected, not attributed to joetoo hardening. Exact 3.32.1
Wayland CMake marks that frontend unmaintained. This does not disable SDL3,
GTK or Qt Wayland support. FreeRDP installed USE includes client/X/sdl/server,
but not kerberos; do not promise Kerberos SSO. q552u01 inventory is deferred
until preparing the native client comparison, not assumed identical.

**Security and integration gates.** Existing VNC supervisor uses strict SSH
host-key checking, BatchMode, dedicated owned master, no agent/X11 forwarding,
and local/remote loopback forwarding; local listener/teardown were natively
accepted. Remote VNC listener exposure remains independently checked, not proven
by the forwarding destination. RDP is not intrinsically safer than this design.
Require verified CA/name or independently confirmed certificate pins, no ignore
or automatic TOFU, no password in URI/argv/logs, and no classic-RDP downgrade.
KRDC's core/krdc.kcfg defaults NLA/TLS/**classic RDP** all on; a pilot needs explicit
policy. Remmina cert_ignore is off by default but is configurable. xrdp's stable
0.10.5 template permits TLS/classic negotiation; use a TLS-only policy if selected.
Do not assume server NLA: [xrdp NLA PR 3868](https://github.com/neutrinolabs/xrdp/pull/3868)
is open; KRDP 6.7.5 RdpConnection.cpp explicitly sets NlaSecurity=false/TlsSecurity=true,
contrary to its stale README NLA-only claim. Record actual Ubuntu negotiation.
Use existing restricted LAN/VPN access; no Internet forwarding or VPN gate.
An SSH-carried RDP alternative would still need certificate-name/redirection tests.

Source anchors: current [VNC supervisor](../libexec/joetoo_kwin_vnc_launch.py)
ssh_argv/control_argv; broker _poll_correlation requires new source-consistent
UUID/exact PID and rejects ambiguity. [KRDC main](https://github.com/KDE/krdc/blob/v26.04.3/main.cpp),
[KRDP security](https://github.com/KDE/krdp/blob/v6.7.5/src/RdpConnection.cpp),
[SDL3 frontend](https://github.com/FreeRDP/FreeRDP/tree/3.32.1/client/SDL/SDL3),
[Remmina source](https://gitlab.com/Remmina/Remmina/-/tree/v1.4.43).
No RDP class/title/window-order adoption or reuse of TigerVNC role signaling is justified.

**Focused follow-up: private PKI and Windows (2026-11-03).** The maintainer
already operates root/intermediate CA and certificate-administration utilities on
three workstations. Reuse that workflow; no CA, key or credential material was
inspected. Recommend server-authentication leaf certificates with matching DNS
SANs (IP SANs for literal-IP connections), suitable key usage and protected,
service-readable matching private keys. Serve leaf plus intermediate certificates;
trust the root through the actual client trust store. Never deploy CA signing keys.
FreeRDP 3.32.1 crypto/x509_utils.c loads OpenSSL default trust paths; KRDC/SDL use
FreeRDP but actual trust-store/name checks still need native verification. A valid
certificate authenticates the server, not the user, and does not replace NLA/PAM.
Do not assume intermediate fetching or automatic revocation checks.

| Server | Existing-PKI integration and renewal assessment |
| --- | --- |
| GNOME Remote Login | `grdctl --system rdp set-tls-cert` / `set-tls-key` select service-readable certificate/key files for the system service, separate from Desktop Sharing user settings. Use the CA-issued chain instead of generating a self-signed identity. Verify chain/name through login and any session handover; upstream configuration alone does not establish deployed handover behavior. |
| xrdp | `certificate=` / `key_file=` accept PEM; upstream TLS guidance supports a PEM certificate bundle, not PKCS#7. Protect key access and select TLS-only policy. Documentation calls for service restart; verify renewed endpoint certificate afterward. |
| KRDP 6.7.5 | Server certificate/key settings load through FreeRDP PEM readers; that library accepts a leaf/intermediate chain. Configure the issued identity explicitly rather than relying on generated self-signed defaults. Native chain presentation and renewed-certificate activation remain untested. |
| FreeRDP Shadow 3.32.1 | Reads `<FreeRDP ConfigPath>/shadow/shadow.crt` and `shadow.key`; no dedicated certificate/key-path CLI switches in this release. PEM chain support verified in FreeRDP crypto source. Installed `WITH_WINPR_TOOLS=OFF` means missing files cannot be auto-generated by this code path. Key loading has no interactive passphrase callback; a protected service-readable key and controlled restart are needed. |
| Windows RDP | Import leaf/private key into Local Computer Personal (PFX is the portable import route), root/intermediates into their appropriate trust stores, then bind the listener certificate and grant its service identity key-read access. Microsoft documents `SSLCertificateSHA1Hash` and NETWORK SERVICE for standalone Windows Server listeners; the property selects a certificate, not its signature algorithm. Check the actual Windows edition/build before choosing a binding procedure. RDS role certificates have separate management. Renewal generally changes the thumbprint and needs rebinding unless established enrollment policy handles it. |

Renew through the existing CA process, retain complete chain and correct names,
and verify the certificate actually presented after the supported reload/restart;
no hot-reload/session-continuity guarantee has been established. CA-valid same-name
renewals avoid manual leaf-pin churn; pinned clients need deliberate pin rollover.
Windows RDS documents serverAuth EKU and PFX/export requirements for role import;
do not generalize exportability to every key generated in place. Existing CA
algorithm policy should be checked against each server/client before deployment.
Sources: [GNOME certificate configuration](https://github.com/GNOME/gnome-remote-desktop/blob/main/docs/configuration.md),
[xrdp TLS/PEM bundle](https://github.com/neutrinolabs/xrdp/wiki/TLS-security-layer),
[Windows RDS certificates](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/remote-desktop-services-certificates),
[Windows Server listener binding](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/remote-desktop-listener-certificate-configurations).

**Shadow is a sharing server, not remote login.** Exact 3.32.1 server/shadow source
shows NLA/EXT/TLS/classic RDP enabled as negotiation choices by default; do not
mistake defaults for an NLA-only policy. NLA uses CredSSP with NTLM SAM-backed
verification (`/sam-file`); it does not automatically validate Unix/PAM passwords.
Kerberos paths exist upstream, but installed `WITH_KRB5=OFF` excludes that option.
Explicit `/sec:tls` disables NLA/EXT/classic RDP and permits the X11 subsystem's
PAM authentication callback when compiled in. gmki91's installed subsystem links
libpam and imports pam_authenticate/pam_acct_mgmt; actual PAM policy/login remains
untested. In TLS/PAM mode the password is available to the server inside TLS,
not plaintext on the network when TLS is enforced and verified. Do not disable
authentication or weaken certificate checks to bypass SAM provisioning.
The X11 subsystem opens DISPLAY and captures its existing root window; it neither
creates sessions nor captures a complete Wayland compositor desktop through
XWayland. SDL client Wayland support does not change this server limitation.
No Shadow server was started, SAM database read or authentication configured.
Source: [exact Shadow 3.32.1](https://github.com/FreeRDP/FreeRDP/tree/3.32.1/server/shadow)
(shadow_server.c, shadow_client.c, cli/shadow.c, X11/x11_shadow.c), plus cached
crypto/certificate.c and crypto/tls.c (PEM chain parsing/presentation).

**Windows target distinction.** Pro/Enterprise/Education and Windows Server can
host native RDP; Home cannot. Linux FreeRDP-based clients are candidates for those
hosts, subject to certificate/NLA and credential testing. Native Windows client-OS
RDP transfers interactive access to the remote session and leaves the physical
console at login/lock, rather than providing simultaneous attended console sharing;
reconnecting may resume existing work. Windows Server RDS supports a different,
configured/licensed multi-session model. Record target edition/build and account
model before selecting a pilot. [Microsoft host editions](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/remotepc/remote-desktop-allow-access),
[console/session semantics](https://learn.microsoft.com/en-us/windows/win32/termserv/consoles-vs-terminals).
For attended Windows console collaboration, Quick Assist has no documented Linux
helper client; Intune Remote Help explicitly does not support Linux (web access
may function, not a supported substitute). RustDesk is a cross-platform,
self-hostable candidate for a separately approved attended-sharing evaluation,
not an RDP recipe. FreeRDP Remote Assistance invitation support and RDS shadowing
are not established as a usable Linux-to-Windows console workflow here.
[Quick Assist](https://learn.microsoft.com/windows/client-management/quick-assist),
[Remote Help platforms](https://learn.microsoft.com/en-us/intune/remote-help/plan/),
[RustDesk](https://rustdesk.com/docs/en/index.html).

**Native evidence assessment — 2026-11-04.** Reviewed the maintainer's
[Ubuntu GRD report](README_gnome_remote_desktop.md) and all 17 screenshots;
these are maintainer-operated observations, not Codex native tests. The report
supersedes the earlier pending-pilot status without changing prior research history.

| Workflow on raspiubuntu401 (Ubuntu 26.04.1, Raspberry Pi 4) | gmki91 native result and confidence |
| --- | --- |
| System GRD Remote Login, actual listener 3389 | Reported usable GDM/GNOME login with xfreerdp 3.32.1, KRDC 26.04.3 and Remmina 1.4.43; screenshots support client/desktop usability. Remmina disconnect/reconnect without logout resumed the session. |
| User GRD Desktop Sharing, actual listener 3390 | Reported working with all three clients, remote input and bidirectional plain-text clipboard; requires an existing unlocked local session in this setup. Preferred status port alone did not identify the actual negotiated listener. |
| Authentication and server identity | Separate system/user RDP credential scopes and separate self-signed certificates. Report records independent fingerprint comparison, not CA/name validation. Remote Login additionally requires GDM account authentication; neither mode used an SSH tunnel. |

**Revised recommendation.** GNOME Remote Login is now a demonstrated Ubuntu
login/reconnection baseline; replacing it with xrdp is not justified by this pilot.
Retain xrdp as an alternative for different session/desktop requirements and
TigerVNC-over-SSH as the accepted compatibility baseline. KRDC remains the
provisional first managed-client candidate for KDE usability; xfreerdp is now a
working diagnostic/reference client. Remmina is a demonstrated alternative whose
saved profiles worked at the default TLS level, not merely an untested option.
SDL3 FreeRDP still lacks native evidence; do not rank it above the tested clients
on demonstrated reliability, though it remains worth comparing for native Wayland.
None yet has demonstrated positive managed PID/new-UUID ownership or placement.

**Security qualifications.** The tested GNOME endpoint required NLA; TLS-only
negotiation was refused. KRDC NLA-only worked with its 192-bit UI security level;
NLA still uses TLS. Failure at 256 and success at 192 do not establish the precise
cipher, cryptographic cause or a general requirement to lower client settings.
Screenshot 06 shows an interim all-four-checkbox state, not the final reported
selection. Do not copy classic-RDP enablement into a future contract. Remmina's
default TLS level worked and needs no inferred KRDC-style adjustment. Private-PKI
replacement, hostname/chain validation and renewal are still untested for both
GRD services. Screenshot 16 also contains a changed-server-identification warning;
prior cached-certificate history is not explained, so do not presume every changed
identity is benign or automatically acceptable.

**Lifecycle contract implications.** Viewer disconnect is not GNOME logout;
remote work can survive closure and conflict with a subsequent local login.
Do not force-stop sessions, disable locking or terminate remote processes as
launcher cleanup. The report's journal plus successful unlock/retry strongly
supports lock-related sharing denial; the later disappearing Remmina window has
no matching journal and must not be labeled a proven lock event or client crash.
A local client window/blank frame is not proof of authenticated desktop readiness;
reported initialization delays and GDM conflicts require separate outcome reporting.
Desktop Sharing scaling/cropping reflects the physical display, unlike Remote
Login's virtual-display sizing. logind session evidence distinguishes user graphical
sessions from greeters, managers and SSH sessions; window counts cannot do that.

**Evidence integrity and remaining gate.** Screenshot 01 is byte-identical to 04
and visibly shows KRDC, despite its FreeRDP filename/index description; use 02/03
for FreeRDP visual evidence. This qualification is recorded here only; the supplied
report/screenshots remain untouched. Native evidence establishes a working server
and three clients, not a completed secure managed-RDP implementation contract.
Still outstanding: fresh-reboot login before any physical user login (including
service activation), private-PKI trust/renewal, synchronized lock-event diagnostics,
Windows server pilot, q552u01 client inventory/native Wayland comparison, SDL3
trial if selected, and exact per-client PID/UUID/dialog/delegation behavior.
No quantitative performance ranking or universal GNOME lock policy is established.
Next actor: maintainer selects the client and login/sharing scope, then authorizes
any further identity/security validation and a bounded endpoint/credential/readiness
contract. No implementation, new network session or host administration occurred
in this review; no FreeRDP legacy Wayland unmask is recommended.


### SDL lifecycle diagnostic and temporary transport — candidate, 2026-11-04

Subsequent explicit maintainer conversation authorization covers the standalone
observational diagnostic, temporary receiver, focused tests and the new
maintainer-run wrapper. This is diagnostic preparation, not authorization for
Codex-operated GUI/network activity or production RDP integration. The earlier
research and native-evidence records above remain historical; this entry does
not repeat interoperability testing or declare a desktop-role discriminator.

- [Observer](../tools/joetoo-rdp-window-diagnostic.js) records bounded, sequenced
  creation/property/activation/move-resize/removal evidence. Unsupported fields
  are explicit. Captions are filtered to the generated proof marker; unrelated
  captions, input contents, credentials and certificate contents are excluded.
  Activation does not establish operator intent; a marker invoked from Konsole
  records Konsole at invocation, not the previously active viewer.
- The reported startx session routes KWin descriptors to tty1; no usable current
  console-log capture was established. Exact local KWin X11 6.7.5/Qt 6.11.2
  sources were inspected. KWin's asynchronous `callDBus` suppresses JavaScript
  callbacks on D-Bus errors, requiring an independent acknowledgement deadline.
- [Temporary receiver](../tools/joetoo-rdp-diagnostic-receiver.py) uses the existing
  Unix session bus, pins KWin's unique owner/UID, and writes private exclusive
  evidence. `Append` acknowledges only after persistence. `Probe` confirms
  observing/draining and receipt of the end acknowledgement; `Status` exposes
  readiness/completion. Independent verification checks framing, sequences,
  schema, hashes and receipts. No production bridge method or service changes.
- Observation defaults to 1,800 seconds; `RDP_DIAG_SECONDS=2400` is preserved
  when supplied. Default buffer: 1,024 events. ACK/liveness defaults: 3,000/5,000
  ms. Export ceiling is derived as `(maxRecords + 3) * ackTimeoutMs` (3,081,000 ms
  by default), covering the full buffer plus drain/end/sender confirmation;
  an individual missing acknowledgement fails after 3 seconds. Full-buffer
  disposable persistence/verification took 2.35 seconds in the prior full run;
  that is not native throughput evidence. Overflow and interrupted output remain
  explicitly incomplete. `transport_complete`, `sender_confirmed_end_ack` and
  `internal_capture_intact` are distinct; native lifecycle coverage is unassessed.
- [Maintainer runner](../tools/joetoo-rdp-diagnostic-run.sh) uses the installed
  joetoo header/AAR and pseudo-boolean conventions, confirms the native action,
  creates private storage, owns one receiver, refuses an existing diagnostic,
  gates the unchanged proof on persisted readiness, exports/verifies, unloads
  only its diagnostic, stops only its receiver and archives without overwrite.
  Python/Linux pidfd support is required for automatic receiver cleanup; failure
  retains evidence and reports the remaining receiver. Viewer/remote-session
  termination is never a cleanup action. Failure/interruption retains partial
  evidence and cannot count as acceptance. The existing proof archive remains
  separate; correlate its PID/title/phase markers/screenshots with diagnostic
  UUID/event history. No changes to either maintainer-owned tool.

Current headless evidence: **440 Python / 91 JavaScript passed**, no skips or
failures; 58 focused receiver/wrapper tests passed. Wrapper paths ran with fake
KWin, receiver, header and proof commands in disposable fixtures, including
readiness/cancellation/failure/interrupt cleanup, unrelated-process preservation,
argument arrays, reporting faults and archive non-overwrite. The real proof and
restart tools were neither executed nor modified. All five tool/test candidate
files are untracked; this HANDOFF update is uncommitted. No native diagnostic,
RDP connection, service restart, deployment or publication was performed.

**Next actor:** maintainer reviews the candidate and authorizes/runs one gmki91
X11 temporary-to-persistent lifecycle capture. A valid receipt does not establish
coverage through authentication, GDM, GNOME and viewer removal; check those
against the proof evidence before deciding whether a repeatable role discriminator
exists. Evaluate X11 findings before selecting additional Wayland observations.
Production enrollment, fixed-delay selection and any RDP executor remain outside
this diagnostic increment. Commit/push/PR/native execution require their separate
maintainer decisions.

### Native-Wayland SDL viewer identity — investigation, 2026-11-05

**Determination (proposed contract, not production acceptance):** existing KWin
observations can support a native-Wayland SDL-specific marker/PID/new-UUID role
predicate without input observation. The generic managed-launch selector cannot
be used unchanged: `_poll_correlation()` selects by PID, treats the title only as
a hint, and uses a fifteen-second deadline. Isolated broker fixtures reproduced
registration of an unmarked credential window alone and ambiguity when that
window coexisted with the marked viewer. These are limitations for the proposed
SDL reuse, not defects in the accepted Konsole/Dolphin contract.

**Maintainer-native provenance:** the original capture was
`/tmp/joetoo-rdp-stage-a.uXBwj934`; its verified current private archive is
`~/.local/share/joetoo-ai/rdp-evidence/joetoo-rdp-stage-a.uXBwj934.tbz2`, SHA-256
`b7e392d31c7bf00b814453ee896270418c52938444fc3d24a9822e723e790c4b`.
It reports native `wayland`, PID 1763685, credential UUID
`17559f9c-a1c8-4607-8b8b-d2b19e90ebd3` without the launch marker (events 11–762),
and viewer UUID `70f7e047-fe6f-4fd4-b363-58bf0e6130ca` with the exact marker at
addition 763 through removal 1236. The 2,403 samples showed one observer source
and one viewer-caption value; before/after inventories were synchronized.
First samples containing credential addition and viewer addition were more than
five minutes apart: the generic fifteen-second lease does not cover this proof.
These sample times are not exact window-creation timestamps. Client exit 2 and
remote logout/disconnect remain separate from identity. Raw archives were read
in place, not copied into this public repository.

**Inspected source:** local distfiles FreeRDP 3.32.1 (`client/SDL/SDL3/`),
SDL 3.4.18 (`src/video/wayland/SDL_waylandwindow.c`, `SDL_video.c`, `SDL_hints.c`),
and KWin 6.7.5 (`waylandwindow.cpp`, `xdgshellwindow.cpp`, `wayland_server.cpp`).
`SdlContext::windowTitle()/createWindows()` passes the configured title into
`SdlWindow` creation properties; credential/retry dialogs use their own titles.
SDL publishes the title through xdg-shell or libdecor. KWin propagates title
changes and gets the native client PID from its Wayland connection. Its native
window-added path waits for mapping/painting readiness after a configured
surface commit with a buffer; this supports stronger lifecycle evidence than raw
SDL object creation, but does not prove indefinite persistence or remote login.
Source supports multiple display windows, so restrict the first recipe to a
single desktop window, excluding multimonitor/RemoteApp behavior. Installed
versions on q552u01 should be recorded during the remaining check; the old
archive's client log does not establish its exact FreeRDP/SDL versions.

**Necessary broker-owned predicate:** arm before launch; pin live process,
request nonce, source/revision and baseline; require a new normal-window UUID
with a complete added lifecycle, matching launched PID/application and exact
marker. A late caption can qualify that same UUID; a changed-only snapshot
cannot establish creation. Track marker-bearing UUIDs as existing observations
arrive, including competitors that subsequently disappear; coalesced latest
snapshots alone cannot establish absence of competitors. More than one eligible
UUID, history loss, source replacement, expiry/cancellation, process mismatch or
exit, lost marker before commit, disappearance or prior ownership must not
register. There is no last-window or quiet-delay role rule and no required
predecessor. Treat other token-bearing/decorated candidates conservatively as
competitors rather than silently ignoring them. After registration, a new UUID
requires a new authorized transaction; never silently retarget the record.
Existing `WindowRegistry.register_match()` supplies source/PID/live-UUID/baseline
and duplicate-ownership checks, not the missing SDL role predicate.

The backend must actually be native Wayland, not inferred from the Plasma
session. SDL3's canonical child-only override is `SDL_VIDEO_DRIVER=wayland`;
source selects only that backend when it is the sole requested driver. The old
`SDL_VIDEODRIVER` spelling is a fallback alias. Confirm `backend.txt` on native
runs. No backend/session configuration was changed here. Existing resident
caption signals and the standalone diagnostic suffice; normal-caption evidence
is already captured by the diagnostic. No additional input observer is proposed.

**Remaining bounded native check:** use the existing runner on q552u01 with
`SDL_VIDEO_DRIVER=wayland RDP_DIAG_X11_USE=` and the revised proof, no screenshots.
Across short separate captures, cancel naturally presented credentials, inspect
one failed/retried NLA attempt only if account policy safely permits it, and
check a maintainer-chosen connection failure. Include one delayed successful
attempt while an unrelated SDL viewer remains open to verify distinct PID/nonce
and UUID histories. Use a naturally available retry/reconnect path if available;
do not change networking/services/credentials to manufacture it. Record an
unexercised reconnect as untested and reject UUID replacement in the initial
contract. Any marked auxiliary window or multiple eligible UUIDs invalidates
title-only selection for that path. No enrollment occurs in these diagnostics.
Wrong GDM credentials inside an already valid viewer are a remote-login outcome,
not evidence that the local viewer is the wrong window. The twelve proof phases
now separate observation, screenshots, graphical login, logout and viewer close.

**Smallest subsequent implementation, subject to separate authorization:** a
client-specific native-Wayland role policy in the existing broker-controlled
viewer transaction plus its local launcher adapter, configurable readiness
bounds and focused regressions. Preserve registry and generic launch semantics;
no new observation service. Both `SubmitManagedLaunch()` and the VNC-specific
`CompleteManagedViewer()` currently couple registration with placement, so they
cannot implement placement-held registration unchanged. Start with a narrowly
reviewed registration-only SDL slice; separately approve the post-login release
and exact-UUID placement contract. Title identity does not prove GDM login,
remote-session health or production certificate validation.

**Checks and artifacts:** 92 Python regressions; 44 focused / 99 full JavaScript
regressions passed without skips. Two diagnostic-only test additions cover late
caption arrival/loss and simultaneous same-PID marked UUIDs, preserving privacy
and no-selection behavior. No production selector has been implemented or
validated by those tests. New `/tmp/step1.5c5c-wayland-identity-*.log` files are
reproducible/disposable once these results are retained. Unique new assertions
remain in `tests/test_rdp_window_diagnostic.js`; findings are retained here.
Existing untracked diagnostic source/tests remain **retain**, pending review and
publication. Private native tarballs are **retain** in the verified `rdp-evidence`
directory; original `/tmp` captures are not presumed retained. Older review
patches already represented by current source are redundant exports; other old
intermediates and maintainer-organized generators/backups were not reassessed
for disposal and remain **needs maintainer review**. No relocation, deletion,
new archive, broad cleanup or new standalone report was performed.

## 6. Current gate — Step 1.5c.5b TigerVNC-over-SSH contract review

**Completed gate:** Step 1.5c.5a SFTP is accepted and closed. Both X11 and Wayland have positive managed SFTP and independently observed remote browsing; the two-stage advisory has positive/negative native evidence, including the previously overlooked X11 `resolved/open/22` run. Remaining edge cases stay documented as limitations, not blockers.

**Active gate:** inspect the actual working KDE launcher and archived `vnc-via-ssh-launch`; recommend a safe VNC-over-authenticated-SSH invocation with loopback-only forwarding, reliable actual viewer-window PID/UUID correlation, conservative timeout/partial-failure behavior and deterministic tunnel cleanup. Distinguish GUI launch, transport establishment, server authentication and window placement. No network or graphical actions by Codex; no executable code changes until the specific contract is approved.

**Next actor:** Codex performs that narrowly authorized read-only investigation and reports findings for the maintainer's next decision, using existing task records rather than creating more `.md` files. The maintainer supplies the live KDE launcher command if absent from the repository, reviews the proposed contract, and authorizes or defers implementation. RDP and integrated Step 1.5d remain separately gated. Commit/merge/deployment authority remains with the maintainer.
