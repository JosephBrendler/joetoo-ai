#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Private files and recipe-only snapshots. Neither file grants window authority."""
import json
import datetime
import fcntl
import time
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import tempfile
import subprocess
from copy import deepcopy

# Fixed allowlist: executable configuration is generated, never copied from a
# user's Bash source. No arbitrary variable, command, credential or log survives.
LEGACY_SETTING_NAMES = '''snapshot_validation_timeout_ms screen_width screen_height desktop_limit dt_win_limit min_window_exposure_px
terminal_width_percent terminal_gap_percent terminal_height_percent terminal_left_percent terminal_top_percent terminal_row_gap_percent
graphical_left_percent graphical_top_percent graphical_width_percent graphical_height_percent
initial_focus_timeout_ms initial_focus_poll_interval_ms sftp_capability_timeout_ms
SFTP_ADVISORY_ENABLED sftp_advisory_timeout_ms sftp_advisory_ssh_port
rdp_registration_timeout_ms rdp_registration_poll_ms rdp_registration_event_limit rdp_registration_window_limit rdp_backend_log_byte_limit
rdp_x11_renderer rdp_x11_identity_settle_ms rdp_remote_width rdp_remote_height RDP_SMART_SIZING
rdp_initial_client_width rdp_initial_client_height rdp_windowing_backend rdp_security_protocol rdp_certificate_policy
vnc_ssh_start_timeout_ms vnc_viewer_ready_timeout_ms vnc_supervisor_poll_interval_ms vnc_cleanup_timeout_ms
vnc_local_port_attempts vnc_identity_event_limit vnc_identity_settle_ms vnc_dbus_timeout_ms vnc_identity_start_timeout_ms vnc_placement_timeout_ms'''.split()
SETTING_NAMES = LEGACY_SETTING_NAMES
HISTORY_PATTERN = re.compile(r'snapshot-([0-9]{8}T[0-9]{6}\.[0-9]{9}Z)-[0-9a-f]{32}\.conf')
BYTE_LIMIT = 4 * 1024 * 1024  # File-format safety ceiling, not an operation timer.


def private_directory(path):
    """Walk directory FDs without following symlinks; never repair permissions."""
    path = Path(path)
    if not path.is_absolute():
        raise ValueError('private path must be absolute')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            try:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(part, 0o700, dir_fd=fd)
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        info = os.fstat(fd)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('private directory ownership/mode rejected')
        return fd
    except Exception:
        os.close(fd)
        raise


def read_private_at(parent, name):
    """Read one regular private file relative to an already validated directory."""
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1 or info.st_size > BYTE_LIMIT):
            raise ValueError('private file ownership/type/mode/size rejected')
        raw = os.read(fd, BYTE_LIMIT + 1)
        if len(raw) != info.st_size or os.fstat(fd).st_mtime_ns != info.st_mtime_ns:
            raise ValueError('private file changed during read')
        return raw.decode('utf-8')
    finally:
        os.close(fd)


def read_private(path):
    parent = private_directory(Path(path).parent)
    try:
        return read_private_at(parent, Path(path).name)
    finally:
        os.close(parent)


def atomic_private(path, text):
    """fsync + atomic rename relative to the verified private directory FD."""
    raw = text.encode('utf-8')
    if len(raw) > BYTE_LIMIT:
        raise ValueError('private file too large')
    parent = private_directory(Path(path).parent)
    name = '.pending-' + os.urandom(16).hex()
    try:
        # Existing bad files are errors, never silently replaced/followed.
        try:
            existing = os.stat(Path(path).name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing and (not stat.S_ISREG(existing.st_mode) or existing.st_uid != os.geteuid()
                         or stat.S_IMODE(existing.st_mode) != 0o600 or existing.st_nlink != 1):
            raise ValueError('existing private file unsafe')
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'wb') as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, Path(path).name, src_dir_fd=parent, dst_dir_fd=parent)
        os.fsync(parent)
    finally:
        try:
            os.unlink(name, dir_fd=parent)
        except FileNotFoundError:
            pass
        os.close(parent)


def runtime_path():
    root = os.environ.get('XDG_RUNTIME_DIR', '')
    if not root.startswith('/'):
        raise ValueError('XDG_RUNTIME_DIR required')
    info = os.lstat(root)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
        raise ValueError('private runtime directory required')
    return Path(root) / 'joetoo-kwin' / 'managed-windows.json'


def snapshot_path():
    root = os.environ.get('XDG_STATE_HOME', '')
    if not root.startswith('/'):
        root = str(Path.home() / '.local/state')
    return Path(root) / 'joetoo-kwin' / 'last-session.conf'


