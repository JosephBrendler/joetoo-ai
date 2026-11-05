#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Temporary diagnostic receiver. No production bridge or window-control API.

serve uses only an explicitly supplied existing Unix session bus. status and
verify are separate gates: a durable transport receipt never proves complete
native window-lifecycle coverage. All D-Bus/GLib imports are lazy for offline
verification and disposable-fixture testing.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import sys
import time
import uuid

IFACE = 'org.joetoo.RDPDiagnostic'
OBJECT = '/org/joetoo/RDPDiagnostic'
UNIQUE = re.compile(r'^:\d+\.\d+$')
OBSERVER = re.compile(r'^rdp-diag-[a-z0-9-]{1,128}$')
UUID = re.compile(r'^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$')
DEFAULTS = dict(durationMs=1800000, maxRecords=1024, maxWindows=64,
                maxRecordBytes=8192, maxTotalBytes=16777216, expectedClass='com.freerdp.client.sdl3',
                shortcutPrefix='joetoo_rdp_diagnostic', ackTimeoutMs=3000,
                livenessIntervalMs=5000, exportTimeoutMs=3081000)
EVENTS = set('existing added removed initial_active workspace.windowActivated '
             'active_window_marker_request window_signals captionChanged '
             'frameGeometryChanged clientGeometryChanged bufferGeometryChanged '
             'windowRoleChanged hiddenChanged modalChanged transientChanged '
             'skipTaskbarChanged skipPagerChanged skipSwitcherChanged '
             'decorationChanged decorationPolicyChanged noBorderChanged surfaceChanged '
             'readyForPaintingChanged activeChanged keepAboveChanged keepBelowChanged '
             'fullScreenChanged interactiveMoveResizeStarted interactiveMoveResizeStepped '
             'interactiveMoveResizeFinished windowClassChanged desktopFileNameChanged'.split())


class Invalid(ValueError):
    """A sanitized protocol/storage failure; never include received text."""


def require(condition, reason):
    if not condition:
        raise Invalid(reason)


def integer(value, low=0, high=2147483647):
    return type(value) is int and low <= value <= high


