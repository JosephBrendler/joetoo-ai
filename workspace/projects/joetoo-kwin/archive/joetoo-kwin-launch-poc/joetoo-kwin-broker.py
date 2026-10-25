#!/usr/bin/env python3
"""Experimental session-bus broker for KWin moves and new-window placement.

Single-flight only; deliberately not a production service.
"""

import json
import time
import uuid

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

BUS = "org.joetoo.KWinBridge"
PATH = "/org/joetoo/KWinBridge"
IFACE = BUS


def matches_class(expected, resource_class, desktop_file):
    """Accept either the advertised class or the final component of an app ID."""
    target = str(expected).strip().casefold()
    if not target:
        return False
    for actual in (resource_class, desktop_file):
        actual = str(actual).strip().casefold()
        if actual == target or actual.endswith("." + target):
            return True
    return False


class Broker(dbus.service.Object):
    def __init__(self, bus_name):
        super().__init__(bus_name, PATH)
        self.request = None

    def _submit(self, kind, desktop, x, y, width, height, app_class=""):
        # Single-flight. Reject overlapping requests rather than overwriting them.
        if (self.request is not None
                and self.request["state"] in ("PENDING", "RUNNING")
                and time.monotonic() - self.request["created"] < 20):
            raise dbus.DBusException("Previous request has not completed",
                                     name=IFACE + ".Busy")

        if not (1 <= desktop <= 256 and
                -32768 <= x <= 32768 and -32768 <= y <= 32768 and
                1 <= width <= 32768 and 1 <= height <= 32768):
            raise dbus.DBusException("Desktop, position, or size out of range",
                                     name=IFACE + ".BadArguments")

        if kind == "launch" and not (0 < len(app_class) <= 128):
            raise dbus.DBusException("Expected application class is required",
                                     name=IFACE + ".BadArguments")

        self.request = {
            "id": uuid.uuid4().hex,
            "kind": kind,
            "desktop": int(desktop),
            "x": int(x), "y": int(y),
            "width": int(width), "height": int(height),
            "app_class": str(app_class),
            "state": "PENDING", "detail": "",
            "created": time.monotonic(),
        }
        return self.request["id"]

    def _take(self, kind):
        r = self.request
        if r is None or r["state"] != "PENDING" or r["kind"] != kind:
            return ""
        r["state"] = "RUNNING"
        return json.dumps({k: r[k] for k in
                           ("id", "desktop", "x", "y", "width", "height")})

    @dbus.service.method(IFACE, in_signature="iiiii", out_signature="s")
    def Submit(self, desktop, x, y, width, height):
        # Preserve the original 'move active window' client protocol.
        return self._submit("move", desktop, x, y, width, height)

    @dbus.service.method(IFACE, in_signature="", out_signature="s")
    def Take(self):
        return self._take("move")

    @dbus.service.method(IFACE, in_signature="siiiii", out_signature="s")
    def SubmitLaunch(self, app_class, desktop, x, y, width, height):
        return self._submit("launch", desktop, x, y, width, height, app_class)

    @dbus.service.method(IFACE, in_signature="ss", out_signature="s")
    def TakeLaunch(self, resource_class, desktop_file):
        r = self.request
        if (r is None or r["state"] != "PENDING" or r["kind"] != "launch"
                or not matches_class(r["app_class"], resource_class, desktop_file)):
            return ""
        return self._take("launch")

    @dbus.service.method(IFACE, in_signature="sss", out_signature="")
    def Complete(self, request_id, result, detail):
        r = self.request
        if r is None or r["id"] != request_id or r["state"] != "RUNNING":
            raise dbus.DBusException("Unknown or inactive request",
                                     name=IFACE + ".InvalidRequest")
        if result not in ("OK", "ERROR"):
            raise dbus.DBusException("Invalid completion result",
                                     name=IFACE + ".BadArguments")
        r["state"] = str(result)
        r["detail"] = str(detail)[:1024]

    @dbus.service.method(IFACE, in_signature="s", out_signature="s")
    def Status(self, request_id):
        r = self.request
        if r is None or r["id"] != request_id:
            return "UNKNOWN"
        return r["state"] + (" " + r["detail"] if r["detail"] else "")


def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    name = dbus.service.BusName(BUS, bus=bus, do_not_queue=True)
    broker = Broker(name)
    print(f"Ready on session bus: {BUS} {PATH}", flush=True)
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
