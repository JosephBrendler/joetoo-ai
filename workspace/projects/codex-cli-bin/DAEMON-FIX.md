# Fix for session resume: missing codex-path/rg

Reapplied to maintainer feedback commit `e4ccd06`, in
`workspace/projects/codex-cli-bin/`. The copyright header, SRC_URI wrapping,
empty-global cleanup, metadata.xml, and Manifest from that baseline are retained.
The previous draft was preserved in a stash, not applied over this baseline.

## Cause

The original candidate removed upstream's bundled ripgrep in favor of
`sys-apps/ripgrep`. That works for the install-context's ordinary PATH fallback,
but it does not satisfy background-server package preparation. The release's
`codex-rs/app-server-daemon/src/prepare_install.rs::validate_package` requires:

```text
codex-package.json
bin/codex
bin/codex-code-mode-host
codex-path/rg
codex-resources/bwrap
```

`package_tree` additionally rejects file links whose resolved target escapes the
package root. A symlink from the private package into `/usr/bin/rg` therefore
is not an adequate repair. The package source must contain its own executable.
This was a candidate packaging defect, not lost session data or an account issue.

## Immediate workaround

From the user's existing test directory:

```sh
codex --no-daemon resume 01a16ea0-5d5e-7b00-a3e4-23b8aeaa8e8a
```

This uses the CLI's supported direct mode. It does not delete or recreate the
session and does not disable command sandboxing or approval settings. It bypasses
the shared background server, so features requiring that server are unavailable.

## Candidate repair

`codex-cli-bin-0.164.0-r1.ebuild` restores upstream's actual `codex-path/rg` under
`/usr/libexec/codex/codex-path/rg`, declares it in QA_PREBUILT, installs its three
original COPYING/LICENSE-MIT/UNLICENSE files, and removes the unnecessary
system-ripgrep dependency. Existing system ripgrep need not be removed.
The selected licensing option for ripgrep is MIT; that term was already present
in the package LICENSE expression.

The bundled ripgrep is 15.2.0. The amd64 executable was compared byte-for-byte
with its upstream release, whose checksum matches Codex's pinned DotSlash
manifest. Its original three notice files were copied from that verified release.
Both installed rg files are copied unchanged from the Codex package archives.

Architecture difference: amd64's bundled rg is static. Arm64's is GNU-linked,
requiring `/lib/ld-linux-aarch64.so.1`, libgcc_s.so.1, and glibc symbols through
GLIBC_2.18. The revised candidate declares arm64 glibc >=2.18 and GCC runtime
provider dependencies. This candidate consequently does not support arm64
musl-only systems; arm64 native execution has not been tested.

The revision bump allows an already installed 0.164.0 package to receive the fix.
Upstream PV and archive names remain 0.164.0; installed documentation uses PF
and is therefore under `codex-cli-bin-0.164.0-r1`.

## Validation performed

Fresh checks after applying to `e4ccd06` confirm the maintainer's metadata.xml
and Manifest are unchanged. All five Manifest entries match the actual files'
size, BLAKE2B and SHA512 values. The maintainer's copyright header, SRC_URI
wrapping and empty-global cleanup are preserved. The fresh staged amd64 public
command passes --version and --help, and its private rg reports 15.2.0.


- Bash syntax and whitespace checks pass.
- Both architecture images pass a file/mode/containment check matching the
  release's daemon-required file set. Every executable matches its archive bytes.
- Both images contain all nine documentation files; voice remains excluded.
- Staged amd64 CLI reports 0.164.0.
- An actual isolated amd64 daemon-start attempt passed package preparation,
  copied the package into its managed daemon location, and spawned the server.
  It then failed readiness with `app-server socket directory must be a user-owned
  directory with mode 0700`, the previously observed cloud-environment error.
  The daemon was stopped and the isolated test home removed.

Thus the missing-resource defect is repaired and daemon package preparation has
been exercised, but full daemon readiness and session resume still need native
Gentoo validation. No successful cloud daemon startup is claimed.

## Human incorporation

Merge the r1 changes into your already QA-corrected ebuild; retain your formatting
and metadata.xml. Include the three new `files/ripgrep-15.2.0-*` notices. Regenerate
the Manifest, run pkgcheck, and install the revision using your usual overlay
workflow. INCORPORATING.md gives the full commands. Do not add an escaping
symlink or overwrite `/usr/bin/rg` as a workaround.

After installing the revision:

```sh
/usr/libexec/codex/codex-path/rg --version
codex resume 01a16ea0-5d5e-7b00-a3e4-23b8aeaa8e8a
```

The private rg should report 15.2.0. Normal resume should no longer report a
missing package resource. If it fails for a different reason, preserve that
specific output for diagnosis; do not delete the existing session or daemon
state blindly.
