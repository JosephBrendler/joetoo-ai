#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4a headless registry-contract tests; no D-Bus or desktop needed."""

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import TestCase


REGISTRY_FILE = Path(__file__).resolve().parents[1] / "libexec/joetoo_kwin_registry.py"
FIRST = "d848c4c9-64ed-48bf-b083-40230314d5ab"
SECOND = "d848c4c9-64ed-48bf-b083-40230314d5ac"
THIRD = "d848c4c9-64ed-48bf-b083-40230314d5ad"
SOURCE = "resident-test-source"


def load_registry():
    """Load the standalone model without modifying the installed PYTHONPATH."""
    spec = importlib.util.spec_from_loader(
        "joetoo_kwin_registry_step1_4a", SourceFileLoader(
            "joetoo_kwin_registry_step1_4a", str(REGISTRY_FILE)))
    module = importlib.util.module_from_spec(spec)
    # dataclasses expects the module being constructed to be in sys.modules.
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RegistryTests(TestCase):
    def setUp(self):
        self.module = load_registry()
        self.registry = self.module.WindowRegistry()

    def arm(self, request_id="req-001", pid=41, *, baseline=(), run_id="run-001"):
        self.registry.begin_launch(
            request_id, source=SOURCE, synchronized=True, baseline=baseline,
            recipe={"desktop": 3, "slot": 1, "program": "konsole",
                    "mode": "ssh", "target": "test.example"}, run_id=run_id)
        self.registry.mark_running(request_id, pid)

    def evidence(self, request_id="req-001", identifier=FIRST, pid=41, **extra):
        result = {"state": "MATCHED", "request_id": request_id,
                  "window_uuid": identifier, "evidence": "pid",
                  "candidate_history_complete": True, "pid": pid}
        result.update(extra)
        return result

    def window(self, identifier=FIRST, pid=41):
        return {"uuid": identifier, "pid": pid, "caption": "Konsole",
                "geometry": {"x": 100, "y": 80, "width": 850, "height": 700}}

    def register(self, request_id="req-001", identifier=FIRST, pid=41, **kwargs):
        result = kwargs.pop("result", self.evidence(request_id, identifier, pid))
        inventory = kwargs.pop("inventory", {identifier: self.window(identifier, pid)})
        return self.registry.register_match(
            request_id, result, current_windows=inventory,
            source=kwargs.pop("source", SOURCE),
            synchronized=kwargs.pop("synchronized", True))

    def test_intention_is_not_registration(self):
        self.arm()
        self.assertEqual(self.registry.managed_windows, {})
        self.assertEqual(self.registry.requests["req-001"].state, "running")
        self.assertIsNone(self.registry.get_window(FIRST))

    def test_one_to_one_alias_and_uuid_and_multiple_windows(self):
        self.arm()
        first = self.register()
        self.arm("req-002", pid=42, run_id="run-001")
        second = self.register("req-002", SECOND, 42)
        self.assertEqual((first.managed_id, second.managed_id), ("win-001", "win-002"))
        self.assertEqual(self.registry.uuid_by_managed_id["win-001"], FIRST)
        self.assertEqual(self.registry.get_window("win-002").window_uuid, SECOND)
        self.assertEqual(self.registry.get_window(FIRST).managed_id, "win-001")
        self.assertEqual(len(self.registry.managed_windows), 2)
        self.assertEqual(self.registry.requests["req-001"].state, "succeeded")

    def test_registration_rejects_duplicate_uuid_without_mutating(self):
        self.arm()
        self.register()
        self.arm("req-002", pid=41)
        with self.assertRaises(self.module.RegistryError):
            self.register("req-002", FIRST)
        self.assertEqual(len(self.registry.managed_windows), 1)
        self.assertEqual(len(self.registry.uuid_by_managed_id), 1)
        # A rejected attempt consumes no alias. The next valid match gets win-002.
        self.registry.finish_failed("req-002", "failed")
        self.arm("req-003", pid=43)
        self.assertEqual(self.register("req-003", THIRD, 43).managed_id, "win-002")

    def test_unmatched_and_ambiguous_requests_never_register(self):
        for i, state in enumerate(("timeout", "ambiguous", "failed"), 1):
            rid = f"req-{i:03d}"
            self.arm(rid)
            self.registry.finish_failed(rid, state)
            self.assertEqual(self.registry.requests[rid].state, state)
        self.assertEqual(self.registry.managed_windows, {})

    def test_preexisting_window_is_not_eligible(self):
        self.arm(baseline=[FIRST])
        with self.assertRaises(self.module.RegistryError):
            self.register()
        self.assertEqual(self.registry.managed_windows, {})

    def test_incomplete_history_or_non_pid_match_is_not_eligible(self):
        self.arm()
        for altered in (
            {"candidate_history_complete": False},
            {"evidence": "class_only"},
            {"evidence": "class_title_hint"},
            {"state": "AMBIGUOUS"},
            {"request_id": "another-request"},
            {"pid": 412},
        ):
            with self.subTest(altered=altered):
                with self.assertRaises(self.module.RegistryError):
                    self.register(result=self.evidence(**altered))
                self.assertEqual(self.registry.managed_windows, {})

    def test_source_change_and_missing_current_window_fail_closed(self):
        self.arm()
        with self.assertRaises(self.module.RegistryError):
            self.register(source="new-resident")
        with self.assertRaises(self.module.RegistryError):
            self.register(synchronized=False)
        with self.assertRaises(self.module.RegistryError):
            self.register(inventory={})
        with self.assertRaises(self.module.RegistryError):
            self.register(inventory={FIRST: self.window(FIRST, 987)})
        self.assertEqual(self.registry.managed_windows, {})

    def test_serialized_active_request_and_no_implicit_reuse(self):
        self.arm()
        with self.assertRaises(self.module.RegistryError):
            self.registry.begin_launch("req-002", source=SOURCE,
                                       synchronized=True, baseline=[], recipe={})
        with self.assertRaises(self.module.RegistryError):
            self.registry.mark_running("req-001", 50)
        self.register()
        with self.assertRaises(self.module.RegistryError):
            self.registry.finish_failed("req-001", "timeout")

    def test_exact_uuid_presence_changes_do_not_affect_other_windows(self):
        self.arm()
        self.register()
        self.arm("req-002", pid=42)
        self.register("req-002", SECOND, 42)
        self.assertTrue(self.registry.set_presence(FIRST, "missing"))
        self.assertEqual(self.registry.get_window(FIRST).presence, "missing")
        self.assertEqual(self.registry.get_window(SECOND).presence, "present")
        self.assertFalse(self.registry.set_presence(THIRD, "missing"))
        with self.assertRaises(self.module.RegistryError):
            self.registry.set_presence(FIRST, "present", self.window(FIRST))

    def test_placement_is_not_registration_or_connection(self):
        self.arm()
        self.register()
        self.registry.set_placement(FIRST, "pending")
        self.registry.set_placement(FIRST, "failed")
        record = self.registry.get_window(FIRST)
        self.assertEqual(record.placement, "failed")
        self.assertEqual(record.presence, "present")
        self.assertEqual(record.connection, "not_attempted")
        with self.assertRaises(self.module.RegistryError):
            self.registry.set_placement(FIRST, "succeeded")

    def test_unreachable_ssh_keeps_window_but_not_a_session(self):
        self.arm()
        self.register()
        with self.assertRaises(self.module.RegistryError):
            self.registry.set_connection(FIRST, "connected")
        self.registry.set_connection(FIRST, "unavailable", application_reported=True)
        record = self.registry.get_window("win-001")
        self.assertEqual(record.connection, "unavailable")
        self.assertEqual(record.application_sessions, [])
        self.assertEqual(record.presence, "present")

    def test_mutable_records_do_not_leak_through_lookup(self):
        self.arm()
        self.register()
        external = self.registry.get_window("win-001")
        external.recipe["target"] = "tampered.example"
        external.observation["geometry"]["x"] = -1
        self.assertEqual(self.registry.get_window(FIRST).recipe["target"], "test.example")
        self.assertEqual(self.registry.get_window(FIRST).observation["geometry"]["x"], 100)

    def test_bounded_completed_results_not_an_unbounded_run_history(self):
        registry = self.module.WindowRegistry(completed_limit=2)
        for i in range(3):
            rid = f"req-{i+1:03d}"
            registry.begin_launch(rid, source=SOURCE, synchronized=True,
                                  baseline=[], recipe={}, run_id="run-001")
            registry.finish_failed(rid, "timeout")
        self.assertEqual(sorted(registry.requests), ["req-002", "req-003"])
        self.assertFalse(hasattr(registry, "runs"))

    def test_invalid_identifiers_and_states(self):
        with self.assertRaises(self.module.RegistryError):
            self.registry.begin_launch("req-001", source="", synchronized=False,
                                       baseline=[], recipe={})
        self.arm()
        with self.assertRaises(self.module.RegistryError):
            self.registry.finish_failed("req-001", "succeeded")
        self.register()
        with self.assertRaises(self.module.RegistryError):
            self.registry.set_presence(FIRST, "closed")
        with self.assertRaises(self.module.RegistryError):
            self.registry.set_placement(FIRST, "closed")
