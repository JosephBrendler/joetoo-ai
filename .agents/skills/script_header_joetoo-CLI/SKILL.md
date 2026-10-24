---
name: script-header-joetoo-cli
description: Design, extend, review, and test command-line interfaces for scripts sourcing script_header_joetoo. Select between the header's process_cmdline framework, local argument handlers, and an application-specific getopts parser that reuses _pc_action_verbosity for -v/-q. Apply joetoo's return-code, configuration, messaging, and compatibility conventions without inventing a second CLI framework.
---

# `script_header_joetoo` command-line interfaces

## Scope and authority

Use this skill when writing or reviewing a joetoo application's command-line options, operand processing, help text, verbosity controls, or application-specific extensions to `script_header_joetoo`.

Read the applicable repository `AGENTS.md`, AI policy, and current header **source**, not merely this document. For the governing header see `joetoo-upstream/dev-util/script_header_joetoo/script_header_joetoo`. Complementary skills: `script_header_joetoo`, `pseudo-boolean_framework`, and `announce-act-report` (actual directory names may differ from skill names).

This is guidance for candidate work and review. Do not modify, build, commit, or deploy in the protected `joetoo` or `joetoo-upstream` repositories. The human maintainer performs official integration and native testing.

## Quick choice: three legitimate integration patterns

| Pattern | Use when | Working reference |
| --- | --- | --- |
| **A. Standard `process_cmdline "$@"`** | The header's existing `-v/-q`, `-I/-N`, status/resume/sequence, help, and single-operand extension model fit the application | `dev-util/script_header_joetoo/joetoo_cli_example` |
| **B. Standard parser plus local handlers** | Additional flags should participate in `process_argument`, short-option clusters, and the header's `usage` implementation | `dev-util/script_header_joetoo/joetoo_cli_example_local.cmdline_arg_handler` or `dev-util/joetoolkit/iptools/distccmon-tui` |
| **C. Application-specific `getopts` plus selected header helpers** | The application has positional operands, a specialized subcommand grammar, or command-line semantics incompatible with the standard parser | `joetoo-base/joetoo-per-package-env/tools/test-harness` |

**Do not automatically replace an existing `getopts` parser with `process_cmdline`.** In the inspected header, `process_cmdline` treats non-option positional tokens as invalid, and `--` currently breaks out without providing an application-level remaining-arguments interface. Its local argument callback can consume *one* following operand using return code `6`; this is not a general parser for commands like `-m DESKTOP X Y [WIDTH HEIGHT]`. If a specialized interface is needed, retain a thin application parser and reuse documented header helpers.

## Minimal `-v`/`-q` integration for a custom `getopts` parser

The header's `_pc_action_verbosity()` expects a global `_pc_operator` of `+` or `-`, and a global `_pc_adjust_verbosity` string. `process_cmdline()` **already creates** that macro itself before processing arguments and unsets it afterward. Only supply the macro explicitly when calling `_pc_action_verbosity()` outside `process_cmdline()` (as `test-harness` does):

```bash
# Define once before invoking _pc_action_verbosity directly.
# The backslashes DELAY expansion until the helper's eval executes.
_pc_adjust_verbosity="verbosity=\$(( verbosity \${_pc_operator} 1 ))"

# In the calling script's existing getopts case:
case "$opt" in
    v) _pc_operator="+"; _pc_action_verbosity || return $? ;;
    q) _pc_operator="-"; _pc_action_verbosity || return $? ;;
esac
```

This fragment is **contextual**, not a complete parser. Adapt `return` to the surrounding function's actual failure policy. Do not add the macro redundantly if the application uses `process_cmdline "$@"`. Do not independently `eval` untrusted operator text: the helper performs its own `eval`, and `_pc_operator` must be assigned only the two literal signs.

