# Configuration templates: short starter and annotated reference

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired root files:** `joetoo-kwin-per-run-template.conf` and
`joetoo-kwin-template.conf`. Both are **inert documentation/examples** until
the user explicitly copies or selects one; the ebuild must not create active
files under HOME.

- **Short starter:** `joetoo-kwin-per-run-template.conf` (~30 lines), designed
  to become an edited per-run plan. It sets an explicit display size and two
  local-only example recipes, with optional remote recipes commented out.
- **Long reference:** `joetoo-kwin-template.conf` (~130 lines), documenting
  geometry policy, RDP/VNC/SFTP bounds, close/recovery settings and sample
  recipes. Its illustrative SSH targets include `example.invalid`; **do not**
  launch it unchanged. Use the configuration reference for full validation.

The planned installed template path for the short starter is
`/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf`. Package layout
for the long annotated reference is subject to the reviewed ebuild.
Do not confuse these templates with either additive `defaults.conf` or with
an automatically active `joetoo-kwin.conf`; copy only the settings that
belong in the desired file and preserve existing plans during upgrades.

Read [`README_joetoo_kwin_launch_conf.md`](README_joetoo_kwin_launch_conf.md)
and [`docs/configuration-reference.md`](docs/configuration-reference.md).