def intent(data):
    """Complete original recipe including logical slot; metadata is not authority."""
    keys = {'desktop', 'slot', 'program', 'mode', 'target', 'layer', 'settings'}
    if not isinstance(data, dict) or set(data) - {"frame_override"} != keys:
        raise ValueError('incomplete restore intent')
    if any(type(data[k]) is not int or not 1 <= data[k] <= 256 for k in ('desktop', 'slot')):
        raise ValueError('invalid intended reservation')
    if data['layer'] not in ('under', 'panel', 'over'):
        raise ValueError('invalid restore layer')
    target = data['target']
    if (not isinstance(target, str) or len(target.encode()) > 4096
            or '|' in target or any(ord(c) < 32 or ord(c) == 127 for c in target)):
        raise ValueError('invalid restore target (redacted)')
    pair = (data['program'], data['mode'])
    if pair == ('sdl-freerdp', 'rdp'):
        from joetoo_kwin_rdp_target import target as parse
        parse(target)
    elif pair == ('vncviewer', 'ssh'):
        from joetoo_kwin_vnc_target import target as parse
        parse(target)
    elif pair == ('dolphin', 'sftp'):
        from joetoo_kwin_sftp_target import sftp_uri
        sftp_uri(target)
    elif pair == ('konsole', 'ssh'):
        if not re.fullmatch(r'(?:[A-Za-z0-9_.-]+@)?[A-Za-z0-9_.:\[\]-]+', target) or target.startswith('-'):
            raise ValueError('unrestorable SSH target (redacted)')
    elif pair == ('konsole', 'local'):
        if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.+-]*', target):
            raise ValueError('unrestorable executable basename (redacted)')
    elif pair == ('dolphin', 'local'):
        if '://' in target:
            raise ValueError('unrestorable local directory (redacted)')
    else:
        raise ValueError('unsupported restore recipe')
    if 'frame_override' in data:
        frame = data['frame_override']
        if not isinstance(frame, str) or not re.fullmatch(r'[0-9]{1,5}\|[0-9]{1,5}\|[0-9]{1,5}\|[0-9]{1,5}', frame):
            raise ValueError('invalid original frame policy')
    values = data['settings']
    if not isinstance(values, dict) or set(values) != set(SETTING_NAMES):
        raise ValueError('incomplete effective restore settings')
    enums = {'rdp_windowing_backend': ('auto', 'wayland', 'x11'), 'rdp_x11_renderer': ('auto', 'software'),
             'rdp_security_protocol': ('nla', 'negotiate'), 'rdp_certificate_policy': ('strict', 'prompt'),
             'RDP_SMART_SIZING': ('0', ''), 'SFTP_ADVISORY_ENABLED': ('0', '')}
    for name, value in values.items():
        if not isinstance(value, str) or (value not in enums[name] if name in enums else not re.fullmatch(r'[0-9]{1,8}', value)):
            raise ValueError('invalid restore settings (redacted)')
    if not 100 <= int(values["snapshot_validation_timeout_ms"]) <= 120000:
        raise ValueError("invalid snapshot validation timeout")
    return deepcopy(data)


def snapshot_data(data):
    """Normalize legacy per-record policy into one session-level policy."""
    if not isinstance(data, dict) or type(data.get('protocol')) is not int:
        raise ValueError('invalid snapshot schema')
    if data['protocol'] == 1 and set(data) == {'protocol', 'entries'}:
        entries = [intent(item) for item in data['entries']]
    elif data['protocol'] == 2 and set(data) == {'protocol', 'settings', 'entries'}:
        if any(not isinstance(e, dict) or 'settings' in e for e in data['entries']):
            raise ValueError('policy must occur only at session level')
        entries = [intent(dict(e, settings=data['settings'])) for e in data['entries']]
    else:
        raise ValueError('invalid snapshot schema')
    if not 1 <= len(entries) <= 512:
        raise ValueError('empty or oversized snapshot')
    entries.sort(key=lambda e: (e['desktop'], e['slot']))
    if len({(e['desktop'], e['slot']) for e in entries}) != len(entries):
        raise ValueError('duplicate snapshot reservation')
    if any(e['settings'] != entries[0]['settings'] for e in entries):
        raise ValueError('mixed effective settings cannot be faithfully exported')
    return dict(protocol=2, settings=entries[0]['settings'],
                entries=[{k: v for k, v in e.items() if k != 'settings'} for e in entries])


