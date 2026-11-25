#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Broker-owned close transactions. Legacy observations never prove dispatch/close.

The native adapter shares org.kde.KWin's authenticated unique bus connection.
All adapter calls address that pinned unique name, not a re-resolved service.
For single-window close:
No process termination, registry retirement or placement mutation occurs here.
Confirmed bulk sweeps additionally retire only verified missing registrations.
"""
from collections import OrderedDict
from copy import deepcopy
import json
import os
import re
import time
import uuid

SERVICE = 'org.joetoo.KWinCloseNative'
PATH = '/org/joetoo/KWinCloseNative'
DEFAULTS = dict(managed_close_timeout_ms=15000, managed_close_total_timeout_ms=300000,
                managed_close_prepare_timeout_ms=300000, managed_close_x11_grab_ms=100,
                managed_close_poll_ms=100, managed_close_dbus_timeout_ms=3000)
BOUNDS = dict(managed_close_timeout_ms=(100, 120000), managed_close_total_timeout_ms=(100, 600000),
              managed_close_prepare_timeout_ms=(1000, 600000), managed_close_x11_grab_ms=(10, 500),
              managed_close_poll_ms=(10, 1000), managed_close_dbus_timeout_ms=(100, 10000))
ACTIVE = frozenset(('authenticating', 'preparing', 'prepared', 'running', 'cleanup_uncertain'))


def settings(values=None):
    result = dict(DEFAULTS)
    for key, value in (values or {}).items():
        if key not in DEFAULTS or isinstance(value, bool):
            raise ValueError('invalid managed close settings')
        if isinstance(value, str) and re.fullmatch(r'[1-9][0-9]{0,6}', value):
            value = int(value)
        if type(value) is not int or not BOUNDS[key][0] <= value <= BOUNDS[key][1]:
            raise ValueError('invalid managed close setting: ' + key)
        result[key] = value
    if result['managed_close_total_timeout_ms'] < result['managed_close_timeout_ms']:
        raise ValueError('managed close total timeout precedes per-window timeout')
    return result


def payload(text):
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError('duplicate field')
            obj[k] = v
        return obj
    if not isinstance(text, str) or len(text) > 8192:
        raise ValueError('invalid close payload')
    return json.loads(text, object_pairs_hook=unique)


class CloseRuntime:
    """One serial job; asynchronous callbacks carry explicit job identity."""
    def __init__(self, broker, glib, dbus_module, clock=time.monotonic):
        self.b = broker
        self.glib = glib
        self.dbus = dbus_module
        self.clock = clock
        self.job = None
        self.history = OrderedDict()

    def busy(self):
        return self.job is not None and self.job['state'] in ACTIVE

    def other_busy(self):
        b = self.b
        b._expire_managed_correlation()
        b._advance_placement()
        return bool(b.registry._active_request_id or b._initial_layout_active() or b._sdl_pending_auth
                    or (b.request and b.request['state'] in ('PENDING', 'RUNNING', 'VERIFYING'))
                    or (b._sdl_placement and (not b._sdl_placement.get('terminal') or
                                              b._sdl_placement.get('cleanup_uncertain')))
                    or (b._managed_correlation and (b._managed_correlation.get('state') == 'PENDING' or
                                                    b._managed_correlation.get('observer_cleanup_uncertain')))
                    or (b.correlation and b.correlation.get('state') == 'PENDING' and time.monotonic() < b.correlation.get('deadline', float('inf'))))

    def synchronized(self, j):
        return bool(self.b.observation_synced and self.b.observation_source == j['source'] and
                    self.b.observation_revision >= j['revision'] and not self.other_busy())

    def report(self, j):
        # Do not expose confirmation tokens, bus names, credentials or captions.
        retired = {t['managed_id'] for t in j['targets'] if t.get('retired') is True}
        retained = (j.get('scope') != 'all' or
                    any(record.managed_id not in retired for record in j['records']))
        # Surface only validated scalar helper diagnostics, never raw process output.
        target_fields = ('managed_id', 'window_uuid', 'request_id', 'desktop', 'slot',
                         'backend', 'state', 'action', 'retired', 'reason',
                         'helper_exit_code', 'helper_exit_status', 'helper_receipt_ok')
        return json.dumps(dict(protocol=1, request_id=j['id'], state=j['state'], reason=j.get('reason', ''),
                               targets=[{k: v for k, v in t.items() if k in target_fields} for t in j['targets']], excluded=deepcopy(j['excluded']),
                               registration_retained=retained, reservations_retained=retained,
                               self_terminal=j.get('self_terminal', 'unknown')), sort_keys=True)

    def remember(self, j):
        self.history[j['id']] = j
        while len(self.history) > max(1, self.b.registry._completed_limit):
            first = next(iter(self.history))
            if self.history[first] is self.job and self.busy():
                break
            old = self.history.pop(first)
            self.release(old)

    @staticmethod
    def release(j):
        for key in ('caller', 'kwin', 'terminal_identity'):
            identity = j.pop(key, None)
            if identity is not None:
                identity.close()

    def finish(self, j, state, reason):
        if j is not self.job or j['state'] not in ACTIVE:
            return
        j['state'], j['reason'] = state, reason
        for target in j['targets']:
            if target['state'] == 'queued':
                target['state'] = 'skipped'
            elif state == 'cleanup_uncertain' and target['state'] in ('claiming', 'waiting', 'checking_absence'):
                target['state'] = 'unresolved'
        if state != 'cleanup_uncertain':
            self.release(j)
        self.remember(j)
        callback = j.pop('reply', None)
        if callback:
            callback(self.report(j))

    def current(self, j):
        return j is self.job and j['state'] in ACTIVE and j['state'] != 'cleanup_uncertain'

    def adapter(self, j, method, args, done, fail=None):
        """A response from the pinned KWin connection is authenticated evidence."""
        step, phase = j["index"], j["state"]
        def applicable():
            return self.current(j) and j["index"] == step and j["state"] == phase
        def received(raw):
            if not applicable():
                return
            try:
                if not j['kwin'].alive() or not self.synchronized(j):
                    raise ValueError('source lost')
                answer = payload(str(raw))
                if not isinstance(answer, dict):
                    raise ValueError('invalid adapter reply')
                done(answer)
            except Exception:
                (fail or (lambda: self.finish(j, 'failed', 'native_evidence_unavailable')))()
        try:
            proxy = self.b._sdl_bus_connection().get_object(j['kwin_name'], PATH, introspect=False)
            getattr(self.dbus.Interface(proxy, SERVICE), method)(*args,
                reply_handler=received, error_handler=lambda *unused: (fail or
                (lambda: self.finish(j, 'failed', 'native_evidence_unavailable')))() if applicable() else None,
                timeout=j['bounds']['managed_close_dbus_timeout_ms'] / 1000)
        except Exception:
            if applicable():
                (fail or (lambda: self.finish(j, 'failed', 'native_evidence_unavailable')))()

    def prepare(self, text, sender, reply, error):
        from joetoo_kwin_rdp_launch import CallerIdentity
        j = None
        try:
            data = payload(text)
            if set(data) not in ({'protocol', 'scope', 'managed_id', 'settings'}, {'protocol', 'scope', 'managed_id', 'settings', 'terminal'}) or type(data['protocol']) is not int or data['protocol'] != 1:
                raise ValueError('schema')
            if data['scope'] not in ('one', 'all') or not isinstance(sender, str) or not sender.startswith(':'):
                raise ValueError('scope')
            if (data['scope'] == 'one' and (not isinstance(data['managed_id'], str) or not re.fullmatch(r'win-[0-9]{3,}', data['managed_id']))) or (data['scope'] == 'all' and data['managed_id'] != ''):
                raise ValueError('managed ID')
            limits = settings(data['settings'])
            if self.busy() or self.other_busy() or not self.b.observation_synced:
                raise ValueError('busy or unsynchronized')
            records = list(self.b.registry.managed_windows.values())
            if data['scope'] == 'one':
                records = [r for r in records if r.managed_id == data['managed_id']]
                if not records:
                    raise ValueError('unknown managed ID')
            records.sort(key=lambda r: (r.recipe.get('desktop', 0), r.recipe.get('slot', 0), r.managed_id))
            # Managed slots already bound this finite snapshot; no post-prepare
            # registration can enter it. Missing/uncertain records stay reserved.
            j = dict(id=uuid.uuid4().hex, scope=data['scope'], state='authenticating', sender=sender, targets=[], excluded=[],
                     records=deepcopy(records), terminal_hint=data.get('terminal', {}), index=0, source=self.b.observation_source,
                     revision=self.b.observation_revision, bounds=limits, reply=reply,
                     deadline=self.clock() + limits['managed_close_prepare_timeout_ms'] / 1000)
            self.job = j
            bus = self.b._sdl_bus_connection()
            if not getattr(self, '_owner_watch', None):
                self._owner_watch = bus.add_signal_receiver(self.owner_changed, signal_name='NameOwnerChanged',
                    dbus_interface='org.freedesktop.DBus', bus_name='org.freedesktop.DBus',
                    path='/org/freedesktop/DBus')
            daemon = self.dbus.Interface(bus.get_object(
                'org.freedesktop.DBus', '/org/freedesktop/DBus', introspect=False), 'org.freedesktop.DBus')
        except Exception:
            if j is not None and self.job is j:
                j.pop('reply', None)
                self.finish(j, 'failed', 'authentication_or_source_unavailable')
            return error(self.dbus.DBusException('Managed close unavailable or invalid request', name='org.joetoo.KWinBridge.CloseRejected'))

        def fail(*unused):
            self.finish(j, 'failed', 'authentication_or_source_unavailable')

        def guarded(callback):
            def received(*args):
                if not self.current(j):
                    return
                try:
                    callback(*args)
                except Exception:
                    fail()
            return received

        def identity(credentials, key, next_step):
            if not self.current(j):
                self.b._sdl_discard_credentials(credentials)
                return
            try:
                if key in j:
                    self.b._sdl_discard_credentials(credentials)
                    return fail()
                j[key] = CallerIdentity(credentials)
                next_step()
            except Exception:
                fail()

        def owners(name):
            if not self.current(j):
                return
            j['kwin_name'] = str(name)
            def adapter_owner(value):
                if not self.current(j):
                    return
                if str(value) != j['kwin_name']:
                    return fail()
                daemon.GetConnectionCredentials(j['kwin_name'], reply_handler=lambda c:
                    identity(c, 'kwin', lambda: self.inspect_next(j)), error_handler=fail,
                    timeout=limits['managed_close_dbus_timeout_ms'] / 1000)
            daemon.GetNameOwner(SERVICE, reply_handler=guarded(adapter_owner), error_handler=fail,
                                timeout=limits['managed_close_dbus_timeout_ms'] / 1000)

        try:
            # Arm before the first RPC: a lost callback or synchronous send
            # failure must never leave an unbounded authenticating Busy record.
            self.glib.timeout_add(limits['managed_close_poll_ms'], lambda: self.tick(j))
            daemon.GetConnectionCredentials(sender, reply_handler=lambda c: identity(c, 'caller', lambda:
                daemon.GetNameOwner('org.kde.KWin', reply_handler=guarded(owners), error_handler=fail,
                                    timeout=limits['managed_close_dbus_timeout_ms'] / 1000)),
                error_handler=fail, timeout=limits['managed_close_dbus_timeout_ms'] / 1000)
        except Exception:
            fail()

    def observation(self, source, revision):
        """Legacy ordering is a rejection gate, never close-completion proof."""
        j = self.job
        if not j or not self.current(j):
            return
        if source != j['source'] or revision != j['revision'] + 1:
            self.finish(j, 'cleanup_uncertain' if j['state'] == 'running' else 'failed', 'observation_source_or_revision_gap')
        else:
            j['revision'] = revision

    def owner_changed(self, name, old, new):
        j = self.job
        if not j or not self.current(j):
            return
        if str(name) == j['sender'] and not str(new) and j['state'] != 'running':
            self.finish(j, 'failed', 'confirmation_owner_lost')
        elif str(name) in ('org.kde.KWin', SERVICE) and str(old) and str(new) != j.get('kwin_name'):
            self.finish(j, 'cleanup_uncertain' if j['state'] == 'running' else 'failed', 'native_owner_replaced')

    def identify_terminal(self, j):
        """Optional read-only Konsole proof. Missing APIs/ambiguity => unknown.

        Session.processId and Window.sessionList bind the invoking shell to the
        authenticated Konsole process. Exactly one native window for that PID
        is required; multi-window Konsole is deliberately not guessed.
        """
        hint = j.get('terminal_hint', {})
        def ready():
            callback = j.pop('reply', None)
            if callback:
                callback(self.report(j))
        try:
            if not isinstance(hint, dict) or set(hint) != {'service', 'session', 'window'}:
                return ready()
            if (not re.fullmatch(r'(?:org\.kde\.konsole-[0-9]+|:[0-9]+\.[0-9]+)', hint['service']) or
                    not re.fullmatch(r'/Sessions/[0-9]+', hint['session']) or
                    not re.fullmatch(r'/Windows/[0-9]+', hint['window'])):
                return ready()
            from joetoo_kwin_rdp_launch import CallerIdentity, _proc_info
            ancestors = {}
            pid = j['caller'].pid
            for _ in range(32):
                info = _proc_info(pid, include_executable=False)
                if info['uid'] != os.geteuid() or pid in ancestors:
                    break
                ancestors[pid] = info['start']
                pid = info['parent']
                if pid <= 1:
                    break
            bus = self.b._sdl_bus_connection()
            daemon = self.dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'), 'org.freedesktop.DBus')
            def owned(name):
                def credentials(c):
                    if not self.current(j):
                        self.b._sdl_discard_credentials(c)
                        return
                    identity = None
                    try:
                        identity = CallerIdentity(c)
                        j['terminal_identity'] = identity
                        if ancestors.get(identity.pid) != identity.start:
                            identity.close()
                            return ready()
                        proxy = bus.get_object(str(name), hint['session'], introspect=False)
                        def session(shell_pid):
                            try:
                                shell_pid = int(shell_pid)
                                if shell_pid not in ancestors or _proc_info(shell_pid, include_executable=False)['start'] != ancestors[shell_pid] or not identity.alive() or not j['caller'].alive():
                                    identity.close()
                                    return ready()
                                window = self.dbus.Interface(bus.get_object(str(name), hint['window'], introspect=False), 'org.kde.konsole.Window')
                                def sessions(ids):
                                    try:
                                        if int(hint['session'].rsplit('/', 1)[1]) not in [int(v) for v in ids] or not identity.alive():
                                            return ready()
                                        native_pid = identity.pid
                                        def native(a):
                                            if a.get('state') == 'identified' and identity.alive() and j.get('caller') and j['caller'].alive() and _proc_info(shell_pid, include_executable=False)['start'] == ancestors[shell_pid]:
                                                matches = [t['managed_id'] for t in j['targets']
                                                           if t['window_uuid'] == a.get('uuid')
                                                           and t.get('action', 'close') == 'close']
                                                j['self_terminal'] = matches[0] if len(matches) == 1 else 'excluded'
                                            identity.close()
                                            ready()
                                        self.adapter(j, 'Terminal', (native_pid,), native, lambda: (identity.close(), ready()))
                                    except Exception:
                                        identity.close()
                                        ready()
                                window.sessionList(reply_handler=sessions, error_handler=lambda *unused: (identity.close(), ready()), timeout=j['bounds']['managed_close_dbus_timeout_ms']/1000)
                            except Exception:
                                identity.close()
                                ready()
                        self.dbus.Interface(proxy, 'org.kde.konsole.Session').processId(reply_handler=session,
                            error_handler=lambda *unused: (identity.close(), ready()), timeout=j['bounds']['managed_close_dbus_timeout_ms']/1000)
                    except Exception:
                        if identity:
                            identity.close()
                        ready()
                daemon.GetConnectionCredentials(str(name), reply_handler=credentials, error_handler=lambda *unused: ready(), timeout=j['bounds']['managed_close_dbus_timeout_ms']/1000)
            daemon.GetNameOwner(hint['service'], reply_handler=owned, error_handler=lambda *unused: ready(), timeout=j['bounds']['managed_close_dbus_timeout_ms']/1000)
        except Exception:
            ready()

    def inspect_next(self, j):
        if not self.current(j):
            return
        j['state'] = 'preparing'
        if j['index'] == len(j['records']):
            if j['scope'] == 'all':
                # Resolve authenticated absences first, so a later native
                # dispatch hazard cannot strand otherwise safe missing entries.
                j['targets'].sort(key=lambda t: t.get('action') != 'retire_missing')
            j['state'] = 'prepared'
            j['index'] = 0
            self.identify_terminal(j)
            return
        record = j['records'][j['index']]
        def received(a):
            expected = record.observation
            if (j['scope'] == 'all' and record.presence in ('present', 'missing') and
                    a.get('state') == 'missing' and a.get('uuid') == record.window_uuid):
                j['targets'].append(dict(managed_id=record.managed_id, window_uuid=record.window_uuid,
                    request_id=record.request_id, desktop=record.recipe.get('desktop'), slot=record.recipe.get('slot'),
                    pid=expected.get('pid'), app_class=expected.get('resource_class'), state='queued',
                    action='retire_missing', retired=False))
            elif (record.presence == 'present' and a.get('state') == 'present' and
                    a.get('uuid') == record.window_uuid and type(a.get('pid')) is int and
                    a['pid'] == expected.get('pid') and a.get('class') == expected.get('resource_class') and
                    a.get('backend') in ('wayland', 'x11') and a.get('closeable') is True):
                j['targets'].append(dict(managed_id=record.managed_id, window_uuid=record.window_uuid,
                    request_id=record.request_id, desktop=record.recipe.get('desktop'), slot=record.recipe.get('slot'),
                    pid=a['pid'], app_class=a['class'], backend=a['backend'], state='queued'))
                if j['scope'] == 'all':
                    j['targets'][-1].update(action='close', retired=False)
            else:
                j['excluded'].append(dict(managed_id=record.managed_id, presence=record.presence,
                                           reason='missing_uncertain_or_native_identity_unavailable'))
                if j['scope'] == 'all':
                    reason = ('registered_identity_uncertain' if record.presence == 'uncertain' else
                              'native_presence_conflict' if record.presence == 'missing' else
                              'native_not_closeable' if a.get('state') == 'present' and a.get('closeable') is False else
                              'native_unsupported' if a.get('state') == 'unsupported' else
                              'native_identity_unavailable')
                    j['excluded'][-1].update(state='failed', retired=False, reason=reason)
            j['index'] += 1
            self.inspect_next(j)
        self.adapter(j, 'Inspect', (record.window_uuid,), received)

    def commit(self, request_id, sender, reply, error):
        j = self.job
        if not j or j['id'] != request_id or j['state'] != 'prepared' or j['sender'] != sender:
            return error(self.dbus.DBusException('Managed close commit rejected', name='org.joetoo.KWinBridge.CloseRejected'))
        if not j['caller'].alive() or not j['kwin'].alive() or not self.synchronized(j) or self.clock() >= j['deadline']:
            self.finish(j, 'failed', 'confirmation_stale')
            return reply(self.report(j))
        j['state'] = 'running'
        j['deadline'] = self.clock() + j['bounds']['managed_close_total_timeout_ms'] / 1000
        # Accepted work survives this owner's exit; no further caller-liveness
        # check or parent/foreground child supervision belongs to window close.
        j.pop('caller').close()
        self.dispatch_next(j)
        reply(self.report(j))

    def dispatch_next(self, j):
        if not self.current(j) or j['state'] != 'running':
            return
        if j['index'] >= len(j['targets']):
            done = ('closed', 'already_missing') if j['scope'] == 'all' else ('closed',)
            complete = (all(t['state'] in done and (j['scope'] != 'all' or t.get('retired') is True)
                            for t in j['targets']) and not j['excluded'])
            return self.finish(j, 'succeeded' if complete else 'partial', 'verified' if complete else 'incomplete')
        if self.clock() >= j['deadline']:
            return self.finish(j, 'partial', 'deadline')
        t = j['targets'][j['index']]
        record = self.matching_record(t)
        if not record or record.presence not in ('present', 'missing'):
            return self.target_failed(j, t, 'identity_lost', 'registered_identity_lost')
        j['window_deadline'] = min(j['deadline'], self.clock() + j['bounds']['managed_close_timeout_ms'] / 1000)
        if t.get('action') == 'retire_missing':
            j['polling'] = True
            t['state'] = 'checking_absence'
            def absent(a):
                if self.clock() >= j['window_deadline']:
                    return self.uncertain(j, t, 'native_absence_unavailable')
                if a.get('state') == 'missing' and a.get('uuid') == t['window_uuid']:
                    self.retire_verified(j, t, 'already_missing')
                else:
                    self.target_failed(j, t, 'identity_lost', 'native_absence_not_verified')
            # Fresh authenticated absence after confirmation, not a legacy
            # presence flag or an old preview, authorizes retirement.
            return self.adapter(j, 'Inspect', (t['window_uuid'],), absent,
                                lambda: self.uncertain(j, t, 'native_absence_unavailable'))
        if record.presence != 'present':
            return self.target_failed(j, t, 'identity_lost', 'registered_identity_lost')
        t['token'] = uuid.uuid4().hex
        t['state'] = 'claiming'
        j['polling'] = True
        def received(a):
            if a.get('token') != t['token'] or a.get('uuid') != t['window_uuid']:
                return self.uncertain(j, t, 'native_claim_receipt_invalid')
            t['state'] = 'waiting'
            self.native_result(j, t, a)
        self.adapter(j, 'Close', (t['token'], t['window_uuid'], t['pid'], t['app_class'],
                                 j['bounds']['managed_close_x11_grab_ms'], str(int(j['window_deadline'] * 1000))), received,
                     lambda: self.uncertain(j, t, 'dispatch_reply_unavailable'))

    def matching_record(self, t):
        from joetoo_kwin_registry import RegistryError
        try:
            record = self.b.registry.get_window(t['managed_id'])
        except RegistryError:
            return None
        if (record and record.window_uuid == t['window_uuid'] and record.request_id == t['request_id']
                and record.recipe.get('desktop') == t['desktop'] and record.recipe.get('slot') == t['slot']
                and record.observation.get('pid') == t['pid']
                and record.observation.get('resource_class') == t['app_class']):
            return record
        return None

    def target_failed(self, j, t, state, reason):
        t.update(state=state, reason=reason)
        if j['scope'] != 'all':
            return self.finish(j, 'failed', reason)
        # No native claim remains unowned here; unrelated targets may proceed.
        j['index'] += 1
        j['polling'] = False
        self.dispatch_next(j)

    def retire_verified(self, j, t, state):
        from joetoo_kwin_registry import RegistryError
        record = self.matching_record(t)
        if not record or record.presence not in ('present', 'missing'):
            return self.target_failed(j, t, 'identity_lost', 'registered_identity_lost')
        self.b.registry.set_presence(t['window_uuid'], 'missing')
        try:
            self.b.registry.retire_missing(t['managed_id'], window_uuid=t['window_uuid'], request_id=t['request_id'])
        except RegistryError:
            return self.target_failed(j, t, 'retirement_failed', 'retirement_guard_rejected')
        t.update(state=state, retired=True, reason='verified')
        j['index'] += 1
        j['polling'] = False
        self.dispatch_next(j)

    def uncertain(self, j, t, reason):
        if not self.current(j) or j['state'] != 'running' or j['index'] >= len(j['targets']) or j['targets'][j['index']] is not t:
            return
        t['state'] = 'unresolved'
        self.finish(j, 'cleanup_uncertain', reason)

    def native_result(self, j, t, a):
        if not self.current(j) or j['state'] != 'running' or j['index'] >= len(j['targets']) or j['targets'][j['index']] is not t:
            return
        if a.get('token') != t['token'] or a.get('uuid') != t['window_uuid'] or type(a.get('helper_reaped')) is not bool:
            return self.uncertain(j, t, 'native_receipt_invalid')
        t['last_reaped'] = a['helper_reaped']
        if not a['helper_reaped']:
            j['polling'] = False
            return
        if self.clock() >= j['window_deadline']:
            t['state'] = 'not_closed_timeout'
            j['index'] += 1
            j['polling'] = False
            return self.dispatch_next(j)
        if a.get('state') == 'closed' and a.get('gone') is True:
            if j['scope'] == 'all':
                return self.retire_verified(j, t, 'closed')
            t['state'] = 'closed'
            # Only this authenticated native callback marks successful closure.
            self.b.registry.set_presence(t['window_uuid'], 'missing')
            j['index'] += 1
            j['polling'] = False
            self.dispatch_next(j)
        elif a.get('state') not in ('dispatching', 'fencing'):
            rejected = {'expired', 'busy_or_replay', 'identity_or_capability_rejected'}
            failed = {'unsupported', 'helper_unavailable', 'helper_channel_unavailable',
                      'helper_channel_rejected', 'helper_channel_lost', 'helper_timeout',
                      'identity_lost', 'source_lost', 'dispatch_failed'}
            if a.get('state') not in rejected | failed:
                return self.uncertain(j, t, 'native_phase_unknown')
            if j['scope'] == 'all' and a['state'] in ('source_lost', 'busy_or_replay'):
                return self.uncertain(j, t, 'native_' + a['state'])
            if a['state'] == 'dispatch_failed':
                # Diagnostic metadata is not authorization or proof of close. Accept
                # only the three bounded scalar fields from the pinned native effect.
                code = a.get('helper_exit_code')
                status = a.get('helper_exit_status')
                receipt = a.get('helper_receipt_ok')
                if (type(code) is int and -255 <= code <= 255 and
                        status in ('normal', 'crash') and type(receipt) is bool):
                    t.update(helper_exit_code=code, helper_exit_status=status,
                             helper_receipt_ok=receipt)
            self.target_failed(j, t, 'dispatch_rejected' if a['state'] in rejected else 'dispatch_failed',
                               'native_' + a['state'])
        else:
            j['polling'] = False

    def tick(self, j):
        try:
            return self._tick(j)
        except Exception:
            if self.current(j):
                self.finish(j, 'cleanup_uncertain' if j['state'] == 'running' else 'failed', 'close_guard_unavailable')
            return self.glib.SOURCE_REMOVE

    def _tick(self, j):
        if not self.current(j):
            return self.glib.SOURCE_REMOVE
        if j['state'] == 'cleanup_uncertain':
            return self.glib.SOURCE_REMOVE  # Retains ownership; no silent reuse.
        if not self.synchronized(j) or ('kwin' in j and not j['kwin'].alive()):
            if j['state'] == 'running':
                return self.finish(j, 'cleanup_uncertain', 'source_or_owner_lost') or self.glib.SOURCE_REMOVE
            self.finish(j, 'failed', 'source_or_owner_lost')
            return self.glib.SOURCE_REMOVE
        if j['state'] in ('authenticating', 'preparing', 'prepared'):
            if self.clock() >= j['deadline'] or ('caller' in j and not j['caller'].alive()):
                self.finish(j, 'failed', 'confirmation_expired_or_owner_lost')
                return self.glib.SOURCE_REMOVE
            return True
        if j['state'] == 'running' and j['index'] < len(j['targets']):
            t = j['targets'][j['index']]
            if t.get('action') == 'retire_missing':
                if self.clock() >= j['window_deadline']:
                    self.uncertain(j, t, 'native_absence_unavailable')
                return self.busy()
            if self.clock() >= j['window_deadline']:
                # Pending dispatch/unknown helper ownership cannot be hidden by
                # a terminal timeout. Normal dispatched-but-open == refusal or
                # no convergence; no resend, force kill, or late success.
                if t.get('last_reaped') is True:
                    t['state'] = 'not_closed_timeout'
                    j['index'] += 1
                    if self.clock() >= j['deadline']:
                        self.finish(j, 'partial', 'deadline')
                    else:
                        self.dispatch_next(j)
                else:
                    self.uncertain(j, t, 'native_cleanup_unconfirmed')
                return self.busy()
            if not j.get('polling'):
                j['polling'] = True
                def received(a):
                    t['last_reaped'] = a.get('helper_reaped') is True
                    self.native_result(j, t, a)
                self.adapter(j, 'Status', (t['token'],), received,
                             lambda: self.uncertain(j, t, 'native_status_unavailable'))
        return True

    def status(self, request_id):
        j = self.job if self.job and self.job['id'] == request_id else self.history.get(request_id)
        return self.report(j) if j else json.dumps(dict(protocol=1, state='unknown', request_id=request_id))


def frontend(scope, managed_id, values):
    """One original bus connection spans preview and explicit confirmation.

    stdin/stdout are private pipes owned by the Bash CLI. EOF before CONFIRM
    performs no action. Accepted work is detached on Ctrl-C/console loss.
    """
    limits = settings(values)
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    from joetoo_kwin_rdp_launch import CallerIdentity
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus(private=True)
    pinned = None
    try:
        daemon = dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'), 'org.freedesktop.DBus')
        owner = str(daemon.GetNameOwner('org.joetoo.KWinBridge'))
        pinned = CallerIdentity(daemon.GetConnectionCredentials(owner))
        api = dbus.Interface(bus.get_object(owner, '/org/joetoo/KWinBridge', introspect=False), 'org.joetoo.KWinBridge')
        preview = payload(str(api.PrepareManagedClose(json.dumps(dict(protocol=1, scope=scope,
            managed_id=managed_id, settings=limits, terminal={k: os.environ.get(v, '') for k, v in
            (('service', 'KONSOLE_DBUS_SERVICE'), ('session', 'KONSOLE_DBUS_SESSION'), ('window', 'KONSOLE_DBUS_WINDOW'))})), timeout=limits['managed_close_prepare_timeout_ms']/1000)))
        print(json.dumps(preview), flush=True)
        if preview.get('state') != 'prepared':
            return 1
        import sys
        if sys.stdin.readline(32) != 'CONFIRM\n':
            return 1
        if not pinned.alive() or str(daemon.GetNameOwner('org.joetoo.KWinBridge')) != owner:
            return 1
        result = payload(str(api.CommitManagedClose(preview['request_id'], timeout=limits['managed_close_dbus_timeout_ms']/1000)))
        import select
        control = select.poll()
        control.register(sys.stdin.fileno(), select.POLLHUP | select.POLLERR)
        end = time.monotonic() + (limits['managed_close_total_timeout_ms'] + limits['managed_close_dbus_timeout_ms'])/1000
        while result.get('state') in ACTIVE and result.get('state') != 'cleanup_uncertain':
            if control.poll(0):
                return 130  # Issuer detached; accepted broker work continues.
            if time.monotonic() >= end or not pinned.alive() or str(daemon.GetNameOwner('org.joetoo.KWinBridge')) != owner:
                raise RuntimeError('accepted_result_unavailable')
            time.sleep(limits['managed_close_poll_ms']/1000)
            result = payload(str(api.ManagedCloseStatus(preview['request_id'], timeout=limits['managed_close_dbus_timeout_ms']/1000)))
        print(json.dumps(result), flush=True)
        return 0 if result.get('state') == 'succeeded' else 1
    finally:
        if pinned:
            pinned.close()
        bus.close()


if __name__ == '__main__':
    import sys
    try:
        if sys.argv[1:] == ['--defaults']:
            print(json.dumps(settings()), flush=True)
            raise SystemExit(0)
        if len(sys.argv) == 3 and sys.argv[1] == '--settings':
            print(json.dumps(settings(payload(sys.argv[2]))), flush=True)
            raise SystemExit(0)
        if len(sys.argv) != 4 or sys.argv[1] not in ('one', 'all'):
            raise ValueError('invalid close invocation')
        raise SystemExit(frontend(sys.argv[1], sys.argv[2], payload(sys.argv[3])))
    except KeyboardInterrupt:
        # Do not cancel a committed broker operation or signal any application.
        raise SystemExit(130)
    except BrokenPipeError:
        raise SystemExit(130)
    except Exception:
        try:
            print(json.dumps(dict(state='unresolved', reason='close_frontend_unavailable_or_detached')), flush=True)
        except OSError:
            pass
        raise SystemExit(1)
