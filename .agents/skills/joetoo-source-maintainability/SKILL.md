---
name: joetoo-source-maintainability
description: Audit and improve Joetoo Bash, Python, JavaScript, and C++ source comments, function contracts, and extractable metadata using the established script_header_joetoo summarize_header conventions and the joetoo-kwin-stage-upstream explanatory-comment standard. Use for Step 1.9 joetoo-kwin source stabilization and later Joetoo maintainability reviews.
---

# Joetoo source maintainability and structured metadata

## Purpose

Use this skill for reviewable source-documentation audits. Combine (1) concise,
structured contracts that can feed generated references with (2) explanatory
inline comments that clarify *why* non-obvious code exists. The source of truth
is the implementation, not a comment or an anticipated release contract.

For `joetoo-kwin` Step 1.9, audit all curated production source code,
including Bash, Python, JavaScript, C++ implementations and headers,
before source-release transfer and `tarup`. This skill is reusable beyond that
task; do not hard-code its inventory into the skill.

## Authority and source discovery

1. Read applicable repository/workspace/project `AGENTS.md` and the current
   architecture, task HANDOFF, packaging contract, and current branch. For
   `joetoo-kwin`, enumerate production sources from project-root `MANIFEST`.
   Review actual callers/callees and do not use historical archives as the
   authoritative current implementation.
2. Inspect the **actual installed/checked-out** `script_header_joetoo`,
   especially `summarize_header()`, `_sh_render_buffered_tag()`, `toc()`, and
   several real function metadata blocks. Examples: `summarize_header -f toc`
   and `summarize_header -f j_msg`. Metadata output assists discovery but is
   not a substitute for reading the code.
3. Inspect `tools/joetoo-kwin-stage-upstream` as a model for explanatory
   comments: function purpose, non-obvious language semantics, subprocess
   outcomes, ordering, safety and explicit limits. **Do not** assume it already
   follows the complete structured-metadata declaration layout.
4. Follow the relevant `script-header-joetoo` skill, when present. Confirm
   syntax/extractor behavior against the installed version; if version differs,
   report the differences rather than silently extending the format.
5. Use connected repositories read-only unless expressly authorized. Do not
   modify protected `joetoo-upstream` or `joetoo`, run `tarup`, publish,
   install, change host configuration, commit or push without permission.

## Two complementary documentation layers

- **Structured contracts:** concise purpose/signature, arguments, options,
  outputs/return statuses, external globals/state, dependencies, prerequisites,
  mandatory invariants, notes and warnings. Make these discoverable by tools.
- **Inline explanations:** why mechanisms and ordering matter, non-obvious
  Bash/Python/JS/C++ behavior, security and lifecycle decisions, failure
  classifications, and deliberate tradeoffs. Don't narrate trivial code.

Add documentation only after verifying the actual behavior. Do not assert
unproven guarantees, fabricate error-code meanings, or mask defects with prose.

## Exact current Bash metadata convention

The source-reviewed `summarize_header()` in
`joetoo-upstream/dev-util/script_header_joetoo/script_header_joetoo`
recognizes a function line at **column one** matching a shell name followed
by `()` and a space. It extracts the top-level description from the `#`
comment on that declaration line; metadata tags are later associated with the
last recognized function. The existing Joetoo layout uses the opening `{`
on the **following line**. The parser recognizes the declaration, not the
brace as a separate metadata field; do not claim that it validates braces.

Prefer this formatting when converting `joetoo-kwin` Bash functions:

```bash
file_parity() # Return success only when release inputs have byte/mode parity
{
    local src=$1 dest=$2
    # ... existing implementation, unchanged ...
}
# @usage file_parity SRC DEST
# @args $1: source file path
# @args $2: staged destination path
# @ret 0 when both are safe, regular, byte-identical, and mode-identical
# @ret nonzero otherwise; the current function does not classify causes
# @deps cmp, stat
# @rule do not equate a zero rsync exit with successful file parity
```

This layout **can require rearranging the function opening** from
`name() {` into `name() # description` followed by `{`. That is a small
**executable-syntax/layout edit**, not a literal comment-only change.
Preserve the function body and verify its syntax and behavior. Keep these
formatting changes separately recognizable in the diff and avoid unrelated
code changes. Do not change function declaration styles in Python/JS to mimic
shell metadata.