def decode(text):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    try:
        return json.loads(text, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Invalid('nonfinite_json')))
    except (ValueError, TypeError, RecursionError):
        raise Invalid('invalid_json') from None


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def settings(values):
    result = dict(DEFAULTS, **values)
    require(set(result) == set(DEFAULTS) | {'receiverUniqueName', 'runId'}, 'settings_keys')
    for key in ('durationMs', 'maxRecords', 'maxWindows', 'maxRecordBytes',
                'ackTimeoutMs', 'livenessIntervalMs', 'exportTimeoutMs', 'maxTotalBytes'):
        require(integer(result[key], 1), 'settings_integer')
    require(result['maxRecords'] <= 65536 and result['maxWindows'] <= 4096
            and result['maxRecordBytes'] <= 1048576 and result['maxTotalBytes'] <= 67108864, 'settings_bounds')
    require((result['maxRecords']+2)*(result['maxRecordBytes']+2048) <= result['maxTotalBytes'],
            'cumulative_byte_budget')
    # Drain handshake, every event, terminal end and sender confirmation. This is a
    # conservative worst-case budget, not an assumed filesystem throughput.
    require(result['exportTimeoutMs'] >= (result['maxRecords'] + 3) * result['ackTimeoutMs'],
            'export_deadline_cannot_cover_full_buffer')
    require(isinstance(result['receiverUniqueName'], str)
            and UNIQUE.fullmatch(result['receiverUniqueName']), 'receiver_identity')
    require(isinstance(result['runId'], str)
            and re.fullmatch('[0-9a-f]{32}', result['runId']), 'run_identity')
    require(isinstance(result['expectedClass'], str)
            and re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', result['expectedClass']), 'expected_class')
    require(isinstance(result['shortcutPrefix'], str)
            and re.fullmatch(r'[A-Za-z0-9_]{1,64}', result['shortcutPrefix']), 'shortcut_prefix')
    return result


class PrivateDirectory:
    """Directory-relative, no-follow operations, including all parent components."""
    def __init__(self, path):
        path = Path(path)
        require(path.is_absolute() and '..' not in path.parts, 'unsafe_directory')
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in path.parts[1:]:
                new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = new
            info = os.fstat(fd)
            require(info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700,
                    'directory_must_be_owned_and_0700')
            self.fd = fd
        except BaseException:
            os.close(fd)
            raise

    def close(self):
        os.close(self.fd)

    @staticmethod
    def basename(name):
        require(isinstance(name, str) and name not in {'', '.', '..'}
                and Path(name).name == name, 'unsafe_file_name')

    def create(self, name):
        self.basename(name)
        return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                       0o600, dir_fd=self.fd)

    def read(self, name, limit):
        self.basename(name)
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
                    and stat.S_IMODE(info.st_mode) == 0o600 and info.st_size <= limit,
                    'unsafe_or_oversized_file')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                result = stream.read(limit + 1)
            require(len(result) <= limit, 'oversized_file')
            return result
        finally:
            os.close(fd)

    def write_new(self, name, value):
        fd = self.create(name)
        try:
            write_all(fd, encoded(value))
            os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(self.fd)

    def publish(self, old, new):
        # Exclusive publication: never overwrite another file or a symlink.
        self.basename(old); self.basename(new)
        previous = os.stat(old, dir_fd=self.fd, follow_symlinks=False)
        require(stat.S_ISREG(previous.st_mode) and previous.st_uid == os.geteuid()
                and stat.S_IMODE(previous.st_mode) == 0o600, 'unsafe_publication_source')
        os.link(old, new, src_dir_fd=self.fd, dst_dir_fd=self.fd, follow_symlinks=False)
        published = os.stat(new, dir_fd=self.fd, follow_symlinks=False)
        require((previous.st_dev, previous.st_ino) == (published.st_dev, published.st_ino), 'publication_changed')
        os.unlink(old, dir_fd=self.fd)
        os.fsync(self.fd)


def write_all(fd, data):
    while data:
        count = os.write(fd, data)
        require(count > 0, 'short_write')
        data = data[count:]


def safe_window(data):
    require(isinstance(data, dict), 'window_schema')
    bools = set('normalWindow dialog utility modal transient resizeable noBorder hidden visible '
                'readyForPainting decorationHasAlpha skipTaskbar skipSwitcher skipPager fullScreen '
                'minimized keepAbove keepBelow active deleted wantsInput move resize'.split())
    structural = {'windowRole', 'resourceClass', 'resourceName', 'desktopFileName'}
    rects = {'frameGeometry', 'clientGeometry', 'bufferGeometry'}
    sizes = {'minSize', 'maxSize'}
    markers = {'title_marker', 'normal_title_marker'}
    require(set(data) <= bools | structural | rects | sizes | markers |
            {'uuid', 'in_scope', 'pid', 'windowType', 'transientFor'}, 'window_keys')
    require(isinstance(data.get('uuid'), str) and UUID.fullmatch(data['uuid']), 'window_uuid')
    for key, value in data.items():
        if key == 'uuid':
            continue
        if key == 'in_scope':
            require(type(value) is bool, 'scope_boolean')
            continue
        require(isinstance(value, dict) and value.get('state') in
                {'ok', 'unsupported', 'inaccessible', 'invalid', 'redacted'}, 'property_state')
        if value['state'] != 'ok':
            require(set(value) == {'state'}, 'property_nonvalue')
            continue
        require(set(value) <= {'state', 'value', 'exact'} and 'value' in value, 'property_keys')
        v = value['value']
        if key in bools:
            require(type(v) is bool, 'property_boolean')
        elif key in structural:
            require(isinstance(v, str) and len(v) <= 128 and re.fullmatch(r'[A-Za-z0-9_.:-]*', v),
                    'structural_string')
        elif key in markers:
            require(isinstance(v, str) and re.fullmatch(
                r'joetoo-rdp-proof-[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', v)
                and type(value.get('exact')) is bool, 'title_marker')
        elif key == 'transientFor':
            require(v is None or (isinstance(v, str) and UUID.fullmatch(v)), 'transient_uuid')
        elif key in rects | sizes:
            require(isinstance(v, dict) and set(v) ==
                    ({'x', 'y', 'width', 'height'} if key in rects else {'width', 'height'}), 'geometry_keys')
            require(all(type(n) in (int, float) and math.isfinite(n) for n in v.values()), 'geometry_values')
        else:
            require(type(v) in (int, float) and math.isfinite(v), 'numeric_property')


