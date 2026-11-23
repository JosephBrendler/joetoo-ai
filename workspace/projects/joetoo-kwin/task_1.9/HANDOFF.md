# Step 1.9 — Version 1 packaging and integration HANDOFF

**Status (2026-11-21): IN PROGRESS, PAUSED for proposed new Step 1.8 CLI completion.**
The existing Step 1.7 **includes the former Step 1.8** and remains fully
accepted (merged [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33),
`df118da`). The newly proposed **Step 1.8** is a distinct, post-1.7 task:
read-only `-s`, `-i MANAGED_ID` and a verified one-shot `-L under`. `-L panel`
and live panel reflow remain Version 2, not a Version 1 release gate.

## Source, authority, and current evidence

- **Repository/project:** `JosephBrendler/joetoo-ai`,
  `workspace/projects/joetoo-kwin/`; last confirmed `main` baseline **`24cd67f`**
  (maintainer pushed `release/README.md`). Refresh actual HEAD and worktree
  before starting another implementation.
- **Design:** [ARCHITECTURE §9/§11/§12](../ARCHITECTURE.md), including the new
  Step 1.8 proposed acceptance boundary and historical Version 2 separation.
- **Packaging scope:** [task README](README.md) and the
  [revised inventory/contract](step1.9-packaging-inventory-contract-REVISED-DRAFT.md).
  The project-root [`MANIFEST`](../MANIFEST) is the authoritative curated
  source-to-source file list; [`tools/joetoo-kwin-stage-upstream`](../tools/joetoo-kwin-stage-upstream)
  is the human-run transfer/checker.
- **Actual progress:** source MANIFEST and staging script committed; all eight
  colocated config companions, three inactive `.conf` examples, and
  `release/README.md` authored/committed. Prior upstream staging existed,
  **but no post-`24cd67f` upstream parity or tarup success is claimed**.
- **Open packaging work:** source/installed libexec and OpenRC service paths;
  human maintainability-comment review of every shipped Bash, OpenRC,
  eselect, Python and JS script (including sourced/imported modules, excluding
  test fixtures); final headers/provenance and relative-links audit; complete
  transfer validation; `tarup`, ebuild/install image and native package QA.
- **Version boundary:** initial source package may target accepted KWin **6.7.6**;
  KWin 6.8 compatibility work is not a prerequisite for this 0.1.0 release.

## Current next actor and stop boundary

**Next actor: maintainer.** Review this proposed revised Version 1 scope, then
create/authorize a *new* `task/joetoo-kwin-step1.8-cli-completion` branch from
current accepted `main`. Write its bounded `task_1.8/README.md` and
`task_1.8/HANDOFF.md` before implementation, linking to ARCHITECTURE rather
than copying the historical acceptance record. No Step 1.8 code or native
operation is authorized merely by this Step 1.9 HANDOFF.

**When new Step 1.8 is accepted/merged**, return to Step 1.9: refresh the
MANIFEST, complete packaging-path integration and human comment review, stage
curated source to `joetoo-upstream`, perform provenance/tarup checks, then
build and inspect the `joetoo` ebuild. These are separate maintainer gates.

`joetoo-upstream` and `joetoo` remain advisory-only for AI agents. No agent
write/commit, `tarup`, `emerge`, host administration, service restart or effect
load is authorized by this handoff. The maintainer owns commits, PRs, merges,
protected repository integrations and native acceptance.

## Completion boundary

Step 1.9 is complete only after the newly accepted CLI contract is packaged,
maintainability comments and source provenance are human reviewed, install
paths/dependencies/permissions and OpenRC user lifecycle are verified, and the
maintainer accepts the resulting source archive and Gentoo 0.1.0 package.
Preserve Step 1.7 safety and history. Do not expand the release to KWin 6.8,
Version 2 panel insertion/reflow, new remote protocols, or a redundant full
RDP/VNC regression matrix absent an actual change requiring it.
