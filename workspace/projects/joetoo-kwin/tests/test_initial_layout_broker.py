"""Bounded initial cohort: real broker methods with mock IPC imports."""
import json
import unittest
from unittest.mock import patch
import test_step1_4c_queries as queries


class InitialLayoutBrokerTests(queries.ReadOnlyManagedQueryTests):
    def setUp(self):
        super().setUp()
        self.sync(); self.register(); self.register(queries.SECOND, pid=43)
        for index, record in enumerate(self.broker.registry.managed_windows.values(), 1):
            record.recipe['slot'] = index
            record.placement = 'succeeded'
        self.broker.initial_layout_protocol = 1
        self.ids = [r.request_id for r in self.broker.registry.managed_windows.values()]
        self.uuids = list(self.broker.registry.managed_windows)

    def submit(self, layers=('under', 'panel'), **timing):
        return self.broker.SubmitInitialLayout(json.dumps({'entries': [
            {'registration_request_id': rid, 'layer': layer} for rid, layer in zip(self.ids, layers)], **timing}))

    def complete(self, rid, **override):
        r = self.broker.initial_layout
        result = dict(source=queries.SOURCE, order=r['order'], current_desktop=3,
                      before_active_uuid=self.uuids[0], active_uuid=r['preferred_uuid'],
                      focus_attempted=True, geometry_unchanged=True)
        result.update(override)
        self.broker.CompleteInitialLayout(rid, json.dumps(result))
        return json.loads(self.broker.InitialLayoutStatus(rid))

    def test_owned_cohort_and_focus_preference(self):
        for layers, expected in [(('under', 'panel'), 1), (('over', 'panel'), 0), (('panel', 'over'), 1)]:
            rid = self.submit(layers)
            self.assertEqual(self.broker.TakeInitialLayout('wrong-source'), '')
            request = json.loads(self.broker.TakeInitialLayout(queries.SOURCE))
            self.assertEqual(request['preferred_uuid'], self.uuids[expected])
            self.assertEqual(self.complete(rid)['state'], 'SUCCEEDED')

    def test_under_only_and_inactive_focus_are_not_claimed_as_activation(self):
        rid = self.submit(('under', 'under')); self.broker.TakeInitialLayout(queries.SOURCE)
        state = self.complete(rid, focus_attempted=False, active_uuid=self.uuids[0])
        self.assertEqual(state['focus'], 'no automatic target')
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        state = self.complete(rid, current_desktop=1, focus_attempted=False, active_uuid=self.uuids[0])
        self.assertIn('inactive desktop', state['focus'])
        self.assertEqual(state['state'], 'SUCCEEDED')

    def test_no_arbitrary_or_duplicate_identity(self):
        for payload in ({'entries': [{'uuid': self.uuids[0], 'layer': 'panel'}]},
                        {'entries': [{'registration_request_id': 'unknown', 'layer': 'panel'}]},
                        {'entries': [{'registration_request_id': self.ids[0], 'layer': 'panel'}]*2}):
            with self.assertRaises(self.module.dbus.DBusException):
                self.broker.SubmitInitialLayout(json.dumps(payload))
        self.broker.initial_layout_protocol = 0
        with self.assertRaises(self.module.dbus.DBusException): self.submit()

    def test_shared_busy_and_expiration(self):
        rid = self.submit()
        with self.assertRaises(self.module.dbus.DBusException): self.broker.Submit(1, 0, 0, 800, 900)
        with self.assertRaises(self.module.dbus.DBusException): self.submit()
        self.clock[0] += 11
        self.assertEqual(self.broker.TakeInitialLayout(queries.SOURCE), '')
        self.assertEqual(json.loads(self.broker.InitialLayoutStatus(rid))['state'], 'FAILED')
        self.broker.Submit(3, 0, 0, 800, 900)
        with self.assertRaises(self.module.dbus.DBusException): self.submit()

    def test_stack_focus_geometry_independent_and_post_focus_mismatch_fails(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        state = self.complete(rid, order=list(reversed(self.broker.initial_layout['order'])))
        self.assertEqual(state['state'], 'FAILED')
        self.assertEqual(state['geometry'], 'unchanged')
        self.assertEqual(state['focus'], 'verified')
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        self.broker.observed_windows[self.uuids[0]]['geometry']['x'] += 1
        self.assertEqual(self.complete(rid)['state'], 'FAILED')

    def test_source_disappearance_and_stale_completion(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        self.broker.observation_source = 'new-source'
        self.assertEqual(json.loads(self.broker.InitialLayoutStatus(rid))['state'], 'FAILED')
        with self.assertRaises(self.module.dbus.DBusException): self.complete(rid)

    def test_disappearing_target_and_unverified_registration_reject(self):
        first = self.broker.registry.managed_windows[self.uuids[0]]
        first.placement = 'pending'
        with self.assertRaises(self.module.dbus.DBusException): self.submit()
        first.placement = 'succeeded'
        rid = self.submit()
        self.broker.observed_windows.pop(self.uuids[0])
        self.assertEqual(self.broker.TakeInitialLayout(queries.SOURCE), '')
        self.assertEqual(json.loads(self.broker.InitialLayoutStatus(rid))['state'], 'FAILED')

    def test_malformed_completion_cannot_finish_a_request(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        for payload in ('[]', '{"source":"wrong"}', 'null'):
            with self.assertRaises(self.module.dbus.DBusException):
                self.broker.CompleteInitialLayout(rid, payload)
            self.assertEqual(json.loads(self.broker.InitialLayoutStatus(rid))['state'], 'RUNNING')
        self.assertEqual(self.complete(rid)['state'], 'SUCCEEDED')

    def test_disappearance_before_completion_is_bounded(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        self.broker.observed_windows.pop(self.uuids[0])
        with self.assertRaises(self.module.dbus.DBusException):
            self.complete(rid)
        state = json.loads(self.broker.InitialLayoutStatus(rid))
        self.assertEqual(state['state'], 'FAILED')
        self.assertFalse(self.broker._initial_layout_active())

    def test_disappearance_after_completion_guard_is_failed_evidence(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        active = self.broker._initial_layout_active

        def disappear_after_check():
            result = active()
            self.broker.observed_windows.pop(self.uuids[0], None)
            return result

        with patch.object(self.broker, '_initial_layout_active', disappear_after_check):
            state = self.complete(rid)
        self.assertEqual(state['state'], 'FAILED')
        self.assertEqual(state['stacking'], 'failed')
        self.assertEqual(state['geometry'], 'changed or unverified')
        self.assertIn(self.uuids[0], state['detail'])
        self.assertIn('disappeared', state['detail'])
        self.assertFalse(self.broker._initial_layout_active())

    def test_focus_bounds_are_validated_and_conveyed_without_changing_lease(self):
        for timing in ({'focus_timeout_ms': 0}, {'focus_timeout_ms': True},
                       {'focus_timeout_ms': 2001}, {'focus_poll_interval_ms': 251},
                       {'focus_timeout_ms': 10, 'focus_poll_interval_ms': 20},
                       {'focus_timeout_ms': '500'}):
            with self.assertRaises(self.module.dbus.DBusException): self.submit(**timing)
            self.assertIsNone(self.broker.initial_layout)
        rid = self.submit(focus_timeout_ms=1200, focus_poll_interval_ms=40)
        request = json.loads(self.broker.TakeInitialLayout(queries.SOURCE))
        self.assertEqual(request['focus_timeout_ms'], 1200)
        self.assertEqual(request['focus_poll_interval_ms'], 40)
        self.assertLessEqual(request['remaining_ms'], 10000)
        with self.assertRaises(self.module.dbus.DBusException): self.broker.Submit(1, 0, 0, 800, 900)
        self.assertEqual(self.complete(rid, focus_observation='delayed', focus_elapsed_ms=40)['state'], 'SUCCEEDED')

    def test_focus_timeout_preserves_verified_stack_and_placement(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        state = self.complete(rid, active_uuid=self.uuids[0],
                              error='Focus observation timed out', focus_observation='timeout', focus_elapsed_ms=500)
        self.assertEqual(state['state'], 'FAILED')
        self.assertEqual(state['stacking'], 'verified')
        self.assertEqual(state['geometry'], 'unchanged')
        self.assertEqual(state['focus'], 'failed')
        self.assertEqual(state['focus_observation'], 'timeout')
        self.assertIn('timed out', state['detail'])
        self.assertTrue(all(r.placement == 'succeeded' for r in self.broker.registry.managed_windows.values()))

    def test_mismatch_without_resident_error_has_actionable_focus_detail(self):
        rid = self.submit(); self.broker.TakeInitialLayout(queries.SOURCE)
        state = self.complete(rid, active_uuid=self.uuids[0])
        self.assertIn('Preferred focus did not verify', state['detail'])
        self.assertIn(self.uuids[1], state['detail'])


    def test_single_raise_requires_capability_and_one_owned_over_window(self):
        payload=dict(entries=[dict(registration_request_id=self.ids[0],layer='over')],single_raise=True)
        with self.assertRaises(self.module.dbus.DBusException):self.broker.SubmitInitialLayout(json.dumps(payload))
        self.broker.single_raise_protocol=1
        for change in (dict(single_raise=False),dict(single_raise=1),dict(entries=[dict(registration_request_id=self.ids[0],layer='panel')])):
            with self.assertRaises(self.module.dbus.DBusException):self.broker.SubmitInitialLayout(json.dumps(dict(payload,**change)))
        rid=self.broker.SubmitInitialLayout(json.dumps(payload))
        claim=json.loads(self.broker.TakeInitialLayout(queries.SOURCE));self.assertTrue(claim['single_raise'])
        state=self.complete(rid,raise_order=[self.uuids[1],self.uuids[0]])
        self.assertEqual(state['state'],'SUCCEEDED')

    def test_singleton_cohort_order_alone_is_not_proof_of_raising(self):
        self.broker.single_raise_protocol=1
        for evidence in (None,[self.uuids[0]],[self.uuids[0],self.uuids[1]],
                         [self.uuids[1],self.uuids[0],self.uuids[0]]):
            rid=self.broker.SubmitInitialLayout(json.dumps(dict(single_raise=True,
                entries=[dict(registration_request_id=self.ids[0],layer='over')])))
            self.broker.TakeInitialLayout(queries.SOURCE)
            state=self.complete(rid,raise_order=evidence)
            self.assertEqual(state['state'],'FAILED')
            self.assertEqual(state['stacking'],'failed')

    def test_single_raise_cannot_hide_existing_peer_geometry_changes(self):
        self.broker.single_raise_protocol=1
        rid=self.broker.SubmitInitialLayout(json.dumps(dict(single_raise=True,
            entries=[dict(registration_request_id=self.ids[0],layer='over')])))
        self.broker.TakeInitialLayout(queries.SOURCE)
        self.broker.observed_windows[self.uuids[1]]['geometry']['x']+=1
        state=self.complete(rid,raise_order=[self.uuids[1],self.uuids[0]])
        self.assertEqual(state['state'],'FAILED')


for _name in dir(queries.ReadOnlyManagedQueryTests):
    if _name.startswith('test_') and _name not in InitialLayoutBrokerTests.__dict__:
        setattr(InitialLayoutBrokerTests, _name, None)
