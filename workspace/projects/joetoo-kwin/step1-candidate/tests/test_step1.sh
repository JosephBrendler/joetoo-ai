#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Headless Step 1 tests — never operate on live KWin or SSH.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
test_dir=$(mktemp -d)
trap 'rm -rf "$test_dir"' EXIT
mkdir -p "$test_dir/bin"

cat > "$test_dir/mock-header" <<'MOCK'
notice=5; err=3
isint() { [[ ${1:-} =~ ^-?[0-9]+$ ]]; }
j_msg() { shift; [[ ${1:-} == -p ]] && shift; printf '%s\n' "$*"; }
separator() { :; }
checknotroot() { :; }
MOCK
sed "s|source /usr/sbin/script_header_joetoo|source \"$test_dir/mock-header\"|" \
    "$script_dir/joetoo-kwin" > "$test_dir/joetoo-kwin"
cp "$script_dir/joetoo-kwin-plan-functions" "$test_dir/"
chmod +x "$test_dir/joetoo-kwin"

cat > "$test_dir/bin/qdbus6" <<'MOCK'
#!/bin/bash
case "$*" in
    *'.Submit '* ) printf '%s\n' 'test-request' ;;
    *'invokeShortcut '* ) exit 0 ;;
    *'.Status '* ) printf '%s\n' 'OK move mock-placement' ;;
    *) echo 'unexpected qdbus6 call' >&2; exit 1 ;;
esac
MOCK
chmod +x "$test_dir/bin/qdbus6"
export PATH="$test_dir/bin:$PATH"

result=$($test_dir/joetoo-kwin -f "$script_dir/desktop_sessions.conf" -c)
[[ $result == *'DRY RUN: [5] windows'* ]]
[[ $result == *'terminal width budget: [87%]'* ]]
[[ $result == *underlay-proposed* ]]
[[ $(printf '%s\n' "$result" | grep -c 'nuthuvia') -eq 2 ]]

result=$($test_dir/joetoo-kwin -m 3 100 80 850 700)
[[ $result == *'OK move mock-placement'* ]]
result=$($test_dir/joetoo-kwin move 1 100 80 850 700)
[[ $result == *'OK move mock-placement'* ]]

if $test_dir/joetoo-kwin -m 0 100 80 850 700 >/dev/null 2>&1; then
    echo 'FAIL: accepted desktop zero' >&2; exit 1
fi
if $test_dir/joetoo-kwin -o >/dev/null 2>&1; then
    echo 'FAIL: executed reserved -o' >&2; exit 1
fi
if $test_dir/joetoo-kwin -c -f "$test_dir/missing.conf" >/dev/null 2>&1; then
    echo 'FAIL: accepted missing config' >&2; exit 1
fi

cat > "$test_dir/five.conf" <<'MOCK'
screen_width=1920
screen_height=1080
desktop_session_list=("1|konsole|ssh|a" "1|konsole|ssh|b" \
    "1|konsole|ssh|c" "1|konsole|ssh|d" "1|konsole|ssh|e")
MOCK
if $test_dir/joetoo-kwin -f "$test_dir/five.conf" -c >/dev/null 2>&1; then
    echo 'FAIL: accepted five Konsole windows on one desktop' >&2; exit 1
fi

cat > "$test_dir/three.conf" <<'MOCK'
screen_width=1000
screen_height=800
desktop_session_list=("1|konsole|ssh|a" "1|vncviewer|via-ssh|a" \
    "1|konsole|ssh|b" "1|konsole|ssh|c")
MOCK
result=$($test_dir/joetoo-kwin -f "$test_dir/three.conf" -c)
[[ $result == *'DRY RUN: [4] windows'* ]]
[[ $result == *'1       4     konsole'* ]]

printf 'PASS: mock CLI, plan, reserved action, and invalid-input checks\n'
