# Step 1.9 — Version 1 packaging and integration HANDOFF

**Status (2026-11-23): ACTIVE — Step 1.8 accepted/merged; source
stabilization and Gentoo packaging remain.** This is the **sole active
joetoo-kwin task dispatcher**. The new Step 1.8 CLI completion (`-s`,
`-i MANAGED_ID`, and one-shot `-L under`) was merged through
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36) at
`main` `67c054c`. Its [archived HANDOFF](../archive/task_step1.8/HANDOFF.md),
[task README](../archive/task_step1.8/README.md) and
[merge closure](../archive/task_step1.8/step1.8-pr36-merge-closure-2026-11-23.md)
preserve the acceptance evidence. Do not recreate the Step 1.8 branch or
repeat its native acceptance tests for administrative closure.

## Source, scope, evidence and authority

- **Repository:** `JosephBrendler/joetoo-ai`;
  `workspace/projects/joetoo-kwin/`. Accepted source baseline
  `main` at `67c054c` after PR #36. A separate documentation-only
  archive-transition candidate was committed as `48dc17a` on
  `task/joetoo-kwin-step1.8-archive-step1.9-resume` and is awaiting
  maintainer review/merge. Refresh actual HEAD before any new work.
- **Design:** [ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md); the
  [project status](../README.md); [Step 1.8 archived acceptance](../archive/task_step1.8/README.md).
- **Detailed packaging scope:** [Step 1.9 README](README.md) and
  [revised packaging inventory/contract](step1.9-packaging-inventory-contract-REVISED-DRAFT.md).
  The latter remains a **revised draft** until outstanding installed-image,
  optional native-X11 plugin and ebuild choices are verified/settled.
  Source-to-source selection is the project-root [`MANIFEST`](../MANIFEST);
  the human-run staging/checking tool is
  [`tools/joetoo-kwin-stage-upstream`](../tools/joetoo-kwin-stage-upstream).
- **Completed preparation:** MANIFEST and staging script committed; eight
  colocated configuration READMEs, three inactive configuration examples,
  `release/README.md`, initial licensing metadata and the native close
  sources are in the development checkout. No current upstream parity,
  accepted tarball, production ebuild or installed-image QA is claimed.
- **Reserved operations:** the maintainer controls authorization, commits,
  PR merges, native KWin/service tests, integration into `joetoo-upstream`
  and `joetoo`, `tarup`, Portage builds and publication. Neither this
  HANDOFF nor the archive permits an agent to modify protected repos or
  administer hosts.

## Current next actor and ordered actions

**Next actor: maintainer.** Review and merge the documentation-only
Step 1.8 archive/Step 1.9 reactivation candidate, then authorize the
separate Step 1.9 implementation/release-stabilization branch from the
new accepted `main`. Keep the already approved scope and do not introduce
a new functional CLI milestone.

1. **Reconcile source and installed runtime inventory:** include the
   accepted Step 1.8 `libexec/joetoo_kwin_readonly.py`, verify sibling imports
   and all SFTP/RDP/VNC/close/recovery helpers, and repair CLI source-versus-
   installed lookup and both OpenRC `JOETOO_KWIND_EXEC` defaults.
2. **Human maintainability and provenance review:** inspect comments of
   every shipped Bash/OpenRC/eselect/Python/JS script, plus licensing,
   headers, third-party attribution and relevant C++ provenance. Use focused
   syntax/regression checks for any corrections; avoid unrelated rewrites.
3. **Curate and validate source transfer:** human-run `--plan`, `--apply`,
   `--verify`/`--release-check`, inspect stale/unlisted files and links,
   review the source archive and run `tarup` only when ready.
4. **Create and validate the production ebuild:** inspect `${ED}` against
   the source-to-installed contract in an isolated fixture, including an
   SFTP restore intent; decide the optional legacy native-X11 effect policy,
   then run maintainer-operated installed-path native Wayland/X11 smoke QA.

## Completion and stop boundary

The first target remains `dev-util/joetoo-kwin-0.1.0` with an accepted
KWin 6.7.6 development baseline. KWin 6.8, Version 2 panel reflow,
parallel remote authentication, new viewer clients and general focus-policy
redesign are **not** release prerequisites. No release succeeds by merely
passing source-tree or POC-installer tests; actual source provenance,
`tarup`, Portage installed-image completeness, path/isolation and appropriate
native package smoke checks require separate maintainer verification.
