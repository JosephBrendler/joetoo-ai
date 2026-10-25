#!/bin/bash
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
#

# 


if [[ $# -ne 3 && $# -ne 5 ]]; then
    echo "Usage: ${0##*/} DESKTOP X Y [WIDTH HEIGHT]" >&2
    exit 2
fi

desktop=$1
x=$2
y=$3
width=${4:-0}
height=${5:-0}

script=/home/joe/scratch/joetoo-move-test.js
name=joetoo-move-test

# Remove any previous copy of this test script
qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.unloadScript "$name" \
    >/dev/null 2>&1 || :

# Load it into KWin
id=$(qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.loadScript "$script" "$name") || exit 1

[[ "$id" =~ ^[0-9]+$ ]] || {
    echo "Invalid KWin script ID: $id"
    exit 1
}

# Execute the script
qdbus6 org.kde.KWin "/Scripting/Script$id" \
    org.kde.kwin.Script.run

# Stop and unload it
qdbus6 org.kde.KWin "/Scripting/Script$id" \
    org.kde.kwin.Script.stop

qdbus6 org.kde.KWin /Scripting \
    org.kde.kwin.Scripting.unloadScript "$name"

