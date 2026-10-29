#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate an exact-baseline Step 1.4d managed-launch patch (no auto-apply).

Read the existing user-owned joetoo-ai task-branch source, validate original
Git blob hashes, then produce a reviewable unified patch on stdout.
No repository file is modified by this generator.
"""

import difflib
from pathlib import Path
import subprocess
import sys

ROOT_REL = "workspace/projects/joetoo-kwin/"
EXPECTED = {'workspace/projects/joetoo-kwin/libexec/joetoo-kwind': 'b838345f55855bcbacdebf16968cde416f29374c',
 'workspace/projects/joetoo-kwin/joetoo-kwin': '13143ce01a1c5545580308aae31c5629354575e9',
 'workspace/projects/joetoo-kwin/tests/test_step1_4d_cli.py': '51fb045de51247f02c5c49f8a36f93ddeb9aacab'}
REPLACEMENTS = {'workspace/projects/joetoo-kwin/libexec/joetoo-kwind': [('        return r["state"] + (" " + r["detail"] if '
                                                          'r["detail"] else "")\n'
                                                          '\n'
                                                          '\n'
                                                          '    # Step 1.3b.1: a read-only launch correlation probe. It '
                                                          'does not replace\n',
                                                          '        return r["state"] + (" " + r["detail"] if '
                                                          'r["detail"] else "")\n'
                                                          '\n'
                                                          '    # Step 1.4d: a launch-intent interface, NOT an '
                                                          'arbitrary registration API.\n'
                                                          '    # The broker alone creates registration records, after '
                                                          'exact PID/UUID\n'
                                                          '    # correlation; clients cannot provide a window UUID or '
                                                          'managed ID.\n'
                                                          '    @dbus.service.method(IFACE, in_signature="siiiiii", '
                                                          'out_signature="s")\n'
                                                          '    def SubmitManagedLaunch(self, app_class, desktop, slot, '
                                                          'x, y, width, height):\n'
                                                          '        """Atomically arm placement and broker-owned '
                                                          'managed correlation."""\n'
                                                          '        if not isinstance(slot, int) or isinstance(slot, '
                                                          'bool) or not 1 <= slot <= 256:\n'
                                                          '            raise dbus.DBusException("Invalid launch slot", '
                                                          'name=IFACE + ".BadArguments")\n'
                                                          '        previous_request = self.request\n'
                                                          '        placement_id = self._submit("launch", desktop, x, '
                                                          'y, width, height, app_class)\n'
                                                          '        try:\n'
                                                          '            registration_id = self._begin_managed_launch(\n'
                                                          '                expected_class=app_class,\n'
                                                          '                recipe={"desktop": int(desktop), "slot": '
                                                          'int(slot),\n'
                                                          '                        "program": str(app_class), "mode": '
                                                          '"local", "target": ""})\n'
                                                          '        except RegistryError as exc:\n'
                                                          '            # Both arms must succeed or neither may remain '
                                                          'active. Since D-Bus\n'
                                                          '            # dispatch is single-threaded here, no resident '
                                                          'event can consume\n'
                                                          '            # the newly created placement request before '
                                                          'this method returns.\n'
                                                          '            self.request = previous_request\n'
                                                          '            raise dbus.DBusException(str(exc), name=IFACE + '
                                                          '".InvalidRequest") from exc\n'
                                                          '        return json.dumps({"placement_request_id": '
                                                          'placement_id,\n'
                                                          '                           "registration_request_id": '
                                                          'registration_id}, sort_keys=True)\n'
                                                          '\n'
                                                          '    @dbus.service.method(IFACE, in_signature="si", '
                                                          'out_signature="")\n'
                                                          '    def SetManagedLaunchPid(self, request_id, pid):\n'
                                                          '        """Supply the freshly spawned child\'s PID; never '
                                                          'choose a KWin UUID."""\n'
                                                          '        if not isinstance(pid, int) or isinstance(pid, '
                                                          'bool) or pid <= 0:\n'
                                                          '            raise dbus.DBusException("Invalid launch PID", '
                                                          'name=IFACE + ".BadArguments")\n'
                                                          '        try:\n'
                                                          '            self._set_managed_launch_pid(request_id, pid)\n'
                                                          '        except RegistryError as exc:\n'
                                                          '            raise dbus.DBusException(str(exc), name=IFACE + '
                                                          '".InvalidRequest") from exc\n'
                                                          '\n'
                                                          '    @dbus.service.method(IFACE, in_signature="s", '
                                                          'out_signature="s")\n'
                                                          '    def PollManagedLaunch(self, request_id):\n'
                                                          '        """Report privately verified registration; caller '
                                                          'supplies no UUID."""\n'
                                                          '        return '
                                                          'json.dumps(self._poll_managed_launch(request_id), '
                                                          'sort_keys=True)\n'
                                                          '\n'
                                                          '\n'
                                                          '    # Step 1.3b.1: a read-only launch correlation probe. It '
                                                          'does not replace\n')],
 'workspace/projects/joetoo-kwin/joetoo-kwin': [('    j_msg "-${notice}" -p "       ${PN} test-multi-launch  (TEST '
                                                 'ONLY: 4 local Konsoles, fixed 1920x1080)"\n'
                                                 '    j_msg "-${notice}" -p "       ${PN} -h"\n',
                                                 '    j_msg "-${notice}" -p "       ${PN} test-multi-launch  (TEST '
                                                 'ONLY: register 4 local Konsoles)"\n'
                                                 '    j_msg "-${notice}" -p "       ${PN} -h"\n'),
                                                ('# Step 1.4d native placement fixture, not the configured -o '
                                                 'launcher.\n'
                                                 '# The four coordinates deliberately describe one 1920x1080 test '
                                                 'display.\n'
                                                 '# These are fixed TEST VALUES; the shared geometry policy belongs to '
                                                 'Step 1.5.\n'
                                                 '# This exercises SubmitLaunch/Status and does NOT enroll managed '
                                                 'windows.\n'
                                                 'test_multi_launch() {\n',
                                                 '# Step 1.4d native registration test fixture, not the configured -o '
                                                 'launcher.\n'
                                                 '# The four coordinates deliberately describe one 1920x1080 test '
                                                 'display.\n'
                                                 '# These are fixed TEST VALUES; the shared geometry policy belongs to '
                                                 'Step 1.5.\n'
                                                 '# Each launch must become managed by positive PID/UUID correlation.\n'
                                                 'test_multi_launch() {\n'),
                                                ('# Step 1.4d native registration test fixture, not the configured -o '
                                                 'launcher.\n'
                                                 '# The four coordinates deliberately describe one 1920x1080 test '
                                                 'display.\n'
                                                 '# These are fixed TEST VALUES; the shared geometry policy belongs to '
                                                 'Step 1.5.\n'
                                                 '# Each launch must become managed by positive PID/UUID correlation.\n'
                                                 'test_multi_launch() {\n',
                                                 '# Managed launch test entry point. The broker owns the registry and '
                                                 'performs\n'
                                                 '# all UUID selection; the Bash client supplies only intent and its '
                                                 'child PID.\n'
                                                 'launch_managed_window() {\n'
                                                 '    local _lm_class=$1 _lm_slot=$2 _lm_payload _lm_placement '
                                                 '_lm_registration\n'
                                                 '    local _lm_pid _lm_result _lm_state _lm_attempt '
                                                 '_lm_registration_rc=1\n'
                                                 '    local _lm_placement_rc=1\n'
                                                 '    shift 2\n'
                                                 '    if (( $# < 7 )) || [[ ${6:-} != -- || -z ${7:-} ]]; then\n'
                                                 "        bad_args 'managed test launch requires CLASS SLOT DESKTOP X "
                                                 "Y WIDTH HEIGHT -- PROGRAM [ARG ...]'\n"
                                                 '        return 2\n'
                                                 '    fi\n'
                                                 '    validate_geometry "$1" "$2" "$3" "$4" "$5" || return $?\n'
                                                 '    if ! isint "$_lm_slot" || (( _lm_slot < 1 || _lm_slot > 256 )); '
                                                 'then\n'
                                                 '        j_msg "-${err}" -p "${PN}: invalid test slot [${_lm_slot}]"\n'
                                                 '        return 2\n'
                                                 '    fi\n'
                                                 '    if [[ -z $_lm_class || ${#_lm_class} -gt 128 ]]; then\n'
                                                 '        j_msg "-${err}" -p "${PN}: invalid expected KWin class"\n'
                                                 '        return 2\n'
                                                 '    fi\n'
                                                 '    local -a _lm_geometry=("$1" "$2" "$3" "$4" "$5")\n'
                                                 '    shift 6\n'
                                                 '    if ! command -v "$1" >/dev/null 2>&1; then\n'
                                                 '        j_msg "-${err}" -p "${PN}: program not found [${1}]"\n'
                                                 '        return 1\n'
                                                 '    fi\n'
                                                 '    _lm_payload=$(qdbus6 "$bus" "$path" "$iface.SubmitManagedLaunch" '
                                                 '\\\n'
                                                 '        "$_lm_class" "${_lm_geometry[0]}" "$_lm_slot" '
                                                 '"${_lm_geometry[@]:1}") || return 1\n'
                                                 "    _lm_placement=$(jq -er '.placement_request_id | select(type == "
                                                 '"string" and length > 0)\' \\\n'
                                                 '        <<< "$_lm_payload") || return 1\n'
                                                 "    _lm_registration=$(jq -er '.registration_request_id | "
                                                 'select(type == "string" and length > 0)\' \\\n'
                                                 '        <<< "$_lm_payload") || return 1\n'
                                                 '    j_msg "-${notice}" -p "Armed managed launch '
                                                 '[${_lm_registration}], placement [${_lm_placement}]"\n'
                                                 '    "$@" &\n'
                                                 '    _lm_pid=$!\n'
                                                 '    j_msg "-${notice}" -p "Launched [${1}], shell PID [${_lm_pid}]"\n'
                                                 '    if ! qdbus6 "$bus" "$path" "$iface.SetManagedLaunchPid" '
                                                 '"$_lm_registration" "$_lm_pid"; then\n'
                                                 '        j_msg "-${err}" -p "${PN}: managed PID handoff failed for '
                                                 '[${_lm_registration}]"\n'
                                                 '        return 1\n'
                                                 '    fi\n'
                                                 '    # Correlation has a 15-second deadline. Poll it before the '
                                                 'potentially\n'
                                                 '    # 15-second placement wait so the quiet-period match can '
                                                 'complete.\n'
                                                 '    for ((_lm_attempt=0; _lm_attempt<150; _lm_attempt++)); do\n'
                                                 '        _lm_result=$(qdbus6 "$bus" "$path" '
                                                 '"$iface.PollManagedLaunch" "$_lm_registration") || return 1\n'
                                                 '        _lm_state=$(jq -er \'.state | select(type == "string")\' <<< '
                                                 '"$_lm_result") || return 1\n'
                                                 '        case $_lm_state in\n'
                                                 '            registered)\n'
                                                 '                j_msg "-${notice}" -p "Registered [$(jq -r '
                                                 '\'.managed_id\' <<< "$_lm_result")] UUID [$(jq -r \'.window_uuid\' '
                                                 '<<< "$_lm_result")]"\n'
                                                 '                _lm_registration_rc=0\n'
                                                 '                break ;;\n'
                                                 '            pending) sleep 0.1 ;;\n'
                                                 '            failed|timeout|ambiguous|UNKNOWN)\n'
                                                 '                j_msg "-${err}" -p "${PN}: managed registration '
                                                 '[${_lm_state}]: ${_lm_result}"\n'
                                                 '                break ;;\n'
                                                 '            *) j_msg "-${err}" -p "${PN}: unexpected registration '
                                                 'result: ${_lm_result}"; break ;;\n'
                                                 '        esac\n'
                                                 '    done\n'
                                                 '    if wait_for_request "$_lm_placement" launch; then\n'
                                                 '        _lm_placement_rc=0\n'
                                                 '    fi\n'
                                                 '    (( _lm_registration_rc == 0 && _lm_placement_rc == 0 ))\n'
                                                 '}\n'
                                                 '\n'
                                                 '# Step 1.4d native registration test fixture, not the configured -o '
                                                 'launcher.\n'
                                                 '# The four coordinates deliberately describe one 1920x1080 test '
                                                 'display.\n'
                                                 '# These are fixed TEST VALUES; the shared geometry policy belongs to '
                                                 'Step 1.5.\n'
                                                 '# Each launch must become managed by positive PID/UUID correlation.\n'
                                                 'test_multi_launch() {\n'),
                                                ('test_multi_launch() {\n'
                                                 '    local _tml_desktop _tml_x _tml_failed=0\n'
                                                 '    j_msg "-${notice}" -p "${PN}: TEST ONLY: four local Konsole '
                                                 'windows on desktops 1 and 2"\n'
                                                 '    for _tml_desktop in 1 2; do\n'
                                                 '        for _tml_x in 19 873; do\n',
                                                 'test_multi_launch() {\n'
                                                 '    local _tml_desktop _tml_x _tml_slot _tml_failed=0\n'
                                                 '    j_msg "-${notice}" -p "${PN}: TEST ONLY: register four local '
                                                 'Konsole windows on desktops 1 and 2"\n'
                                                 '    for _tml_desktop in 1 2; do\n'
                                                 '        _tml_slot=0\n'
                                                 '        for _tml_x in 19 873; do\n'
                                                 '            _tml_slot=$((_tml_slot + 1))\n'),
                                                ('            if launch_one_window konsole "$_tml_desktop" "$_tml_x" '
                                                 '54 816 918 -- konsole --separate; then\n',
                                                 '            if launch_managed_window konsole "$_tml_slot" '
                                                 '"$_tml_desktop" "$_tml_x" 54 816 918 -- konsole --separate; then\n'),
                                                ('    j_msg "-${notice}" -p "${PN}: four placement requests completed; '
                                                 'managed registration was NOT tested"\n',
                                                 '    j_msg "-${notice}" -p "${PN}: all four test launches registered '
                                                 'and placement succeeded"\n')],
 'workspace/projects/joetoo-kwin/tests/test_step1_4d_cli.py': [('"""Headless tests for the deliberately non-managed '
                                                                '1.4d launch fixture."""\n',
                                                                '"""Headless tests for the Step 1.4d native '
                                                                'managed-launch fixture."""\n'),
                                                               ('                launch_one_window() {\n',
                                                                '                launch_managed_window() {\n'),
                                                               ("            'konsole 1 19 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 1 873 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 2 19 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 2 873 54 816 918 -- konsole "
                                                                "--separate'])\n",
                                                                "            'konsole 1 1 19 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 2 1 873 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 1 2 19 54 816 918 -- konsole "
                                                                "--separate',\n"
                                                                "            'konsole 2 2 873 54 816 918 -- konsole "
                                                                "--separate'])\n"),
                                                               ('                    if [[ ${FAIL_LAUNCH:-0} == 1 && '
                                                                '$2 == 2 && $3 == 873 ]]; then\n',
                                                                '                    if [[ ${FAIL_LAUNCH:-0} == 1 && '
                                                                '$3 == 2 && $4 == 873 ]]; then\n'),
                                                               ("        self.assertNotIn('Register', fixture)\n"
                                                                "        self.assertNotIn('BeginManaged', fixture)\n",
                                                                "        self.assertIn('launch_managed_window', "
                                                                'fixture)\n'
                                                                "        self.assertNotIn('RegisterWindow', "
                                                                'fixture)\n')]}
