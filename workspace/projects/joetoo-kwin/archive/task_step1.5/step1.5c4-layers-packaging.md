# Packaging recommendations for maintainer integration

No ebuild, protected repository, installed file or user configuration was changed.

- Install joetoo-kwin-template.conf as readable template data, for example under
  /usr/share/joetoo-kwin/. Do not automatically populate or overwrite HOME/.config.
- The user may copy/edit it at ${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf.
  Empty/unset/relative XDG roots follow the documented HOME fallback.
- /etc/joetoo-kwin/joetoo-kwin.conf remains an optional system fallback only when no
  user file exists. Any system-config installation/CONFIG_PROTECT policy is a human
  ebuild decision; do not replace a user's selection with the template.
- Install the exposure helper with the existing CLI helpers, preserving their expected
  relative libexec location or adapting that location explicitly during integration.
  Pure offline planning now requires Python3 for rectangle exposure prediction.
  Existing dbus-python, jq, flock and application dependencies remain relevant.
- Broker and resident must be upgraded together for initial_layout_protocol=1; older
  clients keep their existing D-Bus contracts, but a new -o must not run layered geometry
  against an old resident and imply full initialization. Native reload/install is human work.
- Announce migration: four-field graphical entries now mean panel; explicit under/over
  preserves large-graphical intent. Desktop groups execute by first occurrence, not global
  file order. The template uses illustrative targets and must be reviewed before real SSH.
