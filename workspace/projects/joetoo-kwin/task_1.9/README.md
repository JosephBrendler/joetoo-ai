# Step 1.9 — Version 1 packaging and integration

**Status at `joetoo-ai/main` `24cd67f` (2026-11-21): source curation and
configuration documentation in progress; packaging temporarily paused for a
new Step 1.8 CLI-completion task.** No production ebuild, published tarball,
package installation or native packaged-path smoke-test result is claimed.
Step 1.7 (which absorbed the *former* Step 1.8) remains accepted and merged
([PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33), `df118da`).
The [active dispatcher](HANDOFF.md) identifies the next actor and reserved
authorizations; this task README is a state/history summary, not permission
to operate on either protected repository.

## Objective and release boundary

Package a **maintainable, tested KWin 6.7.6 Version 1** installation for
Gentoo/OpenRC, preserving the accepted application/broker/KWin identity and
remote-resource contracts. The intended release is
`dev-util/joetoo-kwin-0.1.0`, with curated sources in `joetoo-upstream`,
`tarup` archive, and an EAPI-8 ebuild in `joetoo`. `joetoo-upstream` and
`joetoo` remain maintainer-integrated; the development checkout is not a
production install image. KWin 6.8 support is subsequent compatibility work,
not a prerequisite for delivering the accepted 6.7.6 implementation.

An additional Version 1 CLI scope issue has been discovered: `-s` and `-i`
are recognized but unimplemented; `-L under` was previously deferred. The
maintainer proposes a **new Step 1.8** to finish read-only status/detail
and verified one-shot lowering without panel reflow. See
[ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md) for the proposed scope, explicit
historical correction and Version 2 deferral of `-L panel`.

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

## Remaining Step 1.9 stabilization work — after new Step 1.8 acceptance

1. **Freeze the accepted CLI semantics.** Merge/accept new Step 1.8 first;
   update affected manual/usage text and run focused X11/Wayland regression.
   Do not reopen accepted Step 1.7 snapshot/recovery or existing `-o` layers.
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

The **maintainer** decides whether to accept the proposed revised architecture
and starts the new `task/joetoo-kwin-step1.8-cli-completion` branch from a
fresh, clean accepted `main`. That task should have its own small README and
HANDOFF (not historical changes to the already accepted Step 1.7 archive),
with explicit test cases for `-s`, `-i`, and verified `-L under`. On acceptance,
resume this Step 1.9 source freeze and packaging integration. See
[HANDOFF](HANDOFF.md) for the authorization and next-actor boundary.
