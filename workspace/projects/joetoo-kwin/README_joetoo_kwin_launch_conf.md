# Per-run launch configuration — `joetoo-kwin.conf`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired source starters:** `joetoo-kwin-per-run-template.conf` (short) and
`joetoo-kwin-template.conf` (comprehensive), both beside this README.
The release source tree contains **templates, not an active user plan**.

After installation, the normal selected plan is
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf` (relative
XDG_CONFIG_HOME falls back to `$HOME/.config`). Only if that plan is absent
does the CLI use `/etc/joetoo-kwin/joetoo-kwin.conf` as fallback. An explicit
`-f FILE` selects that file for this run without changing the normal selection.
`eselect` may manage a user-owned symlink at the user-plan path, but is not
required to use an ordinary regular plan.

Every launch plan is **trusted Bash**, not a passive INI file. It should provide
`screen_width` and `screen_height` explicitly; there is no automatic display
dimension detection. It can set exposed settings and populate the
`desktop_session_list=(...)` recipe array. Source loading order is built-ins,
optional system defaults, optional user defaults, this chosen plan, supported
CLI overrides. `-c` is dry-run planning **but still executes trusted config**.

For an initial local-only plan, make an inspected copy of
`joetoo-kwin-per-run-template.conf` (after installation, its packaged copy
is expected at `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf`).
The short template uses example `screen_width=1920`, `screen_height=1080` and
local Dolphin/Konsole recipes; **replace both dimensions** for your host.
Use `joetoo-kwin -c -f FILE` to validate and plan, then `-o -f FILE` only
after review and the application's explicit confirmation.

Neither the package nor the selector should overwrite a regular user plan.
For multiple plans, read [`eselect/README_eselect_profiles_conf.md`](eselect/README_eselect_profiles_conf.md).
Full policy and recipes: [`docs/configuration-reference.md`](docs/configuration-reference.md).
