## Step 1.5c — implementation scope and outline

**Status:** Proposed refinement for maintainer review. Steps 1.5a and 1.5b are complete (PRs #23/#24). Initial 1.5c.1–1.5c.3 authorization was recorded in HANDOFF.md on 2026-10-29 at 21:46:16; the maintainer must confirm this reconciled scope before coding begins. Step 1.5c.4 remains separately gated.

**Task branch baseline:** Accepted `main` containing the final authorized scope (published as `06ab98ca4d5b34eb2adf73557559bd5be522f4a6` at this review). PR #24 merged at `54f2ef6895f02dc198c79a821f76ef8343e5e701` before the Step 1.5c authorization. Verify the branch point dynamically.

**Proposed task branch:** `task/joetoo-kwin-step1.5c-configured-launch`

### Objective

Implement configuration-driven `joetoo-kwin -o` (open/launch) using the accepted launch configuration/plan presenter (also refered to previously as planner), existing managed-launch broker interfaces, and proven interactive SSH startup pattern (archive/joetoo-kwin-ssh-nc-poc, archive/joetoo-kwin-ssh-rcfile-poc). Preserve exact window identity, registration and placement verification, interactive shell continuity, and independent reporting of SSH transport outcomes.

### Proposed increments

**1.5c.1 — Plan-to-launch integration**

- Reuse existing defaults → trusted configuration → CLI override precedence.
- Validate and display effective configuration through the existing `varlist` and `show_config` conventions.
- Display the shared calculated launch plan.
- Run `confirm_continue_or_exit` before initiating application launches.
- Reject unsupported or malformed **executable `-o` plans as a whole** during preflight, before creating any window. Detect active managed desktop/slot conflicts and unresolved broker/registry state before confirmation.
- Ensure cancellation and validation failure create no application windows.
- Preserve `-c` as a descriptive dry run even for configured modes not yet executable by `-o`. Document both `desktop_session_list=(...)` and separate `desktop_session_list+=(...)` assignments; examples of unsupported entries may be commented out or retained only for `-c` testing.
- Preserve the established norms for use of messaging severity levels. Notice for progress/results, info for window and placement details, debug for request diagnostics.

**1.5c.2 — Managed Konsole and local application launching**

- Reuse `launch_managed_window`, `SubmitManagedLaunch`, positive PID/UUID correlation, registration polling and asynchronous placement verification.
- Launch configured windows sequentially, waiting for definitive registration and placement results before proceeding.
- Respect existing broker serialization and Busy behavior.
- Reject an individual request that conflicts with an **active, positively registered** managed window assigned the same intended desktop and slot; do not adopt, replace or block merely overlapping unmanaged windows. Repeated SSH target hostnames are valid.
- On a **known, isolated** window registration/placement failure, report it conspicuously, leave already launched windows intact, and continue with remaining independent entries. Report the overall layout as incomplete. Stop further launches when Busy/ownership state remains unresolved or safety cannot be established.

**1.5c.3 — Interactive SSH and placeholders**

- Adapt the archived single-Bash `--rcfile` proof of concept.
- Preserve the installed `ssh_wrapper` function and normal interactive Bash environment. It calls `command ssh "$@"`, preserves its exit status and restores terminal state; do **not** substitute `swr`, whose `pur` and SSH-port waiting loops target a different, interactive use case.
- Use the archived **short `nc -z -w 2` TCP-port probe** as a bounded connection-start convenience, not a reason to suppress window creation. Keep the same original Bash available after SSH logout, failure or unreachable-host detection; display the target, outcome and manual retry command.
- Preserve the intended connection target and purpose for manual retry.
- Treat successful registration and placement of an unreachable SSH placeholder as successful window management.
- Keep transport, registration and placement status logically independent.

**1.5c.4 — Graphical applications (separate approval)**

- In a separately approved design, define the relationship among graphical application, transport and launch mode. Historic `direct` and `via-ssh` labels are not executable contracts. Consider TigerVNC-over-SSH and possible RDP clients without conflating the program with its transport.
- Preserve correct managed correlation for graphical windows.
- Implement and natively validate appropriate underlay, visibility, stacking and focus behavior.
- Until supported, reject such executable recipes before launching any part of a plan.

### Policy decisions

1. Invalid/unsupported `-o` plans and declined confirmation launch **no** windows. Show effective configuration, a complete plan, and reliable unmanaged-overlap warnings before confirmation.
2. Permit only one active managed-launch transaction at a time. Do not submit the next window until the preceding transaction is definitively completed; unresolved Busy or uncertain ownership stops the run safely.
3. A known, isolated window registration/placement failure should **not** abort the remaining independent launch entries. Report the failure prominently, keep prior windows open, and provide a final complete/incomplete summary. Never silently roll back or close already-created windows.
4. Reject active, positively registered managed desktop/slot conflicts. An unrelated window at overlapping coordinates is not managed ownership; repeated hostnames/connections are valid.
5. A correctly identified and placed Konsole counts as a successful window-management result even when its SSH connection is unavailable or has ended. Distinguish launch/registration, placement and SSH transport outcomes.
6. For initial multi-window SSH use `ssh_wrapper` within the original `bash --rcfile` shell and an optional short TCP probe; `swr`/`pur` waiting semantics remain separate. A single-window launch interface is not yet approved.
7. Establish only those configuration mode mappings supported by inspected source and a safe tested dispatch. Unsupported graphical/transport modes fail `-o` preflight without preventing their presentation in `-c`.
8. Preserve existing broker/resident interfaces and exact geometry verification unless separate evidence and authorization justify a change.
9. Preserve `script_header_joetoo` severity conventions and announce–act–report: notice for progress/results, info for window and placement details, debug for request diagnostics; error/warning messages must remain conspicuous.


### Authorization boundaries

The **single active authorization record** is Section 4 of [HANDOFF.md](HANDOFF.md). It specifies the permitted write paths, read-only references, headless validation, native gates, and separate publication decisions. This detailed scope does not expand those permissions. Broker, resident, registry, installed files, archive sources, and protected repositories remain out of scope without separate approval.

### Acceptance and handoff

The candidate should demonstrate configuration validation, safe cancellation, successful sequential managed launch, exact UUID registration, correct placement, transport-independent SSH placeholders, absence of unintended changes to unrelated windows, and consistent announce–act–report behavior.

Maintainer-native acceptance will be performed on `gmki91` X11 and `q552u01` Wayland.

Outstanding Step 1.5b native edge cases will be incorporated into the Step 1.5d regression matrix, except launch-concurrency scenarios that should receive additional 1.5c coverage.

**Next actor:** Maintainer confirms this reconciled scope and HANDOFF authorization; then Codex begins only the approved 1.5c.1–1.5c.3 tasks in its isolated branch. Native operations and publication remain separate gates.
