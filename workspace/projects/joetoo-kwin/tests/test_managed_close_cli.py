# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Actual Bash parser/confirmation/private-pipe flow; disposable Python frontend."""
import json
import shutil
import subprocess
import unittest
from test_step1_5a_plan import PlannerHarness, ROOT


class ManagedCloseCliTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.env['REAL_LIBEXEC']=str(ROOT/'libexec')
        self.frontend = self.folder/'libexec/joetoo_kwin_managed_close.py'
        self.frontend.write_text('''import json,os,sys
sys.path.insert(0,os.environ['REAL_LIBEXEC'])
from joetoo_kwin_managed_close import settings
if sys.argv[1:]==['--defaults']:
    print(json.dumps(settings()));sys.exit(0)
if len(sys.argv)==3 and sys.argv[1]=='--settings':
    try: print(json.dumps(settings(json.loads(sys.argv[2]))))
    except Exception: sys.exit(2)
    sys.exit(0)
preview=dict(protocol=1,state='prepared',request_id='close-test',targets=[dict(managed_id='win-001',desktop=1,slot=1,window_uuid='11111111-1111-4111-8111-111111111111')],excluded=[],self_terminal=os.environ.get('SELF_TERMINAL','unknown'))
with open(os.environ['TRACE'],'a') as f: f.write('prepare:'+sys.argv[1]+':'+sys.argv[2]+'\\n')
print(json.dumps(preview),flush=True)
if sys.stdin.readline()!='CONFIRM\\n': sys.exit(1)
with open(os.environ['TRACE'],'a') as f: f.write('commit\\n')
state=os.environ.get('CLOSE_RESULT','succeeded')
print(json.dumps(dict(protocol=1,state=state,request_id='close-test')),flush=True)
sys.exit(0 if state=='succeeded' else 1)
''')
        self.client.write_text(self.client.read_text().replace('# run as regular user, not root','''
confirm_continue_or_exit() { printf 'confirmation\\n' >> "$TRACE"; [[ ${CANCEL:-} != yes ]]; }
# run as regular user, not root'''))
    def invoke(self,*args,expected=0):
        run=subprocess.run(['bash',str(self.client),'-f',str(self.config),*args],env=self.env,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,expected,run.stdout+run.stderr)
        return run.stdout+run.stderr, self.calls.read_text().splitlines() if self.calls.exists() else []
    def test_single_managed_id_preview_confirmation_then_commit(self):
        output,calls=self.invoke('-d','win-001')
        self.assertEqual(calls,['prepare:one:win-001','confirmation','commit'])
        self.assertIn('reserved slots will remain',output)
        self.assertNotIn('This terminal',output)
    def test_bulk_uses_same_confirmation_and_fixed_frontend(self):
        output,calls=self.invoke('-x')
        self.assertEqual(calls,['prepare:all:','confirmation','commit'])
        self.assertNotIn('This terminal',output)
    def test_conditional_positive_terminal_warning_only(self):
        self.env['SELF_TERMINAL']='win-001'
        output,_=self.invoke('-x');self.assertIn('This terminal (win-001)',output)
        for value in ('unknown','excluded'):
            self.env['SELF_TERMINAL']=value
            output,_=self.invoke('-x');self.assertNotIn('This terminal',output)
    def test_declined_confirmation_dispatches_nothing(self):
        self.env['CANCEL']='yes'
        _,calls=self.invoke('-x',expected=1)
        self.assertEqual(calls,['prepare:all:','confirmation'])
    def test_terminal_failure_is_nonzero_and_no_retry(self):
        self.env['CLOSE_RESULT']='partial'
        _,calls=self.invoke('-d','win-001',expected=1)
        self.assertEqual(calls.count('commit'),1)
    def test_bad_id_and_operand_count_fail_before_frontend(self):
        for args in (('-d',),('-d','not-managed'),('-d','win-001','extra'),('-x','extra'),('-f','','-x')):
            _,calls=self.invoke(*args,expected=2)
            self.assertEqual(calls,[])
    def test_no_plan_uses_builtins_and_optional_defaults_without_creating_home(self):
        self.config.unlink()
        before = sorted(str(p) for p in self.folder.rglob('*'))
        run = subprocess.run(['bash',str(self.client),'-x'],env=self.env,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        after = sorted(str(p) for p in self.folder.rglob('*') if p != self.calls)
        self.assertEqual(before,after)
    def test_invalid_close_budget_is_rejected_without_dispatch(self):
        self.write_config(extra='managed_close_timeout_ms="1; secret"')
        output,calls=self.invoke('-x',expected=2)
        self.assertEqual(calls,[]);self.assertNotIn('1; secret',output)


if __name__ == '__main__': unittest.main()
