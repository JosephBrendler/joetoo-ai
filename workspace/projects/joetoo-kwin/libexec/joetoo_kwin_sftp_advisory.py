#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Post-confirmation advisory only. Never substitutes an endpoint or gates launch."""
import ipaddress
import json
import math
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit
from joetoo_kwin_sftp_target import sftp_uri


def resolve(host, timeout_ms, runner=subprocess.run):
    resolver = shutil.which('getent')
    if not resolver:
        return 'unavailable', []
    try:
        result = runner([resolver, 'ahosts', host], capture_output=True, text=True,
                        timeout=timeout_ms / 1000, check=False)
    except subprocess.TimeoutExpired:
        return 'timeout', []
    except (OSError, UnicodeError):
        return 'uncertain', []
    if result.returncode == 2:  # getent: supplied key not found (NSS, not just DNS).
        return 'failed', []
    if result.returncode != 0:
        return 'uncertain', []
    addresses = []
    for line in result.stdout.splitlines():
        try:
            address = str(ipaddress.ip_address(line.split()[0]))
            if address not in addresses:
                addresses.append(address)
        except (ValueError, IndexError):
            continue
    return ('resolved', addresses) if addresses else ('uncertain', [])


def probe_tcp(addresses, port, timeout_ms, runner=subprocess.run):
    probe = shutil.which('nc')
    if not probe:
        return 'unavailable'
    # Match the established nc zero-I/O probe. Numeric addresses and -n avoid
    # another name lookup. The outer subprocess deadline also bounds nc variants
    # whose own -w behavior differs; one budget covers both address families.
    deadline = time.monotonic() + timeout_ms / 1000
    states = []
    for address in addresses:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return 'timeout'
        try:
            result = runner([probe, '-n', '-z', '-w', str(math.ceil(remaining)), address, str(port)],
                            capture_output=True, text=True, timeout=remaining, check=False)
            if result.returncode == 0:
                return 'open'
            # A failed nc check is not proof the host is down. Nonstandard
            # command/option failures are uncertainty, never launch rejection.
            states.append('failed' if result.returncode == 1 and not result.stderr.strip() else 'uncertain')
        except subprocess.TimeoutExpired:
            states.append('timeout')
        except (OSError, UnicodeError):
            states.append('uncertain')
    if 'timeout' in states:
        return 'timeout'
    return 'failed' if states and all(s == 'failed' for s in states) else 'uncertain'


def advisory(target, timeout_ms, default_port, resolver=None, connector=None):
    if type(timeout_ms) is not int or not 1 <= timeout_ms <= 10000:
        raise ValueError('Invalid advisory timeout')
    if type(default_port) is not int or not 1 <= default_port <= 65535:
        raise ValueError('Invalid advisory port')
    parsed = urlsplit(sftp_uri(target))
    host, port = parsed.hostname, parsed.port or default_port
    try:
        addresses = [str(ipaddress.ip_address(host))]
        resolution = 'numeric'
    except ValueError:
        resolution, addresses = (resolver or resolve)(host, timeout_ms)
    connectivity = (connector or probe_tcp)(addresses, port, timeout_ms) if addresses else 'skipped'
    warning = ''
    if resolution == 'failed':
        warning = f'local name resolution failed for [{host}]'
    elif resolution in ('timeout', 'unavailable', 'uncertain'):
        warning = f'local name-resolution advisory {resolution} for [{host}]; TCP check skipped'
    elif connectivity == 'failed':
        warning = f'remote host TCP connectivity check failed for [{host}] port [{port}]; this is not proof the host is down'
    elif connectivity in ('timeout', 'unavailable', 'uncertain'):
        warning = f'TCP connectivity advisory {connectivity} for [{host}] port [{port}]'
    if warning:
        if 'timeout' in (resolution, connectivity):
            warning += '; more time may be needed: set sftp_advisory_timeout_ms in the selected configuration'
        warning = ('SFTP advisory: ' + warning +
                   '; KIO/SSH configuration may differ. Launching app [Dolphin] with the requested SFTP URL anyway.')
    return {'resolution': resolution, 'tcp': connectivity, 'port': port, 'warning': warning}


def main():
    try:
        print(json.dumps(advisory(sys.stdin.read(), int(sys.argv[1]), int(sys.argv[2]))))
    except Exception:
        # Advisory failure is uncertainty, never a launch veto or raw-URI dump.
        print(json.dumps({'warning': 'SFTP advisory: check inconclusive; launching Dolphin anyway.',
                          'resolution': 'uncertain', 'tcp': 'skipped'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
