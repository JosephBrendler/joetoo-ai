# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared activation context: real broker and CLI, synthetic IPC only."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_step1_3a import load_broker_without_real_dbus, WINDOW_ID

ROOT = Path(__file__).resolve().parents[1]


class ControlFocusBrokerTests(unittest.TestCase):
    def setUp(self):
        self.m = load_broker_without_real_dbus()
        self.b = self.m.Broker(object())
        self.b.observation_source = 'resident'
        self.b.observation_synced = True
        self.b._recovery = SimpleNamespace(authenticate=Mock())
        self.daemon = SimpleNamespace(GetConnectionUnixUser=lambda *a, **k: os.geteuid(),
                                      GetNameOwner=lambda *a, **k: ':1.kwin')
        self.b._control_daemon = lambda: self.daemon
        self.accel = SimpleNamespace(invokeShortcut=Mock())
        self.b.connection = SimpleNamespace(get_object=lambda *a, **k: self.accel)
        self.m.dbus.Interface = lambda obj, iface: obj
        self.timers = []
        self.removed = []
        self.m.GLib.timeout_add = lambda ms, callback: self.timers.append(callback) or len(self.timers)
        self.m.GLib.source_remove = self.removed.append
        self.now = 100
        timer = patch.object(self.m.time, 'monotonic', side_effect=lambda: self.now)
        timer.start(); self.addCleanup(timer.stop)
        self.replies = []

    def start(self, action='capture', handle=''):
        self.b.ControlFocus(action, handle, ':1.cli', self.replies.append, self.fail)
        return self.b._control_pending

    def claim(self):
        return json.loads(self.b.TakeControlFocus('resident', ':1.kwin'))

    def complete(self, state='captured', identifier=WINDOW_ID, request=None, sender=':1.kwin'):
        return self.b.CompleteControlFocus(request or self.b._control_pending['id'],
            json.dumps(dict(state=state, window_uuid=identifier)), sender)

    def capture(self):
        self.start(); self.claim(); self.assertTrue(self.complete())
        return json.loads(self.replies[-1])['handle']

    def test_capture_restore_one_time_no_managed_adoption(self):
        self.start(); self.claim()
        self.assertTrue(self.complete(identifier='{'+WINDOW_ID.upper()+'}'))
        handle = json.loads(self.replies[-1])['handle']
        self.assertEqual(len(handle), 64)
        self.assertEqual(self.b.registry.managed_windows, {})
        self.start('restore', handle)
        self.assertEqual(self.claim()['window_uuid'], WINDOW_ID)
        self.assertTrue(self.complete('requested'))
        self.assertEqual(json.loads(self.replies[-1]), {'state': 'requested'})
        self.start('restore', handle)
        self.assertEqual(json.loads(self.replies[-1])['reason'], 'unknown_context')

    def test_foreign_uid_and_arbitrary_uuid_not_accepted(self):
        self.daemon.GetConnectionUnixUser = lambda *a, **k: os.geteuid() + 1
        self.start()
        self.assertIsNone(self.b._control_pending)
        self.assertEqual(json.loads(self.replies[-1])['state'], 'skipped')
        self.daemon.GetConnectionUnixUser = lambda *a, **k: os.geteuid()
        self.start('restore', WINDOW_ID)
        self.assertEqual(json.loads(self.replies[-1])['reason'], 'unknown_context')

    def test_callback_authenticated_and_claimed_and_not_replayed(self):
        self.start()
        self.assertFalse(self.complete())
        self.b._recovery.authenticate.side_effect = PermissionError
        self.assertEqual(self.b.TakeControlFocus('resident', ':1.foreign'), '')
        self.assertFalse(self.complete())
        self.b._recovery.authenticate.side_effect = None
        claim = self.claim()
        self.assertEqual(self.b.TakeControlFocus('resident', ':1.kwin'), '')
        self.assertFalse(self.complete(request='wrong'))
        self.assertFalse(self.complete(identifier='not-a-uuid'))
        self.assertTrue(self.complete())
        self.assertFalse(self.complete(request=claim['id']))

    def test_timeout_and_late_callback_cannot_create_context(self):
        self.start(); claim = self.claim()
        self.now += 4
        self.assertFalse(self.complete())
        self.timers[-1]()
        self.assertIsNone(self.b._control_pending)
        self.assertFalse(self.complete(request=claim['id']))
        self.assertEqual(self.b._control_contexts, {})
        self.assertEqual(json.loads(self.replies[-1])['reason'], 'coordination_timeout')

    def test_source_replacement_and_owner_replacement_skip(self):
        for key in ('source', 'owner'):
            handle = self.capture()
            if key == 'source': self.b.observation_source = 'new'
            else: self.daemon.GetNameOwner = lambda *a, **k: ':1.other'
            self.start('restore', handle)
            self.assertIsNone(self.b._control_pending)
            self.assertNotIn(handle, self.b._control_contexts)
            self.b.observation_source = 'resident'

    def test_bounded_contexts_and_busy(self):
        self.b.registry._completed_limit = 2
        first = self.capture(); self.capture(); self.capture()
        self.assertNotIn(first, self.b._control_contexts)
        self.assertEqual(len(self.b._control_contexts), 2)
        self.start(); pending = self.b._control_pending
        self.start()
        self.assertIs(self.b._control_pending, pending)
        self.assertEqual(json.loads(self.replies[-1])['reason'], 'coordination_busy')

    def test_no_active_and_each_restore_outcome(self):
        self.start(); self.claim(); self.assertTrue(self.complete('no_active_window', None))
        self.assertEqual(self.b._control_contexts, {})
        for state in ('requested', 'already_active', 'missing', 'off_desktop', 'minimized', 'unavailable'):
            handle = self.capture(); self.start('restore', handle); self.claim()
            self.assertFalse(self.complete(state, 'd848c4c9-64ed-48bf-b083-40230314d5ac'))
            self.assertTrue(self.complete(state))

    def test_timeout_reports_last_handshake_boundary(self):
        for stage in ('dispatch_pending','shortcut_returned','claim_accepted','completion_rejected'):
            self.start()
            if stage != 'dispatch_pending':
                self.accel.invokeShortcut.call_args.kwargs['reply_handler']()
            if stage in ('claim_accepted','completion_rejected'):
                self.claim()
            if stage == 'completion_rejected':
                self.assertFalse(self.complete(identifier='malformed'))
            self.timers[-1]()
            result=json.loads(self.replies[-1])
            self.assertEqual(result['reason'],'coordination_timeout')
            self.assertEqual(result['stage'],stage)
            self.assertNotIn('handle',result)

    def test_registered_shortcut_roundtrip_real_resident_braced_qt_uuid(self):
        # Bridge the actual JS registerShortcut/Take/Complete calls to the real
        # broker methods. Only IPC transport and authenticated identity are fake.
        script = r"""
const fs=require('node:fs'),vm=require('node:vm');
function line(){let s='',b=Buffer.alloc(1);while(fs.readSync(0,b,0,1,null)){if(b[0]===10)return s;s+=b.toString();}throw Error('closed fixture');}
const config=JSON.parse(line()), source=fs.readFileSync(config.source,'utf8');
const shortcuts={},desktop={x11DesktopNumber:1},control={internalId:config.uuid,desktops:[desktop]};
let active=config.action==='capture'?control:{internalId:'other'},activations=0;
const workspace={currentDesktop:desktop,windowList:()=>[control]};
Object.defineProperty(workspace,'activeWindow',{get:()=>active,set(w){active=w;activations++;}});
const context={workspace,observerSource:'resident',BRIDGE:'b',PATH:'/b',
registerShortcut(name,label,key,fn){shortcuts[name]=fn;},
callDBus(...args){console.log(JSON.stringify({method:args[3],args:args.slice(4).filter(v=>typeof v!=='function')}));
if(args[3]==='TakeControlFocus')args.at(-1)(JSON.parse(line()));}};
const uuid=source.match(/function windowUUID\(win\) \{[\s\S]*?\n\}/)[0];
vm.runInNewContext(uuid+'\n'+source.slice(source.indexOf('function controlFocusFromBroker()')),context);
if(!shortcuts[config.shortcut])throw Error('shortcut not registered');
shortcuts[config.shortcut]();console.log(JSON.stringify({activations}));
"""
        counts, accepted_callbacks = [], []
        def invoke(name, **options):
            with subprocess.Popen(['node','-e',script],stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as process:
                process.stdin.write(json.dumps(dict(source=str(ROOT/'joetoo-kwin-resident.js'),
                    uuid='{'+WINDOW_ID.upper()+'}',action=self.b._control_pending['action'],shortcut=name))+'\n')
                process.stdin.flush()
                take=json.loads(process.stdout.readline())
                self.assertEqual(take['method'],'TakeControlFocus')
                claimed=self.b.TakeControlFocus(*take['args'],sender=':1.kwin')
                self.assertTrue(claimed)
                process.stdin.write(json.dumps(claimed)+'\n');process.stdin.flush()
                complete=json.loads(process.stdout.readline())
                self.assertEqual(complete['method'],'CompleteControlFocus')
                accepted=self.b.CompleteControlFocus(*complete['args'],sender=':1.kwin')
                counts.append(json.loads(process.stdout.readline())['activations'])
                _,stderr=process.communicate(timeout=5)
                self.assertEqual(process.returncode,0,stderr)
                accepted_callbacks.append(accepted)
        self.accel.invokeShortcut=invoke
        self.start()
        self.assertEqual(accepted_callbacks,[True], 'Take succeeded but Complete rejected Qt UUID')
        self.assertIsNone(self.b._control_pending, 'must finish without firing timeout')
        self.assertEqual(json.loads(self.replies[-1])['state'],'captured')
        handle=json.loads(self.replies[-1])['handle']
        self.assertEqual(self.b._control_contexts[handle]['uuid'],WINDOW_ID)
        self.start('restore',handle)
        self.assertEqual(json.loads(self.replies[-1])['state'],'requested')
        self.assertEqual(counts,[0,1])
        self.assertEqual(accepted_callbacks,[True,True])
        self.assertIsNone(self.b._control_pending)

    def test_shortcut_failure_returns_nonfatal_skip(self):
        self.accel.invokeShortcut = lambda *a, **k: k['error_handler']('unavailable')
        self.start()
        self.assertIsNone(self.b._control_pending)
        self.assertEqual(json.loads(self.replies[-1])['reason'], 'resident_unavailable')


class ControlFocusCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.trace = self.folder / 'trace'
        self.env = dict(os.environ, TRACE=str(self.trace), verbosity='6', PATH=str(self.folder)+os.pathsep+os.environ['PATH'])
        header = self.folder / 'header'
        header.write_text((ROOT/'tests/fixtures/step1_5a_header.bash').read_text()+r'''
qdbus6() {
    printf 'focus:%s\n' "$4" >> "$TRACE"
    case $4 in
      capture) [[ ${UNAVAILABLE:-} != yes ]] || return 1
        if [[ ${CAPTURE_REPLY:-} ]]; then printf '%s\n' "$CAPTURE_REPLY"; return 0; fi
        printf '{"state":"captured","handle":"%064d"}\n' 0 ;;
      restore) [[ ${RESTORE_UNAVAILABLE:-} != yes ]] || return 1
        printf '{"state":"requested"}\n' ;;
    esac
}
''')
        source = (ROOT/'joetoo-kwin').read_text().replace('source /usr/sbin/script_header_joetoo', 'source '+str(header), 1)
        # Substitute only mission bodies: production parse/dispatch/finalization
        # and production control helpers execute for every tested operation.
        marker = '# run as regular user, not root\nchecknotroot'
        stubs = r'''
mission_stub() { printf 'mission:%s\n' "$cli_operation" >> "$TRACE"; return "${MISSION_RC:-0}"; }
move_window() { mission_stub; }
open_plan() { mission_stub; }
close_managed_windows() { mission_stub; }
check_plan() { mission_stub; }
readonly_managed_query() { mission_stub; }
save_managed_snapshot() { mission_stub; }
restore_managed_snapshot() { mission_stub; }
list_managed_windows() { mission_stub; }
usage() { mission_stub; }
launch_one_window() { mission_stub; }
test_multi_launch() { mission_stub; }
'''
        source = source.replace(marker, stubs+'\n'+marker)
        # Source lookup retains its ordinary success path without real launch code.
        (self.folder/'libexec').mkdir()
        (self.folder/'libexec/joetoo-kwin-launch-functions').write_text(':\n')
        self.client = self.folder/'joetoo-kwin'; self.client.write_text(source)

    def run_cli(self, args, rc=0, **values):
        self.trace.unlink(missing_ok=True)
        result = subprocess.run(['bash',str(self.client),*args],env=dict(self.env,MISSION_RC=str(rc),**values),
            capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,rc,result.stderr+result.stdout)
        return self.trace.read_text().splitlines(), result

    def test_general_dispatch_capture_before_mission_restore_afterward(self):
        for args in (['-h'],['-s'],['-l'],['-i','win-001'],['-S'],['-r'],['-c'],['-o'],
                     ['-L','2','konsole','local','btop','under'],['-m','l'],['move','1','0','0','100','100'],
                     ['-d','win-001'],['-x']):
            with self.subTest(args=args):
                lines,_ = self.run_cli(args)
                self.assertEqual(lines, ['focus:capture', 'mission:'+args[0], 'focus:restore'])

    def test_ordinary_failure_decline_status_preserved_and_restored(self):
        for rc in (1,2,7):
            lines,_ = self.run_cli(['-o'],rc=rc)
            self.assertEqual(lines,['focus:capture','mission:-o','focus:restore'])
            lines,_ = self.run_cli(['-o'],rc=rc,RESTORE_UNAVAILABLE='yes')
            self.assertEqual(lines,['focus:capture','mission:-o','focus:restore'])

    def test_unavailable_capture_does_not_fail_or_attempt_restore(self):
        lines,_ = self.run_cli(['-l'], UNAVAILABLE='yes')
        self.assertEqual(lines,['focus:capture','mission:-l'])

    def test_debug_capture_failure_reports_stage_but_never_raw_response(self):
        self.env['verbosity']='7'
        payload=json.dumps(dict(state='skipped',reason='coordination_timeout',
            stage='completion_rejected',handle='PRIVATE_HANDLE',caption='PRIVATE_CAPTION'))
        lines,result=self.run_cli(['-o'],rc=1,CAPTURE_REPLY=payload)
        self.assertEqual(lines,['focus:capture','mission:-o'])
        self.assertIn('Control-window focus capture:',result.stdout)
        self.assertIn('reason=[coordination_timeout] stage=[completion_rejected]',result.stdout)
        self.assertNotIn('PRIVATE_',result.stdout+result.stderr)
        _,result=self.run_cli(['-o'],rc=2,CAPTURE_REPLY='PRIVATE_RAW_REPLY')
        self.assertIn('state=[unavailable]',result.stdout)
        self.assertNotIn('PRIVATE_RAW_REPLY',result.stdout+result.stderr)

    def test_header_style_ordinary_exit_still_restores_and_preserves_status(self):
        self.client.write_text(self.client.read_text().replace('return "${MISSION_RC:-0}";', 'exit 7;'))
        lines,_ = self.run_cli(['-o'],rc=7)
        self.assertEqual(lines,['focus:capture','mission:-o','focus:restore'])

    def test_existing_exit_cleanup_runs_before_focus_completion(self):
        self.client.write_text(self.client.read_text().replace('return "${MISSION_RC:-0}";',
            'trap \'saved=$?; printf "cleanup\\n" >> "$TRACE"; control_focus_on_exit "$saved"\' EXIT; exit 9;'))
        lines,_ = self.run_cli(['-r'],rc=9)
        self.assertEqual(lines,['focus:capture','mission:-r','cleanup','focus:restore'])

    def test_signal_exit_keeps_original_cleanup_and_does_not_run_completion(self):
        # Use a complete stub body to preserve shell syntax.
        source = self.client.read_text().replace('return "${MISSION_RC:-0}";', 'exit 130;')
        self.client.write_text(source)
        lines,_ = self.run_cli(['-x'],rc=130)
        self.assertEqual(lines,['focus:capture','mission:-x'])
