#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real broker/registry/process/FD validation; fake local bus/KWin, no GUI/network."""
import importlib.util
import io
from contextlib import redirect_stderr
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_rdp_broker as broker_tests
from test_rdp_broker import APP, OTHER
from test_step1_3a import observation, WINDOW_ID


class PlacementTests(unittest.TestCase):
    def setUp(self):
        # Capture through cleanup too; production diagnostics remain enabled.
        self.log = io.StringIO()
        capture = redirect_stderr(self.log)
        capture.__enter__()
        self.addCleanup(capture.__exit__, None, None, None)
        self.f = broker_tests.SdlInterfaceTests()
        self.f.setUp()
        # The borrowed fixture guards registration-only behavior. Its final
        # assertions do not apply after an explicitly authorized placement.
        self.f._cleanups = [entry for entry in self.f._cleanups if entry[0] != self.f.finish]
        self.addCleanup(self.f.doCleanups)
        self.b = self.f.b
        # Registration is exercised through the actual public process/FD path.
        profile = getattr(self, 'profile', None)
        if profile:
            import os
            renderer = self.renderer
            env = patch.dict(os.environ)
            env.start(); self.addCleanup(env.stop)
            for key in ('SDL_RENDER_DRIVER', 'SDL_FRAMEBUFFER_ACCELERATION', 'SDL_VIDEODRIVER'):
                os.environ.pop(key, None)
            if renderer == 'software':
                os.environ.update(SDL_RENDER_DRIVER='software', SDL_FRAMEBUFFER_ACCELERATION='0')
            self.f.begin(payload=json.dumps(dict(protocol=1, desktop=3, slot=1,
                profile=profile, bounds=dict(rdp_x11_renderer=renderer))))
            self.f.spawn(backend='x11', driver='x11')
        else:
            self.f.begin(); self.f.spawn()
        self.f.bind(); self.f.event()
        if profile:
            self.f.poll()  # First complete qualification starts the dwell clock.
            self.f.clock += .501
        self.registered = self.f.poll()
        self.assertEqual(self.registered['state'], 'registered')
        self.mid = self.registered['managed_id']
        self.assertIsNone(self.b.request)
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'not_requested')
        self.f.patch(self.f.bus, 'GetNameOwner', lambda name, reply_handler, error_handler, timeout:
                     reply_handler(':1.kwin'), create=True)
        # _submit/_sync are guarded in the registration fixture; restore only
        # now, after proving registration itself caused no placement.
        self.b._submit = self.b.__class__._submit.__get__(self.b)
        self.b._sync_managed_placement = self.b.__class__._sync_managed_placement.__get__(self.b)
        self.reply, self.errors = [], []
        self.sender = ':1.operator'
        self.data = dict(protocol=1, confirmed=True, managed_id=self.mid, action_id='a' * 32,
            source='source', revision=self.f.revision, desktop=3, slot=1,
            x=25, y=35, width=800, height=600, timeout_ms=1000)
        self.addCleanup(self.cleanup)

    def cleanup(self):
        c = self.b._sdl_placement
        if c and not c.get('terminal'):
            self.b._sdl_placement_finish(c, 'failed', 'test cleanup')
        self.assertEqual(self.f.loop.callbacks, {})
        self.assertTrue(all(m.removed for m in self.f.bus.matches))
        self.f.submit.assert_not_called()
        self.f.place.assert_not_called()
        if self.f.child is not None:
            if not self.f.child.stdin.closed: self.f.child.stdin.close()
            self.f.child.wait(timeout=5)
            self.f.child.stderr.close()

    def submit(self, **changes):
        self.reply.clear(); self.errors.clear()
        payload = dict(self.data, **changes)
        self.b.SubmitSdlPlacement(json.dumps(payload), sender=self.sender,
                                  reply=self.reply.append, error=self.errors.append)
        return json.loads(self.reply[-1]) if self.reply else None

    def claim(self):
        return json.loads(self.b.TakeSdlPlacement('source', sender=':1.kwin'))

    def poll(self):
        return json.loads(self.b.PollSdlPlacement(self.b._sdl_placement['id'], sender=self.sender))

    def observe(self, kind='changed', identifier=WINDOW_ID, **changes):
        w = dict(self.b.observed_windows.get(identifier) or json.loads(observation(uuid=identifier))['window'])
        w.update(pid=self.f.child.pid, resource_class=APP, caption=self.f.marker)
        w.update(changes)
        self.f.revision += 1
        self.b.ObserveWindow(json.dumps(dict(source='source', revision=self.f.revision, event=kind, window=w)))
        return w

    def verification(self, request, uuid=WINDOW_ID):
        before = self.b.observed_windows[WINDOW_ID]
        captured = {k: before[k] for k in ('geometry', 'desktops', 'on_all_desktops')}
        resolved = dict(geometry={k: request[k] for k in ('x', 'y', 'width', 'height')},
                        desktops=[request['desktop']], on_all_desktops=False)
        return dict(window_uuid=uuid, source='source', before='before', tiled=False,
                    fullscreen=False, captured=captured, resolved=resolved)

    def complete(self, request, payload=None):
        self.b.Complete(request['id'], 'VERIFY', json.dumps(payload or self.verification(request)), sender=':1.kwin')

    def test_exact_uuid_success_and_original_launcher_child_remains_alive(self):
        accepted = self.submit()
        self.assertFalse(self.errors)
        self.assertEqual(accepted['placement'], 'pending')
        request = self.claim()
        self.assertEqual(request['window_uuid'], WINDOW_ID)
        self.complete(request)
        self.assertEqual(self.poll()['placement'], 'pending')
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        result = self.poll()
        self.assertEqual(result['placement'], 'succeeded')
        self.assertEqual(result['registration'], 'registered')
        self.assertEqual(result['remote_session'], 'unverified')
        self.assertEqual(result['window_uuid'], WINDOW_ID)
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'succeeded')
        self.assertIsNone(self.f.child.poll())
        self.assertEqual(self.f.poll(), self.registered)
        self.assertEqual(self.f.loop.callbacks, {})
        self.assertEqual(self.poll(), result)
        # Subsequent manual geometry is retained, never repaired by a timer.
        self.observe(geometry=dict(x=200, y=300, width=700, height=500))
        self.assertEqual(self.b.observed_windows[WINDOW_ID]['geometry']['x'], 200)
        self.assertEqual(self.poll(), result)

    def second_registration_after_placement(self, succeeded, slot=2):
        # One real broker/registry survives A's placement and closure and B's
        # actual development-launcher preflight, Begin/Bind/Poll and cleanup.
        self.submit(); request = self.claim()
        if succeeded:
            self.complete(request)
            self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
            self.assertEqual(self.poll()['placement'], 'succeeded')
        else:
            self.b.CancelSdlPlacement(request['id'], sender=self.sender)
            self.assertEqual(self.poll()['placement'], 'failed')
        context = self.b._sdl_placement
        self.assertFalse(context.get('cleanup_uncertain', False))
        self.assertFalse(any(k in context for k in ('timer', 'match', 'child', 'operator', 'launch_owner', 'kwin_identity')))
        self.observe('removed')
        self.f.child.stdin.close(); self.f.child.wait(timeout=5)
        original = self.b.registry.get_window(self.mid)
        self.assertEqual(original.presence, 'missing')
        history = self.b.request
        self.assertEqual(history['state'], 'OK' if succeeded else 'ERROR')
        self.assertIsNotNone(history['id'])
        spec = importlib.util.spec_from_file_location('sdl_sequential_launcher',
            Path(__file__).resolve().parents[1] / 'tools/joetoo-sdl-registration-launch.py')
        client = importlib.util.module_from_spec(spec); spec.loader.exec_module(client)
        test = self
        children, statuses, output = [], [], []
        polls = 0
        sender = ':1.next-launcher'
        class Bridge:
            def Introspect(self, **kw):
                return '<node><interface name="org.joetoo.KWinBridge">' + ''.join(
                    '<method name="' + name + '">' + ''.join('<arg type="' + c + '" direction="in"/>' for c in sig)
                    + '<arg type="s" direction="out"/></method>' for name, sig in
                    dict(BeginSdlRegistration='s', BindSdlRegistration='sih', PollSdlRegistration='s', CancelSdlRegistration='s').items()) + '</interface></node>'
            def RegistryStatus(self, **kw):
                result = test.b.RegistryStatus(); statuses.append(json.loads(result)); return result
            def BeginSdlRegistration(self, payload, **kw):
                replies, errors = [], []
                test.b.BeginSdlRegistration(payload, sender=sender, reply=replies.append, error=errors.append)
                if errors: raise errors[0]
                return replies[0]
            def BindSdlRegistration(self, rid, pid, fd, **kw):
                return test.b.BindSdlRegistration(rid, pid, test.f.FD(test.f.os.dup(fd.fd)), sender=sender)
            def PollSdlRegistration(self, rid, **kw):
                nonlocal polls
                polls += 1
                if polls == 2:
                    test.observe('added', OTHER, pid=children[0].pid,
                                 caption=test.b._rdp_registration['title_token'])
                result = test.b.PollSdlRegistration(rid, sender=sender)
                if json.loads(result)['state'] == 'registered':
                    children[0].stdin.close(); children[0].wait(timeout=5)
                return result
            def CancelSdlRegistration(self, rid, **kw):
                return test.b.CancelSdlRegistration(rid, sender=sender)
        bridge = Bridge()
        daemon = SimpleNamespace(GetNameOwner=lambda *a, **kw: ':1.broker')
        class Bus:
            connected = True
            def get_is_connected(self): return self.connected
            def get_object(self, name, path, **kw):
                return daemon if name == 'org.freedesktop.DBus' else bridge
            def close(self):
                self.connected = False
                for match in list(test.f.bus.matches):
                    if not match.removed: match.callback(sender, sender, '')
        def spawn(argv, **kw):
            import select
            code = ('import os,sys; print("[0] [%d:thread] [DEBUG][com.freerdp.client.SDL] - '
                    '[main]: client is using backend \'%s\'" % (os.getpid(),sys.argv[1]),flush=True); '
                    'print("ready",file=sys.stderr,flush=True); sys.stdin.read()')
            child = subprocess.Popen([sys.executable, '-c', code, kw['env']['SDL_VIDEO_DRIVER']],
                stdin=subprocess.PIPE, stdout=kw['stdout'], stderr=subprocess.PIPE, env=kw['env'], close_fds=True)
            children.append(child)
            self.assertTrue(select.select([child.stderr], [], [], 5)[0])
            self.assertEqual(child.stderr.readline(), b'ready\n')
            return child
        def wait(seconds): self.f.clock += seconds
        import tempfile
        with tempfile.TemporaryDirectory(prefix='sdl-sequential-test-') as folder:
            mkdtemp = client.tempfile.mkdtemp
            with patch.object(client.tempfile, 'mkdtemp', lambda **kw: mkdtemp(dir=folder, **kw)):
                try:
                    result = client.launch(Bus(), lambda obj, iface: obj,
                        lambda fd: self.f.FD(self.f.os.dup(fd)), self.f.adapter,
                        'example.invalid', 3389, 'testuser', 3, slot,
                        {'rdp_x11_renderer': self.renderer} if getattr(self, 'profile', None) else {},
                        emit=output.append, spawn=spawn, sleep=wait, clock=lambda: self.f.clock,
                        profile=getattr(self, 'profile', None))
                    self.assertEqual(result, 0)
                except RuntimeError as error:
                    if slot != 1: raise
                    self.assertIn('BeginSdlRegistration failed: org.joetoo.KWinBridge.Busy', str(error))
                    self.assertEqual(children, [])  # Slot refusal precedes spawn.
                    self.assertEqual(self.b.registry.get_window(self.mid), original)
                    self.assertIs(self.b.request, history)
                    self.assertIsNone(self.b.registry._active_request_id)
                    return 'slot_rejected'
                finally:
                    for child in children:
                        if not child.stdin.closed: child.stdin.close()
                        child.wait(timeout=5); child.stderr.close()
        registered = next(json.loads(line) for line in output if json.loads(line).get('state') == 'registered')
        second = self.b.registry.get_window(registered['managed_id'])
        self.assertNotEqual(second.managed_id, original.managed_id)
        self.assertNotEqual(second.request_id, original.request_id)
        self.assertEqual(second.window_uuid, OTHER)
        self.assertNotEqual(second.observation['pid'], original.observation['pid'])
        self.assertNotEqual(second.observation['caption'], original.observation['caption'])
        self.assertEqual(second.recipe['slot'], 2)
        self.assertEqual(second.placement, 'not_requested')
        self.assertEqual(self.b.registry.get_window(self.mid), original)
        self.assertIs(self.b.request, history)
        self.assertIs(self.b._sdl_placement, context)
        self.assertGreaterEqual(len(statuses), 2)  # Includes pending-monitor guard.
        self.assertTrue(all(s['placement_transaction'] == dict(id=history['id'], state=history['state']) for s in statuses))
        self.assertIsNone(self.b.registry._active_request_id)

    def test_second_launcher_after_verified_placement_and_close_without_restart(self):
        self.second_registration_after_placement(True)

    def test_second_launcher_cannot_reuse_closed_viewers_reserved_slot(self):
        self.assertEqual(self.second_registration_after_placement(True, slot=1), 'slot_rejected')

    def test_second_launcher_after_safely_failed_placement_without_restart(self):
        self.second_registration_after_placement(False)

    def test_resident_payload_drives_real_broker_verification_end_to_end(self):
        self.submit(); request = self.claim()
        # Execute real resident code inside Node's restricted fake KWin VM.
        run = subprocess.run(['node', str(Path(__file__).with_suffix('.js')), '--fixture'],
            input=json.dumps(request), text=True, capture_output=True, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.b.Complete(request['id'], result['state'], result.get('wire_detail', json.dumps(result['detail'])), sender=':1.kwin')
        self.observe(geometry=result['geometry'], desktops=result['desktops'])
        self.assertEqual(self.poll()['placement'], 'succeeded')
        self.assertEqual(result['uuid'], WINDOW_ID)
        self.assertEqual(result['unrelated_mutations'], 0)

    def test_invalid_policy_unknown_or_raw_uuid_never_arms(self):
        for fields in [dict(managed_id='win-999'), dict(managed_id=WINDOW_ID), dict(desktop=4),
                       dict(slot=2), dict(confirmed=False), dict(width=0), dict(x=True),
                       dict(timeout_ms=15001), dict(source='old'), dict(revision=0)]:
            with self.subTest(fields=fields):
                self.submit(**fields)
                self.assertTrue(self.errors)
                self.assertIsNone(self.b.request)
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'not_requested')

    def test_busy_and_initial_layout_conflicts(self):
        self.f.patch(self.b, '_initial_layout_active', lambda: True)
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)

    def test_stale_action_replay_is_rejected_after_cancellation(self):
        result = self.submit()
        first = json.loads(self.b.CancelSdlPlacement(result['request_id'], sender=self.sender))
        self.assertEqual(first['placement'], 'failed')
        self.assertIsNone(self.submit())
        self.assertTrue(self.errors)
        self.assertEqual(self.poll(), first)
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'failed')

    def test_unknown_id_and_foreign_sender_cannot_claim_poll_cancel_or_complete(self):
        result = self.submit()
        for fn, args in [(self.b.TakeSdlPlacement, ('source',)),
                         (self.b.PollSdlPlacement, (result['request_id'],)),
                         (self.b.CancelSdlPlacement, (result['request_id'],)),
                         (self.b.Complete, (result['request_id'], 'ERROR', 'forged'))]:
            with self.assertRaises(Exception): fn(*args, sender=':1.foreign')
        with self.assertRaises(Exception): self.b.PollSdlPlacement('unknown', sender=self.sender)
        self.assertEqual(self.poll()['placement'], 'pending')

    def test_late_completion_after_cancellation_is_inert(self):
        self.submit(); request = self.claim()
        first = json.loads(self.b.CancelSdlPlacement(request['id'], sender=self.sender))
        self.complete(request)
        self.assertEqual(self.poll(), first)
        self.assertEqual(self.b.request['state'], 'ERROR')

    def test_wrong_uuid_completion_does_not_succeed(self):
        self.submit(); request = self.claim()
        with self.assertRaises(Exception): self.complete(request, self.verification(request, OTHER))
        self.assertEqual(self.poll()['placement'], 'pending')
        self.f.clock += 1
        self.assertEqual(self.poll()['placement'], 'failed')

    def test_missing_or_uncertain_record_is_rejected(self):
        self.b.registry.set_presence(WINDOW_ID, 'uncertain')
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)

    def test_marker_loss_and_restoration_before_release_remains_invalid(self):
        self.observe(caption='lost'); self.observe(caption=self.f.marker)
        self.data['revision'] = self.f.revision
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)

    def test_mutation_source_loss_removal_and_expiry_during_placement(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.observe('removed')
        self.assertEqual(self.poll()['placement'], 'failed')
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'failed')
        self.assertEqual(self.f.poll(), self.registered)

    def test_source_replacement_after_claim_never_succeeds(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.b.SyncInventory(json.dumps(dict(source='replaced', revision=1, windows=[])))
        self.assertEqual(self.poll()['placement'], 'failed')

    def test_mechanical_deadline_expires_without_any_operator_poll(self):
        self.submit(); self.f.clock += 1; self.f.loop.tick()
        self.assertEqual(self.poll()['placement'], 'failed')
        self.assertEqual(self.f.loop.callbacks, {})
        self.assertIsNone(self.f.child.poll())

    def test_missing_processfd_cannot_authorize_placement(self):
        self.f.bus.process_fd = False
        result = self.submit()
        self.assertEqual(result['placement'], 'failed')
        self.assertIsNone(self.b.request)

    def test_pending_credentials_reserve_placement_against_initial_layout(self):
        self.f.bus.auto = False
        self.submit()
        with self.assertRaises(Exception): self.b.SubmitInitialLayout('{}')
        self.f.bus.auto = True
        self.f.bus.deliver()
        self.assertIsNotNone(self.b.request)

    def test_late_authentication_callbacks_cannot_arm_after_timeout(self):
        self.f.bus.auto = False
        self.submit(); self.f.clock += 1; self.f.loop.tick()
        result = self.poll()
        self.f.bus.deliver()
        self.assertEqual(self.poll(), result)
        self.assertIsNone(self.b.request)

    def test_pid_lifetime_and_original_owner_mismatch_are_rejected(self):
        meta = self.b._sdl_registered[self.mid]
        meta['start'] -= 1
        self.assertEqual(self.submit()['placement'], 'failed')
        self.assertIsNone(self.b.request)

    def test_original_launcher_connection_loss_fails_pending_placement(self):
        self.submit(); self.f.bus.lost()
        self.assertEqual(self.poll()['placement'], 'failed')
        self.assertIsNone(self.f.child.poll())


    def test_competing_uuid_and_pid_class_mutations_are_permanent_failures(self):
        self.observe('added', OTHER)
        self.data['revision'] = self.f.revision
        self.assertIsNone(self.submit())
        self.assertTrue(self.errors)
        self.assertIsNone(self.b.request)

    def test_class_mutation_during_claim_fails_without_verified_placement(self):
        self.submit(); self.claim()
        self.observe(resource_class='other')
        self.assertEqual(self.poll()['placement'], 'failed')

    def test_revision_gap_cannot_be_repaired_with_a_later_inventory(self):
        self.f.revision += 1
        self.observe()
        w = self.b.observed_windows[WINDOW_ID]
        self.f.revision += 1
        self.b.SyncInventory(json.dumps(dict(source='source', revision=self.f.revision, windows=[w])))
        self.data['revision'] = self.f.revision
        self.assertIsNone(self.submit())
        self.assertTrue(self.errors)

    def test_slot_conflict_and_changed_registry_request_are_rejected(self):
        record = self.b.registry.managed_windows[WINDOW_ID]
        record.request_id = 'other'
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)
        record.request_id = self.registered['request_id']
        from copy import deepcopy
        other = deepcopy(record)
        other.managed_id = 'win-999'; other.window_uuid = OTHER
        self.b.registry.managed_windows[OTHER] = other
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)
        self.assertIsNone(self.b.request)

    def test_live_generic_request_blocks_operator_action(self):
        self.b.request = dict(id='generic', state='RUNNING', kind='move')
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)
        self.assertEqual(self.b.request['id'], 'generic')

    def test_child_exit_during_placement_never_succeeds(self):
        self.submit(); self.claim()
        self.f.child.stdin.close(); self.f.child.wait(timeout=5)
        self.f.loop.tick()
        self.assertEqual(self.poll()['placement'], 'failed')

    def test_untrusted_operator_and_substituted_log_inode_are_rejected(self):
        self.f.bus.uid += 1
        self.assertEqual(self.submit()['placement'], 'failed')
        self.assertIsNone(self.b.request)
        self.f.bus.uid -= 1
        self.data['action_id'] = 'b' * 32
        self.b._sdl_registered[self.mid]['log_inode'] = (0, 0)
        self.assertEqual(self.submit()['placement'], 'failed')
        self.assertIsNone(self.b.request)

    def test_wrong_source_claim_and_kwin_owner_loss_fail_closed(self):
        self.submit()
        self.assertEqual(self.b.TakeSdlPlacement('old', sender=':1.kwin'), '')
        self.assertEqual(self.poll()['placement'], 'failed')
        self.data['action_id'] = 'b' * 32
        self.submit()
        for match in self.f.bus.matches:
            if not match.removed: match.callback('org.kde.KWin', ':1.kwin', ':1.new')
        self.assertEqual(self.poll()['placement'], 'failed')

    def test_cleanup_failure_remains_owned_and_blocks_new_work(self):
        self.submit()
        match = self.b._sdl_placement['match']
        original = match.remove
        self.f.patch(match, 'remove', lambda: (_ for _ in ()).throw(OSError('cleanup fault')))
        result = json.loads(self.b.CancelSdlPlacement(self.b._sdl_placement['id'], sender=self.sender))
        self.assertTrue(self.b._sdl_placement['cleanup_uncertain'])
        self.assertEqual(result['placement'], 'failed')
        self.assertEqual(self.b.request['state'], 'ERROR')
        self.assertEqual(self.b._sdl_placement['unreleased'], [('match', match)])
        self.data['action_id'] = 'b' * 32
        self.assertIsNone(self.submit()); self.assertTrue(self.errors)
        with self.assertRaises(Exception): self.b.Submit(3, 0, 0, 100, 100)
        self.assertEqual(self.poll(), result)
        original()  # Dispose only our fake match; production uncertainty remains.


