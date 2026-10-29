#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#
# demonstration.sh - demonstrate forms of announce/act/report idiom

source /usr/sbin/script_header_joetoo

PN=${0##*/}   #  like =$(basename $0) but w/o subshell and function call

if [ -f /etc/joetoolkit/BUILD ]; then . /etc/joetoolkit/BUILD; else BUILD="0.0.1"; fi

[ -z "$verbosity" ] && verbosity=${notice}  # assign default if null; allow calling program to dictate

# simplest form, but at debug severity
var=3
# note - j_msg using -n to leave the output line "open" for result on same line
j_msg "-${debug}" -p -n "Demonstrating simple AAR (isint/right_status)"
isint "$var" >/dev/null 2>&1    # just demonstrating silenced sureiled cmd
right_status $? "$debug" || die "failed isint check"

# simple, more informative, at info everity
j_msg "-${info}" -p -n "Demonstrating simple AAR (timestamp/handle_result)"
output="$(timestamp)" 2>/dev/null    # just demonstrating silenced sureiled cmd
handle_result $? "$output" "" "$info" || die "failed to assign timestamp to output"

j_msg "-${notice}" -mp ""  # severity-aware newline

# simple, but allowing surveiled cmd output; more informative, at notice everity
# note first j_msg announces what the action is, but does not use -n because cmd output is expected
j_msg "-${notice}" -p "Demonstrating simple AAR (timestamp/handle_result)"
timestamp | sed 's|^|    |'    # indenting each line of surveiled cmd output
result=$?    # persist result during followup single line "done" announcement
# note - second j_msg opens a new line, announcing action is done and leaving line open with -n, for results
j_msg "-${notice}" -p -n "timestamp complete; result:"
handle_result $? "" "" "$notice" || { j_msg "-${err}" -p "failed to run or surveil timestamp"; exit 5 ; }

j_msg "-${notice}" -mp ""  # severity-aware newline

# complex, rigorous form is announce, act, coapture status, decode promulgated result, apply policy
# designed to enable safe developer-built error-handling/analysis under set -e
set -e
    # simulated failure of tmux-workflow
    session="maint_1"; _a_result=1
    # this wont run until user detaches from or kills from inside the session, so report detachment or failure>
    j_msg "-${notice}" -p -n "tmux result:"
    # note: using if ! handle_result; then doesn't work becuase $? becomes 0
    if handle_result $_a_result "tmux exited status [$_a_result]" "Failed to attach to root tmux" ; then
        _hr_result=0    # nothing to do here
    else
        _hr_result=$?   # this preserves the bad status info
        # check bit0 - did the surveiled action fail?
        if [ $(( _hr_result & 1 )) -eq 1 ]; then
            # before dying, check if bits other tha 0 are also set and report that
            if [ $(( _hr_result & ~1 )) -ne 0 ] ; then
                j_msg "-${err}" -p "handle_result/right_status failed with status [$_hr_result]"
                command -v decode_right_status &>/dev/null && decode_right_status "$_hr_result"
            fi
            die "failed to attach to [$session]; tmux exited with status [$_a_result]"
        else
            # the only way to get here when bit 0 is not be set, so it must be one of the others - report that
            j_msg "-${err}" -p "handle_result/right_status failed with status [$_hr_result]"
            command -v decode_right_status &>/dev/null && decode_right_status "$_hr_result"
            die "failure(s) as stated, after attaching to [$session]; status [$_hr_result]"
        fi
    fi
set +e


j_msg "-${notice}" -p "Run this script with cmdline override prefix to exercise severity/verbosity"
j_msg "-${notice}" -m "( either DEBUG=$TRUE  or verbosity=$iinfo or verbosity=$debug )"