def capabilities(value, detail=False):
    allowed = EVENTS if detail else {'timeout','windowAdded','windowRemoved','windowActivated',
                                    'finishShortcut','markerShortcut'}
    require(isinstance(value, dict) and set(value) <= allowed, 'capability_keys')
    require(all(type(v) is bool or v in {'connected','unsupported','inaccessible','inactive'}
                for v in value.values() if isinstance(v, (str, bool))), 'capability_value')
    require(all(isinstance(v, (str, bool)) for v in value.values()), 'capability_type')


class Sequence:
    """Shared live/independent verifier: bounded schema and framing state."""
    def __init__(self, config):
        self.config = settings(config)
        self.observer = None
        self.count = self.events = self.last_capture = 0
        self.ended = False
        self.end = None

    def accept(self, r):
        require(isinstance(r, dict) and not self.ended, 'record_after_end')
        require(r.get('protocol') == 1 and type(r['protocol']) is int
                and r.get('run_id') == self.config['runId'], 'protocol_or_run')
        require(isinstance(r.get('observer'), str) and OBSERVER.fullmatch(r['observer']), 'observer')
        require(r.get('transport_seq') == self.count + 1 and type(r['transport_seq']) is int, 'transport_sequence')
        require(self.count < self.config['maxRecords'] + 2, 'record_count_limit')
        common = {'protocol', 'run_id', 'observer', 'transport_seq', 'kind'}
        if self.count == 0:
            require(r.get('kind') == 'ready' and r.get('settings') == self.config
                    and r.get('format_version') == 1 and integer(r.get('wall_time_ms'), 0, 2**53-1), 'ready_schema')
            require(set(r) == common | {'settings', 'capabilities', 'wall_time_ms', 'format_version'}, 'ready_keys')
            caps = r['capabilities']
            capabilities(caps)
            require(isinstance(caps, dict) and caps.get('windowAdded') == 'connected'
                    and caps.get('windowRemoved') == 'connected' and caps.get('timeout') == 'connected', 'required_signals')
            self.observer = r['observer']
        else:
            require(r['observer'] == self.observer, 'observer_changed')
            if r.get('kind') == 'event':
                require(set(r) <= common | {'seq', 'event', 'capture_seq', 'wall_time_ms', 'clock_regressed',
                        'window', 'baseline', 'observed_active', 'activated_uuid', 'intent', 'supported',
                        'cached_on_removal', 'scope'}, 'event_keys')
                require(r.get('event') in EVENTS and r.get('seq') == self.events + 1
                        and type(r['seq']) is int and integer(r.get('capture_seq'), self.last_capture + 1, 2**53-1)
                        and integer(r.get('wall_time_ms'), 0, 2**53-1)
                        and type(r.get('clock_regressed')) is bool, 'event_schema')
                if 'window' in r:
                    safe_window(r['window'])
                if 'observed_active' in r:
                    active = r['observed_active']
                    require(isinstance(active, dict) and active.get('state') in {'ok','unsupported','inaccessible'}, 'active_schema')
                    require(set(active) == ({'state','value'} if active['state'] == 'ok' else {'state'}), 'active_keys')
                    if active['state'] == 'ok':
                        v = active['value']
                        require(v is None or (isinstance(v, str) and UUID.fullmatch(v)), 'active_uuid')
                if 'activated_uuid' in r:
                    v = r['activated_uuid']
                    require(v is None or (isinstance(v, str) and UUID.fullmatch(v)), 'activated_uuid')
                for key in ('baseline', 'cached_on_removal'):
                    require(key not in r or type(r[key]) is bool, 'event_boolean')
                if 'intent' in r:
                    require(r['intent'] in {'unknown', 'explicit invocation; operator provenance unverified'}, 'intent')
                if 'scope' in r:
                    require(r['scope'] == 'active at invocation only; no previous-viewer confirmation', 'marker_scope')
                if 'supported' in r:
                    capabilities(r['supported'], detail=True)
                self.events += 1
                self.last_capture = r['capture_seq']
            elif r.get('kind') == 'end':
                require(set(r) == common | {'records','captured','reason','truncated','buffered_records','overflow',
                        'callback_failures','cleanup_failures','output_failures','delivery',
                        'unresolved_window_count','capture_intact','capabilities'}, 'end_keys')
                require(r['records'] == self.events and integer(r['records'])
                        and integer(r['captured'], self.last_capture, 2**53-1)
                        and integer(r['buffered_records'], self.events, self.config['maxRecords']), 'end_counts')
                for key in ('callback_failures','cleanup_failures','output_failures','unresolved_window_count'):
                    require(integer(r[key]), 'end_failure_count')
                require(type(r['truncated']) is bool and type(r['capture_intact']) is bool, 'end_boolean')
                require(r['reason'] in {'requested','expired','record_limit','window_limit',
                        'record_size_limit','callback_error','identity_unavailable'}, 'end_reason')
                require(r['delivery'] == 'pending acknowledgement and independent receipt verification', 'delivery_label')
                capabilities(r['capabilities'])
                if r['overflow'] is not None:
                    overflow = r['overflow']
                    require(isinstance(overflow, dict) and set(overflow) <=
                            {'event','rejected_records','rejected_windows','limit'}
                            and overflow.get('event') in EVENTS | {'track'}
                            and integer(overflow.get('limit'), 1)
                            and overflow.get('rejected_records', overflow.get('rejected_windows')) == 1,
                            'overflow_schema')
                truncated = r['reason'] in {'record_limit', 'window_limit', 'record_size_limit'}
                intact = r['reason'] in {'requested','expired'} and not any(r[k] for k in (
                    'callback_failures','cleanup_failures','output_failures','unresolved_window_count'))
                require(r['truncated'] == truncated and r['capture_intact'] == intact, 'integrity_claim')
                self.ended = True
                self.end = r
            else:
                raise Invalid('record_kind')
        self.count += 1


