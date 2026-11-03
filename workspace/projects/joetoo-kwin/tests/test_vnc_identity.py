"""Isolated XCB observer prototype. Never connects to a graphical session."""
import ctypes as C
import importlib.util
from pathlib import Path
import struct
import unittest
from unittest.mock import MagicMock

spec = importlib.util.spec_from_file_location('vnc_identity', Path(__file__).resolve().parents[1]/'libexec/joetoo_kwin_vnc_identity.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class IdentityPrototypeTests(unittest.TestCase):
    def event(self, xid=123, atom=9, enabled=1):
        return struct.pack('=BBHIII16x', 33 | 128, 32, 7, xid, atom, enabled)

    def test_client_message_extracts_desktop_xid(self):
        self.assertEqual(m.decode_event(self.event(), 9), ('desktop', 123))
        self.assertIsNone(m.decode_event(self.event(atom=8), 9))
        self.assertIsNone(m.decode_event(self.event(enabled=0), 9))
        self.assertIsNone(m.decode_event(bytes([33])+self.event()[1:], 9))
        destroyed = struct.pack('=BBHII20x',17,0,2,1,123)
        self.assertEqual(m.decode_event(destroyed,9), ('destroyed',123))

    def test_observer_receives_event_and_uses_nonexclusive_mask(self):
        observer = object.__new__(m.NativeObserver)
        observer.connection = 99; observer.atom = 9
        observer.lib = MagicMock(); observer.libc = MagicMock()
        observer.lib.xcb_connection_has_error.return_value = 0
        observer.lib.xcb_request_check.return_value = None
        masks=[]
        observer.lib.xcb_change_window_attributes_checked.side_effect = lambda c,w,b,p: masks.append(C.cast(p,C.POINTER(C.c_uint32)).contents.value)
        observer.select(1,m.SUBSTRUCTURE_NOTIFY)
        self.assertEqual(masks,[1<<19]); self.assertFalse(masks[0] & (1<<20))
        # A simulated server delivers the real 32-byte X11 ClientMessage layout.
        packet=C.create_string_buffer(self.event())
        observer.lib.xcb_poll_for_event.side_effect=[C.addressof(packet),None]
        self.assertEqual(observer.drain(10),[('desktop',123)])
        observer.close(); observer.close()
        observer.lib.xcb_disconnect.assert_called_once_with(99)

    def test_errors_and_event_flood_fail_closed(self):
        observer=object.__new__(m.NativeObserver); observer.connection=99;observer.atom=9
        observer.lib=MagicMock();observer.libc=MagicMock()
        observer.lib.xcb_connection_has_error.return_value=1
        with self.assertRaises(RuntimeError):observer.drain(2)
        observer.lib.xcb_connection_has_error.return_value=0
        packet=C.create_string_buffer(self.event())
        observer.lib.xcb_poll_for_event.return_value=C.addressof(packet)
        with self.assertRaises(RuntimeError):observer.drain(2)

    def test_real_libxcb_receives_isolated_server_event(self):
        """Exercise the actual native ABI over socketpair, not a live X server.

        The tiny in-process peer implements setup/atom/select/sync only. It
        records event selection and sends a real X11 wire ClientMessage. No
        DISPLAY connection, KWin process, GUI, TCP or credentials are used.
        """
        import socket
        import os
        import threading
        from unittest.mock import patch
        client,server=socket.socketpair()
        server.settimeout(2)
        errors=[];masks=[]
        def exact(count):
            result=b''
            while len(result)<count:
                part=server.recv(count-len(result))
                if not part: raise EOFError
                result+=part
            return result
        def peer():
            try:
                hello=exact(12)
                order='<' if hello[0]==ord('l') else '>'
                auth_name,auth_data=struct.unpack_from(order+'HH',hello,6)
                exact((auth_name+3)//4*4+(auth_data+3)//4*4)
                setup=struct.pack(order+'BBHHHIIIIHHBBBBBBBB4x',1,0,11,0,18,
                    1,0x200000,0x1fffff,0,0,65535,1,0,0,0,32,32,8,255)
                screen=struct.pack(order+'IIIIIHHHHHHIBBBB',1,2,0xffffff,0,0,
                    1920,1080,500,300,1,1,3,0,0,24,0)
                os.write(server.fileno(),setup+screen)
                sequence=0;sent=False
                while True:
                    header=exact(4);opcode=header[0];size=struct.unpack_from(order+'H',header,2)[0]*4
                    data=header+exact(size-4);sequence+=1
                    if opcode==16:
                        os.write(server.fileno(),struct.pack(order+'BBHII20x',1,0,sequence,0,9))
                    elif opcode==2:
                        masks.append(struct.unpack_from(order+'I',data,12)[0])
                    elif opcode==43:
                        os.write(server.fileno(),struct.pack(order+'BBHII20x',1,0,sequence,0,1))
                        if not sent:
                            os.write(server.fileno(),self.event());sent=True
                    else: raise AssertionError('Unexpected X11 request '+str(opcode))
            except EOFError: pass
            except Exception as exc:
                import traceback
                errors.append(traceback.format_exc())
            finally: server.close()
        thread=threading.Thread(target=peer,daemon=True);thread.start()
        original=m.C.CDLL
        native=original(m.ctypes_library())
        native.xcb_connect_to_fd.argtypes=[C.c_int,C.c_void_p]
        native.xcb_connect_to_fd.restype=C.c_void_p
        def connect(display,screen):
            C.cast(screen,C.POINTER(C.c_int)).contents.value=0
            return native.xcb_connect_to_fd(client.detach(),None)
        class Proxy:
            xcb_connect=staticmethod(connect)
            def __getattr__(self,name):return getattr(native,name)
        observer=None
        try:
            with patch.dict(m.os.environ,{'DISPLAY':':99'}), \
                 patch.object(m.C,'CDLL',side_effect=lambda name: original(None) if name is None else Proxy()):
                try: observer=m.NativeObserver()
                except RuntimeError as exc: raise AssertionError(str(errors)) from exc
            self.assertEqual(observer.drain(16),[('desktop',123)])
            self.assertEqual(masks,[m.SUBSTRUCTURE_NOTIFY])
            self.assertFalse(masks[0]&(1<<20))
        finally:
            if observer: observer.close()
            client.close();thread.join(timeout=3)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,[])

    def test_broker_pipe_wrapper_drains_and_closes_only_its_observer(self):
        from unittest.mock import patch
        observer=object.__new__(m.DesktopObserver)
        observer.process=MagicMock();observer.process.poll.return_value=None
        observer.buffer=b'';observer.queue=[];observer.ready=False;observer.limit=16;observer.cleanup=.1
        with patch.object(m.os,'read',return_value=b'{"ready":true}\n["desktop",123]\n'):
            self.assertEqual(observer.drain(16),[('desktop',123)])
        self.assertTrue(observer.ready)
        process=observer.process;observer.close();observer.close()
        process.terminate.assert_called_once();process.stdout.close.assert_called_once()

    def test_broker_observer_startup_timeout_cleans_up_without_connecting_display(self):
        from unittest.mock import patch
        process=MagicMock();process.poll.return_value=None
        bounds=dict(vnc_identity_event_limit=16,vnc_cleanup_timeout_ms=100,
                    vnc_identity_start_timeout_ms=100,vnc_supervisor_poll_interval_ms=10)
        with patch.dict(m.os.environ,{'DISPLAY':':99'}), \
             patch.object(m.subprocess,'Popen',return_value=process), \
             patch.object(m.os,'set_blocking'),patch.object(m.time,'monotonic',side_effect=[0,1]):
            with self.assertRaises(RuntimeError):m.DesktopObserver(bounds)
        process.terminate.assert_called_once();process.stdout.close.assert_called_once()


    def test_missing_broker_display_rejected_before_observer_spawn(self):
        from unittest.mock import patch
        with patch.dict(m.os.environ,{'DISPLAY':''}),patch.object(m.subprocess,'Popen') as spawn:
            with self.assertRaisesRegex(RuntimeError,'Broker requires a local DISPLAY'):
                m.DesktopObserver({})
        spawn.assert_not_called()