Tags recognized in the current parser are literal, unindented lines beginning
`# @tag ` (starting at column one), with lowercase tag names. Use preferred
ordering `usage opts args ret deps vars req rule note warn ex`. Include
`@usage` as the baseline for each normal function; add other tags as actually
applicable. Prefer lines shorter than 80 columns. Use these existing tags:

| Tag | Purpose |
| --- | --- |
| `@usage` | Invocation/signature |
| `@opts` | Options or option-like arguments |
| `@args` | Argument meaning |
| `@ret` | Return status, emitted output and/or returned value |
| `@deps` | Called functions, tools, modules or package dependencies |
| `@vars` | External globals required or mutated (not merely local variables) |
| `@req` | Preconditions or required state |
| `@rule` | Required behavior and invariant |
| `@note` | Explanatory/administrative note |
| `@warn` | Important warning |
| `@ex` | Example |
| `@cont` | Manual next display line under the prior tag |
| `@append` | Append to prior tag's buffered payload, then smart-wrap together |

### `@cont` is not `@append`

The actual parser maintains a current tag and text buffer:

- On a primary tag such as `# @rule ...`, it flushes the previous tag and
  starts the new tagged payload in a buffer.
- On `# @append ...`, it **does not flush**. It appends a space and this text
  to the existing buffered payload. The combined text is emitted and
  automatically smart-wrapped as **one tag entry**.
- On `# @cont ...`, it **flushes the buffer first**, then prints this text
  immediately on a **separate, aligned, continuation line**, without a
  repeated tag label. It thus enforces a deliberate displayed line break.

Example:

```bash
# @rule a long logical requirement whose sentence continues
# @append without requesting a forced line break in generated output
# @cont a distinct aligned line intentionally separated from the rule
```

The first two lines become one smart-wrapped `rules:` entry; the `@cont`
text appears beneath it on a new aligned line. Neither tag introduces an
independent new category. Do not use `@cont` merely because the source comment
line was too long; use `@append` for that case. Don't presume `@append` after
an already-flushed `@cont` behaves like continuation of its printed line;
write normal primary-tag / append / cont sequences.

The parser's display implementation and its prose may not agree in every
edge case. Check extraction on representative files rather than inventing
unsupported tag syntax. Avoid metadata text containing a backslash directly
followed by `U` or `u`; prefer `U+` notation, per the existing header's
formatting warning.

### Compatibility and testing caution

The current `summarize_header()` enumerates installed header files under
`JOETOO_HEADER_DIR` and uses name/glob conventions for
`script_header_joetoo*`; it is **not** a general arbitrary-path parser.
Do not claim `summarize_header -f function` can immediately read an arbitrary
`joetoo-kwin` file. A temporary, isolated fixture with the expected directory
and name convention or a separately reviewed adapter may be used for parser
compatibility tests. Do not install/copy into `/usr/sbin` or modify the real
header merely to test extraction.

When measuring compliance, distinguish metadata *parseability* from its
semantic correctness: generated text can look good while describing the code
incorrectly.

## Python conventions

Use module docstrings for responsibilities and boundaries, and idiomatic
function/class docstrings for parameters, return values, exceptions and side
effects. Explain subprocess lifetime, safe filesystem/persistence boundaries,
state changes and error classifications inline when needed. Map these
information categories conceptually to Joetoo tags but do not insert
shell-style post-function tag blocks in Python or claim that the current
`summarize_header` parses docstrings. A Python adapter is separate work.

## JavaScript conventions

Use file/module purpose comments and JSDoc where useful for arguments,
returns, promises/callbacks, events, KWin APIs, state, subscriptions and
cleanup. Explain positive window identity and safety invariants adjacent to
enforcement points. Do not claim current `summarize_header` parses JSDoc;
future extraction/adapters are separately authorized work.

## C++ conventions — mandatory maintainability audit

Include every curated C++ implementation and header in the **same mandatory
source-maintainability audit** as Bash, Python and JavaScript. For joetoo-kwin,
derive the current inventory from `MANIFEST`, including
`native/managed-close/adapter.cpp`, `native/managed-close/x11.cpp`, and
`native/managed-close/channel.h`. Review related `CMakeLists.txt` build
comments and installation assumptions. Review `metadata.json` separately
for accuracy/provenance, not as C++ function source.

