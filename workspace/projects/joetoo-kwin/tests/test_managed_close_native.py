# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Actual compiled XCB helper over a disposable socketpair, never an X server.

Kernel credential delivery is separately availability-tested; wire tests use
a clearly isolated platform credential double. The peer models the adapter's GO; it does NOT prove KWin's
UUID lookup/fence ordering. Those remain explicit native acceptance obligations.
"""
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class XcbCloseWireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('c++') or not shutil.which('pkg-config'):
            raise unittest.SkipTest('C++/pkg-config unavailable for isolated native ABI test')
        cls.temp = tempfile.TemporaryDirectory(prefix='joetoo-close-wire-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = Path(cls.temp.name)/'helper'
        flags = subprocess.run(['pkg-config','--cflags','--libs','xcb'],capture_output=True,text=True)
        if flags.returncode:
            raise unittest.SkipTest('libxcb development files unavailable')
        import shlex
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
            cls.mock_credentials=False
        except PermissionError:
            cls.mock_credentials=True
        finally:
            a.close();b.close()
        # The sandbox denies socket credential options. Interpose only the
        # platform IPC seam; production receiveOwnedPacket logic still executes.
        # This fixture is never part of CMake or the installed helper.
        shim=Path(cls.temp.name)/'credentials.cpp'
        shim.write_text(r'''#include <sys/socket.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
extern "C" int __wrap_setsockopt(int,int,int,const void*,socklen_t) { return 0; }
extern "C" int __wrap_getsockopt(int,int,int,void *p,socklen_t *n) { *static_cast<int*>(p)=SOCK_SEQPACKET;*n=sizeof(int);return 0; }
extern "C" ssize_t __wrap_recvmsg(int fd,msghdr *m,int) {
    auto count=read(fd,m->msg_iov[0].iov_base,m->msg_iov[0].iov_len);
    if(count<0)return count;
    m->msg_controllen=CMSG_SPACE(sizeof(ucred));
    auto *h=CMSG_FIRSTHDR(m);h->cmsg_level=SOL_SOCKET;h->cmsg_type=SCM_CREDENTIALS;h->cmsg_len=CMSG_LEN(sizeof(ucred));
    ucred c{getppid(),geteuid(),getegid()};
    if(getenv("MOCK_FOREIGN_SENDER"))c.pid+=100000;
    memcpy(CMSG_DATA(h),&c,sizeof(c));return count;
}
''')
        shim_flags=[str(shim),'-Wl,--wrap=setsockopt,--wrap=getsockopt,--wrap=recvmsg'] if cls.mock_credentials else []
        run=subprocess.run(['c++','-std=c++20','-DJOETOO_CLOSE_TEST_FD',str(ROOT/'native/managed-close/x11.cpp')]+shim_flags+['-o',str(cls.binary)]+shlex.split(flags.stdout),capture_output=True,text=True)
        if run.returncode: raise AssertionError(run.stderr)
    def exercise(self, *, go=True, supports=True, property_type=4, extra=0, stale=False, setup=True, expired=False, foreign_sender=False):
        client, server=socket.socketpair()
        control, child_control=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        for item in (client,server,control,child_control): self.addCleanup(item.close)
        if not self.mock_credentials:
            control.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
            child_control.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        errors=[];requests=[];events=[];grabbed=False
        env=dict(os.environ,JOETOO_CLOSE_TEST_FD=str(client.fileno()))
        env.pop('DISPLAY',None);env.pop('XAUTHORITY',None)
        if foreign_sender and self.mock_credentials: env['MOCK_FOREIGN_SENDER']='1'
        process=subprocess.Popen([str(self.binary),'77','9','123','500',str(int((time.monotonic()+(-1 if expired else 1))*1000)),'0'],
            stdin=child_control.fileno(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,pass_fds=(client.fileno(),),env=env)
        def cleanup_process():
            if process.poll() is None: process.kill();process.wait(timeout=2)
            for stream in (process.stdin,process.stdout,process.stderr):
                if stream: stream.close()
        self.addCleanup(cleanup_process)
        client.close()
        child_control.close()
        control.settimeout(2)
        if not expired:
            if self.mock_credentials:
                self.assertEqual(control.recv(5),b'ready')
            else:
                ready,ancillary,flags,_=control.recvmsg(5,socket.CMSG_SPACE(struct.calcsize('3i')))
                self.assertEqual(ready,b'ready')
                credentials=[struct.unpack('3i',data) for level,kind,data in ancillary if level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS]
                self.assertEqual(credentials,[(process.pid,os.geteuid(),os.getegid())])
            if foreign_sender and not self.mock_credentials:
                packet=struct.pack('=4I',1,2,3,4)
                child=subprocess.run([os.sys.executable,'-c','import os,sys;os.write(int(sys.argv[1]),bytes.fromhex(sys.argv[2]))',str(control.fileno()),packet.hex()],
                    pass_fds=(control.fileno(),),capture_output=True,timeout=2)
                self.assertEqual(child.returncode,0,child.stderr)
            else:
                self.assertEqual(os.write(control.fileno(),struct.pack('=4I',1,2,3,4)),16)
        self.assertEqual(len(process.args),7,'the private nonce must not appear in argv')
        server.settimeout(2)
        def exact(count):
            data=b''
            while len(data)<count:
                part=server.recv(count-len(data))
                if not part: raise EOFError
                data+=part
            return data
        def send(data):
            self.assertEqual(os.write(server.fileno(), data), len(data), "short isolated wire write")
        def peer():
            nonlocal grabbed
            try:
                hello=exact(12)
                order='<' if hello[0]==ord('l') else '>'
                name,data=struct.unpack_from(order+'HH',hello,6)
                exact((name+3)//4*4+(data+3)//4*4)
                if not setup:
                    while server.recv(4096): pass # Watchdog, not a sleeping sender.
                    return
                prefix=struct.pack(order+'BBHHHIIIIHHBBBBBBBB4x',1,0,11,0,18,
                    1,0x200000,0x1fffff,0,0,65535,1,0,0,0,32,32,8,255)
                screen=struct.pack(order+'IIIIIHHHHHHIBBBB',1,2,0xffffff,0,0,1920,1080,500,300,1,1,3,0,0,24,0)
                send(prefix+screen)
                sequence=0
                while True:
                    head=exact(4);opcode=head[0];size=struct.unpack_from(order+'H',head,2)[0]*4
                    request=head+exact(size-4);sequence+=1;requests.append(opcode)
                    if opcode==16:
                        n=struct.unpack_from(order+'H',request,4)[0]
                        atom=10 if request[8:8+n]==b'WM_PROTOCOLS' else 11
                        send(struct.pack(order+'BBHII20x',1,0,sequence,0,atom))
                    elif opcode==36: grabbed=True
                    elif opcode==37: grabbed=False
                    elif opcode==43:
                        send(struct.pack(order+'BBHII20x',1,0,sequence,0,1))
                    elif opcode==20:
                        self.assertTrue(grabbed,'property must be checked while server is held')
                        if stale:
                            send(struct.pack(order+'BBHIHB21x',0,3,sequence,123,0,20))
                        else:
                            values=struct.pack(order+'I',11 if supports else 12)
                            send(struct.pack(order+'BBHIIII12x',1,32,sequence,1,property_type,extra,1)+values)
                    elif opcode==25:
                        event=request[12:44];events.append(event)
                        window,atom=struct.unpack_from(order+'II',event,4)
                        self.assertTrue(grabbed,'both fence and WM_DELETE are inside grab')
                        self.assertEqual(struct.unpack_from(order+'I',request,8)[0],0,'NoEventMask only')
                        if window==77:
                            self.assertEqual(atom,9)
                            self.assertEqual(struct.unpack_from(order+'4I',event,12),(1,2,3,4))
                            if go: self.assertEqual(os.write(control.fileno(),b'GO\n'),3)
                        else:
                            self.assertEqual((window,atom),(123,10))
                            self.assertEqual(struct.unpack_from(order+'2I',event,12),(11,0))
                    else: raise AssertionError('unexpected X11 opcode '+str(opcode))
            except EOFError: pass
            except Exception as exc: errors.append(repr(exc))
            finally: server.close()
        thread=threading.Thread(target=peer);thread.start()
        try:
            code=process.wait(timeout=3)
            out=process.stdout.read();err=process.stderr.read()
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive(),'socket peer leaked')
            self.assertEqual(errors,[])
            self.assertEqual(err,b'')
            self.assertNotIn(113,requests,'KillClient must never be sent')
            self.assertNotIn(4,requests,'DestroyWindow must never be sent')
            return code,out,events,requests
        finally:
            if process.poll() is None: process.kill();process.wait(timeout=2)
            for stream in (process.stdin,process.stdout,process.stderr):
                if stream: stream.close()
            server.close();control.close();child_control.close();thread.join(timeout=3)
    def test_supported_delete_is_one_checked_protocol_request(self):
        code,out,events,requests=self.exercise()
        self.assertEqual((code,out),(0,b'dispatched\n'))
        self.assertEqual(len(events),2)
        self.assertEqual(requests.count(36),1);self.assertEqual(requests.count(37),1)
    def test_no_go_cannot_dispatch_even_for_reused_numeric_xid(self):
        code,out,events,_=self.exercise(go=False)
        self.assertEqual(code,4);self.assertEqual(out,b'');self.assertEqual(len(events),1)
    def test_absent_wm_delete_has_no_kill_fallback(self):
        code,out,events,_=self.exercise(supports=False)
        self.assertEqual(code,5);self.assertEqual(out,b'');self.assertEqual(len(events),1)
    def test_wrong_type_and_truncated_property_fail_closed(self):
        for opts in (dict(property_type=31),dict(extra=4)):
            code,out,events,_=self.exercise(**opts)
            self.assertEqual(code,5);self.assertEqual(out,b'');self.assertEqual(len(events),1)
    def test_stale_badwindow_property_has_no_dispatch(self):
        code,out,events,_=self.exercise(stale=True)
        self.assertEqual(code,5);self.assertEqual(out,b'');self.assertEqual(len(events),1)
    def test_foreign_credential_packet_is_rejected_before_xcb(self):
        code,out,events,requests=self.exercise(foreign_sender=True)
        self.assertEqual(code,4);self.assertEqual(out,b'');self.assertEqual(events,[]);self.assertEqual(requests,[])
    def test_expired_dispatch_lease_never_connects_or_dispatches(self):
        code,out,events,requests=self.exercise(expired=True)
        self.assertEqual(code,4);self.assertEqual(out,b'');self.assertEqual(events,[]);self.assertEqual(requests,[])
    def test_independent_watchdog_bounds_blocking_setup(self):
        code,out,events,_=self.exercise(setup=False)
        self.assertEqual(code,-14);self.assertEqual(out,b'');self.assertEqual(events,[])


class KernelCredentialAvailabilityTests(unittest.TestCase):
    def test_kernel_credentials_on_isolated_socketpair(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        self.addCleanup(a.close);self.addCleanup(b.close)
        try:
            a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        except PermissionError:
            self.skipTest('sandbox denies SO_PASSCRED; native credential IPC not exercised')
        self.assertEqual(os.write(b.fileno(),b'hello'),5)
        data,ancillary,flags,_=a.recvmsg(5,socket.CMSG_SPACE(struct.calcsize('3i')))
        self.assertEqual(data,b'hello')
        credentials=[struct.unpack('3i',v) for level,kind,v in ancillary if level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS]
        self.assertEqual(credentials,[(os.getpid(),os.geteuid(),os.getegid())])


if __name__ == '__main__': unittest.main()
