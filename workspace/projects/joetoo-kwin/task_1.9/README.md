# Step 1.9 — Version 1 packaging and integration

**Status (2026-11-27): ACTIVE — Step 1.9 stabilization and source audit in
progress.** Step 1.8 was accepted/merged through
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36) at `67c054c`,
then the archive/Step 1.9 transition through PR #37 at `b61655a`.
On `task/joetoo-kwin-step1.9-packaging-integration`, the maintainer has
accepted four production source readability audits, most recently in
`98ce0d4`; the `eselect` `configs/` change passed focused checks and was
committed and pushed in `0dd2ba3`. Its **comment audit** remains pending.
No accepted source tarball, production ebuild, installed-image QA or
packaged-path native
acceptance is claimed. [HANDOFF.md](HANDOFF.md) remains the active dispatcher;
see the [ordered audit ledger](step1.9-comment-readability-audit-ledger.md).

## Objective and release boundary

Package a **maintainable, tested KWin 6.7.6 Version 1** installation for
Gentoo/OpenRC, preserving the accepted application/broker/KWin identity and
remote-resource contracts. The intended release is
`dev-util/joetoo-kwin-0.1.0`, with curated sources in `joetoo-upstream`,
`tarup` archive, and an EAPI-8 ebuild in `joetoo`. `joetoo-upstream` and
`joetoo` remain maintainer-integrated; the development checkout is not a
production install image. KWin 6.8 support is subsequent compatibility work,
not a prerequisite for delivering the accepted 6.7.6 implementation.

The previously missing Version 1 CLI commands are now accepted:
read-only `-s`, read-only `-i MANAGED_ID`, and verified one-shot
`-L ... under`. The `-L panel`/live-reflow feature remains deferred to
Version 2. See the [Step 1.8 acceptance archive](../archive/task_step1.8/README.md),
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36) and
[ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md) for the accepted scope.
Production packaging and installation of these new helpers are still
Step 1.9 obligations, not assumed complete merely because the CLI passed
source-tree validation.

## Completed source-preparation progress (not yet release acceptance)

- Project-root [`MANIFEST`](../MANIFEST) is now the **single** explicit curated
  source-to-source allowlist, with reporting group, source-relative path and
  optional upstream-relative destination. Source `release/README.md` is mapped
  to upstream root `README.md`; `ARCHITECTURE.md` and license metadata are
  included. Transfer order can group each README after its corresponding file.
- [`tools/joetoo-kwin-stage-upstream`](../tools/joetoo-kwin-stage-upstream)
  has default read-only `--plan`, opt-in `--apply`, byte/mode `--verify`, and
  pre-tarup `--release-check`, all with Joetoo announce–act–report. The human
  ran prior staging successfully; that is **not** proof that the present final
  source tree is synchronized or has passed tarup.
- Eight short configuration READMEs are **colocated with their respective
  configuration/example/module** under `conf.d/`, `user-conf.d/`,
  `account-conf.d/`, `config-examples/system/`, `config-examples/user/`,
  `eselect/` and the project root. Three non-active `.conf` examples and
  `release/README.md` have been added. `docs/configuration-reference.md`
  remains the full setting reference; `docs/joetoo-kwin_user_manual.md` the
  operational manual.
- `LICENSES.package` and `COPYRIGHT.exceptions` exist as **provisional**
  release metadata and still require final curated-source provenance/header
  verification. The native Wayland KWin effect and XWayland XCB helper remain
  core, separate from the optional legacy native-X11 effect.

## Source readability audit progress — 2026-11-27

The maintainability skill requires a per-file ledger. The
[ordered source audit ledger](step1.9-comment-readability-audit-ledger.md)
was created from `MANIFEST`: **26 production files**, including shell,
OpenRC, eselect, Python, KWin JavaScript, and three C++ files; review CMake
build commentary with the C++ files. **Four production files are ACCEPTED:**
`joetoo-kwin` and `libexec/joetoo-kwin-plan-functions` on 2026-11-25
(`f4e9ba92`); `libexec/joetoo-kwin-launch-functions` and
`libexec/joetoo-kwin-session.bashrc` on 2026-11-27 (`98ce0d4`). The
accepted development/reference `tools/joetoo-kwin-stage-upstream` is not a
curated production file. Do not recommend another audit of an accepted file.

