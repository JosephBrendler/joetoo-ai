#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline configured RDP endpoint/sizing contract; no display, process or network API.

The development adapter's fixed argv is intentionally independent. Stage 2 can
consume sizing_arguments() after validation; it must separately prove the actual
windowing backend. 'auto' here is intent, never permission to assume Wayland.
"""
import ipaddress
import json
import re
import sys

DEFAULTS = dict(rdp_remote_width=1024, rdp_remote_height=768, RDP_SMART_SIZING=True,
                rdp_initial_client_width=800, rdp_initial_client_height=600,
                rdp_windowing_backend='auto', rdp_security_protocol='nla',
                rdp_certificate_policy='strict')
# Application policy: bound pathological/tiny allocations, below FreeRDP 3.32.1's
# UINT16_MAX size parser ceiling. This is not server/renderer capability proof.
DIMENSION_BOUNDS = (64, 8192)
TARGET_BYTE_LIMIT = 4096


def target(text):
    """Strict ASCII authority; plain account, DNS/IPv4 or bracketed IPv6 only."""
    try:
        if (not isinstance(text, str) or len(text) > TARGET_BYTE_LIMIT or not text.isascii()
                or any(ord(c) <= 32 or ord(c) >= 127 for c in text)):
            raise ValueError()
        match = re.fullmatch(r'rdp://(?P<user>[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})@'
                             r'(?P<host>\[[0-9A-Fa-f:.]+\]|[A-Za-z0-9.-]+)'
                             r'(?::(?P<port>[1-9][0-9]{0,4}))?', text)
        if not match:
            raise ValueError()
        user, host = match['user'], match['host']
        port = int(match['port']) if match['port'] is not None else 3389
        if not 1 <= port <= 65535:
            raise ValueError()
        if host.startswith('['):
            host = str(ipaddress.IPv6Address(host[1:-1]))
        elif re.fullmatch(r'[0-9.]+', host):
            host = str(ipaddress.IPv4Address(host))
        elif (len(host) > 253 or not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
                                       for label in host.split('.'))):
            raise ValueError()
        return dict(user=user, host=host, port=port)
    except (ValueError, TypeError):
        # ipaddress and other parser errors may include input. Never forward them.
        raise ValueError('Invalid RDP target (redacted); expected rdp://USER@HOST[:PORT]') from None


def settings(data):
    if not isinstance(data, dict) or set(data) - set(DEFAULTS):
        raise ValueError('Unknown RDP configuration setting')
    result = dict(DEFAULTS)
    for name, default in DEFAULTS.items():
        value = data.get(name, default)
        if name == 'rdp_windowing_backend':
            if value not in ('auto', 'wayland', 'x11'):
                raise ValueError('Invalid rdp_windowing_backend; expected auto, wayland or x11')
        elif name in ('rdp_security_protocol', 'rdp_certificate_policy'):
            allowed = ('nla', 'negotiate') if name == 'rdp_security_protocol' else ('strict', 'prompt')
            if not isinstance(value, str) or value not in allowed:
                raise ValueError('Invalid RDP security policy (redacted)')
        elif name == 'RDP_SMART_SIZING':
            # Trusted Bash uses TRUE=0, FALSE="". JSON callers use actual bools;
            # do not accept truthy strings, numeric booleans or shell expressions.
            if type(value) is bool:
                pass
            elif type(value) is str and value in ('0', ''):
                value = value == '0'
            else:
                raise ValueError('Invalid RDP_SMART_SIZING; use joetoo TRUE/FALSE')
        else:
            if isinstance(value, str) and re.fullmatch(r'[1-9][0-9]{0,3}', value):
                value = int(value)
            low, high = DIMENSION_BOUNDS
            if type(value) is not int or not low <= value <= high:
                raise ValueError('RDP dimensions must be decimal integers in 64..8192 pixels')
        result[name] = value
    return result


def sizing_arguments(data):
    """Pure Stage 2 mapping; no outer-frame allocation or client invocation.

    FreeRDP 3.32.1 client/common/cmdline.c parse_size_options() and
    parse_smart_sizing_options() support these forms, including explicit off.
    No dynamic-resolution, security or decoration-offset policy is added.
    """
    s = settings(data)
    return [f"/size:{s['rdp_remote_width']}x{s['rdp_remote_height']}",
            (f"/smart-sizing:{s['rdp_initial_client_width']}x{s['rdp_initial_client_height']}"
             if s['RDP_SMART_SIZING'] else '/smart-sizing:off')]


def security_arguments(data):
    """Map validated policy enums only; omission deliberately selects stock defaults."""
    s = settings(data)
    result = []
    if s['rdp_security_protocol'] == 'nla':
        result.append('/sec:nla')
    if s['rdp_certificate_policy'] == 'strict':
        result.append('/cert:deny')
    return result


def registration_bounds(data, backend):
    """Offline delegation to the existing import-safe identity budget validator."""
    from joetoo_kwin_rdp_launch import settings as bounds_settings, DEFAULTS as bounds_defaults, X11_PROFILE
    if backend not in ('auto', 'wayland', 'x11'):
        raise ValueError('Invalid backend intent')
    result = bounds_settings(data, X11_PROFILE)
    return {k: v for k, v in result.items() if backend != 'wayland' or k in bounds_defaults}


def main():
    try:
        if sys.argv[1:] == ['--target']:
            value = target(sys.stdin.read(TARGET_BYTE_LIMIT + 1))
        elif sys.argv[1:2] == ['--bounds'] and len(sys.argv[2:]) == 8:
            from joetoo_kwin_rdp_launch import DEFAULTS as bounds_defaults, X11_DEFAULTS
            names = list(bounds_defaults) + list(X11_DEFAULTS)
            value = registration_bounds(dict(zip(names, sys.argv[3:])), sys.argv[2])
        elif sys.argv[1:2] == ['--settings'] and len(sys.argv[2:]) == len(DEFAULTS):
            value = settings(dict(zip(DEFAULTS, sys.argv[2:])))
        else:
            raise ValueError('Invalid RDP validator invocation')
        print(json.dumps(value, sort_keys=True))
        return 0
    except (ValueError, TypeError, UnicodeError, ImportError):
        # Fixed error also covers malformed configuration, never argv/input text.
        print('Invalid RDP target/settings (redacted)', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
