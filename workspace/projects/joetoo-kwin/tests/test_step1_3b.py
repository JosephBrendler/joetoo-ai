#!/usr/bin/env python3
"""Headless, non-destructive Step 1.3b.1 correlation-probe regression tests."""
import json
from unittest import TestCase
from unittest.mock import patch
from test_step1_3a import load_broker_without_real_dbus, observation, WINDOW_ID

OTHER = 'd848c4c9-64ed-48bf-b083-40230314d5ac'
THIRD = 'd848c4c9-64ed-48bf-b083-40230314d5ad'
SOURCE = 'kwin-resident-test-01'


class CorrelationProbeTests(TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())
        self.revision = 1
        self.clock = [100.0]
        self.clock_patch = patch.object(self.module.time, 'monotonic',
                                        side_effect=lambda: self.clock[0])
        self.clock_patch.start()
        self.addCleanup(self.clock_patch.stop)

    def sync(self, windows=None, source=SOURCE):
        self.revision += 1
        if windows is None:
            windows = []
        self.broker.SyncInventory(json.dumps({
            'source': source, 'revision': self.revision, 'windows': windows}))

    def add(self, identifier, pid=42, caption='New window', klass='konsole'):
        self.revision += 1
        data = json.loads(observation('added', uuid=identifier, caption=caption))
        data['window']['pid'] = pid
        data['window']['resource_class'] = klass
        # The mock observation() defaults to Konsole's desktop ID; keep the
        # synthetic class and desktop-file evidence mutually consistent.
        data['window']['desktop_file'] = 'org.kde.' + klass
        data.update(source=SOURCE, revision=self.revision)
        self.broker.ObserveWindow(json.dumps(data))

    def begin(self, klass='konsole', token='', pid=42):
        rid = self.broker.BeginCorrelation(klass, token)
        if pid is not None:
            self.broker.SetCorrelationPid(rid, pid)
        return rid

    def poll(self, rid):
        return json.loads(self.broker.PollCorrelation(rid))

    def test_requires_synchronized_inventory(self):
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.BeginCorrelation('konsole', '')

    def test_new_exact_pid_uuid_is_matched_after_quiet_period(self):
        self.sync()
        rid = self.begin(pid=12345)
        self.add(WINDOW_ID, pid=12345)
        self.assertEqual(self.poll(rid)['state'], 'PENDING')
        self.clock[0] += 0.6
        result = self.poll(rid)
        self.assertEqual(result['state'], 'MATCHED')
        self.assertEqual(result['window_uuid'], WINDOW_ID)
        self.assertEqual(result['evidence'], 'pid')
        self.assertFalse(hasattr(self.broker, 'managed_windows'))

    def test_existing_same_pid_is_not_reused_for_new_launch(self):
        existing = json.loads(observation('existing', uuid=WINDOW_ID))['window']
        self.sync([existing])
        rid = self.begin(pid=42)
        self.assertEqual(self.poll(rid)['pid_candidates'], [])
        self.add(OTHER, pid=42)
        self.poll(rid)
        self.clock[0] += 0.6
        self.assertEqual(self.poll(rid)['window_uuid'], OTHER)

    def test_unrelated_same_class_pid_not_adopted(self):
        self.sync()
        rid = self.begin(pid=500)
        self.add(WINDOW_ID, pid=42)
        self.clock[0] += 15.1
        result = self.poll(rid)
        self.assertEqual(result['state'], 'TIMEOUT')
        self.assertEqual(result['pid_candidates'], [])

    def test_title_token_is_a_hint_not_ownership_evidence(self):
        self.sync()
        rid = self.begin(token='unique-launch-token', pid=500)
        self.add(WINDOW_ID, pid=999, caption='unique-launch-token — Konsole')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual(result['title_hints'], [WINDOW_ID])
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'TIMEOUT')

    def test_two_new_windows_same_pid_are_ambiguous(self):
        self.sync()
        rid = self.begin(pid=42)
        self.add(WINDOW_ID, pid=42)
        self.add(OTHER, pid=42)
        result = self.poll(rid)
        self.assertEqual(result['state'], 'AMBIGUOUS')
        self.assertEqual(result['candidates'], [WINDOW_ID, OTHER])

    def test_changed_only_is_not_proof_of_new_window(self):
        self.sync()
        rid = self.begin(pid=42)
        self.revision += 1
        data = json.loads(observation('changed', uuid=WINDOW_ID))
        data.update(source=SOURCE, revision=self.revision)
        self.broker.ObserveWindow(json.dumps(data))
        self.assertEqual(self.poll(rid)['pid_candidates'], [])

    def test_restarted_resident_invalidates_in_flight_request(self):
        self.sync()
        rid = self.begin(pid=42)
        self.revision = 2
        self.sync(source='new-resident-test-02')
        self.assertEqual(self.poll(rid)['state'], 'STALE_SOURCE')

    def test_bad_pid_and_second_pid_are_rejected(self):
        self.sync()
        rid = self.begin(pid=None)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetCorrelationPid(rid, 0)
        self.broker.SetCorrelationPid(rid, 42)
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.SetCorrelationPid(rid, 43)

    def test_same_class_different_pid_cannot_trigger_ambiguous(self):
        self.sync()
        rid = self.begin(pid=42)
        self.add(WINDOW_ID, pid=987)
        self.add(OTHER, pid=42)
        self.poll(rid)
        self.clock[0] += 0.6
        self.assertEqual(self.poll(rid)['window_uuid'], OTHER)

    def test_second_active_probe_refused(self):
        self.sync()
        self.begin(pid=42)
        with self.assertRaises(self.module.dbus.DBusException):
            self.begin(pid=42)


    # Step 1.3b.2: these are *diagnostic candidates*, never registered or
    # accepted as ownership evidence based solely on timing and class.
    def test_delegated_chrome_timeout_reports_class_candidate(self):
        self.sync()
        rid = self.begin(klass='google-chrome', pid=1818083)
        self.add(WINDOW_ID, pid=5843, klass='google-chrome',
                 caption='about:blank - Google Chrome')
        pending = self.poll(rid)
        self.assertEqual(pending['state'], 'PENDING')
        self.assertEqual(pending['pid_candidates'], [])
        self.assertTrue(pending['candidate_history_complete'])
        self.assertEqual(len(pending['class_candidates']), 1)
        candidate = pending['class_candidates'][0]
        self.assertEqual(candidate, {
            'window_uuid': WINDOW_ID, 'pid': 5843, 'event_id': 1,
            'currently_observed': True, 'evidence': 'class_only'})
        self.clock[0] += 15.1
        timeout = self.poll(rid)
        self.assertEqual(timeout['state'], 'TIMEOUT')
        self.assertEqual(timeout['class_candidates'], [candidate])
        self.assertFalse(hasattr(self.broker, 'managed_windows'))

    def test_class_candidates_include_multiple_new_windows_in_event_order(self):
        self.sync()
        rid = self.begin(klass='konsole', pid=700)
        self.add(WINDOW_ID, pid=701)
        self.add(OTHER, pid=700)
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual([x['window_uuid'] for x in result['class_candidates']],
                         [WINDOW_ID, OTHER])
        self.assertEqual([x['event_id'] for x in result['class_candidates']],
                         [1, 2])
        self.assertEqual([x['evidence'] for x in result['class_candidates']],
                         ['class_only', 'pid'])
        self.clock[0] += 0.6
        matched = self.poll(rid)
        self.assertEqual(matched['state'], 'MATCHED')
        self.assertEqual(matched['window_uuid'], OTHER)
        self.assertEqual(len(matched['class_candidates']), 2)

    def test_same_pid_ambiguity_still_reports_class_candidates(self):
        self.sync()
        rid = self.begin(pid=42)
        self.add(WINDOW_ID, pid=42)
        self.add(OTHER, pid=42)
        result = self.poll(rid)
        self.assertEqual(result['state'], 'AMBIGUOUS')
        self.assertEqual(result['candidates'], [WINDOW_ID, OTHER])
        self.assertEqual(len(result['class_candidates']), 2)
        self.assertEqual([x['evidence'] for x in result['class_candidates']],
                         ['pid', 'pid'])

    def test_closed_window_keeps_addition_identity_as_diagnostic_only(self):
        self.sync()
        rid = self.begin(pid=700)
        self.add(WINDOW_ID, pid=5843)
        self.revision += 1
        removed = json.loads(observation('removed', uuid=WINDOW_ID,
                                         caption='Last title'))
        removed['window']['pid'] = 5843
        removed.update(source=SOURCE, revision=self.revision)
        self.broker.ObserveWindow(json.dumps(removed))
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual(result['pid_candidates'], [])
        self.assertEqual(result['class_candidates'], [{
            'window_uuid': WINDOW_ID, 'pid': 5843, 'event_id': 1,
            'currently_observed': False, 'evidence': 'class_only'}])
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'TIMEOUT')

    def test_preexisting_and_wrong_class_windows_are_not_candidates(self):
        existing = json.loads(observation('existing', uuid=WINDOW_ID))['window']
        self.sync([existing])
        rid = self.begin(klass='konsole', pid=42)
        self.add(OTHER, pid=42, klass='dolphin')
        self.add(THIRD, pid=43, klass='konsole')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual([x['window_uuid'] for x in result['class_candidates']],
                         [THIRD])
        self.assertEqual(result['class_candidates'][0]['evidence'], 'class_only')

    def test_title_token_remains_a_hint_in_class_candidates(self):
        self.sync()
        rid = self.begin(token='run-token', pid=111)
        self.add(WINDOW_ID, pid=9070, caption='run-token — Konsole')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual(result['title_hints'], [WINDOW_ID])
        self.assertEqual(result['class_candidates'][0]['evidence'],
                         'class_title_hint')
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'TIMEOUT')

    def test_late_class_discovery_is_reported_without_fake_addition(self):
        self.sync()
        rid = self.begin(klass='konsole', pid=88)
        self.add(WINDOW_ID, pid=88, klass='unknown')
        self.assertEqual(self.poll(rid)['class_candidates'], [])
        self.revision += 1
        changed = json.loads(observation('changed', uuid=WINDOW_ID))
        changed['window']['pid'] = 88
        changed.update(source=SOURCE, revision=self.revision)
        self.broker.ObserveWindow(json.dumps(changed))
        result = self.poll(rid)
        self.assertEqual(result['class_candidates'][0]['event_id'], 1)
        self.assertEqual(result['class_candidates'][0]['evidence'], 'pid')

    def test_changed_only_event_does_not_produce_class_candidate(self):
        self.sync()
        rid = self.begin(pid=42)
        self.revision += 1
        changed = json.loads(observation('changed', uuid=WINDOW_ID))
        changed.update(source=SOURCE, revision=self.revision)
        self.broker.ObserveWindow(json.dumps(changed))
        self.assertEqual(self.poll(rid)['class_candidates'], [])

    def test_evicted_history_is_reported_as_incomplete(self):
        self.sync()
        rid = self.begin(pid=9)
        self.add(WINDOW_ID, pid=42)
        for index in range(129):
            other = f'{index + 1:08x}-0000-4000-8000-000000000001'
            self.add(other, pid=500, klass='dolphin')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'PENDING')
        self.assertFalse(result['candidate_history_complete'])
        self.assertEqual(result['class_candidates'], [])
        self.clock[0] += 15.1
        self.assertEqual(self.poll(rid)['state'], 'TIMEOUT')

    def test_incomplete_history_never_declares_single_pid_match(self):
        self.sync()
        rid = self.begin(pid=42)
        for index in range(129):
            other = f'{index + 1:08x}-0000-4000-8000-000000000001'
            self.add(other, pid=500, klass='dolphin')
        self.add(WINDOW_ID, pid=42)
        self.assertFalse(self.poll(rid)['candidate_history_complete'])
        self.clock[0] += 0.6
        self.assertEqual(self.poll(rid)['state'], 'PENDING')
        self.clock[0] += 15.0
        result = self.poll(rid)
        self.assertEqual(result['state'], 'TIMEOUT')
        self.assertFalse(result['candidate_history_complete'])
        self.assertEqual(result['pid_candidates'], [WINDOW_ID])

    def test_stale_source_does_not_mix_class_candidates(self):
        self.sync()
        rid = self.begin(pid=700)
        self.add(WINDOW_ID, pid=5843)
        self.revision = 2
        self.sync(source='another-resident')
        result = self.poll(rid)
        self.assertEqual(result['state'], 'STALE_SOURCE')
        self.assertEqual(result['class_candidates'], [])
        self.assertFalse(result['candidate_history_complete'])

    def test_terminal_result_keeps_snapshot_unchanged(self):
        self.sync()
        rid = self.begin(pid=700)
        self.add(WINDOW_ID, pid=5843)
        self.clock[0] += 15.1
        first = self.poll(rid)
        self.assertEqual(first['state'], 'TIMEOUT')
        self.add(OTHER, pid=5843)
        self.assertEqual(self.poll(rid), first)


if __name__ == '__main__':
    import unittest
    unittest.main()
