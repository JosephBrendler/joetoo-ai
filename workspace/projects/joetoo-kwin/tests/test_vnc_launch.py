"""VNC contract and actual supervisor with mocked processes, sockets and D-Bus."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from test_step1_5a_plan import ROOT, PlannerHarness
from test_step1_5c_launch import ConfiguredLaunchTests as _Configured

with patch.object(sys,'path',[str(ROOT/'libexec')]+sys.path):
    spec=importlib.util.spec_from_file_location('vnc_launch',ROOT/'libexec/joetoo_kwin_vnc_launch.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    from joetoo_kwin_vnc_target import target, settings


class VncTargetTests(unittest.TestCase):
    def test_valid_targets_preserve_alias_user_and_ports(self):
        for text,host,port in [('ssh://joe@Alias/display/2','Alias',5902),
                               ('ssh://[2001:db8::1]:2222/port/5900','2001:db8::1',5900),
                               ('ssh://192.0.2.1/display/0','192.0.2.1',5900)]:
            result=target(text);self.assertEqual(result['host'],host);self.assertEqual(result['vnc_port'],port)
        self.assertEqual(target('ssh://host:2222/display/2')['ssh_port'],2222)

    def test_invalid_ambiguous_or_secret_targets_rejected(self):
        for text in ['host:2','ssh://joe:secret@host/display/2','ssh://host/port/0','ssh://host:65536/display/2',
                     'ssh://host/display/99999','ssh://host/display/02','ssh://2001:db8::1/display/2',
                     'ssh://host/display/2?x=y','ssh://host/display/2\n','ssh://host;touch/x',
                     'ssh://host/%64isplay/2','ssh://host../display/2','ssh://host/port/5900/other']:
            with self.subTest(text=text), self.assertRaises(ValueError):target(text)

    def test_operational_bounds_and_long_authentication_override(self):
        self.assertEqual(settings({'vnc_viewer_ready_timeout_ms':300000})['vnc_viewer_ready_timeout_ms'],300000)
        for value in [0,-1,True,3600001,'$(touch bad)']:
            with self.assertRaises(ValueError):settings({'vnc_viewer_ready_timeout_ms':value})

    def test_ssh_and_viewer_endpoint_arrays_never_use_via_or_shell(self):
        e=target('ssh://joe@Alias:2222/display/2');argv=m.ssh_argv(e,Path('/private/control'))
        self.assertEqual(argv[-2:],['--','joe@Alias']);self.assertIn('-N',argv);self.assertIn('-T',argv)
        for option in ['-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oClearAllForwardings=yes',
                       '-oControlPersist=no','-oForkAfterAuthentication=no']:self.assertIn(option,argv)
        control=m.control_argv('/private/control',e,'forward','127.0.0.1:4444:127.0.0.1:5902')
        self.assertIn('127.0.0.1:4444:127.0.0.1:5902',control)
        self.assertEqual(control[1:3],['-F','/dev/null'])


    def test_broker_rejection_preserves_known_reason_without_raw_stderr(self):
        stderr='Error: org.joetoo.KWinBridge.InvalidRequest\nBroker requires a local DISPLAY for the X11/XWayland identity observer\nsecret=DO_NOT_LOG'
        with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'',stderr)):
            with self.assertRaises(RuntimeError) as raised:m.dbus('SubmitManagedViewerLaunch','{}',timeout=1)
        message=str(raised.exception)
        self.assertIn('org.joetoo.KWinBridge.InvalidRequest',message)
        self.assertIn('Broker requires a local DISPLAY',message)
        self.assertNotIn('DO_NOT_LOG',message)
        with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','untrusted secret=DO_NOT_LOG')):
            with self.assertRaisesRegex(RuntimeError,'Unclassified broker rejection') as raised:
                m.dbus('SubmitManagedViewerLaunch','{}',timeout=1)
        self.assertNotIn('DO_NOT_LOG',str(raised.exception))


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.job=dict(target='ssh://joe@Alias/display/2',frontend_pid=123,desktop=2,slot=1,x=1,y=2,width=500,height=400)
        with patch.object(m.os,'pidfd_open',return_value=90):self.worker=m.Supervisor(self.job,self.folder)
        self.ssh=MagicMock();self.ssh.pid=24;self.ssh.poll.return_value=None
        self.viewer=MagicMock();self.viewer.pid=42;self.viewer.poll.return_value=None
        self.worker.cancelled=lambda:False;self.worker.pause=lambda:None
        self.worker.start_tunnel=MagicMock(side_effect=lambda:setattr(self.worker,'ssh',self.ssh) or 4444)
        self.calls=[]
        def call(method,*args):
            self.calls.append((method,args))
            if method=='SubmitManagedViewerLaunch':return json.dumps(dict(registration_request_id='reg',placement_request_id='place'))
            if method=='PollManagedLaunch':return json.dumps(dict(state='registered',managed_id='win-1',window_uuid='uuid'))
            if method=='Status':return 'OK geometry verified'
            return ''
        self.worker.call=call

    def run_worker(self):
        with patch.object(m.subprocess,'Popen',return_value=self.viewer) as launch, \
             patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0)), \
             patch.object(m,'stop_owned') as stop,patch.object(m.os,'close'):
            self.worker.run()
        return json.loads((self.folder/'status').read_text()),launch,stop

    def test_actual_worker_reports_real_viewer_pid_and_retains_until_exit(self):
        result,launch,stop=self.run_worker()
        self.assertEqual(result['state'],'completed')
        self.assertIn(('SetManagedLaunchPid',('reg',42)),self.calls)
        self.assertEqual(launch.call_args.args[0],['vncviewer','-via','','-Fullcolor','-QualityLevel','9','-FullScreen=0','127.0.0.1::4444'])
        self.assertTrue(launch.call_args.kwargs['close_fds']);self.assertTrue(launch.call_args.kwargs['start_new_session'])
        self.viewer.wait.assert_called_once();stop.assert_called_once_with(self.ssh,2.)
        self.worker.start_tunnel.assert_called_once()
        argv=launch.call_args.args[0]
        self.assertEqual(argv[argv.index('-via')+1], '')
        self.assertEqual(launch.call_count,1)  # No viewer-owned forwarding command is launched here.

    def test_ssh_failure_cancels_registration_and_cleans_owned_resources(self):
        def fail_after_spawn():
            self.worker.ssh=self.ssh
            raise RuntimeError('SSH startup failed')
        self.worker.start_tunnel=MagicMock(side_effect=fail_after_spawn)
        result,launch,stop=self.run_worker()
        self.assertEqual(result['state'],'failed');launch.assert_not_called()
        self.assertIn(('CancelManagedViewerLaunch',('reg',)),self.calls)
        stop.assert_any_call(self.ssh,2.)

    def test_viewer_exit_does_not_claim_cancellation_or_authentication_failure(self):
        self.viewer.poll.return_value=0
        result,_,stop=self.run_worker()
        self.assertEqual(result['state'],'failed');self.assertIn('unverified',result['detail'])
        stop.assert_any_call(self.viewer,2.)

    def test_placement_failure_preserves_registered_viewer_and_tunnel_lifetime(self):
        previous=self.worker.call
        self.worker.call=lambda method,*args:'ERROR rejected geometry' if method=='Status' else previous(method,*args)
        result,_,stop=self.run_worker()
        self.assertEqual(result['state'],'failed');self.viewer.wait.assert_called_once()
        self.assertNotIn(('CancelManagedViewerLaunch',('reg',)),self.calls)
        stop.assert_called_once_with(self.ssh,2.)

    def test_cancel_and_uncertain_cleanup_stop_safely(self):
        self.worker.cancelled=lambda:True
        result,_,_=self.run_worker();self.assertEqual(result['state'],'failed')
        self.worker.registered=False
        with patch.object(m.subprocess,'Popen',return_value=self.viewer), \
             patch.object(m,'stop_owned',side_effect=RuntimeError('cleanup failed')) as stop,patch.object(m.os,'close'):
            self.worker.run()
            self.assertEqual([call.args[0] for call in stop.call_args_list], [self.viewer,self.ssh])
        result=json.loads((self.folder/'status').read_text());self.assertEqual(result['state'],'unresolved')

    def test_readiness_timeout_cleans_both_children_without_claiming_auth_failure(self):
        with patch.object(m.time,'monotonic',side_effect=[100.,221.]):
            result,_,stop=self.run_worker()
        self.assertEqual(result['state'],'failed')
        self.assertIn('timed out',result['detail']);self.assertIn('unverified',result['detail'])
        self.assertEqual([call.args[0] for call in stop.call_args_list], [self.viewer,self.ssh])
        self.assertIn(('CancelManagedViewerLaunch',('reg',)),self.calls)

    def test_worker_removes_private_directory_and_control_path_after_frontend_ack(self):
        # Model a residual control-socket pathname; no SSH process or listener.
        self.worker.control.write_text('owned control path')
        (self.folder/'ack').touch()
        with patch.object(m.subprocess,'Popen',return_value=self.viewer), \
             patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0)), \
             patch.object(m,'stop_owned') as stop,patch.object(m.os,'close'):
            self.worker.run()
        self.assertFalse(self.worker.control.exists());self.assertFalse(self.folder.exists())
        stop.assert_called_once_with(self.ssh,2.)

    def test_startup_port_collision_retries_only_owned_master_forward(self):
        self.worker=object.__new__(m.Supervisor)
        self.worker.endpoint=target(self.job['target']);self.worker.control=self.folder/'ssh'
        self.worker.control.touch();self.worker.bounds=settings(self.job);self.worker.pause=lambda:None
        master=MagicMock();master.poll.return_value=None
        outcomes=[subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],255),subprocess.CompletedProcess([],0)]
        with patch.object(m.subprocess,'Popen',return_value=master) as spawn, \
             patch.object(m.subprocess,'run',side_effect=outcomes) as run,patch.object(m,'free_port',side_effect=[4444,4445]):
            self.assertEqual(self.worker.start_tunnel(),4445)
        self.assertTrue(spawn.call_args.kwargs['close_fds'])
        self.assertIn('127.0.0.1:4445:127.0.0.1:5902',run.call_args.args[0])

    def test_stop_only_signals_owned_child_session_and_reaps(self):
        process=MagicMock();process.pid=4242;process.poll.return_value=None
        process.wait.side_effect=[subprocess.TimeoutExpired('owned',.1),0]
        with patch.object(m.os,'killpg') as kill:m.stop_owned(process,.1)
        self.assertEqual([c.args[0] for c in kill.call_args_list],[4242,4242])
        self.assertEqual(process.wait.call_count,2)


class OwnedProcessTests(unittest.TestCase):
    def test_cleanup_preserves_an_unrelated_headless_process(self):
        # These are disposable Python stand-ins, never SSH or GUI clients.
        children=[subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'],
                  start_new_session=True,close_fds=True,stdin=subprocess.DEVNULL,
                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) for _ in range(2)]
        try:
            m.stop_owned(children[0],.5)
            self.assertIsNotNone(children[0].poll());self.assertIsNone(children[1].poll())
        finally:
            for process in children:
                if process.poll() is None:process.terminate()
                process.wait(timeout=2)


class FrontendTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.runtime=Path(self.tmp.name);self.runtime.chmod(0o700)
        self.job=dict(target='ssh://Alias/display/2')

    def execute(self,cancel=False,worker_exited=False):
        worker=MagicMock();worker.poll.return_value=None
        def write_final(*args, **kwargs):
            folder=next(self.runtime.iterdir())
            m.write_status(folder,dict(state='failed' if cancel else 'completed',detail='mock outcome'))
            if worker_exited:
                (folder/'ssh').touch()
                (folder/'worker-exited').touch()
        worker.stdin.close.side_effect=None if cancel else write_final
        worker.wait.side_effect=write_final
        import io
        output=io.StringIO()
        with patch.dict(os.environ,{'XDG_RUNTIME_DIR':str(self.runtime)}), \
             patch.object(m,'preflight'),patch.object(m.subprocess,'Popen',return_value=worker) as spawn, \
             patch.object(m.signal,'signal'),patch.object(m.sys,'stdout',output), \
             patch.object(m.time,'sleep',side_effect=KeyboardInterrupt if cancel else None):
            result=m.launch(self.job)
        return result,json.loads(output.getvalue()),spawn,worker

    def test_detached_worker_closes_inherited_fds_and_success_returns(self):
        result,outcome,spawn,worker=self.execute()
        self.assertEqual(result,0);self.assertEqual(outcome['state'],'completed')
        self.assertTrue(spawn.call_args.kwargs['close_fds']);self.assertTrue(spawn.call_args.kwargs['start_new_session'])
        self.assertIn('--worker',spawn.call_args.args[0])

    def test_frontend_removes_directory_when_worker_exited_before_ack(self):
        result,outcome,_,_=self.execute(worker_exited=True)
        self.assertEqual(result,0);self.assertEqual(outcome['state'],'completed')
        self.assertEqual(list(self.runtime.iterdir()),[])

    def test_frontend_cancellation_requests_owned_cleanup(self):
        result,outcome,spawn,worker=self.execute(cancel=True)
        self.assertNotEqual(result,0);self.assertEqual(outcome['state'],'cancelled')
        self.assertTrue((next(self.runtime.iterdir())/'cancel').exists())
        worker.wait.assert_called_once()


class VncConfiguredTests(_Configured):
    def setUp(self):
        super().setUp()
        state=json.loads(self.env['BROKER_STATE']);state['viewer_protocol']=1;self.env['BROKER_STATE']=json.dumps(state)
        helper=self.folder/'libexec/joetoo_kwin_vnc_launch.py'
        helper.write_text('''import json,sys,os
if '--preflight' in sys.argv: sys.exit(0)
job=json.load(sys.stdin)
with open(os.environ['TRACE'],'a') as trace: trace.write('viewer:'+str(job['desktop'])+'\\n')
state=os.environ.get('VNC_RESULT','completed')
print(json.dumps(dict(state=state,registration_request_id='reg',placement_request_id='place')))
sys.exit({'completed':0,'failed':1,'unresolved':2}[state])
''')
        self.write_config(['1|vncviewer|ssh|ssh://joe@Alias/display/2','2|konsole|local|btop'])

    def test_vnc_mixed_order_and_known_failure_continuation(self):
        self.assertEqual(self.execute(),['confirm','viewer:1','launch:1:2'])
        self.calls.unlink();self.env['VNC_RESULT']='failed';self.env['REG_STATE']='failed';self.env['PLACEMENT_STATE']='ERROR'
        self.assertEqual(self.execute(1),['confirm','viewer:1','launch:1:2'])

    def test_uncertain_viewer_finalization_stops_subsequent_entries(self):
        self.env['VNC_RESULT']='unresolved'
        self.assertEqual(self.execute(1),['confirm','viewer:1'])

    def test_cancel_invalid_plan_and_c_are_offline(self):
        self.env['CANCEL']='yes';self.assertEqual(self.execute(1),['confirm'])
        self.calls.unlink();self.run_cli('-c','-f',str(self.config));self.assertFalse(self.calls.exists())
        self.write_config(['1|konsole|local|btop','2|vncviewer|ssh|ssh://joe:SECRET@host/display/2'])
        self.assertEqual(self.execute(2),[])

    def test_middle_failure_preserves_other_entries_and_cancel_stops(self):
        self.write_config(['1|konsole|local|btop','2|vncviewer|ssh|ssh://Alias/display/2','3|konsole|local|btop'])
        self.env['VNC_RESULT']='failed'
        self.assertEqual(self.execute(1),['confirm','launch:1:1','viewer:2','launch:1:3'])



for name in dir(_Configured):
    if name.startswith('test_') and name not in VncConfiguredTests.__dict__:setattr(VncConfiguredTests,name,None)
del _Configured
