# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only CLI inventory using a disposable bus executable, never a live bus."""
import copy
import json
import os
from pathlib import Path
import subprocess
import unittest

from test_step1_5a_plan import PlannerHarness
import test_step1_4c_queries as queries
from test_step1_3a import WINDOW_ID


class ManagedInventoryTests(PlannerHarness, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.payload = self.folder / 'inventory.json'
        self.env['INVENTORY_FILE'] = str(self.payload)
        self.env['INVENTORY_EXIT'] = '0'
        spy = self.folder / 'qdbus6'
        spy.write_text('''#!/usr/bin/env python3
import json,os,sys
with open(os.environ['TRACE'],'a') as stream: stream.write(json.dumps(sys.argv[1:])+'\\n')
if sys.argv[1:] != ['org.joetoo.KWinBridge','/org/joetoo/KWinBridge','org.joetoo.KWinBridge.ListManaged']:
    sys.exit(98)
sys.stdout.buffer.write(open(os.environ['INVENTORY_FILE'],'rb').read())
sys.exit(int(os.environ['INVENTORY_EXIT']))
''')
        spy.chmod(0o755)
        self.base_record = dict(managed_id='win-001',window_uuid=WINDOW_ID,
            intended=dict(desktop=3,slot=1),presence='present',placement='succeeded',
            request_id='a'*32,run_id=None,connection='not_attempted')

    def listing(self, payload, expected=0, args=('-l',)):
        self.payload.write_text(payload if isinstance(payload,str) else json.dumps(payload))
        self.calls.unlink(missing_ok=True)
        run = subprocess.run(['bash',str(self.client),*args],env=self.env,
                             capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,expected,run.stdout+run.stderr)
        calls = [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []
        self.assertEqual(calls,[['org.joetoo.KWinBridge','/org/joetoo/KWinBridge','org.joetoo.KWinBridge.ListManaged']])
        return run.stdout+run.stderr

    def test_empty_inventory_is_success_and_no_configuration_is_sourced(self):
        self.config.write_text('touch "$TRACE"; return 99\n')
        user = Path(self.env['XDG_CONFIG_HOME']) / 'joetoo-kwin';user.mkdir(parents=True)
        (user/'defaults.conf').write_text('return 99\n')
        (user/'joetoo-kwin.conf').write_text('return 99\n')
        self.assertIn('No managed windows',self.listing(dict(count=0,windows=[])))

    def test_sorted_fixed_columns_preserve_full_ids_uuids_and_missing_records(self):
        rows=[]
        for number,desktop,slot,presence in ((1,3,2,'missing'),(123456789012345,2,1,'present'),(2,3,1,'uncertain')):
            row=copy.deepcopy(self.base_record)
            row.update(managed_id='win-'+str(number),presence=presence,
                       window_uuid=f'{number:08x}-0000-0000-0000-000000000001' if number<2**32 else 'aaaaaaaa-0000-0000-0000-000000000001')
            row['intended']=dict(desktop=desktop,slot=slot);rows.append(row)
        output=self.listing(dict(count=3,windows=rows))
        lines=output.splitlines();self.assertEqual(len(lines),4)
        headers=('MANAGED_ID','DESKTOP','SLOT','PRESENCE','PLACEMENT','WINDOW_UUID')
        starts=[lines[0].index(header) for header in headers]
        for line,row in zip(lines[1:],[rows[1],rows[2],rows[0]]):
            values=[row['managed_id'],str(row['intended']['desktop']),str(row['intended']['slot']),
                    row['presence'],row['placement'],row['window_uuid']]
            for start,value in zip(starts,values):self.assertEqual(line[start:start+len(value)],value)
        self.assertNotIn('disconnected',output)

    def test_real_broker_query_and_lookup_shape_and_retained_missing_record(self):
        fixture=queries.ReadOnlyManagedQueryTests();fixture.setUp()
        try:
            fixture.sync();fixture.register()
            fixture.event('removed')
            before=fixture.broker.ListManaged()
            record=json.loads(fixture.broker.GetManaged('win-001'))['window']
            output=self.listing(before)
            self.assertIn(record['window_uuid'],output)
            self.assertIn('missing',output)
            self.assertEqual(fixture.broker.ListManaged(),before)
            self.assertIsNone(fixture.broker.request)
        finally:fixture.doCleanups()

    def test_private_extra_fields_never_displayed(self):
        row=copy.deepcopy(self.base_record)
        row.update(title='PRIVATE',target='PASSWORD',log='/private/log',connection='not_attempted')
        output=self.listing(dict(count=1,windows=[row]))
        for token in ('PRIVATE','PASSWORD','/private/log','disconnected'):self.assertNotIn(token,output)

    def test_unavailable_broker_is_not_empty_success(self):
        self.env['INVENTORY_EXIT']='7'
        output=self.listing(dict(count=0,windows=[]),expected=2)
        self.assertIn('unavailable',output);self.assertNotIn('No managed windows',output)

    def test_malformed_or_inconsistent_inventory_never_displays_partial_rows(self):
        bad=[{},None,[],dict(count=True,windows=[]),dict(count=1,windows=[]),
             '{"count":0,"count":0,"windows":[]}', 'not JSON', '['*2000+']'*2000]
        for key,value in (('managed_id','win-0'),('window_uuid','PRIVATE'),('presence','PRIVATE'),
                          ('placement','PRIVATE'),('intended',dict(desktop=True,slot=1)),
                          ('intended',dict(desktop=1,slot=0)),('intended',dict(desktop=257,slot=1))):
            row=copy.deepcopy(self.base_record);row[key]=value;bad.append(dict(count=1,windows=[row]))
        for duplicate in ('managed_id','window_uuid','slot'):
            row=copy.deepcopy(self.base_record)
            if duplicate!='managed_id':row['managed_id']='win-002'
            if duplicate!='window_uuid':row['window_uuid']='aaaaaaaa-0000-0000-0000-000000000001'
            if duplicate!='slot':row['intended']['slot']=2
            bad.append(dict(count=2,windows=[self.base_record,row]))
        for payload in bad:
            with self.subTest(payload=payload):
                output=self.listing(payload if payload is not None else 'null',expected=2)
                self.assertIn('malformed or inconsistent',output)
                self.assertNotIn('MANAGED_ID',output);self.assertNotIn('PRIVATE',output)
