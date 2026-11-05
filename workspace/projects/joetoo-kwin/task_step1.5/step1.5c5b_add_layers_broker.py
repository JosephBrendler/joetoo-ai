from pathlib import Path
p=Path('libexec/joetoo-kwind');s=p.read_text().replace('''        self.move_protocol = 0''','''        self.initial_layout = None
        self.initial_layout_protocol = 0
        self.move_protocol = 0''',1)
s=s.replace('''        # Shared implementation for Submit (move) and SubmitLaunch (launch).''','''        if self._initial_layout_active():
            raise dbus.DBusException("Initial layout is still active", name=IFACE + ".Busy")
        # Shared implementation for Submit (move) and SubmitLaunch (launch).''',1)
s=s.replace('''        now = time.monotonic()
        self._expire_managed_correlation(now)''','''        if self._initial_layout_active():
            raise dbus.DBusException("Initial layout is still active", name=IFACE + ".Busy")
        now = time.monotonic()
        self._expire_managed_correlation(now)''',1)
idx=s.index('    def _set_managed_launch_pid');s=s[:idx]+s[idx:] # Private launch is reached via serialized public submission.
s=s.replace('''        self.move_protocol = move_protocol''','''        self.initial_layout_protocol = (1 if message.get("initial_layout_protocol") == 1 else 0)
        self.move_protocol = move_protocol''',1)
s=s.replace('''            "managed_count": len(self.registry.managed_windows),''','''            "initial_layout_protocol": self.initial_layout_protocol,
            "initial_layout_active": self._initial_layout_active(),
            "managed_count": len(self.registry.managed_windows),''',1)
