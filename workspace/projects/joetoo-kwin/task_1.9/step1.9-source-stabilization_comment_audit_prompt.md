# Joetoo source maintainability and metadata audit

Use the repository skill:

`.agents/skills/joetoo-source-maintainability/SKILL.md`

If that exact path does not exist, locate the installed skill named `joetoo-source-maintainability` and read its complete instructions before proceeding.

**Target files:**

`libexec/joetoo-kwin-launch-functions`

## Task

Audit and improve the source comments, structured function metadata, and explanatory documentation of the specified files according to the skill.

The objectives are:

1. Make the code understandable and maintainable by a future developer unfamiliar with its implementation.
2. Document nontrivial function contracts, dependencies, state, side effects, return behavior, and important invariants.
3. Explain non-obvious language constructs and implementation decisions, including **why** the existing approach is necessary.
4. Correct misleading, outdated, incomplete, contradictory, or redundant comments.
5. Prepare structured metadata for future automated documentation extraction, using Joetoo's existing conventions wherever applicable.

Use `tools/joetoo-kwin-stage-upstream` as the reference standard for explanatory implementation comments.

For Bash, inspect the actual `summarize_header()` implementation in `script_header_joetoo`, including its parser expectations and the different behaviors of `@cont` and `@append`.

## Mandatory inline block-level documentation

**Do not equate completed function metadata with readable implementation.**
Read every targeted function statement by statement, dividing it into logical
blocks. A nontrivial block can be one or two lines (even a single opaque shell
expression); a straightforward sequence may be longer. For each such block,
explain at the point of use, as applicable:

1. **Purpose:** what it accomplishes and why it is needed here.
2. **Inputs and state:** origins and scopes of important values (local, global
   configuration, environment, caller-local/dynamic scope, prior command).
3. **Mechanics:** non-obvious language behavior, pipelines, options, command
   substitutions, file descriptors, subprocesses and ordering.
4. **Data contracts:** expected types/formats; JSON or IPC fields, helper
   arguments and outputs, parsing/filter semantics and exit-status meanings.
5. **Decisions:** what enters each meaningful branch and what it permits,
   prevents, skips or defers.
6. **Failure handling:** why an operation returns, continues, retries, falls
   back or deliberately suppresses a failure.
7. **Invariants:** relevant ownership, lifecycle, ordering, resource and
   security constraints.

Put explanations immediately before their block or beside a statement. Cover
**all** functions, including long control-flow functions and short helpers;
do not concentrate only on the first function or the existing metadata.
A `j_msg`/diagnostic may be adequate if it truly conveys the explanation.
Avoid narrating obvious syntax, but do not leave an opaque block unexplained
merely to minimize comments. The developer should not need to run `--help`,
trace multiple source files or reconstruct a protocol to understand that block.
Verify technical claims against actual callers/callees/helpers and tests.

For Bash, explicitly examine config versus local state, pseudo-booleans and
naming conventions, Bash dynamic scope, `BASH_SOURCE`/resource locations,
short-circuit operators such as `|| :`, `jq` flags and filters, and differences
between action, process and reporting statuses **where they occur**. For other
languages, apply the same coverage standard to their corresponding constructs.
Never claim a pattern is necessary or a status has a particular meaning without
checking the implementation and its contract.

**Separate documentation from refactoring.** Explain existing code accurately,
even when it is clumsy. In the findings, record overly complex constructs,
potential defects, conflicts with Joetoo conventions or best practices, and
cases where the conventions themselves appear at odds with best practices.
Do not change executable behavior during this audit.

## Language-specific requirements

**Bash and shell:** Apply Joetoo's `# @usage`, `# @args`, `# @ret`, `# @deps`, `# @vars`, `# @req`, `# @rule`, `# @note`, and related metadata conventions. Where appropriate, adapt function declaration formatting to make the top-level description recognizable to `summarize_header()`, with the opening brace on the following line. Preserve function behavior.

**Python:** Use idiomatic module, class, and function docstrings. Explain contracts, exceptions, subprocess and resource ownership, state, and significant failure handling.

