---
name: pseudo-boolean-framework
description: Apply and review joetoo's pseudo-boolean convention in shell scripts that use script_header_joetoo. This may be used when drafting, modifying, reviewing, or debugging joetoo shell scripts involving flag assignments, truth tests, state transitions, or related output. Do not impose it on unrelated shell projects.
---

# Joetoo pseudo-boolean framework

## Purpose and scope

Use the joetoo pseudo-boolean convention to provide a visually clear logical boolean variable capability in shell environments that otherwise lack a boolean data type, thus allowing the variable's content to be understood as a representation of logical truth rather than string or numerical value.  Follow the existing joetoo convention for **state flags** in shell code that sources `script_header_joetoo`. This skill guides analysis and proposed code; it does not authorize editing, testing, committing, or pushing any repository. Observe the repository's `AGENTS.md` and applicable AI policy, and the user's explicit authorization.

The framework uses **string presence**, to represent truth, not numeric value:

```bash
TRUE=0
FALSE=""
```

These are the framework's established fundamental values, supplied by `script_header_joetoo` in the intended environment. Do **not** redefine them in a script that already sources that header. Do not silently substitute `true`/`false`, `1`/`0`, integer comparisons, or command exit statuses for a pseudo-boolean flag.

## Core invariant rules

1. Assign a pseudo-boolean flag **only** `$TRUE` or `$FALSE`
2. Use conspicuous uppercase names (for example, `NEED_UPDATE`).
3. Evaluate the logical truth of a pseudo-boolean variable by testing it with shell test, [, [[ or direct string comparison -- this tests a flag by its **string non-emptiness**, e.g. [ "$NEED_UPDATE" ]` or, in Bash, `[[ $NEED_UPDATE ]]`.
4. Negate a flag with `[ ! "$NEED_UPDATE" ]` or `[[ ! $NEED_UPDATE ]]`.
5. Use `case` when matching the two canonical values explicitly, with quoted patterns.
6. Do **not** execute the value as a command (`if "$NEED_UPDATE"; then ...`) or treat it as arithmetic (`(( NEED_UPDATE ))`).
7. Keep pseudo-boolean state, numeric/bitmask data, and command exit status separate. Explicitly convert between domains only after determining the intended semantics.
8. Preserve existing joetoo APIs and naming conventions when reviewing or proposing changes. Do not introduce an alternative boolean abstraction unless requested.

## Recommended idioms

```bash
NEED_UPDATE=$FALSE

if [ "$NEED_UPDATE" ]; then
    printf '%s\n' 'update required'
fi

[ ! "$NEED_UPDATE" ] && printf '%s\n' 'no update required'

# Bash-specific form:
if [[ $NEED_UPDATE ]]; then
    printf '%s\n' 'update required'
fi

case "$NEED_UPDATE" in
    "$TRUE")  printf '%s\n' 'true' ;;
    "$FALSE") printf '%s\n' 'false' ;;
esac

right_status $? "$notice" || FLAGGED=$TRUE
```

When a command's success or failure determines a flag, test the **command**, then assign the canonical value:

```bash
if some_command; then
    COMMAND_SUCCEEDED=$TRUE
else
    COMMAND_SUCCEEDED=$FALSE
fi
```

Do not assign `$?` directly to a pseudo-boolean variable. Do not assume that the numeric string `1` is false: `[ "1" ]` succeeds because it is nonempty. A numeric string `0` is also nonempty, but is canonical **true** only because joetoo defines `TRUE=0`.

## How evaluation works

- `[ "$FLAG" ]` (the one-argument `test` form) succeeds for a nonempty string and fails for an empty string. Its command exit status is a separate quantity.
- Bash `[[ $FLAG ]]` likewise evaluates the string as nonempty/empty. `[[ ... ]]` is Bash-specific, while `[ ... ]` can be used in POSIX shell.
- `if` branches on the exit status of the command or compound command it executes; it does not interpret a variable's contents as a boolean data type.
- `case "$FLAG" in ... esac` matches string patterns; it does not use the command-status mechanism to select a branch.
- Quoted parameter expansions are the default in `[ ... ]` tests. Unquoted expansions may undergo field splitting and pathname expansion; do not rely on their accidental behavior, especially in negation or multi-argument tests.

## Distinguish three domains

| Domain | Typical representation | Appropriate operation |
| --- | --- | --- |
| Joetoo pseudo-boolean state | `"0"` (true), `""` (false) | `[ "$FLAG" ]`, `[[ $FLAG ]]`, `case` |
| Numeric data and bitmasks | Shell integer values | `(( ... ))`, `$(( ... ))`, numeric comparison |
| Command execution result | Exit status `0` for success, nonzero for failure | `if command; then ...`, `$?` when needed |

Shell variables generally store strings; shell arithmetic interprets values numerically when requested. Avoid describing a numeric shell variable as an actual native boolean type.

## Existing joetoo helper functions

- `TrueFalse()` is a joetoo **display/interpretation helper**, not the definition of the pseudo-boolean convention. Its handling of inputs outside the canonical values is function-specific; inspect its implementation before using it to convert an external value into a framework flag.
- `status_color()` and `${Boff}` can provide colored status display where the header supplies them. They are presentation aids, not truth tests.
- The existing demonstration `demonstrate_header -2` provides illustrative, colorized cases. Treat those results as examples of the implementation, not a universal string-to-boolean specification.

A pre-existing display idiom is:

```bash
j_msg "-${notice}" -p "VAR is: [$(status_color "$VAR")$(TrueFalse "$VAR")${Boff}]"
```

This form is available in any script that has sourced script_header_joetoo; verify that availability.

## Workflow for AI contributions

When a task involves joetoo pseudo-boolean logic:

1. **Inspect context.** Determine whether the script sources `script_header_joetoo`; identify all assignments, tests, and consumers of the affected flag. Do not invent missing declarations or helper behavior.
2. **Classify each value.** Is it a pseudo-boolean flag, an exit status, a numeric value/bitmask, or external input? Note boundaries where conversion is required; does it apply the "conspicuous capitalization" convention?
3. **Preserve the convention.** Draft the smallest appropriate change, using `$TRUE`/`$FALSE` for state and quoted string tests. Preserve surrounding code, names, interfaces, and behavior unless a change is explicitly requested.
4. **Check edge cases.** Consider empty, nonempty noncanonical, unset (including `set -u` implications), and external values where they can reach the flag. Canonical flags should not silently accept arbitrary values.
5. **Validate within authorization.** Where tools and permissions allow, use `bash -n`, ShellCheck, and focused tests. Otherwise state which checks are recommended but not run. Tests must verify the actual logic, not just the text of generated output.
6. **Report precisely.** Identify the affected source locations, explain the semantic issue, provide a reviewable proposed diff or code excerpt, and distinguish verified observations from assumptions.

## Avoid these mistakes

```bash
# Wrong: tries to execute the string as a command
if "$NEED_UPDATE"; then :; fi

# Wrong: numeric test does not express the framework's string semantics
if [ "$NEED_UPDATE" -eq 0 ]; then :; fi

# Wrong: directly conflates command exit status and flag state
some_command
NEED_UPDATE=$?

# Wrong: creates a noncanonical flag value
NEED_UPDATE=1
```
## practial examples

# in joetoo announce, act, report idiom (flag failure as anomaly, but don't die over it)
j_msg "-${info}" -m "About to assign var with subshell output"
var=$(...)
right_status $? "$info" || FLAGGED=$TRUE

# in orchestrated interactive process
emerge_args=( --nodeps getbinpkg=y with-bdeps=y )
[ "$INTERACTIVE"] && emerge_args+=( --ask )
emerge "${emerge_args[@]}""

Do not automatically rewrite unrelated uses of `true`, `false`, `0`, or `1`: some represent command status or numeric quantities rather than joetoo state flags.