class PlacementDiagnosticTests(unittest.TestCase):
    # Real Linux process/FD validators, synthetic transport/scheduling/faults.
    # Labels diagnose rejection boundaries; no native KWin permissions are inferred.
    cleanup = PlacementTests.cleanup
    submit = PlacementTests.submit
    observe = PlacementTests.observe

    def setUp(self):
        PlacementTests.setUp(self)

    def inject(self, fault):
        def private_error(*args, **kw): raise PermissionError('PRIVATE-DO-NOT-LOG')
        meta = self.b._sdl_registered[self.mid]
        if fault.startswith('credentials_'):
            _, index, kind = fault.split('_'); index = int(index)
            original = self.f.bus.GetConnectionCredentials
            calls = 0
            def credentials(name, reply_handler, error_handler, timeout):
                nonlocal calls
                calls += 1
                if calls != index: return original(name, reply_handler, error_handler, timeout)
                if kind == 'request': return private_error()
                if kind == 'reply': return error_handler(RuntimeError('PRIVATE-DO-NOT-LOG'))
                # ProcessFD is transferred normally, but the UID is rejected
                # by the real CallerIdentity; it must close the transferred FD.
                value = self.f.bus.credentials(); value['UnixUserID'] += 1
                return reply_handler(value)
            self.f.patch(self.f.bus, 'GetConnectionCredentials', credentials)
        elif fault == 'kwin_proc_permission':
            self.denied_exe_lookups = []
            original = self.f.bus.GetConnectionCredentials
            calls = 0
            inode = self.f.adapter._inode
            def credentials(name, **kw):
                nonlocal calls
                calls += 1
                if calls == 3:
                    def denied(path):
                        if path == '/proc/' + str(self.f.os.getpid()) + '/exe':
                            self.denied_exe_lookups.append(path)
                            return private_error()
                        return inode(path)
                    self.f.patch(self.f.adapter, '_inode', denied)
                return original(name, **kw)
            self.f.patch(self.f.bus, 'GetConnectionCredentials', credentials)
        elif fault in ('revision', 'record'):
            def owner(name, reply_handler, **kw):
                if fault == 'revision': self.observe()  # Valid event; no identity mutation.
                else: meta['invalid'] = True
                reply_handler(':1.kwin')
            self.f.patch(self.f.bus, 'GetNameOwner', owner)
        elif fault in ('owner_name', 'owner_request', 'owner_reply'):
            def owner(name, reply_handler, error_handler, **kw):
                if fault == 'owner_request': return private_error()
                if fault == 'owner_reply': return error_handler(RuntimeError('PRIVATE-DO-NOT-LOG'))
                reply_handler('org.kde.KWin')
            self.f.patch(self.f.bus, 'GetNameOwner', owner)
        elif fault in ('owner_pid', 'owner_start', 'child_start'):
            key = {'owner_pid': 'owner_pid', 'owner_start': 'owner_start', 'child_start': 'start'}[fault]
            meta[key] -= 1
        elif fault == 'child_proc':
            original = self.f.adapter._proc_info
            self.f.patch(self.f.adapter, '_proc_info', lambda pid, **kwargs:
                private_error() if pid == self.f.child.pid else original(pid, **kwargs))
        elif fault == 'stdout_open':
            original = self.f.os.open
            self.f.patch(self.f.os, 'open', lambda path, *a, **kw:
                private_error() if path == '/proc/' + str(self.f.child.pid) + '/fd/1' else original(path, *a, **kw))
        elif fault == 'stdout_stat':
            self.f.patch(self.f.os, 'fstat', lambda fd: SimpleNamespace(st_mode=0))
        elif fault == 'stdout_inode': meta['log_inode'] = (0, 0)
        elif fault == 'log_mode': self.f.os.fchmod(self.f.log.fileno(), 0o640)
        elif fault == 'log_budget':
            self.f.os.ftruncate(self.f.log.fileno(), meta['bounds']['rdp_backend_log_byte_limit'] + 1)
        elif fault in ('child_snapshot', 'deadline'):
            original = self.f.adapter.ChildIdentity
            def identity(*args, **kw):
                child = original(*args, **kw)
                if fault == 'child_snapshot': child.start -= 1
                else: self.f.clock += 2
                return child
            self.f.patch(self.f.adapter, 'ChildIdentity', identity)
        elif fault.startswith('guard_'):
            original = self.b._sdl_placement_valid
            def valid(c):
                key = fault[6:]
                if key == 'record': c['meta']['invalid'] = True
                elif key == 'bus': self.f.bus.connected = False
                elif key == 'child': c['child'].poll = lambda: 1
                else: c[key].alive = lambda: False
                return original(c)
            self.f.patch(self.b, '_sdl_placement_valid', valid)
        elif fault == 'bus_proxy': self.f.patch(self.f.module.dbus, 'Interface', private_error)
        elif fault == 'owner_watch': self.f.patch(self.f.bus, 'add_signal_receiver', private_error)
        elif fault == 'watchdog': self.f.patch(self.f.module.GLib, 'timeout_add', lambda *a: 0)
        elif fault == 'submit': self.f.patch(self.b, '_submit', private_error)
        else: raise AssertionError(fault)

    def failed_at(self, stage):
        c = self.b._sdl_placement
        result = dict(c['terminal'])
        self.assertEqual(result['placement'], 'failed')
        reason = {'auth_deadline': 'Placement authentication deadline expired',
                  'owner_changed': 'Placement bus owner changed'}.get(stage, 'Placement authentication/source unavailable')
        self.assertEqual(result['reason'], reason)
        legacy = [line for line in self.log.getvalue().splitlines() if line.startswith('joetoo-kwind: SDL placement preflight failed stage=')]
        self.assertEqual(legacy, ['joetoo-kwind: SDL placement preflight failed stage=' + stage])
        self.assertIsNone(self.b.request)
        self.assertIsNone(self.f.child.poll())
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'not_requested')
        self.assertEqual(self.f.loop.callbacks, {})
        self.assertTrue(all(m.removed for m in self.f.bus.matches))
        self.assertFalse(any(k in c for k in ('child', 'operator', 'launch_owner', 'kwin_identity')))
        # Internal idempotence only. A disconnected sender cannot make a new
        # external Poll call; late timer/authentication outcomes remain inert.
        self.b._sdl_placement_finish(c, 'failed', 'late private exception')
        self.assertEqual(c['terminal'], result)
        self.assertEqual(self.log.getvalue().count('stage='), 1)

    def test_kwin_exe_denial_does_not_block_real_wayland_authorization_or_placement(self):
        self.inject('kwin_proc_permission')
        self.assertEqual(self.submit()['placement'], 'pending')
        request = PlacementTests.claim(self)
        payload = PlacementTests.verification(self, request)
        self.b.Complete(request['id'], 'VERIFY', json.dumps(payload), sender=':1.kwin')
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        result = json.loads(self.b.PollSdlPlacement(request['id'], sender=self.sender))
        self.assertEqual(result['placement'], 'succeeded')
        self.assertEqual(result['window_uuid'], WINDOW_ID)
        self.assertEqual(self.denied_exe_lookups, [])
        self.assertNotIn('preflight failed', self.log.getvalue())

    def test_missing_auth_callback_expires_and_late_fd_is_discarded(self):
        self.f.bus.auto = False
        self.submit(); self.f.clock += 2; self.f.loop.tick()
        self.failed_at('auth_deadline')
        value = self.f.bus.credentials(); fd = value['ProcessFD'].fd
        reply, _ = self.f.bus.pending.pop(0); reply(value)
        with self.assertRaises(OSError): self.f.os.fstat(fd)
        self.failed_at('auth_deadline')

    def test_owner_loss_during_auth_is_distinct(self):
        self.f.bus.auto = False
        self.submit(); self.f.bus.lost()
        self.failed_at('owner_changed')

    def test_success_is_silent_and_schema_errors_do_not_claim_auth_failure(self):
        self.submit(managed_id='win-999')
        self.assertTrue(self.errors); self.assertEqual(self.log.getvalue(), '')
        self.assertEqual(self.submit()['placement'], 'pending')
        self.assertNotIn('preflight failed', self.log.getvalue())

    def test_diagnostic_sink_failure_cannot_bypass_terminal_cleanup(self):
        self.f.bus.process_fd = False
        with patch('builtins.print', side_effect=OSError('sink unavailable')):
            self.assertEqual(self.submit()['placement'], 'failed')
        self.assertIsNone(self.b.request)
        self.assertEqual(self.f.loop.callbacks, {})
        self.assertFalse(self.b._sdl_placement.get('cleanup_uncertain'))


