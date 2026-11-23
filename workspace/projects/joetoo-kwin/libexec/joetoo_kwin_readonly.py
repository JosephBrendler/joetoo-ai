#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate and render bounded read-only joetoo-kwind query replies.

The Bash CLI owns the D-Bus call and passes its reply on descriptor 3.
No config sourcing, D-Bus calls, registry changes, or window operations here.
"""
import json
import os
import re
import sys
import uuid


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate key')
        obj[key] = value
    return obj


def obj(value):
    if not isinstance(value, dict):
        raise ValueError('expected object')
    return value


def integer(value, minimum=0, maximum=1000000000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('invalid integer')
    return value


def boolean(value):
    if type(value) is not bool:
        raise ValueError('invalid boolean')
    return value


def token(value, pattern=r'[a-z_]{1,48}'):
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError('invalid token')
    return value


def validate_status(data):
    data = obj(data)
    managed = integer(data['managed_count'])
    presence = obj(data['presence_counts'])
    if set(presence) != {'present', 'missing', 'uncertain'}:
        raise ValueError('presence fields')
    for key in presence:
        integer(presence[key])
    if sum(presence.values()) != managed:
        raise ValueError('presence total')
    requests = integer(data['request_count'])
    states = obj(data['request_counts'])
    if set(states) != {'pending', 'running', 'succeeded', 'failed', 'timeout', 'ambiguous'}:
        raise ValueError('request fields')
    for key in states:
        integer(states[key])
    if sum(states.values()) != requests:
        raise ValueError('request total')
    transaction = obj(data['placement_transaction'])
    state = token(transaction['state'], r'[A-Z_]{1,32}')
    # The broker retains the latest completed placement, including OK/ERROR.
    # Only PENDING/RUNNING/VERIFYING are in-flight transactions.
    if state not in ('IDLE', 'PENDING', 'RUNNING', 'VERIFYING', 'OK', 'ERROR'):
        raise ValueError('unknown placement transaction state')
    request_id = transaction['id']
    if state == 'IDLE':
        if request_id is not None:
            raise ValueError('idle transaction id')
    elif not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
        raise ValueError('non-idle transaction id')
    observation = obj(data['observation'])
    synchronized = boolean(observation['synchronized'])
    source = observation['source']
    if source is not None and (not isinstance(source, str) or not 1 <= len(source) <= 256):
        raise ValueError('observation source')
    revision = integer(observation['revision'], -1)
    if synchronized and (source is None or revision < 0):
        raise ValueError('synchronized source/revision missing')
    observed_count = integer(observation['observed_count'])
    recovery = token(data['recovery'])
    close_active = boolean(data['managed_close_active'])
    layout_active = boolean(data['initial_layout_active'])
    cleanup_uncertain = boolean(data['viewer_cleanup_uncertain'])
    for key in ('managed_close_protocol', 'recovery_snapshot_protocol',
                'viewer_protocol', 'initial_layout_protocol', 'single_raise_protocol'):
        integer(data[key], 0, 1024)
    concerns = []
    if not synchronized:
        concerns.append('observer unsynchronized')
    if presence['uncertain']:
        concerns.append('uncertain managed windows')
    if state in ('PENDING', 'RUNNING', 'VERIFYING'):
        concerns.append('placement transaction active')
    elif state == 'ERROR':
        concerns.append('last placement transaction failed')
    if close_active:
        concerns.append('managed close active')
    if layout_active:
        concerns.append('initial layout active')
    if cleanup_uncertain:
        concerns.append('viewer cleanup uncertain')
    if recovery not in ('inactive', 'ready'):
        concerns.append('recovery not ready')
    lines = [
        'Broker registry status (snapshot; not remote connection health)',
        'State: ' + ('Busy/uncertain' if concerns else 'No reported Busy/uncertain flags'),
        f'Managed windows: {managed} (present={presence["present"]}, missing={presence["missing"]}, uncertain={presence["uncertain"]})',
        f'Launch requests: {requests} (pending={states["pending"]}, running={states["running"]}, succeeded={states["succeeded"]}, failed={states["failed"]}, timeout={states["timeout"]}, ambiguous={states["ambiguous"]})',
        f'Observation: {"synchronized" if synchronized else "unsynchronized"}; observed={observed_count}; revision={observation["revision"]}',
        f'Placement transaction: {state}',
        f'Recovery: {recovery}',
        f'Capabilities: managed_close={data["managed_close_protocol"]}, snapshot={data["recovery_snapshot_protocol"]}, viewer={data["viewer_protocol"]}, initial_layout={data["initial_layout_protocol"]}, single_raise={data["single_raise_protocol"]}',
    ]
    if concerns:
        lines.append('Attention: ' + ', '.join(concerns))
    return lines


def validate_info(data, requested):
    data = obj(data)
    state = data['state']
    if state == 'UNKNOWN':
        # Never treat a guessed or absent identifier as a managed window.
        if set(data) != {'state'}:
            raise ValueError('unknown record shape')
        return None
    if state != 'FOUND':
        raise ValueError('invalid record state')
    record = obj(data['window'])
    if record['managed_id'] != requested:
        raise ValueError('managed ID mismatch')
    uid = record['window_uuid']
    if not isinstance(uid, str) or str(uuid.UUID(uid)) != uid:
        raise ValueError('noncanonical UUID')
    intended = obj(record['intended'])
    desktop = integer(intended['desktop'], 1, 256)
    slot = integer(intended['slot'], 1, 256)
    presence = token(record['presence'])
    placement = token(record['placement'])
    if presence not in ('present', 'missing', 'uncertain') or placement not in (
            'not_requested', 'pending', 'succeeded', 'failed'):
        raise ValueError('invalid record state')
    observation = obj(record['observation'])
    lines = [
        'Managed window information (broker record; not remote connection health)',
        f'MANAGED_ID: {requested}',
        f'WINDOW_UUID: {uid}',
        f'DESKTOP: {desktop}',
        f'SLOT: {slot}',
        f'PRESENCE: {presence}',
        f'PLACEMENT: {placement}',
    ]
    if observation:
        lines.append('OBSERVATION: last-known (not independently verified live)')
        if 'pid' in observation:
            lines.append(f'PID: {integer(observation["pid"], 0)}')
        if 'resource_class' in observation:
            cls = observation['resource_class']
            # Do not echo captions, targets, private recipes or arbitrary
            # window-supplied text; a simple class token is safe to display.
            if isinstance(cls, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', cls):
                lines.append('RESOURCE_CLASS: ' + cls)
        if 'geometry' in observation:
            g = obj(observation['geometry'])
            if set(g) >= {'x', 'y', 'width', 'height'}:
                values = [g[k] for k in ('x', 'y', 'width', 'height')]
                if all(type(v) in (int, float) and abs(v) <= 1000000 for v in values):
                    lines.append('LAST_KNOWN_FRAME: ' + ' '.join(str(v) for v in values))
    return lines



def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('status', 'info'):
        print('Invalid read-only query arguments', file=sys.stderr)
        return 2
    try:
        with os.fdopen(3) as stream:
            data = json.load(stream, object_pairs_hook=unique_keys)
        mode, identifier = sys.argv[1:3]
        if mode == 'status':
            lines = validate_status(data)
        elif mode == 'info':
            lines = validate_info(data, identifier)
        else:
            raise ValueError('unknown query mode')
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError,
            RecursionError, OSError):
        print('Malformed or inconsistent read-only broker response; no details displayed', file=sys.stderr)
        return 2
    if lines is None:
        print('Managed window UNKNOWN: no positively registered record for requested ID', file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