class Receiver:
    def __init__(self, directory, config, kwin_owner, clock=time.monotonic):
        require(UNIQUE.fullmatch(kwin_owner), 'kwin_owner')
        self.directory = directory
        self.config = settings(config)
        self.kwin_owner = kwin_owner
        self.clock = clock
        self.sequence = Sequence(self.config)
        self.fd = directory.create('evidence.partial.jsonl')
        os.fsync(directory.fd)
        self.digest = hashlib.sha256()
        self.bytes = self.persisted_count = 0
        self.draining = False
        self.ready = self.complete = self.sender_confirmed = False
        self.failure = None
        self.last_seen = None

    def fail(self, reason):
        self.ready = False
        if self.failure is None:
            self.failure = reason
            try:
                self.directory.write_new('failure.json', dict(reason=reason, records=self.persisted_count,
                                                            transport_complete=False))
            except OSError:
                pass  # Partial evidence remains; absent receipt always fails verification.

    def status(self):
        return dict(protocol=1, run_id=self.config['runId'], receiver=self.config['receiverUniqueName'],
                    kwin_owner=self.kwin_owner, observer=self.sequence.observer,
                    ready_persisted=self.persisted_count > 0, native_launch_ready=self.ready,
                    transport_complete=self.complete, sender_confirmed_end_ack=self.sender_confirmed, failure=self.failure, records=self.persisted_count,
                    internal_capture_intact=self.sequence.end['capture_intact'] if self.complete else None,
                    lifecycle_coverage='unassessed')

    def check_owner(self, current):
        if current != self.kwin_owner and not self.sender_confirmed:
            self.fail('kwin_owner_changed')
            raise Invalid('kwin_owner_changed')

    def alive(self):
        if self.last_seen is not None and not self.sender_confirmed and not self.failure:
            limit = (self.config['livenessIntervalMs'] + 2*self.config['ackTimeoutMs']) / 1000
            if self.clock() - self.last_seen > limit:
                self.fail('sender_liveness_expired')

    def request(self, method, text, sender):
        require(sender == self.kwin_owner, 'incorrect_sender')
        require(not self.failure and (not self.complete or method == 'Probe'), 'receiver_terminal')
        limit = self.config['maxRecordBytes'] + 2048
        require(isinstance(text, str) and len(text.encode()) <= limit, 'message_size')
        r = decode(text)
        require(isinstance(r, dict) and r.get('protocol') == 1 and r.get('run_id') == self.config['runId'], 'protocol_or_run')
        try:
            if method == 'Append':
                require(self.sequence.count == 0 or self.draining, 'drain_not_started')
                self.sequence.accept(r)
                line = encoded(r)
                require(self.bytes + len(line) <= limit*(self.config['maxRecords']+2), 'total_bytes')
                write_all(self.fd, line)
                os.fsync(self.fd)  # Acknowledgement is after persistence, not enqueueing.
                self.digest.update(line)
                self.bytes += len(line)
                self.persisted_count = self.sequence.count
                if r['kind'] == 'event':
                    self.ready = False
                    self.draining = True
                if self.sequence.ended:
                    self.ready = False
                    receipt = dict(protocol=1, run_id=self.config['runId'], observer=self.sequence.observer,
                                   records=self.sequence.count, bytes=self.bytes, sha256=self.digest.hexdigest(),
                                   transport_complete=True, internal_capture_intact=r['capture_intact'],
                                   lifecycle_coverage='unassessed', kwin_owner=self.kwin_owner)
                    self.directory.publish('evidence.partial.jsonl', 'evidence.jsonl')
                    self.directory.write_new('receipt.pending.json', receipt)
                    self.directory.publish('receipt.pending.json', 'receipt.json')
                    self.complete = True
            elif method == 'Probe':
                require(set(r) == {'protocol','run_id','observer','action'} and
                        r.get('observer') == self.sequence.observer and self.sequence.count > 0,
                        'probe_identity')
                require(r['action'] in {'observe','drain','delivered'}, 'probe_action')
                if r['action'] == 'delivered':
                    require(self.complete and not self.sender_confirmed, 'confirmation_state')
                    self.directory.write_new('delivery-ack.json', dict(protocol=1, run_id=self.config['runId'],
                        observer=self.sequence.observer, sha256=self.digest.hexdigest(),
                        sender_confirmed_end_ack=True))
                    self.sender_confirmed = True
                else:
                    require(not self.complete and (r['action'] != 'observe' or not self.draining), 'already_draining')
                    self.ready = r['action'] == 'observe'
                    if r['action'] == 'drain':
                        self.draining = True
            else:
                raise Invalid('method')
            self.last_seen = self.clock()
            return dict(protocol=1, run_id=self.config['runId'], observer=self.sequence.observer,
                        ok=True, persisted=True, transport_seq=self.sequence.count,
                        native_launch_ready=self.ready, transport_complete=self.complete,
                        sender_confirmed_end_ack=self.sender_confirmed)
        except (OSError, Invalid, TypeError, KeyError, RecursionError):
            self.fail('persistence_or_protocol_failure')
            raise Invalid('persistence_or_protocol_failure') from None

    def close(self):
        if not self.sender_confirmed:
            self.fail('receiver_stopped_incomplete')
        os.close(self.fd)


