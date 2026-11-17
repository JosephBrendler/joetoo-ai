#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real broker/registry/CallerIdentity, synthetic native transport; no user bus.

These tests do not establish native effect loading, X11 event FIFO, compositor
scheduling, or actual application refusal. Native acceptance remains separate.
"""
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from test_step1_3a import load_broker_without_real_dbus, WINDOW_ID

LIB = Path(__file__).resolve().parents[1] / 'libexec'
sys.path.insert(0, str(LIB))
from joetoo_kwin_managed_close import DEFAULTS, settings, payload


class FD:
    def __init__(self, fd): self.fd = fd
    def take(self):
        value, self.fd = self.fd, None
        return value


class Native:
    def __init__(self):
        self.windows = {}
        self.calls = []
        self.results = {}
        self.hold = False
        self.pending = []
        self.owner = ':1.2'
        self.mode = 'wayland'
    def Inspect(self, uuid, **kw):
        answer = self.windows.get(uuid, dict(state='missing', uuid=uuid))
        kw['reply_handler'](json.dumps(answer))
    def Close(self, token, uuid, pid, app, grab, expires, **kw):
        self.calls.append((token, uuid, pid, app, grab))
        self.results[token] = dict(state='dispatching', token=token, uuid=uuid, helper_reaped=True, gone=False)
        if self.hold: self.pending.append(kw)
        else: kw['reply_handler'](json.dumps(self.results[token]))
    def Status(self, token, **kw): kw['reply_handler'](json.dumps(self.results[token]))


class ManagedCloseTests(unittest.TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.b = self.module.Broker(object())
        self.runtime = self.b._managed_close
        self.now = 10.0
        self.runtime.clock = lambda: self.now
        self.native = Native()
        self.timers = []
        self.module.GLib.timeout_add = lambda ms, fn: self.timers.append((ms, fn)) or len(self.timers)
        self.b.observation_synced = True
        self.b.observation_source = 'source-1'
        self.b.observation_revision = 1
        self.replies = []
        self.errors = []
        self.credentials_uid = os.geteuid()
        self.credentials_pid = os.getpid()
        self.credentials_fd = True
        self.credentials_bad = False
        test = self
        class Daemon:
            def GetNameOwner(self, name, **kw):
                kw['reply_handler'](':1.2' if name == 'org.kde.KWin' else test.native.owner)
            def GetConnectionCredentials(self, name, **kw):
                c = dict(UnixUserID=test.credentials_uid, ProcessID=test.credentials_pid)
                if test.credentials_fd:
                    c['ProcessFD'] = FD(os.open('/dev/null', os.O_RDONLY) if test.credentials_bad else os.pidfd_open(os.getpid()))
                kw['reply_handler'](c)
        class Bus:
            def get_object(self, name, path, **kw):
                if name == 'org.freedesktop.DBus': return Daemon()
                if name != ':1.2': raise AssertionError('native call must address pinned unique KWin owner')
                return test.native
            def add_signal_receiver(self, *args, **kw): return object()
        self.b._sdl_bus_connection = lambda: Bus()
        self.module.dbus.Interface = lambda obj, iface: obj
        self.register(WINDOW_ID)
    def tearDown(self):
        if self.runtime.job: self.runtime.release(self.runtime.job)
    def register(self, identifier, number=1, presence='present', backend='wayland'):
        r = self.b.registry
        request = 'launch' + str(number)
        r.begin_launch(request, source='source-1', synchronized=True, baseline=[], recipe=dict(desktop=1, slot=number))
        r.mark_running(request, os.getpid())
        observed = dict(uuid=identifier, pid=os.getpid(), resource_class='konsole', caption='not authorization')
        record = r.register_match(request, dict(state='MATCHED',request_id=request,pid=os.getpid(),evidence='pid',candidate_history_complete=True,window_uuid=identifier), current_windows={identifier:observed},source='source-1',synchronized=True)
        r.set_placement(identifier, 'pending'); r.set_placement(identifier, 'succeeded')
        if presence != 'present': r.set_presence(identifier, presence)
        self.native.windows[identifier] = dict(state='present', uuid=identifier, pid=os.getpid(),
            **{'class':'konsole'}, backend=backend, closeable=True, xid='123' if backend=='x11' else '0')
        return record
    def prepare(self, scope='one', identifier='win-001', **extra):
        self.b.PrepareManagedClose(json.dumps(dict(protocol=1,scope=scope,managed_id=identifier if scope=='one' else '',settings=extra)),sender=':1.7',reply=self.replies.append,error=self.errors.append)
        return json.loads(self.replies[-1]) if self.replies else None
    def commit(self, sender=':1.7'):
        self.b.CommitManagedClose(self.runtime.job['id'],sender=sender,reply=self.replies.append,error=self.errors.append)
        return json.loads(self.replies[-1])
    def close_current(self):
        token = self.runtime.job['targets'][self.runtime.job['index']]['token']
        self.native.results[token].update(state='closed',gone=True)
        self.runtime.tick(self.runtime.job)
    def test_defaults_and_bounded_overrides(self):
        self.assertEqual(settings(), DEFAULTS)
        self.assertEqual(settings({'managed_close_timeout_ms':'1000'})['managed_close_timeout_ms'], 1000)
        for value in (0, True, '500;echo secret', -1, 600001):
            with self.assertRaises(ValueError): settings({'managed_close_total_timeout_ms':value})
        with self.assertRaises(ValueError): payload('{"protocol":1,"protocol":1}')
    def test_exact_native_wayland_close_retains_registration_slot_and_placement(self):
        preview = self.prepare()
        self.assertEqual(preview['state'], 'prepared')
        self.assertEqual(self.native.calls, []) # Preview never dispatches.
        self.commit(); self.close_current()
        report = json.loads(self.b.ManagedCloseStatus(self.runtime.job['id']))
        self.assertEqual(report['state'], 'succeeded')
        self.assertEqual(self.native.calls[0][1], WINDOW_ID)
        r = self.b.registry.get_window('win-001')
        self.assertEqual((r.presence,r.placement,r.recipe['slot']), ('missing','succeeded',1))
        self.assertNotIn('token', report['targets'][0])
        with self.assertRaises(self.module.dbus.DBusException):
            self.b.SubmitManagedLaunch('konsole',1,1,1,1,800,600)
    def test_native_x11_uses_same_authenticated_adapter_contract(self):
        self.native.windows[WINDOW_ID]['backend']='x11'
        self.prepare();self.commit();self.close_current()
        self.assertEqual(self.runtime.job['state'],'succeeded')
        self.assertEqual(len(self.native.calls),1)
    def test_unknown_or_raw_uuid_id_rejected(self):
        for value in ('win-999', WINDOW_ID, 'win-1;echo secret'):
            self.prepare(identifier=value)
            self.assertTrue(self.errors)
        self.assertEqual(self.native.calls,[])
    def test_missing_and_uncertain_are_excluded_not_adopted_or_released(self):
        for presence in ('missing','uncertain'):
            self.b.registry.managed_windows[WINDOW_ID].presence=presence
            self.prepare();self.commit()
            self.assertEqual(self.native.calls,[])
            self.assertEqual(self.runtime.job['state'],'partial')
            self.assertEqual(self.b.registry.get_window('win-001').recipe['slot'],1)
    def test_actual_caller_identity_requires_processfd_uid_pid_and_liveness(self):
        for attribute,value in (('credentials_fd',False),('credentials_bad',True),('credentials_pid',os.getpid()+100000),('credentials_uid',os.geteuid()+1)):
            with self.subTest(attribute=attribute):
                original=getattr(self,attribute);setattr(self,attribute,value)
                self.prepare()
                self.assertEqual(self.runtime.job['state'],'failed')
                self.assertEqual(self.native.calls,[])
                setattr(self,attribute,original)
    def test_adapter_owner_must_be_authentic_kwin_unique_connection(self):
        self.native.owner=':1.99';self.prepare()
        self.assertEqual(self.runtime.job['state'],'failed')
        self.assertFalse(self.native.calls)
    def test_native_identity_mismatch_is_excluded(self):
        for key,value in (('pid',123),('uuid','11111111-1111-4111-8111-111111111111'),('class','foreign'),('closeable',False),('backend','unknown')):
            with self.subTest(key=key):
                old=self.native.windows[WINDOW_ID][key];self.native.windows[WINDOW_ID][key]=value
                self.prepare();self.commit();self.assertEqual(self.native.calls,[])
                self.native.windows[WINDOW_ID][key]=old
    def test_confirmation_owner_and_replay_rejected(self):
        self.prepare();self.commit(':1.99');self.assertTrue(self.errors);self.assertFalse(self.native.calls)
        self.commit();self.close_current();self.commit()
        self.assertEqual(len(self.native.calls),1)
    def test_synchronous_bus_failure_does_not_leave_authentication_busy(self):
        self.b._sdl_bus_connection=lambda: (_ for _ in ()).throw(RuntimeError('unavailable'))
        self.prepare()
        self.assertTrue(self.errors)
        self.assertFalse(self.runtime.busy())
        self.assertFalse(self.native.calls)

    def test_lost_authentication_callback_expires_with_no_dispatch(self):
        base=self.b._sdl_bus_connection()
        class Bus:
            def add_signal_receiver(self,*args,**kw): return object()
            def get_object(self,*args,**kw):
                return types.SimpleNamespace(GetConnectionCredentials=lambda *args,**kw: None)
        self.b._sdl_bus_connection=lambda: Bus()
        self.assertIsNone(self.prepare())
        self.assertTrue(self.runtime.busy())
        self.now+=301
        self.runtime.tick(self.runtime.job)
        self.assertFalse(self.runtime.busy())
        self.assertFalse(self.native.calls)

    def test_prepare_expiry_does_not_dispatch(self):
        self.prepare();self.now+=301;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'failed');self.assertFalse(self.native.calls)
    def test_source_and_ownership_loss_before_commit(self):
        self.prepare();self.b.observation_source='replacement';self.commit()
        self.assertEqual(self.runtime.job['state'],'failed');self.assertFalse(self.native.calls)
    def test_bulk_fixed_snapshot_and_frontend_loss(self):
        second='11111111-1111-4111-8111-111111111111'
        third='22222222-2222-4222-8222-222222222222'
        self.register(second,2);self.prepare('all');self.commit()
        self.runtime.owner_changed(':1.7',':1.7','')
        self.register(third,3) # Real broker gates this; snapshot must still exclude it.
        self.close_current();self.close_current()
        self.assertEqual(self.runtime.job['state'],'succeeded')
        self.assertEqual([c[1] for c in self.native.calls],[WINDOW_ID,second])
        self.assertEqual(self.b.registry.get_window(third).presence,'present')
    def test_busy_guards_new_placement_and_new_close(self):
        self.prepare()
        with self.assertRaises(self.module.dbus.DBusException): self.b.Submit(1,1,1,800,600)
        self.b.PrepareManagedClose(json.dumps(dict(protocol=1,scope='all',managed_id='',settings={})), sender=':1.9',reply=self.replies.append,error=self.errors.append)
        self.assertTrue(self.errors);self.assertFalse(self.native.calls)
    def test_active_initial_layout_or_registration_blocks_preparation(self):
        with patch.object(self.b,'_initial_layout_active',return_value=True):
            self.prepare();self.assertTrue(self.errors)
        self.b.registry._active_request_id='other'
        self.prepare();self.assertFalse(self.native.calls)
    def test_untrusted_observation_cannot_prove_close(self):
        self.prepare();self.commit()
        self.b.registry.set_presence(WINDOW_ID,'missing')
        self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'running')
        self.assertEqual(self.runtime.job['targets'][0]['state'],'waiting')
    def test_refusal_timeout_is_not_force_kill_and_bulk_continues_serially(self):
        self.register('11111111-1111-4111-8111-111111111111',2)
        self.prepare('all');self.commit();self.runtime.tick(self.runtime.job)
        self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(len(self.native.calls),2)
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'partial')
        self.assertEqual(self.runtime.job['targets'][0]['state'],'not_closed_timeout')
        self.assertEqual(self.b.registry.get_window('win-001').presence,'present')
    def test_unknown_dispatch_and_helper_cleanup_block_future_work(self):
        self.native.hold=True;self.prepare();self.commit();self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.assertTrue(self.runtime.busy())
        token=self.runtime.job['targets'][0]['token']
        self.native.pending[0]['reply_handler'](json.dumps(self.native.results[token]))
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
    def test_source_replacement_after_acceptance_never_revives(self):
        self.prepare();self.commit();self.runtime.owner_changed('org.kde.KWin',':1.2',':1.88')
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
    def test_invalid_close_receipt_cannot_hide_helper_ownership(self):
        self.native.Close=lambda token,uuid,pid,app,grab,expires,**kw: kw['reply_handler'](json.dumps(
            dict(state='dispatching',token='foreign',uuid=uuid,helper_reaped=False,gone=False)))
        self.prepare();self.commit()
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.assertTrue(self.runtime.busy())

    def test_forged_native_receipt_is_unresolved(self):
        self.prepare();self.commit()
        token=self.runtime.job['targets'][0]['token'];self.native.results[token]['uuid']='foreign'
        self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
    def test_completed_history_survives_new_operation_and_placement_unchanged(self):
        self.prepare();self.commit();self.close_current();first=self.runtime.job['id']
        self.prepare('all');self.commit()
        self.assertEqual(json.loads(self.b.ManagedCloseStatus(first))['state'],'succeeded')
        self.assertEqual(self.b.registry.get_window('win-001').placement,'succeeded')
    def terminal_preview(self, *, native_state='identified', session_pid=None):
        base=self.b._sdl_bus_connection()
        daemon=base.get_object('org.freedesktop.DBus','/org/freedesktop/DBus')
        def owner(name,**kw):
            if name=='org.kde.konsole-123': kw['reply_handler'](':1.3')
            else: daemon.GetNameOwner(name,**kw)
        console=types.SimpleNamespace(processId=lambda **kw: kw['reply_handler'](os.getpid() if session_pid is None else session_pid),
            sessionList=lambda **kw: kw['reply_handler'](['1']))
        test=self
        class Bus:
            def add_signal_receiver(self,*args,**kw): return object()
            def get_object(self,name,path,**kw):
                if name=='org.freedesktop.DBus':
                    return types.SimpleNamespace(GetNameOwner=owner,GetConnectionCredentials=daemon.GetConnectionCredentials)
                if name==':1.3' and path in ('/Sessions/1','/Windows/1'): return console
                return base.get_object(name,path,**kw)
        self.b._sdl_bus_connection=lambda: Bus()
        self.native.Terminal=lambda pid,**kw: kw['reply_handler'](json.dumps(dict(state=native_state,uuid=WINDOW_ID)))
        self.b.PrepareManagedClose(json.dumps(dict(protocol=1,scope='all',managed_id='',settings={},
            terminal=dict(service='org.kde.konsole-123',session='/Sessions/1',window='/Windows/1'))),
            sender=':1.7',reply=self.replies.append,error=self.errors.append)
        return json.loads(self.replies[-1])

    def test_terminal_warning_requires_actual_credentials_session_and_native_uuid_chain(self):
        preview=self.terminal_preview()
        self.assertEqual(preview['self_terminal'],'win-001')
        self.assertEqual(self.runtime.job['terminal_identity'].fd,None)
        self.assertFalse(self.native.calls)

    def test_missing_retirement_entry_cannot_trigger_self_close_warning(self):
        self.missing()
        preview=self.terminal_preview()
        self.assertEqual(preview['self_terminal'],'excluded')
        self.assertFalse(self.native.calls)

    def test_ambiguous_native_terminal_is_unknown_not_guessed(self):
        preview=self.terminal_preview(native_state='unknown')
        self.assertEqual(preview['self_terminal'],'unknown')
        self.assertFalse(self.native.calls)

    def test_foreign_terminal_session_pid_does_not_produce_warning(self):
        preview=self.terminal_preview(session_pid=9999999)
        self.assertEqual(preview['self_terminal'],'unknown')
        self.assertFalse(self.native.calls)

    def test_expired_diagnostic_probe_is_not_an_active_close_conflict(self):
        self.b.correlation=dict(state='PENDING',deadline=0)
        self.assertEqual(self.prepare()['state'],'prepared')

    def test_revision_gap_and_unsynchronized_stream_fail_closed(self):
        self.prepare()
        self.runtime.observation('source-1',3)
        self.assertEqual(self.runtime.job['state'],'failed')
        self.prepare();self.commit()
        self.b.observation_synced=False
        self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')

    def test_contiguous_observation_updates_do_not_prove_disappearance(self):
        self.prepare();self.commit()
        self.runtime.observation('source-1',2)
        self.b.observation_revision=2
        self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'running')
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'succeeded')

    def test_late_status_for_previous_target_cannot_skip_next_target(self):
        self.register('11111111-1111-4111-8111-111111111111',2)
        self.prepare('all');self.commit();self.runtime.tick(self.runtime.job)
        pending=[]
        self.native.Status=lambda token,**kw: pending.append((token,kw))
        self.runtime.tick(self.runtime.job)
        self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['index'],1)
        token,kw=pending[0]
        a=dict(self.native.results[token],state='closed',gone=True)
        kw['reply_handler'](json.dumps(a))
        self.assertEqual(self.runtime.job['index'],1)
        self.assertEqual(self.runtime.job['targets'][1]['state'],'waiting')

    def test_late_callback_cannot_claim_timely_closure_before_timer_runs(self):
        self.prepare();self.commit();self.now+=16
        t=self.runtime.job['targets'][0]
        self.runtime.native_result(self.runtime.job,t,dict(self.native.results[t['token']],state='closed',gone=True))
        self.assertEqual(self.runtime.job['state'],'partial')
        self.assertEqual(t['state'],'not_closed_timeout')

    def test_late_disappearance_does_not_change_terminal_timeout(self):
        self.prepare();self.commit();self.runtime.tick(self.runtime.job);self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'partial')
        self.close_current_after_terminal()
        self.assertEqual(self.runtime.job['state'],'partial')
    def missing(self, identifier=WINDOW_ID):
        self.b.registry.set_presence(identifier, 'missing')
        self.native.windows.pop(identifier, None)

    def test_sweep_preview_decline_and_expiry_never_retire(self):
        self.missing()
        for cancel in ('owner', 'deadline'):
            preview=self.prepare('all')
            self.assertEqual(preview['targets'][0]['action'],'retire_missing')
            self.assertTrue(preview['registration_retained'])
            self.assertEqual(len(self.b.registry.managed_windows),1)
            if cancel=='owner': self.runtime.owner_changed(':1.7',':1.7','')
            else: self.now+=301;self.runtime.tick(self.runtime.job)
            self.assertEqual(len(self.b.registry.managed_windows),1)
            self.assertTrue(json.loads(self.runtime.report(self.runtime.job))['registration_retained'])
            self.assertEqual(self.native.calls,[])

    def test_failed_sweep_authentication_reports_snapshot_as_retained(self):
        self.credentials_uid=os.geteuid()+1
        self.prepare('all')
        result=json.loads(self.runtime.report(self.runtime.job))
        self.assertEqual(result['state'],'failed')
        self.assertTrue(result['registration_retained']);self.assertTrue(result['reservations_retained'])
        self.assertEqual(len(self.b.registry.managed_windows),1)

    def test_confirmed_all_missing_sweep_succeeds_without_close_dispatch(self):
        second='11111111-1111-4111-8111-111111111111'
        self.register(second,2);self.missing();self.missing(second)
        self.prepare('all');self.commit()
        result=json.loads(self.b.ManagedCloseStatus(self.runtime.job['id']))
        self.assertEqual(result['state'],'succeeded')
        self.assertFalse(result['registration_retained']);self.assertFalse(result['reservations_retained'])
        self.assertEqual([t['state'] for t in result['targets']],['already_missing']*2)
        self.assertTrue(all(t['retired'] for t in result['targets']))
        self.assertEqual(json.loads(self.b.ListManaged()),dict(count=0,windows=[]))
        self.assertEqual(self.b.registry.uuid_by_managed_id,{})
        self.assertEqual(self.native.calls,[])
        self.assertEqual(self.b.registry.requests['launch1'].state,'succeeded')
        # The real broker's reservation gate now permits this logical slot.
        self.assertTrue(self.b.SubmitManagedLaunch('konsole',1,1,1,1,800,600))

    def test_mixed_sweep_retires_progressively_and_keeps_fixed_results(self):
        second='11111111-1111-4111-8111-111111111111'
        self.register(second,2);self.missing(second)
        self.prepare('all');self.commit()
        self.assertEqual(self.runtime.job['targets'][0]['state'],'already_missing')
        self.assertNotIn(second,self.b.registry.managed_windows)
        self.assertIn(WINDOW_ID,self.b.registry.managed_windows)
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'succeeded')
        self.assertEqual(self.b.registry.managed_windows,{})
        request_id=self.runtime.job['id']
        self.runtime.owner_changed(':1.7',':1.7','')
        self.prepare('all');self.commit()
        old=json.loads(self.b.ManagedCloseStatus(request_id))
        self.assertEqual([t['state'] for t in old['targets']],['already_missing','closed'])

    def test_legacy_missing_flag_and_wrong_native_uuid_are_not_absence_proof(self):
        self.b.registry.set_presence(WINDOW_ID,'missing')
        self.prepare('all');self.commit()
        self.assertEqual(self.runtime.job['state'],'partial')
        self.assertEqual(self.runtime.job['excluded'][0]['reason'],'native_presence_conflict')
        self.native.windows[WINDOW_ID]=dict(state='missing',uuid='11111111-1111-4111-8111-111111111111')
        self.prepare('all');self.commit()
        self.assertEqual(len(self.b.registry.managed_windows),1)
        self.assertFalse(self.native.calls)

    def test_preview_absence_is_revalidated_before_retirement(self):
        second='11111111-1111-4111-8111-111111111111'
        self.register(second,2);self.missing()
        self.prepare('all')
        self.native.windows[WINDOW_ID]=dict(state='present',uuid=WINDOW_ID)
        self.commit()
        self.assertEqual(self.runtime.job['targets'][0]['reason'],'native_absence_not_verified')
        self.assertEqual([c[1] for c in self.native.calls],[second])
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'partial')
        self.assertEqual(set(self.b.registry.managed_windows),{WINDOW_ID})

    def test_known_reaped_native_failure_continues_later_safe_target(self):
        second='11111111-1111-4111-8111-111111111111'
        self.register(second,2)
        close=self.native.Close
        def fail_first(token,identifier,pid,app,grab,expires,**kw):
            if identifier==WINDOW_ID:
                kw['reply_handler'](json.dumps(dict(token=token,uuid=identifier,state='unsupported',helper_reaped=True,gone=False)))
            else: close(token,identifier,pid,app,grab,expires,**kw)
        self.native.Close=fail_first
        self.prepare('all');self.commit()
        self.assertEqual(self.runtime.job['targets'][0]['reason'],'native_unsupported')
        self.close_current()
        self.assertEqual(self.runtime.job['state'],'partial')
        self.assertEqual(set(self.b.registry.managed_windows),{WINDOW_ID})
        result=json.loads(self.runtime.report(self.runtime.job))
        self.assertTrue(result['registration_retained'])
        self.assertFalse(result['targets'][0]['retired']);self.assertTrue(result['targets'][1]['retired'])

    def test_changed_record_identity_does_not_block_independent_targets(self):
        second='11111111-1111-4111-8111-111111111111'
        self.register(second,2);self.prepare('all')
        self.b.registry.managed_windows[WINDOW_ID].observation['pid']+=100000
        self.commit()
        self.assertEqual(self.runtime.job['targets'][0]['state'],'identity_lost')
        self.assertEqual([c[1] for c in self.native.calls],[second])
        self.close_current()
        self.assertEqual(set(self.b.registry.managed_windows),{WINDOW_ID})

    def test_uncertain_helper_never_undoes_retirements_or_dispatches_next(self):
        missing='11111111-1111-4111-8111-111111111111'
        later='22222222-2222-4222-8222-222222222222'
        self.register(missing,2);self.register(later,3);self.missing(missing)
        self.native.hold=True;self.prepare('all');self.commit()
        self.assertNotIn(missing,self.b.registry.managed_windows)
        self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.assertTrue(self.runtime.busy())
        self.assertEqual([c[1] for c in self.native.calls],[WINDOW_ID])
        token=self.runtime.job['targets'][1]['token']
        self.native.pending[0]['reply_handler'](json.dumps(dict(self.native.results[token],state='closed',gone=True)))
        self.assertEqual(set(self.b.registry.managed_windows),{WINDOW_ID,later})
        self.assertTrue(self.runtime.job['targets'][0]['retired'])
        self.assertEqual(self.runtime.job['targets'][2]['state'],'skipped')

    def test_source_loss_after_progress_preserves_retirement_and_blocks_dispatch(self):
        missing='11111111-1111-4111-8111-111111111111'
        self.register(missing,2);self.missing(missing)
        self.prepare('all');self.commit()
        self.runtime.owner_changed('org.kde.KWin',':1.2',':1.88')
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.assertNotIn(missing,self.b.registry.managed_windows)
        self.assertIn(WINDOW_ID,self.b.registry.managed_windows)

    def test_unanswered_post_confirmation_absence_preserves_record_and_guard(self):
        self.missing();self.prepare('all')
        self.native.Inspect=lambda identifier,**kw: None
        self.commit();self.now+=16;self.runtime.tick(self.runtime.job)
        self.assertEqual(self.runtime.job['state'],'cleanup_uncertain')
        self.assertIn(WINDOW_ID,self.b.registry.managed_windows)
        self.assertFalse(self.native.calls)

    def close_current_after_terminal(self):
        token=self.runtime.job['targets'][0]['token'];self.native.results[token].update(state='closed',gone=True)
        self.runtime.tick(self.runtime.job)


if __name__ == '__main__': unittest.main()
