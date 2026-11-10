#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Private SDL development adapter; no CLI, D-Bus API or configured recipe.

The development launcher arms the broker before spawning, then binds its
actual direct child and private stdout descriptor through the existing API.
This module neither selects production security flags nor launches a connection.
"""
import fcntl
import ipaddress
import os
import re
import stat
import select
import time

DEFAULTS = dict(rdp_registration_timeout_ms=120000, rdp_registration_poll_ms=100,
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


def development_argv(host, port, username, marker):
    """Restricted development arguments, NOT an approved production recipe.

    No arbitrary switches, shell parsing, password or certificate exceptions.
    Production NLA/negotiation/trust decisions and the executable entry point
    remain maintainer gates. Do not use these arguments for native testing yet.
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
    return ['sdl-freerdp', '/v:' + host + ':' + str(port), '/u:' + username,
            '/t:' + marker,
            '/size:1024x768',
            '/smart-sizing:800x600',
            '/log-level:INFO',
            '/log-filters:com.freerdp.client.SDL:DEBUG']


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
