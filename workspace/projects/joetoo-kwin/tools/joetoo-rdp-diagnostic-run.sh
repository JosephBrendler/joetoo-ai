#!/bin/bash
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#
# joetoo-rdp-diagnostic-run.sh - Maintainer-operated Stage A orchestration only. Never run unattended through
#
# an AI tool: the unchanged proof script performs real RDP/GUI operations.
# Cleanup owns only our KWin script and receiver, never an RDP viewer/session.
# The X11 companion follows the same ownership rule for its second script/child.
# Action functions are dispatched via run_step; cleanup is invoked by EXIT.

# shellcheck disable=SC2329
# shellcheck source=/usr/sbin/script_header_joetoo.shellcheck_var_stub
# shellcheck source=/usr/sbin/script_header_joetoo.shellcheck_func_stub
source /usr/sbin/script_header_joetoo
set -o pipefail

PN=${0##*/}
BUILD=20261108
verbosity=${verbosity:-$notice}
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P) || exit 1
receiver="$project_dir/tools/joetoo-rdp-diagnostic-receiver.py"
proof="$project_dir/tools/rdp_identity-security_proof"
x11_observer="$project_dir/tools/joetoo-rdp-x11-use.py"
rdp_diag_capture=""
receiver_pid=""
x11_pid=""
DIAGNOSTIC_OWNED=$FALSE
RECEIVER_STOPPED=$TRUE
X11_OWNED=$FALSE
X11_STOPPED=$TRUE
REPORT_FAULT=$FALSE

# Environment overrides are explicit and remain separate from production
# joetoo-kwin configuration. Receiver validates its own transport bounds.
export RDP_DIAG_SECONDS=${RDP_DIAG_SECONDS:-1800}
RDP_DIAG_START_TIMEOUT_SECONDS=${RDP_DIAG_START_TIMEOUT_SECONDS:-15}
RDP_DIAG_READY_WAIT_MS=${RDP_DIAG_READY_WAIT_MS:-15000}
RDP_DIAG_DBUS_SECONDS=${RDP_DIAG_DBUS_SECONDS:-5}
RDP_DIAG_CLEANUP_MS=${RDP_DIAG_CLEANUP_MS:-5000}
RDP_DIAG_POLL_MS=${RDP_DIAG_POLL_MS:-100}
RDP_DIAG_ACK_MS=${RDP_DIAG_ACK_MS:-3000}
RDP_DIAG_LIVENESS_MS=${RDP_DIAG_LIVENESS_MS:-5000}
RDP_DIAG_MAX_RECORDS=${RDP_DIAG_MAX_RECORDS:-1024}
RDP_DIAG_MAX_TOTAL_BYTES=${RDP_DIAG_MAX_TOTAL_BYTES:-16777216}
RDP_DIAG_EXPORT_MS=${RDP_DIAG_EXPORT_MS:-0}
# The X11 property experiment does not describe native Wayland windows. An
# explicit empty pseudo-boolean disables it; unknown/startx sessions default on.
if [[ ! ${RDP_DIAG_X11_USE+x} ]]; then
    RDP_DIAG_X11_USE=$TRUE
    if [[ ${XDG_SESSION_TYPE:-} == wayland ]]; then RDP_DIAG_X11_USE=$FALSE; fi
fi
RDP_DIAG_X11_POLL_MS=${RDP_DIAG_X11_POLL_MS:-10}
RDP_DIAG_X11_ACK_MS=${RDP_DIAG_X11_ACK_MS:-3000}
RDP_DIAG_X11_MAX_CANDIDATES=${RDP_DIAG_X11_MAX_CANDIDATES:-64}
RDP_DIAG_X11_MAX_CLIENTS=${RDP_DIAG_X11_MAX_CLIENTS:-512}
RDP_DIAG_X11_EVENT_LIMIT=${RDP_DIAG_X11_EVENT_LIMIT:-4096}
# shellcheck disable=SC2034 # Consumed by the installed header's show_config.
varlist="PN BUILD project_dir RDP_DIAG_SECONDS RDP_DIAG_ACK_MS
RDP_DIAG_LIVENESS_MS RDP_DIAG_MAX_RECORDS RDP_DIAG_MAX_TOTAL_BYTES
RDP_DIAG_EXPORT_MS RDP_DIAG_START_TIMEOUT_SECONDS RDP_DIAG_READY_WAIT_MS
RDP_DIAG_DBUS_SECONDS RDP_DIAG_CLEANUP_MS RDP_DIAG_POLL_MS
RDP_DIAG_X11_USE RDP_DIAG_X11_POLL_MS RDP_DIAG_X11_ACK_MS
RDP_DIAG_X11_MAX_CANDIDATES RDP_DIAG_X11_MAX_CLIENTS RDP_DIAG_X11_EVENT_LIMIT"

