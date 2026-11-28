# Optional per-account launch config selection

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired selector implementation:** `eselect/joetoo-kwin.eselect`.
**Installed selector module:** `/usr/share/eselect/modules/joetoo-kwin.eselect`.
The package always installs the module, but **using it is optional**.
It manages only the user-selected default launch config symlink, not OpenRC
configuration, either `defaults.conf` layer, or any files/links under `/etc`.

The selectable configs belong in
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/configs/` (relative
`XDG_CONFIG_HOME` falls back to `$HOME/.config`). The active plan path is
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf`.
For example, `joetoo-kwin.conf -> configs/joetoo-kwin.conf` selects
`configs/joetoo-kwin.conf` as the default for `joetoo-kwin -o`.

Neither Portage nor `eselect list/show` creates configs in HOME. As the intended
**non-root** user, explicitly create and review a config first:

```bash
config_root=${XDG_CONFIG_HOME:-$HOME/.config}
[[ $config_root == /* ]] || config_root=$HOME/.config
install -d -m 0700 -- "$config_root/joetoo-kwin/configs"
cp -n -- /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf "$config_root/joetoo-kwin/configs/joetoo-kwin.conf"
chmod 600 -- "$config_root/joetoo-kwin/configs/joetoo-kwin.conf"
# Edit/review it, then validate without launching:
joetoo-kwin -c -f "$config_root/joetoo-kwin/configs/joetoo-kwin.conf"
eselect joetoo-kwin list
eselect joetoo-kwin set joetoo-kwin.conf
eselect joetoo-kwin show
joetoo-kwin -c
# End of commands
```

`list` marks the current valid selection; `set` accepts a config basename or
list number, and safely switches the symlink. It never executes a config itself.
It refuses to replace an existing regular active plan or unsafe/dangling link;
migration is an explicit user action. Configs must be readable, user-owned,
regular, single-link files with safe permissions and valid Bash syntax. The
CLI later sources their content as **trusted executable Bash**. Old links into
`profiles/` require deliberate migration; the selector does not convert them.

See [`../docs/configuration-reference.md`](../docs/configuration-reference.md)
for the complete selection/migration and security contract.