The inspected helper clamps `verbosity` to **0–7**, or to **notice (5) through 7 when `INTERACTIVE` is joetoo-true**. Higher numeric severity values mean more verbose output. `-v` raises the value; `-q` lowers it; repeated flags are meaningful. `QUIET` (`-Q` in the standard parser) and `DEBUG` (`-V`) are separate pseudo-boolean controls; they are not synonyms for `-q` and `-v`. Verify the installed header's exact behavior before changing these contracts.

Example from the actual `test-harness` source: it defines the macro before `parse_cmdline`, then its `getopts` arms assign `_pc_operator` and call `_pc_action_verbosity`. The test-harness parser additionally preserves ordinary positional package arguments after `shift "$((OPTIND - 1))"`; this is a reason to retain the application-specific pattern.

## Standard parser and external local handler file

The complete `joetoo_cli_example` pattern calls `app_configure`, followed by `process_cmdline "$@"`. In the inspected header, `app_configure()` searches **`app_customization_root`** (normally `/etc/${PN}/`) for the first `*local.cmdline_arg_handler`, sources it, and discovers up to three functions:

- `handle_local_arg "$arg" "$possible_operand"`: handles whole short/long options;
- `handle_local_compound_arg "$character"`: handles one otherwise unrecognized character in a short-option cluster;
- `handle_local_usage`: appends help text when the header's `usage()` is called.

The canonical external example is named `joetoo_cli_example_local.cmdline_arg_handler`, under the example's configuration directory. For an application `${PN}`, a corresponding installation path would normally be `/etc/${PN}/${PN}_local.cmdline_arg_handler`. Confirm `app_customization_root`, the actual packaged file, and discovery behavior instead of assuming the filename alone causes sourcing. The searched directory's filesystem actions and other `app_configure` side effects must be reviewed before invocation.

### Return status contract

| Status | Meaning in the inspected header |
| --- | --- |
| `0` | Handled successfully; did not consume the next operand |
| `6` | Handled successfully and consumed the next operand; caller shifts twice |
| `7` | Not recognized; permit fallback (or report unknown option) |
| `1` | Processing error |

An unknown option is **not automatically an error within** `handle_local_arg`: return `7` so `process_argument()` may attempt `process_compound_arg()`. For recognized flags that need an operand, validate `$2` *before* returning `6`; a successful assignment of an empty string is not evidence that the operand was present. Do not use `7` for an ordinary command failure.

Minimal external module skeleton (illustrative; add only the options the application needs):

```sh
handle_local_arg() {
    hla_ret=0
    _hla_arg=$1
    _hla_operand=$2
    case $_hla_arg in
        -o|--open) OPEN=$TRUE ;;
        -f|--file)
            if [ -n "$_hla_operand" ]; then
                config=$_hla_operand
                hla_ret=6
            else
                j_msg "-${err}" -p "missing operand for $_hla_arg"
                hla_ret=1
            fi
            ;;
        *) hla_ret=7 ;;
    esac
    unset -v _hla_arg _hla_operand
    return "$hla_ret"
}

handle_local_compound_arg() {
    hlca_ret=0
    case "$1" in
        o) OPEN=$TRUE ;;
        *) hlca_ret=7 ;;
    esac
    return "$hlca_ret"
}

handle_local_usage() {
    j_msg "-${notice}" -m '  -o | --open ......: open configured windows'
    j_msg "-${notice}" -m '  -f | --file PATH .: select configuration'
}
```

`OPEN=$TRUE` is an example of the joetoo pseudo-boolean convention and presumes that the application has sourced the header and initialized the application flag. The `-f` option consumes an operand only in the **whole-argument** handler; clustered operand-taking options need explicit additional design and tests. The header's parser uses global state; in Bash-specific applications, still follow established application naming and variable-scope conventions.

## Inline local handlers

An alternative is to define `handle_local_arg`, `handle_local_compound_arg`, and `handle_local_usage` directly in the calling script **before** `process_cmdline "$@"`. The actual `dev-util/joetoolkit/iptools/distccmon-tui` implements this pattern and calls the header's parser without using `run_sequence`. It also sets several `app_configure`-related variables itself; **those placeholders belong to that caller and are not universal requirements for every joetoo CLI**.

