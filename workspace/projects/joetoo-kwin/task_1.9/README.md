# Step 1.9 — Version 1 packaging and integration

**Kickoff status (2026-11-19): scope/inventory and maintainer authorization
pending; no production ebuild, install or deployment is claimed.** Step 1.7
(including former Step 1.8) was formally accepted and merged through
[PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33), `main` at
`df118da`. Its [archived evidence](../archive/task_step1.7/README.md) is the
accepted functional baseline. The [active dispatcher](HANDOFF.md) identifies
the next actor and permissible scope; this document is not an operation grant.

## Objective and boundaries

Deliver a maintainable Gentoo/OpenRC version 1 installation and upgrade path
for the already accepted X11/Wayland `joetoo-kwin` application. Package rather
than redesign the existing CLI, broker, KWin resident/native adapter, shared
Python libraries, configuration reference, templates and optional `eselect`
selector. The development installer's user-home layout is **not** a mandatory
production layout; preserve the application behavior and trust boundaries.

Official source/integration belongs to `joetoo-upstream` and Portage ebuilds,
profiles or package metadata to `joetoo`, under their **maintainer-operated**
AI policies. Authoring a bounded candidate in `joetoo-ai` does not authorize
writes to those repositories, native installation, service changes or release.

## First deliverable — packaging inventory and installation contract

Establish an explicit, reviewable manifest before editing production package
files. For each component, record the source path, runtime role, intended
system-wide installed path, executable/data mode and package ownership:

- `joetoo-kwin` CLI, Bash planning/launch helpers and each imported Python
  broker/registry/recovery/persistence, RDP, VNC and managed-close module
- `joetoo-kwind` **user-level** OpenRC unit, configuration defaults and any
  opt-in user OpenRC enable/start instructions; never substitute a root service
- KWin resident JavaScript and required native-close adapter, including its
  backend-specific installation/availability requirements
- configuration templates and `/etc/joetoo-kwin/` defaults, annotated
  documentation/user manual and optional user-owned `eselect` selector
- dependencies, executable lookup/resource paths, permission requirements,
  optional X11/Wayland/RDP/VNC features and package split if actually needed

Use [ARCHITECTURE §3](../ARCHITECTURE.md#3-components-and-ownership),
[§8](../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17),
[the accepted configuration reference](../docs/configuration-reference.md),
[the user manual](../docs/joetoo-kwin_user_manual.md),
`tools/joetoo-kwind-install-poc`, and
`tools/joetoo-kwind-configure-openrc-user` as source material. The POC's
per-user paths and dev-only backup/update machinery are evidence of an
existing workflow, **not** automatically the final packaged contract.

## Packaging acceptance targets (proposal for maintainer review)

1. **Install:** reproducible Gentoo build/merge owns all selected files and
   dependencies; version-specific paths and imports resolve as installed.
   Both KWin backends retain their accepted features and D-Bus interfaces.
2. **Safety:** package installation never writes personal HOME/configuration,
   activates a user service without consent, changes login shells, or destroys
   runtime managed-window state. User-owned OpenRC supervision remains separate
   from root package operations and must not own/kill application children.
3. **Configuration:** ship an annotated reference template separately from
   mutable user configuration; preserve documented global defaults, user and
   per-run precedence and the optional `eselect` workflow. Upgrades preserve
   existing user and administrator overrides.
4. **Lifecycle:** document explicit opt-in first-run, service start/stop,
   update, uninstall and rollback where supported; do not delete or implicitly
   replace private last-good snapshots, checkpoints or user-managed sessions.
5. **Verification:** metadata/QA and install-image inspection first; then
   maintainer-authorized Gentoo merge, non-destructive smoke checks and focused
   native X11/Wayland verification of the **packaged paths**. Do not retest
   the entire accepted Step 1.7 recovery/RDP/VNC matrix without a packaging
   change that warrants it.

The final path manifest, ebuild/package names, dependency policy, `eselect`
installation and release acceptance checks are **not yet approved** by this
kickoff. If choices materially alter interface, security or system integration,
return them for a maintainer decision before implementation.

## Scope exclusions and next transition

No new viewer protocol, RDP/VNC redesign, compositor registry rewrite, generic
plugin framework or Version 2 feature belongs in this milestone. Official
`joetoo`/`joetoo-upstream` integration and publication remain maintainer-owned.

The next concrete review item is a small source-to-destination packaging
manifest and installation/lifecycle plan against `main` at `df118da`; proceed
to a limited package candidate only after the maintainer approves that
contract. See [HANDOFF](HANDOFF.md).
