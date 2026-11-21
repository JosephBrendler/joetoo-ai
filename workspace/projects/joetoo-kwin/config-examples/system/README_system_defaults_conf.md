# Optional system-wide CLI defaults — `defaults.conf`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Paired example:** `config-examples/system/defaults.conf`.
**Optional active destination:** `/etc/joetoo-kwin/defaults.conf`, managed by
the administrator. The ebuild should ship this example as documentation, not
activate it silently or overwrite a live administrator file.

The CLI loads configuration in this order: built-in `plan_defaults()`;
**this system defaults file** if present; optional user defaults; exactly
one chosen per-run plan; then supported CLI overrides. Later layers can
replace a variable set here. The example sets
`terminal_width_percent=80`; adapt the value to local policy before copying.

This is **trusted Bash executable code**, not a key-value format. Even
`joetoo-kwin -c` sources it. Keep the actual `/etc` file root-owned and not
writable by other users; present-but-invalid files cause validation failure.
If absent, built-in defaults remain in force. A user plan supplied with `-f`
still loads preceding system and account defaults.

The filename is deliberately different from
`/etc/joetoo-kwin/joetoo-kwin.conf`: that is a **fallback per-run plan**, not a
system defaults layer. The configuration reference documents the full list
of variables and their validation ranges:
[`../../docs/configuration-reference.md`](../../docs/configuration-reference.md).
