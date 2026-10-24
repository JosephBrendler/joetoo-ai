# joetoo-kwin-plan (dry-run-only prototype)

This is a stand-alone **planner**, not an update to the working KWin Python broker,
resident JavaScript, or launch test drivers. No GUI/D-Bus operations, subprocess
launches, SSH checks, or networking are performed.

Copy both files into one directory on a joetoo workstation. The tool uses
`/usr/sbin/script_header_joetoo`, following existing joetoolkit conventions.

```bash
chmod +x joetoo-kwin-plan
./joetoo-kwin-plan
./joetoo-kwin-plan -c ./desktop_sessions.conf
```

The config is trusted Bash (sourced), as with the legacy
`xdotool_open_windows.conf`. Its session entries use four literal fields:
`desktop|program|mode|target`. The initial allowed mode names are `swr`,
`via-ssh`, `local`, and `direct`; **they are names only** at this stage. No
command construction is implemented.

- `swr` refers to the user's existing Bash function, **not an executable**.
- `via-ssh` is a placeholder for the eventual TigerVNC-over-SSH policy.
- `local` denotes a program within Konsole, e.g. `btop`.
- `direct` is reserved for launching a graphical program without a connection.

This version validates session records and allows 1–4 intended windows per desktop:
- one: 94% width, 85% height, at (1%, 5%)
- two: 46% width, 85% height, at (1%, 5%) and (51%, 5%)
- three/four: two columns with the same X and width percentages, two rows
  at Y=5% and 49%, each 40% tall

For simplicity, percentages are converted to whole pixels using the explicitly
configured `screen_width` and `screen_height`, not queried from KWin.
The initial geometry rules are proposals for inspection, not agreed final policy.
The script does not assume that a successful ping is required for a window to exist.

`desktop_limit` is an *expected* desktop count set in the config for validation;
the planner does not query KWin to confirm that these desktops exist. All
records are emitted in config order. The number of windows per desktop is
computed from *configured records*, not reachable hosts.

Before integrating with the existing launcher, revisit how screen selection,
window layout preferences, SSH failure placeholders, and `swr` shell
initialization should be configured. Per-window launch correlations are not
implemented here.
