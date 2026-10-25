#!/usr/bin/env python3
"""Proof-of-concept, single-request D-Bus broker for a resident KWin script."""

import json
import time
import uuid

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

BUS = "org.joetoo.KWinBridge"
PATH = "/org/joetoo/KWinBridge"
IFACE = "org.joetoo.KWinBridge"


class Broker(dbus.service.Object):
    def __init__(self, bus_name):
        super().__init__(bus_name, PATH)
        self.request = None

    @dbus.service.method(IFACE, in_signature="iiiii", out_signature="s")
    def Submit(self, desktop, x, y, width, height):
        # Single-flight protocol. Stale requests may be replaced after 10 s.
        if (self.request is not None
                and self.request["state"] in ("PENDING", "RUNNING")
                and time.monotonic() - self.request["created"] < 10):
            raise dbus.DBusException(
                "Previous request has not completed",
                name=IFACE + ".Busy")

        if not (1 <= desktop <= 256 and
                -32768 <= x <= 32768 and -32768 <= y <= 32768 and
                1 <= width <= 32768 and 1 <= height <= 32768):
            raise dbus.DBusException(
                "Desktop, position, or size outside permitted range",
                name=IFACE + ".BadArguments")

        request_id = uuid.uuid4().hex
        self.request = {
            "id": request_id,
            "desktop": int(desktop),
            "x": int(x), "y": int(y),
            "width": int(width), "height": int(height),
            "state": "PENDING", "detail": "",
            "created": time.monotonic(),
        }
        return request_id

    @dbus.service.method(IFACE, in_signature="", out_signature="s")
    def Take(self):
        r = self.request
        if r is None or r["state"] != "PENDING":
            return ""
        r["state"] = "RUNNING"
        return json.dumps({k: r[k] for k in
                           ("id", "desktop", "x", "y", "width", "height")})

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
    broker = Broker(name)  # Keep the exported object alive.
    print(f"Ready on session bus: {BUS} {PATH}", flush=True)
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
