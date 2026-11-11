#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Maintainer-only persistent SDL registration launcher; never requests placement.

Native use requires separate maintainer approval. No production recipe or TLS/NLA
policy is selected here. Keep this foreground supervisor alive until the viewer
exits; Ctrl-C cancels pending registration and stops/reaps only its direct child.
Private stdout/stderr evidence is retained, never printed or automatically deleted.
"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

_libexec = str(Path(__file__).resolve().parents[1] / 'libexec')
if _libexec not in sys.path:
    sys.path.insert(0, _libexec)
import joetoo_kwin_rdp_launch as _runtime

BUS, PATH = _runtime.BUS, _runtime.PATH
DEFAULT_CALL_TIMEOUT_MS = _runtime.DEFAULT_CALL_TIMEOUT_MS
require = _runtime.require
dbus_error_name = _runtime.dbus_error_name
Connection = _runtime.Connection
stop_child = _runtime.stop_child
placement_available = _runtime.placement_available


def launch(*args, **kwargs):
    # Preserve the POC's patchable Connection seam and registration-only default.
    kwargs.setdefault('connection_factory', Connection)
    return _runtime.launch_registration(*args, **kwargs)


def main(argv=None, *, emit=print, on_registered=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('host')
    parser.add_argument('username')
    parser.add_argument('--port', type=int, default=3389)
    parser.add_argument('--desktop', type=int, required=True)
    parser.add_argument('--slot', type=int, required=True)
    parser.add_argument('--call-timeout-ms', type=int, default=DEFAULT_CALL_TIMEOUT_MS)
    # Omission preserves the accepted Wayland wire shape and defaults.
    parser.add_argument('--profile', choices=['sdl-x11-a1c-v1'],
                        help='Explicit legacy native-X11 profile; omission preserves native Wayland')
    # Reuse and explicitly transmit the existing configurable five budgets.
    sys.dont_write_bytecode = True
    installed = Path.home() / '.local/libexec/joetoo_kwin_rdp_launch.py'
    require(installed.is_file() and not installed.is_symlink(), 'Installed adapter missing/unsafe')
    info = installed.stat()
    require(info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o644
            and installed.read_bytes() == (Path(__file__).resolve().parents[1] /
                'libexec/joetoo_kwin_rdp_launch.py').read_bytes(), 'Installed adapter mismatch')
    sys.path.insert(0, str(installed.parent))
    import joetoo_kwin_rdp_launch as adapter
    for name, default in adapter.DEFAULTS.items():
        parser.add_argument('--' + name.replace('_', '-'), type=int, default=default)
    parser.add_argument('--rdp-x11-renderer', choices=['auto', 'software'],
                        help='X11 child-only renderer policy (default: auto); requires --profile')
    parser.add_argument('--rdp-x11-identity-settle-ms', type=int,
                        help='X11 UUID dwell, 1..30000 ms below registration timeout (default: 500)')
    args = parser.parse_args(argv)
    limits = {name: getattr(args, name) for name in adapter.DEFAULTS}
    for name in adapter.X11_DEFAULTS:
        if getattr(args, name) is not None:
            limits[name] = getattr(args, name)
    limits = adapter.settings(limits, args.profile)
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    require(os.geteuid() != 0 and address.startswith('unix:') and ';' not in address,
            'Existing local non-root session bus required')
    require(callable(getattr(os, 'pidfd_open', None)) and callable(getattr(signal, 'pidfd_send_signal', None)),
            'Linux pidfd support required')
    import dbus
    from dbus.types import UnixFd
    interrupted = [False]
    def cancel(signum, frame):
        interrupted[0] = True  # Do cleanup in ordinary control flow, outside handler.
    signal.signal(signal.SIGINT, cancel)
    signal.signal(signal.SIGTERM, cancel)
    return launch(dbus.bus.BusConnection(address), dbus.Interface, UnixFd, adapter,
                  args.host, args.port, args.username, args.desktop, args.slot,
                  limits, args.call_timeout_ms / 1000, cancelled=lambda: interrupted[0], profile=args.profile,
                  emit=emit, on_registered=on_registered)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        # No raw remote/log/credential/argv or D-Bus exception text is exported.
        reason = dbus_error_name(error) or (str(error) if type(error) is RuntimeError else type(error).__name__)
        print('SDL development launcher FAILED: ' + reason, file=sys.stderr)
        sys.exit(1)
