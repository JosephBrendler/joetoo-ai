# joetoo-ssh-startup.bashrc
# Proof of concept: start an SSH session inside ONE interactive Bash process.
# Used only with: bash --rcfile /absolute/path/to/this/file -i

# Retain the user's normal joetoo interactive functions, aliases, and prompt.
# This runs BEFORE the test's connection-status messages.
if [[ -r $HOME/.bashrc ]]; then
    source "$HOME/.bashrc"
fi

joetoo_ssh_target=${JOETOO_SSH_TARGET-}
joetoo_ssh_port=${JOETOO_SSH_PORT:-22}
joetoo_ssh_pidfile=${JOETOO_SSH_PIDFILE-}
unset -v JOETOO_SSH_TARGET JOETOO_SSH_PORT JOETOO_SSH_PIDFILE

# Tell the launcher which actual Bash process owns the foreground SSH child.
if [[ -n $joetoo_ssh_pidfile ]]; then
    printf '%s\n' "$$" > "$joetoo_ssh_pidfile"
fi

printf '\n=== joetoo SSH window: [%s:%s] ===\n' "$joetoo_ssh_target" "$joetoo_ssh_port"
printf 'Local shell PID: [%s]\n' "$$"

if [[ -z $joetoo_ssh_target ]]; then
    printf 'ERROR: no target supplied to joetoo startup file\n' >&2
elif ! declare -F ssh_wrapper >/dev/null; then
    printf 'ERROR: ssh_wrapper is unavailable in this shell\n' >&2
elif ! command -v nc >/dev/null 2>&1; then
    printf 'ERROR: nc is unavailable in this shell\n' >&2
elif nc -z -w 2 "$joetoo_ssh_target" "$joetoo_ssh_port" >/dev/null 2>&1; then
    printf 'SSH port reachable: [%s:%s]; invoking ssh_wrapper\n' "$joetoo_ssh_target" "$joetoo_ssh_port"
    ssh_wrapper -p "$joetoo_ssh_port" "$joetoo_ssh_target"
    joetoo_ssh_rc=$?
    printf '\nSSH session ended for [%s:%s]; status [%s]\n' \
           "$joetoo_ssh_target" "$joetoo_ssh_port" "$joetoo_ssh_rc"
else
    printf 'SSH unavailable: [%s:%s] (TCP probe failed); no connection attempted\n' \
           "$joetoo_ssh_target" "$joetoo_ssh_port"
fi

printf 'This is still the ORIGINAL local Bash shell, PID [%s].\n' "$$"
printf 'To retry manually: ssh_wrapper -p %q %q\n\n' \
       "$joetoo_ssh_port" "$joetoo_ssh_target"

# No exec, exit, or replacement shell. Bash now presents its usual prompt.
