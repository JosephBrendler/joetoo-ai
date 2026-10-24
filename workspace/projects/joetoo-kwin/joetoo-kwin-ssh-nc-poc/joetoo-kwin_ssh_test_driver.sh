#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#
# joetoo-kwin_ssh_test_driver.sh - exercise the KWin launch bridge with an SSH session
# Create a placed Konsole regardless of host availability, then probe SSH and connect.
# Requires the existing Python broker and KWin JavaScript to be running already.

source /usr/sbin/script_header_joetoo

PN=${0##*/}
if [ -f /etc/joetoolkit/BUILD ]; then . /etc/joetoolkit/BUILD; else BUILD="0.0.1"; fi
[ -z "$verbosity" ] && verbosity="${notice}"

#-----[ variables ]-----------------------------------------------------------------------------
# Known-working placement policy from the launch POC; deliberately fixed for this test.
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

# Do not allow a host to be interpreted as an option by nc/ssh_wrapper.
if [[ $target == -* || $target == *$'\n'* ]]; then
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

for val in "$desktop" "$x" "$y" "$width" "$height"; do
    if ! isint "$val"; then
        j_msg "-${err}" -p "${PN}: invalid geometry/desktop integer [${val}]"
        exit 2
    fi
done

for cmd in konsole nc qdbus6; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        j_msg "-${err}" -p "${PN}: required command not found [$cmd]"
        exit 1
    fi
done

# ssh_wrapper is a Bash function in the user's interactive shell setup.
# Check a fresh interactive Bash, since that is what the new Konsole will run.
if ! bash -ic 'declare -F ssh_wrapper >/dev/null' >/dev/null 2>&1; then
    j_msg "-${err}" -p "${PN}: ssh_wrapper not available in a NEW interactive Bash; check ~/.bashrc and joetoo shell setup"
    exit 1
fi

loaded=$(qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.isScriptLoaded joetoo-bridge) || exit 1
if [[ $loaded != true ]]; then
    j_msg "-${err}" -p "${PN}: resident KWin script [joetoo-bridge] is not loaded; run your start test driver first"
    exit 1
fi

# bash -ic loads ~/.bashrc, where the user's ssh_wrapper function is expected.
# In the child, $0 is joetoo-ssh, $1 is HOST, and $2 is PORT.
# The port probe is performed INSIDE the new Konsole, not in this driver.
# Leave a shell running whether SSH connects, fails, or the user logs out.
program=(konsole --separate -e bash -ic '
    target=$1
    port=$2
    printf "\n=== Intended SSH session: %s (TCP port %s) ===\n" "$target" "$port"

    if ! declare -F ssh_wrapper >/dev/null; then
        printf "ERROR: ssh_wrapper is unavailable in this shell\n" >&2
    elif ! command -v nc >/dev/null 2>&1; then
        printf "ERROR: nc is unavailable in this shell\n" >&2
    elif nc -z -w 2 "$target" "$port" >/dev/null 2>&1; then
        printf "SSH TCP port reachable: %s:%s; starting ssh_wrapper\n" "$target" "$port"
        ssh_wrapper -p "$port" "$target"
        ssh_rc=$?
        printf "\nSSH session ended: target=%s port=%s status=%d\n" "$target" "$port" "$ssh_rc"
    else
        printf "\nSSH unavailable: target=%s port=%s (TCP probe unsuccessful)\n" "$target" "$port"
        printf "No SSH connection was attempted.\n"
    fi

    printf "\nThis terminal is retained for %s.\n" "$target"
    printf "Manual retry: ssh_wrapper -p %s %s\n" "$port" "$target"
    exec bash -i
' joetoo-ssh "$target" "$port")

# Arm window placement BEFORE the new application window is created.
request=$(qdbus6 "$bus" "$path" "$iface.SubmitLaunch" \
    "$expected_class" "$desktop" "$x" "$y" "$width" "$height") || exit 1
j_msg "-${notice}" -p "Armed Konsole placement for [${target}:${port}], request [${request}]"

"${program[@]}" &
child=$!
j_msg "-${notice}" -p "Launched Konsole for [${target}:${port}], shell PID [${child}]"

# Wait only for placement, NOT for connection establishment or SSH logout.
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
