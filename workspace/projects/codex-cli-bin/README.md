# Gentoo Codex CLI binary candidate

Target package: **dev-util/codex-cli-bin-0.164.0**, EAPI 8.

This is a thin Gentoo installer for OpenAI's official
`codex-package-<target>.tar.gz` release archives. OpenAI's standalone installer
uses these same package archives. The checked `rust-v0.164.0` GitHub release has
no `.deb` or `.rpm` assets. We are adapting an upstream binary package rather
than building or assembling Codex from source.

## Files to incorporate

```text
dev-util/codex-cli-bin/
├── codex-cli-bin-0.164.0.ebuild
└── files/
    ├── Ratatui-MIT
    ├── libcap-2.75-LICENSE
    └── libcap-2.75-COPYRIGHTS
```

Add or retain the overlay's own `metadata.xml`. Do not copy this README,
INCORPORATING.md, or LICENSING-REVIEW.md into the package's `files/` directory.
There is no generated Manifest in this workspace; create it in the destination
repository using the instructions below.

**Start with [INCORPORATING.md](INCORPORATING.md)** for exact human-run copy,
Manifest, QA, and install commands. Those commands have not been executed against
the official overlay.

## Installation behavior

| Payload | Destination |
| --- | --- |
| CLI | `/usr/libexec/codex/bin/codex` |
| Code-mode host | `/usr/libexec/codex/bin/codex-code-mode-host` |
| Matching bubblewrap | `/usr/libexec/codex/codex-resources/bwrap` |
| Package metadata | `/usr/libexec/codex/codex-package.json` |
| Public command | `/usr/bin/codex` relative symlink to the private CLI |
| LICENSE, NOTICE, Ratatui, libcap, bubblewrap notices | `/usr/share/doc/codex-cli-bin-0.164.0/` (Portage may compress them) |

The package rename does not rename the upstream command or resource layout.
There is no Node/npm launcher, source compilation, setuid mode, or capability
assignment. `RESTRICT=strip` preserves upstream's bubblewrap digest; targeted
`QA_PREBUILT` entries describe the three binaries.

The existing scope is unchanged: upstream's voice runtime is excluded and
Gentoo's `sys-apps/ripgrep` supplies `rg` instead of the bundled copy. This is a
voice-free CLI candidate, not every feature in the upstream package. Supported
archive targets are x86_64 musl (`amd64`) and aarch64 musl (`arm64`). The six
selected binaries were identified as statically linked ELF files for their
respective architectures. This does not establish every kernel/CPU/profile's
runtime compatibility.

`SRC_URI` fetches the Apache LICENSE, NOTICE and bubblewrap COPYING from the
release tag into `${DISTDIR}`. They need not be in `files/`. `newdoc` installs
them; `dodoc` installs the three supplemental local files listed above.

## Licensing and provenance evidence

Source commit for `rust-v0.164.0`:
`6aaac694803004a63c6f393d153c96d22521a6b9`.

- Ratatui-MIT is byte-identical to ratatui 0.30.2's LICENSE. Its crate was checked
  against Codex's Cargo.lock checksum.
- libcap's exact 2.75 source archive matches the release build's pinned SHA-256
  `de4e7e064c9ba451d5234dd46e897d7c71c96a9ebf9a0c445bc04f4742d83632`.
  Its actual License and library-source copyright headers are now installed.
- Both Linux packages match GitHub's asset digests and the release checksum file.
- Full signature verification was attempted but blocked while fetching Sigstore
  trust metadata from `tuf-repo-cdn.sigstore.dev`. No verification was disabled.

`LICENSE="Apache-2.0 BSD MIT LGPL-2+"` describes the terms identified so far.
The full incorporated-component notice inventory is not finished; concrete
remaining work and the exact signature-verification command are in
[LICENSING-REVIEW.md](LICENSING-REVIEW.md). Local installation testing and
redistributing binary artifacts are separate activities. Publishing an ebuild
that references upstream downloads is not itself the same as hosting those
binary artifacts.

## Validation

The renamed candidate is checked with Bash syntax, whitespace, and a local
phase-staging harness for both architectures. The harness substitutes ordinary
filesystem operations for Portage helpers; it is not a Portage build. The check
covers the renamed distfile paths, installed relative symlink, binary bytes and
modes, and all six installed license/notice documents. The staged amd64 command
is smoke-tested with `--version` and `--help`.

No native arm64 execution, Gentoo Portage installation, pkgcheck run, or
interactive/authenticated agent session has been performed here. `KEYWORDS`
remains empty pending native Gentoo validation.

The earlier amd64 sandbox smoke test failed with:

```text
error building bubblewrap command: app-server socket directory must be a user-owned directory with mode 0700
```

The responsible socket directory was not identified. Test sandbox behavior in the
native Gentoo environment; this cloud result establishes neither compatibility
nor incompatibility there. Do not describe sandbox operation as validated yet.
