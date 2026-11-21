# Global OpenRC user-service configuration — `joetoo-kwind`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired source:** `conf.d/joetoo-kwind` (same directory). **Installed active
file:** `/etc/conf.d/joetoo-kwind`, root-owned, normally readable `0644`.
The ebuild installs this global file; it never starts the user service or
creates account-specific configuration.

The user OpenRC script `/etc/user/init.d/joetoo-kwind` explicitly sources
this file if readable. It establishes Joetoo's `TRUE=0` and `FALSE=""`
pseudo-booleans and its broker executable, resident JS and KWin script names.
It then conditionally sources the administrator and account layers, **in order**:

1. `/etc/user/conf.d/joetoo-kwind` — optional root-owned override.
2. `${XDG_CONFIG_HOME}/rc/conf.d/joetoo-kwind` when XDG_CONFIG_HOME is
   absolute, or `$HOME/.config/rc/conf.d/joetoo-kwind` if unset and HOME is
   absolute — optional account override.

**Important:** If `XDG_CONFIG_HOME` is set but *relative*, the present OpenRC
loader does not load the account override; do not assume it falls back to HOME.
The CLI launch-plan loader has different XDG fallback rules.

This global file is **shell code, not a plain key-value parser**. Keep it
root-managed and do not set passwords, user paths, or user-specific profiles.
An existing administrator-edited `/etc/conf.d` file must be preserved under
Portage config protection during upgrades; do not replace it with a copied
source file without review.

For the standard packaged installation the intended broker path is
`/usr/libexec/joetoo-kwin/joetoo-kwind`. The current development source may
still use `/usr/libexec/joetoo-kwind`; Step 1.9 must correct both this file
and the service script together before releasing `0.1.0`.

**Service usage, as the graphical account:** `rc-service -U joetoo-kwind status`.
`rc-service -U` does not change to that account on your behalf. The service
must not run as root and should not terminate managed application children.

Further details: [`../docs/joetoo-kwin_user_manual.md`](../docs/joetoo-kwin_user_manual.md)
and [`../docs/configuration-reference.md`](../docs/configuration-reference.md).
