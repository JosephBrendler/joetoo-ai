#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#
# joetoo-kwin_ssh_rcfile_test_driver.sh - exercise single-shell SSH under KWin
# The known-working Python D-Bus broker and resident KWin JavaScript must already be running.

source /usr/sbin/script_header_joetoo

PN=${0##*/}
if [ -f /etc/joetoolkit/BUILD ]; then . /etc/joetoolkit/BUILD; else BUILD="0.0.1"; fi
[ -z "$verbosity" ] && verbosity="${notice}"

#-----[ variables ]-----------------------------------------------------------------------------
expected_class=konsole
desktop=3
x=100
y=80
width=850
height=700

bus=org.joetoo.KWinBridge
path=/org/joetoo/KWinBridge
iface=org.joetoo.KWinBridge

#-----[ main script ]---------------------------------------------------------------------------
checknotroot

if (( $# < 1 || $# > 2 )) || [[ -z ${1:-} ]]; then
    j_msg "-${err}" -p "Usage: ${PN} SSH_HOST [SSH_PORT]"
    exit 2
fi

target=$1
port=${2:-22}
if [[ $target == -* || $target == *$'\n'* || $target == *$'\r'* ]]; then
    j_msg "-${err}" -p "${PN}: invalid SSH host [${target}]"
    exit 2
fi
if ! isint "$port" || [[ ! $port =~ ^[0-9]{1,5}$ ]]; then
    j_msg "-${err}" -p "${PN}: invalid SSH port [${port}]"
    exit 2
fi
port=$((10#$port))
if (( port < 1 || port > 65535 )); then
    j_msg "-${err}" -p "${PN}: SSH port out of range [${port}]"
    exit 2
fi

for cmd in konsole nc qdbus6 mktemp; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        j_msg "-${err}" -p "${PN}: required command not found [$cmd]"
        exit 1
    fi
done

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P) || exit 1
rcfile="${script_dir}/joetoo-ssh-startup.bashrc"
if [[ ! -r $rcfile ]]; then
    j_msg "-${err}" -p "${PN}: rcfile is not readable [${rcfile}]"
    exit 1
fi

if ! bash -ic 'declare -F ssh_wrapper >/dev/null' >/dev/null 2>&1; then
    j_msg "-${err}" -p "${PN}: ssh_wrapper unavailable in a fresh interactive Bash"
    exit 1
fi

loaded=$(qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.isScriptLoaded joetoo-bridge) || exit 1
if [[ $loaded != true ]]; then
    j_msg "-${err}" -p "${PN}: KWin script [joetoo-bridge] not loaded; run your start test driver"
    exit 1
fi

# A private run directory retains the exact Bash PID for the close-window test.
# Kept after the test so the user can inspect the recorded PID; remove it manually later.
session_dir=$(mktemp -d "${XDG_RUNTIME_DIR:-${TMPDIR:-/tmp}}/joetoo-kwin-ssh.XXXXXXXX") || exit 1
pidfile="${session_dir}/bash.pid"

# No large bash -c string; no second shell, and no sensitive Konsole D-Bus API.
# -e must follow all Konsole options. Bash reads the rcfile once, then stays interactive.
program=(konsole --separate -e env
    "JOETOO_SSH_TARGET=$target"
    "JOETOO_SSH_PORT=$port"
    "JOETOO_SSH_PIDFILE=$pidfile"
    bash --rcfile "$rcfile" -i)

request=$(qdbus6 "$bus" "$path" "$iface.SubmitLaunch" \
    "$expected_class" "$desktop" "$x" "$y" "$width" "$height") || exit 1
j_msg "-${notice}" -p "Armed Konsole placement for [${target}:${port}], request [${request}]"

"${program[@]}" &
konsole_pid=$!
j_msg "-${notice}" -p "Launched Konsole PID [${konsole_pid}] for [${target}:${port}]"
j_msg "-${notice}" -p "Test Bash PID will be recorded at [${pidfile}]"

# This reports KWin placement success; it does not wait for SSH to finish.
for ((attempt=0; attempt<150; attempt++)); do
    status=$(qdbus6 "$bus" "$path" "$iface.Status" "$request") || exit 1
    case $status in
        OK*) j_msg "-${notice}" -p "$status"; exit 0 ;;
        ERROR*|UNKNOWN*) j_msg "-${err}" -p "$status"; exit 1 ;;
    esac
    sleep 0.1
done
j_msg "-${err}" -p "${PN}: timed out waiting for Konsole placement (request [${request}])"
exit 1
