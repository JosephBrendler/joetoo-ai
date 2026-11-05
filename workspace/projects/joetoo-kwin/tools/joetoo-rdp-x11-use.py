#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated X11 activity-property experiment, NEVER managed-window enrollment.

SDL 3.4.18 X11_UpdateUserTime updates _NET_WM_USER_TIME after input presses.
Read only property notifications, not key/button events, text, or input devices.
The first changed, nonzero timestamp is latched; no activity cadence is saved.
Initial timestamps are not use evidence. Latches are not desktop-role proof.
Native operations occur only with --serve; tests and --verify are offline.
"""
import argparse
import ctypes as C
import ctypes.util
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import struct
import sys
import time
import uuid


class Invalid(ValueError):
    pass


MARKER = re.compile(rb'joetoo-rdp-proof-[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}')


def require(test, reason):
    if not test:
        raise Invalid(reason)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


class Capture:
    """Bounded ledger; no raw activity timestamps or repeated use observations."""
    def __init__(self, emit, max_candidates):
        self.emit, self.limit = emit, max_candidates
        self.windows = {}; self.history = []; self.generation = 0; self.gaps = 0

    def add(self, xid, pid, marker, baseline, timestamp, delegated=False):
        if xid in self.windows and self.windows[xid]['live']:
            return
        require(self.generation < self.limit, 'candidate_limit')
        self.generation += 1
        w = dict(xid=xid, pid=pid, generation=self.generation, marker=marker,
                 baseline=baseline, live=True, used=False, uuid=None,
                 property_supported=not delegated)
        self.windows[xid] = dict(w, last=timestamp)
        self.history.append(self.windows[xid])
        self.emit('candidate', w)

    def observe(self, xid, timestamp):
        w = self.windows.get(xid)
        if not w or not w['live'] or w['used'] or not w['property_supported']:
            return False
        previous = w['last']; w['last'] = timestamp
        # Keep checking absent/unchanged/zero timestamps. Do not stop after one
        # unsuccessful check. A first value following absence establishes a
        # baseline, because initial property publication is not itself proof of
        # interaction. X server timestamps are opaque wrapping uint32s.
        if timestamp is None or timestamp == 0 or timestamp == previous or previous is None:
            return False
        w['used'] = True
        self.emit('use_latched', dict(generation=w['generation'], xid=xid,
                                     evidence='changed_nonzero_user_time',
                                     desktop_role='unproven'))
        w.pop('last', None)
        return True

    def remove(self, xid):
        w = self.windows.get(xid)
        if w and w['live']:
            w['live'] = False; w.pop('last', None)
            self.emit('removed', dict(xid=xid, generation=w['generation']))

    def candidates(self):
        return [dict(xid=w['xid'], pid=w['pid'], generation=w['generation'])
                for w in self.windows.values() if w['live'] and not w['uuid']]

    def link(self, links):
        require(isinstance(links, list) and len(links) <= self.limit, 'invalid_links')
        for link in links:
            require(isinstance(link, dict) and set(link) == {'xid', 'pid', 'generation', 'uuid'}, 'invalid_link')
            w = self.windows.get(link['xid'])
            # A disappeared window is a coverage gap, never an invitation to
            # associate a later window with an earlier generation.
            if not w or not w['live'] or link['generation'] != w['generation']:
                continue
            require(link['pid'] == w['pid'] and isinstance(link['uuid'], str)
                    and re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', link['uuid']), 'invalid_identity')
            require(w['uuid'] in (None, link['uuid']), 'uuid_replacement')
            require(not any(o is not w and o['uuid'] == link['uuid'] for o in self.history), 'duplicate_uuid')
            if w['uuid'] is None:
                w['uuid'] = link['uuid']
                self.emit('uuid_link', link)

    def summary(self):
        return dict(candidates=len(self.history), latched=sum(w['used'] for w in self.history),
                    unlinked=sum(not w['uuid'] for w in self.history),
                    unsupported=sum(not w['property_supported'] for w in self.history),
                    discovery_gaps=self.gaps, desktop_role='unproven',
                    lifecycle_coverage='requires_comparison_with_KWin_capture')


class Cookie(C.Structure):
    _fields_ = [('sequence', C.c_uint)]


class Iterator(C.Structure):
    _fields_ = [('data', C.c_void_p), ('rem', C.c_int), ('index', C.c_int)]


class X11:
    """Independent libxcb connection. No input selection or window mutation.

    Only this connection's nonexclusive PropertyChange/StructureNotify masks
    are set. Destroyed-window races become explicit evidence gaps.
    """
    def __init__(self, max_clients):
        require(re.fullmatch(r'(?:unix)?:[0-9]+(?:\.[0-9]+)?', os.getenv('DISPLAY', '')), 'local_DISPLAY_required')
        name = ctypes.util.find_library('xcb'); require(name, 'libxcb_missing')
        self.lib = C.CDLL(name); self.libc = C.CDLL(None)
        self.libc.free.argtypes = [C.c_void_p]; self.max_clients = max_clients
        methods = {
            'connect': ([C.c_char_p, C.POINTER(C.c_int)], C.c_void_p),
            'disconnect': ([C.c_void_p], None), 'connection_has_error': ([C.c_void_p], C.c_int),
            'get_setup': ([C.c_void_p], C.c_void_p),
            'setup_roots_iterator': ([C.c_void_p], Iterator),
            'screen_next': ([C.POINTER(Iterator)], None),
            'intern_atom': ([C.c_void_p, C.c_uint8, C.c_uint16, C.c_char_p], Cookie),
            'intern_atom_reply': ([C.c_void_p, Cookie, C.POINTER(C.c_void_p)], C.c_void_p),
            'get_property': ([C.c_void_p, C.c_uint8, C.c_uint32, C.c_uint32, C.c_uint32, C.c_uint32, C.c_uint32], Cookie),
            'get_property_reply': ([C.c_void_p, Cookie, C.POINTER(C.c_void_p)], C.c_void_p),
            'change_window_attributes_checked': ([C.c_void_p, C.c_uint32, C.c_uint32, C.c_void_p], Cookie),
            'request_check': ([C.c_void_p, Cookie], C.c_void_p),
            'poll_for_event': ([C.c_void_p], C.c_void_p),
            'flush': ([C.c_void_p], C.c_int),
        }
        for method, (args, result) in methods.items():
            f = getattr(self.lib, 'xcb_' + method); f.argtypes = args; f.restype = result
        screen = C.c_int(); self.conn = self.lib.xcb_connect(None, C.byref(screen))
        try:
            require(not self.lib.xcb_connection_has_error(self.conn), 'X11_connection_failed')
            it = self.lib.xcb_setup_roots_iterator(self.lib.xcb_get_setup(self.conn))
            for _ in range(screen.value): self.lib.xcb_screen_next(C.byref(it))
            require(it.rem > 0, 'X11_screen_missing')
            self.root = C.c_uint32.from_address(it.data).value
            self.atoms = {}
            for atom in ['_NET_CLIENT_LIST', '_NET_WM_PID', 'WM_CLASS', '_NET_WM_NAME',
                         '_NET_WM_USER_TIME', '_NET_WM_USER_TIME_WINDOW']:
                b = atom.encode()
                p = self.lib.xcb_intern_atom_reply(self.conn, self.lib.xcb_intern_atom(self.conn, 0, len(b), b), None)
                require(p, 'atom_query_failed')
                try: self.atoms[atom] = C.c_uint32.from_address(p + 8).value
                finally: self.libc.free(p)
            require(all(self.atoms.values()), 'required_X11_atom_missing')
            self.watch(self.root, (1 << 19) | (1 << 22))
        except BaseException:
            self.close(); raise

    def close(self):
        if self.conn:
            self.lib.xcb_disconnect(self.conn); self.conn = None

    def watch(self, xid, mask):
        bits = C.c_uint32(mask)
        p = self.lib.xcb_request_check(self.conn, self.lib.xcb_change_window_attributes_checked(
            self.conn, xid, 1 << 11, C.byref(bits)))
        if p:
            self.libc.free(p); raise Invalid('window_watch_failed')
        self.lib.xcb_flush(self.conn)

    def prop(self, xid, name, count=256):
        error = C.c_void_p()
        p = self.lib.xcb_get_property_reply(self.conn, self.lib.xcb_get_property(
            self.conn, 0, xid, self.atoms[name], 0, 0, count), C.byref(error))
        try:
            require(not error.value and p, 'property_query_failed')
            header = C.string_at(p, 32)
            fmt = header[1]; typ, after, length = struct.unpack_from('=III', header, 8)
            require(after == 0 and fmt in (0, 8, 32), 'property_bound_or_format')
            size = length * (fmt // 8)
            require(size <= count * 4, 'property_size')
            return fmt, typ, C.string_at(p + 32, size)
        finally:
            if p: self.libc.free(p)
            if error.value: self.libc.free(error)

    def number(self, xid, name):
        fmt, typ, value = self.prop(xid, name, 1)
        if fmt == 0: return None
        require(fmt == 32 and typ in (6, 33) and len(value) == 4, 'invalid_numeric_property')
        return struct.unpack('=I', value)[0]

    def clients(self):
        fmt, typ, raw = self.prop(self.root, '_NET_CLIENT_LIST', self.max_clients)
        require(fmt == 32 and typ == 33 and len(raw) % 4 == 0, 'invalid_client_list')
        return struct.unpack('=' + 'I' * (len(raw) // 4), raw)

    def events(self, limit):
        require(not self.lib.xcb_connection_has_error(self.conn), 'X11_disconnected')
        result = []
        for _ in range(limit):
            p = self.lib.xcb_poll_for_event(self.conn)
            if not p: return result
            try: result.append(C.string_at(p, 32))
            finally: self.libc.free(p)
        raise Invalid('X11_event_budget_exhausted')


class Ledger:
    def __init__(self, directory, settings):
        path = Path(directory)
        require(path.is_absolute() and '..' not in path.parts, 'unsafe_directory')
        fd = os.open('/', os.O_DIRECTORY | os.O_RDONLY)
        try:
            for part in path.parts[1:]:
                new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = new
            st = os.fstat(fd)
            require(st.st_uid == os.geteuid() and stat.S_IMODE(st.st_mode) == 0o700, 'private_directory_required')
            self.dirfd = fd
            self.fd = os.open('x11-use.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        except BaseException:
            os.close(fd); raise
        self.seq = 0; self.digest = hashlib.sha256(); self.settings = settings
        self.origin = time.monotonic_ns()

    def file(self, name, data):
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=self.dirfd)
        try:
            with os.fdopen(fd, 'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
            os.fsync(self.dirfd)
        except BaseException: raise

    def emit(self, kind, body):
        self.seq += 1
        # At most candidate/link/latch/removal per generation, plus framing.
        require(self.seq <= self.settings['maxCandidates'] * 5 + 3, 'ledger_record_limit')
        data = encode(dict(seq=self.seq, kind=kind, run=self.settings['run'],
                           wall_time_ms=int(time.time() * 1000),
                           elapsed_ns=time.monotonic_ns() - self.origin, body=body))
        require(len(data) <= 4096, 'ledger_record_size')
        remaining = memoryview(data)
        while remaining:
            n = os.write(self.fd, remaining); require(n > 0, 'short_write'); remaining = remaining[n:]
        os.fsync(self.fd); self.digest.update(data)

    def finish(self, summary, reason):
        self.emit('end', dict(summary, reason=reason))
        self.file('x11-use-receipt.json', encode(dict(records=self.seq, sha256=self.digest.hexdigest())))

    def close(self):
        os.close(self.fd); os.close(self.dirfd)


def serve(args):
    # No new bus, service activation, native process launch, or network transport.
    require(os.geteuid() != 0, 'nonroot_required')
    address = os.getenv('DBUS_SESSION_BUS_ADDRESS', '')
    require(address.startswith('unix:') and ';' not in address, 'existing_unix_session_bus_required')
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    import dbus.service
    from gi.repository import GLib
    DBusGMainLoop(set_as_default=True)
    bus = dbus.bus.BusConnection(address)
    owner = str(bus.get_name_owner('org.kde.KWin'))
    require(int(bus.get_unix_user(owner)) == os.geteuid(), 'KWin_owner_uid')
    settings = dict(run=uuid.uuid4().hex, receiver=str(bus.get_unique_name()), pollMs=args.poll_ms,
                    ackMs=args.ack_ms, maxCandidates=args.max_candidates,
                    expectedClass='com.freerdp.client.sdl3')
    ledger = Ledger(args.directory, settings); native = None; loop = GLib.MainLoop()
    capture = Capture(ledger.emit, args.max_candidates); reason = ['interrupted']; ready = [False]
    last_link = [None]; cycles = [0]
    baseline = set(); source = None; deadline = None

    def discover(xid, old=False):
        if xid in capture.windows and capture.windows[xid]['live']: return
        try:
            fmt, typ, raw = native.prop(xid, 'WM_CLASS', 128)
            parts = raw.split(b'\0')
            if fmt != 8 or typ != 31 or len(parts) < 2 or parts[1] != settings['expectedClass'].encode(): return
            pid = native.number(xid, '_NET_WM_PID'); require(pid and pid > 0, 'candidate_PID_missing')
            native.watch(xid, (1 << 17) | (1 << 22))
            timestamp = native.number(xid, '_NET_WM_USER_TIME')
            delegated = native.number(xid, '_NET_WM_USER_TIME_WINDOW') not in (None, 0, xid)
            _, _, title = native.prop(xid, '_NET_WM_NAME', 128)
            marker = title.decode('ascii') if MARKER.fullmatch(title) else None
            capture.add(xid, pid, marker, old, timestamp, delegated)
        except Invalid as error:
            if str(error) in ('candidate_limit', 'ledger_record_limit', 'ledger_record_size'):
                raise
            capture.gaps += 1  # vanished/oversized/unreadable candidate: never infer no activity

    def step():
        nonlocal source
        try:
            require(str(bus.get_name_owner('org.kde.KWin')) == owner, 'KWin_owner_replaced')
            require(last_link[0] is None or time.monotonic() - last_link[0] <= args.ack_ms / 1000,
                    'linker_liveness_expired')
            for event in native.events(args.event_limit):
                kind = event[0] & 127
                require(kind != 0, 'X11_protocol_error')
                if kind in (16, 19, 21): discover(struct.unpack_from('=I', event, 8)[0])
                elif kind == 17: capture.remove(struct.unpack_from('=I', event, 8)[0])
                elif kind == 28:
                    xid, atom = struct.unpack_from('=II', event, 4)
                    if atom in (native.atoms['_NET_WM_USER_TIME'], native.atoms['_NET_WM_NAME']) and xid in capture.windows:
                        w = capture.windows[xid]
                        if w['live'] and not w['used']:
                            try:
                                if atom == native.atoms['_NET_WM_NAME']:
                                    _, _, title = native.prop(xid, '_NET_WM_NAME', 128)
                                    marker = title.decode('ascii') if MARKER.fullmatch(title) else None
                                    if marker != w['marker']:
                                        require(not w.get('marker_changed'), 'marker_change_limit')
                                        w['marker'] = marker; w['marker_changed'] = True
                                        ledger.emit('marker_changed', dict(generation=w['generation'], marker=marker))
                                elif capture.observe(xid, native.number(xid, '_NET_WM_USER_TIME')):
                                    native.watch(xid, 1 << 17)  # latch: no further property surveillance
                            except Invalid as error:
                                if w['used'] or str(error) in ('marker_change_limit', 'ledger_record_limit', 'ledger_record_size'): raise
                                capture.gaps += 1
            for xid in native.clients(): discover(xid, xid in baseline)
            return True
        except Exception:
            source = None; reason[0] = 'observation_failed'; loop.quit(); return False

    class Service(dbus.service.Object):
        def authenticated(self, text, sender):
            require(str(sender) == owner and str(bus.get_name_owner('org.kde.KWin')) == owner, 'sender_rejected')
            require(len(text) < args.max_candidates * 256 + 256, 'message_bound')
            data = json.loads(text); require(data['run'] == settings['run'], 'run_rejected')
            last_link[0] = time.monotonic()
            return data['body']

        @dbus.service.method('org.joetoo.RDPX11Use', in_signature='s', out_signature='s', sender_keyword='sender')
        def Candidates(self, text, sender=None):
            try:
                self.authenticated(text, sender)
                # A second request proves KWin received the first Links reply.
                if cycles[0] and not ready[0]:
                    ledger.emit('linker_ready', {})
                    ledger.file('linker-ready.json', encode(dict(run=settings['run'], owner=owner)))
                    ready[0] = True
                return json.dumps(dict(run=settings['run'], ok=True, body=capture.candidates()))
            except Exception:
                reason[0] = 'linker_failed'; loop.quit(); raise

        @dbus.service.method('org.joetoo.RDPX11Use', in_signature='s', out_signature='s', sender_keyword='sender')
        def Links(self, text, sender=None):
            try:
                capture.link(self.authenticated(text, sender))
                cycles[0] += 1
                return json.dumps(dict(run=settings['run'], ok=True, body=None))
            except Exception:
                reason[0] = 'linker_failed'; loop.quit(); raise

        @dbus.service.method('org.joetoo.RDPX11Use', in_signature='s', out_signature='s', sender_keyword='sender')
        def Status(self, text, sender=None):
            # The wrapper may inspect readiness, but only pinned KWin can supply
            # candidate links. Status never renews the linker's liveness lease.
            require(int(bus.get_unix_user(sender)) == os.geteuid(), 'status_uid_rejected')
            require(text == settings['run'], 'status_run_rejected')
            current = str(bus.get_name_owner('org.kde.KWin')) == owner
            fresh = last_link[0] is not None and time.monotonic() - last_link[0] <= args.ack_ms / 1000
            return json.dumps(dict(run=settings['run'], kwin_owner=owner,
                                   ready=bool(ready[0] and current and fresh)))

    service = None
    try:
        native = X11(args.max_clients); baseline = set(native.clients())
        ledger.emit('ready', dict(settings, kwin_owner=owner, duration_seconds=args.seconds))
        template = Path(__file__).with_suffix('.js').read_text()
        ledger.file('linker.js', ('var JOETOO_RDP_X11_USE = ' + json.dumps(settings) + ';\n' + template).encode())
        service = Service(bus, '/org/joetoo/RDPX11Use')
        for xid in baseline: discover(xid, True)
        source = GLib.timeout_add(args.poll_ms, step)
        def stop(signum, frame):
            reason[0] = 'requested' if signum == signal.SIGTERM else 'interrupted'; loop.quit()
        signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
        def expire():
            nonlocal deadline
            deadline = None; reason[0] = 'time_limit'; loop.quit(); return False
        deadline = GLib.timeout_add_seconds(args.seconds, expire)
        loop.run()
        summary = capture.summary(); summary['linker_ready'] = ready[0]
        summary['observation_completed_as_requested'] = reason[0] == 'requested' and ready[0]
        ledger.finish(summary, reason[0])
        return 0 if reason[0] == 'requested' and ready[0] else 1
    finally:
        if source: GLib.source_remove(source)
        if deadline: GLib.source_remove(deadline)
        if service: service.remove_from_connection()
        if native: native.close()
        ledger.close(); bus.close()


def private_path(directory):
    path = Path(directory)
    # Use the same ownership/path checks without creating any file.
    for p in [path, *path.parents]: require(not p.is_symlink(), 'symlink_path')
    require(path.is_absolute() and '..' not in path.parts and stat.S_IMODE(path.stat().st_mode) == 0o700
            and path.stat().st_uid == os.geteuid(), 'private_directory_required')
    return path


def status(directory):
    """Check current bus owner and live linker, not merely a stale ready file."""
    path = private_path(directory)
    fd = os.open(path / 'x11-use.jsonl', os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
                and stat.S_IMODE(info.st_mode) == 0o600, 'unsafe_evidence_file')
        line = stream.readline(8193)
    require(len(line) <= 8192 and line.endswith(b'\n'), 'invalid_ready_record')
    header = json.loads(line)
    require(header['kind'] == 'ready' and header['seq'] == 1, 'invalid_ready_record')
    cfg = header['body']
    require(re.fullmatch(r':\d+\.\d+', cfg['receiver'])
            and re.fullmatch('[a-f0-9]{32}', cfg['run']), 'invalid_ready_identity')
    address = os.getenv('DBUS_SESSION_BUS_ADDRESS', '')
    require(address.startswith('unix:') and ';' not in address, 'existing_unix_session_bus_required')
    import dbus
    bus = dbus.bus.BusConnection(address)
    try:
        require(str(bus.get_name_owner('org.kde.KWin')) == cfg['kwin_owner']
                and int(bus.get_unix_user(cfg['receiver'])) == os.geteuid(), 'bus_identity_changed')
        obj = bus.get_object(cfg['receiver'], '/org/joetoo/RDPX11Use', introspect=False)
        result = json.loads(str(obj.Status(cfg['run'], dbus_interface='org.joetoo.RDPX11Use',
                                          timeout=cfg['ackMs'] / 1000)))
        require(result['run'] == cfg['run'] and result['kwin_owner'] == cfg['kwin_owner'], 'status_identity')
        return result
    finally: bus.close()


def verify(directory):
    path = private_path(directory)
    def read(name, bound):
        p = path / name; st = p.lstat()
        require(stat.S_ISREG(st.st_mode) and st.st_uid == os.geteuid()
                and stat.S_IMODE(st.st_mode) == 0o600 and st.st_size <= bound, 'unsafe_evidence_file')
        return p.read_bytes()
    data = read('x11-use.jsonl', 2 * 1024 * 1024)
    receipt = json.loads(read('x11-use-receipt.json', 4096))
    records = [json.loads(line) for line in data.splitlines()]
    require(records and records[0]['kind'] == 'ready' and records[-1]['kind'] == 'end', 'incomplete_framing')
    require([r['seq'] for r in records] == list(range(1, len(records) + 1))
            and len({r['run'] for r in records}) == 1, 'sequence_or_run')
    require(receipt == dict(records=len(records), sha256=hashlib.sha256(data).hexdigest()), 'receipt_mismatch')
    return dict(transport_complete=True, **records[-1]['body'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--serve', action='store_true'); mode.add_argument('--verify', action='store_true')
    mode.add_argument('--status', action='store_true')
    parser.add_argument('directory')
    parser.add_argument('--seconds', type=int, default=int(os.getenv('RDP_DIAG_SECONDS', '1800')))
    parser.add_argument('--poll-ms', type=int, default=10)
    parser.add_argument('--ack-ms', type=int, default=3000)
    parser.add_argument('--max-candidates', type=int, default=64)
    parser.add_argument('--max-clients', type=int, default=512)
    parser.add_argument('--event-limit', type=int, default=4096)
    args = parser.parse_args()
    require(1 <= args.seconds <= 86400 and 1 <= args.poll_ms <= 1000
            and args.poll_ms < args.ack_ms <= 60000 and 1 <= args.max_candidates <= 64
            and 1 <= args.max_clients <= 4096 and 1 <= args.event_limit <= 65536, 'invalid_bounds')
    if args.verify:
        print(json.dumps(verify(args.directory), sort_keys=True)); return 0
    if args.status:
        result = status(args.directory)
        print(json.dumps(result, sort_keys=True)); return 0 if result['ready'] is True else 1
    return serve(args)


if __name__ == '__main__':
    try: sys.exit(main())
    except Exception:
        # Never echo property values, bus payloads, environment, or credentials.
        print('X11 use diagnostic failed; retain partial evidence and inspect completion status.', file=sys.stderr)
        sys.exit(1)
