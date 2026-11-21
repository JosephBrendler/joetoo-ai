# Optional per-account CLI defaults — `defaults.conf`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired example:** `config-examples/user/defaults.conf`.
**Optional active destination:**
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf` with one caveat:
if `XDG_CONFIG_HOME` is set to a *relative* path, the CLI instead uses
`$HOME/.config/joetoo-kwin/defaults.conf`. This behavior is different from
the per-account **OpenRC** override's XDG handling.

Nothing is created under HOME during package installation. As the intended
non-root user, prepare a private config directory (typically `0700`), copy
the example to an explicitly chosen file (`0600` is appropriate), inspect it,
and try `joetoo-kwin -c -f YOUR_PLAN` before any confirmed launch.

The example sets `terminal_gap_percent=3`, a harmless *sample override* rather
than a required setting. Missing user defaults are allowed. A present file
must be a readable, valid trusted Bash file; it runs even during the `-c`
preview. Precedence: built-ins → system defaults → **user defaults** → selected
per-run plan → supported CLI overrides. The plan can supersede this file;
`-f` does not suppress it.

This defaults file is **not** the selected `joetoo-kwin.conf` plan, and
`eselect joetoo-kwin` does not edit or select `defaults.conf`.
See [`../../docs/configuration-reference.md`](../../docs/configuration-reference.md).
