#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Maintainer-only Begin/Cancel smoke client. No SDL, Bind or network operation.

Run only after approval in the existing non-root graphical session, from the
checkout. This verification tool is not an installed broker component.
"""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import xml.etree.ElementTree as ET

BUS = 'org.joetoo.KWinBridge'
PATH = '/org/joetoo/KWinBridge'
DEFAULT_CALL_TIMEOUT_MS = 3000


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def smoke(bus, interface, bounds, timeout):
    """One connection, pinned broker owner, two bounded cleanup-proving cycles."""
    daemon = interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus',
                                     introspect=False), 'org.freedesktop.DBus')
    owner = str(daemon.GetNameOwner(BUS, timeout=timeout))
    proxy = bus.get_object(owner, PATH, introspect=False)
    api = interface(proxy, BUS)
    tree = ET.fromstring(interface(proxy, 'org.freedesktop.DBus.Introspectable').Introspect(timeout=timeout))
    methods = {m.get('name'): m for i in tree.findall('interface') if i.get('name') == BUS for m in i.findall('method')}
    for name, signature in {'BeginSdlRegistration': 's', 'BindSdlRegistration': 'sih',
                            'PollSdlRegistration': 's', 'CancelSdlRegistration': 's'}.items():
        require(name in methods, 'SDL method missing')
        args = methods[name].findall('arg')
        require(''.join(a.get('type') for a in args if a.get('direction', 'in') == 'in') == signature
                and ''.join(a.get('type') for a in args if a.get('direction') == 'out') == 's',
                'SDL method signature mismatch')

    def pinned():
        require(str(daemon.GetNameOwner(BUS, timeout=timeout)) == owner, 'Broker owner changed')

    def snapshot():
        pinned()
        status = json.loads(api.RegistryStatus(timeout=timeout))
        managed = json.loads(api.ListManaged(timeout=timeout))
        require(status['observation']['synchronized'] is True, 'Inventory is not synchronized')
        require(not status['initial_layout_active'] and not status['viewer_cleanup_uncertain'], 'Broker is busy')
        require(status['request_counts']['pending'] == status['request_counts']['running'] == 0, 'Active launch exists')
        require(status['managed_count'] == managed['count'] == 0 and managed['windows'] == [],
                'Smoke test requires an empty managed registry')
        require(status['placement_transaction'] == {'id': None, 'state': 'IDLE'}, 'Placement is not idle')
        return status

    before = snapshot()
    previous = None
    active = None
    try:
        for cycle in range(2):
            pinned()
            result = json.loads(api.BeginSdlRegistration(json.dumps(dict(protocol=1, desktop=1, slot=1,
                                                                         bounds=bounds)), timeout=timeout))
            # Retain an ID for best-effort cancellation even if a later schema
            # assertion fails. Never print launch markers or raw D-Bus errors.
            active = result.get('request_id')
            require(isinstance(active, str) and active and active != previous, 'Invalid/new request ID missing')
            require(result['state'] == 'pending' and result['protocol'] == 1
                    and result['placement'] == 'not_requested' and result['remote_session'] == 'unverified',
                    'Unexpected Begin result')
            pinned()
            cancelled = json.loads(api.CancelSdlRegistration(active, timeout=timeout))
            require(cancelled['request_id'] == active and cancelled['state'] == 'failed'
                    and cancelled['reason'] == 'cancelled' and cancelled['protocol'] == 1
                    and cancelled['placement'] == 'not_requested' and cancelled['remote_session'] == 'unverified'
                    and 'managed_id' not in cancelled and 'window_uuid' not in cancelled,
                    'Unexpected cancellation result')
            require(json.loads(api.PollSdlRegistration(active, timeout=timeout)) == cancelled,
                    'Terminal Poll changed')
            require(json.loads(api.CancelSdlRegistration(active, timeout=timeout)) == cancelled,
                    'Repeated cancellation changed')
            previous, active = active, None
            after = snapshot()
            require(after['observation']['source'] == before['observation']['source'], 'Resident source changed')
            require(after['placement_transaction'] == before['placement_transaction'], 'Placement changed')
            require(after['request_count'] == before['request_count'] + cycle + 1
                    and after['request_counts']['failed'] == before['request_counts']['failed'] + cycle + 1,
                    'Unexpected transaction counts/concurrent activity')
        # The second successful Begin proves the first registry reservation was
        # released. Failed terminal records are retained history, not activity.
        return dict(ok=True, cancelled_transactions=2, active_requests=0, managed_count=0,
                    placement='IDLE', broker_owner_unchanged=True, source_unchanged=True)
    finally:
        if active:
            try:
                pinned()
                api.CancelSdlRegistration(active, timeout=timeout)
            except Exception:
                # Caller closes its connection in main, allowing owner-loss
                # cleanup. The failed smoke run must never be reported as PASS.
                pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--call-timeout-ms', type=int, default=DEFAULT_CALL_TIMEOUT_MS)
    args = parser.parse_args()
    require(100 <= args.call_timeout_ms <= 30000, 'Call timeout out of range')
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    require(os.geteuid() != 0 and address.startswith('unix:') and ';' not in address,
            'Existing local non-root session bus required')
    installed = Path.home() / '.local/libexec/joetoo_kwin_rdp_launch.py'
    require(not installed.is_symlink() and installed.is_file(), 'Installed SDL adapter missing/unsafe')
    info = installed.stat()
    require(info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o644,
            'Installed SDL adapter owner/mode mismatch')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(installed.parent))
    import joetoo_kwin_rdp_launch as adapter
    import dbus
    bounds = adapter.settings({})
    bus = dbus.bus.BusConnection(address)  # No session-bus autolaunch.
    try:
        print(json.dumps(smoke(bus, dbus.Interface, bounds, args.call_timeout_ms / 1000), sort_keys=True))
    finally:
        bus.close()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        # Our guard messages are static; D-Bus contributes only its error name.
        reason = str(error) if type(error) is RuntimeError else type(error).__name__
        if callable(getattr(error, 'get_dbus_name', None)):
            reason = error.get_dbus_name()
        print('SDL Begin/Cancel smoke FAILED: ' + reason +
              '; retain terminal output and verify broker cleanup. No SDL client was started.', file=sys.stderr)
        sys.exit(1)
