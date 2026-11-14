from pathlib import Path
p=Path('tests/test_rdp_diagnostic_receiver.py')
s=p.read_text().replace('import signal\n', 'import signal\n')
a=s.index("\nif __name__ == '__main__':")
addition=r'''

class DiagnosticWrapperTests(unittest.TestCase):
    """Run ONLY a private copy with fake proof/KWin/receiver and header."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.tools = self.folder/'tools'; self.tools.mkdir()
        self.bin = self.folder/'bin'; self.bin.mkdir()
        (self.folder/'captures').mkdir()
        self.trace = self.folder/'trace'
        self.header = self.folder/'header'
        self.header.write_text(''' + "'''" + r'''
TRUE=0; FALSE=""; notice=5; warn=4; err=3
j_msg() { printf '%s\n' "$*"; }
handle_result() {
    printf 'report:%s\n' "$1" >> "$TRACE"
    [[ ${MOCK_REPORT_FAIL:-} ]] && return 32
    return "$1"
}
right_status() { return "$1"; }
separator() { :; }
show_config() { :; }
checknotroot() { :; }
confirm_continue_or_exit() { [[ ${MOCK_ALLOW:-yes} == yes ]]; }
decode_right_status() { printf 'decode:%s\n' "$1" >> "$TRACE"; }
''' + "'''" + r''')
        wrapper = SOURCE.with_name('joetoo-rdp-diagnostic-run.sh').read_text()
        self.wrapper = self.tools/'joetoo-rdp-diagnostic-run.sh'
        self.wrapper.write_text(wrapper.replace('source /usr/sbin/script_header_joetoo',
                                                'source "'+str(self.header)+'"', 1))
        helper = self.tools/'joetoo-rdp-diagnostic-receiver.py'
        helper.write_text(''' + "'''" + r'''
import json, os, pathlib, signal, sys, time
trace=pathlib.Path(os.environ['TRACE'])
root=pathlib.Path(os.environ['FIXTURE'])
mode=os.environ.get('MOCK_MODE','')
def log(value):
 with trace.open('a') as stream: stream.write(value+'\n')
command=sys.argv[1]; directory=pathlib.Path(sys.argv[2])
if command=='serve':
 log('serve')
 if mode=='startfail': sys.exit(1)
 (root/'receiver.pid').write_text(str(os.getpid()))
 def stop(*args):
  log('receiver_stop'); sys.exit(0)
 signal.signal(signal.SIGTERM,stop)
 (directory/'run.json').write_text(json.dumps({'settings':{'exportTimeoutMs':1000,'ackTimeoutMs':100}}))
 (directory/'observer.js').write_text('// Fake observer; never loaded into KWin\n')
 while True: time.sleep(.05)
elif command=='status':
 if '--require-ready' in sys.argv:
  log('ready')
  if mode=='readyfail': sys.exit(1)
  (root/'ready').write_text('ready')
 elif '--require-complete' in sys.argv:
  log('complete')
  if mode=='completefail': sys.exit(1)
  assert (root/'finished').exists()
  (directory/'receipt.json').write_text(json.dumps({'internal_capture_intact':mode!='internalfail'}))
 else: log('status')
 print('{}')
elif command=='verify':
 log('verify')
 if mode=='verifyfail': sys.exit(1)
 print('{"transport_complete":true,"lifecycle_coverage":"unassessed"}')
else: sys.exit(1)
''' + "'''" + r''')
        proof = self.tools/'rdp_identity-security_proof.sh'
        proof.write_text(''' + "'''" + r'''#!/bin/bash
python3 - "$@" <<'PROOF'
import json, os, pathlib, sys, time
root=pathlib.Path(os.environ['FIXTURE'])
assert (root/'ready').exists(), 'proof before persisted readiness'
with open(os.environ['TRACE'],'a') as stream: stream.write('proof:'+json.dumps(sys.argv[1:])+'\n')
if os.environ.get('MOCK_MODE')=='proofslow':
 (root/'proof-started').write_text('yes')
 time.sleep(.3)
sys.exit(2 if os.environ.get('MOCK_MODE')=='prooffail' else 0)
PROOF
''' + "'''" + r''')
        qdbus = self.bin/'qdbus6'
        qdbus.write_text(''' + "'''" + r'''#!/usr/bin/env python3
import os, pathlib, sys
root=pathlib.Path(os.environ['FIXTURE']); mode=os.environ.get('MOCK_MODE','')
method=sys.argv[3]
with open(os.environ['TRACE'],'a') as stream: stream.write('dbus:'+method+'\n')
if method.endswith('isScriptLoaded'): print('true' if mode=='preexisting' else 'false')
elif method.endswith('loadScript'): print('71')
elif method.endswith('.run'):
 if mode=='runfail': sys.exit(1)
elif method.endswith('unloadScript'): print('false' if mode=='unloadfail' else 'true')
elif method.endswith('invokeShortcut'): (root/'finished').write_text('finished')
else: sys.exit(1)
''' + "'''" + r''')
        qdbus.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin)+os.pathsep+os.environ['PATH'],
                        FIXTURE=str(self.folder), TRACE=str(self.trace),
                        TMPDIR=str(self.folder/'captures'), RDP_DIAG_SECONDS='2400',
                        RDP_DIAG_START_TIMEOUT_SECONDS='1', RDP_DIAG_CLEANUP_MS='1000',
                        RDP_DIAG_READY_WAIT_MS='1000', RDP_DIAG_DBUS_SECONDS='2',
                        RDP_DIAG_POLL_MS='10')

    def run_wrapper(self, mode='', allow='yes', operands=None, **env):
        result = subprocess.run(['bash', str(self.wrapper), *(operands or ['sdl-freerdp','example.invalid:3389','joe'])],
                                env=dict(self.env, MOCK_MODE=mode, MOCK_ALLOW=allow, **env),
                                capture_output=True, text=True, timeout=15)
        pidfile=self.folder/'receiver.pid'
        if pidfile.exists():
            pid=int(pidfile.read_text())
            try:
                os.kill(pid,0)
            except ProcessLookupError:
                pass
            else:
                # Test cleanup only, never a production receiver. Keep a leak
                # failure visible even on hosts whose sandbox denies pidfd.
                os.kill(pid,15)
                self.fail('owned fixture receiver was not cleaned up: '+result.stdout+result.stderr)
        return result

    def entries(self):
        return self.trace.read_text().splitlines() if self.trace.exists() else []

    def captures(self):
        return [p for p in (self.folder/'captures').iterdir() if p.is_dir()]

    def test_successful_order_readiness_export_cleanup_and_archive(self):
        result=self.run_wrapper()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        entries=self.entries()
        names=['serve','status','ready','proof:', 'invokeShortcut','complete','verify','unloadScript','receiver_stop']
        indices=[]
        for name in names:
            indices.append(next(i for i,line in enumerate(entries) if name in line))
        self.assertEqual(indices,sorted(indices))
        capture=self.captures()[0]
        archive=Path(str(capture)+'.tbz2')
        self.assertTrue(archive.exists())
        self.assertEqual(archive.stat().st_mode & 0o777,0o600)
        self.assertIn('UNASSESSED',result.stdout)
        self.assertIn('report:0',entries)

    def test_cancel_and_preexisting_observer_do_not_start_resources(self):
        result=self.run_wrapper(allow='no')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.entries(),[])
        result=self.run_wrapper(mode='preexisting')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('serve'==line or 'unloadScript' in line or 'proof:' in line for line in self.entries()))
        self.assertEqual(self.captures(),[])

    def test_failed_readiness_prevents_proof_but_unloads_our_observer(self):
        result=self.run_wrapper('readyfail')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any(line.startswith('proof:') for line in self.entries()))
        self.assertTrue(any('unloadScript' in line for line in self.entries()))
        self.assertTrue(Path(str(self.captures()[0])+'.tbz2').exists())

    def test_receiver_start_failure_is_bounded_and_never_loads_script(self):
        result=self.run_wrapper('startfail')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('loadScript' in line or line.startswith('proof:') for line in self.entries()))

    def test_run_failure_still_unloads_the_script_we_loaded(self):
        result=self.run_wrapper('runfail')
        self.assertNotEqual(result.returncode,0)
        self.assertTrue(any('unloadScript' in line for line in self.entries()))
        self.assertFalse(any(line.startswith('proof:') for line in self.entries()))

    def test_proof_failure_still_exports_and_retains_both_outcomes(self):
        result=self.run_wrapper('prooffail')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('verify',self.entries())
        self.assertIn('report:2',self.entries())
        self.assertIn('Proof command result [2]',result.stdout)

    def test_delivery_failure_preserves_evidence_and_stops_owned_resources(self):
        result=self.run_wrapper('completefail')
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('verify',self.entries())
        self.assertIn('receiver_stop',self.entries())
        self.assertTrue(self.captures())

    def test_verification_failure_does_not_claim_success(self):
        result=self.run_wrapper('verifyfail')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('receiver_stop',self.entries())

    def test_transport_complete_but_internal_incomplete_is_failure(self):
        result=self.run_wrapper('internalfail')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Internal observation incomplete',result.stderr)

    def test_reporting_fault_blocks_continuation_and_retains_original_action_status(self):
        result=self.run_wrapper(MOCK_REPORT_FAIL='yes')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any(line.startswith('proof:') for line in self.entries()))
        self.assertIn('decode:32',self.entries())
        self.assertIn('action status [0]',result.stdout)

    def test_unload_failure_is_reported_but_receiver_still_stopped(self):
        result=self.run_wrapper('unloadfail')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('receiver_stop',self.entries())

    def test_arguments_are_forwarded_as_array_without_shell_evaluation(self):
        target='example.invalid; touch '+str(self.folder/'injected')
        result=self.run_wrapper(operands=['sdl-freerdp',target,'user name'])
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        line=next(line for line in self.entries() if line.startswith('proof:'))
        self.assertEqual(json.loads(line.removeprefix('proof:')),['sdl-freerdp',target,'user name'])
        self.assertFalse((self.folder/'injected').exists())

    def test_unrelated_process_remains_alive(self):
        unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])
        try:
            result=self.run_wrapper()
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate(); unrelated.wait(timeout=5)
'''
s=s[:a]+addition+s[a:]
p.write_text(s)
