from pathlib import Path
p=Path('tools/joetoo-kwind-install-poc')
s=p.read_text().replace('--check | --install | --update\\n', '--check | --install | --update | --preview-legacy-backups\\n').replace('--check|--install|--update)', '--check|--install|--update|--preview-legacy-backups)')
anchor="printf 'OpenRC user service: %s\\n'"
pos=s.index(anchor)
s=s[:pos]+'''# Keep archival work in this installer; Python is already required by its
# configuration helper. Each component has its own namespace (several share
# the basename joetoo-kwind). A version is immutable, with rollback provenance.
archive_files() {
    python3 - "$action" "${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/archive" \\
        "$service_source" "$service_dest" "$daemon_source" "$daemon_dest" \\
        "$registry_source" "$registry_dest" "$override_source" "$override_dest" \\
        "$resident_source" "$resident_dest" "$cli_source" "$cli_dest" \\
        "$vnc_identity_source" "$vnc_identity_dest" "$vnc_target_source" "$vnc_target_dest" \\
        "$vnc_launch_source" "$vnc_launch_dest" <<'PY'
import datetime
import filecmp
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile


def safe_path(path):
    # Reject symlinks in ancestors too, before reading or writing through them.
    for part in reversed((path, *path.parents)):
        if part.is_symlink():
            raise ValueError(f"Refusing symlink: {part}")
    if path.exists() and (not path.is_file() or path.stat().st_uid != os.geteuid()):
        raise ValueError(f"Refusing non-regular/non-owned file: {path}")


def private_directory(path):
    if path.is_symlink():
        raise ValueError(f"Refusing symlink: {path}")
    if not path.exists():
        private_directory(path.parent)
        path.mkdir(mode=0o700)
    info = path.stat()
    if not path.is_dir() or info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise ValueError(f"Refusing unsafe archive directory: {path}")


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    action, archive = sys.argv[1], Path(sys.argv[2])
    if not archive.is_absolute() or '..' in archive.parts:
        raise ValueError('XDG_STATE_HOME must be an absolute path without .. components')
    components = ('service', 'daemon', 'registry', 'override', 'resident', 'cli',
                  'vnc_identity', 'vnc_target', 'vnc_launch')
    for component, src, dest in zip(components, sys.argv[3::2], sys.argv[4::2]):
        src, dest = Path(src), Path(dest)
        safe_path(dest)
        if action == '--preview-legacy-backups':
            # Read only: group old beside-installation backups by actual bytes.
            groups = []
            for pattern in (dest.name + '.before-update.*', dest.name + '.before-step1.2a-update.*'):
                for old in sorted(dest.parent.glob(pattern)):
                    safe_path(old)
                    for group in groups:
                        if filecmp.cmp(old, group[0], shallow=False):
                            group.append(old)
                            break
                    else:
                        groups.append([old])
            print(json.dumps({'component': component, 'installed_path': str(dest),
                              'active_sha256': digest(dest) if dest.exists() else None,
                              'versions': [{'sha256': digest(g[0]), 'representative': str(g[0]),
                                            'copies': len(g), 'paths': list(map(str, g))}
                                           for g in groups]}))
            continue
        safe_path(src)
        if not dest.exists() or filecmp.cmp(src, dest, shallow=False):
            continue
        # Save every superseded component BEFORE the shell starts installing any
        # replacement. Failure here leaves the old installation intact.
        safe_path(archive / 'probe')
        directory = archive / component
        private_directory(directory)
        version = directory / digest(dest)
        payload = version / dest.name
        safe_path(payload)
        if version.exists():
            safe_path(version / 'provenance.json')
            if not filecmp.cmp(dest, payload, shallow=False) or not (version / 'provenance.json').is_file():
                raise ValueError(f'Archive integrity failure: {version}')
            print(f'Already archived: {payload}')
            continue
        staging = Path(tempfile.mkdtemp(prefix='.pending-', dir=directory))
        try:
            copied = staging / dest.name
            shutil.copy2(dest, copied)
            if not filecmp.cmp(dest, copied, shallow=False) or digest(copied) != version.name:
                raise ValueError(f'Archive copy verification failed: {dest}')
            metadata = {'installed_path': str(dest), 'source_path': str(src),
                        'original_name': dest.name, 'sha256': version.name,
                        'mode': oct(stat.S_IMODE(dest.stat().st_mode)),
                        'archived_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            provenance = staging / 'provenance.json'
            provenance.write_text(json.dumps(metadata, indent=2) + '\\n')
            provenance.chmod(0o600)
            for saved in (copied, provenance):
                with saved.open('rb') as stream:
                    os.fsync(stream.fileno())
            staging.rename(version)
            print(f'Backup: {payload}')
        finally:
            if staging.exists():
                shutil.rmtree(staging)


try:
    main()
except (OSError, ValueError) as error:
    print(f'Installer archive: {error}', file=sys.stderr)
    sys.exit(1)
PY
}

if [ "$action" = --preview-legacy-backups ]; then
    archive_files
    exit "$?"
fi

'''+s[pos:]
a=s.index('"$config_helper" --apply || exit 1')
b=s.index('# -D creates BOTH',a)
s=s[:a]+'''if [ "$action" = --update ]; then
    # Explicit update preserves the previous on-disk POC. No silent reset of a
    # known-working service/daemon installation.
    archive_files || exit 1
fi
"$config_helper" --apply || exit 1
'''+s[b:]
p.write_text(s)
