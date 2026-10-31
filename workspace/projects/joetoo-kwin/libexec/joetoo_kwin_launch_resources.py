#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded desktop provisioning and local-path validation; no broker policy."""
import json
import os
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET

INTERFACE = 'org.kde.KWin.VirtualDesktopManager'


def local_path(target, config):
    if any(ord(char) < 32 or ord(char) == 127 for char in target) or '://' in target:
        raise ValueError('Dolphin local target must be a local directory, without controls or URL schemes')
    path = Path(target) if target else Path.home()
    if not path.is_absolute():
        path = Path(config).resolve().parent / path
    path = path.resolve(strict=True)
    if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
        raise ValueError('Dolphin local target must be an existing readable directory')
    return str(path)


class Desktops:
    def __init__(self, bus):
        import dbus
        self.bus = bus
        self.owner = str(bus.get_name_owner('org.kde.KWin'))
        proxy = bus.get_object(self.owner, '/VirtualDesktopManager', introspect=False)
        xml = dbus.Interface(proxy, 'org.freedesktop.DBus.Introspectable').Introspect(timeout=3)
        root = ET.fromstring(str(xml))
        method = root.find(f"./interface[@name='{INTERFACE}']/method[@name='createDesktop']")
        if method is None or [arg.get('type') for arg in method.findall('arg')
                              if arg.get('direction', 'in') == 'in'] != ['u', 's']:
            raise ValueError('supported KWin createDesktop interface unavailable')
        self.properties = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
        self.manager = dbus.Interface(proxy, INTERFACE)

    def snapshot(self):
        if str(self.bus.get_name_owner('org.kde.KWin')) != self.owner:
            raise ValueError('KWin session owner changed')
        values = self.properties.GetAll(INTERFACE, timeout=3)
        entries = sorted((int(item[0]), str(item[1])) for item in values['desktops'])
        count = int(values['count'])
        if (not 1 <= count <= 256 or len(entries) != count or
                [item[0] for item in entries] != list(range(count)) or
                len({item[1] for item in entries if item[1]}) != count):
            raise ValueError('inconsistent KWin desktop inventory')
        return {'owner': self.owner, 'ids': [item[1] for item in entries], 'count': count}

    def append_desktop(self):
        import dbus
        # KWin clamps positions to the current count. UInt32 maximum requests
        # append even if another desktop was added since the inventory read.
        self.manager.createDesktop(dbus.UInt32(0xffffffff), '', timeout=3)

    def ensure(self, required, baseline, create=False):
        if not 1 <= required <= 256:
            raise ValueError('invalid required desktop count')
        if baseline['owner'] != self.owner:
            raise ValueError('KWin session changed since confirmation preflight')
        current = self.snapshot()
        original = baseline['ids']
        if current['ids'][:len(original)] != original:
            raise ValueError('existing desktops removed or reordered since preflight')
        while current['count'] < required:
            if not create:
                raise ValueError(f"required {required}, observed {current['count']} desktops")
            before = current
            # Empty name selects KWin's default. Never remove, rename or switch.
            try:
                self.append_desktop()
            except Exception as exc:
                raise ValueError(f"desktop creation failed: required {required}, observed {before['count']}; partial additions retained: {exc}") from exc
            deadline = time.monotonic() + 2
            while True:
                current = self.snapshot()
                if current['ids'][:len(before['ids'])] != before['ids']:
                    raise ValueError('desktop inventory changed during append')
                if current['count'] > before['count']:
                    break
                if time.monotonic() >= deadline:
                    raise ValueError(f"desktop creation made no progress (capacity/API limit); required {required}, observed {current['count']}; partial additions retained")
                time.sleep(.05)
        return current


def main():
    try:
        mode = sys.argv[1]
        if mode == 'local-path':
            result = local_path(sys.argv[2], sys.argv[3])
        else:
            import dbus
            desktops = Desktops(dbus.SessionBus())
            if mode == 'snapshot':
                result = desktops.snapshot()
            elif mode in ('provision', 'verify'):
                result = desktops.ensure(int(sys.argv[2]), json.loads(sys.argv[3]), mode == 'provision')
            else:
                raise ValueError('unknown resource action')
        print(json.dumps(result))
        return 0
    except Exception as exc:
        print(f'Launch resource check failed: {exc}; no automatic desktop rollback', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