# Keep the action status independent of the header's reporting bitmask. A
# rendering/logging fault must not silently turn a failed action into success.
run_step() {
    local label=$1 action_rc report_rc
    shift
    j_msg "-${notice}" -p "$label"
    if "$@"; then action_rc=0; else action_rc=$?; fi
    j_msg "-${notice}" -p -n "$label result:"
    if handle_result "$action_rc" "completed" "failed" "$notice"; then
        report_rc=0
    else
        report_rc=$?
    fi
    if (( report_rc & ~1 )); then
        REPORT_FAULT=$TRUE
        j_msg "-${err}" -p "Reporting fault [$report_rc]; action status [$action_rc]"
        if command -v decode_right_status >/dev/null; then
            decode_right_status "$report_rc" || :
        fi
    fi
    if (( action_rc != 0 )); then return "$action_rc"; fi
    (( report_rc == 0 ))
}

kwin_call() {
    timeout "$RDP_DIAG_DBUS_SECONDS" qdbus6 org.kde.KWin "$@"
}

make_capture() {
    rdp_diag_capture=$(mktemp -d "${TMPDIR:-/tmp}/joetoo-rdp-diagnostic.XXXXXXXX")
}

start_receiver() {
    python3 "$receiver" serve "$rdp_diag_capture" \
        --ack-ms "$RDP_DIAG_ACK_MS" --liveness-ms "$RDP_DIAG_LIVENESS_MS" \
        --max-records "$RDP_DIAG_MAX_RECORDS" --max-total-bytes "$RDP_DIAG_MAX_TOTAL_BYTES" \
        --export-ms "$RDP_DIAG_EXPORT_MS" > "$rdp_diag_capture/receiver.log" 2>&1 &
    receiver_pid=$!
    RECEIVER_STOPPED=$FALSE
}

wait_receiver() {
    local started=$SECONDS
    while [[ ! -f "$rdp_diag_capture/run.json" || ! -f "$rdp_diag_capture/observer.js" ]]; do
        kill -0 "$receiver_pid" 2>/dev/null || return 1
        (( SECONDS - started < RDP_DIAG_START_TIMEOUT_SECONDS )) || return 1
        sleep "$poll_seconds" || return 1
    done
    python3 "$receiver" status "$rdp_diag_capture"
}

load_diagnostic() {
    local script_id
    script_id=$(kwin_call /Scripting org.kde.kwin.Scripting.loadScript \
        "$rdp_diag_capture/observer.js" joetoo-rdp-window-diagnostic) || return
    [[ "$script_id" =~ ^[0-9]+$ ]] || return 1
    DIAGNOSTIC_OWNED=$TRUE # Also unload if run fails after successful loading.
    kwin_call "/Scripting/Script${script_id}" org.kde.kwin.Script.run
}

unload_diagnostic() {
    local result
    result=$(kwin_call /Scripting org.kde.kwin.Scripting.unloadScript joetoo-rdp-window-diagnostic) || return
    [[ "$result" == true ]] || return 1
    DIAGNOSTIC_OWNED=$FALSE
}

# A separate private subdirectory keeps the independently verifiable property
# ledger beside the main capture, inside the same final archive.
start_x11() {
    mkdir -m 0700 -- "$rdp_diag_capture/x11-use" || return
    python3 "$x11_observer" --serve "$rdp_diag_capture/x11-use" \
        --seconds "$RDP_DIAG_SECONDS" --poll-ms "$RDP_DIAG_X11_POLL_MS" \
        --ack-ms "$RDP_DIAG_X11_ACK_MS" --max-candidates "$RDP_DIAG_X11_MAX_CANDIDATES" \
        --max-clients "$RDP_DIAG_X11_MAX_CLIENTS" --event-limit "$RDP_DIAG_X11_EVENT_LIMIT" \
        > "$rdp_diag_capture/x11-use/observer.log" 2>&1 &
    x11_pid=$!
    X11_STOPPED=$FALSE
}

wait_x11_script() {
    local started=$SECONDS
    while [[ ! -f "$rdp_diag_capture/x11-use/linker.js" ]]; do
        kill -0 "$x11_pid" 2>/dev/null || return 1
        (( SECONDS - started < RDP_DIAG_START_TIMEOUT_SECONDS )) || return 1
        sleep "$poll_seconds" || return 1
    done
}