class LatePlacementTraceTests(unittest.TestCase):
    setUp = PlacementDiagnosticTests.setUp
    cleanup = PlacementTests.cleanup
    submit = PlacementTests.submit
    claim = PlacementTests.claim
    poll = PlacementTests.poll
    observe = PlacementTests.observe
    verification = PlacementTests.verification
    complete = PlacementTests.complete

    def rows(self):
        prefix = 'joetoo-kwind: SDL placement diagnostic '
        return [json.loads(line[len(prefix):]) for line in self.log.getvalue().splitlines() if line.startswith(prefix)]

    def stage(self, name): return [r for r in self.rows() if r['stage'] == name]

    def expire(self):
        self.f.clock += 1
        self.f.loop.tick()
        result = self.poll()
        self.assertIn(result['reason'], ('Placement claim deadline expired',
            'Placement completion deadline expired', 'Placement geometry confirmation timed out'))
        return result

    def test_unclaimed_pending_phase_and_deadline_are_preserved(self):
        self.submit(); result = self.expire()
        row = self.stage('terminal')[0]
        self.assertEqual(row['phase'], 'PENDING')
        self.assertEqual(row['guard'], 'placement_deadline')
        self.assertTrue(row['deadline_expired'])
        self.assertEqual(row['receipt_elapsed_ms'], 1000)
        self.assertEqual(self.stage('take_accepted'), [])
        self.assertEqual(self.poll(), result)

    def test_claimed_uncompleted_running_is_distinct(self):
        self.submit(); self.claim(); self.expire()
        self.assertEqual(self.stage('terminal')[0]['phase'], 'RUNNING')
        self.assertEqual(len(self.stage('take_accepted')), 1)
        self.assertEqual(self.stage('complete_received'), [])

    def test_verifying_nonconvergence_reports_geometry_timeout(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.assertEqual(self.b.request['state'], 'VERIFYING')
        self.expire()
        row = self.stage('terminal_begin')[0]
        self.assertEqual(row['phase'], 'VERIFYING')
        self.assertEqual(row['guard'], 'placement_deadline')
        self.assertFalse(row['geometry_match'])
        self.assertTrue(row['desktop_match'])
        self.assertEqual(len(self.stage('complete_accepted')), 1)
        self.assertEqual(len(self.stage('verifying_entered')), 1)

    def test_observation_after_failure_is_passive_and_not_a_success(self):
        self.submit(); request = self.claim(); self.complete(request)
        result = self.expire()
        self.f.clock += .25
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        late = self.stage('post_observation')[-1]
        self.assertTrue(late['geometry_match']); self.assertTrue(late['after_terminal'])
        self.assertEqual(late['causality'], 'unproven')
        self.assertEqual(late['receipt_elapsed_ms'], 1250)
        self.assertEqual(late['window_uuid'], WINDOW_ID)
        self.assertEqual(self.poll(), result)
        self.assertEqual(self.b.request['state'], 'ERROR')
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'failed')

    def test_success_reports_actual_frame_and_no_repair_after_manual_move(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        result = self.poll()
        self.assertEqual(result['placement'], 'succeeded')
        self.assertTrue(self.stage('terminal')[0]['geometry_match'])
        self.observe(geometry=dict(x=400, y=90, width=800, height=600))
        self.assertEqual(self.poll(), result)
        self.assertFalse(self.stage('post_observation')[-1]['geometry_match'])
        self.assertEqual(self.b.observed_windows[WINDOW_ID]['geometry']['x'], 400)

    def test_wrong_sender_and_wrong_uuid_completions_are_rejected(self):
        self.submit(); request = self.claim()
        with self.assertRaises(Exception): self.b.TakeSdlPlacement('source', sender='foreign-private')
        with self.assertRaises(Exception):
            self.b.Complete(request['id'], 'VERIFY', 'private exception data', sender='foreign-private')
        with self.assertRaises(Exception):
            self.complete(request, self.verification(request, OTHER))
        self.assertTrue(self.stage('take_rejected'))
        self.assertTrue(self.stage('complete_rejected'))
        self.assertEqual([r['sender_matches'] for r in self.stage('complete_received')], [False, True])
        self.assertEqual(self.b.request['state'], 'RUNNING')
        self.assertEqual(self.stage('complete_accepted'), [])
        self.assertNotIn('foreign-private', self.log.getvalue())
        self.assertNotIn('private exception data', self.log.getvalue())

    def test_wrapped_error_preserves_exact_original_detail_and_redacts_stages(self):
        self.submit(); request = self.claim()
        original = 'PRIVATE caption destination arguments'
        finish = self.b._sdl_placement_finish
        seen = []
        def inspect_detail(*args):
            seen.append(self.b.request['detail'])
            return finish(*args)
        with patch.object(self.b, '_sdl_placement_finish', inspect_detail):
            self.b.Complete(request['id'], 'ERROR', json.dumps(dict(sdl_diagnostic=['PRIVATE stage'], detail=original)), sender=':1.kwin')
        self.assertEqual(seen, [original])
        self.assertEqual(self.poll()['reason'], 'Placement resident reported ERROR')
        self.assertEqual(self.stage('complete_accepted')[0]['result'], 'ERROR')
        self.assertNotIn('PRIVATE', self.log.getvalue())

    def test_late_resident_report_cannot_revive_or_prove_late_assignment(self):
        self.submit(); request = self.claim(); result = self.expire()
        detail = json.dumps(dict(sdl_diagnostic=['uuid_selected', 'assignment_attempt', 'assignment_returned'],
                                 detail=json.dumps(self.verification(request))))
        self.f.clock += .25
        self.b.Complete(request['id'], 'VERIFY', detail, sender=':1.kwin')
        self.assertTrue(self.stage('resident_assignment_attempt')[0]['after_terminal'])
        self.assertEqual(self.stage('resident_assignment_attempt')[0]['receipt_elapsed_ms'], 1250)
        self.assertTrue(self.stage('complete_rejected'))
        self.assertEqual(self.poll(), result)
        self.assertEqual(self.b.request['state'], 'ERROR')

    def test_real_resident_code_can_be_replayed_after_simulated_broker_failure_without_revival(self):
        self.submit(); request = self.claim(); result = self.expire()
        # Deliberately independent fake clocks: replay a previously issued Take
        # reply in the real resident VM after the simulated broker has failed.
        # This demonstrates trace handling, not real Qt scheduling or clock skew.
        run = subprocess.run(['node', str(Path(__file__).with_suffix('.js')), '--fixture'],
            input=json.dumps(request), text=True, capture_output=True, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        resident = json.loads(run.stdout)
        self.b.Complete(request['id'], resident['state'], resident['wire_detail'], sender=':1.kwin')
        self.observe(geometry=resident['geometry'], desktops=resident['desktops'])
        self.assertTrue(self.stage('resident_assignment_attempt')[0]['after_terminal'])
        self.assertTrue(self.stage('post_observation')[0]['geometry_match'])
        self.assertEqual(self.poll(), result)
        self.assertEqual(resident['unrelated_mutations'], 0)

    def test_late_report_for_old_request_never_changes_a_new_request(self):
        self.submit(); first = self.claim(); self.expire()
        self.data['action_id'] = 'b' * 32
        self.submit(); second = self.b.request
        with self.assertRaises(Exception): self.complete(first)
        self.assertIs(self.b.request, second)
        self.assertEqual(second['state'], 'PENDING')
        late = self.stage('complete_received')[-1]
        self.assertEqual(late['request_id'], first['id'])
        self.assertTrue(late['after_terminal'])

    def test_post_capture_count_time_and_unrelated_uuid_bounds(self):
        self.b._sdl_registered[self.mid]['bounds']['rdp_registration_window_limit'] = 2
        self.submit(); self.expire()
        self.observe('added', OTHER, pid=999, caption='PRIVATE unrelated')
        self.assertEqual(self.stage('post_observation'), [])
        for x in range(5): self.observe(geometry=dict(x=x, y=0, width=800, height=600))
        self.assertEqual(len(self.stage('post_observation')), 2)
        self.assertEqual(len(self.stage('post_observation_limit')), 1)
        before = self.log.getvalue()
        self.f.clock += 121
        self.observe(geometry=dict(x=90, y=0, width=800, height=600))
        self.assertEqual(self.log.getvalue(), before)
        self.assertNotIn('PRIVATE', before)

    def test_post_capture_horizon_is_independent_of_placement_deadline(self):
        self.submit(); self.expire()
        self.f.clock += self.b._sdl_placement['trace']['post_ms'] / 1000 + 1
        self.observe(geometry=dict(x=90, y=0, width=800, height=600))
        self.assertEqual(self.stage('post_observation'), [])
        self.assertEqual(self.b.request['state'], 'ERROR')

    def test_post_source_replacement_stops_old_uuid_capture(self):
        self.submit(); result = self.expire()
        self.b.SyncInventory(json.dumps(dict(source='new', revision=1,
            windows=[self.b.observed_windows[WINDOW_ID]])))
        self.assertEqual(len(self.stage('post_source_changed')), 1)
        self.assertEqual(self.stage('post_observation'), [])
        self.assertEqual(self.poll(), result)

    def test_owner_loss_is_not_misreported_as_deadline_in_trace(self):
        self.submit(); self.claim(); self.f.bus.lost()
        row = self.stage('terminal')[0]
        self.assertEqual(row['guard'], 'owner_changed')
        self.assertFalse(row['deadline_expired'])
        self.assertEqual(row['phase'], 'RUNNING')

    def test_source_loss_has_guard_record_and_keeps_public_outcome(self):
        self.submit(); self.claim()
        self.b.SyncInventory(json.dumps(dict(source='replaced', revision=1, windows=[])))
        self.assertEqual(self.poll()['placement'], 'failed')
        self.assertEqual(self.stage('terminal')[0]['guard'], 'guard_record')
        self.assertFalse(self.stage('terminal')[0]['deadline_expired'])

    def test_child_exit_has_guard_child_without_reviving_registration(self):
        self.submit(); self.claim()
        self.f.child.stdin.close(); self.f.child.wait(timeout=5)
        self.f.loop.tick()
        self.assertEqual(self.poll()['placement'], 'failed')
        self.assertEqual(self.stage('terminal')[0]['guard'], 'guard_child')
        self.assertEqual(self.f.poll(), self.registered)

    def test_trace_budget_is_bounded_but_terminal_is_always_retained(self):
        self.submit(); trace = self.b._sdl_placement['trace']; trace['limit'] = 16
        for i in range(100): self.b._sdl_trace(trace, 'post_observation', present=True)
        self.assertEqual(len(self.stage('trace_limit')), 1)
        self.expire()
        self.assertEqual(len(self.stage('terminal')), 1)
        self.assertLessEqual(len(self.rows()), 18)
        self.assertLess(len(self.log.getvalue()), 20000)



def placement_diagnostic_case(fault, stage):
    def test(self):
        self.inject(fault); self.submit(); self.failed_at(stage)
    return test


for _index, _key in ((1, 'operator'), (2, 'launch_owner'), (3, 'kwin_identity')):
    for _kind in ('request', 'reply', 'verify'):
        setattr(PlacementDiagnosticTests, 'test_credentials_' + str(_index) + '_' + _kind,
            placement_diagnostic_case('credentials_' + str(_index) + '_' + _kind, _key + '_credentials_' + _kind))
for _fault, _stage in (
        ('revision', 'revision_recheck'), ('record', 'record_recheck'),
        ('owner_name', 'kwin_owner_name'), ('owner_request', 'kwin_owner_request'), ('owner_reply', 'kwin_owner_reply'),
        ('owner_pid', 'launcher_pid_recheck'), ('owner_start', 'launcher_start_recheck'),
        ('child_proc', 'child_identity'), ('child_start', 'child_snapshot'),
        ('stdout_open', 'stdout_open'), ('stdout_stat', 'stdout_stat'), ('stdout_inode', 'stdout_inode'),
        ('log_mode', 'child_identity'), ('log_budget', 'child_identity'),
        ('child_snapshot', 'child_snapshot'), ('deadline', 'deadline_recheck'),
        ('bus_proxy', 'bus_proxy'), ('owner_watch', 'owner_watch'), ('watchdog', 'watchdog_setup'), ('submit', 'submit')):
    setattr(PlacementDiagnosticTests, 'test_stage_' + _fault, placement_diagnostic_case(_fault, _stage))
for _key in ('record', 'operator', 'launch_owner', 'kwin_identity', 'child', 'bus'):
    # Log names describe public roles; dictionary keys retain existing names.
    _stage = {'launch_owner': 'launcher', 'kwin_identity': 'kwin'}.get(_key, _key)
    setattr(PlacementDiagnosticTests, 'test_guard_' + _key, placement_diagnostic_case('guard_' + _key, 'guard_' + _stage))


class ConsolidatedPlacementTests(unittest.TestCase):
    """Real broker/registry and Linux identity checks; simulated bus/time only."""
    setUp = PlacementTests.setUp
    cleanup = PlacementTests.cleanup
    submit = PlacementTests.submit
    claim = PlacementTests.claim
    poll = PlacementTests.poll
    observe = PlacementTests.observe
    verification = PlacementTests.verification
    complete = PlacementTests.complete

    def test_authentication_claim_and_verify_share_original_deadline(self):
        started = self.f.clock
        credentials = self.f.bus.GetConnectionCredentials
        def delayed(*args, **kwargs):
            self.f.clock += .125
            return credentials(*args, **kwargs)
        with patch.object(self.f.bus, 'GetConnectionCredentials', delayed):
            self.submit()
        r = self.b.request
        self.assertGreater(r['created'], started)
        self.assertEqual(r['placement_deadline'], started + 1)
        self.assertEqual(r['placement_deadline'], self.b._sdl_placement['deadline'])
        request = self.claim(); self.complete(request)
        self.f.clock = started + .999
        self.assertEqual(self.poll()['placement'], 'pending')
        self.f.clock = started + 1
        result = self.poll()
        self.assertEqual(result['reason'], 'Placement geometry confirmation timed out')
        self.assertNotIn('identity', result['reason'])
        self.assertEqual(self.b.request['state'], 'ERROR')
        self.assertEqual(self.poll(), result)

    def test_one_runtime_guard_pass_per_poll_without_provenance_reconstruction(self):
        self.submit()
        c = self.b._sdl_placement
        with patch.object(c['child'], 'poll', wraps=c['child'].poll) as child, \
             patch.object(c['launch_owner'], 'alive', wraps=c['launch_owner'].alive) as owner, \
             patch.object(self.f.adapter, 'ChildIdentity', side_effect=AssertionError('reconstruction')):
            self.assertEqual(self.poll()['placement'], 'pending')
        self.assertEqual(child.call_count, 1)
        self.assertEqual(owner.call_count, 1)  # Checked inside ChildIdentity.poll.

    def test_deadline_at_claim_is_terminal_without_geometry_authorization(self):
        self.submit(); self.f.clock += 1
        self.assertEqual(self.b.TakeSdlPlacement('source', sender=':1.kwin'), '')
        self.assertEqual(self.poll()['reason'], 'Placement claim deadline expired')

    def test_complete_at_deadline_cannot_open_a_new_verification_budget(self):
        self.submit(); request = self.claim()
        self.f.clock += 1
        self.complete(request)
        self.assertEqual(self.poll()['reason'], 'Placement completion deadline expired')
        self.assertEqual(self.b.request['state'], 'ERROR')

    def test_exact_frame_after_deadline_does_not_turn_timeout_into_success(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.f.clock += 1
        # Even if the observation callback runs before the watchdog callback.
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        result = self.poll()
        self.assertEqual(result['reason'], 'Placement geometry confirmation timed out')
        self.assertEqual(result['placement'], 'failed')
        self.f.loop.tick()
        self.assertEqual(self.poll(), result)

    def test_position_only_match_is_never_full_frame_success(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.observe(geometry=dict(x=25, y=35, width=1024, height=796), desktops=[3])
        self.assertEqual(self.poll()['placement'], 'pending')
        self.f.clock += 1
        self.assertEqual(self.poll()['reason'], 'Placement geometry confirmation timed out')
        rows = [json.loads(line.split('diagnostic ', 1)[1]) for line in self.log.getvalue().splitlines()
                if 'SDL placement diagnostic ' in line]
        terminal = next(row for row in rows if row['stage'] == 'terminal')
        self.assertTrue(terminal['position_match'])
        self.assertTrue(terminal['desktop_match'])
        self.assertFalse(terminal['size_match'])
        self.assertFalse(terminal['geometry_match'])
        self.assertFalse(terminal['guard_failed'])

    def test_late_old_completion_and_frame_cannot_complete_new_unclaimed_request(self):
        self.submit(); first = self.claim(); self.complete(first)
        self.f.clock += 1
        old = self.poll()
        self.submit(action_id='b' * 32, x=300, y=160)
        second = self.b.request
        self.assertEqual(second['state'], 'PENDING')
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        with self.assertRaises(Exception): self.complete(first)
        self.assertIs(self.b.request, second)
        self.assertEqual(second['state'], 'PENDING')
        self.assertEqual(old['placement'], 'failed')
        request = self.claim(); self.complete(request)
        self.assertEqual(self.poll()['placement'], 'pending')
        self.observe(geometry=dict(x=300, y=160, width=800, height=600), desktops=[3])
        self.assertEqual(self.poll()['placement'], 'succeeded')

    def test_terminal_ok_history_survives_next_submit_and_is_not_reauthorized(self):
        self.submit(); request = self.claim(); self.complete(request)
        self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        self.assertEqual(self.poll()['placement'], 'succeeded')
        previous = self.b.request
        accepted = self.submit(action_id='b' * 32, revision=self.f.revision)
        self.assertEqual(accepted['placement'], 'pending')
        self.assertFalse(self.errors)
        self.assertEqual(previous['state'], 'OK')
        self.assertEqual(previous['detail'].split(':', 1)[0], 'sdl')
        self.assertNotEqual(self.b.request['id'], previous['id'])

    def test_verified_geometry_with_uncertain_cleanup_is_failed_and_blocks_reuse(self):
        self.submit(); request = self.claim(); self.complete(request)
        c = self.b._sdl_placement
        match = c['match']
        remove = match.remove
        with patch.object(match, 'remove', side_effect=OSError('PRIVATE cleanup')):
            self.observe(geometry=dict(x=25, y=35, width=800, height=600), desktops=[3])
        self.assertEqual(self.poll()['reason'], 'Placement cleanup incomplete')
        self.assertTrue(c['cleanup_uncertain'])
        self.assertEqual(c['unreleased'], [('match', match)])
        self.assertEqual(self.b.request['state'], 'ERROR')
        self.assertEqual(self.b.registry.get_window(self.mid).placement, 'failed')
        self.assertIsNone(self.submit(action_id='b' * 32))
        self.assertTrue(self.errors)
        self.assertNotIn('PRIVATE', self.log.getvalue())
        remove()  # Fixture releases its deliberately faulted resource.

    def test_identity_loss_has_distinct_reason_and_original_request_phase(self):
        self.submit(); self.claim()
        c = self.b._sdl_placement
        with patch.object(c['operator'], 'alive', return_value=False):
            self.assertEqual(self.poll()['reason'], 'Placement operator lost')
        rows = [json.loads(line.split('diagnostic ', 1)[1]) for line in self.log.getvalue().splitlines()
                if 'SDL placement diagnostic ' in line]
        terminal = next(row for row in rows if row['stage'] == 'terminal')
        self.assertEqual(terminal['phase'], 'RUNNING')
        self.assertTrue(terminal['guard_failed'])
        self.assertFalse(terminal['deadline_expired'])


class X11PlacementTests(unittest.TestCase):
    # Exercise the same public registration/release path with both accepted
    # child profiles, without running SDL or weakening the 500 ms heuristic.
    setUp = PlacementTests.setUp
    cleanup = PlacementTests.cleanup
    submit = PlacementTests.submit
    claim = PlacementTests.claim
    poll = PlacementTests.poll
    observe = PlacementTests.observe
    complete = PlacementTests.complete
    verification = PlacementTests.verification
    profile = 'sdl-x11-a1c-v1'
    renderer = 'auto'
    second_registration_after_placement = PlacementTests.second_registration_after_placement

    def test_second_launcher_after_completed_x11_placement_without_restart(self):
        self.second_registration_after_placement(True)

    def test_x11_auto_registration_then_explicit_exact_uuid_placement(self):
        PlacementTests.test_exact_uuid_success_and_original_launcher_child_remains_alive(self)


class SoftwarePlacementTests(X11PlacementTests):
    renderer = 'software'


class OperatorClientTests(unittest.TestCase):
    def setUp(self):
        capture = redirect_stderr(io.StringIO())
        capture.__enter__()
        self.addCleanup(capture.__exit__, None, None, None)
        spec = importlib.util.spec_from_file_location('sdl_release_test',
            Path(__file__).resolve().parents[1] / 'tools/joetoo-sdl-release-placement.py')
        self.client = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.client)
        self.calls, self.output, self.shortcuts = [], [], []
        self.clock = 100.
        self.result = dict(protocol=1, request_id='a' * 32, managed_id='win-001',
            window_uuid=WINDOW_ID, registration='registered', remote_session='unverified', placement='pending')
        self.mode = 'success'
        outer = self
        class Bus:
            closed = False
            def close(self): self.closed = True
            def get_object(self, name, path, **kw):
                outer.assertEqual(name, ':1.accel')
                outer.assertEqual(path, '/component/kwin')
                return SimpleNamespace(invokeShortcut=lambda key, **kw: outer.shortcuts.append(key))
        self.bus = Bus()
        class API:
            def __init__(self, bus, interface, timeout):
                outer.assertIs(bus, outer.bus)
                self.daemon = SimpleNamespace(GetNameOwner=lambda name, **kw: ':1.accel')
            def call(self, name, *args):
                outer.calls.append((name, args))
                if name == 'RegistryStatus':
                    return dict(observation=dict(source='source', revision=9))
                if name == 'SubmitSdlPlacement': return dict(outer.result)
                if name == 'PollSdlPlacement':
                    result = dict(outer.result)
                    if outer.mode == 'success': result['placement'] = 'succeeded'
                    if outer.mode == 'wrong_uuid': result['window_uuid'] = OTHER
                    if outer.mode == 'unknown': result['placement'] = 'unknown'
                    if outer.mode == 'owner_loss': raise RuntimeError('Broker owner changed')
                    return result
                if name == 'CancelSdlPlacement': return dict(outer.result, placement='failed')
                raise AssertionError(name)
        self.patcher = patch.object(self.client.connection, 'Connection', API)
        self.patcher.start(); self.addCleanup(self.patcher.stop)

    def run_client(self, confirmed=True):
        def sleep(seconds): self.clock += seconds
        return self.client.release(self.bus, lambda obj, iface: obj, 'win-001', 3, 1,
            dict(x=25, y=35, width=800, height=600), confirmed=confirmed,
            timeout_ms=1000, poll_ms=100, call_timeout_ms=1000,
            emit=self.output.append, sleep=sleep, clock=lambda: self.clock)

    def test_operator_confirmation_and_same_connection_exact_result(self):
        self.assertEqual(self.run_client(), 0)
        payload = json.loads(self.calls[1][1][0])
        self.assertEqual(payload['managed_id'], 'win-001')
        self.assertNotIn('window_uuid', payload)
        self.assertEqual(payload['revision'], 9)
        self.assertEqual(self.shortcuts, ['joetoo_bridge_sdl_placement'])
        self.assertEqual(json.loads(self.output[-1])['window_uuid'], WINDOW_ID)
        self.assertTrue(self.bus.closed)
        self.assertFalse(any(name == 'CancelSdlPlacement' for name, _ in self.calls))

    def test_delayed_shortcut_fetches_broker_terminal_result_before_local_watchdog(self):
        self.mode = 'timeout'
        self.result.update(placement='failed', reason='Placement completion deadline expired')
        api_type = self.client.connection.Connection
        original_call = api_type.call
        def call(api, name, *args):
            result = original_call(api, name, *args)
            if name == 'SubmitSdlPlacement': result['placement'] = 'pending'
            return result
        original_object = self.bus.get_object
        def get_object(*args, **kwargs):
            proxy = original_object(*args, **kwargs)
            def invoke(key, **unused):
                self.shortcuts.append(key)
                self.clock += 1.1  # Simulated bus delay, no sleep/native action.
            proxy.invokeShortcut = invoke
            return proxy
        with patch.object(api_type, 'call', call), patch.object(self.bus, 'get_object', get_object):
            self.assertEqual(self.run_client(), 1)
        self.assertEqual(json.loads(self.output[-1])['reason'], 'Placement completion deadline expired')
        self.assertFalse(any(name == 'CancelSdlPlacement' for name, _ in self.calls))
        self.assertTrue(self.bus.closed)

    def test_dispatch_trace_is_redacted_monotonic_and_separate_from_result(self):
        import io
        from contextlib import redirect_stderr
        stream = io.StringIO()
        with redirect_stderr(stream): self.assertEqual(self.run_client(), 0)
        prefix = 'joetoo-kwin SDL operator diagnostic '
        rows = [json.loads(line[len(prefix):]) for line in stream.getvalue().splitlines()]
        self.assertEqual([r['stage'] for r in rows], ['shortcut_dispatch', 'shortcut_returned'])
        self.assertTrue(all(r['request_id'] == self.result['request_id'] and r['window_uuid'] == WINDOW_ID for r in rows))
        self.assertEqual([r['elapsed_ms'] for r in rows], sorted(r['elapsed_ms'] for r in rows))
        self.assertNotIn('caption', stream.getvalue())
        self.assertEqual(len(self.output), 1)

    def test_dispatch_diagnostic_sink_failure_does_not_change_operation(self):
        # inject the sink only, not the public result emitter
        with patch('sys.stderr.write', side_effect=OSError('sink failure')):
            self.assertEqual(self.run_client(), 0)
        self.assertTrue(self.bus.closed)
        self.assertEqual(len(self.output), 1)

    def test_absent_confirmation_never_submits(self):
        with self.assertRaises(RuntimeError): self.run_client(confirmed=False)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.shortcuts, [])

    def test_wrong_result_unknown_state_owner_loss_and_timeout_cancel(self):
        for mode in ('wrong_uuid', 'unknown', 'owner_loss', 'timeout'):
            with self.subTest(mode=mode):
                self.mode = mode; self.calls.clear()
                with self.assertRaises(RuntimeError): self.run_client()
                self.assertEqual(self.calls[-1][0], 'CancelSdlPlacement')
                self.assertTrue(self.bus.closed)
                self.assertEqual(self.output, [])


if __name__ == '__main__':
    unittest.main()
