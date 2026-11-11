#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import-safe SDL identity helpers and configured serial frontend/worker.

The development launcher arms the broker before spawning, then binds its
actual direct child and private stdout descriptor through the existing API.
Executable paths add configured supervision; importing the module never launches
a connection or chooses authentication/certificate exceptions.
"""
import fcntl
import ipaddress
import os
import re
import stat
import select
import time
import argparse
import json
import secrets
import uuid
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

DEFAULTS = dict(rdp_registration_timeout_ms=300000, rdp_registration_poll_ms=100,
                rdp_registration_event_limit=4096, rdp_registration_window_limit=64,
                rdp_backend_log_byte_limit=65536)
BOUNDS = dict(rdp_registration_timeout_ms=(1000, 3600000),
              rdp_registration_poll_ms=(10, 1000),
              rdp_registration_event_limit=(16, 65536),
              rdp_registration_window_limit=(1, 512),
              rdp_backend_log_byte_limit=(1024, 1048576))
APPLICATION = 'com.freerdp.client.sdl3'
X11_PROFILE = 'sdl-x11-a1c-v1'
X11_DEFAULTS = dict(rdp_x11_renderer='auto', rdp_x11_identity_settle_ms=500)


def expected_backend(profile=None):
    if profile is None:
        return 'wayland'
    if profile == X11_PROFILE:
        return 'x11'
    raise ValueError('Unsupported SDL registration profile')


def settings(data, profile=None):
    """Explicit bounds passed across the future launcher/broker boundary."""
    backend = expected_backend(profile)
    allowed = set(DEFAULTS) | (set(X11_DEFAULTS) if backend == 'x11' else set())
    if set(data) - allowed:
        raise ValueError('Unknown SDL registration setting')
    result = {}
    for name, default in DEFAULTS.items():
        value = data.get(name, default)
        if isinstance(value, str) and re.fullmatch(r'[1-9][0-9]{0,7}', value):
            value = int(value)
        low, high = BOUNDS[name]
        if type(value) is not int or not low <= value <= high:
            raise ValueError('Invalid RDP registration bounds')
        result[name] = value
    if result['rdp_registration_poll_ms'] >= result['rdp_registration_timeout_ms']:
        raise ValueError('RDP watchdog must be shorter than registration timeout')
    if backend == 'x11':
        renderer = data.get('rdp_x11_renderer', X11_DEFAULTS['rdp_x11_renderer'])
        if renderer not in ('auto', 'software'):
            raise ValueError('Invalid X11 renderer')
        settle = data.get('rdp_x11_identity_settle_ms', X11_DEFAULTS['rdp_x11_identity_settle_ms'])
        if isinstance(settle, str) and re.fullmatch(r'[1-9][0-9]{0,7}', settle):
            settle = int(settle)
        if type(settle) is not int or not 1 <= settle <= 30000 or settle >= result['rdp_registration_timeout_ms']:
            raise ValueError('Invalid X11 identity interval')
        result.update(rdp_x11_renderer=renderer, rdp_x11_identity_settle_ms=settle)
    return result


def development_argv(host, port, username, marker, client_settings=None):
    """Shared restricted SDL arguments, including the validated security policy.

    Development callers use the same NLA/strict defaults as production. Only
    configured callers pass validated settings to select negotiate or prompt;
    neither path accepts arbitrary switches, shell parsing or passwords.
    """
    if not isinstance(host, str) or not host or not host.isascii():
        raise ValueError('Invalid development endpoint (redacted)')
    try:
        address = ipaddress.ip_address(host)
        host = '[' + str(address) + ']' if address.version == 6 else str(address)
    except ValueError:
        if (len(host) > 253 or not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
                                       for label in host.split('.'))):
            raise ValueError('Invalid development endpoint (redacted)') from None
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Invalid development port')
    if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.@-]{0,127}', username):
        raise ValueError('Invalid development username (redacted)')
    if not isinstance(marker, str) or not re.fullmatch(r'joetoo-rdp-[0-9a-f]{64}', marker):
        raise ValueError('Invalid broker launch marker')
    from joetoo_kwin_rdp_target import security_arguments
    policy = security_arguments({} if client_settings is None else client_settings)
    return ['sdl-freerdp', '/v:' + host + ':' + str(port), '/u:' + username,
            '/t:' + marker,
            '/size:1024x768',
            '/smart-sizing:800x600',
            '/log-level:INFO',
            '/log-filters:com.freerdp.client.SDL:DEBUG'] + policy


def development_environment(environment, profile=None, bounds=None):
    """Child-only driver/log profile; observed backend evidence is still required.

    FreeRDP 3.32.1 consumes these WLOG overrides before its SDL main. A
    redirected appender, custom prefix or inherited filter can defeat the
    bounded parser. Restore the known console layout, not a logging attestation
    or a libc flush guarantee. Never alter the parent environment.
    """
    result = dict(environment)
    result.pop('SDL_VIDEODRIVER', None)
    result['SDL_VIDEO_DRIVER'] = expected_backend(profile)
    if profile == X11_PROFILE:
        limits = settings(bounds or {}, profile)
        for key in ('SDL_RENDER_DRIVER', 'SDL_FRAMEBUFFER_ACCELERATION'):
            result.pop(key, None)
        if limits['rdp_x11_renderer'] == 'software':
            result.update(SDL_RENDER_DRIVER='software', SDL_FRAMEBUFFER_ACCELERATION='0')
    for name in ('WLOG_APPENDER', 'WLOG_PREFIX', 'WLOG_FILTER', 'WLOG_LEVEL'):
        result.pop(name, None)
    result['WLOG_APPENDER'] = 'CONSOLE'
    return result


class BackendEvidence:
    """Read a private regular child log, never a pipe or a raw log export.

    The development launcher redirects its owned child to this 0600 regular file.
    pread() keeps reader/writer offsets independent. Closing our duplicate never
    breaks a running viewer's output pipe or signals the child. The launcher
    owns log retention and process lifetime; this reader never launches a child.
    """
    def __init__(self, process, log, bounds, profile=None):
        self.expected_backend = expected_backend(profile)
        self.limit = settings(bounds, profile)['rdp_backend_log_byte_limit']
        self.pid = process.pid
        info = os.fstat(log.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or
                info.st_mode & 0o077 or info.st_nlink != 1):
            raise ValueError('SDL evidence requires a private regular log')
        self.fd = os.dup(log.fileno())
        self.inode = info.st_dev, info.st_ino
        self.buffer = b''
        self.total = 0
        self.driver = None
        self.closed = False

    def read_backend(self):
        if self.closed:
            raise ValueError('SDL backend evidence reader closed')
        info = os.fstat(self.fd)
        if (info.st_size < self.total or info.st_uid != os.geteuid() or
                stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1 or
                (info.st_dev, info.st_ino) != self.inode):
            raise ValueError('SDL backend log integrity lost')
        if info.st_size > self.limit:
            raise ValueError('SDL backend log budget exhausted')
        # A regular file cannot wait for the child to supply data. Read at most
        # the configured total budget; unfinished lines stay bounded/private.
        chunk = os.pread(self.fd, self.limit - self.total + 1, self.total)
        self.total += len(chunk)
        if self.total > self.limit:
            raise ValueError('SDL backend log budget exhausted')
        self.buffer += chunk
        lines = self.buffer.split(b'\n')
        self.buffer = lines.pop()
        for line in lines:
            # FreeRDP's own SDL main log includes the originating process PID.
            match = re.search(rb"\[(\d+):[^\]]+\] \[(?:DEBUG|INFO)\]\[com\.freerdp\.client\.SDL\] - \[main\]: client is using backend '([^']+)'\r?$", line)
            if match:
                if int(match[1]) != self.pid or match[2] != self.expected_backend.encode('ascii'):
                    raise ValueError('SDL native-Wayland backend not established' if self.expected_backend == 'wayland'
                                     else 'SDL native-X11 backend not established')
                self.driver = self.expected_backend
        return self.driver

    def close(self):
        if not self.closed:
            self.closed = True
            self.buffer = b''
            os.close(self.fd)


# Linux process/descriptor checks used only by the additive development API.
# No process is launched, signalled or waited for by these reference objects.
def _pidfd_pid(fd):
    with open('/proc/self/fdinfo/' + str(fd), 'rb') as info:
        data = info.read(8193)
    if len(data) > 8192:
        raise ValueError('Invalid process descriptor')
    match = re.search(rb'^Pid:\s+([0-9]+)$', data, re.M)
    if not match:
        raise ValueError('Invalid process descriptor')
    return int(match[1])


def _exited(fd):
    poller = select.poll()
    poller.register(fd, select.POLLIN)
    return bool(poller.poll(0))


def _proc_info(pid, *, include_executable=True):
    """Read process metadata; executable evidence remains required by default.

    D-Bus caller identity uses its supplied pidfd, UID and start time. Reading
    an unused exe symlink can fail for KWin Wayland under /proc access policy.
    SDL child validators still require that lookup and propagate its errors.
    """
    base = '/proc/' + str(pid)
    with open(base + '/stat', 'rb') as stream:
        raw = stream.read(8193)
    if len(raw) > 8192:
        raise ValueError('Invalid process identity')
    fields = raw.rsplit(b')', 1)[1].split()
    info = dict(parent=int(fields[1]), start=int(fields[19]), uid=os.stat(base).st_uid)
    if include_executable:
        info['exe'] = _inode(base + '/exe')
    return info


def _inode(path):
    info = os.stat(path)
    return info.st_dev, info.st_ino


def executable_identity():
    """Fixed development executable, never a caller-supplied path or switch."""
    info = os.stat('/usr/bin/sdl-freerdp')
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or
            info.st_mode & 0o022 or not info.st_mode & 0o111):
        raise ValueError('Untrusted development executable')
    return info.st_dev, info.st_ino


def boot_ticks():
    # /proc starttime and CLOCK_BOOTTIME include suspend; monotonic deadlines
    # intentionally use their existing separate clock. Tick equality needs the
    # independent prelaunch UUID baseline and unpredictable marker as well.
    return int(time.clock_gettime(time.CLOCK_BOOTTIME) * os.sysconf('SC_CLK_TCK'))


class CallerIdentity:
    """A bus-supplied ProcessFD is optional in D-Bus, mandatory for this path.

    Absence raises NotImplementedError; numeric credentials are NOT upgraded
    into equivalent proof by opening a fresh pidfd for a possibly reused PID.
    """
    def __init__(self, credentials):
        self.fd = None
        received = credentials.get('ProcessFD')
        try:
            if received is not None:
                self.fd = received.take()
            if int(credentials.get('UnixUserID', -1)) != os.geteuid() or os.geteuid() == 0:
                raise PermissionError('Caller UID rejected')
            if self.fd is None or 'ProcessID' not in credentials or not hasattr(os, 'pidfd_open'):
                raise NotImplementedError('Bus ProcessFD unavailable')
            self.pid = int(credentials['ProcessID'])
            if self.pid <= 0 or _pidfd_pid(self.fd) != self.pid or _exited(self.fd):
                raise ValueError('Caller process identity rejected')
            info = _proc_info(self.pid, include_executable=False)
            self.start = info['start']
            if info['uid'] != os.geteuid() or not self.alive():
                raise ValueError('Caller process identity rejected')
        except Exception:
            self.close()
            raise

    def alive(self):
        try:
            if self.fd is None or _exited(self.fd):
                return False
            info = _proc_info(self.pid, include_executable=False)
            return (info['start'] == self.start and info['uid'] == os.geteuid()
                    and not _exited(self.fd))
        except (OSError, ValueError, IndexError):
            return False

    def close(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


class ChildIdentity:
    """Pin the actual direct child and revalidate it without PID-only lookup."""
    def __init__(self, caller, pid, log_fd, floor, executable, byte_limit, profile=None, bounds=None):
        self.fd = None
        self.caller = caller
        self.pid = pid
        self.executable = executable
        self.byte_limit = byte_limit
        self.profile = profile
        self.backend = expected_backend(profile)
        self.bounds = settings(bounds or {}, profile)
        if type(pid) is not int or pid <= 0 or not caller.alive():
            raise ValueError('Invalid child identity')
        try:
            self.fd = os.pidfd_open(pid)
            if _pidfd_pid(self.fd) != pid or _exited(self.fd):
                raise ValueError('Child already exited')
            info = _proc_info(pid)
            self.start = info['start']
            self.log_inode = _inode('/proc/' + str(pid) + '/fd/1')
            log = os.fstat(log_fd)
            mode = fcntl.fcntl(log_fd, fcntl.F_GETFL)
            if (mode & os.O_ACCMODE == os.O_WRONLY or mode & os.O_APPEND or
                    not stat.S_ISREG(log.st_mode) or log.st_uid != os.geteuid() or
                    stat.S_IMODE(log.st_mode) != 0o600 or log.st_nlink != 1 or
                    not 0 <= log.st_size <= byte_limit or
                    (log.st_dev, log.st_ino) != self.log_inode or self.start < floor):
                raise ValueError('Child log evidence rejected')
            if self.poll() is not None:
                raise ValueError('Child identity rejected')
        except Exception:
            self.close()
            raise

    def poll(self):
        # No waitpid: the persistent launcher owns/reaps the child. A pidfd
        # becoming readable means exit even if its numeric PID is later reused.
        if self.fd is None or _exited(self.fd) or not self.caller.alive():
            return 1
        info = _proc_info(self.pid)
        if (info['uid'] != os.geteuid() or info['parent'] != self.caller.pid or
                info['start'] != self.start or info['exe'] != self.executable or
                _inode('/proc/' + str(self.pid) + '/fd/1') != self.log_inode):
            return 1
        # Inspect only the driver setting in bounded memory; never return or
        # print the environment or command line (which may contain secrets).
        with open('/proc/' + str(self.pid) + '/environ', 'rb') as stream:
            data = stream.read(self.byte_limit + 1)
        if len(data) > self.byte_limit:
            return 1
        drivers = [v for v in data.split(b'\0') if v.startswith(b'SDL_VIDEO_DRIVER=')]
        if drivers != [b'SDL_VIDEO_DRIVER=' + self.backend.encode('ascii')]:
            return 1
        if self.profile == X11_PROFILE:
            fields = data.split(b'\0')
            if any(v.startswith(b'SDL_VIDEODRIVER=') for v in fields):
                return 1
            for key, value in ((b'SDL_RENDER_DRIVER=', b'software'), (b'SDL_FRAMEBUFFER_ACCELERATION=', b'0')):
                actual = [v for v in fields if v.startswith(key)]
                expected = [key + value] if self.bounds['rdp_x11_renderer'] == 'software' else []
                if actual != expected:
                    return 1
        return 1 if _exited(self.fd) else None

    def close(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


# Shared import-safe client routines; D-Bus is imported only by executable paths.
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
        self.methods = methods
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


def launch_registration(bus, interface, unix_fd, adapter, host, port, username, desktop, slot,
           bounds, call_timeout=3., emit=print, spawn=subprocess.Popen,
           sleep=time.sleep, clock=time.monotonic, cancelled=lambda: False, profile=None, on_registered=None,
           argv_builder=None, connection_factory=None, on_cleanup=None, registered_cancelled=None):
    """Injectable orchestration; real broker enforces all identity/ownership rules.

    Registration is reported promptly, then supervision continues until child
    exit. Cancellation/error terminates only this owned child. Registered UUIDs
    remain registered after exit; this tool never unregisters or transfers them.
    """
    argv_builder = argv_builder or adapter.development_argv
    connection_factory = connection_factory or Connection
    api = child = pidfd = log = None
    active = None
    registered = False
    termination_requested = False
    stage = 'registration'
    def check_log():
        current = os.fstat(log.fileno())
        require(stat.S_IMODE(current.st_mode) == 0o600 and current.st_nlink == 1
                and current.st_uid == os.geteuid() and current.st_size <= bounds['rdp_backend_log_byte_limit'],
                'Private log integrity/budget lost')
    def supervision_report(**fields):
        # Reporting is best effort after enrollment, never authority to kill.
        value = dict(state='unresolved', phase='supervision', supervision='degraded',
            registration='registered', request_id=active, managed_id=result['managed_id'],
            window_uuid=result['window_uuid'], remote_session='unverified', reason=stage, **fields)
        try:
            emit(json.dumps(value, sort_keys=True))
        except Exception:
            try:
                print('joetoo-kwin: registered SDL supervision degraded stage=' + stage,
                      file=sys.stderr, flush=True)
            except Exception:
                pass
    try:
        bounds = adapter.settings(bounds, profile) if profile is not None else adapter.settings(bounds)
        require(100 <= call_timeout * 1000 <= 30000, 'Call/cleanup timeout out of range')
        require(type(desktop) is int and type(slot) is int and 1 <= desktop <= 256 and 1 <= slot <= 256,
                'Invalid desktop/slot')
        # Validate all local arguments and executable before creating an intent.
        argv_builder(host, port, username, 'joetoo-rdp-' + '0' * 64)
        expected_exe = adapter.executable_identity()
        api = connection_factory(bus, interface, call_timeout)
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
        argv = argv_builder(host, port, username, result.get('title_marker'))
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
            if not registered and result['state'] == 'registered':
                # A validated positive broker reply is the ownership boundary,
                # even if the next reporting/logging operation subsequently fails.
                registered = True
                stage = 'registration_notification'
                # Opt-in notification precedes output/supervision waits;
                # the ordinary launcher still requests no placement.
                if on_registered is not None:
                    on_registered(dict(result), cancelled)
                emit(json.dumps(result, sort_keys=True))
            stage = 'cancellation_check'
            if cancelled():
                termination_requested = True
                raise RuntimeError('Operator cancellation')
            stage = 'private_log_integrity_or_budget'
            check_log()
            if not registered:
                if result['state'] != 'pending':
                    emit(json.dumps(result, sort_keys=True))
                    return 1
                require(child.poll() is None, 'Child exited before registration')
                require(clock() < deadline, 'Local registration deadline expired')
                result = api.result(api.call('PollSdlRegistration', active), active)
                if result['state'] != 'pending':
                    continue
            stage = 'child_supervision'
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
            stage = 'supervision_wait'
            sleep(bounds['rdp_registration_poll_ms'] / 1000)
    except KeyboardInterrupt:
        # The foreground POC's Ctrl-C remains an explicit owned-child stop.
        termination_requested = True
        raise
    except Exception:
        if not registered or termination_requested:
            raise
        supervision_report()
        # Retain the original connection and direct-child ownership. Failed
        # evidence is not reused for registration, placement or success claims.
        # Regular-file size is detected, not a kernel write quota: a preserved
        # client can still write beyond the budget; report that unresolved state.
        while child.poll() is None:
            try:
                stop = cancelled()
            except Exception:
                stop = False  # Broken supervision is not termination authority.
            if stop:
                termination_requested = True
                raise RuntimeError('Operator cancellation')
            try:
                check_log()
            except Exception:
                pass  # Already degraded; keep checking without flooding output.
            # Use the child's owned pidfd, not a broken injected reporting/wait
            # callback. No broker retry, registration transfer or placement occurs.
            select.select([pidfd], [], [], bounds['rdp_registration_poll_ms'] / 1000)
        supervision_report(child_exit=child.returncode)
        return 1
    finally:
        # A terminal reply and reaping are separate facts. Never infer either
        # from a failed local call, process exit, or a frontend return code.
        local_error = sys.exc_info()[1]
        if isinstance(local_error, KeyboardInterrupt):
            termination_requested = True
        receipt = dict(request_id=active, broker_owner=getattr(api, 'owner', None),
                       source=locals().get('source'), broker_terminal=False,
                       child_reaped=False, resources_released=False, eligible=False)
        clean_error = (local_error is None or isinstance(local_error, KeyboardInterrupt) or
            (type(local_error) is RuntimeError and str(local_error) in (
                'Operator cancellation', 'Local registration deadline expired',
                'Child exited before registration', 'Cancelled/expired or exited before Bind',
                'Cancelled/expired before spawn')))
        def notify_cleanup(value):
            try:
                on_cleanup(value)
            except Exception:
                # Failed private reporting cannot end protection of a retained child.
                try: print('joetoo-kwin: RDP cleanup reporting unavailable', file=sys.stderr, flush=True)
                except Exception: pass
        terminal_not_registered = False
        exited_before_cancel = child is not None and child.poll() is not None
        receipt['natural_exit'] = exited_before_cancel
        if api is not None and active and not registered:
            try:
                reply = api.result(api.call('CancelSdlRegistration', active), active)
                receipt['terminal'] = reply
                terminal_not_registered = reply['state'] in ('failed', 'timeout', 'ambiguous')
                if reply['state'] == 'registered':
                    # Cancellation raced successful enrollment. Inform the owner
                    # before waiting; never kill/re-adopt this positively enrolled child.
                    registered = True
                    if on_cleanup is not None:
                        notify_cleanup(dict(receipt, registration=reply))
                    while child is not None and child.poll() is None:
                        if (registered_cancelled or cancelled)():
                            termination_requested = True
                            break
                        select.select([pidfd], [], [], bounds['rdp_registration_poll_ms'] / 1000)
                else:
                    receipt['broker_terminal'] = (reply.get('state') in ('failed', 'timeout') and
                        (reply.get('reason') in ('cancelled', 'expired') or
                         (reply.get('reason') == 'child_identity_rejected' and exited_before_cancel)) and
                        reply.get('profile') == profile and (profile is None or reply.get('bounds') == bounds))
                emit(json.dumps(reply, sort_keys=True))
            except Exception:
                # Missing/ambiguous cancellation evidence cannot authorize continuation.
                receipt['broker_terminal'] = False
        if (on_cleanup is not None and not registered and child is not None and
                child.poll() is None and not terminal_not_registered):
            # Unknown broker completion is not permission to kill a possibly
            # enrolled viewer. Keep this owned child and original connection.
            notify_cleanup(dict(receipt, retained=True))
            registered = True  # Cleanup protection only; no registration claim.
            termination_requested = False
            while child.poll() is None:
                if (registered_cancelled or cancelled)():
                    termination_requested = True
                    break
                if pidfd is not None:
                    select.select([pidfd], [], [], bounds['rdp_registration_poll_ms'] / 1000)
                else:
                    try: child.wait(timeout=bounds['rdp_registration_poll_ms'] / 1000)
                    except subprocess.TimeoutExpired: pass
        cleanup_okay = True
        try:
            if child is not None and (not registered or termination_requested):
                if pidfd is None:
                    # Before Bind, Popen still owns the unreaped direct child.
                    try:
                        child.terminate(); child.wait(timeout=call_timeout)
                    except subprocess.TimeoutExpired:
                        child.kill(); child.wait(timeout=call_timeout)
                else:
                    stop_child(child, pidfd, call_timeout)
            elif child is not None and child.poll() is not None:
                child.wait(timeout=call_timeout)
            receipt['child_reaped'] = child is None or child.returncode is not None
        except Exception:
            cleanup_okay = False
        if not registered and receipt['broker_terminal'] and receipt['child_reaped'] and clean_error:
            try:
                status = api.call('RegistryStatus')
                require(status['observation']['synchronized'] is True and
                        status['observation']['source'] == source and placement_available(status) and
                        status['request_counts']['pending'] == status['request_counts']['running'] == 0 and
                        status['presence_counts']['uncertain'] == 0, 'Cleanup state unavailable')
                require(not any(w['intended'] == dict(desktop=desktop, slot=slot)
                    for w in api.call('ListManaged')['windows']), 'Cleanup slot remains reserved')
                receipt['eligible'] = True
            except Exception:
                receipt['eligible'] = False
        for resource, close in ((bus, lambda b: b.close()), (pidfd, os.close), (log, lambda f: f.close())):
            if resource is not None:
                try: close(resource)
                except Exception: cleanup_okay = False
        receipt['resources_released'] = cleanup_okay
        receipt['eligible'] = receipt['eligible'] and cleanup_okay and not registered
        if on_cleanup is not None and not registered:
            on_cleanup(receipt)



def release_placement(bus, interface, managed_id, desktop, slot, geometry, *, confirmed,
            timeout_ms, poll_ms, call_timeout_ms, emit=print, sleep=time.sleep, clock=time.monotonic,
            expected_window_uuid=None, cancelled=lambda: False, observe=None, connection_factory=None):
    require(confirmed is True, 'Explicit --confirm required')
    connection_factory = connection_factory or Connection
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
    def notify(stage, value=None):
        # Optional diagnostic consumers cannot change authorization or cleanup.
        if observe is not None:
            try: observe(stage, value, api)
            except Exception: pass
    try:
        require(not cancelled(), 'Operator cancellation')
        api = connection_factory(bus, interface, call_timeout_ms / 1000)
        # No raw UUID is submitted. The broker owns the managed-ID resolution.
        before = api.call('RegistryStatus')
        payload = dict(protocol=1, confirmed=True, managed_id=managed_id,
            action_id=uuid.uuid4().hex, desktop=desktop, slot=slot, **geometry,
            source=before['observation']['source'], revision=before['observation']['revision'], timeout_ms=timeout_ms)
        require(not cancelled(), 'Operator cancellation')
        notify('submission')
        result = api.call('SubmitSdlPlacement', json.dumps(payload))
        rid = result['request_id']
        expected_uuid = result['window_uuid']
        def valid(value):
            require(value.get('protocol') == 1 and value.get('request_id') == rid
                and re.fullmatch(r'[0-9a-f]{32}', rid) and value.get('window_uuid') == expected_uuid
                and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', expected_uuid)
                and value.get('managed_id') == managed_id and value.get('registration') == 'registered'
                and value.get('remote_session') == 'unverified'
                and value.get('placement') in ('pending', 'succeeded', 'failed'),
                'Placement identity/result mismatch')
        valid(result)
        require(expected_window_uuid is None or expected_uuid == expected_window_uuid,
                           'Registered/placement UUID mismatch')
        notify('submitted', result)
        # Broker owns the mechanical deadline, including its authentication.
        # This later local bound only detects an unresponsive/stuck broker.
        deadline = clock() + timeout_ms / 1000
        if result['placement'] == 'pending':
            require(not cancelled(), 'Operator cancellation')
            # Invoke the dedicated action; never an active-window move shortcut.
            accel = str(api.daemon.GetNameOwner('org.kde.kglobalaccel', timeout=call_timeout_ms / 1000))
            proxy = bus.get_object(accel, '/component/kwin', introspect=False)
            diagnostic('shortcut_dispatch', result)
            interface(proxy, 'org.kde.kglobalaccel.Component').invokeShortcut(
                'joetoo_bridge_sdl_placement', timeout=call_timeout_ms / 1000)
            diagnostic('shortcut_returned', result)
        while result['placement'] == 'pending':
            require(not cancelled(), 'Operator cancellation')
            sleep(min(poll_ms / 1000, max(0, deadline - clock())))
            require(not cancelled(), 'Operator cancellation')
            result = api.call('PollSdlPlacement', rid)
            valid(result)
            require(result['placement'] != 'pending' or clock() < deadline,
                               'Placement broker response deadline expired')
        terminal = True
        notify('terminal', result)
        emit(json.dumps(result, sort_keys=True))
        return 0 if result['placement'] == 'succeeded' else 1
    finally:
        try:
            if rid is not None and not terminal:
                api.call('CancelSdlPlacement', rid)
        finally:
            bus.close()



class ConfiguredError(RuntimeError):
    """Fixed nonsecret error codes for the configured frontend."""
    pass


def configured_argv(host, port, username, marker, client_settings):
    from joetoo_kwin_rdp_target import sizing_arguments
    # Reuse endpoint/marker/log/security policy, replacing only development sizing.
    return [v for v in development_argv(host, port, username, marker, client_settings)
            if not v.startswith(('/size:', '/smart-sizing:'))] + sizing_arguments(client_settings)


def configured_job(data):
    from joetoo_kwin_rdp_target import target, settings as client_settings
    from joetoo_kwin_vnc_target import settings as mechanical_settings
    keys = {'target', 'settings', 'bounds', 'mechanical', 'desktop', 'slot', 'x', 'y', 'width', 'height'}
    if not isinstance(data, dict) or set(data) != keys:
        raise ConfiguredError('invalid_job_schema')
    try:
        target(data['target'])
        sizing = client_settings(data['settings'])
    except (TypeError, ValueError):
        raise ConfiguredError('invalid_rdp_target_or_settings') from None
    requested = sizing['rdp_windowing_backend']
    profile = X11_PROFILE if requested == 'x11' else None
    raw = data['bounds']
    if not isinstance(raw, dict): raise ConfiguredError('invalid_registration_bounds')
    # Auto needs both profiles' knobs validated, without changing backend intent.
    limits = settings(raw, X11_PROFILE)
    if requested == 'wayland':
        limits = settings({k: v for k, v in limits.items() if k in DEFAULTS})
    if (not isinstance(data['mechanical'], dict) or
            set(data['mechanical']) != {'call_timeout_ms', 'placement_timeout_ms'}):
        raise ConfiguredError('invalid_mechanical_bounds')
    mechanical = mechanical_settings(dict(vnc_dbus_timeout_ms=data['mechanical']['call_timeout_ms'],
        vnc_placement_timeout_ms=data['mechanical']['placement_timeout_ms']))
    for k in ('desktop', 'slot', 'x', 'y', 'width', 'height'):
        v = data[k]
        low, high = ((1, 256) if k in ('desktop', 'slot') else
                     (-32768, 32768) if k in ('x', 'y') else (1, 32768))
        if type(v) is not int or not low <= v <= high:
            raise ConfiguredError('invalid_destination')
    return dict(data, settings=sizing, bounds=limits,
        mechanical=dict(call_timeout_ms=mechanical['vnc_dbus_timeout_ms'],
                        placement_timeout_ms=mechanical['vnc_placement_timeout_ms']))


def resolve_windowing_backend(bus, interface, requested, timeout):
    """Pinned authenticated KWin support-information, never session env guessing.

    KWin/kwin-x11 6.7.6 src/workspace.cpp emits one literal Operation Mode line.
    Unknown/changed formats fail closed. Child backend evidence remains mandatory.
    """
    daemon = interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspect=False),
                       'org.freedesktop.DBus')
    owner = str(daemon.GetNameOwner('org.kde.KWin', timeout=timeout))
    require(owner.startswith(':'), 'KWin owner unavailable')
    identity = CallerIdentity(daemon.GetConnectionCredentials(owner, timeout=timeout))
    try:
        info = str(interface(bus.get_object(owner, '/KWin', introspect=False), 'org.kde.KWin').supportInformation(timeout=timeout))
        modes = re.findall(r'^Operation Mode: (X11|Wayland)$', info, re.M) if len(info.encode()) <= 65536 else []
        if len(modes) != 1 or not identity.alive() or str(daemon.GetNameOwner('org.kde.KWin', timeout=timeout)) != owner:
            raise ConfiguredError('windowing_backend_unverified_select_wayland_or_x11')
        backend = modes[0].lower()
        if requested != 'auto' and requested != backend:
            raise ConfiguredError('native_x11_required_not_xwayland' if requested == 'x11' else 'windowing_backend_mismatch')
        return backend
    finally:
        identity.close()


def configured_preflight(job, bus, interface):
    job = configured_job(job)
    require(os.geteuid() != 0 and hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'),
            'Non-root Linux pidfd session required')
    executable_identity()
    timeout = job['mechanical']['call_timeout_ms'] / 1000
    backend = resolve_windowing_backend(bus, interface, job['settings']['rdp_windowing_backend'], timeout)
    if backend == 'x11':
        if not re.fullmatch(r'(?:unix)?:[0-9]+(?:\.[0-9]+)?', os.environ.get('DISPLAY', '')):
            raise ConfiguredError('local_x11_display_required')
    elif not os.environ.get('WAYLAND_DISPLAY'):
        raise ConfiguredError('wayland_display_required')
    api = Connection(bus, interface, timeout)
    # Introspection is sufficient; no new public capability/schema is required.
    for name in ('SubmitSdlPlacement', 'PollSdlPlacement', 'CancelSdlPlacement', 'TakeSdlPlacement'):
        method = api.methods.get(name)
        args = method.findall('arg') if method is not None else []
        if (''.join(a.get('type') for a in args if a.get('direction', 'in') == 'in') != 's' or
                ''.join(a.get('type') for a in args if a.get('direction') == 'out') != 's'):
            raise ConfiguredError('placement_interface_unavailable')
    status = api.call('RegistryStatus')
    if (not status['observation']['synchronized'] or not placement_available(status) or
            status['request_counts']['pending'] or status['request_counts']['running'] or
            status.get('initial_layout_protocol') != 1 or status['presence_counts']['uncertain']):
        raise ConfiguredError('broker_busy_or_observation_unavailable')
    for window in api.call('ListManaged')['windows']:
        if window['intended'] == dict(desktop=job['desktop'], slot=job['slot']):
            raise ConfiguredError('managed_slot_reserved_including_missing_history')
    return dict(job, resolved_backend=backend, broker_owner=api.owner,
                source=status['observation']['source'])


def _private_json(path, value):
    """Atomic 0600 control/status file inside an already verified 0700 directory."""
    pending = path.with_name(path.name + '.tmp-' + secrets.token_hex(8))
    fd = os.open(pending, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)
    finally:
        if pending.exists(): pending.unlink()


def _read_private_json(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or
                stat.S_IMODE(st.st_mode) != 0o600 or st.st_nlink != 1 or st.st_size > 65536):
            raise ConfiguredError('unsafe_control_file')
        raw = os.read(fd, 65537)
        if len(raw) > 65536: raise ConfiguredError('control_file_budget')
        return json.loads(raw)
    finally:
        os.close(fd)


def _runtime_directory(path):
    path = Path(path)
    st = path.lstat()
    if not path.is_absolute() or not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o700:
        raise ConfiguredError('private_runtime_directory_required')
    return path


def _failure_code(error):
    if isinstance(error, ConfiguredError): return str(error)
    known = {'Broker is busy': 'broker_busy', 'Operator cancellation': 'cancelled',
             'Child exited before registration': 'child_exited', 'Local registration deadline expired': 'timeout',
             'Broker owner changed': 'broker_owner_changed', 'Observation source lost': 'source_lost'}
    if type(error) is RuntimeError and str(error) in known: return known[str(error)]
    if type(error) is RuntimeError:
        match = re.fullmatch(r'(?:Begin|Bind|Poll|Cancel)SdlRegistration failed: (org\.[A-Za-z0-9_.]+)', str(error))
        if match: return match[1]
    return dbus_error_name(error) or type(error).__name__


def configured_worker(folder, bus_factory, interface, unix_fd):
    """One stable worker owns original Begin connection and direct SDL child."""
    folder = _runtime_directory(folder)
    envelope = _read_private_json(folder / 'job')
    job, nonce = envelope['job'], envelope['nonce']
    if not re.fullmatch(r'[0-9a-f]{32}', nonce): raise ConfiguredError('invalid_job_nonce')
    own_start = _proc_info(os.getpid(), include_executable=False)['start']
    parent_fd = os.pidfd_open(envelope['frontend_pid'])
    try:
        if (_pidfd_pid(parent_fd) != envelope['frontend_pid'] or _exited(parent_fd) or
                _proc_info(envelope['frontend_pid'], include_executable=False)['start'] != envelope['frontend_start']):
            raise ConfiguredError('frontend_identity_lost')
    except Exception:
        os.close(parent_fd)
        raise
    registered = False
    published = False
    explicit_stop = [False]
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, lambda signum, frame: explicit_stop.__setitem__(0, True))
    def pending_cancel():
        cancel = False
        if (folder / 'cancel').exists():
            cancel = _read_private_json(folder / 'cancel').get('nonce') == nonce
        return explicit_stop[0] or cancel or (not published and _exited(parent_fd))
    def publish(state, **fields):
        _private_json(folder / 'status', dict(state=state, nonce=nonce, worker_pid=os.getpid(),
            worker_start=own_start, remote_session='unverified', **fields))
    def connection_factory(bus, iface, timeout):
        api = Connection(bus, iface, timeout)
        if api.owner != job['broker_owner'] or api.call('RegistryStatus')['observation']['source'] != job['source']:
            raise ConfiguredError('broker_owner_or_source_replaced')
        return api
    registration = {}
    registration_events = []
    cleanup = {}
    def cleaned(value):
        nonlocal cleanup, registered, published
        cleanup = value
        if value.get('registration', {}).get('state') == 'registered' or value.get('retained'):
            registered = published = True
            publish('unresolved', phase='registration', reason='registration_outcome_unresolved' if value.get('retained') else 'cancellation_raced_registration',
                    registration=value.get('registration', {}), cleanup_confirmed=False)
    def emitted(line):
        value = json.loads(line)
        if value.get('supervision') == 'degraded':
            _private_json(folder / 'supervision', dict(value, nonce=nonce,
                worker_pid=os.getpid(), worker_start=own_start))
        elif value.get('state') in ('failed', 'ambiguous', 'timeout'):
            registration_events.append(value)
    def positive(result, unused):
        nonlocal registered, published, registration
        registered = True
        registration = result
        publish('pending', phase='placement', registration=result, broker_owner=job['broker_owner'])
        final = []
        success = False
        try:
            placement_bus = bus_factory()
            code = release_placement(placement_bus, interface, result['managed_id'], job['desktop'], job['slot'],
                {k: job[k] for k in ('x', 'y', 'width', 'height')}, confirmed=True,
                timeout_ms=job['mechanical']['placement_timeout_ms'], poll_ms=job['bounds']['rdp_registration_poll_ms'],
                call_timeout_ms=job['mechanical']['call_timeout_ms'], expected_window_uuid=result['window_uuid'],
                cancelled=pending_cancel, emit=lambda line: final.append(json.loads(line)),
                connection_factory=connection_factory)
            success = code == 0
            publish('completed' if success else 'failed', phase='placement',
                registration=result, placement=final[-1], broker_owner=job['broker_owner'])
        except Exception as error:
            publish('cancelled' if pending_cancel() else 'unresolved', phase='placement', reason=_failure_code(error), registration=result,
                    broker_owner=job['broker_owner'])
        published = True
        # A bounded private receipt handshake, never a viewer/GDM readiness gate.
        # Failure does not revoke registration or kill the registered client.
        if success:
            deadline = time.monotonic() + job['mechanical']['call_timeout_ms'] / 1000
            acknowledged = False
            while time.monotonic() < deadline:
                try:
                    acknowledged = _read_private_json(folder / 'ack').get('nonce') == nonce
                except FileNotFoundError:
                    pass
                if acknowledged: break
                time.sleep(min(job['bounds']['rdp_registration_poll_ms'] / 1000,
                               max(0, deadline - time.monotonic())))
            _private_json(folder / 'handoff', dict(nonce=nonce, worker_pid=os.getpid(), worker_start=own_start,
                                                 acknowledged=acknowledged))
        # Registered viewers survive placement failure/cancel or frontend exit.
    def registered_callback(result, cancellation):
        nonlocal registered, published
        try:
            positive(result, cancellation)
        except Exception as error:
            # Reporting/receipt failure cannot destroy an enrolled viewer.
            # The frontend will stop unresolved if no trustworthy result arrives.
            registered = published = True
            try:
                publish('unresolved', phase='handoff', reason=_failure_code(error), registration=result,
                        broker_owner=job['broker_owner'])
            except Exception:
                pass
    try:
        if pending_cancel(): raise ConfiguredError('cancelled_before_begin')
        bus = bus_factory()
        try:
            checked = configured_preflight({k: job[k] for k in ('target', 'settings', 'bounds', 'mechanical',
                'desktop', 'slot', 'x', 'y', 'width', 'height')}, bus, interface)
            if any(checked[k] != job[k] for k in ('broker_owner', 'source', 'resolved_backend')):
                raise ConfiguredError('preflight_session_replaced')
        finally:
            bus.close()
        endpoint = __import__('joetoo_kwin_rdp_target').target(job['target'])
        profile = X11_PROFILE if job['resolved_backend'] == 'x11' else None
        bounds = settings({k: v for k, v in job['bounds'].items() if profile is not None or k in DEFAULTS}, profile)
        if pending_cancel(): raise ConfiguredError('cancelled_before_begin')
        launch_registration(bus_factory(), interface, unix_fd, sys.modules[__name__], endpoint['host'], endpoint['port'],
            endpoint['user'], job['desktop'], job['slot'], bounds,
            call_timeout=job['mechanical']['call_timeout_ms'] / 1000,
            emit=emitted, on_registered=registered_callback, profile=profile,
            argv_builder=lambda h, p, u, m: configured_argv(h, p, u, m, job['settings']),
            connection_factory=connection_factory, on_cleanup=cleaned, registered_cancelled=lambda: explicit_stop[0],
            cancelled=lambda: explicit_stop[0] if registered else pending_cancel())
        if not published:
            terminal = registration_events[-1] if registration_events else {}
            state = terminal.get('state', 'failed')
            publish(state if cleanup.get('eligible') is True else 'unresolved', phase='registration',
                    reason=terminal.get('reason', 'registration_not_completed') if cleanup.get('eligible') is True else 'cleanup_unverified',
                    registration=terminal, cleanup=cleanup, cleanup_confirmed=cleanup.get('eligible') is True)
    except Exception as error:
        if not published:
            publish(('cancelled' if pending_cancel() else 'timeout' if _failure_code(error)=='timeout' else 'failed')
                    if cleanup.get('eligible') is True else 'unresolved', phase='registration',
                    reason=_failure_code(error) if cleanup.get('eligible') is True else 'cleanup_unverified',
                    failure_reason=_failure_code(error), cleanup=cleanup, cleanup_confirmed=cleanup.get('eligible') is True)
    finally:
        os.close(parent_fd)
        _private_json(folder / 'worker_exited', dict(nonce=nonce, worker_pid=os.getpid(), worker_start=own_start))


def clean_registration_receipt(value, job):
    """Private worker proof; the next broker Begin remains the final eligibility gate."""
    c = value.get('cleanup', {})
    terminal = c.get('terminal', {})
    return (value.get('phase') == 'registration' and value.get('cleanup_confirmed') is True and
        value.get('state') in ('failed', 'cancelled', 'timeout') and
        all(c.get(k) is True for k in ('eligible', 'broker_terminal', 'child_reaped', 'resources_released')) and
        c.get('broker_owner') == job['broker_owner'] and c.get('source') == job['source'] and
        isinstance(c.get('request_id'), str) and re.fullmatch(r'[0-9a-f]{32}', c['request_id']) is not None and
        terminal.get('request_id') == c['request_id'] and type(terminal.get('protocol')) is int and terminal.get('protocol') == 1 and
        terminal.get('state') in ('failed', 'timeout') and
        (terminal.get('reason') in ('cancelled', 'expired') or
         (terminal.get('reason') == 'child_identity_rejected' and c.get('natural_exit') is True)) and
        terminal.get('placement') == 'not_requested' and terminal.get('remote_session') == 'unverified' and
        not any(k in terminal for k in ('managed_id', 'window_uuid')) and
        terminal.get('profile') == (X11_PROFILE if job['resolved_backend'] == 'x11' else None) and
        (job['resolved_backend'] != 'x11' or terminal.get('bounds') == job['bounds']))


def configured_frontend(job, *, spawn=subprocess.Popen, clock=time.monotonic, sleep=time.sleep, verify_cleanup=None):
    """Return only this worker's nonce/PID/start-bound status; never hold FD 9."""
    runtime = _runtime_directory(os.environ.get('XDG_RUNTIME_DIR', ''))
    folder = Path(tempfile.mkdtemp(prefix='joetoo-rdp-', dir=runtime))
    os.chmod(folder, 0o700)
    nonce = secrets.token_hex(16)
    _private_json(folder / 'job', dict(job=job, nonce=nonce, frontend_pid=os.getpid(),
        frontend_start=_proc_info(os.getpid(), include_executable=False)['start']))
    worker = None
    worker_fd = None
    result = None
    interrupted = [False]
    old_handlers = {}
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old_handlers[sig] = signal.signal(sig, lambda signum, frame: interrupted.__setitem__(0, True))
    timeout = job['mechanical']['call_timeout_ms'] / 1000
    deadline = clock() + job['bounds']['rdp_registration_timeout_ms'] / 1000 + job['mechanical']['placement_timeout_ms'] / 1000 + 5 * timeout
    try:
        fd = os.open(folder / 'worker.stderr', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as log:
            worker = spawn([sys.executable, str(Path(__file__).resolve()), '--worker', str(folder)],
                           stdin=None, stdout=subprocess.DEVNULL, stderr=log, start_new_session=True, close_fds=True)
        worker_fd = os.pidfd_open(worker.pid)
        info = _proc_info(worker.pid, include_executable=False)
        if (_pidfd_pid(worker_fd) != worker.pid or info['uid'] != os.geteuid()
                or info['parent'] != os.getpid()):
            raise ConfiguredError('worker_process_identity_mismatch')
        start = info['start']
        while clock() < deadline:
            if interrupted[0]:
                _private_json(folder / 'cancel', dict(nonce=nonce))
                deadline = min(deadline, clock() + 3 * timeout)
                interrupted[0] = False
            try:
                status = _read_private_json(folder / 'status')
                if (status.get('nonce') != nonce or status.get('worker_pid') != worker.pid or status.get('worker_start') != start):
                    raise ConfiguredError('worker_status_identity_mismatch')
                if status.get('state') not in ('pending', 'completed', 'failed', 'cancelled', 'timeout', 'ambiguous', 'unresolved'):
                    raise ConfiguredError('worker_status_invalid')
                if status['state'] == 'completed':
                    if _exited(worker_fd) or worker.poll() is not None:
                        raise ConfiguredError('worker_exited_before_handoff')
                    reg, place = status.get('registration', {}), status.get('placement', {})
                    if (status.get('broker_owner') != job['broker_owner'] or reg.get('state') != 'registered' or
                            place.get('placement') != 'succeeded' or place.get('remote_session') != 'unverified' or
                            status.get('remote_session') != 'unverified' or
                            not re.fullmatch(r'win-[0-9]+', reg.get('managed_id', '')) or
                            not re.fullmatch(r'[0-9a-f]{32}', reg.get('request_id', '')) or
                            not re.fullmatch(r'[0-9a-f]{32}', place.get('request_id', '')) or
                            not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', reg.get('window_uuid', '')) or
                            place.get('window_uuid') != reg['window_uuid'] or
                            place.get('managed_id') != reg.get('managed_id')):
                        raise ConfiguredError('worker_terminal_identity_mismatch')
                if status['state'] != 'pending':
                    result = status
                    break
            except FileNotFoundError:
                pass
            if worker.poll() is not None: break
            sleep(job['bounds']['rdp_registration_poll_ms'] / 1000)
        if result is None:
            _private_json(folder / 'cancel', dict(nonce=nonce))
            result = dict(state='unresolved', reason='worker_handoff_unavailable', remote_session='unverified')
        _private_json(folder / 'ack', dict(nonce=nonce))
        if result['state'] == 'completed':
            receipt_deadline = clock() + timeout
            received = False
            while clock() < receipt_deadline:
                try:
                    receipt = _read_private_json(folder / 'handoff')
                    received = (receipt.get('nonce') == nonce and receipt.get('worker_pid') == worker.pid
                                and receipt.get('worker_start') == start and receipt.get('acknowledged') is True)
                    if not received: raise ConfiguredError('worker_receipt_identity_mismatch')
                except FileNotFoundError:
                    pass
                if received and not _exited(worker_fd): break
                if _exited(worker_fd): raise ConfiguredError('worker_exited_before_receipt')
                sleep(job['bounds']['rdp_registration_poll_ms'] / 1000)
            if not received: raise ConfiguredError('worker_receipt_unavailable')
        result['continuation_eligible'] = False
        if result.get('cleanup_confirmed') is True:
            if not clean_registration_receipt(result, job):
                raise ConfiguredError('invalid_cleanup_receipt')
            if worker.wait(timeout=timeout) != 0:
                raise ConfiguredError('cleanup_worker_failed')
            exited = _read_private_json(folder / 'worker_exited')
            if exited != dict(nonce=nonce, worker_pid=worker.pid, worker_start=start):
                raise ConfiguredError('cleanup_worker_identity_mismatch')
            if verify_cleanup is None or verify_cleanup(result['cleanup']) is not True:
                raise ConfiguredError('cleanup_session_unverified')
            result['continuation_eligible'] = True
        return result
    except Exception as error:
        _private_json(folder / 'cancel', dict(nonce=nonce))
        return dict(state='unresolved', reason=_failure_code(error), remote_session='unverified')
    finally:
        for sig, handler in old_handlers.items(): signal.signal(sig, handler)
        if worker_fd is not None: os.close(worker_fd)
        if worker is not None and worker.poll() is not None: worker.wait(timeout=timeout)
        # Private evidence/control records are retained, never deleted recursively.


def main(argv=None):
    parser = argparse.ArgumentParser(description='Configured serial SDL RDP frontend/worker')
    parser.add_argument('--worker')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--job-fd', type=int, default=0)
    args = parser.parse_args(argv)
    import dbus
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    if os.geteuid() == 0 or not address.startswith('unix:') or ';' in address:
        raise ConfiguredError('existing_nonroot_local_session_bus_required')
    factory = lambda: dbus.bus.BusConnection(address)
    if args.worker:
        configured_worker(Path(args.worker), factory, dbus.Interface, dbus.types.UnixFd)
        return 0
    with os.fdopen(os.dup(args.job_fd)) as stream:
        raw = stream.read(65537)
    if len(raw) > 65536: raise ConfiguredError('job_budget_exceeded')
    job = configured_job(json.loads(raw))
    bus = factory()
    try: job = configured_preflight(job, bus, dbus.Interface)
    finally: bus.close()
    if args.preflight:
        result = job
    else:
        def verify_cleanup(receipt):
            connection = factory()
            try:
                fresh = configured_preflight({k: job[k] for k in ('target', 'settings', 'bounds', 'mechanical',
                    'desktop', 'slot', 'x', 'y', 'width', 'height')}, connection, dbus.Interface)
                return fresh['broker_owner'] == job['broker_owner'] and fresh['source'] == job['source']
            finally: connection.close()
        try: result = configured_frontend(job, verify_cleanup=verify_cleanup)
        except Exception as error:
            result = dict(state='unresolved', phase='frontend', reason=_failure_code(error), remote_session='unverified')
    print(json.dumps(result, sort_keys=True))
    return 0 if args.preflight or result['state'] == 'completed' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps(dict(state='preflight_failed', reason=_failure_code(error), remote_session='unverified')), file=sys.stderr)
        sys.exit(2)
