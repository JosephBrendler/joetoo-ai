# Step 1.9 — Version 1 packaging and integration

**Status (2026-11-23): ACTIVE, resumed after Step 1.8 acceptance and
merge.** The intervening CLI-completion task was reviewed and merged through
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36), making
`67c054c` the accepted `joetoo-ai/main` source baseline. Its
[archived evidence](../archive/task_step1.8/README.md) and
[merge closure](../archive/task_step1.8/step1.8-pr36-merge-closure-2026-11-23.md)
are historical; Step 1.9 does not rerun the whole native CLI validation
matrix solely because of packaging. No production ebuild, published tarball,
installed-path checks or native packaged-path acceptance is yet claimed.
The [active dispatcher](HANDOFF.md) identifies the next actor and reserved
authorizations; this README records scope and history.

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
3. **Human maintainability-comment audit of EVERY shipped script, excluding
   test fixtures.** Inspect Bash CLI and sourced helpers, the OpenRC user
   service, eselect module, all curated Python broker/launcher modules and
   KWin JavaScript, even when installed as non-executable data. Fix misleading
   comments, clarify argument/return/status contracts, security-sensitive
   assumptions and non-obvious command options. Keep behavior-changing
   edits separately identifiable and run syntax/lint plus focused tests.
   Compiled native C++ gets its own source/header review; this specific
   interpreted-script audit does not imply a C++ redesign.
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
  selector module installed but never run automatically; user profiles,
  snapshots, and HOME configuration never rewritten by Portage.
- Human-reviewed script comments, final source provenance, tarball file listing,
  package/ebuild QA, and native **packaged-path** acceptance against the chosen
  KWin 6.7.6 compatibility boundary. No required KWin 6.8 upgrade test.
- No new viewer protocols, panel insertion/reflow, permanent stacking rules,
  generic plugin framework, forced application shutdown or redundant wholesale
  historical RDP/VNC test matrix.

## Current next transition

Step 1.8 is [accepted and archived](../archive/task_step1.8/README.md).
After the documentation-only archive/transition PR is reviewed, the
maintainer starts the Step 1.9 source-stabilization implementation branch
from updated `main`, using [HANDOFF](HANDOFF.md) as the only active
dispatcher. Next concrete work is the source-versus-installed helper inventory,
including the read-only helper, plus installed path and OpenRC defaults
before a source release or ebuild is claimed. Protected repositories, native
operations and publication remain maintainer-controlled.
