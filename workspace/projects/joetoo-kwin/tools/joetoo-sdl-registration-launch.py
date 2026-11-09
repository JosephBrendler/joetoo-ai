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

BUS = 'org.joetoo.KWinBridge'
PATH = '/org/joetoo/KWinBridge'
DEFAULT_CALL_TIMEOUT_MS = 3000  # Also bounds each TERM/KILL reap wait.


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def dbus_error_name(error):
    """Expose only known error identifiers, never remote exception messages."""
    try:
        getter = getattr(error, 'get_dbus_name', None)
        name = getter() if callable(getter) else getattr(error, 'name', None)
    except Exception:
        return None
    allowed = {BUS + '.' + suffix for suffix in ('BadArguments', 'InvalidRequest', 'Busy', 'UnknownRequest')}
    allowed.update('org.freedesktop.DBus.Error.' + suffix for suffix in (
        'AccessDenied', 'NotSupported', 'Timeout', 'NoReply', 'Disconnected',
        'ServiceUnknown', 'NameHasNoOwner', 'UnknownMethod', 'InvalidArgs'))
    return name if isinstance(name, str) and name in allowed else None


class Connection:
    """One authenticated connection, pinned destination; no owner substitution."""
    def __init__(self, bus, interface, timeout):
        self.bus, self.timeout = bus, timeout
        self.daemon = interface(bus.get_object('org.freedesktop.DBus',
                                '/org/freedesktop/DBus', introspect=False), 'org.freedesktop.DBus')
        self.owner = str(self.daemon.GetNameOwner(BUS, timeout=timeout))
        proxy = bus.get_object(self.owner, PATH, introspect=False)
        self.api = interface(proxy, BUS)
        tree = ET.fromstring(interface(proxy, 'org.freedesktop.DBus.Introspectable').Introspect(timeout=timeout))
        methods = {m.get('name'): m for i in tree.findall('interface') if i.get('name') == BUS
                   for m in i.findall('method')}
        for name, sig in dict(BeginSdlRegistration='s', BindSdlRegistration='sih',
                              PollSdlRegistration='s', CancelSdlRegistration='s').items():
            args = methods[name].findall('arg') if name in methods else []
            require(''.join(a.get('type') for a in args if a.get('direction', 'in') == 'in') == sig
                    and ''.join(a.get('type') for a in args if a.get('direction') == 'out') == 's',
                    'SDL interface mismatch')

    def pinned(self):
        require(self.bus.get_is_connected(), 'Caller connection lost')
        require(str(self.daemon.GetNameOwner(BUS, timeout=self.timeout)) == self.owner,
                'Broker owner changed')

    def call(self, name, *args):
        try:
            self.pinned()
            return json.loads(getattr(self.api, name)(*args, timeout=self.timeout))
        except Exception as error:
            code = dbus_error_name(error)
            if code is not None:
                raise RuntimeError(name + ' failed: ' + code) from None
            raise

    def result(self, result, rid):
        require(result.get('protocol') == 1 and result.get('request_id') == rid
                and result.get('placement') == 'not_requested'
                and result.get('remote_session') == 'unverified'
                and result.get('state') in ('pending', 'registered', 'failed', 'ambiguous', 'timeout'),
                'Invalid SDL transaction reply')
        if result['state'] == 'registered':
            require(result.get('reason') == 'registered' and isinstance(result.get('managed_id'), str)
                    and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',
                                     result.get('window_uuid', '')), 'Invalid registered UUID reply')
        return result


def stop_child(child, pidfd, timeout):
    """Use the retained lifetime descriptor, never signal a recycled numeric PID."""
    if child.poll() is None:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                signal.pidfd_send_signal(pidfd, sig)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=timeout)
                return
            except subprocess.TimeoutExpired:
                continue
        raise RuntimeError('Owned child cleanup incomplete')
    child.wait(timeout=timeout)


def placement_available(status):
    """Retained OK/ERROR IDs are history, not active placement work.

    This snapshot does not certify SDL cleanup. BeginSdlRegistration remains
    the authoritative active/uncertain-cleanup gate before child creation.
    """
    transaction = status['placement_transaction']
    return (not status['initial_layout_active'] and not status['viewer_cleanup_uncertain']
            and (transaction == {'id': None, 'state': 'IDLE'}
                 or transaction['state'] in ('OK', 'ERROR')))


