# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Broker-local persistence adapter. Disk records are candidates, never claims."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
import uuid
from joetoo_kwin_registry import ManagedWindow, LaunchRequest, RegistryError, canonical_uuid, historical_observation
from joetoo_kwin_persistence import atomic_private, read_private, runtime_path, intent, snapshot_text


class Recovery:
    def __init__(self, broker, bus, interface, path=None, glib=None):
        self.b = broker
        self.bus = bus
        self.interface = interface
        self.path = path or runtime_path()
        from joetoo_kwin_managed_close import DEFAULTS
        self.timeout = DEFAULTS["managed_close_dbus_timeout_ms"] / 1000
        self.glib = glib
        self.identity = None
        self.session = None
        self.saved_session = None
        self.owner = None
        self.state = 'awaiting_authenticated_inventory'
        self.generation = 0
        self.candidates = {}
        self.observation_source = None
        self.revision = -1
        self.error = None
        self.last_text = None
        self.last_authority = None
        try:
            self.load()
        except FileNotFoundError:
            pass
        except Exception:
            self.error = 'checkpoint_invalid'
            self.state = self.error
        broker.registry._changed = self.changed
        broker.registry._before_register = self.registering

    def daemon(self):
        return self.interface(self.bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspect=False), 'org.freedesktop.DBus')

    def authenticate(self, sender):
        """ProcessFD + unique bus owner + process start, never observerSource."""
        from joetoo_kwin_rdp_launch import CallerIdentity
        daemon = self.daemon()
        owner = str(daemon.GetNameOwner('org.kde.KWin', timeout=self.timeout))
        if self.owner is not None and owner != self.owner:
            self.state = 'different_compositor_session'
            for record in self.b.registry.managed_windows.values():
                record.presence = 'uncertain'
            self.changed()
            raise PermissionError('compositor owner replaced')
        if sender != owner:
            raise PermissionError('inventory sender is not KWin')
        if self.identity is None:
            identity = CallerIdentity(daemon.GetConnectionCredentials(owner, timeout=self.timeout))
            try:
                session = dict(bus=str(daemon.GetId(timeout=self.timeout)), owner=owner,
                               pid=identity.pid, start=identity.start, uid=os.geteuid())
                if not identity.alive() or str(daemon.GetNameOwner('org.kde.KWin', timeout=self.timeout)) != owner:
                    raise PermissionError('compositor changed during authentication')
            except Exception:
                identity.close()
                raise
            self.identity, self.owner, self.session = identity, owner, session
        if (owner != self.owner or not self.identity.alive()
                or str(daemon.GetId(timeout=self.timeout)) != self.session['bus']):
            self.state = 'different_compositor_session'
            for record in self.b.registry.managed_windows.values():
                record.presence = 'uncertain'
            self.changed()
            raise PermissionError('compositor session changed')
        return self.session

    def load(self):
        data = json.loads(read_private(self.path))
        if (set(data) != {'protocol', 'session', 'source', 'next_id', 'records'} or type(data['protocol']) is not int
                or data['protocol'] != 1 or not isinstance(data['source'], str) or not data['source']
                or not isinstance(data['session'], dict)
                or set(data['session']) != {'bus', 'owner', 'pid', 'start', 'uid'}
                or type(data['next_id']) is not int or data['next_id'] < 1
                or not isinstance(data['records'], list) or len(data['records']) > 512):
            raise ValueError('checkpoint schema')
        records = {}
        aliases = set()
        requests = set()
        slots = set()
        for item in data['records']:
            if not isinstance(item, dict) or set(item) != set(ManagedWindow.__dataclass_fields__):
                raise ValueError("incomplete checkpoint record")
            r = ManagedWindow(**item)
            r.observation = historical_observation(r.observation)
            identifier = canonical_uuid(r.window_uuid)
            if (r.window_uuid != identifier or not isinstance(r.managed_id, str)
                    or not r.managed_id.startswith('win-') or not r.managed_id[4:].isdigit()
                    or not 1 <= int(r.managed_id[4:]) < data['next_id']
                    or r.managed_id != f'win-{int(r.managed_id[4:]):03d}'
                    or r.managed_id in aliases or identifier in records
                    or not isinstance(r.request_id, str) or not r.request_id or r.request_id in requests
                    or r.presence not in ('present', 'missing', 'uncertain')
                    or r.placement not in ('succeeded', 'failed', 'not_requested', 'pending')
                    or r.observation.get('uuid') != identifier
                    or type(r.observation.get('pid')) is not int or r.observation['pid'] <= 0
                    or not isinstance(r.observation.get('resource_class'), str)):
                raise ValueError('checkpoint identity')
            slot = (r.recipe.get('desktop'), r.recipe.get('slot'))
            if any(type(v) is not int or not 1 <= v <= 256 for v in slot) or slot in slots:
                raise ValueError('checkpoint reservations')
            if r.restore_intent is not None:
                metadata = intent(r.restore_intent)
                if any(metadata[k] != r.recipe.get(k) for k in ('desktop', 'slot')):
                    raise ValueError('checkpoint intent mismatch')
                r.recipe.update({k: metadata[k] for k in ("program", "mode", "target", "layer")})
            records[identifier] = r
            aliases.add(r.managed_id)
            requests.add(r.request_id)
            slots.add(slot)
        # Publish reservations only after complete structural validation. Every
        # recovered record begins uncertain; no persisted presence is authority.
        self.saved_session = data['session']
        self.candidates = deepcopy(records)
        for r in records.values():
            r.presence = 'uncertain'
            if r.placement == 'pending':
                r.placement = 'failed'  # An interrupted operation is not resumed.
            r.connection = 'unknown'
            r.application_sessions = []
        self.b.registry.managed_windows = records
        self.b.registry.uuid_by_managed_id = {r.managed_id: r.window_uuid for r in records.values()}
        self.b.registry._next_managed_number = data['next_id']

    def registering(self, record):
        """No successful new managed ID may outrun its durable checkpoint."""
        try:
            if self.session is None or self.error:
                raise ValueError('checkpoint unavailable')
            self.authenticate(self.owner)
            self.persist(record)
        except Exception as exc:
            self.error = self.state = 'checkpoint_write_failed'
            raise RegistryError('registration checkpoint unavailable') from exc

    def changed(self):
        """Memory remains authoritative; later I/O uncertainty blocks new work."""
        if not self.session or self.error or (self.saved_session and self.saved_session != self.session):
            return
        try:
            self.persist()
        except Exception:
            self.error = self.state = 'checkpoint_write_failed'

    def flush(self):
        """Clean broker shutdown captures pending historical-only observation changes."""
        if self.session is not None and not self.error and (not self.saved_session or self.saved_session == self.session):
            try:
                self.persist(force=True)
            except Exception:
                self.error = self.state = 'checkpoint_write_failed'

    def persist(self, extra=None, force=False):
        values = []
        records = list(self.b.registry.managed_windows.values()) + ([extra] if extra else [])
        for record in records:
            item = asdict(record)
            # Historical fields are private bounded facts, never fresh proof.
            # No credentials, FDs, bearer tokens, logs or live sessions survive.
            # The authority fingerprint below avoids writes for every drag.
            item['observation'] = historical_observation(item['observation'])
            item['recipe'] = {k: v for k, v in item['recipe'].items() if k in ('desktop', 'slot', 'program', 'mode')}
            item['application_sessions'] = []
            item['connection'] = 'unknown'
            values.append(item)
        text = json.dumps(dict(protocol=1, session=self.session,
            source=self.b.observation_source, next_id=self.b.registry._next_managed_number + int(extra is not None),
            records=values), sort_keys=True)
        authority = json.loads(text)
        for item in authority['records']:
            item['observation'] = {k: item['observation'][k] for k in ('uuid', 'pid', 'resource_class')}
        fingerprint = json.dumps(authority, sort_keys=True)
        if (force or fingerprint != self.last_authority) and text != self.last_text:
            atomic_private(self.path, text)
            self.last_text = text
            self.last_authority = fingerprint

    def inventory(self, sender):
        """Reconcile a fresh authenticated full inventory, including reloads."""
        if self.error:
            return
        self.authenticate(sender)
        self.generation += 1
        generation = self.generation
        source = self.b.observation_source
        self.state = 'reconciling'
        self.observation_source = source
        self.revision = self.b.observation_revision
        if self.saved_session and self.saved_session != self.session:
            self.state = 'different_compositor_session'
            return  # Preserve all reservations, but never resurrect authority.
        records = list(self.b.registry.managed_windows.values())
        self.remaining = len(records)
        if self.glib is not None:
            def expired():
                if generation == self.generation and self.state == 'reconciling':
                    try:
                        self.authenticate(sender)
                    except Exception:
                        for record in self.b.registry.managed_windows.values():
                            record.presence = 'uncertain'
                        if self.state == 'reconciling':
                            self.state = 'identity_unverified'
                        return False
                    self.generation += 1  # Lost replies may not revive old authority.
                    self.candidates = {}
                    self.state = 'ready'
                    self.changed()
                return False
            self.glib.timeout_add(int(self.timeout * 1000), expired)
        if not records:
            self.state = 'ready'
            self.changed()
        def applicable():
            return (generation == self.generation and source == self.b.observation_source
                    and self.state == 'reconciling')
        for record in records:
            prior = self.candidates.get(record.window_uuid, deepcopy(record))
            record.presence = 'uncertain'
            def received(raw, r=record, previous=prior):
                if not applicable():
                    return
                try:
                    self.authenticate(sender)
                    if not applicable():
                        return
                    a = json.loads(str(raw))
                    observed = self.b.observed_windows.get(r.window_uuid)
                    if (previous.presence == 'present' and observed
                            and a.get('state') == 'present' and a.get('uuid') == r.window_uuid
                            and type(a.get('pid')) is int and a['pid'] == previous.observation['pid'] == observed['pid']
                            and a.get('class') == previous.observation['resource_class'] == observed['resource_class']
                            and a.get('backend') in ('x11', 'wayland')):
                        r.observation = deepcopy(observed)
                        r.presence = 'present'
                        if r.request_id not in self.b.registry.requests:
                            self.b.registry.requests[r.request_id] = LaunchRequest(r.request_id, source, frozenset(),
                                deepcopy(r.recipe), r.run_id, 'succeeded', r.observation['pid'], r.managed_id)
                    elif a.get('state') == 'missing' and a.get('uuid') == r.window_uuid and not observed:
                        r.presence = 'missing'
                except Exception:
                    pass  # Unproved identity retains only a reservation.
                if not applicable():
                    return
                self.remaining -= 1
                if self.remaining == 0:
                    self.state = 'ready'
                    self.candidates = {}
                    self.changed()
            try:
                daemon = self.daemon()
                if str(daemon.GetNameOwner('org.joetoo.KWinCloseNative', timeout=self.timeout)) != self.owner:
                    raise PermissionError('native owner mismatch')
                native = self.interface(self.bus.get_object(self.owner, '/org/joetoo/KWinCloseNative', introspect=False), 'org.joetoo.KWinCloseNative')
                native.Inspect(record.window_uuid, reply_handler=received, error_handler=lambda *unused, callback=received: callback('{}'), timeout=self.timeout)
            except Exception:
                received('{}')

    def event(self, source, revision):
        """Only contiguous authenticated lifecycle events can update live proof."""
        if source != self.observation_source or revision <= self.revision:
            return False
        if revision != self.revision + 1:
            self.generation += 1
            self.candidates = deepcopy(self.b.registry.managed_windows)
            for record in self.b.registry.managed_windows.values():
                record.presence = 'uncertain'
            self.state = 'awaiting_authenticated_inventory'
            self.changed()
            return False
        if self.state not in ('ready', 'reconciling'):
            return False
        self.revision = revision
        return True

    def guard(self):
        if self.identity is not None:
            self.authenticate(self.owner)
        if self.state != 'ready' or self.error:
            raise ValueError('recovery unavailable or unresolved')

    def export(self, sender):
        """Called by an authenticated same-user operator; not a close capability."""
        from joetoo_kwin_rdp_launch import CallerIdentity
        caller = CallerIdentity(self.daemon().GetConnectionCredentials(sender, timeout=self.timeout))
        try:
            self.guard()
            if not caller.alive() or not self.b.observation_synced or self.b._managed_close.other_busy() or self.b._managed_close.busy():
                raise ValueError('busy or unverified snapshot')
            self.authenticate(self.owner)
            entries = []
            revision = (self.b.observation_source, self.b.observation_revision)
            if str(self.daemon().GetNameOwner("org.joetoo.KWinCloseNative", timeout=self.timeout)) != self.owner:
                raise ValueError("native identity unavailable")
            native = self.interface(self.bus.get_object(self.owner, "/org/joetoo/KWinCloseNative", introspect=False), "org.joetoo.KWinCloseNative")
            for r in self.b.registry.managed_windows.values():
                if r.presence != 'present' or r.placement != 'succeeded' or r.restore_intent is None:
                    raise ValueError('incomplete or unrestorable arrangement')
                observed = self.b.observed_windows.get(r.window_uuid)
                if not observed or observed['desktops'] != [r.recipe['desktop']] or observed['on_all_desktops']:
                    raise ValueError('changed desktop or uncertain arrangement')
                proof = json.loads(str(native.Inspect(r.window_uuid, timeout=self.timeout)))
                if (proof.get("state") != "present" or proof.get("uuid") != r.window_uuid
                        or type(proof.get("pid")) is not int or proof["pid"] != r.observation["pid"]
                        or proof.get("class") != r.observation["resource_class"]):
                    raise ValueError("native identity unverified")
                entries.append(intent(r.restore_intent))
            self.authenticate(self.owner)
            if not caller.alive() or revision != (self.b.observation_source, self.b.observation_revision):
                raise ValueError("inventory changed during export")
            return snapshot_text(dict(protocol=1, entries=entries))
        finally:
            caller.close()
