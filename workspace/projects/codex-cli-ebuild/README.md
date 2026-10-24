# Codex CLI binary ebuild candidate

This is collaboration material for human review and eventual incorporation into
an official overlay. It is not an overlay or an install-ready, validated Gentoo
package. Work here does not authorize changes or development workflows in
`joetoo` or `joetoo-upstream`. Follow the root and workspace `AGENTS.md` files.

## Candidate scope and changes

The candidate targets Codex CLI **0.164.0**, EAPI **8**, and upstream's Linux musl
builds for Gentoo `amd64` (x86_64) and `arm64` (aarch64). No other architecture
is supported. `KEYWORDS` remains empty: availability of an upstream binary is
not native Gentoo validation or grounds for stabilization.

The original standalone archives contain only the target-suffixed `codex`
executable. Upstream's canonical package additionally supplies the code-mode
host, matching bubblewrap, ripgrep, package metadata, and a voice runtime.
Installing only the original executable omits runtime resources.

The refined candidate fetches the canonical package and installs this subset:

```text
/usr/bin/codex -> ../libexec/codex/bin/codex
/usr/libexec/codex/bin/codex
/usr/libexec/codex/bin/codex-code-mode-host
/usr/libexec/codex/codex-package.json
/usr/libexec/codex/codex-resources/bwrap
/usr/share/doc/codex-bin-0.164.0/{LICENSE,NOTICE,Ratatui-MIT,bubblewrap-COPYING}
```

Portage may compress installed documentation. The private layout preserves
upstream install-context discovery after resolving the public symlink. No
setuid bits or capabilities are installed. No Node.js/npm launcher is needed.
Configure and compile are explicit no-ops. `QA_PREBUILT` identifies only the
three installed prebuilt executables; `RESTRICT=strip` preserves the matching
bubblewrap digest embedded in Codex, and `RESTRICT=test` reflects the absence of
a source test suite in this binary package. This does not replace human runtime
testing. `pkg_postinst` gives product guidance rather than repository-specific
access policy.

Bundled ripgrep is not installed; `RDEPEND=sys-apps/ripgrep` supplies `rg` via
upstream's PATH fallback. The optional voice subtree is also not installed.
Its native libraries include GLib/GStreamer and other dependencies under several
licenses, and its helper uses a GNU/glibc target rather than musl. Thus the
static-linking observation below applies only to the installed subset, not the
whole upstream archive. Voice support would need a separate packaging design,
dependency/license audit, and tests. The standalone responses API proxy is not
in the canonical package; the CLI source includes a responses-api-proxy
subcommand. No separate proxy executable is installed or tested.

## Evidence checked

Release-specific sources (not `main`):