load_x11() {
    local script_id
    script_id=$(kwin_call /Scripting org.kde.kwin.Scripting.loadScript \
        "$rdp_diag_capture/x11-use/linker.js" joetoo-rdp-x11-use) || return
    [[ "$script_id" =~ ^[0-9]+$ ]] || return 1
    X11_OWNED=$TRUE
    kwin_call "/Scripting/Script${script_id}" org.kde.kwin.Script.run
}

wait_x11_ready() {
    local started=$SECONDS
    while ! timeout "$RDP_DIAG_DBUS_SECONDS" python3 "$x11_observer" --status \
        "$rdp_diag_capture/x11-use" > "$rdp_diag_capture/x11-use/status-last.json" \
        2> "$rdp_diag_capture/x11-use/status-error.log"; do
        kill -0 "$x11_pid" 2>/dev/null || return 1
        (( (SECONDS - started) * 1000 < RDP_DIAG_READY_WAIT_MS )) || return 1
        sleep "$poll_seconds" || return 1
    done
    cat -- "$rdp_diag_capture/x11-use/status-last.json"
}

finish_x11() {
    timeout "$RDP_DIAG_DBUS_SECONDS" qdbus6 org.kde.kglobalaccel /component/kwin \
        org.kde.kglobalaccel.Component.invokeShortcut joetoo_rdp_x11_use_finish
}

unload_x11() {
    local result
    result=$(kwin_call /Scripting org.kde.kwin.Scripting.unloadScript joetoo-rdp-x11-use) || return
    [[ "$result" == true ]] || return 1
    X11_OWNED=$FALSE
}

# A pidfd pins the actual child; a stale/reused numeric PID is never signalled.
# Failure on an older Python/kernel is explicit, with the private evidence kept.
stop_child() {
    local child_pid=$1
    python3 - "$child_pid" "$$" "$RDP_DIAG_CLEANUP_MS" <<'PY'
import os
from pathlib import Path
import select
import signal
import sys
pid, parent, wait_ms = map(int, sys.argv[1:])
try:
    fd = os.pidfd_open(pid)
except ProcessLookupError:
    sys.exit(0)
try:
    try:
        fields = dict(line.split(':', 1) for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line)
    except FileNotFoundError:
        sys.exit(0)
    if int(fields['PPid']) != parent:
        sys.exit('Refusing to signal a process that is not our diagnostic child')
    poll = select.poll()
    poll.register(fd, select.POLLIN)
    if not poll.poll(0):
        signal.pidfd_send_signal(fd, signal.SIGTERM)
    if not poll.poll(wait_ms):
        signal.pidfd_send_signal(fd, signal.SIGKILL)
        if not poll.poll(wait_ms):
            sys.exit('Diagnostic child did not exit within the cleanup bound')
finally:
    os.close(fd)
PY
    local action_rc=$?
    (( action_rc == 0 )) || return "$action_rc"
    wait "$child_pid" 2>/dev/null || : # Receiver result remains in its log.
    # Both diagnostic terminal outcomes are verified separately.
}

stop_receiver() {
    stop_child "$receiver_pid" || return
    RECEIVER_STOPPED=$TRUE
}

stop_x11() {
    stop_child "$x11_pid" || return
    X11_STOPPED=$TRUE
}

verify_x11() {
    python3 "$x11_observer" --verify "$rdp_diag_capture/x11-use" \
        > "$rdp_diag_capture/x11-use/verification.json" || return
    python3 - "$rdp_diag_capture/x11-use/verification.json" <<'PY'
import json
import sys
with open(sys.argv[1]) as stream:
    result = json.load(stream)
print(json.dumps(result, sort_keys=True))
if not result.get('observation_completed_as_requested') or not result.get('linker_ready'):
    sys.exit('X11 property observation incomplete; retain evidence for diagnosis')
if not result.get('candidates') or any(result.get(k) for k in ('unlinked', 'unsupported', 'discovery_gaps')):
    print('X11 candidate coverage has limitations; inspect counts before drawing conclusions.')
print('A use latch does not prove desktop role or graphical-login completion.')
PY
}

archive_capture() {
    # Preserve every capture, including failed runs. Never overwrite an archive.
    ( set -o noclobber
      tar -cjf - -C "$(dirname -- "$rdp_diag_capture")" "$(basename -- "$rdp_diag_capture")" \
          > "${rdp_diag_capture}.tbz2" )
}

