#!/usr/bin/env python3
"""Headless Step 1.3a broker tests; no graphical session or service started."""
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


BROKER_FILE = Path(__file__).resolve().parents[1] / 'libexec/joetoo-kwind'
WINDOW_ID = 'd848c4c9-64ed-48bf-b083-40230314d5ab'


def load_broker_without_real_dbus():
    """Stub only import-time D-Bus/GLib symbols; test the real broker methods."""
    dbus = types.ModuleType('dbus')
    service = types.ModuleType('dbus.service')
    loop_module = types.ModuleType('dbus.mainloop')
    glib_module = types.ModuleType('dbus.mainloop.glib')
    gi_module = types.ModuleType('gi')
    gi_repository = types.ModuleType('gi.repository')

    class FakeException(Exception):
        def __init__(self, message='', name=None):
            super().__init__(message)
            self.name = name

    class FakeObject:
        def __init__(self, *args):
            pass

    service.Object = FakeObject
    service.method = lambda *args, **kwargs: (lambda fn: fn)
    dbus.DBusException = FakeException
    dbus.service = service
    glib_module.DBusGMainLoop = lambda **kwargs: None
    gi_repository.GLib = types.SimpleNamespace(SOURCE_REMOVE=False)

    replacements = {'dbus': dbus, 'dbus.service': service,
                    'dbus.mainloop': loop_module,
                    'dbus.mainloop.glib': glib_module,
                    'gi': gi_module, 'gi.repository': gi_repository}
    spec = importlib.util.spec_from_loader(
        'kwind_observer_test', SourceFileLoader('kwind_observer_test', str(BROKER_FILE)))
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, replacements):
        spec.loader.exec_module(module)
    return module


