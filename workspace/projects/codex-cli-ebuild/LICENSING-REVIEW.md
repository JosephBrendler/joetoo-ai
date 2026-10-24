# Concrete licensing and provenance follow-up for Codex 0.164.0

This follow-up concerns the proposed `dev-util/codex-cli-bin` package. The
workspace candidate is now named `codex-cli-bin-0.164.0.ebuild`; the user's
official candidate has not been accessed. No official overlay or upstream
repository was accessed. No policy change is needed to investigate or prepare candidate files.

## Work completed in this follow-up

- Resolved `rust-v0.164.0` to source commit
  `6aaac694803004a63c6f393d153c96d22521a6b9` through GitHub's commit API.
- Downloaded both canonical Linux packages and compared their SHA-256 values
  with GitHub's asset digests and upstream `codex-package_SHA256SUMS`: all match.
- Retrieved its `.sigstore` bundle. Its certificate claims the release workflow
  identity and source commit below. Reading a certificate is not authenticating it.
- Attempted complete signature verification using cosign v2.4.1, itself checked
  against that version's published release checksum. Verification stopped because
  the environment denies `https://tuf-repo-cdn.sigstore.dev/10.root.json`.
  No trust verification was disabled and no signature success is claimed.
- Downloaded libcap 2.75 from Debian's upstream-source mirror:
  `https://deb.debian.org/debian/pool/main/libc/libcap2/libcap2_2.75.orig.tar.xz`.
  SHA-256 is
  `de4e7e064c9ba451d5234dd46e897d7c71c96a9ebf9a0c445bc04f4742d83632`,
  exactly the value in the pinned Codex release's musl build script.
- Read that archive's actual root `License`, which offers BSD-3-Clause OR
  GPL-2.0-only. Prepared `files/libcap-2.75-LICENSE` verbatim, plus
  `files/libcap-2.75-COPYRIGHTS` containing the leading attribution/license
  comments from its library C/header files. BSD is an available choice for
  this component; no need to add GPL-2 merely because it is an alternative.
- Downloaded ratatui 0.30.2, checked the crate against Codex's Cargo.lock checksum,
  and compared its LICENSE with `files/Ratatui-MIT`: they are byte-identical.
  The earlier uncertainty about using a moving `main` license is now resolved.

## Exact remaining work

### 1. Authenticate both package archives

Run the following with a cosign installation and working Sigstore trust-metadata
network access. This is an artifact-verification operation, not a Portage build.
The current environment needs `tuf-repo-cdn.sigstore.dev` allowed to proceed past
its observed failure. Do not bypass certificate, transparency-log, or TUF checks.

For amd64:

```sh
cosign verify-blob \
  --bundle codex-package-x86_64-unknown-linux-musl.tar.gz.sigstore \
  --certificate-identity 'https://github.com/openai/codex/.github/workflows/rust-release.yml@refs/tags/rust-v0.164.0' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  codex-package-x86_64-unknown-linux-musl.tar.gz
```

Download both named files from the `rust-v0.164.0` release before running it.
Repeat with `aarch64` in place of `x86_64`. Record successful verification output,
archive hashes, source commit, and tool version. Both archives now match GitHub's asset digests and the release checksum file.
Neither architecture has completed signature verification here.

### 2. Complete the notices inventory for the three shipped executables

The deliverable is a table with: executable, incorporated component/version,
selected license, original notice file(s), source identity, and how the package
ships those notices. Only then finalize the ebuild's LICENSE expression and
installed notice set.

Use the pinned source and target-specific dependency graphs rooted at
`codex-cli`, `codex-code-mode-host`, and `codex-bwrap`, matching the release build's
features. Cargo.lock contains 1,474 packages across the whole workspace; treating
all of them as shipped, or assuming none of them need notices, would both be
incorrect. Development-only and other-target dependencies must be distinguished.
License scanners can generate candidate inventories, but their generic license
output must not replace original attribution-bearing files.

The pinned source identifies concrete native inputs requiring attention:

- libcap 2.75: exact source and license now obtained, as above.
- musl: identify the release builder's actual CRT/libc version and retain its
  COPYRIGHT/required notices, not a generic MIT template.
- OpenSSL 3.6.4: the release's `install-musl-openssl.sh` sets a static OpenSSL
  override and pins its source checksum. Check the selected executables' graph
  and obtain that version's required notices where incorporated.
- V8: `codex-code-mode-runtime` uses `v8` 152.2.0 with sandbox support, and the
  code-mode host depends on this runtime. `third_party/v8/README.md` documents
  embedded V8 15.2.124.1 and Codex-published native release inputs. The Rust crate's
  MIT label is not a complete inventory of its native V8/third-party code.
- ICU data: the runtime depends on `deno_core_icudata` 0.78.0. Retrieve the
  corresponding component license/notice files.
- Check selected Rust dependency/native build inputs such as jemalloc, bundled
  SQLite, AWS-LC, and zstd against the actual graph. Their presence in Cargo.lock
  alone is not proof that every executable incorporates them.

The canonical archive's only paths named LICENSE/NOTICE/COPYING are in the voice
subtree. This check did not discover a comprehensive notice bundle for the three
selected executables, nor did the GitHub release asset inventory expose an SBOM
or third-party-license asset. Source/license inventory generation remains work
for the contributor to perform; it is not a task requiring protected-repository
access or expanded AI permissions.

If exact native build provenance cannot be reconstructed from public inputs,
request this precise material from upstream (draft only; no message was sent):

> For rust-v0.164.0's x86_64/aarch64 musl CLI, code-mode host and bwrap binaries,
> please identify the incorporated Rust/native component versions and provide
> their third-party license/copyright notices and corresponding source/build
> materials. In particular, please identify the musl toolchain/CRT and V8/ICU
> inputs. We are preparing a voice-free Gentoo package of these release binaries.

### 3. Install the missing notice files

The libcap files prepared here can be added to the package's files directory.
The workspace ebuild now includes this `src_install` addition:

```bash
dodoc "${FILESDIR}/libcap-2.75-LICENSE" \
  "${FILESDIR}/libcap-2.75-COPYRIGHTS"
```

This addition is now applied to the workspace ebuild. It closes the identified
libcap notice omission, not the entire inventory. Install other components' actual
notices once step 2 identifies them. A component subdirectory or combined,
component-labeled THIRD-PARTY-NOTICES document is suitable, provided required
texts and attributions remain intact. Keep the existing Apache LICENSE, NOTICE,
Ratatui-MIT, and bubblewrap-COPYING installation.

### 4. Decide which distribution activity is being prepared

Publishing an ebuild that points to upstream downloads is different from
redistributing the downloaded archive or a built Gentoo binary package. Local
installation testing is also distinct. Do not describe every distributor's
source-delivery obligation as a prerequisite to merely testing the candidate.

If serving archives or binary packages, establish a specific compliant source
provision for LGPL-covered bubblewrap and any other components whose licenses
require it. Retain the exact modified sources, wrapper/build scripts, required
library inputs, and any necessary build/relink materials for that distribution.
The source must match the release binary, not just the latest upstream source.
Codex checks bwrap's embedded digest; any instructions for user-rebuilt helpers
must account for rebuilding the matching launcher rather than silently disabling
integrity verification. A COPYING file alone does not settle source obligations.

After these licensing/provenance tasks, Gentoo Manifest generation, package QA,
and native runtime tests are separate integration checks, not substitutes for
the inventory. No stable or testing keywords have been asserted here.