def render_snapshot(data, legacy=False):
    """Generate only quoted assignments and accepted recipe arrays."""
    if legacy:
        # Reproduce the previous generator byte-for-byte before accepting old
        # trusted snapshots. Do not relax validation into arbitrary Bash input.
        normalized = snapshot_data(data)
        entries = sorted(data['entries'], key=lambda e: (e['desktop'], e['slot']))
        clean = dict(protocol=1, entries=entries)
        settings = entries[0]['settings']
        names = SETTING_NAMES if 'snapshot_history_depth' in settings else LEGACY_SETTING_NAMES
    else:
        clean = snapshot_data(data)
        entries, settings, names = clean['entries'], clean['settings'], SETTING_NAMES
    text = '# joetoo-kwin recipe snapshot v' + str(clean['protocol']) + '; geometry is recalculated, not restored.\n'
    text += '# data: ' + json.dumps(clean, sort_keys=True, separators=(',', ':')) + '\n'
    text += ''.join(name + '=' + shlex.quote(settings[name]) + '\n' for name in names)
    text += 'desktop_session_list=(\n'
    for e in entries:
        text += '    ' + shlex.quote('|'.join(str(e[k]) for k in ('desktop', 'program', 'mode', 'target', 'layer'))) + '\n'
    text += ')\n'
    if any('frame_override' in e for e in entries):
        text += 'desktop_session_frames=(\n' + ''.join('    ' + shlex.quote(e.get('frame_override', '')) + '\n' for e in entries) + ')\n'
    else:
        text += 'desktop_session_frames=()\n'
    return text


def snapshot_text(data):
    return render_snapshot(data)


def validate_snapshot(text):
    lines = text.splitlines()
    if len(lines) < 2 or not lines[1].startswith('# data: '):
        raise ValueError('not a generated snapshot')
    data = json.loads(lines[1][8:])
    if render_snapshot(data, legacy=data.get('protocol') == 1) != text:
        raise ValueError('snapshot content mismatch; arbitrary Bash rejected')
    return snapshot_data(data)


def latest_at(parent, basename):
    """The only permitted link is one relative basename to our own history."""
    info = os.stat(basename, dir_fd=parent, follow_symlinks=False)
    if stat.S_ISLNK(info.st_mode):
        if info.st_uid != os.geteuid() or info.st_nlink != 1:
            raise ValueError('unsafe latest link owner')
        target = os.readlink(basename, dir_fd=parent)
        if not HISTORY_PATTERN.fullmatch(target):
            raise ValueError('unsafe latest link target')
        return target, read_private_at(parent, target)
    return None, read_private_at(parent, basename)  # Legacy regular last-good.


def snapshot_read(path):
    parent = private_directory(Path(path).parent)
    try:
        _, text = latest_at(parent, Path(path).name)
        return snapshot_text(validate_snapshot(text))
    finally:
        os.close(parent)


def history_names(parent):
    result = []
    for name in os.listdir(parent):
        if HISTORY_PATTERN.fullmatch(name):
            info = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                    or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
                raise ValueError('unsafe history member')
            result.append(name)
    return sorted(result)


