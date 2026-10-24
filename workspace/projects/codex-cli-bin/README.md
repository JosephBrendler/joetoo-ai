# Gentoo Codex CLI binary candidate

Target package: **dev-util/codex-cli-bin-0.164.0-r1**, EAPI 8.

This is a thin Gentoo installer for OpenAI's official
`codex-package-<target>.tar.gz` release archives. OpenAI's standalone installer
uses these same package archives. The checked `rust-v0.164.0` GitHub release has
no `.deb` or `.rpm` assets. We are adapting an upstream binary package rather
than building or assembling Codex from source.

## Files to incorporate

```text
dev-util/codex-cli-bin/
├── codex-cli-bin-0.164.0-r1.ebuild
├── metadata.xml
├── Manifest
└── files/
    ├── Ratatui-MIT
    ├── libcap-2.75-LICENSE
    ├── libcap-2.75-COPYRIGHTS
    ├── ripgrep-15.2.0-COPYING
    ├── ripgrep-15.2.0-LICENSE-MIT
    └── ripgrep-15.2.0-UNLICENSE
```

The maintainer-returned `metadata.xml` and Manifest from baseline `e4ccd06`
are retained unchanged. All distfile names and bytes remain unchanged in r1.
Regenerate the Manifest in the destination repository through the normal workflow.
Do not copy collaboration reports into the package's `files/` directory.

**Start with [INCORPORATING.md](INCORPORATING.md)** for exact human-run copy,
Manifest, QA, and install commands. Those commands have not been executed against
the official overlay.

## Installation behavior

| Payload | Destination |
| --- | --- |
| CLI | `/usr/libexec/codex/bin/codex` |
| Code-mode host | `/usr/libexec/codex/bin/codex-code-mode-host` |
| Matching bubblewrap | `/usr/libexec/codex/codex-resources/bwrap` |
| Bundled ripgrep | `/usr/libexec/codex/codex-path/rg` |
| Package metadata | `/usr/libexec/codex/codex-package.json` |
| Public command | `/usr/bin/codex` relative symlink to the private CLI |
| Upstream, Ratatui, libcap, bubblewrap and ripgrep notices | `/usr/share/doc/codex-cli-bin-0.164.0-r1/` (Portage may compress them) |

The package rename does not rename the upstream command or resource layout.
There is no Node/npm launcher, source compilation, setuid mode, or capability
assignment. `RESTRICT=strip` preserves upstream's bubblewrap digest; targeted
`QA_PREBUILT` entries describe the four binaries.

Voice remains excluded. Revision r1 restores upstream's bundled ripgrep because
the background server requires `codex-path/rg` inside the package root. The
original system-ripgrep substitution broke normal session resume; an escaping
symlink does not satisfy the package-copy validator either. See
[DAEMON-FIX.md](DAEMON-FIX.md) for the diagnosis and supported `--no-daemon`
workaround. Existing system ripgrep need not be removed.

The CLI, code-mode host and bwrap are static on amd64 and arm64. Bundled amd64
ripgrep is also static; bundled arm64 ripgrep requires glibc >=2.18 and libgcc_s.
The r1 candidate declares those arm64 dependencies and therefore does not
support an arm64 musl-only system. Native arm64 execution is still untested.

`SRC_URI` fetches the Apache LICENSE, NOTICE and bubblewrap COPYING from the
release tag into `${DISTDIR}`. They need not be in `files/`. `newdoc` installs
them; `dodoc` installs the six supplemental local files listed above.

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

## Accepted baseline and maintainer feedback

Baseline: maintainer commit `e4ccd06`, returning official-integration edits to
`workspace/projects/codex-cli-bin/`. The r1 fix is applied to that ebuild, not the
previous generated draft. It preserves the maintainer's header, line wrapping,
empty-global cleanup, metadata.xml, and Manifest.

Human-reported results for the original 0.164.0 package on gmki91: pkgcheck clean,
Portage installation successful, expected executable/doc layout, version/help
working, corrected `codex sandbox -- /bin/true` returning 0, and an interactive
hello.sh edit completed. Normal session resume then exposed the missing-rg
packaging defect. These results do not constitute r1 or arm64 validation.

## Validation

The renamed candidate is checked with Bash syntax, whitespace, and a local
phase-staging harness for both architectures. The harness substitutes ordinary
filesystem operations for Portage helpers; it is not a Portage build. The check
covers the renamed distfile paths, installed relative symlink, binary bytes and
modes, and all nine installed license/notice documents. The staged amd64 command
is smoke-tested with `--version` and `--help`.

The agent has not run native Gentoo Portage/pkgcheck, arm64 execution, or an
authenticated session. Human results for the baseline are recorded above; native
r1 resume still needs testing. `KEYWORDS` remains empty.

The earlier cloud smoke test used the incorrect `sandbox linux` syntax and
failed with:

```text
error building bubblewrap command: app-server socket directory must be a user-owned directory with mode 0700
```

The correct command for this release is `codex sandbox -- /bin/true`; the
maintainer reports it succeeds on Gentoo. Cloud daemon readiness remains blocked
by a socket-directory validation error even after r1 passes package preparation.
That separate cloud result does not invalidate the human Gentoo smoke test.
