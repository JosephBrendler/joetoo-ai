## Step 1.5c — implementation scope and outline

**Status:** Maintainer's draft, presented to agents for critical review. Steps 1.5a and 1.5b are complete and merged through PRs #23 and #24. Step 1.5c implementation is not yet authorized.

**Accepted starting baseline:** `54f2ef6895f02dc198c79a821f76ef8343e5e701`

**Proposed task branch:** `task/joetoo-kwin-step1.5c-configured-launch`

### Objective

Implement configuration-driven `joetoo-kwin -o` (open/launch) using the accepted launch configuration/plan presenter (also refered to previously as planner), existing managed-launch broker interfaces, and proven interactive SSH startup pattern (archive/joetoo-kwin-ssh-nc-poc, archive/joetoo-kwin-ssh-rcfile-poc). Preserve exact window identity, registration and placement verification, interactive shell continuity, and independent reporting of SSH transport outcomes.

### Proposed increments

**1.5c.1 — Plan-to-launch integration**

- Reuse existing defaults → trusted configuration → CLI override precedence.
- Validate and display effective configuration through the existing `varlist` and `show_config` conventions.
- Display the shared calculated launch plan.
- Run `confirm_continue_or_exit` before initiating application launches.
- Reject unsupported or malformed launch recipes during preflight.
- Ensure cancellation and validation failure create no application windows.
- Preserve `-c` as a dry run.

**1.5c.2 — Managed Konsole and local application launching**

- Reuse `launch_managed_window`, `SubmitManagedLaunch`, positive PID/UUID correlation, registration polling and asynchronous placement verification.
- Launch configured windows sequentially, waiting for definitive registration and placement results before proceeding.
- Respect existing broker serialization and Busy behavior.
- Reject collisions with currently registered managed desktop/slot identities; do not adopt or replace unrelated windows.
- Stop subsequent launches upon a required registration/placement failure, retaining already-created windows and accurately reporting partial completion.

**1.5c.3 — Interactive SSH and placeholders**

- Adapt the archived single-Bash `--rcfile` proof of concept.
- Preserve the established `ssh_wrapper` function and normal interactive Bash environment.
- Keep the same original Bash available after SSH logout, failure or unreachable-host detection.
- Preserve the intended connection target and purpose for manual retry.
- Treat successful registration and placement of an unreachable SSH placeholder as successful window management.
- Keep transport, registration and placement status logically independent.

**1.5c.4 — Graphical applications (separate approval)**

- Define and implement `direct` and `via-ssh` graphical launch recipes, including VNC.
- Preserve correct managed correlation for graphical windows.
- Implement and natively validate appropriate underlay, visibility, stacking and focus behavior.
- Until supported, reject such executable recipes before launching any part of a plan.

### Policy decisions <--- update this section based on my comments to your request for decisions in last chat turns

1. Use conservative reject-before-launch handling for overlapping managed desktop/slot identities. Unrelated observed windows do not constitute managed ownership.
2. Do not automatically close or roll back windows created by a partially successful `-o` invocation.
3. Do not allow failed SSH connections to invalidate otherwise successfully registered and placed placeholders.
4. Preserve existing broker/resident interfaces unless a specific demonstrated limitation requires separately reviewed changes.
5. Define the supported execution semantics of `ssh`, `swr`, `local`, `direct` and `via-ssh` before implementing their dispatch.
6. Retain the current exact geometry-verification policy unless separate native evidence justifies a change.
7. Preserve the established norms for use of messaging severity levels. Notice for progress/results, info for window and placement details, debug for request diagnostics.

### authorization boundaries

After explicit maintainer approval, the first implementation scope may include:

- `joetoo-kwin`
- `libexec/joetoo-kwin-plan-functions`
- New narrowly scoped launch and interactive-startup helpers under `libexec/`, as justified by inspected POCs
- Relevant Python, Bash and JavaScript test fixtures
- Step 1.5c task evidence and agent-owned handoff iteration records

Broker, resident, registry, installed system files, archive contents, official protected repositories, and governing documentation remain excluded from modification without separate approval.

Permitted headless tests include Python regression suites, JavaScript tests, Bash syntax, ShellCheck, and appropriate installed-header integration tests.

Native KWin operations, SSH connections, installation/service changes, commits, pushes, PR creation and merges remain separately gated.

### Acceptance and handoff

The candidate should demonstrate configuration validation, safe cancellation, successful sequential managed launch, exact UUID registration, correct placement, transport-independent SSH placeholders, absence of unintended changes to unrelated windows, and consistent announce–act–report behavior.

Maintainer-native acceptance will be performed on `gmki91` X11 and `q552u01` Wayland.

Outstanding Step 1.5b native edge cases will be incorporated into the Step 1.5d regression matrix, except launch-concurrency scenarios that should receive additional 1.5c coverage.

**Next actor:** Maintainer reviews and approves or revises this scope before Codex implementation begins.