ADDED = {"tests/test_step1_4d_managed_ipc.py": "tests/test_step1_4d_managed_ipc.py",
         "tests/test_step1_4d_managed_cli.py": "tests/test_step1_4d_managed_cli.py"}


def main():
    if len(sys.argv) != 1:
        raise SystemExit("No arguments; redirects stdout to patch file. No source modifications.")
    root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip())
    branch = subprocess.check_output(["git", "branch", "--show-current"],
                                     cwd=root, text=True).strip()
    if branch != "task/joetoo-kwin-step1.4d-multiwindow-validation":
        raise SystemExit(f"Refusing unexpected branch: {branch!r}")
    output = []
    for name, edits in REPLACEMENTS.items():
        target = root / name
        if not target.is_file():
            raise SystemExit(f"Missing source: {target}")
        actual_hash = subprocess.check_output(["git", "hash-object", str(target)],
                                              cwd=root, text=True).strip()
        if actual_hash != EXPECTED[name]:
            raise SystemExit(f"Source has changed, refusing stale patch: {name}\n"
                             f"expected {EXPECTED[name]}, got {actual_hash}")
        original = target.read_text()
        updated = original
        for old, new in edits:
            count = updated.count(old)
            if count != 1:
                raise SystemExit(f"Expected one anchor, found {count}: {name}: {old[:80]!r}")
            updated = updated.replace(old, new, 1)
        diff = ''.join(difflib.unified_diff(
            original.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile=f"a/{name}", tofile=f"b/{name}", n=3))
        if not diff:
            raise SystemExit(f"No changes: {name}")
        output.append(f"diff --git a/{name} b/{name}\n"+diff)
    for short, relative in ADDED.items():
        name = ROOT_REL + short
        if (root/name).exists():
            raise SystemExit(f"Refusing to replace existing new-test file: {name}")
        source = (Path(__file__).resolve().parent / relative).read_text()
        if not source.endswith('\n'):
            raise SystemExit(f"Missing final newline: {relative}")
        diff = ''.join(difflib.unified_diff(
            [],source.splitlines(keepends=True),
            fromfile="/dev/null",tofile="b/"+name,n=3))
        output.append(f"diff --git a/{name} b/{name}\nnew file mode 100644\n"+diff)
    sys.stdout.write(''.join(output))


if __name__ == '__main__':
    main()
