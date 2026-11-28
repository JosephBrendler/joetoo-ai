# joetoo-kwin — 0.1.0 source release

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

`joetoo-kwin` is a Gentoo/OpenRC-oriented tool for planning, launching,
placing, inspecting, recovering, and gracefully closing **managed windows**
under KDE Plasma/KWin. It brings together a Bash command-line interface,
a per-user D-Bus broker, resident KWin JavaScript, application-specific
launch helpers, and a small native KWin effect.

This is the **curated source distribution**, not a self-installing program.
The intended production delivery mechanism is the Gentoo
`dev-util/joetoo-kwin` ebuild. Building the source archive does not install
the software, configure a user account, start the broker, or load a KWin effect.

## Initial compatibility boundary

Version **0.1.0** is being prepared from the implementation accepted against
**KWin 6.7.6**. The native effect is particularly version-sensitive: its CMake
configuration currently requires the **6.7.6 SDK exactly**, and the KWin
effect loader checks version-specific plugin identity. Rebuild native effects
against their matching installed SDK; do not reuse an incompatible `.so`.

- **Wayland session:** the native Wayland effect supports managed inspection,
  recovery verification, and graceful close for both native Wayland and
  **XWayland** windows.
- **XWayland clients:** the Wayland effect calls the separate
  `joetoo-kwin-close-x11` executable for a bounded `WM_DELETE_WINDOW`
  request. That helper uses libxcb; it does **not** depend on the legacy
  `KWinX11` SDK.
- **Legacy native-X11 session:** a distinct build of the same
  `adapter.cpp` source targets `kwin_x11` and installs to a different
  KWin plugin namespace. Whether this optional legacy variant is packaged
  is an ebuild policy decision, not an XWayland requirement.

Compatibility with KWin 6.8 and later has **not** been established by the
initial 6.7.6 acceptance work. This source archive does not contain a
prebuilt native effect or an automatic upgrade/rebuild mechanism.

## Components in the source tree

| Path | Role |
| --- | --- |
| [`joetoo-kwin`](joetoo-kwin) | Bash CLI: trusted configuration, planning, explicit confirmation, and user-facing operations |
| [`libexec/`](libexec/) | Python broker `joetoo-kwind`, Bash planning/launch functions, application launchers, validation, managed-close and recovery helpers |
| [`joetoo-kwin-resident.js`](joetoo-kwin-resident.js) | Resident KWin script for observation and placement; it does not independently authorize managed ownership |
| [`native/managed-close/`](native/managed-close/) | C++ effect source, X11 protocol helper, CMake definitions, and native protocol documentation |
| [`user-init.d/joetoo-kwind`](user-init.d/joetoo-kwind) | OpenRC **user** service for the broker, not a root-managed system daemon |
| [`conf.d/`](conf.d/) and [`user-conf.d/`](user-conf.d/) | Global service configuration and optional administrator override example |
| [`account-conf.d/`](account-conf.d/) | Inactive example of a per-account OpenRC service override |
| [`config-examples/`](config-examples/) | Inactive examples of sparse system/user CLI defaults |
| [`joetoo-kwin-per-run-template.conf`](joetoo-kwin-per-run-template.conf) | Short, copyable launch-plan template |
| [`joetoo-kwin-template.conf`](joetoo-kwin-template.conf) | Long, annotated configuration reference template |
| [`eselect/`](eselect/) | Optional-to-use user profile selection module (intended to be installed with the package) |
| [`docs/`](docs/) | User manual and comprehensive CLI configuration reference |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Design and component ownership; historical links may refer to the separate development repository |
| [`MANIFEST`](MANIFEST) | Record of files curated from `joetoo-ai`, including the mapping from development `release/README.md` to this root `README.md` |

The per-configuration `README_*_conf.md` companions are intentionally kept
**beside their corresponding source files or examples**. This source-tree
organization does not mean those READMEs or optional examples should be
activated as configuration under `/etc` or a user's home directory.

## Configuration and first use

The CLI launch-plan hierarchy is distinct from OpenRC service configuration.

**CLI launch settings**, from lowest to highest precedence:

1. Built-in defaults.
2. Optional `/etc/joetoo-kwin/defaults.conf`.
3. Optional `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf`.
4. One selected per-run plan: explicit `-f FILE`, otherwise the user's
   `joetoo-kwin/joetoo-kwin.conf`, falling back to
   `/etc/joetoo-kwin/joetoo-kwin.conf` only when the user plan is absent.