Do not source an external handler file and redefine the same functions inline unless overriding is deliberate and documented. If using `app_configure`, inspect when it sources its module relative to inline definitions, as well as when it initializes variables from `varlist`.

## Integrating with `app_configure` safely

The inspected `joetoo_cli_example` calls `app_configure` before `process_cmdline`. `app_configure` does much more than parse options: it initializes and loads variables, reads configuration, validates directories and a status file, and can initialize a workflow command sequence. It may perform filesystem operations. It is **optional** for a focused, non-stateful script if these side effects are unnecessary.

If adding names to `varlist`, note the documented example's warning: values initialized before `app_configure` may be reset by its initialization step. Assign such values at the appropriate point, or put their definitions in the application configuration that is sourced afterward. Do not duplicate its initializations without inspecting current behavior.

`usage()` in the header is not a simple printer: it calls `leave()` and may terminate execution. Review control flow before calling it inside a function that expects to return to its caller.

## CLI consistency and compatibility review

1. Inventory existing flags, aliases, positional arguments, and installed shell functions; distinguish an interactive alias/function such as `mw` from the underlying executable interface.
2. Reserve header-standard flags intentionally: `-v/-q` adjust verbosity, `-V/-Q` control debugging/silence, `-h` requests help, and other options such as `-I/-N/-r/-s` have established meanings **when using the standard parser**. Check conflicts before choosing application flags.
3. Separate *action selection* (`-o` open, `-x` close, `-m` move) from *argument processing* (`-f` config, `-v/-q` verbosity); reject conflicting actions deliberately.
4. Preserve requested optional-operand semantics. For example, `-m DESKTOP X Y [WIDTH HEIGHT]` requires either three or five operands; leaving dimensions unchanged must be implemented and tested by the actual window-management protocol, not simulated with guessed dimensions.
5. Use `j_msg`, `separator`, and established joetoo colors/formatting for help, configuration, and plan output; preserve screen-versus-log output behavior and avoid indiscriminate ANSI output to non-terminals.
6. Use command exit status to communicate failures; keep it separate from pseudo-boolean flags and from `handle_result` reporting status.
7. Validate `-v`, `-q`, `-vv`, `-qq`, `-v -q`, upper/lower clamp boundaries, both pseudo-boolean interactive states, clustered local flags, operand omission, unknown flags, and `--` where applicable. Check precedence between configuration defaults and command-line overrides.
8. Run `bash -n`, ShellCheck when installed, and focused non-destructive parser tests. Do not claim that tests, shell compatibility, or header versions have been verified without evidence.

## Inspected source references

These source paths were inspected in `JosephBrendler/joetoo-upstream` on 2026-10-24 (read-only); re-fetch them for future assignments:

- [`dev-util/script_header_joetoo/script_header_joetoo`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/script_header_joetoo/script_header_joetoo): `app_configure`, `usage`, `process_cmdline`, `_pc_action_verbosity`, `process_argument`, `process_compound_arg`.
- [`dev-util/script_header_joetoo/joetoo_cli_example`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/script_header_joetoo/joetoo_cli_example) and [`joetoo_cli_example_local.cmdline_arg_handler`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/script_header_joetoo/joetoo_cli_example_local.cmdline_arg_handler): external-handler pattern, statuses, configuration order.
- [`dev-util/joetoolkit/iptools/distccmon-tui`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/joetoolkit/iptools/distccmon-tui): inline handlers and direct use of `process_cmdline` without workflow sequencing.
- [`joetoo-base/joetoo-per-package-env/tools/test-harness`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/joetoo-base/joetoo-per-package-env/tools/test-harness): custom `getopts` with the `_pc_adjust_verbosity` bridge; preserves positional operands.

For fuller messaging semantics refer to the `script-header-joetoo` and `announce-act-report` skills instead of copying their contents into this CLI-specific skill.