def launch(bus, interface, unix_fd, adapter, host, port, username, desktop, slot,
           bounds, call_timeout=3., emit=print, spawn=subprocess.Popen,
           sleep=time.sleep, clock=time.monotonic, cancelled=lambda: False, profile=None):
    """Injectable orchestration; real broker enforces all identity/ownership rules.

    Registration is reported promptly, then supervision continues until child
    exit. Cancellation/error terminates only this owned child. Registered UUIDs
    remain registered after exit; this tool never unregisters or transfers them.
    """
    api = child = pidfd = log = None
    active = None
    registered = False
    try:
        bounds = adapter.settings(bounds, profile) if profile is not None else adapter.settings(bounds)
        require(100 <= call_timeout * 1000 <= 30000, 'Call/cleanup timeout out of range')
        require(type(desktop) is int and type(slot) is int and 1 <= desktop <= 256 and 1 <= slot <= 256,
                'Invalid desktop/slot')
        # Validate all local arguments and executable before creating an intent.
        adapter.development_argv(host, port, username, 'joetoo-rdp-' + '0' * 64)
        expected_exe = adapter.executable_identity()
        api = Connection(bus, interface, call_timeout)
        before = api.call('RegistryStatus')
        require(before['observation']['synchronized'] is True, 'Inventory is not synchronized')
        source = before['observation']['source']
        require(before['request_counts']['pending'] == before['request_counts']['running'] == 0
                and placement_available(before), 'Broker is busy')
        folder = Path(tempfile.mkdtemp(prefix='joetoo-sdl-registration-'))
        os.chmod(folder, 0o700)
        descriptor = os.open(folder / 'stdout.log', os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        log = os.fdopen(descriptor, 'w+b')
        os.fchmod(log.fileno(), 0o600)
        inode = os.fstat(log.fileno())
        emit(json.dumps(dict(evidence_directory=str(folder), placement='not_requested')))
        deadline = clock() + bounds['rdp_registration_timeout_ms'] / 1000
        payload = dict(protocol=1, desktop=desktop, slot=slot, bounds=bounds)
        if profile is not None:
            payload['profile'] = profile
        result = api.call('BeginSdlRegistration', json.dumps(payload))
        # Retain a valid ID even if another Begin field is invalid, for cleanup.
        active = result.get('request_id')
        require(isinstance(active, str) and re.fullmatch(r'[0-9a-f]{32}', active), 'Invalid request ID')
        api.result(result, active)
        require(result['state'] == 'pending' and result.get('bounds') == bounds, 'Unexpected Begin result')
        require(result.get('profile') == profile, 'Unexpected SDL profile')
        argv = adapter.development_argv(host, port, username, result.get('title_marker'))
        argv[0] = '/usr/bin/sdl-freerdp'  # Same fixed executable checked by broker.
        api.pinned()
        require(not cancelled() and clock() < deadline, 'Cancelled/expired before spawn')
        child = spawn(argv, stdin=None, stdout=log, stderr=subprocess.STDOUT,
                      env=(adapter.development_environment(os.environ, profile, bounds) if profile is not None
                           else adapter.development_environment(os.environ)), close_fds=True)
        # POSIX Popen returns after exec's error pipe closes. No shell/wrapper,
        # sleep, log forwarder or intermediate process supplies the bound PID.
        pidfd = os.pidfd_open(child.pid)
        info = adapter._proc_info(child.pid)
        require(info['parent'] == os.getpid() and info['exe'] == expected_exe,
                'Direct child executable mismatch')
        emit(json.dumps(dict(child_pid=child.pid, child_start=info['start'], request_id=active,
                             placement='not_requested', remote_session='unverified')))
        # Use separate read-only access; dbus UnixFd duplicates it for transport.
        require(not cancelled() and clock() < deadline and child.poll() is None,
                'Cancelled/expired or exited before Bind')
        with open(folder / 'stdout.log', 'rb') as reader:
            current = os.fstat(reader.fileno())
            require((current.st_dev, current.st_ino) == (inode.st_dev, inode.st_ino), 'Log substituted')
            fd = unix_fd(reader.fileno())
            try:
                result = api.result(api.call('BindSdlRegistration', active, child.pid, fd), active)
            finally:
                os.close(fd.take())
        while True:
            require(result.get('profile') == profile and (profile is None or result.get('bounds') == bounds),
                    'SDL profile/settings changed')
            require(not cancelled(), 'Operator cancellation')
            current = os.fstat(log.fileno())
            require(stat.S_IMODE(current.st_mode) == 0o600 and current.st_nlink == 1
                    and current.st_uid == os.geteuid() and current.st_size <= bounds['rdp_backend_log_byte_limit'],
                    'Private log integrity/budget lost')
            if not registered:
                if result['state'] != 'pending':
                    emit(json.dumps(result, sort_keys=True))
                    if result['state'] != 'registered':
                        return 1
                    registered = True
                else:
                    require(child.poll() is None, 'Child exited before registration')
                    require(clock() < deadline, 'Local registration deadline expired')
                    result = api.result(api.call('PollSdlRegistration', active), active)
                    if result['state'] != 'pending':
                        continue
            if registered and child.poll() is not None:
                emit(json.dumps(dict(child_exit=child.returncode, registration='registered',
                                     remote_session='unverified', placement='not_requested')))
                return 0
            # Broker loss/restart after success must not close the viewer. Only
            # pending registration needs source/placement guards here.
            if not registered:
                status = api.call('RegistryStatus')
                require(status['observation']['synchronized'] is True
                        and status['observation']['source'] == source, 'Observation source lost')
                require(placement_available(status), 'Placement became active')
            sleep(bounds['rdp_registration_poll_ms'] / 1000)
    finally:
        try:
            if api is not None and active and not registered:
                try:
                    emit(json.dumps(api.result(api.call('CancelSdlRegistration', active), active), sort_keys=True))
                except Exception:
                    # Unknown/lost reply or disconnected sender: closing this
                    # connection triggers broker owner-loss cleanup; never PASS.
                    pass
        finally:
            bus.close()
            try:
                if child is not None:
                    if pidfd is None:
                        # Bind has not occurred. Popen still owns this unreaped
                        # direct child (no other waiter in this single-threaded
                        # launcher); use its ordinary cleanup on pidfd exhaustion.
                        # This is never a fallback for broker identity verification.
                        try:
                            child.terminate()
                            child.wait(timeout=call_timeout)
                        except subprocess.TimeoutExpired:
                            child.kill()
                            child.wait(timeout=call_timeout)
                    else:
                        stop_child(child, pidfd, call_timeout)
            finally:
                if pidfd is not None:
                    os.close(pidfd)
                if log is not None:
                    log.close()


def main():
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
    args = parser.parse_args()
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
                  limits, args.call_timeout_ms / 1000, cancelled=lambda: interrupted[0], profile=args.profile)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        # No raw remote/log/credential/argv or D-Bus exception text is exported.
        reason = dbus_error_name(error) or (str(error) if type(error) is RuntimeError else type(error).__name__)
        print('SDL development launcher FAILED: ' + reason, file=sys.stderr)
        sys.exit(1)