cleanup() {
    local original_rc=$? cleanup_rc=0
    trap - EXIT INT TERM
    if [[ "$X11_OWNED" ]]; then
        run_step "Finish only our X11 linker" finish_x11 || cleanup_rc=1
    fi
    if [[ ! "$X11_STOPPED" ]]; then
        run_step "Stop only our X11 property observer" stop_x11 || cleanup_rc=1
    fi
    if [[ "$X11_OWNED" ]]; then
        run_step "Unload only our X11 linker" unload_x11 || cleanup_rc=1
    fi
    if [[ "$DIAGNOSTIC_OWNED" ]]; then
        run_step "Unload only our diagnostic" unload_diagnostic || cleanup_rc=1
    fi
    if [[ ! "$RECEIVER_STOPPED" ]]; then
        run_step "Stop only our receiver" stop_receiver || cleanup_rc=1
    fi
    if [[ -n "$rdp_diag_capture" && -d "$rdp_diag_capture" ]]; then
        if [[ "$RECEIVER_STOPPED" && "$X11_STOPPED" ]]; then
            run_step "Archive private diagnostic evidence" archive_capture || cleanup_rc=1
            j_msg "-${notice}" -p "Evidence retained: [$rdp_diag_capture]"
            j_msg "-${notice}" -p "Archive attempt: [${rdp_diag_capture}.tbz2]; inspect its reported result"
        else
            j_msg "-${err}" -p "Diagnostic cleanup failed; evidence retained at [$rdp_diag_capture]; receiver PID [$receiver_pid], X11 PID [$x11_pid]"
            j_msg "-${warn}" -p "No archive made while a diagnostic child may still be writing"
        fi
    fi
    if (( original_rc == 0 && cleanup_rc != 0 )); then original_rc=1; fi
    if [[ "$REPORT_FAULT" ]]; then original_rc=1; fi
    exit "$original_rc"
}

