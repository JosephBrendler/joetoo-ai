# Step 1.9 — Version 1 packaging and integration HANDOFF

**Current status (2026-11-19): KICKOFF / AWAITING MAINTAINER AUTHORIZATION.**
The preceding Step 1.7 (including former 1.8) is **accepted and merged** via
[PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33), `df118da`.
There is no outstanding Step 1.7 acceptance, native-test or merge gate.

## Source, authority and scope

- Repository/project: `JosephBrendler/joetoo-ai`, `workspace/projects/joetoo-kwin/`.
- **Base:** `main` at `df118da` (maintainer's `q552u01` was synced after merge).
  Reconfirm actual HEAD/worktree before editing; no subsequent changes assumed.
- **Proposed task branch:** `task/joetoo-kwin-step1.9-packaging` (not created
  by this documentation patch; maintainer to choose/authorize).
- **Active objective:** source-to-package inventory, install paths, OpenRC
  user-service lifecycle, configuration/template/profile handling, ebuild
  dependencies, packaging QA and safe upgrade/uninstall. See [task README](README.md).
- **Accepted functional baseline:** [Step 1.7 archive](../archive/task_step1.7/README.md),
  [architecture](../ARCHITECTURE.md), [configuration reference](../docs/configuration-reference.md),
  and [user manual](../docs/joetoo-kwin_user_manual.md).
- **Authority:** the maintainer controls scope, native operations, releases,
  commits/PR/merge and integration into `joetoo` / `joetoo-upstream`. No
  production packaging edit, ebuild merge, installation or host administration
  is authorized by this HANDOFF alone. Respect repository-specific AI policies.

## First bounded assignment and expected result

**Next actor: maintainer**, to authorize a packaging-inventory/planning pass
and decide the target package/repository split, paths and any explicit
constraints. The proposed first agent assignment is **read-only** examination
of the accepted `joetoo-ai` sources and relevant packaging sources (where
policy permits), producing a concise component/install manifest and a
small integration plan. No speculative code rewrite or new framework.

After review, the maintainer may authorize a specific `joetoo-ai` packaging
candidate/diff, focused mock/metadata QA, and separately operate or approve
native install and smoke tests on X11 and Wayland. Agent writes to the
protected `joetoo`/`joetoo-upstream` repositories are not authorized.

## Completion boundary

Version 1 packaging is complete when the maintainer has accepted the install,
configuration, OpenRC/user lifecycle, dependency and safe-upgrade behavior on
both supported KWin backends and approved/published the integration. Preserve
all existing Step 1.7 source behavior and evidence; no new Step 1.7 increment,
whole RDP/VNC matrix or Version 2 features are required by this kickoff.