def verify(directory):
    try:
        os.stat('failure.json', dir_fd=directory.fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise Invalid('recorded_receiver_failure')
    config = decode(directory.read('run.json', 65536))
    conf = settings(config['settings'])
    receipt = decode(directory.read('receipt.json', 65536))
    limit = (conf['maxRecordBytes']+2048)*(conf['maxRecords']+2)
    payload = directory.read('evidence.jsonl', limit)
    require(payload.endswith(b'\n'), 'unterminated_jsonl')
    seq = Sequence(conf)
    for line in payload.splitlines():
        require(len(line) <= conf['maxRecordBytes']+2048, 'record_size')
        seq.accept(decode(line))
    require(seq.ended and seq.observer is not None, 'missing_end')
    expected = dict(protocol=1, run_id=conf['runId'], observer=seq.observer, records=seq.count,
                    bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), transport_complete=True,
                    internal_capture_intact=seq.end['capture_intact'], lifecycle_coverage='unassessed',
                    kwin_owner=config['kwin_owner'])
    require(receipt == expected, 'receipt_mismatch')
    confirmation = decode(directory.read('delivery-ack.json', 65536))
    require(confirmation == dict(protocol=1, run_id=conf['runId'], observer=seq.observer,
            sha256=expected['sha256'], sender_confirmed_end_ack=True), 'sender_confirmation_mismatch')
    return dict(expected, sender_confirmed_end_ack=True)


