#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, credential-redacting SFTP URL contract. Unvalidated input uses stdin."""
import ipaddress
import json
import re
import sys
from urllib.parse import quote, unquote_to_bytes, urlsplit


def sftp_uri(target):
    # Never include target/parser exception text in an error: rejected userinfo
    # can contain a password even though valid URLs cannot contain credentials.
    if not isinstance(target, str) or not target.startswith('sftp://'):
        raise ValueError('SFTP target requires sftp:// authority')
    if any(ord(c) <= 32 or ord(c) >= 127 for c in target) or any(c in target for c in '\\|?#'):
        raise ValueError('SFTP URL requires ASCII percent-encoded path data without controls, query or fragment')
    try:
        parsed = urlsplit(target)
    except ValueError:
        raise ValueError('Malformed SFTP authority') from None
    authority = parsed.netloc
    user = ''
    if '@' in authority:
        if authority.count('@') != 1:
            raise ValueError('Invalid SFTP account')
        user, authority = authority.split('@')
        if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*', user):
            raise ValueError('SFTP account must be a plain account token; credentials are prohibited')
    port = ''
    if authority.startswith('['):
        match = re.fullmatch(r'\[([^\]]+)\](?::([^:]*))?', authority)
        if not match or '%' in match[1]:
            raise ValueError('Invalid or scoped SFTP IPv6 literal')
        try:
            ipaddress.IPv6Address(match[1])
        except ValueError:
            raise ValueError('Invalid SFTP IPv6 literal') from None
        host = '[' + match[1] + ']'
        port = match[2]
    else:
        if authority.count(':') > 1:
            raise ValueError('SFTP IPv6 literals require brackets')
        host, separator, value = authority.partition(':')
        port = value if separator else None
        if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*', host) or '..' in host:
            raise ValueError('Invalid SFTP host/alias token')
        if re.fullmatch(r'[0-9.]+', host):
            try:
                ipaddress.IPv4Address(host)
            except ValueError:
                raise ValueError('Invalid SFTP IPv4 literal') from None
    if port is not None and (not re.fullmatch(r'[1-9][0-9]{0,4}', port) or int(port) > 65535):
        raise ValueError('SFTP port must be decimal 1..65535 without leading zeros')
    path = parsed.path
    if path and not path.startswith('/'):
        raise ValueError('SFTP path must be absolute or absent')
    if re.search(r'%(?![0-9A-Fa-f]{2})', path) or re.search(r'%(?:2f|5c)', path, re.I):
        raise ValueError('Invalid SFTP path escape or encoded separator')
    try:
        decoded = unquote_to_bytes(path).decode('utf-8', errors='strict')
    except UnicodeError:
        raise ValueError('SFTP path must contain valid UTF-8') from None
    if any(ord(c) < 32 or ord(c) == 127 for c in decoded) or any(c in ('.', '..') for c in decoded.split('/')):
        raise ValueError('SFTP path contains controls or prohibited dot segments')
    # No DNS, filesystem resolution, recursive unquoting or local HOME expansion.
    return ('sftp://' + (user + '@' if user else '') + host +
            (':' + port if port is not None else '') + quote(decoded, safe='/-._~'))


def main():
    try:
        print(json.dumps(sftp_uri(sys.stdin.read())))
        return 0
    except (TypeError, UnicodeError):
        print('Invalid SFTP target; use sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH], without credentials', file=sys.stderr)
        return 2
    except ValueError as exc:
        # sftp_uri only raises our fixed rule messages, never parser/input text.
        print('Invalid SFTP target: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
