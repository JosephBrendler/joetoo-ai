---
name: script-header-joetoo-ssh
description: Assist with designing, reviewing, and troubleshooting joetoo shell scripts that source script_header_joetoo_ssh, use its SSH-agent lifecycle helpers, and perform SSH, SCP, or rsync transfers. Apply when adapting joetoo-template ssh, using start_ssh_agent/load_key/unload_key/stop_ssh_agent, transporting data as an unprivileged user or root, or planning bootstrap SSH to a live installation environment.
---

# Joetoo SSH transport and agent lifecycle

## Purpose and boundaries

Help developers produce correct, maintainable, reviewable *draft* joetoo shell code using existing SSH facilities, rather than inventing competing SSH-agent management or transport abstractions. Preserve the caller's existing structure and conventions. The human maintainer decides which proposed changes to incorporate, execute, commit, or push into protected joetoo repositories. Do not assume that this skill authorizes changes to those repositories or remote systems.

This skill complements the `script-header-joetoo`, `pseudo-boolean-framework`, and `announce-act-report` skills when present. Follow applicable repository `AGENTS.md` and AI policies.

## Authoritative references and inspection

- Actual installed `/usr/sbin/script_header_joetoo_ssh` and `/usr/sbin/script_header_joetoo` source and metadata are authoritative for interfaces, return values, ownership, and cleanup behavior.
- Run or inspect `joetoo-template ssh` for a *copyable recipe*. It is a standalone generator that **extracts commented template text**; it does **not** source the SSH header to print the template. Template functions are alternatives, not automatically invoked.
- Inspect actual callers before recommending changes: `dev-util/joetoolkit/iptools/get_remote_ip_addresses`, `dev-sbc/collect-layout-data`, `dev-sbc/collect-system-files/collect-system-files` (`transfer_results`), and `dev-build/joetoobuild-tools/rsync_to_chroot` are referenced by the supplied template. Their current content and behavior must be verified, not assumed.
- Identify the header/package version and installed tool availability. If sources are inaccessible, say so and treat the template as illustrative, not a verified complete API contract.
- `summarize_header -q` and `summarize_header -f FUNCTION` may help inspect metadata if the installed version exposes the SSH module; verify discovery rather than assuming it.

## Workflow for an AI contributor

1. **Classify the operation**: remote command, SCP collection, unprivileged rsync, privileged file transfer through remote sudo, temporary live-media bootstrap, or local user switching via `runuser`.
2. **Determine identity and privileges independently**: local script UID; local account owning private key; agent/socket owner; SSH remote login account; remote filesystem privileges; destination environment.
3. **Inspect existing code and helpers**: read the relevant header functions and caller's cleanup/error conventions; do not introduce replacement agents or lifecycle code without demonstrating a gap.
4. **State prerequisites**: available `sudo`/`runuser`, `ssh`/`scp`/`rsync`/`sshpass`, installed keys, agent access, server trust, remote sudo restrictions, directory permissions, and expected hosts.
5. **Choose exactly one transport pattern** appropriate to the operation, adapt variables deliberately, and preserve argument/filename boundaries using shell quoting and arrays where the script uses Bash.
6. **Implement a reviewable draft** with an explicit failure policy. Keep operation status distinct from reporting/cleanup status. For `set -e`, capture the exit status in an `if ...; then ... else ... fi` context.
7. **Validate without unintended remote effects**: syntax/static analysis and focused tests first; inspect full command argv and source/destination semantics before proposing an actual network write. Report which runtime tests were not performed.

## Initialization and cleanup

Typical template preamble (adapt as needed, do not paste blindly):

```bash
#!/bin/bash
source /usr/sbin/script_header_joetoo
source /usr/sbin/script_header_joetoo_ssh

PN=${0##*/}
if [ -f /etc/joetoolkit/BUILD ]; then . /etc/joetoolkit/BUILD; else BUILD="0.0.1"; fi
[ -z "$verbosity" ] && verbosity="${notice}"
```

The template calls `checkroot`, but **not all SSH consumers need a root-running script**. Decide from the local privilege model before retaining it. Likewise, `start_ssh_agent "$user"` and `load_key "$user"` are for key-based template examples 1–4 and 6; password bootstrap example 5 is separate. Confirm how `SSH_KEY` is chosen by `load_key` and whether the header manages an existing agent before assuming key selection or agent ownership semantics.

```bash
start_ssh_agent "$user" || die "failed starting ssh-agent"
load_key "$user" || die "failed loading SSH key"
# ... selected operation ...
unload_key "$user" || j_msg "-${err}" "failed unloading SSH key"
stop_ssh_agent "$user" || j_msg "-${err}" "failed stopping SSH agent"
```

The template states that `die()`/`leave()` invoke registered SSH cleanup hooks. **Verify** the hook registration, execution order, and whether a helper will affect a shared/pre-existing agent in the installed implementation. Never call `die()` from a cleanup hook (recursive cleanup risk). Do not silently replace a meaningful operation failure with a later cleanup failure; report both. Explicit cleanup versus registered hooks must be coordinated to avoid double cleanup.

## Transport selection

| Situation | Pattern from `joetoo-template ssh` | Crucial distinction |
| --- | --- | --- |
| Run a remote command | `example_ssh` | Local SSH process runs as key-owning user; `SSH_AUTH_SOCK` passed explicitly |
| Copy locally matched files | `example_scp` | Fixed path quoted while `*` expands **locally**; inspect unmatched-glob behavior |
| User-level rsync | `example_rsync_user` | Both ends operate with ordinary user permissions |
| Read local root files and write remote root files | `example_rsync_root_via_sudo` | Local rsync runs as root; SSH login is `remote_user`; remote `sudo -n rsync` requires tightly controlled authorization |
| Bootstrap temporary liveUSB/liveCD destination | `example_rsync_root_via_sshpass` | Password-based root SSH on a trusted bootstrap network, with intentionally reduced host-key checking; **template variation untested** |
| Use `runuser` instead of `sudo -u` | `example_runuser` | Requires util-linux `runuser`, not a BusyBox assumption; **no verified joetoo implementation yet** |

