# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real -L parser/planner/orchestration; fake application/bus seams, no native calls."""
import json
import re
from pathlib import Path
import shutil
import subprocess
import unittest
from test_step1_5a_plan import ROOT
import test_step1_5c_launch as configured


class SingleRecipeTests(configured.ConfiguredLaunchTests):
    def setUp(self):
        super().setUp()
        self.env['BROKER_STATE']=json.dumps(dict(observation=dict(synchronized=True),
            presence_counts=dict(uncertain=0),request_counts=dict(pending=0,running=0),
            placement_transaction=dict(state='IDLE'),initial_layout_protocol=1,
            single_raise_protocol=1,viewer_protocol=1,initial_layout_active=False))
        self.env['MANAGED']=json.dumps(dict(count=0,windows=[]))
        shutil.copyfile(ROOT/'libexec/joetoo_kwin_rdp_target.py',self.folder/'libexec/joetoo_kwin_rdp_target.py')
        for name in ('joetoo_kwin_rdp_launch.py','joetoo_kwin_vnc_launch.py'):
            if name == 'joetoo_kwin_vnc_launch.py':
                (self.folder/'libexec'/name).write_text("print('{}')\n"); continue
            text=(ROOT/'libexec'/name).read_text()
            # Import real validators, but executing the disposable preflight helper
            # must not use the real bus or start a process. Worker suites cover it.
            text=text.rsplit('if __name__',1)[0]+"if __name__ == '__main__': print('{}')\n"
            (self.folder/'libexec'/name).write_text(text)
        self.client.write_text(self.client.read_text().replace('#-----[ main script ]',r'''
eval "$(declare -f qdbus6 | sed '1s/qdbus6/single_base_bus/')"
qdbus6() {
    case $3 in
      *.SubmitInitialLayout) printf 'cohort:%s\n' "$4" >> "$TRACE"; printf 'layout-id\n' ;;
      *.InitialLayoutStatus) printf '{"state":"%s"}\n' "${STACK_STATE:-SUCCEEDED}" ;;
      *.GetManaged) printf '%s\n' '{"state":"FOUND","window":{"presence":"present","placement":"succeeded","request_id":"reg","window_uuid":"aaaaaaaa-0000-0000-0000-000000000001"}}' ;;
      *) single_base_bus "$@" ;;
    esac
}
eval "$(declare -f confirm_continue_or_exit | sed '1s/confirm_continue_or_exit/single_base_confirm/')"
confirm_continue_or_exit() {
    single_base_confirm || return $?
    if [[ $RACE ]]; then MANAGED=$RACE; fi
    if [[ $BECOME_BUSY ]]; then BROKER_STATE=$BECOME_BUSY; fi
}
eval "$(declare -f launch_managed_window | sed '1s/launch_managed_window/single_base_launch/')"
launch_managed_window() {
    printf 'intent:%s:%s:%s:%s,%s,%s,%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "$7" >> "$TRACE"
    single_base_launch "$@" || return $?
    [[ ${PLACEMENT_STATE:-OK} != ERROR* ]]
}
_test_single_configured_window() {
    launch_rdp_result='{"state":"completed","remote_session":"unverified","registration":{"state":"registered","request_id":"reg","managed_id":"win-999","window_uuid":"aaaaaaaa-0000-0000-0000-000000000001"},"placement":{"placement":"succeeded","request_id":"place","managed_id":"win-999","window_uuid":"aaaaaaaa-0000-0000-0000-000000000001"}}'
    launch_managed_window "$@"
}
#-----[ main script ]''',1))

        helper=self.folder/'libexec/joetoo-kwin-launch-functions'
        helper.write_text(helper.read_text()+'\nlaunch_configured_window() { _test_single_configured_window "$@"; }\n')
        (self.folder/'libexec/joetoo_kwin_sftp_capability.py').write_text("print('{}')\n")

    def run_single(self, operands=None, expected=0, flags=(), selected=False):
        if operands is None:operands=['3','konsole','local','btop']
        self.calls.unlink(missing_ok=True)
        config_args=[] if selected else ['-f',str(self.config)]
        result=subprocess.run(['bash',str(self.client),*config_args,*flags,'-L',*operands],
            env=self.env,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        trace=self.calls.read_text().splitlines() if self.calls.exists() else []
        return result.stdout+result.stderr,trace

    def record(self, slot, presence='present', desktop=3):
        return dict(managed_id=f'win-{slot:03}',window_uuid=f'{slot:08x}-0000-0000-0000-000000000001',
            intended=dict(desktop=desktop,slot=slot),presence=presence,placement='succeeded')

    def test_timestamp_occurs_after_confirmation_once_per_actual_attempt(self):
        marker=self.folder/'timestamp-calls'
        with self.mock_header.open('a') as stream:
            stream.write('\ntimestamp() { printf "%s\\n" timestamp >> "'+str(marker)+'"; printf "%s\\n" 20261112-09:11:16; }\n')
        self.env['CANCEL']='yes';self.run_single(expected=1)
        self.assertFalse(marker.exists());del self.env['CANCEL']
        output,trace=self.run_single()
        self.assertEqual(marker.read_text().splitlines(),['timestamp'])
        self.assertRegex(output,r'\[20261112-09:11:16\] Launching desktop \[3\] slot \[1\]')
        marker.unlink();self.calls.unlink()
        run=subprocess.run(['bash',str(self.client),'-o','-f',str(self.config)],env=self.env,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertEqual(marker.read_text().splitlines(),['timestamp','timestamp'])
        self.assertEqual(len(re.findall(r'\[20261112-09:11:16\] Launching desktop',run.stdout)),2)

    @unittest.skipUnless(Path('/usr/sbin/script_header_joetoo').is_file(),'installed header unavailable')
    def test_real_header_timestamp_format_without_loading_host_configuration(self):
        source=Path('/usr/sbin/script_header_joetoo').read_text()
        function=re.search(r'^timestamp\(\)[^\n]*\n\{[^\n]*\}',source,re.M)
        self.assertIsNotNone(function)
        run=subprocess.run(['bash','-c',function[0]+'\ntimestamp'],capture_output=True,text=True,timeout=5)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertRegex(run.stdout,r'^\d{8}-\d{2}:\d{2}:\d{2}\n$')

    def test_omitted_and_explicit_over_share_graphical_geometry_and_one_cohort(self):
        for extra in ([],['over']):
            output,trace=self.run_single(['3','konsole','local','btop',*extra])
            self.assertIn('LAUNCH PLAN: [1]',output)
            self.assertIn('intent:konsole:1:3:96,32,1804,972',trace)
            self.assertEqual(trace.count('confirm'),1)
            cohorts=[json.loads(line[7:]) for line in trace if line.startswith('cohort:')]
            self.assertEqual(len(cohorts),1);self.assertTrue(cohorts[0]['single_raise'])
            self.assertEqual(cohorts[0]['entries'],[dict(registration_request_id='reg',layer='over')])

    def test_reservations_including_missing_pick_free_logical_slot_not_panel_count(self):
        records=[self.record(1),self.record(2,'missing'),self.record(4),self.record(5)]
        original=json.dumps(dict(count=len(records),windows=records));self.env['MANAGED']=original
        _,trace=self.run_single()
        self.assertIn('intent:konsole:3:3:96,32,1804,972',trace)
        self.assertEqual(self.env['MANAGED'],original)
        self.assertFalse(any('move' in line.lower() for line in trace))
        records=[self.record(n) for n in range(1,257)]
        self.env['MANAGED']=json.dumps(dict(count=len(records),windows=records))
        output,trace=self.run_single(expected=2)
        self.assertIn('no unused logical slot',output);self.assertEqual(trace,[])

    def test_layers_counts_and_structural_fields_reject_before_confirmation(self):
        base=['3','konsole','local','btop']
        for layer in ('panel','under','bad',''):
            output,trace=self.run_single(base+[layer],expected=2)
            self.assertIn('LAYER' if layer not in ('panel','under') else 'not implemented yet',output)
            self.assertNotIn('version 2',output);self.assertEqual(trace,[])
        for operands in ([],base[:3],base+['over','1'],['3|konsole|local|btop'],
                         ['3','konsole','local','PRIVATE\n']):
            output,trace=self.run_single(operands,expected=2)
            self.assertEqual(trace,[]);self.assertNotIn('PRIVATE',output)

    def test_field_specific_validation_and_target_redaction(self):
        for operands,field in ((['0','konsole','local','btop'],'desktop'),
             (['3','other','local','btop'],'PROGRAM'),(['3','konsole','sftp','sftp://host/'],'MODE'),
             (['3','sdl-freerdp','rdp','rdp://joe:PRIVATE@host'],'TARGET'),
             (['3','vncviewer','ssh','ssh://joe:PRIVATE@host/display/1'],'TARGET'),
             (['3','dolphin','sftp','sftp://joe:PRIVATE@host/'],'TARGET'),
             (['3','konsole','ssh','bad target'],'target')):
            output,trace=self.run_single(operands,expected=2)
            self.assertIn(field.lower(),output.lower());self.assertNotIn('PRIVATE',output);self.assertEqual(trace,[])

    def test_confirmation_declined_launch_and_stack_failures_are_non_success(self):
        self.env['CANCEL']='yes';_,trace=self.run_single(expected=1)
        self.assertEqual(trace,['confirm']);del self.env['CANCEL']
        self.env['FAIL_FIRST']='yes';_,trace=self.run_single(['1','konsole','local','btop'],expected=1)
        self.assertFalse(any(line.startswith('cohort:') for line in trace));del self.env['FAIL_FIRST']
        self.env['PLACEMENT_STATE']='ERROR refused';_,trace=self.run_single(expected=1)
        self.assertFalse(any(line.startswith('cohort:') for line in trace));del self.env['PLACEMENT_STATE']
        self.env['STACK_STATE']='FAILED';output,_=self.run_single(expected=1)
        self.assertIn('stacking/focus incomplete',output.lower())

    def test_busy_malformed_uncertain_and_slot_race_fail_closed(self):
        baseline=self.env['BROKER_STATE']
        busy=json.loads(baseline);busy['placement_transaction']['state']='RUNNING'
        self.env['BROKER_STATE']=json.dumps(busy);_,trace=self.run_single(expected=1);self.assertEqual(trace,[])
        self.env['BROKER_STATE']=baseline
        for value in ('{}','not JSON',json.dumps(dict(count=1,windows=[self.record(1,'uncertain')]))):
            self.env['MANAGED']=value;_,trace=self.run_single(expected=2);self.assertEqual(trace,[])
        self.env['MANAGED']='{"count":0,"windows":[]}'
        self.env['RACE']=json.dumps(dict(count=1,windows=[self.record(1)]))
        _,trace=self.run_single(expected=1);self.assertEqual(trace,['confirm']);del self.env['RACE']
        self.env['BECOME_BUSY']=json.dumps(busy)
        _,trace=self.run_single(expected=1);self.assertEqual(trace,['confirm'])

    def test_existing_selected_configuration_and_security_settings_remain_effective(self):
        with self.config.open('a') as stream:stream.write('\ngraphical_left_percent=10\ngraphical_width_percent=80\nrdp_security_protocol=nla\nrdp_certificate_policy=strict\n')
        output,trace=self.run_single(flags=('-v',))
        self.assertIn('intent:konsole:1:3:192,32,1536,972',trace)
        self.assertIn('rdp_security_protocol=nla',output);self.assertIn('rdp_certificate_policy=strict',output)

    def test_older_raise_capability_is_rejected_before_confirmation(self):
        state=json.loads(self.env['BROKER_STATE']);state.pop('single_raise_protocol')
        self.env['BROKER_STATE']=json.dumps(state)
        output,trace=self.run_single(expected=2)
        self.assertIn('single-window raise broker/resident required',output);self.assertEqual(trace,[])

    def test_selected_profile_is_loaded_but_its_recipe_list_is_not_launched(self):
        root=Path(self.env['XDG_CONFIG_HOME'])/'joetoo-kwin';(root/'profiles').mkdir(parents=True)
        profile=root/'profiles/work.conf';profile.write_text(self.config.read_text())
        (root/'joetoo-kwin.conf').symlink_to('profiles/work.conf')
        output,trace=self.run_single(selected=True)
        self.assertIn(str(root/'joetoo-kwin.conf'),output)
        self.assertEqual(sum(line.startswith('intent:') for line in trace),1)
        self.assertEqual((root/'joetoo-kwin.conf').readlink(),Path('profiles/work.conf'))

    def test_supported_adapters_reuse_single_entry_serial_orchestration(self):
        for program,mode,target in (('konsole','ssh','unreachable.invalid'),('dolphin','local',''),('dolphin','sftp','sftp://user@host.example/home/user/'),
            ('sdl-freerdp','rdp','rdp://user@host.example'),('vncviewer','ssh','ssh://user@host.example/display/2')):
            output,trace=self.run_single(['3',program,mode,target])
            self.assertTrue(any(line.startswith('intent:'+program+':') for line in trace))
            self.assertEqual(sum(line.startswith('cohort:') for line in trace),1)

# Do not rerun inherited -o tests as if they were new -L coverage.
for _name in dir(configured.ConfiguredLaunchTests):
    if _name.startswith('test_') and _name not in SingleRecipeTests.__dict__:
        setattr(SingleRecipeTests,_name,None)