idx=s.index('    # Step 1.3b.1:')
s=s[:idx]+'''    def _initial_layout_active(self):
        r = self.initial_layout
        if r is None or r["state"] not in ("PENDING", "RUNNING"):
            return False
        if (time.monotonic() >= r["deadline"] or not self.observation_synced
                or r["source"] != self.observation_source
                or any(item["uuid"] not in self.observed_windows
                       or self.registry.get_window(item["uuid"]).presence != "present"
                       for item in r["entries"])):
            r.update(state="FAILED", detail="Initial layout expired or cohort/source disappeared")
            return False
        return True

    @dbus.service.method(IFACE, in_signature="s", out_signature="s")
    def SubmitInitialLayout(self, payload):
        """Freeze broker-owned registrations, never accept launcher-selected UUIDs."""
        self._advance_placement()
        if (self._initial_layout_active() or
                (self.request and self.request["state"] in ("PENDING", "RUNNING", "VERIFYING")) or
                any(r.state in ("pending", "running") for r in self.registry.requests.values()) or
                (self.correlation and self.correlation["state"] == "PENDING")):
            raise dbus.DBusException("Another transaction is active", name=IFACE + ".Busy")
        if not self.observation_synced or self.initial_layout_protocol != 1:
            raise dbus.DBusException("Resident lacks initial-layout protocol 1", name=IFACE + ".Unsupported")
        try:
            if len(payload) > 65536:
                raise ValueError("layout payload too large")
            message = json.loads(payload)
            if set(message) != {"entries"} or not 1 <= len(message["entries"]) <= 256:
                raise ValueError("invalid cohort")
            entries = []
            for item in message["entries"]:
                if set(item) != {"registration_request_id", "layer"} or item["layer"] not in ("under", "panel", "over"):
                    raise ValueError("invalid layer entry")
                launch = self.registry.requests[item["registration_request_id"]]
                record = self.registry.get_window(launch.result) if launch.state == "succeeded" else None
                if (record is None or record.presence != "present" or record.placement != "succeeded"
                        or launch.source != self.observation_source):
                    raise ValueError("registration not positively placed/present")
                observed = self.observed_windows[record.window_uuid]
                entries.append({"uuid": record.window_uuid, "layer": item["layer"],
                                "desktop": record.recipe["desktop"],
                                "geometry": dict(observed["geometry"]),
                                "desktops": list(observed["desktops"]),
                                "on_all_desktops": observed["on_all_desktops"]})
            if len({e["uuid"] for e in entries}) != len(entries) or len({e["desktop"] for e in entries}) != 1:
                raise ValueError("duplicate UUID or mixed desktop groups")
        except (ValueError, KeyError, TypeError, AttributeError, RegistryError) as exc:
            raise dbus.DBusException(str(exc), name=IFACE + ".BadArguments") from exc
        preferred = next((e["uuid"] for layer in ("over", "panel")
                          for e in reversed(entries) if e["layer"] == layer), None)
        ordered = [e["uuid"] for layer in ("under", "panel", "over") for e in entries if e["layer"] == layer]
        self.initial_layout = dict(id=uuid.uuid4().hex, state="PENDING", entries=entries,
                                   order=ordered, preferred_uuid=preferred,
                                   source=self.observation_source, deadline=time.monotonic() + 10,
                                   geometry="placed", stacking="pending", focus="pending", detail="")
        return self.initial_layout["id"]

    @dbus.service.method(IFACE, in_signature="s", out_signature="s")
    def TakeInitialLayout(self, source):
        if not self._initial_layout_active():
            return ""
        r = self.initial_layout
        if r["state"] != "PENDING" or source != r["source"]:
            return ""
        r["state"] = "RUNNING"
        return json.dumps({key: r[key] for key in ("id", "entries", "order", "preferred_uuid", "source")} |
                          {"remaining_ms": max(0, int((r["deadline"] - time.monotonic()) * 1000))})

    @dbus.service.method(IFACE, in_signature="ss", out_signature="")
    def CompleteInitialLayout(self, request_id, payload):
        if not self._initial_layout_active() or self.initial_layout["id"] != request_id or self.initial_layout["state"] != "RUNNING":
            raise dbus.DBusException("Inactive initial layout", name=IFACE + ".InvalidRequest")
        r = self.initial_layout
        try:
            if len(payload) > 65536:
                raise ValueError("completion too large")
            result = json.loads(payload)
            if result["source"] != r["source"]:
                raise ValueError("wrong resident source")
            # Completion is evidence from the resident, not permission to change
            # ownership. Geometry remains independently observed by the broker.
            unchanged = all(self.observed_windows[e["uuid"]]["geometry"] == e["geometry"]
                            and self.observed_windows[e["uuid"]]["desktops"] == e["desktops"]
                            and self.observed_windows[e["uuid"]]["on_all_desktops"] == e["on_all_desktops"]
                            for e in r["entries"])
            stack_ok = result.get("order") == r["order"] and result.get("geometry_unchanged") is True and unchanged
            visible = (r["preferred_uuid"] is not None and result.get("current_desktop") == r["entries"][0]["desktop"])
            if r["preferred_uuid"] is None:
                focus_ok = result.get("focus_attempted") is False and result.get("active_uuid") == result.get("before_active_uuid")
                focus = "no automatic target" if focus_ok else "failed"
            elif not visible:
                focus_ok = result.get("focus_attempted") is False and result.get("active_uuid") == result.get("before_active_uuid")
                focus = "preferred target retained; inactive desktop" if focus_ok else "failed"
            else:
                focus_ok = result.get("focus_attempted") is True and result.get("active_uuid") == r["preferred_uuid"]
                focus = "verified" if focus_ok else "failed"
            ok = stack_ok and focus_ok and not result.get("error")
            r.update(state="SUCCEEDED" if ok else "FAILED", geometry="unchanged" if unchanged else "changed",
                     stacking="verified" if stack_ok else "failed", focus=focus,
                     detail=str(result.get("error", ""))[:512], observed_active_uuid=result.get("active_uuid"),
                     focus_attempted=result.get("focus_attempted"))
        except (ValueError, KeyError, TypeError) as exc:
            raise dbus.DBusException("Invalid initial-layout completion", name=IFACE + ".BadArguments") from exc

    @dbus.service.method(IFACE, in_signature="s", out_signature="s")
    def InitialLayoutStatus(self, request_id):
        self._initial_layout_active()
        r = self.initial_layout
        if r is None or r["id"] != request_id:
            return json.dumps({"state": "UNKNOWN"})
        return json.dumps({key: r.get(key) for key in ("id", "state", "geometry", "stacking", "focus", "detail",
                                                       "preferred_uuid", "observed_active_uuid", "focus_attempted")})

''' +s[idx:];p.write_text(s)
