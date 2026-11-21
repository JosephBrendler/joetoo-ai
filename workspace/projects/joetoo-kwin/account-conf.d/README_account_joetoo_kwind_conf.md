# Per-account OpenRC user-service override

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired distributable example:** `account-conf.d/joetoo-kwind` in this source
tree. It replaces the POC-only example for *release documentation*; the POC's
hard-coded `$HOME/.local/` development executable must **not** be distributed
as the preferred installed configuration.

**Optional destination, for the intended account:**
`$HOME/.config/rc/conf.d/joetoo-kwind`, or
`$XDG_CONFIG_HOME/rc/conf.d/joetoo-kwind` if that variable is absolute.
The ebuild does not create this file or its parent directories. Create them
manually as the account owner (`0700` parent directory, `0600` file is a
reasonable private policy), then copy and review the example before use.

The global `/etc/conf.d/joetoo-kwind` sources this file last, after its defaults
and `/etc/user/conf.d/joetoo-kwind`. An absent account file is normal. Unlike
the CLI plan loader, when `XDG_CONFIG_HOME` is **set but relative**, the current
OpenRC configuration does not load an account override at all. Fix that
setting rather than assuming `$HOME/.config` is used automatically.

Example setting: `JOETOO_KWIND_SCRIPT_NAME="joetoo-bridge"`. The file is
trusted executable shell; avoid passwords and do not point `JOETOO_KWIND_EXEC`
to an unverified or writable program. This is service configuration, **not**
the CLI's `joetoo-kwin.conf` launch plan or `defaults.conf`.

See [`../conf.d/README_global_joetoo_kwind_conf.md`](../conf.d/README_global_joetoo_kwind_conf.md)
and [`../user-conf.d/README_system_user_joetoo_kwind_conf.md`](../user-conf.d/README_system_user_joetoo_kwind_conf.md).
