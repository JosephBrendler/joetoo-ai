# Administrator override for the user OpenRC service

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired source example:** `user-conf.d/joetoo-kwind`.
**Optional active destination:** `/etc/user/conf.d/joetoo-kwind`, installed
only by a deliberate administrator action. The Gentoo package should ship this
as a read-only example, **not** create an active override during installation.

The global `/etc/conf.d/joetoo-kwind` loads this file *after* setting defaults
and *before* the optional per-account file. Although its pathname includes
`user`, it is an **administrator-managed policy file affecting all accounts**
that use this user service, not the personal settings for one account.

The example contains only commented guidance; an absent file is normal.
Possible values are `JOETOO_KWIND_EXEC`, `JOETOO_KWIND_RESIDENT_JS`, and
`JOETOO_KWIND_SCRIPT_NAME`, but setting executable or resource paths to a
personal development checkout is inappropriate for a general installation.

If enabled, use root ownership and non-group-writable permissions (typically
`0644`), review shell content before sourcing, and preserve customizations
through upgrades. The last-loaded account override can still supersede an
administrator value under the **current** loader; this layer is not an
unoverrideable security policy boundary.

See [`../conf.d/README_global_joetoo_kwind_conf.md`](../conf.d/README_global_joetoo_kwind_conf.md)
and [`../account-conf.d/README_account_joetoo_kwind_conf.md`](../account-conf.d/README_account_joetoo_kwind_conf.md).