**JavaScript:** Use suitable JSDoc and inline comments. Explain callbacks, asynchronous behavior, KWin APIs, identity and ownership, event handling, and cleanup.

**C++:** Use consistent Doxygen-compatible function and class documentation. Explain ownership, resource lifetime, Qt/KWin interactions, C++ language semantics, native protocol assumptions, error handling, and ABI-sensitive constraints. Include relevant headers and build-system commentary.

Do not force Bash metadata syntax onto Python, JavaScript, or C++.

## Boundaries

This is a **maintainability/documentation audit**, not a functional redesign.

- Preserve all executable behavior, interfaces, return codes, dependencies, configuration contracts, and safety properties.
- Permit only the narrowly necessary, behavior-preserving shell function-declaration formatting required for Joetoo metadata compatibility.
- Do not refactor, rename, optimize, or otherwise rewrite code merely because an alternative seems preferable.
- If a functional defect or documentation/implementation contradiction is discovered, record it separately rather than silently fixing it.
- Record suspected refactoring opportunities and Joetoo/best-practice tensions separately; do not use them to justify behavior changes.
- Do not invent guarantees, return-code meanings, dependencies, or security properties.
- Do not introduce new metadata tags without explaining why the existing Joetoo taxonomy is insufficient.
- Follow repository `AGENTS.md` instructions and existing skill dependencies.
- Do not modify `joetoo-upstream`, `joetoo`, installed files, or host configuration.
- Do not commit, push, merge, publish, or deploy without explicit maintainer authorization.
- Do not change the calling terminal's umask.

## Workflow

**First: inspect and assess.**

Read the complete target files and relevant callers/callees. Establish their actual behavior. Identify comment deficiencies, incomplete metadata, unclear contracts, misleading explanations, and any functional issues discovered.

Present a concise assessment of the proposed changes.

**Second: prepare improvements.**

Produce the proposed comment/metadata edits as a reviewable diff or patch. For large files, work in coherent sections, but assess the complete file for consistency.

Prefer explanatory completeness over a low comment count. Do not restate
self-evident code, but explain every nontrivial block's relevant mechanics and
rationale, including terse one-liners whose purpose is not obvious.

**Third: validate.**

Run applicable syntax, static-analysis, metadata-extraction, build, and focused regression checks using the available environment.

Review the diff to ensure no unintended executable behavior changes were introduced.

**Independently reread every targeted function, block by block.** Account for
all nontrivial blocks using adjacent comments, or explicitly identify and
justify those left uncommented because their code/messages are already clear.
Check accuracy against the actual called helpers and baseline behavior.
Static checks and metadata extraction do not substitute for this review.

State explicitly which checks passed, failed, or could not be performed;
distinguish reproduced baseline failures from introduced regressions.

**Fourth: report.**

Provide:

1. Files and functions reviewed.
2. Summary of metadata **and inline-block** improvements, function by function.
3. Coverage exceptions: any nontrivial blocks left without added comments,
   with a specific explanation of why existing code/messages suffice.
4. Proposed patch or exact diff.
5. Validation results, including baseline failures and unrun checks.
6. Separate functional issues, potential refactors, convention/best-practice
   tensions and unresolved ambiguities; no silent functional changes.
7. Recommended audit-ledger disposition; leave acceptance to the maintainer.

## Step 1.9 integration

When working within `joetoo-kwin`, use `task_1.9/HANDOFF.md`, the packaging contract, `ARCHITECTURE.md`, and the project-root `MANIFEST` to determine release scope.

Keep the maintainability audit separate from runtime-path corrections, provenance/licensing acceptance, upstream source transfer, `tarup`, ebuild construction, and packaged-path native testing.

The audit is complete only when the designated files have been fully reviewed,
including inline-block comprehension and documented coverage exceptions,
validated as appropriate, and **accepted by the maintainer**. Do not recommend
`ACCEPTED` merely because function metadata, syntax/lint, or tests pass. This
is an existing acceptance criterion, not a new stage or authorization gate.

**Proceed with the audit of the specified targets. Do not expand the requested file scope without explaining the dependency and obtaining approval.**