def serve(args):
    # No autolaunch, runtime-bus fallback, network bus or daemon administration.
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    require(address.startswith('unix:') and ';' not in address and os.geteuid() != 0, 'existing_unix_user_bus_required')
    import dbus
    import dbus.service
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import GLib
    DBusGMainLoop(set_as_default=True)
    bus = dbus.bus.BusConnection(address)
    kwin = str(bus.get_name_owner('org.kde.KWin'))
    require(int(bus.get_unix_user(kwin)) == os.geteuid(), 'kwin_uid')
    conf = dict(DEFAULTS, durationMs=args.duration_seconds*1000, ackTimeoutMs=args.ack_ms,
                livenessIntervalMs=args.liveness_ms, maxRecords=args.max_records, maxTotalBytes=args.max_total_bytes,
                receiverUniqueName=str(bus.get_unique_name()), runId=uuid.uuid4().hex)
    conf['exportTimeoutMs'] = args.export_ms or (conf['maxRecords']+3)*conf['ackTimeoutMs']
    conf = settings(conf)
    directory = PrivateDirectory(args.directory)
    receiver = Receiver(directory, conf, kwin)
    loop = GLib.MainLoop()

    class Service(dbus.service.Object):
        def authorize(self, sender, evidence=False):
            require(int(bus.get_unix_user(sender)) == os.geteuid(), 'caller_uid')
            if not receiver.sender_confirmed:
                receiver.check_owner(str(bus.get_name_owner('org.kde.KWin')))
            if evidence:
                require(str(sender) == kwin, 'incorrect_sender')

        def dispatch(self, method, text, sender):
            try:
                self.authorize(sender, True)
                return json.dumps(receiver.request(method, str(text), str(sender)))
            except Exception:
                # Return a small negative acknowledgement, including on storage
                # errors. Native D-Bus errors would suppress KWin's JS callback.
                return json.dumps(dict(protocol=1, run_id=conf['runId'], ok=False))

        @dbus.service.method(IFACE, in_signature='s', out_signature='s', sender_keyword='sender')
        def Append(self, text, sender=None):
            return self.dispatch('Append', text, sender)

        @dbus.service.method(IFACE, in_signature='s', out_signature='s', sender_keyword='sender')
        def Probe(self, text, sender=None):
            return self.dispatch('Probe', text, sender)

        @dbus.service.method(IFACE, in_signature='', out_signature='s', sender_keyword='sender')
        def Status(self, sender=None):
            self.authorize(sender)
            receiver.alive()
            return json.dumps(receiver.status())

    service = Service(bus, OBJECT)
    try:
        directory.write_new('run.json', dict(settings=conf, kwin_owner=kwin))
        source = Path(__file__).with_name('joetoo-rdp-window-diagnostic.js').read_text()
        observer = 'var JOETOO_RDP_DIAGNOSTIC_SETTINGS = ' + json.dumps(conf) + ';\n' + source
        fd = directory.create('observer.js')
        try:
            write_all(fd, observer.encode()); os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(directory.fd)
        def tick():
            try:
                if str(bus.get_name_owner('org.kde.KWin')) != kwin and not receiver.sender_confirmed:
                    receiver.fail('kwin_owner_changed')
                receiver.alive()
            except Exception:
                receiver.fail('bus_or_kwin_lost')
            return True
        GLib.timeout_add(conf['livenessIntervalMs'], tick)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, lambda: (loop.quit(), False)[1])
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (loop.quit(), False)[1])
        print(json.dumps(dict(state='waiting_for_observer', **receiver.status())), flush=True)
        loop.run()
    finally:
        service.remove_from_connection()
        receiver.close()
        directory.close()
        bus.close()