def observation(event='added', uuid=WINDOW_ID, x=100,
                caption='SSH session title (hint only)', desktops=None):
    """Simulate a JSON observation from the KWin resident, not a managed ID."""
    return json.dumps({'event': event, 'window': {
        'uuid': uuid, 'pid': 42, 'resource_class': 'konsole',
        'resource_name': 'konsole', 'desktop_file': 'org.kde.konsole',
        'caption': caption,
        'on_all_desktops': False, 'desktops': [3] if desktops is None else desktops,
        'geometry': {'x': x, 'y': 80, 'width': 850, 'height': 700}
    }})


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())

    def test_existing_added_and_changed_share_identity(self):
        self.broker.ObserveWindow(observation('existing'))
        self.broker.ObserveWindow(observation('added'))
        self.broker.ObserveWindow(observation('changed', x=175))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual(len(data['windows']), 1)
        self.assertEqual(data['windows'][0]['uuid'], WINDOW_ID)
        self.assertEqual(data['windows'][0]['geometry']['x'], 175)
        self.assertEqual([x['event'] for x in data['events']],
                         ['existing', 'added', 'changed'])
        self.assertIsNone(self.broker.request)
        self.assertFalse(hasattr(self.broker, 'managed_windows'))

    def test_removed_deletes_current_but_preserves_last_snapshot(self):
        self.broker.ObserveWindow(observation('added', x=123))
        self.broker.ObserveWindow(observation('removed', x=123))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual(data['windows'], [])
        self.assertEqual(data['events'][-1]['event'], 'removed')
        self.assertEqual(data['events'][-1]['window']['geometry']['x'], 123)
        self.assertEqual(data['events'][-1]['window']['uuid'], WINDOW_ID)
        self.assertEqual(data['events'][-1]['window_uuid'], WINDOW_ID)
        self.assertEqual(data['changes'], [])

    def test_invalid_uuid_and_field_shapes_rejected(self):
        for malformed in [observation(uuid='not-a-uuid'),
                          observation(event='close'),
                          '{}', 'not json',
                          observation().replace('"width": 850', '"width": false')]:
            with self.subTest(payload=malformed):
                with self.assertRaises(self.module.dbus.DBusException):
                    self.broker.ObserveWindow(malformed)
        self.assertEqual(json.loads(self.broker.ListObserved())['windows'], [])

    def test_uppercase_braced_uuid_normalized(self):
        self.broker.ObserveWindow(observation(uuid='{' + WINDOW_ID.upper() + '}'))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual(data['windows'][0]['uuid'], WINDOW_ID)

    def test_lifecycle_history_is_bounded_independently(self):
        # Historical lifecycle records have their own 128-event ceiling.
        for i in range(135):
            identifier = f'{i + 1:08x}-0000-4000-8000-000000000001'
            self.broker.ObserveWindow(observation('added', uuid=identifier))
            self.broker.ObserveWindow(observation('removed', uuid=identifier))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual(len(data['lifecycle_events']), 128)
        self.assertEqual(len(data['events']), 128)
        self.assertEqual(data['changes'], [])
        self.assertEqual(data['windows'], [])
        self.assertEqual(data['lifecycle_events'][-1]['event'], 'removed')
        ids = [record['event_id'] for record in data['events']]
        self.assertEqual(ids, sorted(set(ids)))

    def test_hundreds_of_drag_updates_do_not_evict_lifecycle(self):
        self.broker.ObserveWindow(observation('added', x=10))
        for x in range(400):
            self.broker.ObserveWindow(observation('changed', x=x))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual([r['event'] for r in data['events']],
                         ['added', 'changed'])
        self.assertEqual(len(data['lifecycle_events']), 1)
        self.assertEqual(data['changes'][0]['change_count'], 400)
        self.assertEqual(data['changes'][0]['window_uuid'], WINDOW_ID)
        self.assertEqual(data['windows'][0]['geometry']['x'], 399)
        self.broker.ObserveWindow(observation('removed', x=399))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual(data['windows'], [])
        self.assertEqual(data['changes'], [])  # no stale per-window cache
        self.assertEqual([r['event'] for r in data['events']],
                         ['added', 'removed'])
        self.assertEqual(data['events'][-1]['window']['geometry']['x'], 399)
        self.assertLess(data['events'][0]['event_id'],
                        data['events'][-1]['event_id'])

    def test_interleaved_windows_coalesce_by_uuid(self):
        other = 'd848c4c9-64ed-48bf-b083-40230314d5ac'
        self.broker.ObserveWindow(observation('added', uuid=WINDOW_ID))
        self.broker.ObserveWindow(observation('added', uuid=other))
        for i in range(20):
            self.broker.ObserveWindow(observation('changed', uuid=WINDOW_ID, x=i))
            self.broker.ObserveWindow(observation('changed', uuid=other, x=100+i))
        data = json.loads(self.broker.ListObserved())
        changes = {r['window_uuid']: r for r in data['changes']}
        self.assertEqual(set(changes), {WINDOW_ID, other})
        self.assertEqual(changes[WINDOW_ID]['change_count'], 20)
        self.assertEqual(changes[other]['change_count'], 20)
        self.assertEqual(changes[WINDOW_ID]['window']['geometry']['x'], 19)
        self.assertEqual(changes[other]['window']['geometry']['x'], 119)
        self.assertEqual(len(data['lifecycle_events']), 2)
        self.assertEqual(len({r['uuid'] for r in data['windows']}), 2)

    def test_non_geometry_changes_and_refresh_deduplication(self):
        self.broker.ObserveWindow(observation('existing'))
        self.broker.ObserveWindow(observation('existing'))
        self.broker.ObserveWindow(observation('changed',
                                               caption='Renamed', desktops=[1, 2]))
        self.broker.ObserveWindow(observation('existing',
                                               caption='Renamed', desktops=[1, 2]))
        data = json.loads(self.broker.ListObserved())
        self.assertEqual([r['event'] for r in data['events']],
                         ['existing', 'changed'])
        self.assertEqual(data['windows'][0]['caption'], 'Renamed')
        self.assertEqual(data['windows'][0]['desktops'], [1, 2])
        self.assertEqual(data['changes'][0]['window']['caption'], 'Renamed')
        self.assertIsNone(self.broker.request)
        self.assertFalse(hasattr(self.broker, 'managed_windows'))

    def test_old_move_contract_still_works(self):
        request_id = self.broker.Submit(3, 100, 80, 850, 700)
        payload = json.loads(self.broker.Take())
        self.assertEqual(payload['id'], request_id)
        self.broker.Complete(request_id, 'OK', 'unchanged method contract')
        self.assertEqual(self.broker.Status(request_id),
                         'OK unchanged method contract')


if __name__ == '__main__':
    unittest.main()
