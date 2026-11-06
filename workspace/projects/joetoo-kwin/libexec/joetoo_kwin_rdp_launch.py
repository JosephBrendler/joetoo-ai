#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Private SDL development adapter; no CLI, D-Bus API or configured recipe.

The future approved launcher must arm the broker before spawning, then pass its
actual child handle and this bounded log reader to _bind_rdp_process().
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


def settings(data):
    """Explicit bounds passed across the future launcher/broker boundary."""
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
            '/t:' + marker, '/log-level:INFO', '/log-filters:com.freerdp.client.SDL:DEBUG']


def development_environment(environment):
    """Child-only driver selection; log evidence must still confirm the driver."""
    result = dict(environment)
    result.pop('SDL_VIDEODRIVER', None)
    result['SDL_VIDEO_DRIVER'] = 'wayland'
    return result


class BackendEvidence:
    """Read a private regular child log, never a pipe or a raw log export.

    The future launcher redirects its owned child to this 0600 regular file.
    pread() keeps reader/writer offsets independent. Closing our duplicate never
    breaks a running viewer's output pipe or signals the child. The launcher
    owns log retention and process lifetime; no native launcher is wired yet.
    """
    def __init__(self, process, log, bounds):
        self.limit = settings(bounds)['rdp_backend_log_byte_limit']
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
                if int(match[1]) != self.pid or match[2] != b'wayland':
                    raise ValueError('SDL native-Wayland backend not established')
                self.driver = 'wayland'
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


def _proc_info(pid):
    base = '/proc/' + str(pid)
    with open(base + '/stat', 'rb') as stream:
        raw = stream.read(8193)
    if len(raw) > 8192:
        raise ValueError('Invalid process identity')
    fields = raw.rsplit(b')', 1)[1].split()
    return dict(parent=int(fields[1]), start=int(fields[19]),
                uid=os.stat(base).st_uid, exe=_inode(base + '/exe'))


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
            info = _proc_info(self.pid)
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
            info = _proc_info(self.pid)
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
    def __init__(self, caller, pid, log_fd, floor, executable, byte_limit):
        self.fd = None
        self.caller = caller
        self.pid = pid
        self.executable = executable
        self.byte_limit = byte_limit
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
        if drivers != [b'SDL_VIDEO_DRIVER=wayland']:
            return 1
        return 1 if _exited(self.fd) else None

    def close(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)