- Write concise file-level purpose, boundaries, version-sensitive KWin/Qt/X11
  dependencies and relevant build/ABI assumptions.
- Use consistent, Doxygen-compatible `///` or `/** ... */` contracts for
  nontrivial public functions/classes/APIs: parameters, returns, failures,
  ownership/lifetime, requirements and side effects. Document internal helpers
  proportionately; avoid narrating trivial code.
- Explain non-obvious C++ and Qt semantics at their use sites: state and
  cleanup, event-loop or signal/slot assumptions, thread-affinity when
  relevant, X11/XWayland protocol behavior and order-dependent operations.
- Adopt Joetoo's **information categories** without copying Bash `# @tag`
  syntax into C++. The current `summarize_header()` does not parse Doxygen.
- Do not change signatures, ABI, build policy, source behavior or conditional
  compilation under the guise of commenting. Copyright/SPDX provenance remains
  a parallel release audit, not an exclusion from maintainability review.
- Validate via diff and relevant native build/syntax tests when the required
  environment exists; disclose unavailable build validation.

## Audit workflow

1. **Inventory:** derive in-scope production Bash/shell, OpenRC/eselect,
   Python, JS, C++ implementations and headers from the current curated
   source manifest. Include CMake in the related explanatory review; review
   configs/examples and licensing provenance separately. Do not omit imported
   or non-executable source modules.
2. **Inspect:** read the full source and relevant callers, implementations,
   return paths, globals, and actual safety enforcement.
3. **Assess:** identify missing contracts, stale assertions, opaque constructs,
   misleading documentation, security implications, and overcommenting.
   Record functional discrepancies separately.
4. **Draft:** prepare small reviewable batches. Bash may require declaration
   formatting for parser compatibility; make such syntax edits explicit.
   Avoid behavior changes, interface changes and speculative refactors.
5. **Validate:** inspect a complete diff; run `bash -n` for shell, appropriate
   ShellCheck using Joetoo stubs, Python syntax/AST and focused unittests,
   `node --check` and relevant JS tests, plus relevant C++/CMake build or
   syntax checks when available. For metadata, test actual extraction
   in a safe fixture where feasible. Check `git diff --check` and, if useful,
   full regression suites. Do not claim static checks prove equivalence.
6. **Review:** present findings, patch, exact validation evidence, unresolved
   ambiguities, and proposed ledger disposition; obtain maintainer approval
   before updating an accepted status.

For the Step 1.9 audit, maintain a ledger under `task_1.9/` with each file's
status: `PENDING`, `INSPECTED`, `DRAFTED`, `VALIDATED`, `ACCEPTED`, or `BLOCKED`.
Include reviewed revision and any separately scoped functional issues.

## Safety and review gates

- Preserve accepted KWin identity/ownership, non-destructive broker restart,
  distinct local placement versus remote usability, private persistence and
  credential boundaries. Explain actual enforcement, not just requirements.
- Distinguish operation exit status from `handle_result`/presentation status;
  ordinary nonzero exit codes are not a universal cross-function enumeration.
- Do not use unscoped `umask 077` snippets. For private file creation use an
  explicitly scoped subshell, or a local file mode such as `install -m 600`
  when appropriate; do not change the user's interactive shell defaults.
- Do not transfer sources, run `tarup`, create an ebuild, publish or modify
  protected repositories as a consequence of completing comments.
- Avoid new metadata tags unless existing `@req`, `@rule`, `@ret`, `@vars`,
  `@note`, and `@warn` are demonstrably insufficient; propose any extension
  and its parser/test implications separately.

## Required batch deliverables

1. Audited files/functions and concise deficiency assessment.
2. Function metadata coverage and exact `@cont`/`@append` usage rationale.
3. Complete patch/diff, with any Bash opening-layout changes identified.
4. Syntax/static/parser/focused test results and their limitations.
5. Verified functional findings kept separate from documentation work.
6. Audit-ledger status proposal and remaining blockers.

Finish only when all in-scope interpreted and C++ production sources have
been reviewed and accepted; completing this audit does not certify the source transfer,
license provenance, tarball, installed image or native acceptance.
