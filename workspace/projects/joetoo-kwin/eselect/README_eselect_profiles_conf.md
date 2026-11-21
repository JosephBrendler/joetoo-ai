# Optional per-account launch profile selection

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired selector implementation:** `eselect/joetoo-kwin.eselect`.
**Installed selector module:** `/usr/share/eselect/modules/joetoo-kwin.eselect`.
The package always installs the module, but **using it is optional**.
It manages only the selected user launch-plan symlink, not OpenRC configuration
or either `defaults.conf` layer.

For the current account, the profile directory is
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/profiles/`, with a relative
XDG_CONFIG_HOME falling back to `$HOME/.config`. The active selection path is
`joetoo-kwin/joetoo-kwin.conf` in that same configuration root. The user
creates profiles explicitly; neither Portage nor `eselect list/show` populates
HOME. As the intended **non-root** user, first make a safe private directory,
copy a reviewed short template to `profiles/work.conf`, and edit its display
size and recipes. Do not set a profile blindly merely because a file exists.

Typical sequence after reviewing the file:

```bash
config_root=${XDG_CONFIG_HOME:-$HOME/.config}
[[ $config_root == /* ]] || config_root=$HOME/.config
install -d -m 0700 -- "$config_root/joetoo-kwin/profiles"
cp -n -- /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf     "$config_root/joetoo-kwin/profiles/work.conf"
chmod 600 -- "$config_root/joetoo-kwin/profiles/work.conf"
# Edit and inspect work.conf first, then:
joetoo-kwin -c -f "$config_root/joetoo-kwin/profiles/work.conf"
eselect joetoo-kwin list
eselect joetoo-kwin set work.conf
eselect joetoo-kwin show
# End of commands
```

`list` indicates the current safe selection with the framework's marker.
`set` uses a profile basename such as `work.conf` (or a list number), and
creates only its controlled selection artifacts. It refuses to replace an
existing regular active plan or an unsafe/dangling link. Migrating such a
file is a deliberate, separate user action; the selector never overwrites it.
The profiles must be user-owned regular files, one link, safe permissions and
valid Bash syntax. All profile content is **trusted executable Bash** when
loaded by the CLI; the selector itself does not source it.

See [`../docs/configuration-reference.md`](../docs/configuration-reference.md)
for the complete selection/migration and security contract.
