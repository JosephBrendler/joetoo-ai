---
name: script-header-joetoo
description: Use when drafting, reviewing, debugging, or explaining joetoo shell scripts that source /usr/sbin/script_header_joetoo. Discover and correctly reuse its existing functions, globals, messaging, terminal UI, validation, configuration, CLI, and command-sequencing facilities instead of reinventing them.
---

# Work effectively with `script_header_joetoo`

## Purpose and scope

`script_header_joetoo` is a reusable joetoo shell framework, not merely a collection of colors and `echo` helpers. It supplies foundations and Unicode/terminal assets; predicates and utility functions; a policy-driven UI/messaging/logging engine; and optional application configuration, CLI parsing, and resumable command sequencing.

Use this skill whenever proposing or analyzing code that sources this header, including `joetoolkit` programs, joetoo system-building tools, and CLI applications. Work from the *specific checked-out or installed version* of the header, not from assumptions based on generic Bash libraries or this inventory alone. This skill does not make every header facility mandatory for a small program.

## Authority and permitted contribution

- The applicable repository `AGENTS.md`, AI policy, and the human maintainer's specific instructions take precedence.
- AI may substantially assist by analyzing, drafting, iterating, reviewing, and preparing source text or patches for human evaluation.
- Do not directly edit, commit, push, release, or deploy to protected `joetoo` or `joetoo-upstream` repositories unless their governing policy expressly permits the particular action. Human incorporation of AI-assisted drafts is expected.
- Do not execute operations that alter host state merely to inspect a header function. Obtain permission for operational or destructive tests.

## First: discover, then design

1. Identify the target program, interpreter (`#!/bin/bash`, `#!/bin/sh`, etc.), header location, installed/package version, and relevant surrounding source. **Sourcing ignores the sourced file's shebang**; the caller's shell interprets its contents. Do not infer that a function described as POSIX makes the complete application POSIX-compatible.
2. Read the target script's initialization, functions, globals, and callers. Identify existing header functions already used, naming and formatting conventions, and whether a local function intentionally overrides a default.
3. Inspect the real header and its modules, if available. On a host with the tools installed, prefer:

   ```sh
   summarize_header -q                 # concise function inventory
   summarize_header -f j_msg           # detailed function contract
   summarize_header -f process_cmdline
   summarize_header -f run_sequence
   summarize_header -h                 # discovery interface
   j_msg -h                            # message option syntax
   ```

   `summarize_header` metadata is a discovery aid, not infallible proof of current behavior. For nontrivial changes, examine the actual function and relevant caller source. Do not assume a `-f` synopsis exposes every important side effect or option.
4. Use `demonstrate_header` and `joetoo_cli_example` / `joetoo_cli_example_mini` as functional examples when their run conditions are safe. Check `--help` or `-h` first. The demonstration may initialize logs, prompt for ownership changes, create status files, and exercise terminal state. Do not run it unattended or with elevated privileges by default.
5. Select the **smallest appropriate existing capability**. Do not invent custom equivalents without identifying why the supplied function is insufficient.
6. If the source or metadata is unavailable, distinguish established facts from unverified assumptions. Provide an inspection command or clearly marked candidate draft rather than fabricate a function signature.

## Standard integration pattern

A commonly used joetoolkit Bash program begins:

```bash
#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later

source /usr/sbin/script_header_joetoo

PN=${0##*/}
if [ -f /etc/joetoolkit/BUILD ]; then
    . /etc/joetoolkit/BUILD
else
    BUILD="0.0.1"
fi
[ -z "$verbosity" ] && verbosity="${notice}"
```

This is an **example of an existing convention**, not an instruction to insert this boilerplate blindly into all scripts. Preserve the individual program's current initialization, package version source, privilege checks, and verbosity policy. The header defines numerous globals and functions; avoid collision with those names. Do not introduce variables that cannot be identified in the inspected source or the proposed patch.

## Capability routing: what to reuse

