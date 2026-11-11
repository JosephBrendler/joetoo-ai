#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Maintainer-only immediate post-registration placement experiment.

Confirm before launch; no GDM/image/readiness wait follows registration. Remaining
arguments go to joetoo-sdl-registration-launch.py (host, username and its bounds).
The original foreground supervisor owns/reaps the only SDL child. Placement
failure does not close it. Ctrl-C/TERM retains the launcher's cancellation policy.
No configured -o workflow or remote authentication/security policy is introduced.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launcher = load('immediate_registration', 'joetoo-sdl-registration-launch.py')
placement = load('immediate_placement', 'joetoo-sdl-release-placement.py')
DEFAULT_GEOMETRY = dict(x=1, y=1, width=800, height=628)
DEFAULT_DIAGNOSTIC_BYTE_LIMIT = 1048576


class BrokerTrace:
    """Read only new bounded lines from an existing private stderr file.

    Broker stages are receipt times relative to its placement Submit, not the
    harness clock or physical assignment times. No raw log line is exported.
    """
    def __init__(self, path, limit):
        launcher.require(type(limit) is int and 1024 <= limit <= 16777216, 'Invalid diagnostic byte bound')
        self.fd = None
        self.limit, self.path = limit, path
        if path is None:
            return
        self.fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(self.fd)
            launcher.require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
                             and not info.st_mode & 0o077, 'Private regular diagnostic log required')
            self.inode = info.st_dev, info.st_ino
            self.offset = info.st_size
        except BaseException:
            self.close()
            raise

    def read(self, request_id, window_uuid):
        result = dict(status='unavailable', assignment=None, geometry_verification=None, terminal=None,
                      time_basis='broker receipt elapsed milliseconds since placement Submit; not physical execution')
        if request_id is None:
            result['reason'] = 'placement_request_id_unavailable'
            return result
        if self.fd is None:
            result['reason'] = 'diagnostic_log_not_supplied'
            return result
        try:
            info, named = os.fstat(self.fd), os.stat(self.path, follow_symlinks=False)
            launcher.require((named.st_dev, named.st_ino) == self.inode and
                             info.st_uid == os.geteuid() and not info.st_mode & 0o077 and
                             info.st_size >= self.offset, 'Diagnostic log replaced/truncated')
            raw = os.pread(self.fd, self.limit + 1, self.offset)
            result['status'] = 'partial' if len(raw) > self.limit else 'read'
            prefix = b'joetoo-kwind: SDL placement diagnostic '
            # Ignore any unfinished final line; never wait or retry for logging.
            for line in raw[:self.limit].split(b'\n')[:-1]:
                if not line.startswith(prefix): continue
                try:
                    row = json.loads(line[len(prefix):])
                    if row.get('request_id') != request_id or row.get('window_uuid') != window_uuid:
                        continue
                    elapsed = row.get('receipt_elapsed_ms')
                    if type(elapsed) is not int or elapsed < 0: continue
                    stage = row.get('stage')
                    if stage == 'resident_assignment_attempt':
                        result['assignment'] = dict(broker_elapsed_ms=elapsed,
                            after_terminal=row.get('after_terminal') is True)
                    if (stage == 'terminal_begin' and row.get('requested_outcome') == 'succeeded'
                            and row.get('geometry_match') is True and row.get('desktop_match') is True):
                        result['geometry_verification'] = dict(broker_elapsed_ms=elapsed,
                            evidence='verified frame/membership at broker terminal_begin')
                    if stage == 'terminal' and row.get('outcome') in ('succeeded', 'failed'):
                        result['terminal'] = dict(broker_elapsed_ms=elapsed, outcome=row['outcome'])
                except (ValueError, TypeError, AttributeError):
                    continue
        except (OSError, RuntimeError):
            result.update(status='unavailable', reason='diagnostic_read_failed')
        result['missing'] = [key for key in ('assignment', 'geometry_verification', 'terminal') if result[key] is None]
        return result

    def close(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


class Experiment:
    """One registration notification -> one independent placement connection."""
    def __init__(self, bus_factory, interface, trace, *, desktop, slot, geometry,
                 timeout_ms, poll_ms, call_timeout_ms, emit=print, clock=time.monotonic,
                 release=placement.release):
        self.bus_factory, self.interface, self.trace = bus_factory, interface, trace
        self.desktop, self.slot, self.geometry = desktop, slot, dict(geometry)
        self.timeout_ms, self.poll_ms, self.call_timeout_ms = timeout_ms, poll_ms, call_timeout_ms
        self.emit, self.clock, self.release = emit, clock, release
        self.started = clock()
        self.attempted = False
        self.placement_ok = False
        self.request_id = None
        self.window_uuid = None
        self.registration_time = None

    def record(self, stage, **fields):
        now = self.clock()
        row = dict(stage=stage, monotonic_s=now, elapsed_ms=(now - self.started) * 1000,
                   remote_session='unverified', **fields)
        self.emit(json.dumps(row, sort_keys=True))

    def launcher_output(self, line):
        # Keep registration-only "not_requested" distinct from the independent
        # experiment result, including the original child's exit report.
        self.record('launcher_output', launcher=json.loads(line))

    def registered(self, registration, cancelled):
        launcher.require(not self.attempted, 'Duplicate registration notification')
        self.attempted = True  # No retry, even if creating the operator connection fails.
        self.registration_time = self.clock()
        self.window_uuid = registration['window_uuid']
        self.record('registered', managed_id=registration['managed_id'], window_uuid=self.window_uuid,
                    registration_request_id=registration['request_id'])
        snapshot = dict(status='unavailable', reason='terminal_snapshot_not_received')
        outcome = None
        def observe(stage, value, api):
            nonlocal snapshot
            if stage == 'submission':
                self.record('placement_submission', window_uuid=self.window_uuid,
                            since_registration_ms=(self.clock() - self.registration_time) * 1000)
            elif stage == 'submitted':
                self.request_id = value['request_id']
                self.record('placement_accepted', request_id=self.request_id, window_uuid=self.window_uuid)
            elif stage == 'terminal':
                self.record('placement_terminal', request_id=value['request_id'], window_uuid=self.window_uuid,
                            placement=value['placement'], reason=value.get('reason'))
                try:
                    detail = api.call('GetManaged', registration['managed_id'])
                    window = detail.get('window', {})
                    launcher.require(detail.get('state') == 'FOUND' and window.get('window_uuid') == self.window_uuid,
                                     'Managed UUID changed')
                    observed = window['observation']
                    snapshot = dict(status='observed', monotonic_s=self.clock(),
                        note='broker snapshot; last-known if presence is missing/uncertain', presence=window['presence'],
                        placement=window['placement'], window_uuid=window['window_uuid'],
                        geometry={key: observed['geometry'][key] for key in ('x', 'y', 'width', 'height')},
                        desktops=observed['desktops'], on_all_desktops=observed['on_all_desktops'])
                except Exception:
                    snapshot = dict(status='unavailable', reason='managed_snapshot_failed_or_uuid_changed')
        def terminal(line):
            nonlocal outcome
            outcome = json.loads(line)
        try:
            code = self.release(self.bus_factory(), self.interface, registration['managed_id'],
                self.desktop, self.slot, self.geometry, confirmed=True, timeout_ms=self.timeout_ms,
                poll_ms=self.poll_ms, call_timeout_ms=self.call_timeout_ms, emit=terminal,
                clock=self.clock, expected_window_uuid=self.window_uuid, cancelled=cancelled, observe=observe)
            self.placement_ok = code == 0
        except Exception as error:
            # A placement error must not terminate an otherwise live viewer.
            # Explicit cancellation is handled by the original supervisor next.
            self.record('placement_error', error_type=type(error).__name__, cancelled=bool(cancelled()))
        self.record('experiment_result', registration='registered', window_uuid=self.window_uuid,
                    placement=outcome or dict(status='unavailable'), observed=snapshot,
                    requested=dict(desktop=self.desktop, slot=self.slot, geometry=self.geometry),
                    broker_evidence=self.trace.read(self.request_id, self.window_uuid),
                    supervision='continuing_under_original_launcher')


def main(argv=None):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'libexec'))
    from joetoo_kwin_vnc_target import DEFAULTS as mechanical_defaults, settings as mechanical_settings
    from joetoo_kwin_rdp_launch import DEFAULTS as registration_defaults, settings as registration_settings
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--confirm-immediate-placement', action='store_true', required=True)
    parser.add_argument('--desktop', type=int, default=1)
    parser.add_argument('--slot', type=int, default=1)
    for key, value in DEFAULT_GEOMETRY.items():
        parser.add_argument('--' + key, type=int, default=value)
    parser.add_argument('--placement-timeout-ms', type=int, default=mechanical_defaults['vnc_placement_timeout_ms'])
    parser.add_argument('--placement-poll-ms', type=int, default=registration_defaults['rdp_registration_poll_ms'])
    parser.add_argument('--call-timeout-ms', type=int, default=launcher.DEFAULT_CALL_TIMEOUT_MS)
    parser.add_argument('--broker-diagnostic-log', help='Existing private broker stderr file; no service changes')
    parser.add_argument('--diagnostic-byte-limit', type=int, default=DEFAULT_DIAGNOSTIC_BYTE_LIMIT)
    args, remaining = parser.parse_known_args(argv)
    # Reuse current mechanical bounds. Registration options/adapter validation
    # still run through the original launcher main, including installed-byte checks.
    mechanical_settings({'vnc_placement_timeout_ms': args.placement_timeout_ms,
                         'vnc_dbus_timeout_ms': args.call_timeout_ms})
    registration_settings({'rdp_registration_poll_ms': args.placement_poll_ms})
    launcher.require(1 <= args.desktop <= 256 and 1 <= args.slot <= 256 and
                     -32768 <= args.x <= 32768 and -32768 <= args.y <= 32768 and
                     1 <= args.width <= 32768 and 1 <= args.height <= 32768, 'Invalid experiment destination')
    import dbus
    with_trace = BrokerTrace(args.broker_diagnostic_log, args.diagnostic_byte_limit)
    try:
        experiment = Experiment(lambda: dbus.bus.BusConnection(os.environ['DBUS_SESSION_BUS_ADDRESS']),
            dbus.Interface, with_trace, desktop=args.desktop, slot=args.slot,
            geometry={key: getattr(args, key) for key in DEFAULT_GEOMETRY},
            timeout_ms=args.placement_timeout_ms, poll_ms=args.placement_poll_ms,
            call_timeout_ms=args.call_timeout_ms,
            emit=lambda line: print(line, flush=True))
        status = launcher.main(remaining + ['--desktop', str(args.desktop), '--slot', str(args.slot),
            '--call-timeout-ms', str(args.call_timeout_ms)],
            emit=experiment.launcher_output, on_registered=experiment.registered)
        return status if status else (0 if experiment.placement_ok else 1)
    finally:
        with_trace.close()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('SDL immediate-placement experiment FAILED: ' + type(error).__name__, file=sys.stderr)
        sys.exit(1)
