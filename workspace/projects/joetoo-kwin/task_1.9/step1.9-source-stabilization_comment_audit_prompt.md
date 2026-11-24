# Joetoo source maintainability and metadata audit

Use the repository skill:

`.agents/skills/joetoo-source-maintainability/SKILL.md`

If that exact path does not exist, locate the installed skill named `joetoo-source-maintainability` and read its complete instructions before proceeding.

**Target files:**

`<INSERT FILE PATH(S) OR DIRECTORY HERE>`

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

Prefer useful explanatory comments over maximum comment volume. Avoid commentary that merely restates obvious code.

**Third: validate.**

Run applicable syntax, static-analysis, metadata-extraction, build, and focused regression checks using the available environment.

Review the diff to ensure no unintended executable behavior changes were introduced.

State explicitly which checks passed, failed, or could not be performed.

**Fourth: report.**

Provide:

1. Files and functions reviewed.
2. Summary of metadata/comment improvements.
3. Proposed patch or exact diff.
4. Validation results.
5. Separate functional findings or unresolved ambiguities.
6. Recommended audit-ledger disposition.

## Step 1.9 integration

When working within `joetoo-kwin`, use `task_1.9/HANDOFF.md`, the packaging contract, `ARCHITECTURE.md`, and the project-root `MANIFEST` to determine release scope.

Keep the maintainability audit separate from runtime-path corrections, provenance/licensing acceptance, upstream source transfer, `tarup`, ebuild construction, and packaged-path native testing.

The audit is complete only when the designated files have been fully reviewed, validated as appropriate, and accepted by the maintainer.

**Proceed with the audit of the specified targets. Do not expand the requested file scope without explaining the dependency and obtaining approval.**