5. Supported CLI overrides.

**OpenRC broker service settings** use the separate hierarchy of global
`/etc/conf.d/joetoo-kwind`, optional administrator
`/etc/user/conf.d/joetoo-kwind`, and optional per-account
`rc/conf.d/joetoo-kwind` within the user's XDG configuration directory.
Read the colocated configuration READMEs for precedence and path safeguards.

Configuration files consumed by the CLI are **trusted executable Bash**,
not passive INI data. Inspect any copied plan before validating it. The
short template contains illustrative screen dimensions; set the actual
`screen_width` and `screen_height` of the target desktop explicitly.
It is not safe to launch unreviewed example remote endpoints.

After the ebuild has been installed and the user service has been configured
by the operator, typical CLI operations include:

```bash
# Validate and preview an inspected, edited plan; do not launch anything.
joetoo-kwin -c -f /path/to/your/plan.conf

# Launch only after reviewing the plan and its explicit confirmation prompt.
joetoo-kwin -o -f /path/to/your/plan.conf

# End of commands
```

The command `-c` does not launch planned applications, but it **does**
source trusted configuration. Neither the source archive nor the ebuild
should silently populate or replace a user's active configuration, enable a
service, or load a native KWin effect.

## Documentation

- [User manual](docs/joetoo-kwin_user_manual.md): CLI operations, managed
  inventory, close/recovery behavior, and operator troubleshooting.
- [Configuration reference](docs/configuration-reference.md): load order,
  supported settings, recipe grammar, and validation limits.
- [Architecture](ARCHITECTURE.md): component boundaries and accepted safety
  invariants.
- [Native managed-close README](native/managed-close/README.md):
  native effect build/loader boundary, authenticated identity checks, and
  graceful-close protocol.
- [Launch-plan companion](README_joetoo_kwin_launch_conf.md) and
  [template companion](README_joetoo_kwin_templates_conf.md).
- [OpenRC global](conf.d/README_global_joetoo_kwind_conf.md),
  [administrator override](user-conf.d/README_system_user_joetoo_kwind_conf.md),
  and [account override](account-conf.d/README_account_joetoo_kwind_conf.md)
  companions.
- [System defaults](config-examples/system/README_system_defaults_conf.md),
  [user defaults](config-examples/user/README_user_defaults_conf.md), and
  [eselect configs](eselect/README_eselect_configs_conf.md) companions.

## Build, installation, and distribution notes

The native C++ build is defined in
[`native/managed-close/CMakeLists.txt`](native/managed-close/CMakeLists.txt).
It uses installed Qt6, KWin/KWinX11, KDE/ECM, and XCB development files.
**Compiling requires no running graphical session**; installing and loading
the resulting native effect are separate, explicit operator activities.
See the native README for the two independent compositor builds.

The intended ebuild installs the CLI under `/usr/bin/`, private runtime
helpers under `/usr/libexec/joetoo-kwin/`, and the broker's OpenRC user
service under `/etc/user/init.d/`. The global service configuration belongs
under `/etc/conf.d/`. Additional package paths, dependencies, optional
features, and upgrade behavior are determined and validated by the ebuild;
this README is not an alternative installation procedure.

This archive is intentionally **curated**, rather than a copy of the
development workspace. Historical task handoffs, archived experiments,
transcripts, POC installers, scratch tools, and other development-only
materials are omitted. Source files and documentation here should be
sufficient for the subsequently reviewed package build; they are not a
record of all historical acceptance tests.

Licensing and copyright information is recorded in individual source
headers, [`LICENSES.package`](LICENSES.package), and
[`COPYRIGHT.exceptions`](COPYRIGHT.exceptions). The `tarup` release process
adds the repository `LICENSE` and applicable `LICENSES/` texts to the
staged archive. These metadata files do not replace the maintainer's
final source-provenance and copyright audit before publication.

For development history, tests, and task-specific evidence, consult the
separate [joetoo-ai project](https://github.com/JosephBrendler/joetoo-ai/tree/main/workspace/projects/joetoo-kwin).
The curated archive and associated Gentoo packaging are maintained in
[joetoo-upstream](https://github.com/JosephBrendler/joetoo-upstream) and
[joetoo](https://github.com/JosephBrendler/joetoo), respectively.
