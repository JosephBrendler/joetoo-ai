#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit operator placement of a registered SDL viewer; never launches a client.

Use from another Konsole while the original SDL supervisor is still running.
--confirm records an operator decision, not proof of remote authentication.
Geometry is explicit policy, not another layout calculator. No active-window lookup.
"""
import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
import sys
import time
import uuid

# Reuse the existing persistent, pinned broker connection and safe error names.
spec = importlib.util.spec_from_file_location('sdl_registration_connection',
    Path(__file__).with_name('joetoo-sdl-registration-launch.py'))
connection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connection)


def release(*args, **kwargs):
    # Same operator tool; the production module owns reusable mechanics.
    kwargs.setdefault('connection_factory', connection.Connection)
    return connection._runtime.release_placement(*args, **kwargs)


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'libexec'))
    from joetoo_kwin_rdp_launch import DEFAULTS, settings
    from joetoo_kwin_vnc_target import DEFAULTS as mechanical_defaults, settings as mechanical_settings
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('managed_id')
    parser.add_argument('--confirm', action='store_true', help='Release after inspecting the actual viewer')
    for name in ('desktop', 'slot', 'x', 'y', 'width', 'height'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--timeout-ms', type=int, default=mechanical_defaults['vnc_placement_timeout_ms'])
    parser.add_argument('--poll-ms', type=int, default=DEFAULTS['rdp_registration_poll_ms'])
    parser.add_argument('--call-timeout-ms', type=int, default=mechanical_defaults['vnc_dbus_timeout_ms'])
    args = parser.parse_args()
    connection.require(args.confirm, 'Explicit --confirm required')
    mechanical_settings({'vnc_placement_timeout_ms': args.timeout_ms, 'vnc_dbus_timeout_ms': args.call_timeout_ms})
    settings({'rdp_registration_poll_ms': args.poll_ms})
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    connection.require(os.geteuid() != 0 and address.startswith('unix:') and ';' not in address,
                       'Existing non-root local session bus required')
    import dbus
    return release(dbus.bus.BusConnection(address), dbus.Interface, args.managed_id,
        args.desktop, args.slot, {k: getattr(args, k) for k in ('x', 'y', 'width', 'height')},
        confirmed=args.confirm, timeout_ms=args.timeout_ms, poll_ms=args.poll_ms, call_timeout_ms=args.call_timeout_ms)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('SDL placement cancelled', file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        reason = connection.dbus_error_name(error) or (str(error) if type(error) is RuntimeError else type(error).__name__)
        print('SDL placement FAILED: ' + reason, file=sys.stderr)
        sys.exit(1)