def publish_snapshot(path, text, depth):
    """One directory lock, immutable files and one atomic relative link swap.

    Errors before the swap preserve last-good/history. Once the swap succeeds,
    later fsync/pruning problems are reported as publication warnings; never
    mislabel an already published save as a failed transaction or prune on an
    uncertain directory fsync. No registry or application ownership is involved.
    """
    parent = private_directory(Path(path).parent)
    lock = None
    created = []
    pending = '.latest-' + os.urandom(16).hex()
    published = False
    try:
        lock = os.open('.snapshot.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
        info = os.fstat(lock)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError('unsafe snapshot lock')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Busy is immediate, not an unbounded wait.
        names = history_names(parent)
        try:
            active, old_text = latest_at(parent, Path(path).name)
            validate_snapshot(old_text)
        except FileNotFoundError:
            try:
                os.stat(Path(path).name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                active, old_text = None, None
            else:
                raise ValueError('dangling latest selection')
        # Monotonic filenames even for identical nanosecond timestamps or a
        # backwards wall clock; entropy and O_EXCL protect against collisions.
        last_stamp = names[-1].split('-')[1] if names else ''
        def create(body):
            nonlocal last_stamp
            ns = time.time_ns()
            if last_stamp:
                sec = datetime.datetime.strptime(last_stamp[:15], '%Y%m%dT%H%M%S').replace(tzinfo=datetime.timezone.utc)
                ns = max(ns, int(sec.timestamp()) * 1_000_000_000 + int(last_stamp[16:25]) + 1)
            stamp = datetime.datetime.fromtimestamp(ns // 1_000_000_000, datetime.timezone.utc).strftime('%Y%m%dT%H%M%S') + f'.{ns % 1_000_000_000:09d}Z'
            name = 'snapshot-' + stamp + '-' + os.urandom(16).hex() + '.conf'
            raw = body.encode('utf-8')
            if len(raw) > BYTE_LIMIT:
                raise ValueError('snapshot too large')
            fd = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            created.append(name)
            with os.fdopen(fd, 'wb') as out:
                out.write(raw); out.flush(); os.fsync(out.fileno())
            last_stamp = stamp
            return name
        migrated = old_text is not None and active is None
        if migrated:
            create(old_text)  # Preserve valid legacy bytes before replacing its name.
        newest = create(text)
        os.symlink(newest, pending, dir_fd=parent)
        os.fsync(parent)
        os.replace(pending, Path(path).name, src_dir_fd=parent, dst_dir_fd=parent)
        published = True
        result = dict(snapshot=newest, history_depth=depth, migrated_legacy=migrated,
                      pruned=0, publication_warning=False, pruning_warning=False)
        try:
            os.fsync(parent)
        except OSError:
            result['publication_warning'] = True
            return result  # Both old and new targets remain; no pruning.
        try:
            names = history_names(parent)
            current, _ = latest_at(parent, Path(path).name)
            keep = set(names[-depth:]) | {current}
            for name in names:
                if name not in keep:
                    os.unlink(name, dir_fd=parent); result['pruned'] += 1
            os.fsync(parent)
        except (OSError, ValueError):
            result['pruning_warning'] = True
        return result
    finally:
        try:
            try:
                os.unlink(pending, dir_fd=parent)
            except OSError:
                pass  # Do not mask the original failure; last-good is unaffected.
            if not published:
                for name in created:
                    try:
                        os.unlink(name, dir_fd=parent)
                    except OSError:
                        pass  # An inaccessible orphan is not permission to prune prior history.
        finally:
            if lock is not None:
                os.close(lock)
            os.close(parent)


def save_snapshot(text, cli, path=None, depth=10):
    """Validate generated Bash through the existing offline planner before publish."""
    path = path or snapshot_path()
    if type(depth) is not int or not 1 <= depth <= 1000:
        raise ValueError('snapshot_history_depth must be 1..1000')
    data = validate_snapshot(text)
    generated = snapshot_text(data)
    directory = private_directory(Path(path).parent)
    os.close(directory)
    fd, temporary = tempfile.mkstemp(prefix='.validate-', suffix='.conf', dir=Path(path).parent)
    try:
        with os.fdopen(fd, 'w') as out:
            out.write(generated)
        result = subprocess.run(['bash', str(cli), '-c', '-f', temporary],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=int(data['settings']['snapshot_validation_timeout_ms']) / 1000)
        if result.returncode:
            raise ValueError('snapshot failed offline plan validation')
        return publish_snapshot(path, generated, depth)
    finally:
        os.unlink(temporary)


def main():
    if sys.argv[1:] == ['--setting-names']:
        print(' '.join(SETTING_NAMES))
    elif len(sys.argv) == 9 and sys.argv[1] == '--intent':
        parts = sys.stdin.buffer.read(BYTE_LIMIT + 1).decode().split('\0')
        if parts[-1] != '' or len(parts) != 2 * len(SETTING_NAMES) + 1:
            raise ValueError('invalid settings input')
        metadata = dict(zip(('desktop', 'slot', 'program', 'mode', 'target', 'layer'),
            [int(sys.argv[2]), int(sys.argv[3]), *sys.argv[4:8]]), settings=dict(zip(parts[0:-1:2], parts[1:-1:2])))
        if sys.argv[8]:
            metadata['frame_override'] = sys.argv[8]
        try:
            validated = intent(metadata)
        except ValueError:
            # Legacy valid launch recipes/settings can be outside the safe
            # export subset. They stay launchable, but -S must refuse them.
            validated = None
        print(json.dumps(validated))
    elif len(sys.argv) in (3, 4) and sys.argv[1] == '--save':
        depth = int(sys.argv[3]) if len(sys.argv) == 4 else 10
        print(json.dumps(save_snapshot(sys.stdin.read(BYTE_LIMIT + 1), sys.argv[2], depth=depth)))
    elif sys.argv[1:] == ['--restore']:
        sys.stdout.write(snapshot_read(snapshot_path()))
    else:
        raise ValueError('unsupported persistence operation')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('joetoo-kwin: invalid or unavailable private snapshot/intent (details redacted)', file=sys.stderr)
        sys.exit(2)
