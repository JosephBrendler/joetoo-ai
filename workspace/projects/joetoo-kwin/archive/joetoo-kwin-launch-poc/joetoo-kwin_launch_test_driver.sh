#!/bin/bash
# Experimental launcher: arm placement request BEFORE creating an app window.
# Run as a regular user in the Plasma session.
source /usr/sbin/script_header_joetoo
PN=${0##*/}

# -------- Test policy: change these for each experiment -------------------
program=(konsole --separate)  # array: executable and optional arguments
expected_class=konsole       # KWin resourceClass or last component of desktopFileName
desktop=3
x=100
y=80
width=850
height=700
# --------------------------------------------------------------------------

if ! command -v "${program[0]}" >/dev/null 2>&1; then
    printf '%s: program not found: %s\n' "$PN" "${program[0]}" >&2
    exit 1
fi
for val in "$desktop" "$x" "$y" "$width" "$height"; do
    isint "$val" || { printf '%s: invalid integer: %s\n' "$PN" "$val" >&2; exit 2; }
done

bus=org.joetoo.KWinBridge
path=/org/joetoo/KWinBridge
iface=org.joetoo.KWinBridge

# Do NOT launch before the request has been accepted.
request=$(qdbus6 "$bus" "$path" "$iface.SubmitLaunch" \
    "$expected_class" "$desktop" "$x" "$y" "$width" "$height") || exit 1
printf 'Armed placement for class [%s], request [%s]\n' "$expected_class" "$request"

"${program[@]}" &
child=$!
printf 'Launched [%s], shell PID [%s]\n' "${program[*]}" "$child"

# One-shot diagnostic; do not block indefinitely.
for ((attempt=0; attempt<150; attempt++)); do
    status=$(qdbus6 "$bus" "$path" "$iface.Status" "$request") || exit 1
    case $status in
        OK*) printf '%s\n' "$status"; exit 0 ;;
        ERROR*|UNKNOWN*) printf '%s\n' "$status" >&2; exit 1 ;;
    esac
    sleep 0.1
done
printf '%s: timed out waiting for windowAdded/placement (request %s)\n' "$PN" "$request" >&2
printf 'Check actual resourceClass in KWin if program appeared but did not move.\n' >&2
exit 1
