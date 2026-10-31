# shellcheck shell=bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
# One interactive Bash owns the foreground application, then returns to its prompt.
joetoo_session_mode=${JOETOO_SESSION_MODE-}
joetoo_session_target=${JOETOO_SESSION_TARGET-}
unset JOETOO_SESSION_MODE JOETOO_SESSION_TARGET
# shellcheck source=/dev/null
[[ ! -r $HOME/.bashrc ]] || source "$HOME/.bashrc"
# Use the installed header if the user's interactive setup did not load it.
if ! declare -F ssh_wrapper >/dev/null; then source /usr/sbin/script_header_joetoo; fi
case $joetoo_session_mode in
    ssh)
        j_msg "-${notice}" -p "SSH target [$joetoo_session_target]; local Bash PID [$$]"
        if nc -z -w 2 "${joetoo_session_target##*@}" 22 >/dev/null 2>&1; then
            j_msg "-${notice}" -p 'SSH session ...'
            if ssh_wrapper "$joetoo_session_target"; then joetoo_session_rc=0; else joetoo_session_rc=$?; fi
            # SSH owns the terminal while connected, so open a fresh result line.
            j_msg "-${notice}" -pn 'SSH session ended ...'
            handle_result "$joetoo_session_rc" 'returned to local shell' 'connection failed' "$notice" || :
        else
            j_msg "-${warn}" -p "SSH unavailable [$joetoo_session_target]; keeping local shell"
        fi
        printf -v joetoo_session_retry 'ssh_wrapper %q' "$joetoo_session_target"
        j_msg "-${notice}" -p "Manual retry: $joetoo_session_retry" ;;
    local)
        if "$joetoo_session_target"; then joetoo_session_rc=0; else joetoo_session_rc=$?; fi
        j_msg "-${notice}" -pn "Local application [$joetoo_session_target] ended ..."
        handle_result "$joetoo_session_rc" 'returned to local shell' 'application failed' "$notice" || : ;;
    *) j_msg "-${err}" -p 'Unknown startup mode; keeping local shell' ;;
esac
# No exec, exit or replacement Bash: this original interactive shell stays usable.
