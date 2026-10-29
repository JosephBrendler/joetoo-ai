---
name: joetoo-announce-act-report
description: Use announce–act–report idioms in development, review, and debug of joetoo shell scripts. Understand how to employ j_msg, handle_result, right_status, and decode_right_status from script_header_joetoo in forming the short and more rigorous variants of these idioms. Use when adding visible progress reporting, status indicators, reliable error handling, or set -e-safe command execution to scripts sourcing the joetoo header.
---

# Joetoo announce–act–report

## Purpose

Make script execution understandable to its human operator: announce what is about to happen, perform the operation, report its result immediately, and apply an explicit failure policy. Prefer the facilities already provided by `script_header_joetoo` over ad-hoc `echo`, manual ANSI cursor movement, and duplicated status-printing functions.

This skill complements the `script-header-joetoo` and `pseudo-boolean-framework` skills. It does not replace the actual header's function contracts.

## Sources of authority and inspection

1. Read the **actual installed or source-tree** version of `script_header_joetoo` relevant to the target program, plus applicable project `AGENTS.md` and repository policy. Do not presume that a transcript represents the latest version.
2. Consult `summarize_header -f j_msg`, `summarize_header -f handle_result`, `summarize_header -f right_status`, and `summarize_header -f decode_right_status` where available. Use `j_msg -h` for its public switches.
3. Inspect real uses in `joetoo_cli_example` (simple idiom) and `joetoolkit/tmux-workflow` (`cmd_attach`, rigorous idiom) if available.
4. Confirm positional arguments and the bitmask definitions **from the selected header revision** before interpreting anything beyond the documented action-failed bit. Do not invent a bit layout.
5. Read and run ./demonstration.sh - understand its forms
- Run this script with cmdline override prefix to exercise severity/verbosity<br>
- ( either DEBUG=$TRUE  or verbosity=$iinfo or verbosity=$debug )<br>
6. `demonstrate_header` shows how to create or alter logs/status files and ask to change ownership: inspect effects before running. Do not run test/demo commands merely to document their output.

## Core concepts — never conflate these values

- **Action status** (`action_rc`): the shell exit status of the action being supervised, captured immediately and faithfully. `0` means command success. Nonzero may have command-specific meanings.
- **Reporting status** (`report_rc`): the return status of `handle_result`, potentially a composite bitmask incorporating the action's failure and reporting-system faults. This is **not necessarily the same integer** as `action_rc`.
- **Application policy**: what the caller does after both statuses are known: continue, flag, retry, return, or call `die`. The reporting helper does not substitute for application policy.
- **Pseudo-boolean flag**: use the joetoo `TRUE`/`FALSE` framework when tracking an accumulated problem; do not store an arbitrary exit code into a pseudo-boolean.

Treat `right_status` as the right-margin result indicator and `handle_result` as the convenience interface that chooses a result message and delegates status reporting. `decode_right_status` is for diagnostics of a captured nonzero reporting bitmask. Verify exact behavior and argument order in source.

## Choose the idiom deliberately

### A. Concise announce → act → report

Use for straightforward operations when an immediate `handle_result "$?"` really captures the action's exit status and no intervening operation can overwrite it. In scripts using `set -e`, use the guarded form in section B instead.

```bash
j_msg "-${info}" -nm "initializing starting_step"
starting_step=1
handle_result "$?" "$starting_step" '' "$info" || _ics_FLAGGED="$TRUE"
```

For context, this example follows the user's `joetoo_cli_example` idiom. **A plain variable assignment without command substitution or other failure-producing expansion ordinarily returns zero.** Thus this pattern reports the assignment's shell success, *not* that `starting_step` is a valid value. When the substantive operation can fail, capture/report that operation instead.

The `||` guard ensures a nonzero `handle_result` status can be handled without triggering `errexit`, but it does not preserve the numeric reporting bitmask. If its detail matters, use B.

### B. Rigorous announce → act → capture → decode → report → apply policy

Use whenever the action may fail, scripts run with `set -e`, recovery needs the original exit status, or reporting failures must be distinguished from action failures.

```bash
# Sketch: replace perform_action with the actual operation.
j_msg "-${notice}" -pn "Performing operation ..."

if perform_action; then
    action_rc=0
else
    action_rc=$?              # original action status, NOT inverted by `!`
fi

if handle_result "$action_rc" "completed" "operation failed"; then
    report_rc=0
else
    report_rc=$?              # preserve handle_result bitmask
fi

if [ "$report_rc" -ne 0 ]; then
    # The action-failure indicator is bit 0 in the cited tmux-workflow idiom.
    # Verify against the currently selected header version.
    if [ "$(( report_rc & ~1 ))" -ne 0 ]; then
        j_msg "-${err}" -p "Result-reporting failure; status [$report_rc]"
        if command -v decode_right_status >/dev/null 2>&1; then
            decode_right_status "$report_rc"
        fi
    fi
fi

# Policy should consider the *original* action status, even if report_rc
# is unexpectedly zero. Customize whether to return/continue/retry/die.
if [ "$action_rc" -ne 0 ]; then
    die "operation failed with exit status [$action_rc]"
fi
if [ "$report_rc" -ne 0 ]; then
    die "result reporting failed with status [$report_rc]"
fi
```