The user-only `eselect joetoo-kwin` selection convention is now
`~/.config/joetoo-kwin/configs/*.conf` with
`~/.config/joetoo-kwin/joetoo-kwin.conf -> configs/NAME.conf` (subject to
`XDG_CONFIG_HOME`). The corrected patch was applied to the maintainer's
working tree, passed ShellCheck and **18/18** focused selector tests,
and was committed/pushed in `0dd2ba3`; details are in
[selector evidence](step1.9-eselect-configs-evidence-2026-11-27.md).
Its separate source-comment audit has not been accepted.
`tools/joetoo-kwind-install-poc` does not manage those per-run files.
The packaging contract draft still contains old `profiles/` references and
must be reconciled before source transfer.

## Remaining Step 1.9 stabilization work — resumed

1. **Use the accepted Step 1.8 CLI baseline.** Preserve its
   `-s`, `-i` and `-L under` behavior and include `joetoo_kwin_readonly.py`
   in both the curated transfer and the installed libexec inventory.
   `-L panel` remains unsupported; do not reopen the Step 1.7 snapshot/
   recovery or serial `-o` contracts. Run focused regression only when
   implementation changes warrant it.
2. **Repair packaged paths only where needed.** Use a consistent safe resolver
   for source-checkout and installed `/usr/bin`/`/usr/libexec/joetoo-kwin/`
   layouts. Synchronize both global OpenRC and user-service broker executable
   defaults; retain no automatic user-home initialization or service start.
3. **Human source maintainability/comment audit of every curated production
   code file, excluding test fixtures.** Follow the ledger for remaining
   OpenRC, eselect, Python, JS and C++ files, including native header contracts
   and related CMake commentary. Explain nontrivial implementation blocks,
   interfaces and failure paths; validate comment-only edits without changing
   functional behavior. The four accepted Bash source files need no repeat
   audit. Track functional/default changes separately.
4. **Source release review.** Correct stale relative links in curated docs,
   final copyright/SPDX attribution and header exceptions, and source-only
   README; run human `--plan` → `--apply` → `--release-check` and inspect
   unlisted upstream files before executing `tarup joetoo-kwin -minor` from
   `joetoo-upstream/dev-util` (after checking for any prior archives).
5. **Package/installation QA.** Implement the separate EAPI-8 ebuild with
   selected USE/dependency policy and package paths; inspect binary
   artifact/installation image, licenses, OpenRC lifecycle and KWin plugin
   variants. Only the maintainer runs native install/Wayland/X11 smoke tests.

The authoritative [Step 1.9 revised inventory/contract](step1.9-packaging-inventory-contract-REVISED-DRAFT.md)
contains the source/install inventory, complete two-tree configuration
precedence and stage gates. The `MANIFEST` supplies exact curated source paths;
**neither document should become a competing second file-selection list**.

## Packaging acceptance criteria and exclusions

- Reproducible installed CLI, broker/private modules, resident JS, KWin 6.7.6
  native plugin and XCB close helper, explicit OpenRC user-service lifecycle;
  optional native-X11 plugin policy remains a bounded ebuild decision.
- Correct protected global configuration and inert override examples;
  selector module installed but never run automatically; user configs,
  snapshots, and HOME configuration never rewritten by Portage.
- Human-reviewed script comments, final source provenance, tarball file listing,
  package/ebuild QA, and native **packaged-path** acceptance against the chosen
  KWin 6.7.6 compatibility boundary. No required KWin 6.8 upgrade test.
- No new viewer protocols, panel insertion/reflow, permanent stacking rules,
  generic plugin framework, forced application shutdown or redundant wholesale
  historical RDP/VNC test matrix.

## Current next transition

Step 1.8 is [accepted and archived](../archive/task_step1.8/README.md),
and Step 1.9 is underway on
`task/joetoo-kwin-step1.9-packaging-integration`. The next comment-audit
file is `eselect/joetoo-kwin.eselect` (semantic comment review still
pending despite the committed functional update), followed by the OpenRC user
service, Python modules, KWin resident JavaScript, and C++ implementation/
header files, as ordered in the ledger. Complete source/installed-path
reconciliation, packaging-draft terminology updates, source provenance,
source staging, tarup, ebuild and packaged-path smoke QA as **separate** gates.
The maintainer retains control of native operations, commits and publication.