#-----[ main ]-------------------------------------------------------------------------------
if [[ ${1:-} == -h || ${1:-} == --help || $# -lt 2 || $# -gt 3 ]]; then
    j_msg "-${notice}" -p "Usage: $PN CLIENT HOST[:PORT] [USER]"
    j_msg "-${notice}" -p "Runs the unchanged interactive proof only after persisted diagnostic readiness."
    j_msg "-${notice}" -p "RDP_DIAG_SECONDS and RDP_DIAG_* environment overrides control diagnostic bounds."
    [[ ${1:-} == -h || ${1:-} == --help ]] && exit 0
    exit 2
fi
checknotroot
for command in python3 qdbus6 timeout mktemp tar bash; do
    command -v "$command" >/dev/null || die "Required command unavailable: [$command]"
done
for value in "$RDP_DIAG_START_TIMEOUT_SECONDS" "$RDP_DIAG_READY_WAIT_MS" \
    "$RDP_DIAG_DBUS_SECONDS" "$RDP_DIAG_CLEANUP_MS" "$RDP_DIAG_POLL_MS" \
    "$RDP_DIAG_X11_POLL_MS" "$RDP_DIAG_X11_ACK_MS" "$RDP_DIAG_X11_MAX_CANDIDATES" \
    "$RDP_DIAG_X11_MAX_CLIENTS" "$RDP_DIAG_X11_EVENT_LIMIT"; do
    [[ "$value" =~ ^[1-9][0-9]{0,6}$ ]] || die "Invalid diagnostic orchestration timing"
done
[[ -z "$RDP_DIAG_X11_USE" || "$RDP_DIAG_X11_USE" == "$TRUE" ]] || die "Invalid X11 diagnostic pseudo-boolean"
printf -v poll_seconds '%d.%03d' "$((RDP_DIAG_POLL_MS / 1000))" "$((RDP_DIAG_POLL_MS % 1000))"
[[ -r "$receiver" && -r "$proof" ]] || die "Run from a complete project checkout"
if [[ "$RDP_DIAG_X11_USE" ]]; then
    [[ -r "$x11_observer" && -r "${x11_observer%.py}.js" ]] || die "X11 diagnostic companion files are missing"
fi
separator "$(hostname)" "${PN}-${BUILD}"
show_config
j_msg "-${warn}" -p "This maintainer-run procedure starts a real RDP client and opens KWin Debug Console."
j_msg "-${notice}" -p "No managed enrollment or production-resident restart; viewer cleanup remains yours."
confirm_continue_or_exit || exit 1

j_msg "-${notice}" -p -n "Check whether diagnostic is already loaded"
existing=$(kwin_call /Scripting org.kde.kwin.Scripting.isScriptLoaded joetoo-rdp-window-diagnostic)
action_rc=$?
j_msg "-${notice}" -p -n "Check diagnostic load state result:"
right_status "$action_rc" "$notice" || exit 1
[[ "$existing" == false ]] || die "Diagnostic already loaded or load state uncertain; leaving it untouched"
if [[ "$RDP_DIAG_X11_USE" ]]; then
    existing=$(kwin_call /Scripting org.kde.kwin.Scripting.isScriptLoaded joetoo-rdp-x11-use) || exit 1
    [[ "$existing" == false ]] || die "X11 linker already loaded or load state uncertain; leaving it untouched"
fi
umask 077
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
run_step "Create private evidence directory" make_capture || exit 1
j_msg "-${notice}" -p "Capture directory: [$rdp_diag_capture]"
run_step "Start temporary receiver" start_receiver || exit 1
run_step "Verify receiver and pinned bus owner" wait_receiver || exit 1
run_step "Load standalone observer" load_diagnostic || exit 1
run_step "Require persisted ready and active observation" \
    python3 "$receiver" status "$rdp_diag_capture" --require-ready --wait-ms "$RDP_DIAG_READY_WAIT_MS" || exit 1
if [[ "$RDP_DIAG_X11_USE" ]]; then
    run_step "Start X11 property observation" start_x11 || exit 1
    run_step "Wait for private X11 linker script" wait_x11_script || exit 1
    run_step "Load isolated X11 UUID linker" load_x11 || exit 1
    run_step "Require current persisted X11 readiness" wait_x11_ready || exit 1
else
    j_msg "-${warn}" -p "X11 property companion disabled; this run cannot establish X11 activity-property evidence."
fi
j_msg "-${notice}" -p "Screenshot-free run: ignore Debug Console; answer skip to prompts claiming debug-console evidence."
j_msg "-${notice}" -p "Answer other phases truthfully. GNOME logout and viewer disconnect/closure are distinct outcomes."
j_msg "-${notice}" -p "If logout ends the viewer, skip the normal viewer-close claim and report that logout ended the session."

# Keep terminal input intact for the proof's credential/phase prompts. A proof
# failure still proceeds to diagnostic export; never kill the viewer afterwards.
proof_rc=0
run_step "Run unchanged maintainer identity proof" bash "$proof" "$@" || proof_rc=$?
j_msg "-${notice}" -p "Proof command result [$proof_rc]; this is separate from remote-session outcome"
run_step "Finish observation and start export" timeout "$RDP_DIAG_DBUS_SECONDS" \
    qdbus6 org.kde.kglobalaccel /component/kwin \
    org.kde.kglobalaccel.Component.invokeShortcut joetoo_rdp_diagnostic_finish || exit 1
x11_rc=0
if [[ "$RDP_DIAG_X11_USE" ]]; then
    run_step "Finish X11 UUID linkage" finish_x11 || x11_rc=1
    run_step "Stop X11 property observation" stop_x11 || x11_rc=1
    run_step "Unload isolated X11 linker" unload_x11 || x11_rc=1
    if [[ "$X11_STOPPED" ]]; then
        run_step "Verify X11 property evidence independently" verify_x11 || x11_rc=1
    fi
fi
export_wait_ms=$(python3 - "$rdp_diag_capture/run.json" <<'PY'
import json
import sys
with open(sys.argv[1]) as stream:
    settings = json.load(stream)['settings']
print(settings['exportTimeoutMs'] + settings['ackTimeoutMs'])
PY
) || exit 1
run_step "Wait for durable export and sender confirmation" \
    python3 "$receiver" status "$rdp_diag_capture" --require-complete --wait-ms "$export_wait_ms" || exit 1
run_step "Independently verify evidence and receipts" \
    python3 "$receiver" verify "$rdp_diag_capture" || exit 1
run_step "Check internal capture integrity separately from delivery" \
    python3 - "$rdp_diag_capture/receipt.json" <<'PY'
import json
import sys
with open(sys.argv[1]) as stream:
    receipt = json.load(stream)
if receipt.get('internal_capture_intact') is not True:
    sys.exit('Internal observation incomplete; keep the transport-complete evidence for diagnosis')
PY
action_rc=$?
j_msg "-${warn}" -p "Lifecycle coverage remains UNASSESSED: correlate proof PID/title/actual phase markers with exact diagnostic UUIDs."
j_msg "-${notice}" -p "Closing a client is not proof of remote logout. No native identity conclusion is automatic."
(( action_rc == 0 && proof_rc == 0 && x11_rc == 0 )) || exit 1
exit 0
