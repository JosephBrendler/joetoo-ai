# Step 1.9 — Version 1 packaging and integration HANDOFF

**Status (2026-11-27): ACTIVE — Step 1.9 source stabilization and readability
audit in progress; Gentoo release packaging remains open.** This is the
**sole active joetoo-kwin task dispatcher**. Step 1.8 CLI completion (`-s`,
`-i MANAGED_ID`, one-shot `-L under`) was accepted/merged through
[PR #36](https://github.com/JosephBrendler/joetoo-ai/pull/36) at
`main` `67c054c`; the archive/Step 1.9 transition was subsequently merged
through PR #37 (`b61655a`). Do not repeat native Step 1.8 acceptance solely
for administrative closure. Four production files are now maintainer-accepted
for readability; see [the ordered audit ledger](step1.9-comment-readability-audit-ledger.md).

## Source, scope, evidence and authority

- **Repository:** `JosephBrendler/joetoo-ai`;
  `workspace/projects/joetoo-kwin/`. Accepted Step 1.8 baseline was
  `main` `67c054c`; PR #37 merged the archive transition as `b61655a`.
  Active stabilization branch:
  `task/joetoo-kwin-step1.9-packaging-integration`. Latest **pushed**
  source checkpoint evidenced here: `0dd2ba3` (2026-11-27). This contains
  the accepted launch-library/session audit (`98ce0d4`) and the subsequently
  committed/pushed eselect `configs/` update. Refresh real HEAD/worktree
  before new work; this documentation patch is only a candidate.
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

## Source readability audit and selector evidence (2026-11-27)

- **ACCEPTED production files (4):** `joetoo-kwin` and
  `libexec/joetoo-kwin-plan-functions` (2026-11-25, `f4e9ba92`);
  `libexec/joetoo-kwin-launch-functions` and
  `libexec/joetoo-kwin-session.bashrc` (2026-11-27, `98ce0d4`).
  `tools/joetoo-kwin-stage-upstream` was also in the first acceptance commit,
  but is a development/reference tool outside the curated release inventory.
- **Authoritative ordered review checklist:**
  [step1.9-comment-readability-audit-ledger.md](step1.9-comment-readability-audit-ledger.md).
  It enumerates **26 production source files**, including the Python broker,
  KWin JavaScript and three C++ files; `CMakeLists.txt` is a related native
  build-comment review. A file remains pending until maintainer acceptance.
- **Selector functional evidence:**
  [step1.9-eselect-configs-evidence-2026-11-27.md](step1.9-eselect-configs-evidence-2026-11-27.md).
  The user-owned `configs/` update is committed/pushed (`0dd2ba3`). Before
  commit, ShellCheck exited 0 and **18/18** focused selector tests passed.
  This does **not** complete selector comment-audit acceptance or prove
  packaged-path QA. No `/etc` selector management or installer HOME-plan
  initialization is intended.
- **Deferred functional choice:** `plan_defaults()` currently uses local RDP
  initial client `800x600` and remote `1024x768`; possible local initial
  `1024x768` is a separate setting change, not reopening the accepted audit.

## Current next actor and ordered actions

**Next actor: maintainer on the active Step 1.9 branch.** Review the selector
module's **comments** for possible audit acceptance (the functional `configs/`
update is already committed), complete the remaining per-file audits using
the ledger, then finish separate source/package gates. Keep Version 1 scope.

1. **Reconcile source and installed runtime inventory:** include the
   accepted Step 1.8 `libexec/joetoo_kwin_readonly.py`, verify sibling imports
   and all SFTP/RDP/VNC/close/recovery helpers, and repair CLI source-versus-
   installed lookup and both OpenRC `JOETOO_KWIND_EXEC` defaults.
2. **Human maintainability and provenance review:** follow the ordered
   audit ledger for pending OpenRC/eselect/Python/JS/**C++** production files,
   with related CMake commentary; track licensing and third-party provenance
   separately. Record focused validation and explicit maintainer acceptance.
   Do not repeat the four accepted Bash audits or mix functional changes into
   comment-only passes.
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