- [Release tag and assets](https://github.com/openai/codex/releases/tag/rust-v0.164.0)
- [Release workflow](https://github.com/openai/codex/blob/rust-v0.164.0/.github/workflows/rust-release.yml)
- [Package builder](https://github.com/openai/codex/blob/rust-v0.164.0/.github/scripts/build-codex-package-archive.sh)
- [Install context and resource discovery](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/install-context/src/lib.rs)
- [Bundled bubblewrap lookup and digest verification](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/linux-sandbox/src/bundled_bwrap.rs)
- [CLI dispatch](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/cli/src/main.rs)
- [Apache license](https://github.com/openai/codex/blob/rust-v0.164.0/LICENSE),
  [NOTICE](https://github.com/openai/codex/blob/rust-v0.164.0/NOTICE), and
  [bubblewrap license](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/vendor/bubblewrap/COPYING)
- [Portage ebuild manual source](https://github.com/gentoo/portage/blob/master/man/ebuild.5)
  for `QA_PREBUILT`, `RESTRICT`, and installation conventions.

Both original standalone download paths and both canonical package paths
resolved and were downloaded over verified HTTPS. The GitHub release API
returned HTTP 403; artifact checks used direct release downloads instead.
Archive contents were inspected for both architectures. `file` identified all
six selected executables (CLI, code-mode host, bubblewrap on each architecture)
as stripped, statically linked ELF binaries for the expected architecture.
`readelf` also inspected amd64 CLI program headers, with no dynamic interpreter.
Both bundled bubblewrap SHA-256 literals occur in their matching CLI binary.

Observed archive SHA-256 values:

| Release asset | SHA-256 |
| --- | --- |
| `codex-x86_64-unknown-linux-musl.tar.gz` | `90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4` |
| `codex-aarch64-unknown-linux-musl.tar.gz` | `29a507a2a3fd8f6cd94b96b762d281d299d15d7902dee6132d314b78cf9108eb` |
| `codex-package-x86_64-unknown-linux-musl.tar.gz` | `3ec55053109608d5038f7e50750f7d25f768dfd740fef071aa710e2559b63aac` |
| `codex-package-aarch64-unknown-linux-musl.tar.gz` | `5918add6c7e9cf1e14a9af1b4c0f4bf1d24a43903faac26df5dc4c019ea91bd5` |

These are locally calculated observations, not independently authenticated
upstream checksums. Sigstore release signatures/attestations were not verified.
They do not substitute for a Portage Manifest or release provenance validation.

## Licensing status

The root upstream license is Apache-2.0. Its NOTICE identifies MIT-licensed code
derived from Ratatui. Both are now installed, together with full Ratatui MIT
terms in `files/Ratatui-MIT`; that file was retrieved from
https://raw.githubusercontent.com/ratatui/ratatui/main/LICENSE and matches the
copyright attribution in Codex's release NOTICE.
Vendored bubblewrap identifies itself as LGPL-2.0-or-later; its COPYING is also
installed, and Gentoo's corresponding license identifier is `LGPL-2+`.

The release's musl-toolchain script builds static libcap 2.75 into the native
build environment. libcap's general terms offer BSD-style conditions or GPL-2;
BSD is provisionally included in `LICENSE`. The general license was inspected
in https://github.com/mhiramat/libcap/blob/master/License, not authenticated
against the exact 2.75 source archive (the kernel.org download returned 403).
Confirm the exact linked library provenance and required copyright notices.

**Licensing review is incomplete.** `LICENSE` lists known terms, not a complete
audit of all statically linked Rust/native dependencies. In particular, obtain
an exact dependency/license inventory, required notices for musl, libcap, and
other linked components, and satisfy LGPL corresponding-source/relinking
obligations as applicable before distribution. Excluding voice avoids installing
its libraries but does not make the remaining binary Apache-only. Resolve
distfile-mirroring/source-availability obligations too: the fetched full archive
still contains voice components even though this ebuild does not install them.

## Checks performed and limits

Passed:

- `bash -n codex-bin-0.164.0.ebuild` and `git diff --check`.
- A local shell harness ran the candidate's unpack, configure, compile, and
  install functions for each architecture with stand-ins for Portage helpers.
  Both staged images had the intended relative symlink, executable modes, and
  byte-identical CLI, host, and bubblewrap files; voice and bundled rg were absent.
  **This was not a Portage build or package-manager QA check.**
- On the x86_64 cloud host, the staged public symlink returned
  `codex-cli 0.164.0`; amd64 `--help` also completed. A project-local isolated
  Codex home was used for clean smoke checks and then removed.
- amd64 bundled bubblewrap returned `bubblewrap built for Codex` for `--version`.

Failed/unverified:

- `codex sandbox linux -- /usr/bin/true` exited 1 with
  `error building bubblewrap command: app-server socket directory must be a user-owned directory with mode 0700`.
  This persisted with an isolated mode-0700 Codex home and temporary directory.
  The responsible socket directory was not identified. This does not establish
  sandbox compatibility or incompatibility on Gentoo.
- No native arm64 execution; no Gentoo/glibc or Gentoo/musl runtime validation.
- No Portage or pkgcheck executable was available; no Manifest, emerge,
  dependency-resolution, package-manager installation, or uninstall tests ran.
- No authenticated API/ChatGPT session, TUI interaction, model requests,
  code-mode session, daemon/MCP workflow, or execution approval behavior tested.
- No kernel minimum, CPU baseline, hardened-kernel/user-namespace compatibility,
  or Gentoo Prefix compatibility established. Static ELF is not proof of these.
- System-ripgrep fallback was verified in source, not in an end-to-end session.

## Human integration checklist

1. Finish the dependency/license and provenance review above. Verify upstream
   signature/attestation identities and retain corresponding source/notices.
   Decide whether the reduced, voice-free scope is acceptable before packaging.
2. Choose the official category and confirm the `codex-bin` name, ownership,
   metadata.xml, repository requirements, and any `/usr/bin/codex` collision or
   blocker against existing packages. No official overlay was inspected here.
3. Copy the reviewed ebuild **and `files/Ratatui-MIT`** into that package
   directory. Generate a fresh Manifest with
   `ebuild codex-bin-0.164.0.ebuild manifest`; run pkgcheck for that package and
   address findings. Ensure distfile and package redistribution meet licensing
   obligations before publishing or mirroring either.
4. In a disposable Gentoo environment, explicitly accept the unkeyworded
   candidate for this package only (`**`), then validate dependency resolution,
   fetch/unpack/prepare/install, file ownership/modes, runtime resource discovery,
   and clean uninstall. Review Portage QA without suppressing unexplained issues.
5. Test natively on each intended architecture and libc/profile: version/help,
   interactive startup, system `rg`, approved authentication and a minimal agent
   session in a disposable project, code-mode host, and sandbox allow/deny
   behavior. Diagnose the socket-directory failure before claiming sandbox
   readiness. Do not disable sandboxing merely to obtain a passing test.
6. Add only architecture testing keywords supported by those results (for
   example `~amd64`, and `~arm64` after arm64 testing). Stable keywords require
   separate stabilization evidence. Human review, commit, push, and official
   overlay incorporation remain separate actions.
