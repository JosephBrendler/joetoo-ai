#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline URL-only VNC-over-SSH target and operational-bound validation."""
import ipaddress
import json
import re
import sys

DEFAULTS = dict(vnc_ssh_start_timeout_ms=10000, vnc_viewer_ready_timeout_ms=300000,
                vnc_supervisor_poll_interval_ms=100, vnc_cleanup_timeout_ms=2000,
                vnc_local_port_attempts=3, vnc_identity_event_limit=256,
                vnc_identity_settle_ms=500, vnc_dbus_timeout_ms=3000, vnc_placement_timeout_ms=15000, vnc_identity_start_timeout_ms=1000)
BOUNDS = dict(vnc_ssh_start_timeout_ms=(100,120000), vnc_viewer_ready_timeout_ms=(1000,3600000),
              vnc_supervisor_poll_interval_ms=(10,1000), vnc_cleanup_timeout_ms=(100,30000),
              vnc_local_port_attempts=(1,20), vnc_identity_event_limit=(16,4096),
              vnc_identity_settle_ms=(10,2000), vnc_dbus_timeout_ms=(100,30000), vnc_placement_timeout_ms=(100,15000), vnc_identity_start_timeout_ms=(100,10000))


def settings(data):
    result = {}
    for name, default in DEFAULTS.items():
        value = data.get(name, default)
        if isinstance(value,str) and re.fullmatch(r'[1-9][0-9]{0,6}',value): value=int(value)
        lo, hi = BOUNDS[name]
        if type(value) is not int or not lo <= value <= hi:
            raise ValueError('Invalid VNC operational bounds')
        result[name]=value
    if result['vnc_identity_settle_ms'] >= result['vnc_viewer_ready_timeout_ms']:
        raise ValueError('Invalid VNC settling interval')
    if result['vnc_identity_start_timeout_ms'] >= result['vnc_dbus_timeout_ms']:
        raise ValueError('Identity startup bound must be below the D-Bus bound')
    return result


def target(text):
    if not isinstance(text,str) or not text.isascii() or re.search(r'[\s\\%?#|]',text):
        raise ValueError('Invalid VNC SSH target (redacted)')
    match=re.fullmatch(r'ssh://(?:(?P<user>[A-Za-z0-9_][A-Za-z0-9_.-]*)@)?(?P<host>\[[0-9A-Fa-f:]+\]|[A-Za-z0-9_][A-Za-z0-9_.-]*)(?::(?P<port>[1-9][0-9]{0,4}))?/(?P<kind>display|port)/(?P<number>0|[1-9][0-9]{0,4})',text)
    if not match: raise ValueError('Invalid VNC SSH target (redacted)')
    parts=match.groupdict(); host=parts['host']
    if host.startswith('['): host=str(ipaddress.IPv6Address(host[1:-1]))
    elif re.fullmatch(r'[0-9.]+',host): host=str(ipaddress.IPv4Address(host))
    elif '..' in host or host.endswith('..'): raise ValueError('Invalid VNC SSH host')
    port=int(parts['port']) if parts['port'] else None
    remote=int(parts['number']) + (5900 if parts['kind']=='display' else 0)
    if (port is not None and port>65535) or not 1<=remote<=65535:
        raise ValueError('Invalid VNC port')
    return dict(host=host,user=parts['user'],ssh_port=port,vnc_port=remote)


if __name__=='__main__':
    try:
        if sys.argv[1:2] == ['--target']:
            print(json.dumps(target(sys.stdin.read())))
        elif sys.argv[1:2] == ['--settings']:
            if len(sys.argv[2:]) != len(DEFAULTS): raise ValueError('Invalid VNC settings')
            print(json.dumps(settings(dict(zip(DEFAULTS,sys.argv[2:])))))
        else:
            data=json.load(sys.stdin)
            print(json.dumps(dict(endpoint=target(data['target']),bounds=settings(data))))
    except (ValueError,KeyError,TypeError):
        print('Invalid VNC target/settings (entry redacted)',file=sys.stderr);sys.exit(2)
