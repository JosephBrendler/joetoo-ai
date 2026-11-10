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


def release(bus, interface, managed_id, desktop, slot, geometry, *, confirmed,
            timeout_ms, poll_ms, call_timeout_ms, emit=print, sleep=time.sleep, clock=time.monotonic):
    connection.require(confirmed is True, 'Explicit --confirm required')
    api = None
    rid = None
    terminal = False
    started = clock()
    def diagnostic(stage, result):
        try:
            print("joetoo-kwin SDL operator diagnostic " + json.dumps(dict(stage=stage,
                request_id=rid, window_uuid=result['window_uuid'],
                elapsed_ms=max(0, int((clock() - started) * 1000))), sort_keys=True), file=sys.stderr, flush=True)
        except Exception:
            pass
    try:
        api = connection.Connection(bus, interface, call_timeout_ms / 1000)
        # No raw UUID is submitted. The broker owns the managed-ID resolution.
        before = api.call('RegistryStatus')
        payload = dict(protocol=1, confirmed=True, managed_id=managed_id,
            action_id=uuid.uuid4().hex, desktop=desktop, slot=slot, **geometry,
            source=before['observation']['source'], revision=before['observation']['revision'], timeout_ms=timeout_ms)
        result = api.call('SubmitSdlPlacement', json.dumps(payload))
        rid = result['request_id']
        expected_uuid = result['window_uuid']
        def valid(value):
            connection.require(value.get('protocol') == 1 and value.get('request_id') == rid
                and re.fullmatch(r'[0-9a-f]{32}', rid) and value.get('window_uuid') == expected_uuid
                and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', expected_uuid)
                and value.get('managed_id') == managed_id and value.get('registration') == 'registered'
                and value.get('remote_session') == 'unverified'
                and value.get('placement') in ('pending', 'succeeded', 'failed'),
                'Placement identity/result mismatch')
        valid(result)
        # Broker owns the mechanical deadline, including its authentication.
        # This later local bound only detects an unresponsive/stuck broker.
        deadline = clock() + timeout_ms / 1000
        if result['placement'] == 'pending':
            # Invoke the dedicated action; never an active-window move shortcut.
            accel = str(api.daemon.GetNameOwner('org.kde.kglobalaccel', timeout=call_timeout_ms / 1000))
            proxy = bus.get_object(accel, '/component/kwin', introspect=False)
            diagnostic('shortcut_dispatch', result)
            interface(proxy, 'org.kde.kglobalaccel.Component').invokeShortcut(
                'joetoo_bridge_sdl_placement', timeout=call_timeout_ms / 1000)
            diagnostic('shortcut_returned', result)
        while result['placement'] == 'pending':
            sleep(min(poll_ms / 1000, max(0, deadline - clock())))
            result = api.call('PollSdlPlacement', rid)
            valid(result)
            connection.require(result['placement'] != 'pending' or clock() < deadline,
                               'Placement broker response deadline expired')
        terminal = True
        emit(json.dumps(result, sort_keys=True))
        return 0 if result['placement'] == 'succeeded' else 1
    finally:
        try:
            if rid is not None and not terminal:
                api.call('CancelSdlPlacement', rid)
        finally:
            bus.close()


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
