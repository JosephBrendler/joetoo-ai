#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline worker-file discovery, not a protocol load/connection/authentication test."""
import glob
import json
import mmap
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def worker_present(path):
    try:
        if not path.is_file():
            return False
        with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            # Inspect embedded Qt/KIO metadata; do not dlopen or execute a worker.
            return (data[:4] == b'\x7fELF' and data.find(b'org.kde.kio.worker.sftp') >= 0
                    and data.find(b'KDE-KIO-Protocols') >= 0)
    except (OSError, ValueError):
        return False


def discover_worker(timeout_ms, roots=None, records=None, tools=None, runner=subprocess.run):
    if type(timeout_ms) is not int or not 1 <= timeout_ms <= 10000:
        raise ValueError('SFTP capability discovery timeout must be 1..10000 ms')
    deadline = time.monotonic() + timeout_ms / 1000
    if roots is None:
        roots = [Path(p) for p in os.environ.get('QT_PLUGIN_PATH', '').split(os.pathsep) if p and Path(p).is_absolute()]
    for root in roots:
        path = root / 'kf6/kio/sftp.so'
        if worker_present(path):
            return {'worker': str(path), 'evidence': 'Qt plugin path metadata; remote state unverified'}
    # Gentoo installed-file records also work without Qt development tools and
    # respect the package's actual library/plugin prefix, including non-lib64.
    if records is None:
        records = [Path(p) for p in glob.glob('/var/db/pkg/kde-apps/kio-extras-*/CONTENTS')]
    for record in records:
        try:
            for line in record.read_text().splitlines():
                if line.startswith('obj '):
                    path = Path(line[4:].rsplit(' ', 2)[0])
                    if path.is_absolute() and path.as_posix().endswith('/kf6/kio/sftp.so') and worker_present(path):
                        return {'worker': str(path), 'evidence': 'installed package/worker metadata; remote state unverified'}
        except (OSError, UnicodeError):
            continue
    if tools is None:
        tools = [p for name in ('qtpaths6', 'qtpaths') if (p := shutil.which(name))]
        dolphin = shutil.which('dolphin')
        if dolphin:
            prefix = Path(dolphin).resolve().parent.parent
            tools += [str(p) for p in prefix.glob('lib*/qt6/bin/qtpaths*') if p.is_file() and os.access(p, os.X_OK)]
    for tool in dict.fromkeys(tools):
        def query(key):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(tool, timeout_ms / 1000)
            return runner([tool, '--query', key], capture_output=True, text=True, timeout=remaining, check=True).stdout.strip()
        try:
            if not query('QT_VERSION').startswith('6.'):
                continue
            root = Path(query('QT_INSTALL_PLUGINS'))
            path = root / 'kf6/kio/sftp.so'
            if root.is_absolute() and worker_present(path):
                return {'worker': str(path), 'evidence': 'Qt6 installation/worker metadata; remote state unverified'}
        except (OSError, subprocess.SubprocessError):
            continue
    raise ValueError('Cannot confirm KIO SFTP capability offline; check KDE worker/search paths. A working installation is not disproved.')


def main():
    try:
        print(json.dumps(discover_worker(int(sys.argv[1]))))
        return 0
    except (ValueError, IndexError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
