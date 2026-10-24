# Human incorporation instructions

These instructions are for the human maintainer. The assistant has not accessed
or modified `joetoo` or `joetoo-upstream`. The candidate is
`dev-util/codex-cli-bin-0.164.0`; it remains unkeyworded.

## 1. Obtain and review the candidate

The new workspace changes must first be transferred to your machine. Until they
are committed and pushed with your approval, fetching PR #1 does not obtain
this revision. Alternatively, extract the supplied candidate bundle locally.

In a terminal on your Gentoo machine, enter the candidate directory containing
`codex-cli-bin-0.164.0.ebuild`, this file and `files/`, then set:

```bash
candidate_dir=$PWD
# Replace this with the actual local overlay root, not its dev-util subdirectory.
overlay_dir=/absolute/path/to/joetoo
package_dir="${overlay_dir}/dev-util/codex-cli-bin"
```

Your existing edited ebuild should be compared before replacement:

```bash
diff -u "${package_dir}/codex-cli-bin-0.164.0.ebuild" \
    "${candidate_dir}/codex-cli-bin-0.164.0.ebuild"
```

A diff exit status of 1 means differences were found. Keep any local changes you
want; merge them into the candidate before the copy step. If the destination
ebuild does not yet exist, skip this comparison. Check any existing supplemental
notice files too. Do not automatically discard your local edits.

## 2. Back up the existing package and copy the reviewed files

After deciding which version to keep, preserve the existing package outside the
overlay and copy only the ebuild and its three supplemental notice files:

```bash
backup_dir=$(mktemp -d /tmp/codex-cli-bin-backup.XXXXXX)
if [[ -d ${package_dir} ]]; then
    cp -a "${package_dir}" "${backup_dir}/"
fi
printf 'Existing-package backup: %s\n' "${backup_dir}"

install -d "${package_dir}/files"
install -m 0644 "${candidate_dir}/codex-cli-bin-0.164.0.ebuild" "${package_dir}/"
install -m 0644 \
    "${candidate_dir}/files/Ratatui-MIT" \
    "${candidate_dir}/files/libcap-2.75-LICENSE" \
    "${candidate_dir}/files/libcap-2.75-COPYRIGHTS" \
    "${package_dir}/files/"
```

Use an account permitted to edit the overlay. Retain the existing `metadata.xml`
or create one using the overlay's actual maintainer conventions and contact
information. Its upstream GitHub identity is `openai/codex`. No maintainer email
has been invented in this candidate. If an older `codex-bin` package was already
installed or published, decide the replacement/blocker policy before emerging
both; they would own the same public command. The other package has not been
inspected here.

## 3. Generate the Manifest and run package QA

From the destination package directory:

```bash
cd "${package_dir}"
bash -n codex-cli-bin-0.164.0.ebuild
ebuild codex-cli-bin-0.164.0.ebuild manifest
```

Manifest generation fetches/hashes the declared artifacts and local files. It
is not a substitute for signature verification. Keep normal Portage checksum
and TLS verification enabled.

From the overlay root, with pkgcheck installed:

```bash
cd "${overlay_dir}"
pkgcheck scan dev-util/codex-cli-bin
git diff --check
git status --short
```

Resolve findings concerning the ebuild, files, metadata.xml, or Manifest. Do not
suppress unexplained checks merely to obtain a clean result. A broader package
rename/move, if relevant to an already published package, needs the overlay's
normal migration policy.

## 4. Resolve and install on a disposable Gentoo test system

Use the overlay's actual repository name (normally the contents of
`profiles/repo_name`). To test the unkeyworded package, add one package-specific
entry through your normal package.accept_keywords configuration. For example,
if the configured repository name is `joetoo`:

```text
=dev-util/codex-cli-bin-0.164.0::joetoo **
```

Do not globally accept unkeyworded packages. On the test system, run:

```bash
emerge --pretend --verbose --oneshot '=dev-util/codex-cli-bin-0.164.0::joetoo'
emerge --ask --verbose --oneshot '=dev-util/codex-cli-bin-0.164.0::joetoo'
```

Replace `joetoo` in those atoms if the repository is configured under another
name. Confirm the resolver selects this repository and the intended version.
The second command installs the package and dependencies; perform it only on
the system you intend to use for the test. Preserve Portage QA output.

## 5. Verify the installed result

As the intended ordinary user:

```bash
command -v codex
readlink -f /usr/bin/codex
codex --version
codex --help
rg --version
ls -l /usr/libexec/codex/bin/ /usr/libexec/codex/codex-resources/
ls -l /usr/share/doc/codex-cli-bin-0.164.0/
codex sandbox linux -- /bin/true
```

Expected CLI version: `codex-cli 0.164.0`. The public command should resolve to
`/usr/libexec/codex/bin/codex`. The companion host and matching bwrap should be
executable without setuid bits. All six documents should be present, possibly
compressed: LICENSE, NOTICE, Ratatui-MIT, libcap-2.75-LICENSE,
libcap-2.75-COPYRIGHTS, and bubblewrap-COPYING.

Use a disposable project for an interactive/authenticated session when ready.
Verify file search with system ripgrep, code-mode functionality if used, and
sandbox allow/deny behavior relevant to your workflow. The `/bin/true` smoke
check alone does not demonstrate confinement. Do not put an isolated CODEX_HOME
under `/tmp`; upstream rejects helper alias creation there. Never share keys or
authentication files in the review output.

Check clean uninstall in the disposable test system and confirm the package's
owned files are removed. Do not unmerge a production installation merely to
satisfy this checklist.

## 6. Record results and finalize

Record architecture, libc/profile, version, Portage/pkgcheck findings and runtime
results. Add only testing keywords supported by native results, e.g. `~amd64`
after amd64 validation; do not add `~arm64` merely because its archive staged.
Stable keywords need separate evidence.

The exact remaining provenance/notices work is in LICENSING-REVIEW.md. Complete
it for a claim of licensing completeness. If serving binary packages or
mirroring upstream archives, resolve source/notice delivery for that distribution
as a separate decision. It does not prevent doing local installation tests.

Review the final diff, then make the official commit/push yourself. Candidate
review in joetoo-ai and publication in the official overlay are separate steps.
