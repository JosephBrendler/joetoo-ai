#!/usr/bin/env python3
"""Step 1.3a.2: atomic inventory and stale-message tests (headless only)."""
import json
import unittest
from unittest.mock import patch

from test_step1_3a import (WINDOW_ID, load_broker_without_real_dbus,
                           observation)

OTHER = "e848c4c9-64ed-48bf-b083-40230314d5ac"


def event(kind, source, revision, uuid=WINDOW_ID, x=100):
    message = json.loads(observation(kind, uuid=uuid, x=x))
    message.update(source=source, revision=revision)
    return json.dumps(message)


def inventory(source, revision, *uuids):
    windows = [json.loads(observation(uuid=id))["window"] for id in uuids]
    return json.dumps({"source": source, "revision": revision, "windows": windows})


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.module = load_broker_without_real_dbus()
        self.broker = self.module.Broker(object())

    def state(self):
        return json.loads(self.broker.ListObserved())

    def test_inventory_replaces_stale_windows_without_fake_removal(self):
        self.broker.ObserveWindow(event("added", "resident-A", 1))
        self.broker.ObserveWindow(event("added", "resident-A", 2, OTHER))
        self.broker.SyncInventory(inventory("resident-A", 3, WINDOW_ID))
        data = self.state()
        self.assertEqual([w["uuid"] for w in data["windows"]], [WINDOW_ID])
        self.assertTrue(data["sync"]["complete"])
        self.assertEqual(data["sync"]["revision"], 3)
        # Missing from a snapshot is not a confirmed KWin windowRemoved event.
        self.assertNotIn("removed", [r["event"] for r in data["events"]])
        self.broker.SyncInventory(inventory("resident-A", 4, WINDOW_ID))
        self.assertEqual(len(self.state()["lifecycle_events"]), 2)

    def test_later_event_updates_and_older_event_does_not_rollback(self):
        self.broker.SyncInventory(inventory("resident-A", 10, WINDOW_ID))
        self.broker.ObserveWindow(event("changed", "resident-A", 12, x=220))
        self.broker.ObserveWindow(event("changed", "resident-A", 11, x=110))
        self.broker.SyncInventory(inventory("resident-A", 9))
        self.assertEqual(self.state()["windows"][0]["geometry"]["x"], 220)
        self.assertEqual(self.state()["changes"][0]["change_count"], 1)
        self.broker.ObserveWindow(event("removed", "resident-A", 13, x=220))
        self.assertEqual(self.state()["windows"], [])
        self.assertEqual(self.state()["changes"], [])

    def test_new_resident_source_replaces_old_without_ownership(self):
        self.broker.SyncInventory(inventory("old", 1, WINDOW_ID))
        self.broker.SyncInventory(inventory("new", 1, OTHER))
        self.broker.ObserveWindow(event("added", "old", 2, WINDOW_ID))
        self.assertEqual([w["uuid"] for w in self.state()["windows"]], [OTHER])
        self.broker.ObserveWindow(event("changed", "new", 2, OTHER, x=333))
        self.assertEqual(self.state()["windows"][0]["geometry"]["x"], 333)
        self.assertFalse(hasattr(self.broker, "managed_windows"))

    def test_bad_snapshot_does_not_partially_mutate_state(self):
        self.broker.SyncInventory(inventory("resident-A", 1, WINDOW_ID))
        before = self.state()
        duplicate = inventory("resident-A", 2, WINDOW_ID, WINDOW_ID)
        malformed = json.loads(inventory("resident-A", 2, WINDOW_ID, OTHER))
        malformed["windows"][1]["geometry"]["width"] = "invalid"
        for payload in (duplicate, json.dumps(malformed), "not-json"):
            with self.subTest(payload=payload):
                with self.assertRaises(self.module.dbus.DBusException):
                    self.broker.SyncInventory(payload)
                self.assertEqual(self.state(), before)

    def test_coordinator_refreshes_reused_resident_only(self):
        coordinator = self.module.ResidentCoordinator(object())
        with patch.object(coordinator, "ensure_loaded", return_value="reused"), \
             patch.object(coordinator, "request_inventory_refresh") as refresh:
            coordinator._attempt()
            refresh.assert_called_once_with()
        with patch.object(coordinator, "ensure_loaded", return_value="started"), \
             patch.object(coordinator, "request_inventory_refresh") as refresh:
            coordinator._attempt()
            refresh.assert_not_called()


    def test_broker_retries_until_inventory_acknowledged(self):
        coordinator = self.module.ResidentCoordinator(object(), self.broker)
        with patch.object(coordinator, "ensure_loaded", return_value="reused"), \
             patch.object(coordinator, "request_inventory_refresh"), \
             patch.object(coordinator, "_schedule") as schedule:
            coordinator._attempt()
            schedule.assert_called_once_with(1000)
            self.broker.SyncInventory(inventory("resident-A", 1, WINDOW_ID))
            schedule.reset_mock()
            coordinator._attempt()
            schedule.assert_not_called()


if __name__ == "__main__":
    unittest.main()