| Need | Start with | Engineering guidance |
| --- | --- | --- |
| Severity-aware terminal output and optional logs | `j_msg`, `get_severity` | Prefer `j_msg` to ad hoc `echo`/`printf` formatting for conventional joetoo user messages. Inspect its policies before changing message options. |
| Announce/action/status-line idiom | `j_msg -n`, `right_status`, `handle_result`, `separator` | Preserve the relevant command's exit status *immediately*; don't let an intervening command replace `$?`. |
| Lower-level output policy | `emit`, `_parse_msg_options`, `_view_mask` | Prefer `j_msg` for ordinary callers. Treat `emit` bitmask design as advanced/internal and inspect named constants before use. |
| Logging and diagnostics | `loggit`, `debug_marker`, `d_do` | Understand `verbosity`, `loglevel`, `logFile`, `DEBUG`, `QUIET`, `LOGGING`, `INTERACTIVE` independently. `d_do` executes code; inspect its evaluation and quoting semantics before proposing it for untrusted input. |
| Pseudo-boolean and status formatting | `TrueFalse`, `status_color`, `initialize_vars`, `display_vars`, `show_config` | Follow the separate `pseudo-boolean-framework` skill and verify return/output conventions. Do not confuse shell return status with pseudo-boolean representation. |
| Numeric/address/timestamp validation | `isint`, `ishexint`, `isfloat_posix`, `isnumeric`, `isipv4`, `isipv6`, `is_valid_timestamp` | Prefer predicates in conditional position; verify accepted edge cases before replacing them with regexes. |
| Environment checks | `isroot`, `checkroot`, `checknotroot`, `checkboot`, `checkshell` | Distinguish silent predicate `isroot` from gatekeepers that may exit; inspect `checkboot`'s bitmask return. |
| Versions, bases, time | `vercomp`, `show_result`, `b2d`/`d2h` and related converters, `millis2time`, `secs2time`, `timestamp` | `vercomp`: 0 equal, 1 greater, 2 less; these are *comparison results*, not an ordinary success/failure predicate. Inspect dependencies (e.g., `bc` for base conversion). |
| Width-aware formatting and wrapping | `get_msg_len`, `utf8_string_width`, `get_longest`, `repeat`, `full_repeat`, `pad`, `smart_wrap_n`, `strip_ansi` | Use display-column width rather than byte length for colored/Unicode output. `smart_wrap_n` requires correct start column and margins. |
| Terminal graphics and controls | `termwidth`, `termheight`, `SCP`, `RCP`, `HCU`, `SCU`, `CUP`, `CUF`, `CUB`, `EL`, `CLR`, `vt_init`, `box_shift`, `box_esca`, `box_msg`, `u_box_msg`, `progress_inline` | Restore cursor visibility/state on failures and signals when needed; do not send control sequences into ordinary logs or nonterminal output without checking policy. |
| Unicode and colors | `emoji_safe`, `u_echo`, `idx_of_emoji`, `name_of_emoji`, `color`, `RGB_FG`, `RGB_BG`, `is_utf8_terminal` | Reuse curated registries and precooked `bin_*` assets; honor Unicode capability/disable policy. Don't hard-code registry indices when a named index is available. |
| Application setup and CLI | `app_configure`, `usage`, `process_cmdline`, `process_argument`, `process_compound_arg`, `show_config` | Discover built-in options and local customization handlers before implementing an additional parser. Avoid assuming universal behavior across applications. |
| Stateful workflows | `run_sequence`, `_pc_action_status`, `_pc_action_resume`, `_pc_action_number`, `register_cleanup_hook` | Inspect status-file semantics, resume behavior, step numbering, cleanup responsibilities, and idempotence; avoid introducing unintended step re-execution. |
| Filesystem and privileged operations | `safe_fs_op`, `safe_sudo_fs_op`, `validate_dir`, `validate_file`, `validate_root_file`, `validate_logfile`, `fix_logfile`, `wipe_device`, `unlock_luks_devices` | High risk: inspect actual implementation and guardrails; never assume a `safe_*` name makes a proposed operation safe. Avoid executing in an AI session. |
| Interaction, remote, and network | `yn_prompt`, `yns_prompt`, `confirm_continue_or_exit`, `ask_pass`, `pur`, `ssh_wrapper`, `swr` | Respect interactive/noninteractive policy, terminal handling, SSH security and retries. Avoid prompts during unattended tests. |

Do not import this table as a complete public API specification; it is a navigation index. Leading-underscore functions are normally implementation details unless inspected source shows otherwise.

## Messaging model: important distinctions

The `j_msg` entry point implements RFC-5424-style severities, with values **0 through 7**: `emerg`, `alert`, `crit`, `err`, `warn`, `notice`, `info`, and `debug`. Larger values are less severe. Example calls from the demonstration:

```bash
j_msg -5 -p "Preparing operation"
j_msg -3 "A failure occurred"
j_msg -5 -p -M "$idx_hammer" "Running a task"
j_msg -7 -m "Diagnostic detail"
DEBUG="$TRUE" j_msg -7 -p "Temporary forced diagnostic"
```

Inspect `j_msg -h` for the current exact modifiers. Observed modifiers include severity `-0`..`-7`; emoji `-M index` and `-m`; prefix `-p`/`-P`; newline `-n`/`-N`; timestamps `-t`/`-T`; color `-C`/`-c`; bold `-B`/`-b`; escape interpretation `-e`/`-E`; and unconditional `-u`. Several option pairs use **lowercase to suppress and uppercase to force**. `-e`/`-E` is a documented exception; verify each case. Do not assume concatenated or reordered options are equivalent without checking the parser.

