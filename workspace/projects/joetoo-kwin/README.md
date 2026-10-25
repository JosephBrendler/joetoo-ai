# joetoo-kwin

Active engineering sources for joetoo-kwin in the joetoo-ai collaboration
repository. Current milestone: Step 1.2b (KWin resident-script
initialization and reconnection). The Step 1.2a OpenRC user-service
lifecycle was validated on gmki91/X11 and q552u01/Wayland.

## Active files

- `libexec/joetoo-kwind` — foreground Python D-Bus broker
- `user-init.d/joetoo-kwind` — OpenRC user service
- `conf.d/joetoo-kwind` — global executable default
- `user-conf.d/joetoo-kwind` — optional administrator override template
- `poc-user-conf.d/joetoo-kwind` — per-user POC executable override
- `tools/` — POC installation and OpenRC user environment configuration
- `tests/` — Step 1.2a regression tests

The promoted broker does not yet activate resident KWin JavaScript.
The Step 1 CLI and its coupled `joetoo-kwin-plan-functions` remain together
under `archive/step1-candidate/` until launcher integration.
`archive/step1.2a-candidate/NATIVE_VALIDATION.md` records the completed
native lifecycle checks. `archive/README.md` indexes historical POCs.

`ARCHITECTURE.md` records the design and milestone definitions.
These are development sources, not the final installed Gentoo package.
