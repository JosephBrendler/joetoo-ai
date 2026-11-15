from pathlib import Path
p=Path('tools/joetoo-kwind-install-poc');s=p.read_text()
pos=s.index('\ndef main():')
s=s[:pos]+'''
def provenance_id(data):
    # Reuse an identical metadata observation without losing distinct modes or
    # timestamps. Archive time describes recording, not the installed version.
    identity = {key: value for key, value in data.items() if key != 'archived_at'}
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def read_provenance(path, version, dest, src):
    safe_path(path)
    info = path.stat()
    if stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
        raise ValueError(f'Unsafe provenance file: {path}')
    data = json.loads(path.read_text())
    fields = {'schema_version', 'installed_path', 'source_path', 'original_name',
              'sha256', 'mode', 'atime_ns', 'mtime_ns', 'archived_at'}
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError(f'Invalid provenance schema: {path}')
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError(f'Unsupported provenance schema: {path}')
    if data['sha256'] != version.name or data['original_name'] != dest.name:
        raise ValueError(f'Provenance identity mismatch: {path}')
    for key, name in (('installed_path', dest.name), ('source_path', src.name)):
        value = data[key]
        if (not isinstance(value, str) or not Path(value).is_absolute()
                or '..' in Path(value).parts or Path(value).name != name):
            raise ValueError(f'Invalid provenance {key}: {path}')
    mode = data['mode']
    if (not isinstance(mode, str) or not mode.startswith('0o')
            or any(c not in '01234567' for c in mode[2:])
            or len(mode) < 3 or not 0 <= int(mode, 8) <= 0o7777
            or oct(int(mode, 8)) != mode):
        raise ValueError(f'Invalid provenance mode: {path}')
    if any(type(data[key]) is not int for key in ('atime_ns', 'mtime_ns')):
        raise ValueError(f'Invalid provenance timestamps: {path}')
    if not isinstance(data['archived_at'], str):
        raise ValueError(f'Invalid provenance archive time: {path}')
    if datetime.datetime.fromisoformat(data['archived_at']).utcoffset() is None:
        raise ValueError(f'Provenance archive time needs a timezone: {path}')
    if path.name != 'provenance.json' and path.name != f'provenance.{provenance_id(data)}.json':
        raise ValueError(f'Provenance record name mismatch: {path}')
    return data


def write_provenance(path, data):
    # Publish a complete record atomically, without overwriting any old record.
    # The temporary link is metadata-only, never a link to an active install.
    fd, pending = tempfile.mkstemp(prefix='.provenance-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(pending, path)
    finally:
        os.unlink(pending)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

''' +s[pos:]
s=s.replace("        safe_path(src)\n        if not dest.exists() or filecmp.cmp(src, dest, shallow=False):\n            continue", """        safe_path(src)
        if not dest.exists():
            continue
        # Capture before content reads can update the installed access time.
        original_info = dest.stat()
        if filecmp.cmp(src, dest, shallow=False):
            continue""")
s=s.replace("        safe_path(payload)\n        if version.exists():", """        safe_path(payload)
        metadata = {'schema_version': 1, 'installed_path': str(dest), 'source_path': str(src),
                    'original_name': dest.name, 'sha256': version.name,
                    'mode': oct(stat.S_IMODE(original_info.st_mode)),
                    'atime_ns': original_info.st_atime_ns, 'mtime_ns': original_info.st_mtime_ns,
                    'archived_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if version.exists():""")
a=s.index("            safe_path(version / 'provenance.json')")
b=s.index("        staging = ",a)
s=s[:a]+'''            private_directory(version)
            if stat.S_IMODE(version.stat().st_mode) != 0o700:
                raise ValueError(f'Unsafe version directory permissions: {version}')
            if not filecmp.cmp(dest, payload, shallow=False) or payload.stat().st_nlink != 1:
                raise ValueError(f'Archive integrity failure: {version}')
            records = [read_provenance(version / 'provenance.json', version, dest, src)]
            records += [read_provenance(path, version, dest, src)
                        for path in sorted(version.glob('provenance.*.json'))]
            # Payload filesystem metadata belongs only to the first observation.
            # Later installations' metadata is represented by separate records.
            first = records[0]
            payload_info = payload.stat()
            if (first['mode'] != oct(stat.S_IMODE(payload_info.st_mode))
                    or first['mtime_ns'] != payload_info.st_mtime_ns):
                raise ValueError(f'Payload/provenance metadata mismatch: {version}')
            if not any(provenance_id(record) == provenance_id(metadata) for record in records):
                write_provenance(version / f'provenance.{provenance_id(metadata)}.json', metadata)
            print(f'Already archived: {payload}; installation metadata recorded separately')
            continue
'''+s[b:]
a=s.index("            metadata = {'installed_path':")
b=s.index("            for saved in (copied, provenance):",a)
s=s[:a]+'''            # The payload keeps its first installation metadata; provenance is
            # authoritative for restoring the metadata of each later observation.
            os.chmod(copied, stat.S_IMODE(original_info.st_mode))
            os.utime(copied, ns=(original_info.st_atime_ns, original_info.st_mtime_ns))
            provenance = staging / 'provenance.json'
            write_provenance(provenance, metadata)
'''+s[b:]
p.write_text(s)
