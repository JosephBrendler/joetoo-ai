"""Desktop API and path contracts with in-memory interfaces only."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_step1_5a_plan import ROOT

spec = importlib.util.spec_from_file_location('resources', ROOT / 'libexec/joetoo_kwin_launch_resources.py')
resources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resources)


class FakeDesktops(resources.Desktops):
    def __init__(self, count=2, limit=20, fail=False):
        self.owner = ':owner'
        self.ids = [str(i) for i in range(count)]
        self.limit = limit
        self.fail = fail
        self.calls = []
        self.manager = self

    def snapshot(self):
        return {'owner': self.owner, 'ids': list(self.ids), 'count': len(self.ids)}

    def append_desktop(self):
        self.calls.append(len(self.ids))
        if self.fail: raise ValueError('controlled API failure')
        if len(self.ids) < self.limit: self.ids.append(str(len(self.ids)))


class ResourceTests(unittest.TestCase):
    def test_existing_sparse_and_append_after_capacity_change(self):
        desktops = FakeDesktops()
        before = desktops.snapshot()
        self.assertEqual(desktops.ensure(2, before, True)['count'], 2)
        self.assertEqual(desktops.calls, [])
        desktops.ids += ['2', '3']  # Another actor appends during confirmation.
        self.assertEqual(desktops.ensure(7, before, True)['count'], 7)
        self.assertEqual(desktops.calls, [4, 5, 6])

    def test_limit_partial_and_api_failures_never_rollback(self):
        desktops = FakeDesktops(limit=3)
        before = desktops.snapshot()
        with patch.object(resources.time, 'monotonic', side_effect=range(100)):
            with self.assertRaisesRegex(ValueError, 'no progress'):
                desktops.ensure(5, before, True)
        self.assertEqual(len(desktops.ids), 3)
        broken = FakeDesktops(fail=True)
        with self.assertRaisesRegex(ValueError, 'API failure'):
            broken.ensure(4, broken.snapshot(), True)

    def test_verify_cannot_create_and_session_or_removal_stops(self):
        desktops = FakeDesktops()
        before = desktops.snapshot()
        with self.assertRaises(ValueError): desktops.ensure(3, before)
        self.assertEqual(desktops.calls, [])
        desktops.owner = ':changed'
        with self.assertRaises(ValueError): desktops.ensure(3, before, True)
        desktops.owner = ':owner'; desktops.ids.reverse()
        with self.assertRaises(ValueError): desktops.ensure(3, before, True)

    def test_local_directory_paths_are_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            directory = base / 'space $(not-a-command)'
            directory.mkdir()
            config = base / 'config.conf'
            with patch.dict('os.environ', {'HOME': tmp}):
                self.assertEqual(resources.local_path('', str(config)), tmp)
            for value in (str(directory), directory.name, str(directory) + '/'):
                self.assertEqual(resources.local_path(value, str(config)), str(directory))
            config.write_text('# a file, not a directory')
            for value in ('sftp://host/path', 'missing', 'bad\nname', 'bad\0name', str(config)):
                with self.subTest(value=value), self.assertRaises((ValueError, OSError)):
                    resources.local_path(value, str(config))

    def test_structured_api_inventory_validation_and_append_wire_type(self):
        from types import SimpleNamespace
        import sys
        api = SimpleNamespace()
        api.values = {'count': 2, 'desktops': [(0, 'a', 'One'), (1, 'b', 'Two')]}
        api.GetAll = lambda *args, **kwargs: api.values
        api.Introspect = lambda **kwargs: ('<node><interface name="' + resources.INTERFACE + '">'
            '<method name="createDesktop"><arg type="u" direction="in"/>'
            '<arg type="s" direction="in"/></method></interface></node>')
        calls = []
        api.createDesktop = lambda position, name, **kwargs: calls.append((position, name))
        owner = [':kwin']
        bus = SimpleNamespace(get_name_owner=lambda name: owner[0],
                              get_object=lambda name, path, **kwargs: api)
        fake = SimpleNamespace(Interface=lambda proxy, interface: proxy, UInt32=lambda value: value)
        with patch.dict(sys.modules, {'dbus': fake}):
            desktops = resources.Desktops(bus)
            self.assertEqual(desktops.snapshot()['ids'], ['a', 'b'])
            desktops.append_desktop()
            self.assertEqual(calls, [(0xffffffff, '')])
            api.values['desktops'] = [(0, 'a', 'One'), (2, 'b', 'Two')]
            with self.assertRaises(ValueError): desktops.snapshot()
            owner[0] = ':different'
            with self.assertRaisesRegex(ValueError, 'owner changed'): desktops.snapshot()
