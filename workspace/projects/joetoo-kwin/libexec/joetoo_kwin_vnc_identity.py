#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transaction-local, read-only TigerVNC desktop-role observation via libxcb.

Select SubstructureNotify, never the WM's exclusive SubstructureRedirect mask.
The stock viewer's DesktopWindow::show sends a ClientMessage to the root with
its client XID. This is role evidence only; KWin UUID/PID/lifecycle checks remain
mandatory. No authentication, geometry, focus or keyboard grab is requested.
"""
import ctypes as C
import ctypes.util
import os
import json
import select
import signal
import subprocess
import sys
import time
import re
import struct

ROLE_ATOM = b'_XWAYLAND_MAY_GRAB_KEYBOARD'
SUBSTRUCTURE_NOTIFY = 1 << 19
STRUCTURE_NOTIFY = 1 << 17
CW_EVENT_MASK = 1 << 11


class Cookie(C.Structure):
    _fields_ = [('sequence', C.c_uint)]


class ScreenIterator(C.Structure):
    _fields_ = [('data', C.c_void_p), ('rem', C.c_int), ('index', C.c_int)]


def decode_event(data, atom):
    """Decode the native-endian XCB wire event, not an English window title."""
    if len(data) != 32:
        raise ValueError('Invalid X11 event size')
    kind = data[0] & 0x7f
    if kind == 0:
        raise RuntimeError('X11 observer protocol error')
    if kind == 33 and data[0] & 0x80 and data[1] == 32:
        xid, message_type, enabled = struct.unpack_from('=III', data, 4)
        if message_type == atom and enabled == 1 and xid:
            return 'desktop', xid
    if kind == 17:
        return 'destroyed', struct.unpack_from('=I', data, 8)[0]
    return None


class NativeObserver:
    """Own an independent X connection; close it at every terminal outcome."""
    def __init__(self):
        display = os.environ.get('DISPLAY', '')
        if not re.fullmatch(r'(?:unix)?:[0-9]+(?:\.[0-9]+)?', display):
            raise RuntimeError('A local X11/XWayland DISPLAY is required')
        name = ctypes_library()
        self.lib = C.CDLL(name)
        self.libc = C.CDLL(None)
        self.libc.free.argtypes = [C.c_void_p]
        signatures = {
            'xcb_connect': ([C.c_char_p, C.POINTER(C.c_int)], C.c_void_p),
            'xcb_connection_has_error': ([C.c_void_p], C.c_int),
            'xcb_get_setup': ([C.c_void_p], C.c_void_p),
            'xcb_setup_roots_iterator': ([C.c_void_p], ScreenIterator),
            'xcb_screen_next': ([C.POINTER(ScreenIterator)], None),
            'xcb_intern_atom': ([C.c_void_p, C.c_uint8, C.c_uint16, C.c_char_p], Cookie),
            'xcb_intern_atom_reply': ([C.c_void_p, Cookie, C.POINTER(C.c_void_p)], C.c_void_p),
            'xcb_change_window_attributes_checked': ([C.c_void_p, C.c_uint32, C.c_uint32, C.c_void_p], Cookie),
            'xcb_request_check': ([C.c_void_p, Cookie], C.c_void_p),
            'xcb_poll_for_event': ([C.c_void_p], C.c_void_p),
            'xcb_flush': ([C.c_void_p], C.c_int),
            'xcb_get_file_descriptor': ([C.c_void_p], C.c_int),
            'xcb_disconnect': ([C.c_void_p], None),
        }
        for function, (args, result) in signatures.items():
            method = getattr(self.lib, function); method.argtypes = args; method.restype = result
        screen = C.c_int()
        self.connection = self.lib.xcb_connect(display.encode(), C.byref(screen))
        try:
            self.check()
            iterator = self.lib.xcb_setup_roots_iterator(self.lib.xcb_get_setup(self.connection))
            for _ in range(screen.value): self.lib.xcb_screen_next(C.byref(iterator))
            if not iterator.rem: raise RuntimeError('Missing X11 screen')
            root = C.c_uint32.from_address(iterator.data).value
            reply = self.lib.xcb_intern_atom_reply(self.connection,
                self.lib.xcb_intern_atom(self.connection, 0, len(ROLE_ATOM), ROLE_ATOM), None)
            if not reply: raise RuntimeError('Cannot query TigerVNC role atom')
            try: self.atom = C.c_uint32.from_address(reply + 8).value
            finally: self.libc.free(reply)
            self.select(root, SUBSTRUCTURE_NOTIFY)
        except Exception:
            self.close(); raise

    def check(self):
        if self.lib.xcb_connection_has_error(self.connection):
            raise RuntimeError('X11 identity observer disconnected')

    def select(self, xid, mask):
        bits = C.c_uint32(mask)
        error = self.lib.xcb_request_check(self.connection,
            self.lib.xcb_change_window_attributes_checked(self.connection, xid, CW_EVENT_MASK, C.byref(bits)))
        if error:
            self.libc.free(error)
            raise RuntimeError('X11 identity watch unavailable')
        self.lib.xcb_flush(self.connection)

    def drain(self, limit):
        self.check()
        events = []
        for _ in range(limit):
            event = self.lib.xcb_poll_for_event(self.connection)
            if not event: return events
            try: decoded = decode_event(C.string_at(event, 32), self.atom)
            finally: self.libc.free(event)
            if decoded: events.append(decoded)
        # A flood must not hide competing/destruction events or block D-Bus.
        raise RuntimeError('X11 identity event budget exhausted')

    def close(self):
        if getattr(self, 'connection', None):
            self.lib.xcb_disconnect(self.connection); self.connection = None


def ctypes_library():
    name = C.util.find_library('xcb')
    if not name: raise RuntimeError('libxcb is unavailable')
    return name


class DesktopObserver:
    """Bound synchronous XCB work in a broker-owned, disposable process.

    Only JSON role/destruction events cross the private pipe. The parent never
    trusts a launcher-supplied UUID and never reads the child's X credentials.
    """
    def __init__(self, bounds):
        # The broker is an OpenRC service, not a child of the interactive
        # launcher. Do not assume it inherited the launcher's X11 context.
        if not re.fullmatch(r'(?:unix)?:[0-9]+(?:\.[0-9]+)?',os.environ.get('DISPLAY','')):
            raise RuntimeError('Broker requires a local DISPLAY for the X11/XWayland identity observer')
        self.process=None;self.buffer=b'';self.queue=[];self.ready=False
        self.limit=bounds['vnc_identity_event_limit']
        self.cleanup=bounds['vnc_cleanup_timeout_ms']/1000
        self.process=subprocess.Popen([sys.executable,__file__,'--observe',str(os.getpid()),
            str(self.limit),str(bounds['vnc_supervisor_poll_interval_ms'])],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            close_fds=True,start_new_session=True)
        os.set_blocking(self.process.stdout.fileno(),False)
        deadline=time.monotonic()+bounds['vnc_identity_start_timeout_ms']/1000
        try:
            while not self.ready:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise RuntimeError('X11 identity observer startup timed out')
                select.select([self.process.stdout],[],[],remaining)
                self._read()
        except Exception:
            self.close();raise

    def _read(self):
        if self.process.poll() is not None: raise RuntimeError('X11 identity observer exited')
        try: block=os.read(self.process.stdout.fileno(),65536)
        except BlockingIOError: return
        if not block: raise RuntimeError('X11 identity observer pipe closed')
        self.buffer+=block
        if len(self.buffer)>65536: raise RuntimeError('X11 identity observer output overflow')
        while b'\n' in self.buffer:
            line,self.buffer=self.buffer.split(b'\n',1)
            message=json.loads(line)
            if message=={'ready':True}: self.ready=True;continue
            if not isinstance(message,list) or len(message)!=2 or message[0] not in ('desktop','destroyed') or type(message[1]) is not int or not 0<message[1]<=0xffffffff:
                raise RuntimeError('Invalid X11 identity event')
            self.queue.append(tuple(message))
            if len(self.queue)>self.limit: raise RuntimeError('X11 identity event budget exhausted')

    def select(self, xid, mask):
        # The native child installs each StructureNotify watch before emitting
        # the role event. The broker's interface remains observational only.
        return None

    def drain(self, limit):
        self._read()
        result=self.queue;self.queue=[]
        if len(result)>limit: raise RuntimeError('X11 identity event budget exhausted')
        return result

    def close(self):
        if self.process is not None:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    try: self.process.wait(timeout=self.cleanup)
                    except subprocess.TimeoutExpired:
                        self.process.kill();self.process.wait(timeout=self.cleanup)
                else: self.process.wait()
            except (OSError,subprocess.SubprocessError):
                # Keep the process handle for a later bounded retry; never
                # claim observer teardown or grant registration on uncertainty.
                return False
            self.process.stdout.close();self.process=None
        return True


def observe_worker(parent, limit, poll_ms):
    # An observer belongs to the broker, unlike the separate viewer supervisor.
    # Linux parent-death signalling closes the watch even if XCB is awaiting a
    # reply when the broker exits. No application windows/processes are owned.
    libc=C.CDLL(None)
    if libc.prctl(1,signal.SIGTERM,0,0,0)!=0 or os.getppid()!=parent:
        raise RuntimeError('Cannot bind X11 observer lifetime')
    observer=NativeObserver()
    try:
        print(json.dumps({'ready':True}),flush=True)
        descriptor=observer.lib.xcb_get_file_descriptor(observer.connection)
        while True:
            for kind,xid in observer.drain(limit):
                if kind=='desktop': observer.select(xid,STRUCTURE_NOTIFY)
                print(json.dumps([kind,xid]),flush=True)
            select.select([descriptor],[],[],poll_ms/1000)
    finally: observer.close()


if __name__=='__main__':
    try:
        if sys.argv[1:2]!=['--observe']: raise ValueError('Observer is broker-only')
        observe_worker(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
    except (OSError,RuntimeError,ValueError,BrokenPipeError): sys.exit(1)
