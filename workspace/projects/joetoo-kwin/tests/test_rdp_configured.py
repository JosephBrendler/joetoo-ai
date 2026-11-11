# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Configured SDL tests: synthetic bus/KWin, real private files/pidfds/disposable workers.

No SDL process, native GUI, network, service operation or deployed user profile.
Existing broker/registry registration/placement suites cover the shared core.
"""
import copy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'libexec'))
import joetoo_kwin_rdp_launch as rdp
from test_step1_3a import WINDOW_ID
import test_step1_5c_launch as launches


def job(backend='auto'):
    return dict(target='rdp://joe@[::1]:3390', settings=dict(rdp_windowing_backend=backend),
        bounds={}, mechanical=dict(call_timeout_ms=3000, placement_timeout_ms=1000),
        desktop=1, slot=1, x=20, y=30, width=800, height=628)


def resolved_job():
    return dict(rdp.configured_job(job()), broker_owner=':1.broker', source='source', resolved_backend='wayland')


def clean_receipt(j):
    return dict(request_id='a'*32,broker_owner=j['broker_owner'],source=j['source'],
        eligible=True,broker_terminal=True,child_reaped=True,resources_released=True,
        terminal=dict(protocol=1,request_id='a'*32,state='timeout',reason='expired',
                      placement='not_requested',remote_session='unverified'))


def completed(job, nonce, pid, start):
    reg = dict(state='registered', request_id='a' * 32, managed_id='win-001', window_uuid=WINDOW_ID)
    place = dict(placement='succeeded', remote_session='unverified', request_id='b' * 32,
                 managed_id='win-001', window_uuid=WINDOW_ID)
    return dict(state='completed', nonce=nonce, worker_pid=pid, worker_start=start,
                remote_session='unverified', broker_owner=job['broker_owner'], registration=reg, placement=place)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.mode = 'Wayland'; self.owner = ':1.kwin'; self.change = False
        self.uid = os.geteuid(); self.processfd = True; self.identity_pid = os.getpid()
        self.calls = []
        outer = self
        class FD:
            def __init__(self): self.fd = os.pidfd_open(os.getpid())
            def take(self): fd, self.fd = self.fd, None; return fd
        class Daemon:
            def GetNameOwner(self, name, **kw):
                return outer.owner if name == 'org.kde.KWin' else ':1.broker'
            def GetConnectionCredentials(self, name, **kw):
                value = dict(ProcessID=outer.identity_pid, UnixUserID=outer.uid)
                if outer.processfd: value['ProcessFD'] = FD()
                return value
        class KWin:
            def supportInformation(self, **kw):
                info = 'Operation Mode: ' + outer.mode + '\n'
                if outer.change: outer.owner = ':1.replacement'
                return info
        class Broker:
            def Introspect(self, **kw):
                methods = dict(BeginSdlRegistration='s', BindSdlRegistration='sih',
                    PollSdlRegistration='s', CancelSdlRegistration='s', SubmitSdlPlacement='s',
                    PollSdlPlacement='s', CancelSdlPlacement='s', TakeSdlPlacement='s')
                return '<node><interface name="org.joetoo.KWinBridge">' + ''.join(
                    '<method name="' + name + '">' + ''.join('<arg type="' + ch + '" direction="in"/>' for ch in sig) +
                    '<arg type="s" direction="out"/></method>' for name, sig in methods.items()) + '</interface></node>'
            def RegistryStatus(self, **kw):
                return json.dumps(dict(observation=dict(synchronized=True, source='source'),
                    request_counts=dict(pending=0, running=0), presence_counts=dict(uncertain=0),
                    placement_transaction=dict(id=None, state='IDLE'), initial_layout_active=False,
                    initial_layout_protocol=1, viewer_cleanup_uncertain=False))
            def ListManaged(self, **kw): return '{"windows":[]}'
        self.daemon, self.kwin, self.broker = Daemon(), KWin(), Broker()
        self.bus = SimpleNamespace(get_object=lambda name, path, **kw:
            self.daemon if name == 'org.freedesktop.DBus' else self.kwin if path == '/KWin' else self.broker,
            get_is_connected=lambda: True)
        self.env = patch.dict(os.environ, DISPLAY=':1', WAYLAND_DISPLAY='wayland-test', XDG_SESSION_TYPE='tty')
        self.env.start(); self.addCleanup(self.env.stop)
        self.exe = patch.object(rdp, 'executable_identity', return_value=(1, 2))
        self.exe.start(); self.addCleanup(self.exe.stop)

    def test_auto_uses_authenticated_compositor_not_tty_or_display_environment(self):
        result = rdp.configured_preflight(job(), self.bus, lambda o, i: o)
        self.assertEqual(result['resolved_backend'], 'wayland')
        self.mode = 'X11'
        result = rdp.configured_preflight(job(), self.bus, lambda o, i: o)
        self.assertEqual(result['resolved_backend'], 'x11')

    def test_readiness_defaults_overrides_and_independent_mechanical_budgets(self):
        import joetoo_kwin_vnc_target as vnc
        self.assertEqual(rdp.DEFAULTS['rdp_registration_timeout_ms'],300000)
        self.assertEqual(vnc.DEFAULTS['vnc_viewer_ready_timeout_ms'],300000)
        for value in (1000,120000,600000,3600000):
            self.assertEqual(rdp.settings(dict(rdp_registration_timeout_ms=value))['rdp_registration_timeout_ms'],value)
            self.assertEqual(vnc.settings(dict(vnc_viewer_ready_timeout_ms=value))['vnc_viewer_ready_timeout_ms'],value)
        for value in (0,999,3600001,True,'unlimited'):
            with self.assertRaises(ValueError):rdp.settings(dict(rdp_registration_timeout_ms=value))
            with self.assertRaises(ValueError):vnc.settings(dict(vnc_viewer_ready_timeout_ms=value))
        self.assertEqual(vnc.settings({})['vnc_placement_timeout_ms'],15000)
        self.assertEqual(vnc.settings({})['vnc_ssh_start_timeout_ms'],10000)
        self.assertEqual(rdp.settings({})['rdp_registration_poll_ms'],100)

    def test_native_x11_requested_on_wayland_is_rejected_before_spawn(self):
        with self.assertRaisesRegex(rdp.ConfiguredError, 'not_xwayland'):
            rdp.configured_preflight(job('x11'), self.bus, lambda o, i: o)

    def test_unknown_ambiguous_or_replaced_compositor_is_not_auto_guessed(self):
        for mode in ('Unknown', 'Wayland\nOperation Mode: X11', 'Wayland' + 'x' * 65536):
            self.mode = mode
            with self.assertRaises(rdp.ConfiguredError): rdp.configured_preflight(job(), self.bus, lambda o, i: o)
        self.mode = 'Wayland'; self.change = True
        with self.assertRaises(rdp.ConfiguredError): rdp.configured_preflight(job(), self.bus, lambda o, i: o)

    def test_processfd_uid_pid_and_executable_prerequisites_fail_closed(self):
        for field, value in (('processfd', False), ('uid', os.geteuid() + 1), ('identity_pid', os.getpid() + 100000)):
            original = getattr(self, field)
            setattr(self, field, value)
            with self.assertRaises(Exception): rdp.configured_preflight(job(), self.bus, lambda o, i: o)
            setattr(self, field, original)
        with patch.object(rdp, 'executable_identity', side_effect=PermissionError):
            with self.assertRaises(PermissionError): rdp.configured_preflight(job(), self.bus, lambda o, i: o)

    def test_x11_software_and_auto_environment_policy_preserves_parent(self):
        self.mode = 'X11'
        parent = dict(os.environ)
        for renderer in ('auto', 'software'):
            value = job('x11'); value['bounds'] = dict(rdp_x11_renderer=renderer)
            checked = rdp.configured_preflight(value, self.bus, lambda o, i: o)
            environment = rdp.development_environment(os.environ, rdp.X11_PROFILE, checked['bounds'])
            self.assertEqual(environment['SDL_VIDEO_DRIVER'], 'x11')
            if renderer == 'software': self.assertEqual(environment['SDL_FRAMEBUFFER_ACCELERATION'], '0')
            else: self.assertNotIn('SDL_RENDER_DRIVER', environment)
        self.assertEqual(dict(os.environ), parent)

    def test_missing_placement_signature_busy_and_historical_slot_are_rejected(self):
        with patch.object(self.broker, 'Introspect', return_value='<node/>'):
            with self.assertRaises(RuntimeError): rdp.configured_preflight(job(), self.bus, lambda o, i: o)
        original = self.broker.RegistryStatus
        value = json.loads(original()); value['placement_transaction']['state'] = 'VERIFYING'
        with patch.object(self.broker, 'RegistryStatus', return_value=json.dumps(value)):
            with self.assertRaises(rdp.ConfiguredError): rdp.configured_preflight(job(), self.bus, lambda o, i: o)
        with patch.object(self.broker, 'ListManaged', return_value=json.dumps(dict(windows=[
                dict(intended=dict(desktop=1, slot=1), presence='missing')]))):
            with self.assertRaisesRegex(rdp.ConfiguredError, 'reserved'):
                rdp.configured_preflight(job(), self.bus, lambda o, i: o)

    def test_configured_sizes_ports_and_existing_defaults_are_independent(self):
        data = rdp.configured_job(job())
        self.assertEqual(data['bounds']['rdp_registration_timeout_ms'], 300000)
        args = rdp.configured_argv('::1', 3390, 'joe', 'joetoo-rdp-' + 'a' * 64,
            dict(rdp_remote_width=1920, rdp_remote_height=1080, RDP_SMART_SIZING=False))
        self.assertIn('/v:[::1]:3390', args)
        self.assertIn('/size:1920x1080', args)
        self.assertIn('/smart-sizing:off', args)
        self.assertFalse(any('/cert:' in arg or '/p:' in arg for arg in args))
        self.assertIn('/smart-sizing:800x600', rdp.development_argv('host', 3389, 'joe', 'joetoo-rdp-' + 'a' * 64))
        with self.assertRaises(rdp.ConfiguredError): rdp.configured_job(dict(job(), target='rdp://joe:secret@host'))


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name); self.folder.chmod(0o700)
        self.job, self.nonce = resolved_job(), 'c' * 32
        rdp._private_json(self.folder / 'job', dict(job=self.job, nonce=self.nonce,
            frontend_pid=os.getpid(), frontend_start=rdp._proc_info(os.getpid(), include_executable=False)['start']))
        self.bus = SimpleNamespace(close=lambda: None)
        self.calls = []
        self.outcome = 'success'
        self.signals = {}
        patcher = patch.object(rdp.signal, 'signal', side_effect=lambda sig, callback: self.signals.setdefault(sig, callback))
        patcher.start(); self.addCleanup(patcher.stop)

    def run_worker(self):
        def registration(bus, interface, fd, adapter, host, port, user, desktop, slot, bounds, **kw):
            self.calls.append('registration')
            self.assertEqual((host, port, user), ('::1', 3390, 'joe'))
            self.assertEqual((desktop, slot), (1, 1))
            self.assertIn('/size:1024x768', kw['argv_builder'](host, port, user, 'joetoo-rdp-' + 'a' * 64))
            if self.outcome == 'registration_failure': raise ValueError('private')
            if self.outcome == 'parent_lost':
                dead = patch.object(rdp, '_exited', return_value=True)
                dead.start(); self.addCleanup(dead.stop)
                self.assertTrue(kw['cancelled']())
                raise RuntimeError('Operator cancellation')
            if self.outcome == 'clean_timeout':
                kw['on_cleanup'](clean_receipt(self.job))
                kw['emit'](json.dumps(dict(state='timeout',request_id='a'*32,reason='expired')))
                return 1
            if self.outcome in ('timeout', 'ambiguous'):
                kw['emit'](json.dumps(dict(state=self.outcome, request_id='a' * 32, reason=self.outcome)))
                return 1
            reg = completed(self.job, self.nonce, os.getpid(), 1)['registration']
            kw['on_registered'](reg, kw['cancelled'])
            # Frontend exit/cancel after positive registration cannot kill the viewer.
            self.assertFalse(kw['cancelled']())
            if self.outcome == 'degraded':
                kw['emit'](json.dumps(dict(state='unresolved', phase='supervision',
                    supervision='degraded', registration='registered', reason='private_log_integrity_or_budget',
                    request_id=reg['request_id'], managed_id=reg['managed_id'], window_uuid=reg['window_uuid'],
                    remote_session='unverified')))
                return 1
            return 0
        def place(*args, **kw):
            self.calls.append('placement')
            self.assertEqual(kw['expected_window_uuid'], WINDOW_ID)
            self.assertEqual(args[4], 1)
            if self.outcome in ('placement_loss', 'front_cancel'):
                if self.outcome == 'front_cancel':
                    rdp._private_json(self.folder / 'cancel', dict(nonce=self.nonce))
                raise RuntimeError('private')
            if self.outcome == 'wrong_cancel':
                rdp._private_json(self.folder / 'cancel', dict(nonce='d' * 32))
                self.assertFalse(kw['cancelled']())
            value = completed(self.job, self.nonce, 1, 1)['placement']
            kw['emit'](json.dumps(value)); return 0
        write = rdp._private_json
        def acknowledge(path, value):
            write(path, value)
            if path.name == 'status' and value.get('state') == 'completed':
                write(self.folder / 'ack', dict(nonce=self.nonce))
        with patch.object(rdp, '_private_json', acknowledge), \
             patch.object(rdp, 'configured_preflight', return_value=self.job), \
             patch.object(rdp, 'launch_registration', registration), patch.object(rdp, 'release_placement', place):
            rdp.configured_worker(self.folder, lambda: self.bus, lambda o, i: o, None)
        return rdp._read_private_json(self.folder / 'status')

    def test_one_registration_one_placement_and_bound_terminal_result(self):
        result = self.run_worker()
        self.assertEqual(self.calls, ['registration', 'placement'])
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(result['nonce'], self.nonce)
        self.assertEqual(result['registration']['window_uuid'], result['placement']['window_uuid'])
        self.assertEqual(result['remote_session'], 'unverified')

    def test_degraded_supervision_record_does_not_relabel_verified_placement(self):
        self.outcome = 'degraded'
        result = self.run_worker()
        self.assertEqual(result['state'], 'completed')
        observation = rdp._read_private_json(self.folder / 'supervision')
        self.assertEqual(observation['supervision'], 'degraded')
        self.assertEqual(observation['state'], 'unresolved')
        self.assertEqual(observation['nonce'], self.nonce)
        self.assertEqual(observation['window_uuid'], result['registration']['window_uuid'])
        self.assertEqual(observation['worker_pid'], os.getpid())

    def test_placement_failure_or_broker_loss_preserves_registered_viewer(self):
        self.outcome = 'placement_loss'
        result = self.run_worker()
        self.assertEqual(result['state'], 'unresolved')
        self.assertEqual(result['phase'], 'placement')
        self.assertEqual(self.calls, ['registration', 'placement'])
        self.assertNotIn('private', json.dumps(result))

    def test_cancel_after_registration_preserves_viewer_and_reports_cancelled(self):
        self.outcome = 'front_cancel'
        result = self.run_worker()
        self.assertEqual(result['state'], 'cancelled')
        self.assertEqual(result['phase'], 'placement')

    def test_known_cleanup_is_bound_to_original_worker_mission(self):
        self.outcome='clean_timeout'
        result=self.run_worker()
        self.assertTrue(rdp.clean_registration_receipt(result,self.job))
        for field, value in (('source','other'),('broker_owner',':1.foreign'),('child_reaped',False),
                             ('broker_terminal',False),('resources_released',False),('request_id','b'*32)):
            forged=copy.deepcopy(result);forged['cleanup'][field]=value
            self.assertFalse(rdp.clean_registration_receipt(forged,self.job),field)
        forged=copy.deepcopy(result);forged['cleanup']['terminal']['managed_id']='win-001'
        self.assertFalse(rdp.clean_registration_receipt(forged,self.job))

    def test_registration_timeout_and_ambiguity_remain_distinct(self):
        for outcome in ('timeout', 'ambiguous'):
            self.outcome = outcome
            result = self.run_worker()
            self.assertEqual(result['state'], 'unresolved')
            self.assertEqual(result['registration']['state'], outcome)
            self.assertFalse(result['cleanup_confirmed'])

    def test_frontend_loss_before_registration_cancels_only_pending_mission(self):
        self.outcome = 'parent_lost'
        result = self.run_worker()
        self.assertEqual(result['state'], 'unresolved')
        self.assertEqual(self.calls, ['registration'])
        self.assertFalse(result['cleanup_confirmed'])

    def test_registration_failure_is_not_a_clean_continuation_claim(self):
        self.outcome = 'registration_failure'
        result = self.run_worker()
        self.assertEqual(result['state'], 'unresolved')
        self.assertFalse(result['cleanup_confirmed'])
        self.assertEqual(self.calls, ['registration'])

    def test_foreign_cancel_nonce_cannot_cancel_this_mission(self):
        self.outcome = 'wrong_cancel'
        self.assertEqual(self.run_worker()['state'], 'completed')

    def test_publication_failure_after_registration_cannot_stop_enrolled_supervision(self):
        write = rdp._private_json
        def failing(path, value):
            if path.name == 'handoff': raise OSError('private disk failure')
            return write(path, value)
        with patch.object(rdp, '_private_json', failing):
            result = self.run_worker()
        self.assertEqual(result['state'], 'unresolved')
        self.assertEqual(result['phase'], 'handoff')
        self.assertEqual(self.calls, ['registration', 'placement'])

    def test_symlink_or_nonprivate_control_data_is_rejected(self):
        (self.folder / 'bad').symlink_to(self.folder / 'job')
        with self.assertRaises(OSError): rdp._read_private_json(self.folder / 'bad')
        (self.folder / 'job').chmod(0o644)
        with self.assertRaises(rdp.ConfiguredError): rdp._read_private_json(self.folder / 'job')


class FrontendTests(unittest.TestCase):
    """Real disposable worker IPC; this synthetic producer is NOT the SDL worker."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.runtime = Path(self.tmp.name); self.runtime.chmod(0o700)
        env = patch.dict(os.environ, XDG_RUNTIME_DIR=str(self.runtime)); env.start(); self.addCleanup(env.stop)
        self.children = []
        self.addCleanup(self.cleanup)
        self.mode = 'success'
        self.helper = self.runtime / 'fixture.py'
        self.helper.write_text('''import json,os,sys,time
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import joetoo_kwin_rdp_launch as r
p=Path(sys.argv[2]); e=r._read_private_json(p/'job')
try: os.fstat(9); inherited=True
except OSError: inherited=False
(p/'fd9').write_text(str(inherited))
reg=dict(state='registered',request_id='a'*32,managed_id='win-001',window_uuid=sys.argv[3])
place=dict(placement='succeeded',remote_session='unverified',request_id='b'*32,managed_id='win-001',window_uuid=sys.argv[3])
value=dict(state='completed',nonce=e['nonce'],worker_pid=os.getpid(),worker_start=r._proc_info(os.getpid(),include_executable=False)['start'],broker_owner=e['job']['broker_owner'],registration=reg,placement=place,remote_session='unverified')
mode=sys.argv[4]
if mode.startswith('clean'):
 value.update(state='timeout',phase='registration',cleanup_confirmed=True,cleanup=dict(
  request_id='a'*32,broker_owner=e['job']['broker_owner'],source=e['job']['source'],eligible=True,
  broker_terminal=True,child_reaped=True,resources_released=True,
  terminal=dict(protocol=1,request_id='a'*32,state='timeout',reason='expired',placement='not_requested',remote_session='unverified')))
 value.pop('registration');value.pop('placement')
 if mode=='clean_forged': value['cleanup']['source']='foreign'
 r._private_json(p/'status',value)
 if mode!='clean_unreaped':
  r._private_json(p/'worker_exited',dict(nonce=e['nonce'],worker_pid=os.getpid(),worker_start=value['worker_start']))
  sys.exit(0)
if mode=='foreign': value['nonce']='f'*32
if mode=='wrong_uuid': place['window_uuid']='ffffffff-ffff-ffff-ffff-ffffffffffff'
if mode=='exit': sys.exit(1)
if mode!='silent': r._private_json(p/'status',value)
if mode in ('success','bad_receipt','no_receipt'):
 while not (p/'ack').exists() and not (p/'cancel').exists(): time.sleep(.005)
 if (p/'ack').exists() and mode!='no_receipt':
  r._private_json(p/'handoff',dict(nonce=('d'*32 if mode=='bad_receipt' else e['nonce']),worker_pid=os.getpid(),worker_start=value['worker_start'],acknowledged=True))
sys.stdin.read()
''')

    def cleanup(self):
        for child in self.children:
            if not child.stdin.closed: child.stdin.close()
            child.wait(timeout=5)

    def spawn(self, argv, **kw):
        self.assertTrue(kw['close_fds']); self.assertTrue(kw['start_new_session'])
        self.assertEqual(kw['stdout'], subprocess.DEVNULL)
        child = subprocess.Popen([sys.executable, str(self.helper), str(ROOT / 'libexec'), argv[-1], WINDOW_ID, self.mode],
            stdin=subprocess.PIPE, stdout=kw['stdout'], stderr=kw['stderr'], start_new_session=True, close_fds=True)
        self.children.append(child)
        return child

    def test_frontend_returns_while_worker_lives_and_records_ack(self):
        result = rdp.configured_frontend(resolved_job(), spawn=self.spawn)
        self.assertEqual(result['state'], 'completed')
        self.assertIsNone(self.children[-1].poll())
        folder, = self.runtime.glob('joetoo-rdp-*')
        self.assertEqual(rdp._read_private_json(folder / 'ack')['nonce'], result['nonce'])
        self.assertEqual((folder / 'fd9').read_text(), 'False')

    def test_clean_failure_waits_for_real_worker_reaping_and_session_verification(self):
        self.mode='clean'
        result=rdp.configured_frontend(resolved_job(),spawn=self.spawn,verify_cleanup=lambda c:True)
        self.assertTrue(result['continuation_eligible'])
        self.assertIsNotNone(self.children[-1].returncode)
        self.assertEqual(result['state'],'timeout')

    def test_forged_cleanup_or_unreaped_worker_never_authorizes_continuation(self):
        for mode in ('clean_forged','clean_unreaped'):
            with self.subTest(mode=mode):
                self.mode=mode
                result=rdp.configured_frontend(resolved_job(),spawn=self.spawn,verify_cleanup=lambda c:True)
                self.assertEqual(result['state'],'unresolved')

    def test_changed_session_after_worker_cleanup_stops(self):
        self.mode='clean'
        result=rdp.configured_frontend(resolved_job(),spawn=self.spawn,verify_cleanup=lambda c:False)
        self.assertEqual(result['state'],'unresolved')

    def test_worker_cannot_retain_configured_fd9_lock(self):
        import fcntl
        lock = self.runtime / 'invocation.lock'
        fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            saved = os.dup(9)
        except OSError:
            saved = None
        try:
            os.dup2(fd, 9, inheritable=True)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = rdp.configured_frontend(resolved_job(), spawn=self.spawn)
            self.assertEqual(result['state'], 'completed')
            self.assertIsNone(self.children[-1].poll())
            os.close(9); os.close(fd); fd = None
            fresh = os.open(lock, os.O_RDWR)
            try: fcntl.flock(fresh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finally: os.close(fresh)
        finally:
            if fd is not None: os.close(fd)
            if saved is not None:
                os.dup2(saved, 9); os.close(saved)
            else:
                try: os.close(9)
                except OSError: pass

    def test_nonce_and_terminal_uuid_forgery_never_become_success(self):
        for mode in ('foreign', 'wrong_uuid', 'exit', 'bad_receipt'):
            self.mode = mode
            self.assertEqual(rdp.configured_frontend(resolved_job(), spawn=self.spawn)['state'], 'unresolved')

    def test_frontend_signal_requests_bound_cancellation_without_killing_worker(self):
        self.mode = 'silent'
        now = [0.]
        sent = [False]
        def pause(seconds):
            if not sent[0]:
                signal.raise_signal(signal.SIGINT); sent[0] = True
            now[0] += 1.; time.sleep(.005)
        result = rdp.configured_frontend(resolved_job(), spawn=self.spawn, clock=lambda: now[0], sleep=pause)
        self.assertEqual(result['state'], 'unresolved')
        folder, = self.runtime.glob('joetoo-rdp-*')
        self.assertEqual(rdp._read_private_json(folder / 'cancel')['nonce'], rdp._read_private_json(folder / 'job')['nonce'])
        self.assertIsNone(self.children[-1].poll())

    def test_lost_receipt_is_terminal_even_when_a_late_receipt_arrives(self):
        self.mode = 'no_receipt'
        result = rdp.configured_frontend(resolved_job(), spawn=self.spawn)
        self.assertEqual(result['state'], 'unresolved')
        self.assertEqual(result['reason'], 'worker_receipt_unavailable')
        folder, = self.runtime.glob('joetoo-rdp-*')
        rdp._private_json(folder / 'handoff', dict(nonce=rdp._read_private_json(folder / 'job')['nonce'], acknowledged=True))
        self.assertEqual(result['state'], 'unresolved')

    def test_deadline_sends_request_bound_cancel_and_never_claims_cleanup(self):
        self.mode = 'silent'; now = [0.]
        def sleep(seconds): now[0] += 200.; time.sleep(.01)
        result = rdp.configured_frontend(resolved_job(), spawn=self.spawn, clock=lambda: now[0], sleep=sleep)
        self.assertEqual(result['state'], 'unresolved')
        folder, = self.runtime.glob('joetoo-rdp-*')
        self.assertEqual(rdp._read_private_json(folder / 'cancel')['nonce'], rdp._read_private_json(folder / 'job')['nonce'])


class PlanTests(launches.ConfiguredLaunchTests):
    setUpBase = launches.ConfiguredLaunchTests.setUp
    execute = launches.ConfiguredLaunchTests.execute

    def setUp(self):
        self.setUpBase()
        self.trace = self.folder / 'cohorts'
        self.env['COHORT_TRACE'] = str(self.trace)
        self.reservations = self.folder / 'rdp-reservations'
        self.preflights = self.folder / 'rdp-preflights'
        self.health = self.folder / 'broker-health'
        self.env.update(RDP_RESERVATIONS=str(self.reservations),
                        RDP_PREFLIGHT_TRACE=str(self.preflights), BROKER_HEALTH=str(self.health), DISPLAY=':1')
        for name in ('joetoo_kwin_rdp_target.py', 'joetoo_kwin_vnc_target.py'):
            import shutil
            shutil.copyfile(ROOT / 'libexec' / name, self.folder / 'libexec' / name)
        import shutil
        import textwrap
        shutil.copyfile(ROOT / 'libexec/joetoo_kwin_rdp_launch.py', self.folder / 'libexec/rdp_contract.py')
        helper = self.folder / 'libexec/joetoo_kwin_rdp_launch.py'
        # Actual production preflight, synthetic transport/executable discovery.
        # A successful synthetic launch persists its reservation for later calls.
        cli = '''import json,os,sys
from pathlib import Path
import rdp_contract as rdp
def managed():
 windows=json.loads(os.environ['MANAGED'])['windows']
 p=Path(os.environ['RDP_RESERVATIONS'])
 return windows+(json.loads(p.read_text()) if p.exists() else [])
def health():
 p=Path(os.environ['BROKER_HEALTH'])
 value=json.loads(p.read_text() if p.exists() else os.environ['BROKER_STATE'])
 value['observation'].setdefault('source','source')
 value['placement_transaction'].setdefault('id',None)
 value.setdefault('viewer_cleanup_uncertain',False)
 return value
class FD:
 def take(self): return os.pidfd_open(os.getpid())
class Daemon:
 def GetNameOwner(self,name,**kw): return ':1.kwin' if name=='org.kde.KWin' else ':1.broker'
 def GetConnectionCredentials(self,name,**kw):
  return dict(ProcessFD=FD(),ProcessID=os.getpid(),UnixUserID=os.geteuid())
class KWin:
 def supportInformation(self,**kw): return 'Operation Mode: X11\\n'
class Broker:
 def Introspect(self,**kw):
  methods=dict(BeginSdlRegistration='s',BindSdlRegistration='sih',PollSdlRegistration='s',CancelSdlRegistration='s',SubmitSdlPlacement='s',PollSdlPlacement='s',CancelSdlPlacement='s',TakeSdlPlacement='s')
  return '<node><interface name="org.joetoo.KWinBridge">'+''.join('<method name="'+n+'">'+''.join('<arg type="'+t+'" direction="in"/>' for t in sig)+'<arg type="s" direction="out"/></method>' for n,sig in methods.items())+'</interface></node>'
 def RegistryStatus(self,**kw): return json.dumps(health())
 def ListManaged(self,**kw): return json.dumps(dict(windows=managed()))
class Bus:
 def get_object(self,name,path,**kw):
  return Daemon() if name=='org.freedesktop.DBus' else KWin() if path=='/KWin' else Broker()
 def get_is_connected(self): return True
rdp.executable_identity=lambda:(1,2)  # Never inspect or launch the native SDL executable.
with os.fdopen(os.dup(3)) as f: j=json.load(f)
if '--preflight' in sys.argv:
 with open(os.environ['RDP_PREFLIGHT_TRACE'],'a') as f: f.write(json.dumps(dict(slot=j['slot'],desktop=j['desktop'],managed=managed()))+'\\n')
 if os.environ.get('RDP_PREFLIGHT_FAIL') or (managed() and os.environ.get('RDP_LATE_PREREQUISITE_FAIL')): sys.exit(2)
 try: result=rdp.configured_preflight(j,Bus(),lambda o,i:o)
 except Exception as error: print(rdp._failure_code(error),file=sys.stderr);sys.exit(2)
 print(json.dumps(result)); sys.exit(0)
n=j['desktop']*100+j['slot']; rid=f'{n:032x}'; pid=f'{n+1000:032x}'; uid=f'{n:08x}-0000-0000-0000-000000000000'
with open(os.environ['TRACE'],'a') as f: f.write(f'rdp:{j["desktop"]}:{j["slot"]}\\n')
result=dict(state='completed',remote_session='unverified',registration=dict(state='registered',request_id=rid,managed_id='win-'+str(n),window_uuid=uid),placement=dict(placement='succeeded',request_id=pid,managed_id='win-'+str(n),window_uuid=uid))
if os.environ.get('RDP_CLEAN_FAIL_SLOT')==str(j['slot']):
 result=dict(state='timeout',phase='registration',cleanup_confirmed=True,continuation_eligible=True,remote_session='unverified',cleanup=dict(request_id=rid))
elif os.environ.get('RDP_FAILED'): result['state']='failed'
else:
 p=Path(os.environ['RDP_RESERVATIONS']); windows=json.loads(p.read_text()) if p.exists() else []
 windows.append(dict(managed_id='win-'+str(n),request_id=rid,window_uuid=uid,presence='present',placement='succeeded',intended=dict(desktop=j['desktop'],slot=j['slot'])))
 if os.environ.get('AFTER_RDP_CONFLICT'):
  windows.append(dict(managed_id='win-foreign',presence='missing',intended=dict(desktop=j['desktop'],slot=j['slot']+1)))
 p.write_text(json.dumps(windows))
 if os.environ.get('AFTER_RDP_HEALTH'): Path(os.environ['BROKER_HEALTH']).write_text(os.environ['AFTER_RDP_HEALTH'])
print(json.dumps(result)); sys.exit(2 if result['state']!='completed' else 0)
'''
        helper.write_text('from rdp_contract import settings, DEFAULTS, X11_DEFAULTS, X11_PROFILE\n' +
                          "if __name__ == '__main__':\n" + textwrap.indent(cli, ' '))
        self.client.write_text(self.client.read_text().replace('qdbus6() {', 'baseline_qdbus6() {', 1).replace(
            '#-----[ main script ]', r'''
qdbus6() {
    if [[ $3 == *.RegistryStatus && -f $BROKER_HEALTH ]]; then
        cat -- "$BROKER_HEALTH"
    elif [[ $3 == *.ListManaged ]]; then
        python3 - <<'INNER'
import json,os
from pathlib import Path
p=Path(os.environ['RDP_RESERVATIONS'])
print(json.dumps(dict(windows=json.loads(os.environ['MANAGED'])['windows']+(json.loads(p.read_text()) if p.exists() else []))))
INNER
    elif [[ $3 == *.GetManaged ]]; then
        python3 - "$4" <<'INNER'
import json,os,sys
from pathlib import Path
windows=json.loads(Path(os.environ['RDP_RESERVATIONS']).read_text())
print(json.dumps(dict(state='FOUND',window=next(w for w in windows if w['managed_id']==sys.argv[1]))))
INNER
    else
        [[ $3 != *.SubmitInitialLayout ]] || printf '%s\n' "$4" >> "$COHORT_TRACE"
        [[ $3 != *.PollManagedLaunch ]] || printf 'generic-poll:%s\n' "$4" >> "$COHORT_TRACE"
        baseline_qdbus6 "$@"
    fi
}
#-----[ main script ]''', 1))

    def test_two_rdp_and_local_entries_use_one_common_ordered_cohort(self):
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host|under',
                           '1|konsole|local|btop|panel', '1|sdl-freerdp|rdp|rdp://joe@other:3390|over'])
        self.assertEqual(self.execute(), ['confirm', 'rdp:1:1', 'launch:2:1', 'rdp:1:3'])
        rows = self.trace.read_text().splitlines()
        self.assertEqual(rows[0], 'generic-poll:reg')
        cohort, = [json.loads(row) for row in rows if row.startswith('{')]
        self.assertEqual([entry['layer'] for entry in cohort['entries']], ['under', 'panel', 'over'])
        self.assertEqual(cohort['entries'][0]['registration_request_id'], f'{101:032x}')
        self.assertEqual(cohort['entries'][2]['registration_request_id'], f'{103:032x}')

    def test_completed_rdp_reservation_does_not_block_following_konsole(self):
        self.write_config(['2|sdl-freerdp|rdp|rdp://joe@host|under', '2|konsole|local|btop|panel'])
        self.assertEqual(self.execute(), ['confirm', 'rdp:2:1', 'launch:2:2'])
        checks = [json.loads(row) for row in self.preflights.read_text().splitlines()]
        self.assertEqual([row['slot'] for row in checks], [1, 1])
        self.assertTrue(all(row['managed'] == [] for row in checks))
        viewer, = json.loads(self.reservations.read_text())
        self.assertEqual(viewer['intended'], dict(desktop=2, slot=1))
        cohort, = [json.loads(row) for row in self.trace.read_text().splitlines() if row.startswith('{')]
        self.assertEqual(cohort['entries'], [dict(registration_request_id=viewer['request_id'], layer='under'),
                                            dict(registration_request_id='reg', layer='panel')])
        self.assertEqual(viewer['window_uuid'], f'{201:08x}-0000-0000-0000-000000000000')

    def test_second_rdp_still_preflights_free_slot_against_first_reservation(self):
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host|under',
                           '1|sdl-freerdp|rdp|rdp://joe@other|panel'])
        self.assertEqual(self.execute(), ['confirm', 'rdp:1:1', 'rdp:1:2'])
        checks = [json.loads(row) for row in self.preflights.read_text().splitlines()]
        self.assertEqual([row['slot'] for row in checks], [1, 2, 1, 2, 2])
        first, second = json.loads(self.reservations.read_text())
        self.assertEqual(checks[-1]['managed'], [first])
        self.assertNotEqual(first['request_id'], second['request_id'])
        self.assertNotEqual(first['window_uuid'], second['window_uuid'])
        cohort, = [json.loads(row) for row in self.trace.read_text().splitlines() if row.startswith('{')]
        self.assertEqual([item['registration_request_id'] for item in cohort['entries']],
                         [first['request_id'], second['request_id']])
        self.assertEqual([item['layer'] for item in cohort['entries']], ['under', 'panel'])

    def test_new_foreign_missing_reservation_stops_second_rdp(self):
        self.env['AFTER_RDP_CONFLICT'] = 'yes'
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host|under',
                           '1|sdl-freerdp|rdp|rdp://joe@other|panel'])
        self.assertEqual(self.execute(1), ['confirm', 'rdp:1:1'])
        checks = [json.loads(row) for row in self.preflights.read_text().splitlines()]
        self.assertEqual(checks[-1]['slot'], 2)
        self.assertEqual(checks[-1]['managed'][-1]['presence'], 'missing')
        self.assertFalse(self.trace.exists(), 'Incomplete cohort must not be submitted')

    def test_preexisting_unlaunched_rdp_reservations_block_before_confirmation(self):
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host', '1|sdl-freerdp|rdp|rdp://joe@other'])
        for presence in ('present', 'missing'):
            with self.subTest(presence=presence):
                self.env['MANAGED'] = json.dumps(dict(windows=[dict(managed_id='win-foreign',
                    presence=presence, intended=dict(desktop=1, slot=2))]))
                self.assertEqual(self.execute(2), [])
                self.assertFalse(self.reservations.exists())

    def test_unlaunched_rdp_prerequisites_are_rechecked_after_first_success(self):
        self.env['RDP_LATE_PREREQUISITE_FAIL'] = 'yes'
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host', '1|sdl-freerdp|rdp|rdp://joe@other'])
        self.assertEqual(self.execute(1), ['confirm', 'rdp:1:1'])
        self.assertFalse(self.trace.exists())

    def test_global_health_still_blocks_after_skipping_completed_rdp(self):
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host', '1|konsole|local|btop'])
        baseline = json.loads(self.env['BROKER_STATE'])
        for field, key, value in (('request_counts', 'pending', 1), ('request_counts', 'running', 1),
                                  ('placement_transaction', 'state', 'VERIFYING'),
                                  ('presence_counts', 'uncertain', 1),
                                  ('observation', 'synchronized', False),
                                  (None, 'viewer_cleanup_uncertain', True),
                                  (None, 'initial_layout_active', True)):
            with self.subTest(field=field, key=key):
                state = copy.deepcopy(baseline)
                (state if field is None else state[field])[key] = value
                self.env['AFTER_RDP_HEALTH'] = json.dumps(state)
                for path in (self.calls, self.reservations, self.health, self.preflights, self.trace):
                    path.unlink(missing_ok=True)
                self.assertEqual(self.execute(1), ['confirm', 'rdp:1:1'])
                self.assertFalse(self.trace.exists())

    def test_clean_rdp_failure_continues_and_finalizes_only_successes(self):
        self.env['RDP_CLEAN_FAIL_SLOT']='2'
        self.write_config(['1|konsole|local|btop|panel','1|sdl-freerdp|rdp|rdp://joe@host|under',
                           '1|sdl-freerdp|rdp|rdp://joe@other|over'])
        self.assertEqual(self.execute(1),['confirm','launch:1:1','rdp:1:2','rdp:1:3'])
        cohorts=[json.loads(row) for row in self.trace.read_text().splitlines() if row.startswith('{')]
        self.assertEqual(len(cohorts),1)
        self.assertEqual(cohorts[0]['entries'],[dict(registration_request_id='reg',layer='panel'),
            dict(registration_request_id=f'{103:032x}',layer='over')])
        windows=json.loads(self.reservations.read_text())
        self.assertEqual([w['intended']['slot'] for w in windows],[3])

    def test_mixed_rdp_konsole_dolphin_vnc_uses_existing_single_cohort(self):
        state = json.loads(self.env['BROKER_STATE']); state['viewer_protocol'] = 1
        self.env['BROKER_STATE'] = json.dumps(state)
        (self.folder / 'dolphin').write_text('#!/bin/sh\nexit 99\n')
        (self.folder / 'dolphin').chmod(0o755)
        (self.folder / 'libexec/joetoo_kwin_vnc_launch.py').write_text("""import sys,json
if '--preflight' in sys.argv: print('{}');sys.exit(0)
json.load(sys.stdin)
print(json.dumps(dict(state='completed',registration_request_id='vnc-reg',placement_request_id='vnc-place')))
""")
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host|under', '1|konsole|local|btop|panel',
                           '1|dolphin|local||panel', '1|vncviewer|ssh|ssh://joe@host/display/2|over'])
        self.assertEqual(self.execute(), ['confirm', 'rdp:1:1', 'launch:2:1', 'launch:3:1'])
        cohorts = [json.loads(row) for row in self.trace.read_text().splitlines() if row.startswith('{')]
        self.assertEqual(len(cohorts), 1)
        self.assertEqual([entry['layer'] for entry in cohorts[0]['entries']], ['under', 'panel', 'panel', 'over'])
        self.assertEqual(cohorts[0]['entries'][-1]['registration_request_id'], 'vnc-reg')

    def test_preflight_refusal_occurs_before_confirmation_or_any_launch(self):
        self.env['RDP_PREFLIGHT_FAIL'] = '1'
        self.write_config(['1|konsole|local|btop', '1|sdl-freerdp|rdp|rdp://joe@host|under'])
        self.assertEqual(self.execute(2), [])

    def test_unsuccessful_rdp_stops_before_subsequent_entry_stage3_not_implemented(self):
        self.env['RDP_FAILED'] = '1'
        self.write_config(['1|sdl-freerdp|rdp|rdp://joe@host', '1|konsole|local|btop'])
        self.assertEqual(self.execute(1), ['confirm', 'rdp:1:1'])


if __name__ == '__main__':
    unittest.main()