This is a **template**, not a drop-in change to an existing script. Verify `die` control flow in the calling context and the header's exact `handle_result` semantics. When reporting status is nonzero because the supervised action failed (bit 0 only), avoid falsely describing this as an independent reporting-system failure.

## `set -e` / `errexit` rules

- Use `if command; then action_rc=0; else action_rc=$?; fi` so a failing command can be captured and examined under `set -e`.
- Never write `if ! command; then action_rc=$?; fi` to preserve a failed command's original status: `!` negates the test, and `$?` in that branch usually becomes `0`.
- Capture `$?` immediately after the action or reporting helper, before logging, assignments containing command substitutions, checks, or other commands overwrite it.
- Use a guarded `if handle_result ...; then ... else report_rc=$?; fi` to capture composite reporting status without premature `errexit` termination.
- If supervising a pipeline, determine whether the script's `pipefail` setting and the intended pipeline/individual process statuses matter; do not claim `$?` identifies a particular stage unless established.
- `set -e` has context-dependent behavior for functions, conditional lists, and subshells. A guarded function invocation can change how `errexit` behaves *inside* that function. Do not present the guards above as a substitute for testing the actual function's internal error handling.

## Output design guidelines

- Announce **before** the action. Keep the announcement concise and meaningful to the operator.
- Use an open line (`j_msg ... -n`) only when the companion result is expected to finish that line; inspect `j_msg` newline/prefix options rather than guessing them.
- Report **immediately** after the action, so the right-margin indicator refers unambiguously to the last announced operation.
- Choose severity (`info`, `notice`, `warn`, `err`, etc.) deliberately and respect configured `verbosity`, `loglevel`, `LOGGING`, `QUIET`, and `DEBUG` policy. Visibility and logging may be gated independently.
- Never emit a green/success indicator for an operation that failed simply because the reporting call itself succeeded.
- For repeated work, balance awareness and noise: group logically, show step context, and retain enough per-step detail to diagnose a failure.
- Preserve the existing script's color, emoji, indentation, and formatting conventions; rely on the header's Unicode/ASCII fallback and layout facilities.

## Rigorous policy decision matrix

| Action status | Reporting status | Required interpretation |
|---|---|---|
| `0` | `0` | Action succeeded and reporting reported no fault; continue. |
| nonzero | nonzero with action-failed bit | Action failed; apply operation-specific policy. Decode/report any *additional* status bits. |
| `0` | nonzero without action-failed bit | Action succeeded but result reporting had a problem; apply independent reporting-failure policy. |
| nonzero | `0`, or nonzero lacking expected action-failed bit | Inconsistent/unexpected; retain original action failure, investigate reporting contract, and do not mark success. |

If the action's nonzero return has domain-specific meaning (e.g. a comparison returns 1 for 'different'), classify it before invoking `handle_result` as an error; do not automatically assume every nonzero is a fatal defect.

## Code-review checklist

Before proposing a change, identify (with exact existing names and source locations):

1. What precisely is the *surveilled action*? Could it fail? Is it an assignment, command substitution, function, pipeline, or external command?
2. What does the announcement promise the user will learn? Will the result correspond to that specific action?
3. Where is the original `action_rc` captured? Can anything overwrite it? Is it guarded from `set -e`?
4. How is `handle_result` called (including success/failure text and severity arguments)? Does the selected header revision support the proposed form?
5. Where is `report_rc` captured and, where needed, decoded? Is the action-failed bit distinguished from auxiliary reporting faults?
6. Is the policy explicit, and does it preserve the caller's existing continue/retry/return/die behavior?
7. Does the implementation avoid false successes, redundant reporting, and silent drops of failures?
8. Does the patch minimize changes and preserve the real variable/function names and project style?
9. What syntax, ShellCheck, and controlled failure-path tests were actually run, and what was not tested?

## Required delivery format for AI contributions

When drafting or reviewing code, provide: (1) the action and desired reporting policy, (2) exact source location/context, (3) a minimal patch or clearly marked illustrative snippet, (4) explicit treatment of both `action_rc` and `report_rc`, (5) success/failure/auxiliary-fault tests, and (6) limitations or unverified assumptions. Do not claim a validation passed unless it ran.

Respect the target repository's AI policy. Drafting and iterating candidate code is permitted as advisory work; do not directly modify, commit, or push to `joetoo` or `joetoo-upstream` where their policy reserves integration to the human maintainer.
