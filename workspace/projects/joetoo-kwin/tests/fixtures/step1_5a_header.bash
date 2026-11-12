#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
# Portable test double: only the planner's header interface, not production UI.
# Installed-header tests separately check the real helper and rendering behavior.
# Globals below form the test header API; other state is supplied by the client.
# shellcheck disable=SC2034,SC2154
TRUE=0; FALSE=''; notice=5; info=6; debug=7; err=3
BCon=''; BGon=''; Boff=''
checknotroot() { :; }
j_msg() {
    local level=5 arg
    for arg in "$@"; do [[ $arg =~ ^-([0-7])$ ]] && level=${BASH_REMATCH[1]}; done
    if (( verbosity >= level )); then printf '%s\n' "${*: -1}"; fi
    return 0
}
isint() { [[ $1 =~ ^-?[0-9]+$ ]]; }
handle_result() { return "${REPORT_RC:-0}"; }
decode_right_status() { printf 'DECODE:%s\n' "$1"; }
show_config() {
    local entry name value
    printf 'CONFIG\n'
    for entry in $varlist; do
        if [[ $entry == bool.* ]]; then
            name=${entry#bool.}
            case ${!name} in
                "$TRUE") value=True ;;
                "$FALSE") value=False ;;
                *) value=INVALID ;;
            esac
        else
            name=${entry#rlv.}
            value=${!name}
        fi
        printf '%s=%s\n' "$name" "$value"
    done
}

# Model the documented verbosity bounds without reading system installations.
_pc_action_verbosity() {
    local floor=0
    [[ ! $INTERACTIVE ]] || floor=$notice
    case $_pc_operator in
        +) (( verbosity < 7 )) && verbosity=$((verbosity + 1)) ;;
        -) (( verbosity > floor )) && verbosity=$((verbosity - 1)) ;;
        *) return 1 ;;
    esac
    return 0
}
# Tests use plain ASCII cells; real display-width handling is integration-tested.
get_msg_len() { printf '%s\n' "${#1}"; }

# Match the header's severity gate and its deliberately unconditional success.
d_do() {
    (( $# >= 2 )) || return 1
    [[ -n $verbosity ]] || return 2
    local level=${!#}
    isint "$level" || return 3
    if [[ $DEBUG ]] || (( verbosity >= level )); then eval "$1"; fi
    return 0
}
die() { printf '%s\n' "$1" >&2; exit 1; }

# Deterministic stand-in; installed-header integration exercises the real helper.
timestamp() { printf '%s\n' '20261112-09:11:16'; }