For any option, verify which files/directories are authoritative, whether the operation is read-only, whether an absent source is an error, and whether local vs remote wildcards will expand in the intended shell.

## Credential, privilege, and trust discipline

- Never embed private keys or passwords in a repository, transcript, test fixture, or generated sample. Do not echo credentials or expose secret-bearing command lines in debug output.
- Preserve `SSH_AUTH_SOCK` when crossing local user boundaries **only** when the socket permissions and user identities make access legitimate. The template uses `sudo -u "$user" env SSH_AUTH_SOCK="$SSH_AUTH_SOCK" ...` or `runuser -u "$user" -- env ...`; do not infer these are interchangeable on every target.
- Differentiate local root permission, local agent/key identity, remote SSH login identity, and remote `sudo` privilege. They are not the same thing.
- Prefer authenticated host keys and `BatchMode=yes` for unattended key-based transfers; never suggest globally disabling host-key verification to suppress errors.
- In the live-media bootstrap exception, `StrictHostKeyChecking=no` and `UserKnownHostsFile=/dev/null` are explicitly **restricted to a temporary, independently verified, trusted target**. Explain the man-in-the-middle risk and consider host-key pinning whenever feasible.
- `sshpass -e` reads `SSHPASS` from the child environment, which can expose the password to sufficiently privileged process inspection. The sample variation is labeled **UNTESTED**, despite an earlier working `sshpass -p` caller. Do not claim it is validated. Where practical, prefer a safer input method with a carefully managed file descriptor and review the tool's actual capabilities.
- Remote `--rsync-path='sudo -n rsync'` requires remote noninteractive sudo authorization; minimize the command/scope allowed and review sudoers before deploying. Beware that rsync options, destination paths, and remote privilege together determine the actual write surface.
- An explicit human approval is required before destructive, root-privileged, or host-trust-changing operations. Prefer dry-run and read-only inspection when available, while recognizing `rsync --dry-run` is not a comprehensive security test.

## Argument construction and filesystem semantics

Use arrays for the rsync executable and each argument in Bash scripts:

```bash
local -a rsync_cmd=(rsync)
local ssh_opts='-o BatchMode=yes -o LogLevel=ERROR'
rsync_cmd+=( -e "ssh ${ssh_opts}" -a -z -h )
rsync_cmd+=( "${sync_root_src%/}/" )
rsync_cmd+=( "${remote_user}@${remote_host}:${sync_root_dest%/}/" )
# Invocation as the intended local UID follows after review.
```

The entire `-e` transport command is one argument to rsync; it is subsequently interpreted by rsync's remote-shell mechanism. Avoid treating a string of arbitrary remote user input as trusted SSH options. Confirm exact source/destination semantics: `source/` copies directory **contents**, while `source` may copy the directory itself depending on destination form. Flags `-a`, `-H`, `-A`, `-X`, `-K`, and `--numeric-ids` have distinct metadata and symlink consequences; do not add or remove them without explaining why.

For the supplied SCP pattern, only the wildcard is intentionally unquoted:

```bash
"${collection_directory%/}/"*".${BOARD}.${DEVTYPE}.${ENC}"
```

Check empty matches, whitespace in filenames, destination interpretation, and platform-specific shell behavior; do not generalize this exception into unquoted variables elsewhere.

## Status reporting and robust error handling

When the calling script uses joetoo's announce–act–report idiom, favor `j_msg`, `handle_result`, and `right_status` over ad hoc UI. Distinguish the transported command's exit status, any reporting-function bitmask, and cleanup failure status. Example pattern:

```bash
j_msg "-${notice}" -nm "running remote command"
if sudo -u "$user" env SSH_AUTH_SOCK="$SSH_AUTH_SOCK" \
        ssh -n -i "$SSH_KEY" "${remote_user}@${remote_host}" hostname; then
    action_rc=0
else
    action_rc=$?
fi
if handle_result "$action_rc" "remote command complete" "remote command failed"; then
    report_rc=0
else
    report_rc=$?
fi
# Apply the caller's policy to action_rc and report_rc separately.
```

This pattern remains inspectable under `set -e` because anticipated failures are inside `if` conditions. Do not use `if ! command; then rc=$?; fi` to capture a failed command: `!` reverses the status. For decoding nonzero reporting bitmasks, inspect `decode_right_status` and the installed header's status-bit contract first. Avoid collapsing transport failure, authentication failure, remote permissions failure, and display/reporting failure into one unexplained error.

## Verification checklist

- Applicable scripts source the correct headers, in the expected order, and run in the intended shell.
- Key/agent initialization and cleanup are compatible with installed function contracts; existing agents are not inadvertently terminated.
- Local and remote UIDs, agent socket access, key path, remote sudo permission, and host-key trust are explicitly checked.
- Bash arrays and rsync `-e` quoting preserve argument boundaries; locally expanded SCP wildcard behavior is intentional.
- Source/trailing-slash/destination semantics and metadata flags match the actual objective.
- Remote writes/root operations are not executed merely to validate a generated draft.
- Operation return code, report return code, and cleanup failures remain distinguishable, including under `set -e`.
- Status of examples is represented accurately: user rsync has no verified joetoo caller in this template; `sshpass -e` is untested; `runuser` alternative has no verified joetoo implementation.
- Final answer states the proposed changes, relevant source evidence, checks performed, remaining uncertainties, and what requires human execution/approval.
