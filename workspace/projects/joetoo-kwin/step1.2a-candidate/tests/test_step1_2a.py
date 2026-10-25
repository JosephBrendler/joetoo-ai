#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Headless Step 1.2a protocol, lifecycle and OpenRC service contract checks."""

import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DAEMON = ROOT / "libexec" / "joetoo-kwind"
SERVICE = ROOT / "user-init.d" / "joetoo-kwind"


def load_with_fake_dbus():
    fake_dbus = types.ModuleType("dbus")
    service = types.ModuleType("dbus.service")
    mainloop = types.ModuleType("dbus.mainloop")
    mainloop_glib = types.ModuleType("dbus.mainloop.glib")
    gi = types.ModuleType("gi")
    repository = types.ModuleType("gi.repository")

    class DbusException(Exception):
        def __init__(self, message, name=None):
            super().__init__(message)
            self.name = name

    class Object:
        def __init__(self, bus_name, object_path):
            self.path = object_path

    class BusName:
        def __init__(self, name, bus, do_not_queue):
            self.name = name

    class MainLoop:
        def __init__(self):
            self.quit_called = False
            self.run_called = False

        def quit(self):
            self.quit_called = True

        def run(self):
            self.run_called = True

    class FakeGLib:
        PRIORITY_DEFAULT = 0
        SOURCE_REMOVE = False
        signals = []

        @staticmethod
        def unix_signal_add(priority, signum, callback):
            FakeGLib.signals.append((signum, callback))
            return len(FakeGLib.signals)

    FakeGLib.MainLoop = MainLoop

    class SessionBus:
        pass

    fake_dbus.DBusException = DbusException
    fake_dbus.SessionBus = SessionBus
    fake_dbus.service = service
    service.Object = Object
    service.BusName = BusName
    service.method = lambda *a, **kw: lambda f: f
    mainloop.glib = mainloop_glib
    mainloop_glib.DBusGMainLoop = lambda set_as_default: None
    gi.repository = repository
    repository.GLib = FakeGLib
    modules = {
        "dbus": fake_dbus, "dbus.service": service,
        "dbus.mainloop": mainloop, "dbus.mainloop.glib": mainloop_glib,
        "gi": gi, "gi.repository": repository,
    }
    with patch.dict(sys.modules, modules):
        loader = importlib.machinery.SourceFileLoader("step1_2a_kwind", str(DAEMON))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
    return module, FakeGLib


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.module, self.glib = load_with_fake_dbus()
        self.broker = self.module.Broker(object())

    def test_legacy_protocol_move_and_completion(self):
        rid = self.broker.Submit(3, 100, 80, 850, 700)
        req = json.loads(self.broker.Take())
        self.assertEqual(req["id"], rid)
        self.assertEqual(req["desktop"], 3)
        self.broker.Complete(rid, "OK", "observed")
        self.assertEqual(self.broker.Status(rid), "OK observed")

    def test_launch_class_and_single_flight(self):
        rid = self.broker.SubmitLaunch("konsole", 3, 100, 80, 850, 700)
        self.assertFalse(self.broker.TakeLaunch("other", "other.desktop"))
        with self.assertRaises(self.module.dbus.DBusException):
            self.broker.Submit(1, 0, 0, 500, 400)
        req = json.loads(self.broker.TakeLaunch("konsole", "org.kde.konsole"))
        self.assertEqual(req["id"], rid)

    def test_no_spawn_and_signal_registration(self):
        self.assertFalse(hasattr(self.broker, "launch_window"))
        # Validate main's signal wiring without starting a real user bus.
        with patch.object(self.module, "validate_session_environment"), patch("builtins.print"):
            self.assertEqual(self.module.main(), 0)
        signals = [n for n, _ in self.glib.signals]
        self.assertEqual(signals, [self.module.signal.SIGTERM, self.module.signal.SIGINT])
        for _, cb in self.glib.signals:
            self.assertIs(cb(), False)

    def test_preflight_rejects_root_and_untrusted_runtime(self):
        with patch.object(self.module.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "root"):
                self.module.validate_session_environment()
        with patch.object(self.module.os, "geteuid", return_value=1234):
            with patch.dict(os.environ, {"XDG_RUNTIME_DIR": "relative"}):
                with self.assertRaisesRegex(RuntimeError, "absolute"):
                    self.module.validate_session_environment()


class ServiceTests(unittest.TestCase):
    def test_shell_parses_and_preserves_default_supervisor(self):
        subprocess.run(["sh", "-n", str(SERVICE)], check=True)
        data = SERVICE.read_text()
        for fragment in (
            "#!/sbin/openrc-run", 'supervisor="supervise-daemon"',
            'rc_cgroup_cleanup="NO"', "respawn_delay=10",
            "respawn_max=5", "respawn_period=120",
            "start_pre()", "XDG_RUNTIME_DIR", "checkpath -d -m 0700",
        ):
            self.assertIn(fragment, data)
        for forbidden in ("kill 0", "pkill ", "killall ", "command_background=", "stop() {", "start() {"):
            self.assertNotIn(forbidden, data)

    def test_start_pre_fails_without_runtime_directory(self):
        shell = '''
            id() { printf '1234\\n'; }
            eerror() { :; }
            stat() { printf '1234\\n'; }
            checkpath() { :; }
            . "$1"
            start_pre
        '''
        env = os.environ.copy()
        env.pop("XDG_RUNTIME_DIR", None)
        env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/tmp/test-nonexistent"
        p = subprocess.run(["sh", "-c", shell, "shell", str(SERVICE)], env=env)
        self.assertNotEqual(p.returncode, 0)

    def test_start_pre_accepts_owned_runtime_and_never_launches_apps(self):
        shell = '''
            id() { printf '1234\\n'; }
            stat() { printf '1234\\n'; }
            eerror() { printf 'failed\\n' >&2; }
            checkpath() { :; }
            . "$1"
            start_pre
        '''
        with tempfile.TemporaryDirectory() as root:
            env = os.environ.copy()
            env["XDG_RUNTIME_DIR"] = root
            env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/tmp/test-nonexistent"
            subprocess.run(["sh", "-c", shell, "shell", str(SERVICE)], env=env,
                           check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