`j_msg` routes through `emit`, which controls terminal emission and logfile emission **independently**. `verbosity` controls conditional screen output; `loglevel` controls conditional log output. `DEBUG` can bypass ordinary print-verbosity filtering, while `QUIET` can suppress terminal output; do not infer that either has the same effect on logfile delivery. `-u` overrides normal conditional policy. Always confirm the current precedence from source before making a change to output policy.

Logging is intended to produce timestamped, ANSI-stripped, escape-normalized text rather than dumping raw screen control sequences. `LOGGING=$TRUE` by itself is not a guarantee of successful file writes: log path, permissions, and configuration still matter. Prefer `j_msg` over calling `emit` directly unless bitmask-level control is required.

**Known demonstration limitation (2026-10-23, `demonstrate_header-1.0.10`):** tests for `-M` emoji forcing with `UNICODE_DISABLE=$TRUE` showed failed *expected-byte checks*, even though their containing demonstration step reported success. Treat this interaction as unverified/possibly defective, not as a guaranteed API contract. Separately identify individual assertions and overall test status.

## UI and status reporting

A common joetoo idiom is announce → execute/test → report. When using `right_status`, preserve the command result before other operations alter `$?`:

```bash
j_msg -5 -n "Checking input ... "
isint "$candidate"
result=$?
right_status "$result"
```

Confirm whether `right_status` itself changes return status or formatting in the installed version before building control flow around it. For simple cases, `handle_result "$result" "success description" "failure description"` may perform the status reporting; inspect its actual argument and return-value contract first.

Before constructing manual padding, cursor motion, emoji, fixed-width tables or multiline boxes, evaluate `pad`, `get_msg_len`, `smart_wrap_n`, `u_box_msg`, `separator`, and related header facilities. Distinguish terminal columns, Unicode display cells, ANSI escape bytes, and log text. For multi-step transient graphics, plan terminal restoration.

## CLI and command sequencing

The header provides a configurable CLI framework and two illustrative executables: `joetoo_cli_example` (with `run_sequence`) and `joetoo_cli_example_mini` (simpler linear action). Use their source and `-h` output to learn wiring, not as unconditional boilerplate.

Observed standard options in the example include `-h`, `-I`/`-N` (supervised/noninteractive), `-s` (status), `-r` (resume), `-l` (logging), `-v`/`-q` (verbosity), and `-V`/`-Q` (debug/quiet). Numbered step selection, grouped short options, operand-taking options, and locally defined flags require actual parser inspection. Do not claim all examples or client programs expose the same supported switches. Inspect local configuration handlers (`handle_local_arg`, `handle_local_compound_arg`, `handle_local_usage`) and files under the application's config directory.

Before proposing `run_sequence` changes, locate the source of `cmd_seq_file`, `status_file`, `starting_step`, `stopping_step`, `num_cmds`, and step implementation; reason explicitly about interrupted operations, re-entry, and return-status propagation. Preserve the application's existing resume contract.

## Validation and review workflow

For every requested source change or review:

1. **Scope:** State the requested outcome, target file/function, and change boundary.
2. **Inventory:** Identify relevant already-available header functions and metadata; cite exact observed names and signatures.
3. **Design:** Explain why each chosen helper fits; distinguish POSIX-described helpers from Bash-specific calling code.
4. **Draft:** Produce a minimal, source-grounded proposed change with exact location/diff; preserve current variables, naming, API, flow, header initialization, and pseudo-boolean policy.
5. **Check:** Where authorized and possible, perform `bash -n` (for Bash scripts), ShellCheck (when present), and targeted *non-destructive* tests. Do not interpret `demonstrate_header`'s aggregate success as proof every subtest passed.
6. **Report:** Distinguish observed behavior, test output, untested assertions, potential side effects, and questions needing human confirmation.

Do not silently convert a script to another shell, replace `j_msg` with generic print utilities, invent missing variables/helpers, equate loglevel with verbosity, treat `vercomp` result `1`/`2` as errors, or assume that source-label descriptions like `(POSIX)` prove the whole header is POSIX-only.

## Further authoritative resources

- Installed header: `/usr/sbin/script_header_joetoo` and any sourced companion modules.
- Development source: `joetoo-upstream/dev-util/script_header_joetoo/` (confirm exact current files and module composition).
- Installed discovery: `summarize_header -q`, `summarize_header -f FUNCTION`.
- Installed functional orientation: `demonstrate_header`, `joetoo_cli_example -h`, `joetoo_cli_example_mini -h`.
- Related joetoo skill: `pseudo-boolean-framework` (directory may presently use `pseudo-boolean_framework`).

The source and test runner available on the target system are authoritative over this skill's examples and function inventory if versions differ.
