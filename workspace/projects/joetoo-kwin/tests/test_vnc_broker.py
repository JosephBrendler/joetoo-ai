"""Real viewer broker state machine, fake X11 observer and KWin reports."""
import json
from unittest import TestCase
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

AUTH='d848c4c9-64ed-48bf-b083-40230314d5ac'
OTHER='d848c4c9-64ed-48bf-b083-40230314d5ad'


class FakeObserver:
    def __init__(self): self.events=[];self.closed=False
    def drain(self, limit): events=self.events;self.events=[];return events
    def select(self, *args): pass
    def close(self): self.closed=True


class ViewerBrokerTests(TestCase):
    def setUp(self):
        self.module=load_broker_without_real_dbus();self.b=self.module.Broker(object())
        self.now=100.;self.rev=1
        p=patch.object(self.module.time,'monotonic',side_effect=lambda:self.now);p.start();self.addCleanup(p.stop)
        self.observer=FakeObserver();p=patch.object(self.module,'DesktopObserver',return_value=self.observer);p.start();self.addCleanup(p.stop)
        self.sync()
        self.spec=dict(desktop=3,slot=1,x=10,y=20,width=500,height=400)
        ids=json.loads(self.b.SubmitManagedViewerLaunch(json.dumps(self.spec)))
        self.rid=ids['registration_request_id'];self.placement=ids['placement_request_id']
        self.b.SetManagedLaunchPid(self.rid,42)

    def sync(self,source='source'):
        self.rev+=1;self.b.SyncInventory(json.dumps(dict(source=source,revision=self.rev,windows=[],viewer_protocol=1)))

    def add(self,identifier=WINDOW_ID,pid=42):
        w=json.loads(observation('added',uuid=identifier))['window'];w.update(pid=pid,resource_class='Vncviewer',desktop_file='')
        self.rev+=1;self.b.ObserveWindow(json.dumps(dict(source='source',revision=self.rev,event='added',window=w)))

    def resolve(self,matches=None):
        claim=json.loads(self.b.TakeManagedViewer('source'))
        return self.b.CompleteManagedViewer(json.dumps(claim|dict(matches=matches if matches is not None else [dict(xid=123,uuid=WINDOW_ID)])))

    def test_auth_never_registered_or_placed_and_auth_can_exceed_15_seconds(self):
        self.add(AUTH);self.now+=25
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'pending')
        self.assertEqual(self.b.TakeLaunch('Vncviewer',''),'')
        self.assertEqual(self.b.registry.managed_windows,{})
        self.add();self.observer.events=[('desktop',123)]
        self.assertEqual(self.resolve(),'');self.now+=.6
        result=json.loads(self.resolve());self.assertEqual(result['window_uuid'],WINDOW_ID)
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'registered')
        self.assertNotIn(AUTH,self.b.registry.managed_windows);self.assertTrue(self.observer.closed)

    def test_timeout_cleanup_and_no_late_registration(self):
        self.now+=121
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'timeout')
        self.assertTrue(self.observer.closed);self.assertEqual(self.b.TakeManagedViewer('source'),'')

    def test_source_replacement_and_cancel_release(self):
        self.sync('new-source');self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'failed')
        self.assertTrue(self.observer.closed)
        self.b.CancelManagedViewerLaunch(self.rid)

    def test_busy_stays_held_beyond_generic_20_seconds(self):
        self.now+=30
        with self.assertRaises(self.module.dbus.DBusException): self.b.Submit(1,1,1,100,100)

    def test_ambiguous_desktop_role_fails(self):
        self.add();self.add(OTHER);self.observer.events=[('desktop',123),('desktop',124)]
        self.resolve([dict(xid=123,uuid=WINDOW_ID),dict(xid=124,uuid=OTHER)])
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'ambiguous')
        self.assertFalse(self.b.registry.managed_windows)

    def test_wrong_pid_stale_claim_and_destroyed_xid_rejected(self):
        self.add(pid=99);self.observer.events=[('desktop',123)]
        self.resolve();self.assertFalse(self.b.registry.managed_windows)
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'failed')

    def test_disappearing_xid_cannot_be_reused(self):
        self.add();self.observer.events=[('desktop',123)]
        claim=json.loads(self.b.TakeManagedViewer('source'))
        self.observer.events=[('destroyed',123)]
        self.b.CompleteManagedViewer(json.dumps(claim|dict(matches=[dict(xid=123,uuid=WINDOW_ID)])))
        self.assertFalse(self.b.registry.managed_windows)

    def test_observer_failure_rolls_back_submission(self):
        self.b.CancelManagedViewerLaunch(self.rid)
        previous=self.b.request
        with patch.object(self.module,'DesktopObserver',side_effect=RuntimeError('no X')):
            with self.assertRaises(self.module.dbus.DBusException): self.b.SubmitManagedViewerLaunch(json.dumps(self.spec))
        self.assertIs(self.b.request,previous)


    def test_expiry_timer_and_stale_callback_are_bounded(self):
        callbacks=[]
        self.module.GLib.timeout_add=lambda interval,fn: callbacks.append((interval,fn)) or len(callbacks)
        self.module.GLib.source_remove=lambda token: None
        c=self.b._managed_correlation
        self.b._viewer_schedule_expiry(c);old=callbacks[-1][1]
        self.now+=1;self.b._viewer_schedule_expiry(c)
        old();self.assertEqual(c['state'],'PENDING')
        self.now+=121;callbacks[-1][1]()
        self.assertTrue(self.observer.closed)
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'timeout')

    def test_stale_claim_is_inert_and_current_claim_can_complete(self):
        self.add();self.observer.events=[('desktop',123)]
        old=json.loads(self.b.TakeManagedViewer('source'))
        current=json.loads(self.b.TakeManagedViewer('source'))
        self.b.CompleteManagedViewer(json.dumps(old|dict(matches=[dict(xid=123,uuid=WINDOW_ID)])))
        self.assertIsNone(self.b._managed_correlation['selected'])
        self.b.CompleteManagedViewer(json.dumps(current|dict(matches=[dict(xid=123,uuid=WINDOW_ID)])))
        self.assertIsNotNone(self.b._managed_correlation['selected'])

    def test_history_loss_fails_without_registration(self):
        self.b.observation_evicted_through=self.b._managed_correlation['event_floor']+1
        result=json.loads(self.b.PollManagedLaunch(self.rid))
        self.assertEqual(result['state'],'failed');self.assertTrue(self.observer.closed)

    def test_registered_viewer_placement_expires_without_erasing_identity(self):
        self.add();self.observer.events=[('desktop',123)]
        self.resolve();self.now+=.6;self.resolve()
        self.now+=16
        self.assertTrue(self.b.Status(self.placement).startswith('ERROR'))
        self.assertIn(WINDOW_ID,self.b.registry.managed_windows)
        self.assertEqual(json.loads(self.b.PollManagedLaunch(self.rid))['state'],'registered')

    def test_uncertain_observer_cleanup_cannot_register_or_allow_new_mutation(self):
        self.add();self.observer.events=[('desktop',123)]
        self.resolve();self.now+=.6
        self.observer.close=lambda:False
        self.assertEqual(self.resolve(),'')
        self.assertFalse(self.b.registry.managed_windows)
        self.assertTrue(json.loads(self.b.RegistryStatus())['viewer_cleanup_uncertain'])
        with self.assertRaises(self.module.dbus.DBusException):self.b.CancelManagedViewerLaunch(self.rid)
        with self.assertRaises(self.module.dbus.DBusException):self.b.Submit(1,0,0,100,100)

    def test_viewer_cannot_complete_without_uuid_verification(self):
        self.add();self.observer.events=[('desktop',123)]
        self.resolve();self.now+=.6;self.resolve()
        with self.assertRaises(self.module.dbus.DBusException):self.b.Complete(self.placement,'OK','unverified')
        self.assertEqual(self.b.request['state'],'RUNNING')
        self.b.observation_source='replacement'
        self.b.Complete(self.placement,'ERROR','late callback')
        self.assertTrue(self.b.Status(self.placement).startswith('ERROR'))