def client_status(args):
    # Use the current graphical bus; never autolaunch or follow a replaced owner.
    address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    require(address.startswith('unix:') and ';' not in address, 'existing_unix_user_bus_required')
    import dbus
    directory = PrivateDirectory(args.directory)
    try:
        run = decode(directory.read('run.json', 65536))
    finally:
        directory.close()
    conf = settings(run['settings'])
    bus = dbus.bus.BusConnection(address)
    try:
        require(str(bus.get_name_owner('org.kde.KWin')) == run['kwin_owner'], 'kwin_owner_changed')
        obj = bus.get_object(conf['receiverUniqueName'], OBJECT, introspect=False)
        deadline = time.monotonic() + args.wait_ms/1000
        while True:
            result = decode(str(obj.get_dbus_method('Status', IFACE)(timeout=conf['ackTimeoutMs']/1000)))
            require(result.get('run_id') == conf['runId'] and result.get('receiver') == conf['receiverUniqueName'], 'status_identity')
            success = (result['transport_complete'] and result['sender_confirmed_end_ack']) if args.require_complete else result['native_launch_ready']
            if result['failure'] or success or not args.wait_ms or time.monotonic() >= deadline:
                print(json.dumps(result, sort_keys=True))
                require(not result['failure'] and (success or not (args.require_ready or args.require_complete)), 'status_gate_not_satisfied')
                return
            time.sleep(args.poll_ms/1000)
    finally:
        bus.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('serve')
    p.add_argument('directory')
    p.add_argument('--duration-seconds', type=int, default=os.environ.get('RDP_DIAG_SECONDS', '1800'))
    p.add_argument('--ack-ms', type=int, default=DEFAULTS['ackTimeoutMs'])
    p.add_argument('--liveness-ms', type=int, default=DEFAULTS['livenessIntervalMs'])
    p.add_argument('--max-records', type=int, default=DEFAULTS['maxRecords'])
    p.add_argument('--max-total-bytes', type=int, default=DEFAULTS['maxTotalBytes'])
    p.add_argument('--export-ms', type=int, default=0, help='default: (max-records + 3) * ack-ms')
    p = sub.add_parser('status')
    p.add_argument('directory')
    gates = p.add_mutually_exclusive_group()
    gates.add_argument('--require-ready', action='store_true')
    gates.add_argument('--require-complete', action='store_true',
                       help='require transport and sender acknowledgement; not native lifecycle coverage')
    p.add_argument('--wait-ms', type=int, default=0)
    p.add_argument('--poll-ms', type=int, default=100)
    p = sub.add_parser('verify')
    p.add_argument('directory')
    args = parser.parse_args()
    try:
        if args.command == 'serve':
            serve(args)
        elif args.command == 'status':
            require(integer(args.wait_ms) and integer(args.poll_ms, 1), 'status_timing')
            client_status(args)
        else:
            directory = PrivateDirectory(args.directory)
            try:
                print(json.dumps(verify(directory), sort_keys=True))
            finally:
                directory.close()
    except Exception as error:
        # No received payload, exception text, credential or arbitrary path output.
        print(json.dumps(dict(error=type(error).__name__,
                              reason=str(error) if isinstance(error, Invalid) else 'operation_failed',
                              state='incomplete_or_unavailable')), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
